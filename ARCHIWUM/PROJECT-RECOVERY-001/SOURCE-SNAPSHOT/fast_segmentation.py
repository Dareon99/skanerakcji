"""backend/v3/tools/fast_segmentation.py — SKAN WYCHYLEŃ MACD (V3.2A, produkcyjny).

ZATWIERDZONA SEGMENTACJA (decyzja właściciela 2026-08-16): wariant B — prominencja
topograficzna, próg 0,25 × odchylenie standardowe MACD danego instrumentu i interwału,
bez minimalnej odległości w barach. Historyczne wychylenia wyłącznie na 1D.

Warianty A, B 0,50 i C pozostają dostępne wyłącznie w trybie diagnostycznym
(v3/tools/segmentation_compare.py) i nie trafiają do tego dashboardu.

Skąd bierze się przyspieszenie (bez chodzenia na skróty w danych):

MACD liczy się z ceny ZAMKNIĘCIA, a ta pochodzi z natywnego bara dziennego — jednego
zapytania. Bary 30m są potrzebne wyłącznie do analitycznego H/L świec i do zbudowania 1H,
czyli do tego, co widać w oknie wykresu. Dlatego pełny przebieg pobierał 30m za ~2,7 roku
(~17 zapytań), choć segmentacja korzysta z nich w zerowym stopniu.

FAST pobiera 30m tylko za okres OKNA WYŚWIETLANIA (~250 sesji ≈ 1 rok, ~6 kawałków), a
MACD i tak liczy na pełnej historii dziennej z natywnego zapytania — z pre-rollem bez
uszczerbku. Razem ~7 zapytań na spółkę zamiast ~17, przy niezmienionej matematyce.

Czego to NIE zmienia: wariantów A/B/C, parametrów segmentacji, formuł wskaźników,
polityki analitycznego H/L (nadal fail closed — sesja bez kompletnego pokrycia 30m nie
dostaje H/L), kanonicznego kalendarza ani kontraktów.
"""

import argparse
import csv
import datetime as _dt
import json
import os
import sys
import time as _time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from v3.macd_excursions import detector as DET  # noqa: E402
from v3.tools import chart_validation as CV  # noqa: E402

FAST_SET = ("RBLX", "AAOI", "INTU", "NVDA", "PLTR", "ADTN")
EXTRA_SET = ("AAPL", "ZS")
DISPLAY_BARS = 250                  # okno wykresu = zakres pobierania 30m
HISTORY_DAYS_1D = 1100              # ~3 lata dziennych zamknięć: jedno zapytanie
LOWER_DAYS = 400                    # 30m pod okno 250 sesji + zapas na święta
SEGMENTATION_TIMEFRAME = "1D"       # historyczne wychylenia MACD tylko na tym interwale
# Kolejnosc = kolejnosc przyciskow w dashboardzie. Jedno zrodlo prawdy dla skanu,
# kompletnosci i UI. 1H nadal z zatwierdzonej sciezki us_rth; 2H i 4H z kanonicznego 30m.
ALL_TIMEFRAMES = ("30m", "1H", "2H", "4H", "1D")
INTRADAY_TIMEFRAMES = ("30m", "1H", "2H", "4H")
PAYLOAD_SCHEMA = "FAST_SEG_PAYLOAD_3"   # 5 interwalow: zmiana wymusza przeliczenie
# Testy i CI nie moga otwierac przegladarki na katalogu tymczasowym.
OPEN_DASHBOARD = os.environ.get("V3_NO_BROWSER", "") == ""
HARD_LIMIT_S = 55 * 60
SYMBOL_WARN_S = 10 * 60
DIAG_VERSION = "FAST_SEG_1"


def _log(stage, symbol="", t0=None, extra=""):
    el = "" if t0 is None else "  %.1fs" % (_time.time() - t0)
    print("[%s] %-20s %-6s%s%s" % (_dt.datetime.now().strftime("%H:%M:%S"), stage,
                                   symbol, el, ("  " + extra) if extra else ""),
          flush=True)


def _fetch(symbol, now, need_daily=True, need_lower=True):
    """Maksymalnie JEDNO pobranie 1D i JEDNO 30m na spolke w calym przebiegu.

    30m jest jedynym zrodlem 30m, 1H, 2H i 4H - kazdy brakujacy interwal intraday
    powstaje z tego samego pobrania. Gdy 1D ma juz aktualny payload, dzienne nie jest
    pobierane ponownie.
    """
    day_to = now.tz_convert(CV.CAL.NY).date()
    d1_from = day_to - _dt.timedelta(days=HISTORY_DAYS_1D)
    m30_from = day_to - _dt.timedelta(days=LOWER_DAYS)
    daily = lower = None
    requests = 0
    if need_daily:
        t = _time.time()
        daily = CV._results_to_frame(CV._aggs(symbol, 1, "day", d1_from, day_to))
        requests += 1
        _log("1D FETCH", symbol, t, "rows=%d zakres=%s..%s (1 zapytanie)"
             % (len(daily), d1_from, day_to))
    else:
        _log("1D REUSE", symbol, None, "payload aktualny - zero pobrania")
    if need_lower:
        t = _time.time()
        lower = CV._results_to_frame(CV._aggs_chunked(symbol, 30, "minute", m30_from,
                                                      day_to))
        chunks = len(CV.chunk_spans(m30_from, day_to))
        requests += chunks
        _log("30M FETCH", symbol, t, "rows=%d zakres=%s..%s (%d kawalkow, jedyne"
             " zrodlo intraday)" % (len(lower), m30_from, day_to, chunks))
    return daily, lower, {"d1_rows": 0 if daily is None else len(daily),
                          "m30_rows": 0 if lower is None else len(lower),
                          "requests": requests}


def _canonical_1d(symbol, daily, lower, now):
    from v3.market_data.daily_analysis import build_daily_analysis
    from v3.market_data.us_rth import session_date_of
    raw = pd.DataFrame(index=daily.index)
    raw["bar_close_utc"] = [
        CV.CAL.session_schedule(session_date_of(ts))["close_utc"]
        if CV.CAL.session_schedule(session_date_of(ts)) else ts for ts in daily.index]
    raw["session_date"] = [session_date_of(ts) for ts in daily.index]
    for col in ("open", "high", "low", "close", "volume"):
        raw[col] = daily[col]
    raw["is_final"] = [pd.Timestamp(bc) <= now for bc in raw["bar_close_utc"]]
    analysis, quality = build_daily_analysis(raw, lower)
    return analysis, quality


def _canonical_intraday(symbol, tf, lower, now):
    """Kazdy interwal intraday z TEGO SAMEGO kanonicznego zbioru 30m.

    1H zostaje na zatwierdzonej sciezce us_rth (kontrakt r591 nietkniety). 2H i 4H
    powstaja bezposrednio z 30m - nigdy z gotowego 1H. Niekompletny kubelek jest
    pomijany (fail closed), nie doszacowywany.
    """
    from v3.market_data import us_multi_tf as MTF
    if tf == "1H":
        return CV.fetch_canonical_1h(symbol, lower, now)
    m30 = MTF.canonical_30m(lower)
    if tf == "30m":
        bars = m30.copy()
    else:
        minutes = MTF.timeframe_minutes(tf.lower())
        bars, skipped = MTF.aggregate_from_lower(m30, minutes)
        if skipped:
            _log("%s FAIL CLOSED" % tf, symbol, None,
                 "pominieto %d niekompletnych kubelkow" % len(skipped))
    bars = bars.copy()
    bars["is_final"] = [pd.Timestamp(bc) <= now for bc in bars["bar_close_utc"]]
    return bars


def _variants(macd, sig, full_macd=None):
    """Zatwierdzona segmentacja produkcyjna: WYLACZNIE wariant B z progiem 0.25.

    Zwraca dwie rzeczy o ROZNEJ semantyce:
      local_valleys  wszystkie kandydaty B 0,25 - ida do profilu, sredniej, mediany
                     i rankingu, ale NIE sa rysowane na wykresie produkcyjnym,
      top            JEDNO najwieksze historyczne wychylenie (max prominencja, przy
                     remisie nowsze) - tylko ono dostaje marker i tooltip.

    `full_macd` to pelna historia po rozgrzewce; gdy podana, wybor najwiekszego
    wychylenia liczy sie na niej, wiec zoom nie zmienia wyboru punktu.
    """
    import v3.macd_excursions as MX
    local = MX.approved_candidates(macd, sig)
    base = full_macd if full_macd else macd
    scale = DET.macd_scale(base)
    top = DET.largest_excursion(base, MX.approved_candidates(base, None))
    return {"local_valleys": local, "top": top, "macd_std": scale,
            "threshold": scale * MX.APPROVED_LEVEL}


def process_symbol(symbol, now=None, timeframes=ALL_TIMEFRAMES):
    """Jedna spolka, wskazane interwaly, z JEDNEGO pobrania 30m i jednego 1D."""
    from v3.features import build_atomic_features
    from v3.features.schema import FeatureBatchMeta
    from v3.market_data import warmup as W
    now = now or pd.Timestamp.now(tz="UTC")
    t_sym = _time.time()
    _log("START", symbol)
    timing = {"fetch": 0.0, "build": 0.0, "variants": 0.0}

    t = _time.time()
    # 30m potrzebne zawsze: to zrodlo intraday ORAZ analitycznych H/L dla 1D.
    daily, lower, diag = _fetch(symbol, now, "1D" in timeframes, True)
    timing["fetch"] = _time.time() - t

    payloads, rows = {}, []
    for tf in timeframes:
        t = _time.time()
        if tf == "1D":
            bars, dq = _canonical_1d(symbol, daily, lower, now)
        else:
            bars, dq = _canonical_intraday(symbol, tf, lower, now), None
        wm = W.plan_warmup(tf, int(bars["is_final"].sum()), True)
        batch = build_atomic_features(bars, FeatureBatchMeta(symbol, tf), wm)
        payload = CV.build_symbol_payload(symbol, tf, bars, batch,
                                          display=DISPLAY_BARS, daily_quality=dq)
        timing["build"] += _time.time() - t
        _log("%s BUILD" % tf, symbol, t, "bars=%d okno=%d"
             % (len(batch.features), payload["quality"]["display_bars"]))

        t = _time.time()
        disp = batch.features.tail(len(payload["candles"]))
        macd = [None if pd.isna(v) else float(v) for v in disp["macd"]]
        sig = [None if pd.isna(v) else float(v) for v in disp["macd_signal"]]
        # Historyczne wychylenia MACD sa kontraktem WYLACZNIE dla 1D. Payload 1H nie
        # dostaje ani kandydatow, ani przeciecia zbiorow - renderer nie ma wiec czego
        # narysowac i zaden wybor wariantu tego nie przywroci.
        if tf != SEGMENTATION_TIMEFRAME:
            payload["segmentation"] = {}
            payload["segmentation_overlap"] = {}
            payload["segmentation_status"] = "NIE DOTYCZY - wychylenia tylko na 1D"
            payload["schema"] = PAYLOAD_SCHEMA
            payload["local_valleys"] = []
            payload["top_excursion"] = None
            timing["variants"] += _time.time() - t
            payloads["%s|%s" % (symbol, tf)] = payload
            # Wiersz raportu MUSI powstac takze dla 1H - inaczej payload istnieje,
            # a results.csv, raport, dashboard i licznik go nie widza.
            rows.append({"symbol": symbol, "tf": tf,
                         "bars": payload["quality"]["display_bars"],
                         "local_valleys": 0, "top_date": "", "top_prominence": "",
                         "macd_std": ""})
            _log("%s BEZ WYCHYLEN" % tf, symbol, None,
                 "kontrakt: tylko 1D (wiersz raportu zapisany)")
            continue
        mk = _variants(macd, sig, full_macd=[None if pd.isna(v) else float(v)
                                              for v in batch.features["macd"]])
        full_ts = [str(x) for x in batch.features.index]
        top = mk["top"]
        # Marker dostaje TYLKO jedno najwieksze wychylenie. Lokalne doliny zostaja
        # w payloadzie do profilu i statystyk, ale nie sa rysowane.
        payload["local_valleys"] = mk["local_valleys"]
        payload["macd_std"] = round(mk["macd_std"], 8)
        payload["threshold"] = round(mk["threshold"], 8)
        disp_start = len(batch.features) - len(disp)
        payload["top_excursion"] = None if top is None else {
            "index_full": top["index"],
            "index_display": top["index"] - disp_start,
            "in_view": bool(top["index"] >= disp_start),
            "date": full_ts[top["index"]][:16],
            "macd": round(top["macd"], 6),
            "macd_std": round(mk["macd_std"], 6),
            "threshold": round(mk["threshold"], 6),
            "left": round(top["left"], 6), "right": round(top["right"], 6),
            "prominence": round(top["prominence"], 6),
            "local_count": len(mk["local_valleys"])}
        payload["schema"] = PAYLOAD_SCHEMA
        payload["segmentation_variant"] = __import__("v3.macd_excursions",
                                                     fromlist=["x"]).APPROVED_VARIANT
        payload["segmentation_level"] = __import__("v3.macd_excursions",
                                                   fromlist=["x"]).APPROVED_LEVEL
        payload["segmentation"] = {}          # brak siatki wariantow w produkcji
        payload["segmentation_overlap"] = {
            "count_local_valleys": len(mk["local_valleys"]),
            "has_top": top is not None}
        payload["segmentation_status"] = (
            "Zatwierdzona segmentacja B 0,25 - %d lokalnych dolin, 1 najwieksze"
            " wychylenie" % len(mk["local_valleys"]))
        timing["variants"] += _time.time() - t
        payloads["%s|%s" % (symbol, tf)] = payload
        rows.append({"symbol": symbol, "tf": tf,
                     "bars": payload["quality"]["display_bars"],
                     "local_valleys": len(mk["local_valleys"]),
                     "top_date": (payload["top_excursion"]["date"] if top else ""),
                     "top_prominence": (payload["top_excursion"]["prominence"]
                                        if top else ""),
                     "macd_std": round(mk["macd_std"], 4)})
        print("%s %s: lokalnych dolin B 0,25 = %d, najwieksze wychylenie: %s"
              % (symbol, tf, len(mk["local_valleys"]),
                 payload["top_excursion"]["date"] if top else "brak"), flush=True)

    timing["total"] = _time.time() - t_sym
    timing["requests"] = diag["requests"]
    _log("DONE", symbol, t_sym, "zapytan=%d" % diag["requests"])
    return payloads, rows, timing


def _payload_dir(out_dir):
    return os.path.join(out_dir, "payloads")


def _save_payloads(out_dir, payloads):
    """Kazdy payload jako osobny plik - to jest CANONICAL PARTIAL STORAGE."""
    d = _payload_dir(out_dir)
    os.makedirs(d, exist_ok=True)
    for key, p in payloads.items():
        path = os.path.join(d, key.replace("|", "_") + ".json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(p, fh, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)


def load_all_payloads(out_dir):
    """Wszystkie ukonczone payloady z dysku - zrodlo prawdy dla dashboardu.

    Dashboard NIGDY nie jest budowany z tego, co akurat jest w pamieci procesu:
    czytamy komplet plikow, wiec kazda przebudowa zawiera wszystkie gotowe spolki.
    """
    d = _payload_dir(out_dir)
    out = {}
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, fn), "r", encoding="utf-8") as fh:
                p = json.load(fh)
            out["%s|%s" % (p["symbol"], p["tf"])] = p
        except Exception as exc:
            print("  pominieto uszkodzony payload %s: %s" % (fn, exc), flush=True)
    return out


def validate_done(out_dir, symbol, timeframes=ALL_TIMEFRAMES, rows=None):
    """Czy symbol mozna bezpiecznie pominac przy wznowieniu.

    Sam znacznik `done` NIE wystarcza - to bylo zrodlo bledu, w ktorym RBLX i AAOI
    znikaly z dashboardu mimo wpisu o ukonczeniu. Wymagamy kompletu payloadow, ktore
    daja sie odczytac, zgadzaja sie co do symbolu i interwalu, maja aktualna
    konfiguracje segmentacji, a 1D ma produkcyjne wychylenia B 0,25 i 1H ich nie ma.

    Zwraca (ok, powod).
    """
    import v3.macd_excursions as MX
    d = _payload_dir(out_dir)
    for tf in timeframes:
        path = os.path.join(d, "%s_%s.json" % (symbol, tf))
        if not os.path.isfile(path):
            return False, "STALE_DONE_MISSING_PAYLOAD (%s %s)" % (symbol, tf)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                pl = json.load(fh)
        except Exception as exc:
            return False, "STALE_DONE_CORRUPT_PAYLOAD (%s: %s)" % (tf, exc)
        if pl.get("symbol") != symbol or pl.get("tf") != tf:
            return False, "STALE_DONE_SYMBOL_MISMATCH (%s)" % tf
        if pl.get("schema") != PAYLOAD_SCHEMA:
            return False, "STALE_DONE_SCHEMA_MISMATCH (%s)" % tf
        if tf == SEGMENTATION_TIMEFRAME:
            if "local_valleys" not in pl or "top_excursion" not in pl:
                return False, "STALE_DONE_NO_APPROVED_EXCURSIONS (1D)"
            if pl.get("segmentation_variant") != MX.APPROVED_VARIANT \
                    or pl.get("segmentation_level") != MX.APPROVED_LEVEL:
                return False, "STALE_DONE_SEGMENTATION_CHANGED (1D)"
        else:
            if pl.get("local_valleys") or pl.get("top_excursion"):
                return False, "STALE_DONE_1H_HAS_EXCURSIONS (%s)" % tf
    if rows is not None:
        have = {(r.get("symbol"), r.get("tf")) for r in rows if not r.get("_stale")}
        missing = [tf for tf in timeframes if (symbol, tf) not in have]
        if missing:
            return False, "STALE_DONE_MISSING_ROW (%s)" % ", ".join(missing)
    return True, "OK"


def missing_timeframes(out_dir, symbol, timeframes=ALL_TIMEFRAMES, rows=None):
    """Ktore pary symbol-TF trzeba zbudowac. Reszta zostaje NIETKNIETA.

    Sprawdzamy kazdy interwal osobno, wiec symbol z aktualnym 1D i 1H, a bez 30m,
    2H i 4H, buduje wylacznie te trzy - istniejacych wynikow r591 nie przeliczamy
    i nie pobieramy ponownie.
    """
    todo = []
    for tf in timeframes:
        ok, why = validate_done(out_dir, symbol, (tf,), rows)
        if ok:
            continue
        if "MISSING_PAYLOAD" in why:
            _log("MISSING_PAYLOAD", symbol, None, "%s %s" % (symbol, tf))
        elif "MISSING_ROW" in why:
            _log("MISSING_REPORT_ROW", symbol, None, "%s %s" % (symbol, tf))
        elif "SCHEMA" in why:
            _log("STALE_SCHEMA", symbol, None, "%s %s" % (symbol, tf))
        else:
            _log("REBUILD", symbol, None, "%s %s: %s" % (symbol, tf, why))
        todo.append(tf)
    return todo


# Kolumny wymagane przez schemat r579. Brak ktorejkolwiek w starym results.csv
# oznacza wiersz sprzed migracji - symbol trzeba przebudowac, a nie pominac.
REQUIRED_ROW_FIELDS = ("symbol", "tf", "bars", "local_valleys", "top_date",
                       "top_prominence", "macd_std")
INT_ROW_FIELDS = ("bars", "local_valleys")


def row_from_payload(payload):
    """Odtwarza wiersz raportu z ISTNIEJACEGO payloadu - bez pobierania i liczenia."""
    tf = payload.get("tf")
    top = payload.get("top_excursion") or {}
    if tf == SEGMENTATION_TIMEFRAME:
        return {"symbol": payload.get("symbol"), "tf": tf,
                "bars": int((payload.get("quality") or {}).get("display_bars", 0)),
                "local_valleys": len(payload.get("local_valleys") or []),
                "top_date": top.get("date", ""),
                "top_prominence": top.get("prominence", ""),
                "macd_std": payload.get("macd_std", "")}
    return {"symbol": payload.get("symbol"), "tf": tf,
            "bars": int((payload.get("quality") or {}).get("display_bars", 0)),
            "local_valleys": 0, "top_date": "", "top_prominence": "",
            "macd_std": ""}


def repair_missing_rows(out_dir, rows, wanted, timeframes=ALL_TIMEFRAMES):
    """Uzupelnia brakujace wiersze raportu z payloadow lezacych juz na dysku.

    Stan odziedziczony po r585: payloady 1D+1H kompletne, ale results.csv bez
    wierszy 1H dla czesci spolek. Odtworzenie wiersza z payloadu jest natychmiastowe
    - zero zapytan do Massive, zero przeliczania wskaznikow.

    Zwraca (rows, repaired, unrepairable).
    """
    have = {(r.get("symbol"), r.get("tf")) for r in rows if not r.get("_stale")}
    payloads = load_all_payloads(out_dir)
    repaired, unrepairable = [], []
    for sym in wanted:
        for tf in timeframes:
            if (sym, tf) in have:
                continue
            pl = payloads.get("%s|%s" % (sym, tf))
            if pl is None:
                unrepairable.append((sym, tf, "brak payloadu"))
                continue
            if pl.get("schema") != PAYLOAD_SCHEMA:
                unrepairable.append((sym, tf, "payload w starym schemacie"))
                continue
            if tf == SEGMENTATION_TIMEFRAME and "local_valleys" not in pl:
                unrepairable.append((sym, tf, "payload bez local_valleys"))
                continue
            rows.append(row_from_payload(pl))
            repaired.append((sym, tf))
            _log("REPAIR_MISSING_ROW", sym, None, "%s FROM_PAYLOAD" % tf)
    return rows, repaired, unrepairable


def _load_rows(out_dir):
    """Wiersze raportu z dysku, odporne na pliki ze starszych wersji.

    results.csv z r573 nie mial kolumn local_valleys, top_date, top_prominence
    ani macd_std - bezwarunkowe r[k] wywracalo caly przebieg z KeyError. Teraz
    brakujace pola dostaja jawne wartosci domyslne, a wiersz jest oznaczany jako
    STALE, zeby symbol trafil do przebudowy zamiast zostac uznany za gotowy.

    Zwraca (rows, stale_symbols).
    """
    path = os.path.join(out_dir, "results.csv")
    if not os.path.isfile(path):
        return [], set()
    rows, stale = [], set()
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                missing = [k for k in REQUIRED_ROW_FIELDS if k not in r or r[k] is None]
                sym = r.get("symbol") or "?"
                if missing:
                    stale.add(sym)
                    _log("REBUILD_STALE_SCHEMA", sym, None,
                         "brakuje kolumn: %s" % ", ".join(missing))
                # Rekord budowany OD NOWA wylacznie z pol aktualnego schematu -
                # dawne kolumny diagnostyczne (a, b025, b050, c, all_three, only_*)
                # nie moga trafic do DictWriter, ktory ich nie zna.
                clean = {}
                for k in REQUIRED_ROW_FIELDS:
                    clean[k] = r.get(k, "")
                for k in INT_ROW_FIELDS:
                    try:
                        clean[k] = int(clean[k] or 0)
                    except (TypeError, ValueError):
                        clean[k] = 0
                        stale.add(sym)
                # Wiersz sprzed migracji NIE jest danymi - zera z wartosci domyslnych
                # nie moga trafic do raportu jako policzony wynik.
                if sym in stale:
                    clean["_stale"] = True
                rows.append(clean)
    except Exception as exc:
        # Uszkodzony plik nie moze przerwac batcha - startujemy z pusta tabela.
        _log("REBUILD_STALE_SCHEMA", "", None,
             "nieczytelny results.csv (%s) - tabela liczona od nowa" % exc)
        return [], set()
    return rows, stale


def pair_completeness(out_dir, wanted, timeframes=ALL_TIMEFRAMES):
    """Kompletnosc liczona na PARACH symbol-TF, nie na samych symbolach.

    6 spolek x 5 interwalow = 30 wymaganych payloadow. Symbol z samym 1D i 1H NIE
    jest gotowy - brakujaca para jest raportowana z nazwa, np. "PLTR 2H".
    """
    have = set()
    for pl in load_all_payloads(out_dir).values():
        have.add((pl.get("symbol"), pl.get("tf")))
    need = {(s, tf) for s in wanted for tf in timeframes}
    missing_pairs = sorted(need - have)
    ready_symbols = sorted({s for s in wanted
                            if all((s, tf) in have for tf in timeframes)})
    return {"need": len(need), "have": len(need) - len(missing_pairs),
            "missing_pairs": missing_pairs,
            "ready_symbols": ready_symbols,
            "missing_symbols": sorted({s for s, _tf in missing_pairs})}


def final_status(out_dir, wanted, status, timeframes=ALL_TIMEFRAMES):
    """COMPLETE tylko wtedy, gdy dashboard naprawde ma komplet symboli.

    Wczesniej status bral sie z samego przebiegu petli, wiec przebieg konczacy sie
    czterema spolkami w dashboardzie i tak raportowal COMPLETE i kod 0. Teraz liczymy
    to, co faktycznie lezy w partial storage.
    """
    pc = pair_completeness(out_dir, wanted, timeframes)
    if pc["missing_pairs"]:
        return "PARTIAL_COMPLETE", pc["missing_symbols"]
    return status, []


def _write_all(out_dir, payloads, rows, errors, timings, status, save=True,
               timeframes=ALL_TIMEFRAMES):
    """Zapis partial storage, a potem przebudowa dashboardu z CALEGO storage."""
    from v3.tools.macd_segmentation_template import render_review
    import config
    os.makedirs(out_dir, exist_ok=True)
    if save and payloads:
        _save_payloads(out_dir, payloads)
    all_payloads = load_all_payloads(out_dir)        # komplet z dysku, nie z pamieci
    symbols = sorted({p["symbol"] for p in all_payloads.values()})
    pc = pair_completeness(out_dir, FAST_SET, timeframes)
    build = {"build_id": config.VERSION,
             "generated": "%s · %d/%d symboli · TF %d/%d%s"
                          % (_dt.datetime.now().strftime("%H:%M:%S"),
                             len(pc["ready_symbols"]), len(FAST_SET),
                             pc["have"], pc["need"],
                             "" if status == "COMPLETE" else " · " + status)}

    idx = os.path.join(out_dir, "index.html")
    tmp = idx + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(render_review(all_payloads, rows, errors, build))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, idx)
    _log("DASHBOARD", "", None, "%s | %s" % (idx, ", ".join(symbols) or "(pusty)"))

    with open(os.path.join(out_dir, "progress.json"), "w", encoding="utf-8") as fh:
        json.dump({"status": status, "diag_version": DIAG_VERSION,
                   "dashboard_symbols": symbols,
                   "done": sorted({r["symbol"] for r in rows}), "errors": errors,
                   "timings": timings, "generated": build["generated"]},
                  fh, ensure_ascii=False, indent=1)

    with open(os.path.join(out_dir, "results.csv"), "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["symbol", "tf", "bars",
                                           "local_valleys", "top_date",
                                           "top_prominence", "macd_std"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in REQUIRED_ROW_FIELDS})

    lines = ["# WYCHYLENIA MACD — SKAN", "",
             "Zatwierdzona segmentacja: wariant B, prog 0,25 x odchylenie MACD,"
             " bez min. odleglosci · %s · build %s"
             % (build["generated"], build["build_id"]), "",
             "Historyczne wychylenia liczone wylacznie na 1D.", "",
             "| Symbol | TF | Barow | lokalnych dolin B 0,25 | najwieksze wychylenie |"
             " prominencja | std(MACD) |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("_stale"):
            lines.append("| %s | %s | %s | (do przeliczenia) | - | - | - |"
                         % (r["symbol"], r["tf"], r["bars"]))
            continue
        if r["tf"] != SEGMENTATION_TIMEFRAME:
            lines.append("| %s | %s | %s | historyczne wychylenia wylaczone | - | - | - |"
                         % (r["symbol"], r["tf"], r["bars"]))
            continue
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (r["symbol"], r["tf"], r["bars"], r["local_valleys"],
                        r.get("top_date") or "-", r.get("top_prominence") or "-",
                        r.get("macd_std") or "-"))
    if timings:
        lines += ["", "## Czasy", "",
                  "| Symbol | zapytań | pobranie | budowa | warianty | razem |",
                  "|---|---|---|---|---|---|"]
        for sym, t in timings.items():
            lines.append("| %s | %d | %.1fs | %.1fs | %.1fs | %.1fs |"
                         % (sym, t.get("requests", 0), t["fetch"], t["build"],
                            t["variants"], t["total"]))
    if errors:
        lines += ["", "## Błędy", ""] + ["- %s: %s" % (e["symbol"], e["error"])
                                         for e in errors]
    lines += ["", "## Segmentacja", "",
              "Zatwierdzona: wariant B, prog 0,25 x odchylenie MACD, bez minimalnej"
              " odleglosci, historyczne wychylenia wylacznie na 1D.", "",
              "Lokalne doliny B 0,25 zasilaja profil, srednia, mediane i ranking."
              " Na wykresie renderowane jest wylacznie JEDNO najwieksze historyczne"
              " wychylenie (max prominencja, przy remisie nowsze).", "",
              "Oddzielne narzedzie diagnostyczne:",
              "wyniki-v3-2/porownanie-wariantow/"]
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return build


def run(out_dir, symbols=None, timeframes=ALL_TIMEFRAMES, resume=True,
        force_symbols=()):
    t_run = _time.time()
    universe = {r["symbol"] for r in CV.load_universe_rows()}
    wanted = [s for s in (symbols or FAST_SET) if s in universe]
    missing = [s for s in (symbols or FAST_SET) if s not in universe]
    if missing:
        _log("POMINIETE", ",".join(missing), None, "brak w canonical Universe")

    payloads, rows, errors, timings = {}, [], [], {}
    rows, stale_rows = _load_rows(out_dir) if resume else ([], set())
    done_before = set()
    prog = os.path.join(out_dir, "progress.json")
    if resume and os.path.isfile(prog):
        try:
            old = json.load(open(prog, "r", encoding="utf-8"))
            if old.get("diag_version") == DIAG_VERSION:
                done_before = set(old.get("done", []))
                if done_before:
                    _log("RESUME", "", None, "gotowe: %s" % ", ".join(sorted(done_before)))
        except Exception:
            pass
    else:
        rows, stale_rows = [], set()

    # Samonaprawa: brakujacy wiersz odtwarzamy z payloadu, zanim zdecydujemy o SKIP.
    if resume:
        rows, repaired, unrepairable = repair_missing_rows(out_dir, rows, wanted,
                                                           timeframes)
        if repaired:
            _log("REPAIR", "", None, "odtworzono %d wierszy z payloadow" % len(repaired))
        for sym_u, tf_u, why_u in unrepairable:
            _log("PRZELICZAM", sym_u, None,
                 "brak wiersza i brak zrodla (%s %s)" % (tf_u, why_u))
            stale_rows.add(sym_u)
    force = {s.upper() for s in (force_symbols or ())}
    now = pd.Timestamp.now(tz="UTC")
    status = "COMPLETE"
    opened = False
    for sym in wanted:
        todo = list(timeframes)
        if sym in force:
            _log("FORCE", sym, None, "wymuszone przeliczenie (--force-symbol)")
        elif sym in stale_rows:
            _log("STALE_SCHEMA", sym, None,
                 "wiersz raportu sprzed migracji - komplet interwalow od nowa")
        elif resume:
            # Selektywnie: budujemy WYLACZNIE brakujace pary, reszta zostaje nietknieta.
            todo = missing_timeframes(out_dir, sym, timeframes, rows)
            if not todo:
                _log("SKIP_ALREADY_DONE", sym, None,
                     "komplet %d payloadow i wierszy" % len(timeframes))
                continue
            reuse = [t for t in timeframes if t not in todo]
            _log("BUILD_MISSING_TF", sym, None, "buduje: %s%s"
                 % (", ".join(todo),
                    ("  ponownie uzyte: " + ", ".join(reuse)) if reuse else ""))
        if _time.time() - t_run > HARD_LIMIT_S:
            status = "PARTIAL_COMPLETE"
            _log("LIMIT CZASU", sym, t_run, "konczę grzecznie")
            break
        try:
            p, r, tm = process_symbol(sym, now, tuple(todo))
            payloads.update(p)
                # Przebudowany rekord ZASTEPUJE stary wpis tego samego symbolu i TF.
            rows = [x for x in rows
                    if not (x.get("symbol") == sym
                            and x.get("tf") in {y.get("tf") for y in r})]
            rows.extend(r)
            timings[sym] = tm
            if tm["total"] > SYMBOL_WARN_S:
                left = len([s for s in wanted if s not in timings])
                est = tm["total"] * left
                _log("UWAGA", sym, None, "spolka >10 min; szacowana reszta %.0f min"
                     % (est / 60.0))
                if _time.time() - t_run + est > HARD_LIMIT_S:
                    status = "PARTIAL_COMPLETE"
                    _log("REDUKCJA ZESTAWU", "", None, "szacowany czas > limitu")
                    _write_all(out_dir, payloads, rows, errors, timings, status,
                               timeframes=timeframes)
                    break
        except Exception as exc:
            import traceback
            traceback.print_exc()
            errors.append({"symbol": sym, "error": "%s: %s" % (type(exc).__name__, exc)})
            _log("BLAD", sym, None, str(exc)[:80])
            continue
        # Brak ktoregokolwiek interwalu = symbol NIE jest gotowy.
        got_tf = {k.split("|")[1] for k in p}
        for tf_missing in sorted(set(todo) - got_tf):
            errors.append({"symbol": sym,
                           "error": "MISSING_PAYLOAD %s %s" % (sym, tf_missing)})
            _log("MISSING_PAYLOAD", sym, None, "%s %s" % (sym, tf_missing))
        # partial storage + przebudowa dashboardu z KOMPLETU ukonczonych spolek
        _write_all(out_dir, payloads, rows, errors, timings, "RUNNING",
                   timeframes=timeframes)
        if not opened:
            opened = True
            if OPEN_DASHBOARD:
                try:
                    os.startfile(os.path.join(out_dir, "index.html"))  # noqa: S606
                    _log("DASHBOARD", "", None,
                         "otwarty - kolejne spolki doklejaja sie (F5)")
                except Exception:
                    pass

    status, missing = final_status(out_dir, wanted, status, timeframes)
    # COMPLETE wymaga zgodnosci warstw: payloady, wiersze raportu i liczniki.
    row_pairs = {(r.get("symbol"), r.get("tf")) for r in rows if not r.get("_stale")}
    need_pairs = {(sym, tf) for sym in wanted for tf in timeframes}
    row_missing = sorted(need_pairs - row_pairs)
    if row_missing and status == "COMPLETE":
        status = "PARTIAL_COMPLETE"
        missing = sorted({s for s, _t in row_missing})
        _log("MISSING_REPORT_ROW", "", None,
             "payloady kompletne, brak wierszy raportu: %s"
             % ", ".join("%s %s" % pr for pr in row_missing))
    build = _write_all(out_dir, payloads, rows, errors, timings, status,
                       timeframes=timeframes)
    total = _time.time() - t_run
    net = sum(t["fetch"] for t in timings.values())
    print("\n" + "=" * 60, flush=True)
    print("SZYBKI SKAN PRODUKCYJNY - %s" % status, flush=True)
    print("  czas calkowity:   %.1f min" % (total / 60.0), flush=True)
    print("  w tym siec:       %.1f min (%.0f%%)"
          % (net / 60.0, 100.0 * net / total if total else 0), flush=True)
    for tf in timeframes:
        print("  wierszy %-5s     %d" % (tf + ":",
              len([r for r in rows if r["tf"] == tf])), flush=True)
    if timings:
        slow = max(timings.items(), key=lambda kv: kv[1]["total"])
        print("  najwolniejsza:    %s (%.0fs)" % (slow[0], slow[1]["total"]), flush=True)
        print("  zapytan lacznie:  %d" % sum(t.get("requests", 0)
                                             for t in timings.values()), flush=True)
    have = {p["symbol"] for p in load_all_payloads(out_dir).values()}
    pcf = pair_completeness(out_dir, wanted, timeframes)
    print("  w dashboardzie:   %d/%d symboli · TF %d/%d"
          % (len(have), len(wanted), pcf["have"], pcf["need"]), flush=True)
    for pair in pcf["missing_pairs"]:
        print("  BRAK PARY:        %s %s" % pair, flush=True)
    if missing:
        print("  BRAKUJE:          %s" % ", ".join(missing), flush=True)
    print("  dashboard:        %s" % os.path.join(out_dir, "index.html"), flush=True)
    print("=" * 60, flush=True)
    return {"status": status, "rows": rows, "errors": errors, "build": build,
            "out_dir": out_dir, "missing": missing,
            "complete": not missing}


def rebuild(out_dir):
    """Przebudowa dashboardu z istniejących partial results — zero fetch, zero liczenia."""
    t = _time.time()
    payloads = load_all_payloads(out_dir)
    rows, _stale = _load_rows(out_dir)
    if not payloads:
        print("BRAK partial results w %s" % _payload_dir(out_dir), flush=True)
        return {"symbols": [], "rows": rows}
    build = _write_all(out_dir, {}, rows, [], {}, "REBUILD", save=False)
    symbols = sorted({p["symbol"] for p in payloads.values()})
    print("PRZEBUDOWANO w %.2fs - spolki: %s"
          % (_time.time() - t, ", ".join(symbols)), flush=True)
    return {"symbols": symbols, "rows": rows, "build": build}


def main(argv=None):
    p = argparse.ArgumentParser(description="V3.2A szybki skan produkcyjny wychylen MACD")
    p.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "wyniki-v3-2",
        "fast-segmentation"))
    p.add_argument("--only", default=None)
    p.add_argument("--tf", default=",".join(ALL_TIMEFRAMES))
    p.add_argument("--fresh", action="store_true", help="ignoruj poprzedni postep")
    p.add_argument("--force-symbol", nargs="+", default=[], dest="force_symbol",
                   help="wymus ponowne przeliczenie wskazanych symboli")
    p.add_argument("--rebuild", action="store_true",
                   help="przebuduj dashboard z partial results (bez pobierania)")
    a = p.parse_args(argv)
    if a.rebuild:
        return 0 if rebuild(a.out)["symbols"] else 1
    syms = [s.strip().upper() for s in a.only.split(",")] if a.only else None
    res = run(a.out, syms, tuple(t.strip() for t in a.tf.split(",")),
              resume=not a.fresh, force_symbols=a.force_symbol)
    # Niekompletny dashboard NIE moze konczyc sie kodem 0.
    return 0 if (res["rows"] and res["complete"]) else 1


if __name__ == "__main__":
    sys.exit(main())

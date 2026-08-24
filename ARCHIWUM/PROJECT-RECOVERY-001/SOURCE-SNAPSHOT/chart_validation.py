"""backend/v3/tools/chart_validation.py — V3.1B KONTROLA WYKRESÓW RZECZYWISTYCH SPÓŁEK.

READ ONLY harness walidacyjny: 19 spółek wskazanych przez właściciela → realne dane
Massive → canonical V3 (1D: CANONICAL ANALYSIS; 1H: rebuilt z 30m) → locked wskaźniki
przez V3.1A Feature Engine → jeden lokalny dashboard HTML do ręcznego porównania
z TradingView.

Zasady:
- symbole rozwiązywane z ISTNIEJĄCEJ bazy Universe (scanner.db, read only) — zero
  zgadywania z pamięci; AMBIGUOUS/NOT_FOUND raportowane, nie blokują pozostałych,
- dane WYŁĄCZNIE Massive (zero Yahoo/Stooq/TradingView fetch),
- warstwa wykresu niczego nie sortuje, nie deduplikuje, nie filluje i nie poprawia,
- brak canonical H/L => świeca NIE jest dorabiana z raw (rysowany jest tylko close
  z jawnym oznaczeniem BRAK PEŁNYCH DANYCH H/L),
- wskaźniki liczone na PEŁNYM pobraniu (pre-roll 500), okno wyświetlania to osobne
  tail(120),
- tylko bary FINAL (finality z kalendarza NYSE + as_of, nigdy z pozycji wiersza),
- zero scoringu, zero BUY/SELL, zero integracji z produkcją.
"""

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys
import time as _time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from v3.features import build_atomic_features  # noqa: E402
from v3.features.schema import FeatureBatchMeta  # noqa: E402
from v3.market_data import us_calendar as CAL  # noqa: E402
from v3.market_data import warmup as W  # noqa: E402
from v3.market_data.daily_analysis import build_daily_analysis  # noqa: E402
from v3.market_data.us_rth import aggregate_1h_from_lower, session_date_of  # noqa: E402

DISPLAY_BARS = 120
FETCH_1D_SESSIONS = 640          # 500 pre-roll + 120 okno + margines świąt
FETCH_1H_DAYS = 130              # ~90 sesji * 7 barów > 620 barów 1H

# Lista właściciela — ZAMKNIĘTA (19 pozycji, nazwy verbatim).
REQUESTED_COMPANIES = (
    "Roblox", "Intuit", "Nvidia", "Adtran Holdings", "Palantir", "Oracle",
    "Nebius", "Figma", "Lumentum", "Applied Optoelectronics", "Zscaler",
    "Datadog", "Coherent", "Apple", "Super Micro Computer", "Delta Air Lines",
    "Morgan Stanley", "Bank of America", "Novo Nordisk")

_LEGAL_SUFFIXES = ("inc", "inc.", "corp", "corp.", "corporation", "ltd", "ltd.",
                   "plc", "co", "co.", "company", "n.v", "n.v.", "nv", "a/s", "sa",
                   "s.a.", "class a", "class b", "class c", "adr", "ads",
                   "sponsored adr", "holdings", "holding", "group", "the")


def _norm(s):
    return " ".join(str(s or "").lower().replace(",", " ").replace("(", " ")
                    .replace(")", " ").split())


def _strip_legal(name):
    words = _norm(name).split()
    while words and words[-1] in _LEGAL_SUFFIXES:
        words = words[:-1]
    # dwuwyrazowe sufiksy typu "class a"
    while len(words) >= 2 and " ".join(words[-2:]) in _LEGAL_SUFFIXES:
        words = words[:-2]
    return " ".join(words)


def resolve_companies(requested, universe_rows):
    """Deterministyczne rozwiązanie nazw właściciela na symbole z bazy Universe.

    Kolejność reguł (bez zgadywania):
      1. requested == symbol (case-insensitive)            -> RESOLVED_EXACT
      2. requested == pełna nazwa w bazie                  -> RESOLVED_EXACT
      3. requested == nazwa po zdjęciu sufiksów prawnych   -> RESOLVED_EXACT
         (dokładnie jeden kandydat)
      4. dokładnie jedna nazwa w bazie zawiera requested
         jako prefiks słowny                               -> RESOLVED_UNIQUE
      5. wielu kandydatów                                  -> AMBIGUOUS
      6. zero                                              -> NOT_FOUND
    """
    out = []
    for req in requested:
        rn = _norm(req)
        by_symbol = [r for r in universe_rows
                     if _norm(r.get("symbol")) == rn]
        exact_name = [r for r in universe_rows if _norm(r.get("name")) == rn]
        stripped = [r for r in universe_rows if _strip_legal(r.get("name")) == rn]
        prefix = [r for r in universe_rows
                  if _norm(r.get("name")).startswith(rn + " ")
                  or _norm(r.get("name")) == rn]
        contains = [r for r in universe_rows if rn in _norm(r.get("name"))]
        row, status = None, "NOT_FOUND"
        if len(by_symbol) == 1:
            row, status = by_symbol[0], "RESOLVED_EXACT"
        elif len(exact_name) == 1:
            row, status = exact_name[0], "RESOLVED_EXACT"
        elif len(stripped) == 1:
            row, status = stripped[0], "RESOLVED_EXACT"
        elif len(prefix) == 1:
            row, status = prefix[0], "RESOLVED_UNIQUE"
        elif len(contains) == 1:
            row, status = contains[0], "RESOLVED_UNIQUE"
        elif len(prefix) > 1 or len(contains) > 1:
            status = "AMBIGUOUS"
        out.append({"requested_name": req,
                    "symbol": (row or {}).get("symbol"),
                    "company_name": (row or {}).get("name"),
                    "exchange": (row or {}).get("exchange"),
                    "status": status,
                    "candidates": sorted({r.get("symbol") for r in (prefix or contains)})[:6]
                    if status == "AMBIGUOUS" else []})
    return out


def load_universe_rows():
    """Read-only odczyt spisu spółek z istniejącej bazy (config.DB_PATH)."""
    import config
    if not os.path.isfile(config.DB_PATH):
        raise FileNotFoundError("UNIVERSE_DB_MISSING: %s" % config.DB_PATH)
    conn = sqlite3.connect("file:%s?mode=ro" % config.DB_PATH.replace("\\", "/"),
                           uri=True)
    try:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(
            "SELECT symbol, name, exchange FROM universe").fetchall()]
    finally:
        conn.close()


# ------------------------------------------------------------------ Massive
def _massive_get(path, params):
    import polygon_source
    if not polygon_source.enabled():
        raise RuntimeError("MASSIVE_REFERENCE_UNAVAILABLE: brak klucza API")
    data = polygon_source._get(path, params)
    if not data or not data.get("results"):
        raise RuntimeError("MASSIVE_DATA_UNAVAILABLE")
    return data["results"]


def _aggs(symbol, mult, span, day_from, day_to):
    return _massive_get("/v2/aggs/ticker/%s/range/%d/%s/%s/%s"
                        % (symbol, mult, span, day_from.isoformat(),
                           day_to.isoformat()),
                        {"adjusted": "true", "sort": "asc", "limit": 50000})


def chunk_spans(day_from, day_to, chunk_days=60):
    """Czyste wyznaczenie kawałków zapytania: pełne pokrycie, zero nakładek i dziur."""
    spans, cur = [], day_from
    while cur <= day_to:
        end = min(cur + _dt.timedelta(days=chunk_days - 1), day_to)
        spans.append((cur, end))
        cur = end + _dt.timedelta(days=1)
    return spans


def _aggs_chunked(symbol, mult, span, day_from, day_to, chunk_days=60):
    """Pobranie intraday w kawałkach ~2-miesięcznych.

    ROOT CAUSE RBLX 575/681 bez H/L: jedno zapytanie o 30m za ~2,7 roku było ucinane
    przez limit wierszy odpowiedzi Massive (sort asc => zostawała najstarsza część,
    nowe sesje bez pokrycia). Kawałek 60 dni to <1500 wierszy 30m — zawsze pod limitem.
    Pusty kawałek (młoda spółka przed debiutem) nie jest błędem całości.
    """
    out, any_data = [], False
    for cur, end in chunk_spans(day_from, day_to, chunk_days):
        try:
            out.extend(_aggs(symbol, mult, span, cur, end))
            any_data = True
        except RuntimeError as exc:
            if "MASSIVE_DATA_UNAVAILABLE" not in str(exc):
                raise
    if not any_data:
        raise RuntimeError("MASSIVE_DATA_UNAVAILABLE")
    return out


def _results_to_frame(results):
    idx, rows = [], []
    for r in results:
        ts = pd.Timestamp(int(r["t"]), unit="ms", tz="UTC")
        idx.append(ts)
        rows.append((float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]),
                     float(r.get("v", 0.0))))
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"],
                      index=pd.DatetimeIndex(idx, name="bar_open_utc"))
    return df


def fetch_canonical_1d(symbol, now_utc=None):
    """Massive native 1D + 30m (CHUNKED) -> CANONICAL ANALYSIS 1D + pokrycie 30m."""
    now = now_utc or pd.Timestamp.now(tz="UTC")
    day_to = now.tz_convert(CAL.NY).date()
    day_from = day_to - _dt.timedelta(days=int(FETCH_1D_SESSIONS * 1.55))
    daily = _results_to_frame(_aggs(symbol, 1, "day", day_from, day_to))
    lower = _results_to_frame(_aggs_chunked(symbol, 30, "minute", day_from, day_to))
    if not lower.index.is_monotonic_increasing or not lower.index.is_unique:
        raise RuntimeError("MASSIVE_30M_CHUNKS_NOT_MONOTONIC: %s" % symbol)

    raw = pd.DataFrame(index=daily.index)
    raw["bar_close_utc"] = [CAL.session_schedule(session_date_of(ts))["close_utc"]
                            if CAL.session_schedule(session_date_of(ts)) else ts
                            for ts in daily.index]
    raw["session_date"] = [session_date_of(ts) for ts in daily.index]
    for col in ("open", "high", "low", "close", "volume"):
        raw[col] = daily[col]
    raw["is_final"] = [pd.Timestamp(bc) <= now for bc in raw["bar_close_utc"]]

    analysis, quality = build_daily_analysis(raw, lower)
    diag = {"native_1d_rows": int(len(daily)),
            "d1_from": str(day_from), "d1_to": str(day_to),
            "m30_rows": int(len(lower)),
            "m30_from": (str(session_date_of(lower.index[0])) if len(lower) else "-"),
            "m30_to": (str(session_date_of(lower.index[-1])) if len(lower) else "-"),
            "complete": sum(1 for q in quality.values()
                            if q.quality_status == "VERIFIED_LOWER_TF_COMPLETE"),
            "incomplete": sum(1 for q in quality.values()
                              if q.quality_status == "INCOMPLETE_LOWER_TF"),
            "no_coverage": sum(1 for q in quality.values()
                               if q.quality_status == "SOURCE_MISSING")}
    return analysis, quality, lower, diag


def fetch_canonical_1h(symbol, lower=None, now_utc=None):
    """Massive 30m -> canonical 1H (kompletne kubełki z kalendarza, [open, close))."""
    now = now_utc or pd.Timestamp.now(tz="UTC")
    if lower is None:
        day_to = now.tz_convert(CAL.NY).date()
        day_from = day_to - _dt.timedelta(days=FETCH_1H_DAYS)
        lower = _results_to_frame(_aggs(symbol, 30, "minute", day_from, day_to))
    rth = lower.loc[[ts for ts in lower.index if CAL.in_canonical_session(ts)]]
    sessions = sorted({session_date_of(ts) for ts in rth.index})
    have = set(rth.index)
    complete = []
    for day in sessions:
        expected = CAL.expected_30m_bar_opens(day)
        for b_open, b_end in CAL.expected_1h_buckets(day):
            need = [t for t in expected if b_open <= t < b_end]
            if need and all(t in have for t in need):
                complete.append((pd.Timestamp(b_open), pd.Timestamp(b_end)))
    rebuilt = aggregate_1h_from_lower(rth, session_dates=sessions)
    keep = [t for t, _ in complete if t in rebuilt.index]
    bars = rebuilt.loc[keep].copy()
    end_of = dict(complete)
    bars["bar_close_utc"] = [end_of[t] for t in bars.index]
    bars["session_date"] = [session_date_of(t) for t in bars.index]
    bars["is_final"] = [pd.Timestamp(end_of[t]) <= now for t in bars.index]
    return bars


# ------------------------------------------------------------------ payload
def _clean(v):
    if v is None:
        return None
    try:
        f = float(v)
        return None if f != f else round(f, 8)
    except (TypeError, ValueError):
        return str(v)


def ema(values, span):
    """EMA RENDERER-ONLY (V3.1B-UI): wyłącznie kontekst wizualny na panelu ceny.

    Liczona z canonical FINAL CLOSE na PEŁNEJ serii (pre-roll), dopiero potem
    przycinana do okna wyświetlania. NIE trafia do Feature Schema, eventów, scoringu
    ani nigdzie poza wykres.
    """
    out, prev, k = [], None, 2.0 / (span + 1.0)
    for v in values:
        if v is None or v != v:
            out.append(float("nan"))
            continue
        prev = float(v) if prev is None else (float(v) - prev) * k + prev
        out.append(prev)
    return out


def accumulation_distribution(highs, lows, closes, volumes):
    """A/D LINE RENDERER-ONLY (V3.1B-UI): standardowa Accumulation/Distribution Line.

    Dla każdego bara, gdy high != low:
        CLV = ((close - low) - (high - close)) / (high - low)
        MFV = CLV * volume
        AD[t] = AD[t-1] + MFV[t]
    Gdy high == low: CLV = 0 i MFV = 0 (bez dzielenia przez zero).

    Skumulowana, więc liczona na PEŁNEJ serii canonical przed przycięciem do okna.
    Wartość bezwzględna zależy od pierwszego bara historii, więc NIE jest obiecywana
    parity z TradingView — do walidacji służy przebieg, kierunek i punkty zwrotne.
    Seria diagnostyczna: nie trafia do Feature Schema, eventów ani scoringu.
    """
    out, ad = [], 0.0
    for h, l, c, v in zip(highs, lows, closes, volumes):
        try:
            h, l, c = float(h), float(l), float(c)
            v = 0.0 if v is None or v != v else float(v)
        except (TypeError, ValueError):
            out.append(float("nan"))
            continue
        if h != h or l != l or c != c:
            out.append(float("nan"))
            continue
        mfv = 0.0 if h == l else ((2.0 * c - h - l) / (h - l)) * v
        ad += mfv
        out.append(ad)
    return out


def _progress(done, total, t0, note=""):
    """Widoczny pasek postępu w oknie BAT (jedna linia, nadpisywana w miejscu)."""
    width = 34
    filled = 0 if not total else int(round(width * done / total))
    elapsed = _time.time() - t0
    eta = "" if done == 0 else "  pozostalo ~%s" % _fmt_secs(
        elapsed / done * (total - done))
    sys.stdout.write("\r  [%s%s] %2d/%d  %s%s%s"
                     % ("#" * filled, "." * (width - filled), done, total,
                        _fmt_secs(elapsed), eta, ("  " + note).ljust(26)))
    sys.stdout.flush()


def _fmt_secs(s):
    s = int(s)
    return "%d:%02d" % (s // 60, s % 60)


def build_symbol_payload(symbol, tf, bars, batch, display=DISPLAY_BARS,
                         daily_quality=None, events=None):
    """Czysta funkcja: bary + FeatureBatch -> JSON dla dashboardu (bez sieci).

    daily_quality (opcjonalnie, tylko 1D): session_date -> DailyBarQuality — pozwala
    ROZDZIELIĆ brak pokrycia 30m (NO_LOWER_TF_COVERAGE / SOURCE_MISSING) od realnie
    niekompletnej sesji (INCOMPLETE_LOWER_TF). To nie jest to samo i raport nie może
    nazywać braku pobrania „wadliwymi sesjami”.
    """
    f = batch.features
    disp = f.tail(display)
    vol = bars["volume"].reindex(disp.index) if "volume" in bars.columns else None
    candles = []
    for ts, row in disp.iterrows():
        hl_ok = row["price_hl_status"] in ("AVAILABLE", "ZERO_RANGE")
        b = bars.loc[ts] if ts in bars.index else None
        candles.append({
            "t": pd.Timestamp(ts).tz_convert(CAL.NY).isoformat(),
            "o": _clean(b["open"]) if b is not None else None,
            "h": _clean(b["high"]) if (b is not None and hl_ok) else None,
            "l": _clean(b["low"]) if (b is not None and hl_ok) else None,
            "c": _clean(row["close"]),
            "v": _clean(vol.loc[ts]) if vol is not None else None,
            "hl_ok": bool(hl_ok)})
    series = {col: [_clean(v) for v in disp[col].tolist()]
              for col in ("macd", "macd_signal", "macd_hist", "rsi", "rsi_helper",
                          "stoch_k", "stoch_d")}
    # Markery przeciec MACD: WYLACZNIE locked eventy z CM_ULT_MTF_TV_V1.
    # Renderer nie liczy przeciec od nowa - tylko potwierdza istniejace zdarzenie.
    for col in ("macd_cross_signal_up", "macd_cross_signal_down"):
        series[col] = [bool(v) for v in disp[col].tolist()]
    # EMA: pełna seria canonical final close -> dopiero potem tail(display)
    closes = f["close"].tolist()
    for span in (20, 50, 100):
        series["ema%d" % span] = [_clean(v) for v in ema(closes, span)[-len(disp):]]
    # A/D: skumulowana, więc licz na PEŁNEJ serii canonical, potem tail(display).
    # H/L wyłącznie canonical (brak canonical H/L => NaN, zero fallbacku do raw).
    hl_ok_mask = f["price_hl_status"].isin(["AVAILABLE", "ZERO_RANGE"])
    ad_h, ad_l, ad_v = [], [], []
    for ts, ok in zip(f.index, hl_ok_mask):
        b = bars.loc[ts] if ts in bars.index else None
        ad_h.append(float(b["high"]) if (b is not None and ok) else float("nan"))
        ad_l.append(float(b["low"]) if (b is not None and ok) else float("nan"))
        ad_v.append(float(b["volume"]) if (b is not None and "volume" in bars.columns)
                    else 0.0)
    series["ad"] = [_clean(v) for v in accumulation_distribution(
        ad_h, ad_l, closes, ad_v)[-len(disp):]]
    last = disp.iloc[-1] if len(disp) else None
    last_bar = ({} if last is None else {
        k: _clean(last[k]) for k in (
            "close", "return_1", "gap_from_prev_close", "range_pct", "body_pct",
            "close_location_in_range", "macd", "macd_signal", "macd_hist",
            "macd_hist_delta", "macd_state", "rsi", "rsi_delta", "rsi_helper",
            "rsi_state", "stoch_k", "stoch_d", "stoch_k_minus_d",
            "warmup_mode", "price_oc_status", "price_hl_status", "macd_status",
            "rsi_status", "stochastic_status")})
    missing_hl = int((~f["price_hl_status"].isin(["AVAILABLE", "ZERO_RANGE"])).sum())
    disp_missing = int((~disp["price_hl_status"].isin(["AVAILABLE",
                                                       "ZERO_RANGE"])).sum())
    no_cov = incomplete = None
    if daily_quality is not None:
        stats = [daily_quality[d].quality_status for d in f["session_date"]
                 if d in daily_quality]
        no_cov = int(sum(1 for s in stats if s == "SOURCE_MISSING"))
        incomplete = int(sum(1 for s in stats if s == "INCOMPLETE_LOWER_TF"))
    status = ("BRAK DANYCH" if not len(f)
              else ("DANE CZĘŚCIOWE" if disp_missing > 0 else "DANE PEŁNE"))
    return {"symbol": symbol, "tf": tf, "candles": candles, "series": series,
            "last_bar": last_bar,
            "events": _map_events(events, disp, tf),
            "last_final_close": (_clean(last["close"]) if last is not None else None),
            "quality": {"bars_requested": int(len(bars)),
                        "bars_available": int(len(bars)),
                        "final_bars": int(len(f)),
                        "display_bars": int(len(disp)),
                        "missing_hl": missing_hl,
                        "display_missing_hl": disp_missing,
                        "display_valid_hl": int(len(disp)) - disp_missing,
                        "no_lower_tf_coverage": no_cov,
                        "incomplete_lower_tf": incomplete,
                        "warmup_mode": batch.warmup_mode,
                        "latest_bar_time": (candles[-1]["t"] if candles else None),
                        "data_status": status}}


def _map_events(events, disp, tf):
    """Przypisanie WAZNYCH INFORMACJI do indeksow widocznych barow (renderer-only).

    Nie tworzy zdarzen i nie pobiera danych: przyjmuje gotowa liste
    {timestamp|session_date, title, description, type} z istniejacego payloadu.
    Brak payloadu => pusta lista => brak markerow. Dla 1D wiaze po session_date,
    dla 1H po timestampie; zdarzenie z sama data trafia na pierwszy bar tej sesji
    (godzina NIE jest wymyslana).
    """
    if not events:
        return []
    by_day, first_of_day = {}, {}
    for i, (ts, day) in enumerate(zip(disp.index, disp["session_date"])):
        by_day.setdefault(day, []).append((i, pd.Timestamp(ts)))
        first_of_day.setdefault(day, i)
    out = []
    for ev in events:
        raw_ts, raw_day = ev.get("timestamp"), ev.get("session_date")
        idx = None
        if raw_ts is not None and tf == "1H":
            want = pd.Timestamp(raw_ts)
            if want.tzinfo is None:
                want = want.tz_localize("UTC")
            best = None
            for i, ts in [p for lst in by_day.values() for p in lst]:
                if ts <= want and (best is None or ts > best[1]):
                    best = (i, ts)
            idx = None if best is None else best[0]
        if idx is None:
            day = raw_day if raw_day is not None else (
                pd.Timestamp(raw_ts).date() if raw_ts is not None else None)
            if day is not None and not isinstance(day, _dt.date):
                day = pd.Timestamp(day).date()
            idx = first_of_day.get(day)
        if idx is None:
            continue
        out.append({"i": int(idx), "title": str(ev.get("title") or ""),
                    "description": str(ev.get("description") or ""),
                    "type": str(ev.get("type") or "")})
    return out


def _warmup_for(tf, bars, range_start_day):
    final_count = int(bars["is_final"].sum())
    first_day = bars["session_date"].iloc[0] if len(bars) else None
    # początek historii znany, jeżeli pierwszy bar jest wyraźnie PO początku zakresu
    listing_known = bool(first_day and first_day > range_start_day
                         + _dt.timedelta(days=7))
    if final_count >= W.PRODUCTION_CANONICAL_PREROLL_BARS:
        return W.plan_warmup(tf, final_count, True)
    return W.plan_warmup(tf, final_count, listing_known)


def _write_dashboard(out_dir, index_path, resolution, payloads, errors,
                     render_index, partial=False):
    """Zapis dashboardu z tym, co JUZ jest gotowe (zapis atomowy przez plik .tmp).

    Wolane po kazdej spolce, zeby nie czekac na caly przebieg. `partial` trafia do
    naglowka jako informacja, ze reszta spolek jeszcze sie dolicza.
    """
    import config
    os.makedirs(os.path.join(out_dir, "data"), exist_ok=True)
    for key, p in payloads.items():
        with open(os.path.join(out_dir, "data", key.replace("|", "_") + ".json"),
                  "w", encoding="utf-8") as fh:
            json.dump(p, fh, ensure_ascii=False)
    build = {"build_id": config.VERSION,
             "generated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             + (" · w toku (%d gotowych)" % (len(payloads) // 2) if partial else "")}
    tmp = index_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(render_index(resolution, payloads, errors, build))
    os.replace(tmp, index_path)
    return build


def generate(out_dir, now_utc=None, only=None):
    from v3.tools.chart_validation_template import render_index
    universe = load_universe_rows()
    resolution = resolve_companies(REQUESTED_COMPANIES, universe)
    if only:
        want = {s.upper() for s in only}
        for r in resolution:
            if (r["symbol"] or "").upper() not in want:
                r["status"] = "SKIPPED_NOT_REQUESTED"
    # Stary artefakt znika ZANIM zaczniemy: nigdy nie da sie otworzyc
    # poprzedniego dashboardu i pomylic go z nowym.
    index_path = os.path.join(out_dir, "index.html")
    if os.path.isfile(index_path):
        os.remove(index_path)
        print("USUNIETO stary dashboard: %s" % index_path, flush=True)
    data_dir = os.path.join(out_dir, "data")
    if os.path.isdir(data_dir):
        for fn in os.listdir(data_dir):
            if fn.endswith(".json"):
                os.remove(os.path.join(data_dir, fn))
    now = now_utc or pd.Timestamp.now(tz="UTC")
    payloads, errors, diags = {}, [], {}
    todo = [r for r in resolution
            if r["status"] in ("RESOLVED_EXACT", "RESOLVED_UNIQUE")]
    total, done, t0 = len(todo), 0, _time.time()
    opened = False
    print("START: %d spolek do wygenerowania (1D + 1H)\n" % total, flush=True)
    for r in resolution:
        if r["status"] not in ("RESOLVED_EXACT", "RESOLVED_UNIQUE"):
            continue
        sym = r["symbol"]
        _progress(done, total, t0, "pobieram " + sym)
        done += 1
        lower_shared = None
        # --- 1D: CANONICAL ANALYSIS (30m pobierane RAZ, w kawałkach) ---
        try:
            bars, q1d, lower_shared, diag = fetch_canonical_1d(sym, now)
            diags[sym] = diag
            range_start = (now.tz_convert(CAL.NY).date()
                           - _dt.timedelta(days=int(FETCH_1D_SESSIONS * 1.55)))
            wm = _warmup_for("1D", bars, range_start)
            batch = build_atomic_features(bars, FeatureBatchMeta(sym, "1D"), wm)
            payloads[sym + "|1D"] = build_symbol_payload(sym, "1D", bars, batch,
                                                         daily_quality=q1d)
            q = payloads[sym + "|1D"]["quality"]
            print("%s 1D: bary=%d 30m=%d pokrycie[pelne=%d niepelne=%d brak=%d] "
                  "okno[HL ok=%d brak=%d]"
                  % (sym, q["final_bars"], diag["m30_rows"], diag["complete"],
                     diag["incomplete"], diag["no_coverage"],
                     q["display_valid_hl"], q["display_missing_hl"]), flush=True)
        except Exception as exc:
            errors.append({"symbol": sym, "tf": "1D",
                           "error": "DATA_FETCH_FAILED: %s" % exc})
            print("%s 1D: BLAD %s" % (sym, exc), flush=True)
        # --- 1H: te same bary 30m (zero drugiego pobrania tego samego zakresu) ---
        try:
            bars = fetch_canonical_1h(sym, lower_shared, now)
            range_start = (now.tz_convert(CAL.NY).date()
                           - _dt.timedelta(days=FETCH_1H_DAYS))
            wm = _warmup_for("1H", bars, range_start)
            batch = build_atomic_features(bars, FeatureBatchMeta(sym, "1H"), wm)
            payloads[sym + "|1H"] = build_symbol_payload(sym, "1H", bars, batch)
            print("%s 1H: bary=%d" % (sym, payloads[sym + "|1H"]["quality"]
                                      ["final_bars"]), flush=True)
        except Exception as exc:
            errors.append({"symbol": sym, "tf": "1H",
                           "error": "DATA_FETCH_FAILED: %s" % exc})
            print("%s 1H: BLAD %s" % (sym, exc), flush=True)
        _progress(done, total, t0, "gotowe " + sym)
        # Dashboard zapisywany PO KAZDEJ spolce, wiec gotowe wykresy mozna ogladac
        # od razu; przy pierwszej otwieramy go automatycznie. Kolejne spolki
        # doklejaja sie do tego samego pliku - wystarczy odswiezyc (F5).
        if payloads:
            _write_dashboard(out_dir, index_path, resolution, payloads, errors,
                             render_index, partial=(done < total))
            if not opened:
                opened = True
                try:
                    os.startfile(index_path)      # noqa: S606 - lokalny plik HTML
                    print("OTWARTO dashboard z pierwszymi wykresami - kolejne "
                          "spolki dokladaja sie, odswiez strone (F5).", flush=True)
                except Exception:
                    print("Dashboard gotowy: %s" % index_path, flush=True)
    print("\n", flush=True)
    build = _write_dashboard(out_dir, index_path, resolution, payloads, errors,
                             render_index, partial=False)
    print("ZAPISANO dashboard: %s  (BUILD %s, %s)"
          % (index_path, build["build_id"], build["generated"]), flush=True)
    return {"resolution": resolution, "payloads": payloads, "errors": errors,
            "diags": diags, "index": index_path, "build": build}


def _sanity(payloads, syms=("RBLX", "INTU", "NVDA", "ZS")):
    lines = []
    for sym in syms:
        for tf in ("1D", "1H"):
            p = payloads.get("%s|%s" % (sym, tf))
            if p is None:
                lines.append("%s %s: BRAK (nie wygenerowano)" % (sym, tf))
                continue
            lb, q = p["last_bar"], p["quality"]
            ok = (q["final_bars"] > 0 and lb.get("macd") is not None
                  and lb.get("rsi") is not None and lb.get("stoch_k") is not None)
            extra = ""
            if tf == "1D":
                extra = ("  okno[HL ok=%s brak=%s]  historia[brak pokrycia 30m=%s "
                         "niepelne sesje=%s]"
                         % (q.get("display_valid_hl"), q.get("display_missing_hl"),
                            q.get("no_lower_tf_coverage"),
                            q.get("incomplete_lower_tf")))
            lines.append("%s %s: bary=%d okno=%d MACD/RSI/STOCH po warmup: %s%s"
                         % (sym, tf, q["final_bars"], q["display_bars"],
                            "TAK" if ok else "NIE", extra))
            if tf == "1D":
                lines.append("    Stochastic ostatni bar: K=%s D=%s (%s)"
                             % (lb.get("stoch_k"), lb.get("stoch_d"),
                                lb.get("stochastic_status")))
    return lines


def _forensics(payloads, syms=("INTU", "RBLX"), n=20):
    """Ostatnie n widocznych barów 1D: dokładnie to, co dostaje renderer."""
    lines = []
    for sym in syms:
        p = payloads.get(sym + "|1D")
        lines.append("%s 1D - ostatnie %d widocznych barow:" % (sym, n))
        if p is None:
            lines.append("  BRAK DANYCH")
            continue
        lines.append("  %-12s %10s %10s %10s %10s  %s"
                     % ("DATA", "OPEN", "HIGH", "LOW", "CLOSE", "HL"))
        for c in p["candles"][-n:]:
            lines.append("  %-12s %10s %10s %10s %10s  %s"
                         % (c["t"][:10], c["o"], c["h"], c["l"], c["c"],
                            "OK" if c["hl_ok"] else "BRAK"))
    return lines


def main(argv=None):
    p = argparse.ArgumentParser(description="V3.1B chart validation (read only)")
    p.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "wyniki-v3-1",
        "chart-validation"))
    p.add_argument("--only", default=None,
                   help="lista symboli po przecinku, np. RBLX (proba na jednej spolce)")
    a = p.parse_args(argv)
    only = [s.strip() for s in a.only.split(",")] if a.only else None
    res = generate(a.out, only=only)
    print("ROZPOZNANIE SPOLEK:")
    for r in res["resolution"]:
        print("  %-24s -> %-6s %-30s %-8s %s"
              % (r["requested_name"], r["symbol"] or "-",
                 (r["company_name"] or "-")[:30], r["exchange"] or "-",
                 r["status"]))
    resolved = [r for r in res["resolution"]
                if r["status"] in ("RESOLVED_EXACT", "RESOLVED_UNIQUE")]
    g1d = len([k for k in res["payloads"] if k.endswith("|1D")])
    g1h = len([k for k in res["payloads"] if k.endswith("|1H")])
    print("ROZWIAZANE: %d / %d" % (len(resolved), len(REQUESTED_COMPANIES)))
    print("WYKRESY 1D: %d / %d   1H: %d / %d" % (g1d, len(resolved), g1h,
                                                 len(resolved)))
    for e in res["errors"]:
        print("  BLAD %s %s: %s" % (e["symbol"], e["tf"], e["error"]))
    print("POKRYCIE DANYCH 30m (diagnostyka 1D):")
    for sym, d in res.get("diags", {}).items():
        print("  %-6s 1D %s..%s (%d barow)  30m %s..%s (%d barow)  "
              "sesje[pelne=%d niepelne=%d brak pokrycia=%d]"
              % (sym, d["d1_from"], d["d1_to"], d["native_1d_rows"],
                 d["m30_from"], d["m30_to"], d["m30_rows"],
                 d["complete"], d["incomplete"], d["no_coverage"]))
    print("KONTROLA SANITY (RBLX/INTU/NVDA/ZS):")
    for line in _sanity(res["payloads"]):
        print("  " + line)
    print("FORENSYKA OSTATNICH BAROW:")
    for line in _forensics(res["payloads"]):
        print("  " + line)
    print("DASHBOARD: %s" % res["index"])
    return 0 if (g1d + g1h) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

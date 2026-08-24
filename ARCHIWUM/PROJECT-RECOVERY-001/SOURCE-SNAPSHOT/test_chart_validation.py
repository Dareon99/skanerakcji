"""backend/v3/tests/test_chart_validation.py — V3.1B harness wykresów (offline).

Testuje wyłącznie logikę harnessu: rozwiązywanie nazw z Universe, okno wyświetlania,
rozdział pre-roll/okno, brak fallbacku do raw H/L, tylko bary FINAL, brak pól
tradingowych/scoringowych. Zero sieci, zero bazy — dane syntetyczne.
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from v3.features import build_atomic_features  # noqa: E402
from v3.features.schema import FeatureBatchMeta  # noqa: E402
from v3.market_data import warmup as W  # noqa: E402
from v3.tools import chart_validation as CV  # noqa: E402

UNIVERSE = [
    {"symbol": "RBLX", "name": "Roblox Corp. Class A", "exchange": "NYSE"},
    {"symbol": "INTU", "name": "Intuit Inc.", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "APLE", "name": "Apple Hospitality REIT Inc", "exchange": "NYSE"},
    {"symbol": "ZS", "name": "Zscaler, Inc.", "exchange": "NASDAQ"},
    {"symbol": "ORCL", "name": "Oracle Corporation", "exchange": "NYSE"},
    {"symbol": "AMBI1", "name": "Delta Data Corp", "exchange": "NYSE"},
    {"symbol": "AMBI2", "name": "Delta Dynamics Inc", "exchange": "NYSE"},
]


def _bars(n=200, hl_nan_at=(), final_mask=None):
    idx = pd.DatetimeIndex([pd.Timestamp("2024-01-02 14:30", tz="UTC")
                            + pd.Timedelta(days=i) for i in range(n)],
                           name="bar_open_utc")
    close = [100.0 + ((i * 7) % 13) - 6 + i * 0.05 for i in range(n)]
    open_ = [c - 0.4 for c in close]
    high = [max(o, c) + 1.0 for o, c in zip(open_, close)]
    low = [min(o, c) - 1.0 for o, c in zip(open_, close)]
    for i in hl_nan_at:
        high[i] = low[i] = float("nan")
    return pd.DataFrame({
        "bar_close_utc": idx + pd.Timedelta(hours=6.5),
        "session_date": [ts.date() for ts in idx],
        "open": open_, "high": high, "low": low, "close": close,
        "volume": [1000.0 + i for i in range(n)],
        "is_final": final_mask if final_mask is not None else [True] * n}, index=idx)


def _payload(n=200, tf="1D", **kw):
    bars = _bars(n, **kw)
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", tf),
                                  W.plan_warmup(tf, n, True))
    return CV.build_symbol_payload("TEST", tf, bars, batch), bars, batch


# ------------------------------------------------------------ lista i symbole
def test_19_requested_names_preserved():
    assert len(CV.REQUESTED_COMPANIES) == 19
    assert CV.REQUESTED_COMPANIES[0] == "Roblox"
    assert CV.REQUESTED_COMPANIES[-1] == "Novo Nordisk"


def test_resolution_exact_and_unique():
    res = CV.resolve_companies(("Roblox", "Intuit", "Nvidia", "Apple"), UNIVERSE)
    by = {r["requested_name"]: r for r in res}
    assert by["Roblox"]["symbol"] == "RBLX"
    assert by["Intuit"]["symbol"] == "INTU"
    assert by["Nvidia"]["symbol"] == "NVDA"          # case-insensitive po nazwie
    # "Apple" -> dokładnie jeden kandydat po zdjęciu sufiksów prawnych (Apple Inc.)
    assert by["Apple"]["symbol"] == "AAPL"
    assert by["Apple"]["status"] == "RESOLVED_EXACT"


def test_resolution_ambiguous_is_not_guessed():
    res = CV.resolve_companies(("Delta",), UNIVERSE)
    assert res[0]["status"] == "AMBIGUOUS"
    assert res[0]["symbol"] is None
    assert len(res[0]["candidates"]) >= 2


def test_resolution_not_found_does_not_block_batch():
    res = CV.resolve_companies(("Nie Istnieje SA", "Roblox"), UNIVERSE)
    assert res[0]["status"] == "NOT_FOUND" and res[0]["symbol"] is None
    assert res[1]["status"].startswith("RESOLVED")
    resolved = [r for r in res if r["status"].startswith("RESOLVED")]
    assert len(resolved) == 1                        # reszta batcha zostaje


# ------------------------------------------------------------ payload
def test_display_window_max_120():
    p, _, _ = _payload(400)
    assert p["quality"]["display_bars"] == 120
    assert len(p["candles"]) == 120
    assert len(p["series"]["macd"]) == 120


def test_short_history_shows_all_without_synthesizing():
    p, _, _ = _payload(60)
    assert p["quality"]["display_bars"] == 60
    assert len(p["candles"]) == 60


def test_preroll_not_truncated_before_indicators():
    """Wskaźniki liczone na pełnej serii, dopiero potem tail(120)."""
    p, bars, batch = _payload(400)
    full = batch.features
    assert p["series"]["macd"][-1] == round(float(full["macd"].iloc[-1]), 8)
    assert p["series"]["macd"][0] == round(float(full["macd"].iloc[-120]), 8)
    # wartość na początku okna NIE jest wartością z serii liczonej od baru -120
    short = build_atomic_features(bars.tail(120), FeatureBatchMeta("TEST", "1D"),
                                  W.plan_warmup("1D", 120, True))
    assert (p["series"]["macd"][20]
            != CV._clean(short.features["macd"].iloc[20]))


def test_missing_hl_candle_has_no_raw_fallback():
    p, _, _ = _payload(200, hl_nan_at=(190,))
    c = p["candles"][-10]
    assert c["hl_ok"] is False
    assert c["h"] is None and c["l"] is None         # nie dorabiamy świecy
    assert c["c"] is not None                        # close nadal jawnie dostępny
    assert p["quality"]["missing_hl"] == 1
    assert p["quality"]["data_status"] == "DANE CZĘŚCIOWE"


def test_multi_session_range_keeps_hl_for_every_complete_session():
    """Regresja buga V3.1B: 30m pokrywa te same sesje co 1D => H/L dla WSZYSTKICH.

    Jeden dzień to za mało — błąd objawiał się dopiero na dłuższym zakresie, gdzie
    starsza część historii nie miała pobranych barów 30m.
    """
    import datetime as dt

    from v3.market_data import us_calendar as CAL
    from v3.market_data.daily_analysis import build_daily_analysis

    days = [d for d in (dt.date(2024, 3, 1) + dt.timedelta(days=i)
                        for i in range(120)) if CAL.session_schedule(d)][:60]
    assert len(days) == 60
    raw_idx, raw_rows, low_idx, low_rows = [], [], [], []
    for i, day in enumerate(days):
        s = CAL.session_schedule(day)
        raw_idx.append(s["open_utc"])
        raw_rows.append((s["close_utc"], day, 100.0 + i, 106.0 + i, 94.0 + i,
                         104.0 + i, 1000.0, True))
        for j, t in enumerate(CAL.expected_30m_bar_opens(day)):
            low_idx.append(t)
            low_rows.append((100.0 + i + j * 0.1, 105.0 + i, 95.0 + i, 104.0 + i,
                             10.0))
    raw = pd.DataFrame(raw_rows, index=pd.DatetimeIndex(raw_idx,
                                                        name="bar_open_utc"),
                       columns=["bar_close_utc", "session_date", "open", "high",
                                "low", "close", "volume", "is_final"])
    lower = pd.DataFrame(low_rows, index=pd.DatetimeIndex(low_idx,
                                                          name="bar_open_utc"),
                         columns=["open", "high", "low", "close", "volume"])
    analysis, quality = build_daily_analysis(raw, lower)
    assert len(analysis) == 60
    assert analysis["high"].notna().all()            # zero utraconych H/L
    assert analysis["low"].notna().all()
    assert all(q.quality_status == "VERIFIED_LOWER_TF_COMPLETE"
               for q in quality.values())
    batch = build_atomic_features(analysis, FeatureBatchMeta("TEST", "1D"),
                                  W.plan_warmup("1D", 60, True))
    p = CV.build_symbol_payload("TEST", "1D", analysis, batch,
                                daily_quality=quality)
    assert p["quality"]["display_missing_hl"] == 0
    assert p["quality"]["display_valid_hl"] == 60
    assert p["quality"]["no_lower_tf_coverage"] == 0
    assert all(c["hl_ok"] for c in p["candles"])


def test_no_coverage_is_separated_from_incomplete_session():
    """Brak pobranego 30m nie jest tym samym co niepełna sesja."""
    import datetime as dt

    class Q:
        def __init__(self, s):
            self.quality_status = s
            self.high_low_available = s == "VERIFIED_LOWER_TF_COMPLETE"

    bars = _bars(30, hl_nan_at=tuple(range(10)))
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1D"),
                                  W.plan_warmup("1D", 30, True))
    days = list(bars["session_date"])
    dq = {d: Q("SOURCE_MISSING" if i < 8
               else ("INCOMPLETE_LOWER_TF" if i < 10
                     else "VERIFIED_LOWER_TF_COMPLETE"))
          for i, d in enumerate(days)}
    assert isinstance(days[0], dt.date)
    p = CV.build_symbol_payload("TEST", "1D", bars, batch, daily_quality=dq)
    assert p["quality"]["no_lower_tf_coverage"] == 8
    assert p["quality"]["incomplete_lower_tf"] == 2


def test_chunk_spans_cover_range_without_gaps_or_overlap():
    import datetime as dt
    spans = CV.chunk_spans(dt.date(2024, 1, 1), dt.date(2024, 6, 30), 60)
    assert spans[0][0] == dt.date(2024, 1, 1)
    assert spans[-1][1] == dt.date(2024, 6, 30)
    for (a1, b1), (a2, _) in zip(spans, spans[1:]):
        assert b1 < a2 and a2 == b1 + dt.timedelta(days=1)


def test_1h_reuses_shared_30m_without_second_fetch():
    """fetch_canonical_1h przyjmuje gotowe bary 30m (bez sieci) — semantyka bez zmian."""
    import datetime as dt

    from v3.market_data import us_calendar as CAL
    days = [d for d in (dt.date(2024, 3, 1) + dt.timedelta(days=i)
                        for i in range(20)) if CAL.session_schedule(d)][:8]
    idx, rows = [], []
    for i, day in enumerate(days):
        for j, t in enumerate(CAL.expected_30m_bar_opens(day)):
            idx.append(t)
            rows.append((100.0 + j, 101.0 + j, 99.0 + j, 100.5 + j, 5.0))
    lower = pd.DataFrame(rows, index=pd.DatetimeIndex(idx, name="bar_open_utc"),
                         columns=["open", "high", "low", "close", "volume"])
    bars = CV.fetch_canonical_1h("TEST", lower,
                                 pd.Timestamp("2024-04-01", tz="UTC"))
    assert len(bars) == 7 * len(days)                # 7 kubelkow na pelna sesje
    assert bool(bars["is_final"].all())
    # canonical contract: obecnosc wymaganych kolumn (kolejnosc nie jest kontraktem)
    for col in ("bar_close_utc", "session_date", "open", "high", "low", "close",
                "volume", "is_final"):
        assert col in bars.columns, col
    # wynik przechodzi canonical validation (funkcja podnosi wyjątek przy błędzie)
    from v3.market_data.validation import validate_bars
    canonical = bars[["bar_close_utc", "session_date", "open", "high", "low",
                      "close", "volume", "is_final"]]
    assert validate_bars(canonical) is canonical


def test_final_bars_only_in_payload():
    bars = _bars(200, final_mask=[True] * 199 + [False])
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1D"),
                                  W.plan_warmup("1D", 199, True))
    p = CV.build_symbol_payload("TEST", "1D", bars, batch)
    assert p["quality"]["final_bars"] == 199
    assert len(p["candles"]) == 120
    # ostatni widoczny bar to bar FINAL nr 199, nie formujacy sie nr 200
    expected_last = pd.Timestamp(bars.index[198]).tz_convert(
        "America/New_York").isoformat()
    assert p["quality"]["latest_bar_time"] == expected_last


def test_no_trading_or_scoring_fields():
    p, _, _ = _payload(150)
    def walk(obj, path=""):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.append(k.lower())
                keys.extend(walk(v))
        elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
            keys.extend(walk(obj[0]))
        return keys
    keys = walk(p)
    for bad in ("score", "rank", "confidence", "probability", "opportunity",
                "buy", "sell", "watch", "target", "stop_loss"):
        assert not any(bad in k for k in keys), bad


def test_1d_and_1h_generated_independently():
    p1, _, _ = _payload(200, tf="1D")
    p2, _, _ = _payload(200, tf="1H")
    assert p1["tf"] == "1D" and p2["tf"] == "1H"


def test_tool_uses_canonical_paths_in_source():
    src = open(os.path.join(os.path.dirname(os.path.abspath(CV.__file__)),
                            "chart_validation.py"), "r", encoding="utf-8").read()
    assert "build_daily_analysis(" in src            # 1D: CANONICAL ANALYSIS
    assert "aggregate_1h_from_lower(" in src         # 1H: rebuilt z 30m
    for bad in ("yahoo", "stooq", "cycles1h", "import cycles"):
        for line in src.splitlines():
            ls = line.strip().lower()
            if ls.startswith(("import ", "from ")):
                assert bad not in ls


def test_feature_values_sourced_from_feature_engine():
    p, _, batch = _payload(200)
    last = batch.features.iloc[-1]
    assert p["last_bar"]["rsi"] == CV._clean(last["rsi"])
    assert p["last_bar"]["macd_hist_delta"] == CV._clean(last["macd_hist_delta"])
    assert p["last_bar"]["macd_state"] == str(last["macd_state"])


# ------------------------------------------------------------ V3.1B-UI
def test_ema_20_50_100_present_and_sourced_from_canonical_close():
    p, _, batch = _payload(300)
    closes = batch.features["close"].tolist()
    for span in (20, 50, 100):
        key = "ema%d" % span
        assert key in p["series"]
        assert len(p["series"][key]) == len(p["candles"])
        expected = CV.ema(closes, span)[-len(p["candles"]):]
        assert p["series"][key][-1] == CV._clean(expected[-1])


def test_ema_computed_on_full_series_before_display_tail():
    """EMA liczona z pre-rollem — nie startuje dopiero od pierwszego widocznego bara."""
    p, _, batch = _payload(400)
    closes = batch.features["close"].tolist()
    full_first_visible = CV.ema(closes, 100)[-120]
    short_only = CV.ema(closes[-120:], 100)[0]
    assert p["series"]["ema100"][0] == CV._clean(full_first_visible)
    assert p["series"]["ema100"][0] != CV._clean(short_only)


def test_ema_is_renderer_only_not_in_feature_schema():
    from v3.features.schema import FEATURE_COLUMNS
    for span in (20, 50, 100, 200):
        assert ("ema%d" % span) not in FEATURE_COLUMNS
    assert not any("ema" in c.lower() for c in FEATURE_COLUMNS)


def test_no_ema200_added():
    p, _, _ = _payload(300)
    assert "ema200" not in p["series"]
    assert set(k for k in p["series"] if k.startswith("ema")) == {
        "ema20", "ema50", "ema100"}


def test_current_price_line_uses_last_final_close():
    bars = _bars(200, final_mask=[True] * 199 + [False])
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1D"),
                                  W.plan_warmup("1D", 199, True))
    p = CV.build_symbol_payload("TEST", "1D", bars, batch)
    assert p["last_final_close"] == CV._clean(batch.features["close"].iloc[-1])
    assert p["last_final_close"] == p["candles"][-1]["c"]
    # forming bar (200) nie jest zrodlem linii ceny
    assert p["last_final_close"] != CV._clean(bars["close"].iloc[-1])


def test_panels_receive_locked_indicator_series():
    p, _, batch = _payload(200)
    f = batch.features.tail(120)
    for key in ("macd", "macd_signal", "macd_hist", "rsi", "rsi_helper",
                "stoch_k", "stoch_d"):
        assert p["series"][key][-1] == CV._clean(f[key].iloc[-1])


def test_ui_guides_are_renderer_only():
    """70/50/30 i 80/50/20 zyja wylacznie w szablonie HTML, nie w danych ani cechach."""
    from v3.features.schema import FEATURE_COLUMNS
    p, _, _ = _payload(150)
    blob = str(p["series"].keys()) + str(list(p["last_bar"].keys()))
    for bad in ("guide", "zone", "level", "overbought", "oversold_zone"):
        assert bad not in blob.lower()
    assert not any("guide" in c.lower() or "zone" in c.lower()
                   for c in FEATURE_COLUMNS)


def test_dashboard_is_self_contained_without_network():
    from v3.tools.chart_validation_template import render_index
    p, _, _ = _payload(150)
    html = render_index([{"requested_name": "Test", "symbol": "TEST",
                          "company_name": "Test Co", "exchange": "NYSE",
                          "status": "RESOLVED_EXACT"}], {"TEST|1D": p}, [])
    low = html.lower()
    for bad in ("fetch(", "xmlhttprequest", "http://", "https://", "<script src",
                "@import"):
        assert bad not in low, bad
    assert "window.__data" in low                    # payload osadzony lokalnie


def test_dashboard_has_no_trading_labels():
    from v3.tools.chart_validation_template import render_index
    p, _, _ = _payload(150)
    html = render_index([], {"TEST|1D": p}, []).lower()
    for bad in ("buy", "sell", "watch", "target", "stop loss", "score",
                "bullish", "bearish", "golden cross"):
        assert bad not in html, bad


def test_dashboard_renders_required_panels_and_controls():
    from v3.tools.chart_validation_template import render_index
    p, _, _ = _payload(150)
    html = render_index([], {"TEST|1D": p}, [])
    for token in ("MACD", "RSI", "Stochastic", "EMA20", "EMA50", "EMA100",
                  "Akumulacja/Dystrybucja", "Reset widoku", "b1d", "b1h",
                  "crosshair"):
        assert token in html, token
    # wspolna os czasu: jedno plotno, jeden zakres indeksow dla wszystkich paneli
    assert html.count("<canvas") == 1
    assert "function range(" in html and "P.stoch" in html


# ------------------------------------------- V3.1B-UI finalne dopracowanie
def _html():
    from v3.tools.chart_validation_template import render_index
    p, _, _ = _payload(300)
    return render_index([], {"TEST|1D": p}, [])


def test_ema_have_three_distinct_colors():
    html = _html()
    import re
    block = re.search(r"const EMA_C=\{(.*?)\};", html, re.S).group(1)
    colors = re.findall(r"rgba\([^)]*\)", block)
    assert len(colors) == 3
    assert len(set(colors)) == 3                     # trzy ROZNE kolory


def test_rsi_has_no_full_background_bands():
    """Zamiast stalych pasow 70-100 i 0-30: wypelnienie tylko przy wyjsciu z kanalu."""
    html = _html()
    assert "function zone(" not in html              # helper pasow tla usuniety
    assert "excursion(S.rsi,i0,i1,70,true" in html
    assert "excursion(S.rsi,i0,i1,30,false" in html


def test_rsi_excursion_fill_only_outside_channel():
    """Wypelnienie liczy sie wylacznie z probek faktycznie poza poziomem."""
    html = _html()
    import re
    body = re.search(r"function excursion\((.*?)\n flush\(\)\}", html, re.S).group(1)
    assert "above?v>level:v<level" in body.replace(" ", "")
    assert "else flush()" in body                    # przerwa konczy obszar


def test_rsi_and_stoch_guides_and_current_value_labels():
    html = _html()
    # r559: oba panele licza sie w tej samej skali OSC_LO/OSC_HI
    for lv in ("70,OSC_LO,OSC_HI", "30,OSC_LO,OSC_HI", "50,OSC_LO,OSC_HI"):
        assert "guide(P.rsi," + lv in html, lv
    for lv in ("80,OSC_LO,OSC_HI", "20,OSC_LO,OSC_HI", "50,OSC_LO,OSC_HI"):
        assert "guide(P.stoch," + lv in html, lv
    assert "vlabel(P.rsi,S.rsi[h]" in html
    assert "vlabel(P.stoch,S.stoch_k[h]" in html
    assert "vlabel(P.stoch,S.stoch_d[h]" in html


def test_oscillator_axes_do_not_print_0_and_100():
    """Panele RSI/Stoch nie maja juz siatki numerycznej z 0 i 100."""
    html = _html()
    assert "hgrid(P.rsi" not in html
    assert "hgrid(P.stoch" not in html


def test_ad_standard_formula():
    from v3.tools.chart_validation import accumulation_distribution as ad
    # CLV = ((c-l)-(h-c))/(h-l); MFV = CLV*v; AD kumulatywne
    out = ad([10.0, 12.0], [8.0, 9.0], [9.0, 12.0], [100.0, 300.0])
    clv1 = ((9.0 - 8.0) - (10.0 - 9.0)) / (10.0 - 8.0)      # 0.0
    clv2 = ((12.0 - 9.0) - (12.0 - 12.0)) / (12.0 - 9.0)    # 1.0
    assert abs(out[0] - clv1 * 100.0) < 1e-12
    assert abs(out[1] - (clv1 * 100.0 + clv2 * 300.0)) < 1e-12


def test_ad_zero_range_bar_contributes_nothing():
    from v3.tools.chart_validation import accumulation_distribution as ad
    out = ad([10.0, 10.0], [10.0, 10.0], [10.0, 10.0], [500.0, 500.0])
    assert out == [0.0, 0.0]                         # brak dzielenia przez zero


def test_ad_is_cumulative_computed_before_display_tail():
    """A/D jest skumulowane, wiec pierwsza widoczna wartosc niesie historie sprzed okna."""
    p, bars, batch = _payload(400)
    from v3.tools.chart_validation import accumulation_distribution as ad
    f = batch.features
    full = ad([float(bars.loc[t, "high"]) for t in f.index],
              [float(bars.loc[t, "low"]) for t in f.index],
              f["close"].tolist(),
              [float(bars.loc[t, "volume"]) for t in f.index])
    assert len(p["series"]["ad"]) == 120
    assert abs(p["series"]["ad"][0] - round(full[-120], 8)) < 1e-6
    assert abs(p["series"]["ad"][-1] - round(full[-1], 8)) < 1e-6
    # gdyby liczono tylko na oknie, pierwsza wartosc bylaby wkladem jednego bara
    window_only = ad([float(bars.loc[t, "high"]) for t in f.index[-120:]],
                     [float(bars.loc[t, "low"]) for t in f.index[-120:]],
                     f["close"].tolist()[-120:],
                     [float(bars.loc[t, "volume"]) for t in f.index[-120:]])
    assert abs(p["series"]["ad"][0] - window_only[0]) > 1e-6


def test_ad_uses_canonical_data_and_not_raw_hl():
    """Sesja bez canonical H/L nie wnosi wkladu z raw H/L (CLV z NaN => NaN)."""
    p, _, _ = _payload(200, hl_nan_at=(190,))
    assert p["candles"][-10]["hl_ok"] is False
    assert p["series"]["ad"][-10] is None            # NaN, zero fallbacku


def test_ad_not_in_feature_schema():
    from v3.features.schema import FEATURE_COLUMNS
    for bad in ("ad", "accumulation", "distribution", "ad_line", "money_flow"):
        assert bad not in FEATURE_COLUMNS, bad


def test_rsi_and_stoch_panels_have_equal_height():
    """r559: rowna sie KANAL, nie pudelko - patrz
    test_rsi_channel_matches_stoch_channel_in_pixels. Panel RSI jest 1.5x wyzszy."""
    html = _html()
    assert "P.rsi={y:y,h:rsi}" in html and "P.stoch={y:y,h:stoch}" in html
    assert "rsi=Math.round(stoch*1.5)" in html


def test_ad_panel_is_lower_than_oscillators_but_has_room():
    html = _html()
    import re
    ad = float(re.search(r"ad=Math\.round\(inner\*([0-9.]+)\)", html).group(1))
    st = float(re.search(r"stoch=Math\.round\(inner\*([0-9.]+)\)", html).group(1))
    assert ad < st                                   # nizszy niz oscylatory
    assert ad >= 0.08                                # ale z oddechem na etykiete


def test_ad_current_value_label_from_last_final():
    html = _html()
    assert "vlabelTxt(P.ad,S.ad[h]" in html          # etykieta w kolorze serii
    assert "'#7fb3a0',big(S.ad[h])" in html          # format K/M/B tylko w UI
    p, _, batch = _payload(300)
    assert p["series"]["ad"][-1] is not None         # ostatni FINAL bar


def test_macd_cross_markers_come_from_locked_events():
    p, _, batch = _payload(300)
    f = batch.features
    for col in ("macd_cross_signal_up", "macd_cross_signal_down"):
        assert p["series"][col] == [bool(v) for v in f[col].tail(120).tolist()]
    html = _html()
    # renderer tylko odczytuje eventy z payloadu, nie liczy przeciec od nowa
    assert "S.macd_cross_signal_up&&S.macd_cross_signal_up[i]" in html
    assert "up?'#00c853':'#ff1744'" in html          # zielona w gore, czerwona w dol
    # r557: S.macd[i-1] sluzy WYLACZNIE interpolacji pozycji markera, nie detekcji
    for bad in ("crossover(", "detectCross", "m0>s0&&m1<s1"):
        assert bad not in html, bad


def test_no_marker_without_cross_event():
    p, _, batch = _payload(300)
    ups = p["series"]["macd_cross_signal_up"]
    downs = p["series"]["macd_cross_signal_down"]
    assert any(ups) or any(downs)                    # sa jakies przeciecia
    # bary bez eventu maja False, wiec renderer nie ma czego rysowac
    assert sum(1 for u, dn in zip(ups, downs) if not u and not dn) > 0


def test_event_markers_render_only_when_payload_has_events():
    import datetime as dt
    bars = _bars(200)
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1D"),
                                 W.plan_warmup("1D", 200, True))
    empty = CV.build_symbol_payload("TEST", "1D", bars, batch)
    assert empty["events"] == []                     # brak payloadu => brak markerow
    day = bars["session_date"].iloc[-5]
    with_ev = CV.build_symbol_payload(
        "TEST", "1D", bars, batch,
        events=[{"session_date": day, "title": "Wyniki kwartalne",
                 "description": "Publikacja raportu okresowego", "type": "info"}])
    assert len(with_ev["events"]) == 1
    ev = with_ev["events"][0]
    assert ev["i"] == 115                            # 5. bar od konca okna 120
    assert ev["title"] == "Wyniki kwartalne"
    assert isinstance(day, dt.date)


def test_event_marker_is_blue_and_has_tooltip():
    html = _html()
    assert "dot(xOf(e.i,i0,i1,W),ey,'#4a8fff'" in html
    assert "Wazna informacja: '+e.title" in html
    assert "PRZECIECIE MACD / SIGNAL" in html          # r557: linia w kolorze markera


def test_events_do_not_touch_data_or_schema():
    from v3.features.schema import FEATURE_COLUMNS
    for bad in ("event", "events", "marker", "cross_marker"):
        assert bad not in FEATURE_COLUMNS, bad
    bars = _bars(200)
    before = bars.copy(deep=True)
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1D"),
                                 W.plan_warmup("1D", 200, True))
    CV.build_symbol_payload("TEST", "1D", bars, batch,
                            events=[{"session_date": bars["session_date"].iloc[-3],
                                     "title": "X", "description": "", "type": "i"}])
    pd.testing.assert_frame_equal(bars, before)      # dane nietkniete


def test_event_hour_is_not_invented_for_date_only_event():
    """Zdarzenie z sama data trafia na pierwszy bar sesji, godzina nie jest wymyslana."""
    bars = _bars(200)
    batch = build_atomic_features(bars, FeatureBatchMeta("TEST", "1H"),
                                 W.plan_warmup("1H", 200, True))
    day = bars["session_date"].iloc[-4]
    p = CV.build_symbol_payload("TEST", "1H", bars, batch,
                                events=[{"session_date": day, "title": "T",
                                         "description": "", "type": "i"}])
    assert p["events"][0]["i"] == 116


def test_rsi_panel_has_internal_visual_padding():
    """Zapas na wychylenia bierze sie z wysokosci panelu, nie z poszerzonej skali."""
    html = _html()
    assert "rsi=Math.round(stoch*1.5)" in html


def test_macd_marker_size_increased_and_high_contrast():
    html = _html()
    import re
    size = float(re.search(r"P\.macd\),up\?'#00c853':'#ff1744',([0-9.]+)\)",
                           html).group(1))
    assert size >= 3.0 * 1.19          # ~+20% wobec poprzednich 3.0
    assert "#00c853" in html and "#ff1744" in html
    for bad in ("shadowBlur", "filter:blur", "glow"):
        assert bad not in html, bad


def test_macd_marker_uses_event_bar_not_interpolation():
    """Marker, event, crosshair i tooltip wskazuja TEN SAM zamkniety bar i.

    Interpolacja polozenia kropki miedzy barami (r557) zostala usunieta w r590:
    przy plytkim przecieciu kropka ladowala wizualnie na barze i-1, mimo ze
    zdarzenie nalezy do i. Ten test pilnuje, zeby nie wrocila.
    """
    html = _html()
    body = html[html.index("Markery przeciec MACD/Signal"):html.index("---- RSI:")]

    # event: zrodlem sa wylacznie locked eventy z payloadu, czytane po indeksie i
    assert "S.macd_cross_signal_up[i]" in body
    assert "S.macd_cross_signal_down[i]" in body
    assert "if(!up&&!dn)continue" in body

    # marker: dokladnie x baru i, zero przesuniecia
    assert "dot(xOf(i,i0,i1,W)" in body
    assert "xOf(i-1" not in body
    assert "d0/(d0-d1)" not in body
    for bad in ("m0+(m1-m0)*t", "const t=Math.max(0,Math.min(1,", "i-1,i0,i1"):
        assert bad not in body, bad

    # tooltip: ten sam indeks co marker
    tip = html[html.index("const cu=S.macd_cross_signal_up"):]
    tip = tip[:tip.index("el.style.display")]
    assert "S.macd_cross_signal_up[i]" in tip
    assert "S.macd_cross_signal_down[i]" in tip

    # crosshair: rysowany na tym samym xOf(i) co marker
    cross = html[html.index("crosshair przez wszystkie panele"):]
    cross = cross[:cross.index("function")] if "function" in cross else cross[:400]
    assert "xOf(" in cross


def test_tooltip_cross_line_color_matches_direction():
    html = _html()
    assert "PRZECIECIE MACD / SIGNAL: '+(cu?'W GORE':'W DOL')" in html
    assert "color:'+(cu?'#00c853':'#ff1744')" in html
    for bad in ("KUP", "SPRZEDAJ", " BUY", " SELL"):
        assert bad not in html.upper().replace("BUILD", ""), bad


def test_ad_panel_has_subtle_grid_and_no_analytical_channel():
    html = _html()
    assert "hgridN(P.ad,AD[0],AD[1],W,3)" in html   # 3 delikatne poziomy z autoscale
    assert "scale([S.ad],i0,i1)" in html            # autoscale, bez wymuszonego zera
    for bad in ("upper_band", "lower_band", "envelope", "stddev", "percentileChannel"):
        assert bad not in html, bad


def test_rsi_and_stoch_have_identical_plot_geometry():
    """Zastapione przez test_rsi_channel_matches_stoch_channel_in_pixels.

    Rowna wysokosc pudelek byla blednym kryterium - przy skali 0-100 dawala
    zawsze mniejszy kanal RSI. Liczy sie rowna wysokosc kanalu w pikselach.
    """
    html = _html()
    assert "P.rsi={y:y,h:rsi}" in html and "P.stoch={y:y,h:stoch}" in html
    assert "RSI_LO" not in html and "RSI_HI" not in html


def test_rounding_remainder_goes_to_price_not_oscillators():
    html = _html()
    assert "price=inner-macd-ad-rsi-stoch" in html


def test_rsi_channel_matches_stoch_channel_in_pixels():
    """Rowna sie KANAL, nie wysokosc pudelka.

    Przy skali 0-100 kanal RSI 30-70 zajmuje 40% panelu, a Stochastic 20-80 az 60%.
    Rowna wysokosc paneli dawala wiec zawsze scisniety RSI. Panel RSI jest 1.5x
    wyzszy, wiec 0.40*1.5 = 0.60 - oba kanaly maja tyle samo pikseli, a RSI dostaje
    przy tym zapas nad 70 i pod 30 na wychylenia.
    """
    html = _html()
    import re
    st = float(re.search(r"stoch=Math\.round\(inner\*([0-9.]+)\)", html).group(1))
    mult = float(re.search(r"rsi=Math\.round\(stoch\*([0-9.]+)\)", html).group(1))
    h_st, h_rsi = st, st * mult
    rsi_channel = (70 - 30) / 100.0 * h_rsi
    stoch_channel = (80 - 20) / 100.0 * h_st
    ratio = rsi_channel / stoch_channel
    assert 0.95 <= ratio <= 1.05, ratio
    # zapas na wychylenia: nad 70 i pod 30
    assert (30 / 100.0) * h_rsi > 0.25 * stoch_channel


def test_rsi_scale_stays_0_100():
    html = _html()
    import re
    lo, hi = re.search(r"const OSC_LO=(\d+),OSC_HI=(\d+);", html).groups()
    assert (int(lo), int(hi)) == (0, 100)      # zero sztuczek ze skala RSI
    for token in ("guide(P.rsi,70,OSC_LO,OSC_HI", "guide(P.rsi,30,OSC_LO,OSC_HI",
                  "line(S.rsi,i0,i1,OSC_LO,OSC_HI"):
        assert token in html, token


def _macd_scale(vals, min_share=0.28, pad=0.10):
    """Odwzorowanie reguly z renderera (macdScale w szablonie) do pomiaru udzialow."""
    mn = min([0.0] + [v for v in vals])
    mx = max([0.0] + [v for v in vals])
    neg, pos = abs(min(mn, 0.0)), max(mx, 0.0)
    if neg == 0 and pos == 0:
        neg = pos = 1.0
    neg *= 1 + pad
    pos *= 1 + pad
    total = neg + pos
    k = min_share / (1 - min_share)
    if pos / total < min_share:
        pos = neg * k
    elif neg / total < min_share:
        neg = pos * k
    return -neg, pos


def _shares(vals):
    lo, hi = _macd_scale(vals)
    span = hi - lo
    return hi / span, -lo / span          # top_share, bottom_share


def test_macd_scale_constants_and_wiring():
    html = _html()
    import re
    share = float(re.search(r"MIN_SIDE_SHARE=([0-9.]+)", html).group(1))
    pad = float(re.search(r"MACD_PAD=([0-9.]+)", html).group(1))
    assert share >= 0.25
    assert 0.08 <= pad <= 0.12
    assert "const[mlo,mhi]=macdScale(S,i0,i1)" in html   # panel uzywa nowej skali
    # wspolna os Y dla histogramu i linii
    assert "[S.macd,S.macd_signal,S.macd_hist].forEach" in html


def test_macd_scale_case_a_negative_dominant():
    """Zakres -8..+1: ujemna czesc wieksza, ale dodatnia ma czytelny kanal."""
    top, bottom = _shares([-8.0, -3.0, 1.0])
    assert top >= 0.25 and bottom >= 0.25
    assert bottom > top                    # asymetria danych zachowana


def test_macd_scale_case_b_positive_dominant():
    top, bottom = _shares([-1.0, 4.0, 8.0])
    assert top >= 0.25 and bottom >= 0.25
    assert top > bottom


def test_macd_scale_case_c_balanced_stays_near_symmetric():
    top, bottom = _shares([-4.0, 0.0, 4.0])
    assert abs(top - bottom) < 0.02        # naturalna symetria, bez wymuszania


def test_macd_scale_never_forces_50_50():
    """Silna asymetria nie jest sprowadzana do 50/50 - tylko podnoszona do minimum."""
    top, bottom = _shares([-8.0, 1.0])
    assert bottom > 0.55                   # ujemna nadal dominuje
    assert 0.25 <= top <= 0.45


def test_macd_extremes_never_touch_panel_edges():
    for vals in ([-8.0, 1.0], [-1.0, 8.0], [-4.0, 4.0], [0.5, 2.0]):
        lo, hi = _macd_scale(vals)
        assert hi > max(vals) and lo < min(vals)   # padding od ekstremow


def test_macd_scale_uses_visible_range_only():
    html = _html()
    body = html[html.index("function macdScale"):]
    body = body[:body.index("function guide")]
    assert "for(let i=i0;i<=i1;i++)" in body        # tylko widoczne bary
    assert ".length" not in body                   # nie cala historia


MOMENTUM_POSITIVE_RISING = "#00BCD4"
MOMENTUM_POSITIVE_FALLING = "#2962FF"
MOMENTUM_NEGATIVE_FALLING = "#F23645"
MOMENTUM_NEGATIVE_RISING = "#880E4F"


def momentum_colors(hist):
    """Odwzorowanie reguly z renderera (momentumColors w szablonie).

    Kolor kazdego slupka wyliczany niezaleznie; przy wartosci identycznej z poprzednia
    zachowywany jest kolor poprzedniego slupka.
    """
    out, prev = [], None
    for i, v in enumerate(hist):
        if v is None:
            out.append(None)
            continue
        p = hist[i - 1] if i > 0 else None
        if p is None:
            c = MOMENTUM_POSITIVE_FALLING if v >= 0 else MOMENTUM_NEGATIVE_RISING
        elif v == p:
            c = prev if prev is not None else (
                MOMENTUM_POSITIVE_FALLING if v >= 0 else MOMENTUM_NEGATIVE_RISING)
        elif v >= 0 and v > p:
            c = MOMENTUM_POSITIVE_RISING
        elif v >= 0 and v < p:
            c = MOMENTUM_POSITIVE_FALLING
        elif v < 0 and v < p:
            c = MOMENTUM_NEGATIVE_FALLING
        else:
            c = MOMENTUM_NEGATIVE_RISING
        out.append(c)
        prev = c
    return out


# ------------------------------------------------------- histogram momentum
def test_momentum_tokens_are_exact_hex_at_full_opacity():
    html = _html()
    for name, hexv in (("MOMENTUM_POSITIVE_RISING", "#00BCD4"),
                       ("MOMENTUM_POSITIVE_FALLING", "#2962FF"),
                       ("MOMENTUM_NEGATIVE_FALLING", "#F23645"),
                       ("MOMENTUM_NEGATIVE_RISING", "#880E4F")):
        assert "%s='%s'" % (name, hexv) in html, name
    body = html[html.index("function momentumColors"):]
    body = body[:body.index("function range(")]
    for bad in ("rgba(", "globalAlpha", "opacity", "filter:", "lighten", "mix"):
        assert bad not in body, bad


def test_all_four_sign_direction_combinations():
    c = momentum_colors([1.0, 2.0])          # dodatnie rosnie
    assert c[1] == MOMENTUM_POSITIVE_RISING
    c = momentum_colors([2.0, 1.0])          # dodatnie slabnie
    assert c[1] == MOMENTUM_POSITIVE_FALLING
    c = momentum_colors([-1.0, -2.0])        # ujemne poglebia sie
    assert c[1] == MOMENTUM_NEGATIVE_FALLING
    c = momentum_colors([-2.0, -1.0])        # ujemne slabnie
    assert c[1] == MOMENTUM_NEGATIVE_RISING


def test_transition_positive_rising_to_positive_falling():
    c = momentum_colors([1.0, 3.0, 2.0])
    assert c[1] == MOMENTUM_POSITIVE_RISING
    assert c[2] == MOMENTUM_POSITIVE_FALLING


def test_transition_negative_falling_to_negative_rising():
    c = momentum_colors([-1.0, -3.0, -2.0])
    assert c[1] == MOMENTUM_NEGATIVE_FALLING
    assert c[2] == MOMENTUM_NEGATIVE_RISING


def test_zero_crossings_both_directions():
    up = momentum_colors([-1.0, 0.0, 1.0])
    assert up[1] == MOMENTUM_POSITIVE_RISING      # 0 traktowane jak >= 0
    assert up[2] == MOMENTUM_POSITIVE_RISING
    down = momentum_colors([1.0, 0.0, -1.0])
    assert down[1] == MOMENTUM_POSITIVE_FALLING
    assert down[2] == MOMENTUM_NEGATIVE_FALLING


def test_identical_consecutive_values_keep_previous_color():
    c = momentum_colors([1.0, 3.0, 3.0, 3.0])
    assert c[1] == MOMENTUM_POSITIVE_RISING
    assert c[2] == MOMENTUM_POSITIVE_RISING       # bez zmiany wartosci -> bez zmiany koloru
    assert c[3] == MOMENTUM_POSITIVE_RISING
    d = momentum_colors([-1.0, -3.0, -3.0])
    assert d[1] == MOMENTUM_NEGATIVE_FALLING and d[2] == MOMENTUM_NEGATIVE_FALLING


def test_first_bar_without_previous_value():
    assert momentum_colors([5.0])[0] == MOMENTUM_POSITIVE_FALLING
    assert momentum_colors([-5.0])[0] == MOMENTUM_NEGATIVE_RISING
    assert momentum_colors([0.0])[0] == MOMENTUM_POSITIVE_FALLING


def test_history_is_not_repainted_by_new_bar():
    base = momentum_colors([1.0, 3.0, 2.0, -1.0])
    grown = momentum_colors([1.0, 3.0, 2.0, -1.0, -5.0, 4.0])
    assert grown[:4] == base                      # dopisanie slupkow nie zmienia historii


def test_momentum_independent_of_candle_and_volume_colors():
    """Ten sam histogram daje te same kolory niezaleznie od kierunku swiec."""
    hist = [1.0, 3.0, 2.0, -1.0, -4.0]
    assert momentum_colors(hist) == momentum_colors(list(hist))
    html = _html()
    body = html[html.index("function momentumColors"):]
    body = body[:body.index("function range(")]
    for bad in ("c.o", "c.c", "S.volume", "candle", "vol"):
        assert bad not in body, bad
    # wolumen zachowuje wlasna, niezmieniona palete zielono-czerwona
    assert "rgba(38,166,154,.26)" in html and "rgba(239,83,80,.26)" in html
    vol = html[html.index("// wolumen w dolnej"):]
    vol = vol[:vol.index("// EMA")]
    for tok in ("#00BCD4", "#2962FF", "#F23645", "#880E4F", "momentumColors"):
        assert tok not in vol, tok


def test_momentum_rule_is_timeframe_agnostic():
    """Renderer jest jeden, wiec 1D i 1H licza kolory ta sama funkcja."""
    html = _html()
    assert html.count("function momentumColors") == 1
    assert html.count("momentumColors(S.macd_hist") == 1
    body = html[html.index("function momentumColors"):]
    body = body[:body.index("function range(")]
    for bad in ("tf", "1D", "1H"):
        assert bad not in body, bad


def test_renderer_uses_precomputed_color_array():
    html = _html()
    assert "const HC=momentumColors(S.macd_hist,S.macd_hist.length)" in html
    assert "ctx.fillStyle=HC[i]" in html
    assert "ctx.fillStyle=v>=0?'rgba(38,166,154" not in html   # stara regula usunieta


def test_rsi_and_stoch_palettes_are_swapped():
    """Zamiana istniejacych tokenow, bez tworzenia nowych kolorow.

    RSI <- dawny kolor %K, srednia RSI <- dawny %D,
    %K <- dawny kolor RSI, %D <- dawny kolor sredniej RSI.
    """
    html = _html()
    rsi = html[html.index("---- RSI:"):html.index("---- Stochastic")]
    st = html[html.index("---- Stochastic"):html.index("---- Akumulacja")]
    assert "line(S.rsi,i0,i1,OSC_LO,OSC_HI,P.rsi,'#4dd0e1'" in rsi
    assert "'#ff8a65'" in rsi
    assert "line(S.stoch_k,i0,i1,OSC_LO,OSC_HI,P.stoch,'#b39ddb'" in st
    assert "'rgba(201,162,39,.7)'" in st
    # etykiety wartosci na prawej osi ida za linia
    assert "vlabel(P.rsi,S.rsi[h],OSC_LO,OSC_HI,W,'#4dd0e1'" in rsi
    assert "vlabel(P.stoch,S.stoch_k[h],OSC_LO,OSC_HI,W,'#b39ddb'" in st
    # zadnych nowych kolorow poza czterema zamienionymi
    for old in ("#b39ddb", "#4dd0e1", "#ff8a65", "rgba(201,162,39,.7)"):
        assert old in html, old


def test_palette_swap_does_not_touch_momentum_or_levels():
    html = _html()
    for tok in ("#00BCD4", "#2962FF", "#F23645", "#880E4F"):
        assert tok in html, tok
    assert "guide(P.rsi,70,OSC_LO,OSC_HI" in html
    assert "guide(P.rsi,30,OSC_LO,OSC_HI" in html
    assert "guide(P.stoch,80,OSC_LO,OSC_HI" in html
    assert "guide(P.stoch,20,OSC_LO,OSC_HI" in html
    assert "excursion(S.rsi,i0,i1,70,true" in html      # wypelnienia bez zmian


def _cross_up(macd, sig, i):
    """Kanoniczna definicja: MACD[i-1] <= Signal[i-1] oraz MACD[i] > Signal[i]."""
    return macd[i - 1] <= sig[i - 1] and macd[i] > sig[i]


def _cross_down(macd, sig, i):
    return macd[i - 1] >= sig[i - 1] and macd[i] < sig[i]


def test_marker_sits_on_event_bar_not_interpolated():
    """r590: kropka na barze i, bez przesuniecia do punktu przeciecia."""
    html = _html()
    body = html[html.index("Markery przeciec MACD/Signal"):html.index("---- RSI:")]
    assert "dot(xOf(i,i0,i1,W)" in body        # dokladnie bar i
    assert "d0/(d0-d1)" not in body            # zadnej interpolacji
    assert "xOf(i-1" not in body               # zaden odnosnik do baru poprzedniego
    assert "if(!up&&!dn)continue" in body      # zrodlem locked event


def test_synthetic_cross_up_belongs_to_bar_i():
    macd = [-1.0, -0.5, 0.5, 1.0]
    sig = [0.0, 0.0, 0.0, 0.0]
    hits = [i for i in range(1, len(macd)) if _cross_up(macd, sig, i)]
    assert hits == [2]                         # pierwszy zamkniety bar po drugiej stronie
    assert not _cross_up(macd, sig, 1)


def test_synthetic_cross_down_belongs_to_bar_i():
    macd = [1.0, 0.5, -0.5, -1.0]
    sig = [0.0, 0.0, 0.0, 0.0]
    hits = [i for i in range(1, len(macd)) if _cross_down(macd, sig, i)]
    assert hits == [2]


def test_touch_and_return_is_no_cross_up():
    """Roznica [-1, 0, -1]: dotkniecie linii i powrot na te sama strone."""
    macd, sig = [-1.0, 0.0, -1.0], [0.0, 0.0, 0.0]
    assert [round(m - s, 6) for m, s in zip(macd, sig)] == [-1.0, 0.0, -1.0]
    assert not any(_cross_up(macd, sig, i) for i in (1, 2))
    # UWAGA: bar 2 spelnia definicje cross DOWN - dotkniecie zera zalicza sie do
    # strony "gornej" przez warunek >=, a bar 2 jest juz ponizej. To wynika wprost
    # z zatwierdzonej definicji i nie jest bledem.
    assert _cross_down(macd, sig, 2)


def test_touch_then_cross_up_on_last_bar():
    """Roznica [-1, 0, +1]: przejscie przez dotkniecie - zdarzenie na ostatnim barze."""
    macd, sig = [-1.0, 0.0, 1.0], [0.0, 0.0, 0.0]
    assert [round(m - s, 6) for m, s in zip(macd, sig)] == [-1.0, 0.0, 1.0]
    assert not _cross_up(macd, sig, 1)          # bar 1 to samo dotkniecie
    assert _cross_up(macd, sig, 2)              # dopiero tu MACD > Signal
    assert not any(_cross_down(macd, sig, i) for i in (1, 2))


def test_touch_and_return_is_no_cross_down():
    """Roznica [+1, 0, +1]: dotkniecie od gory i powrot."""
    macd, sig = [1.0, 0.0, 1.0], [0.0, 0.0, 0.0]
    assert [round(m - s, 6) for m, s in zip(macd, sig)] == [1.0, 0.0, 1.0]
    assert not any(_cross_down(macd, sig, i) for i in (1, 2))
    # UWAGA: bar 2 spelnia definicje cross up (MACD[1] <= Signal[1], MACD[2] > Signal[2])
    assert _cross_up(macd, sig, 2)


def test_touch_then_cross_down_on_last_bar():
    """Roznica [+1, 0, -1]: zdarzenie w dol na ostatnim barze."""
    macd, sig = [1.0, 0.0, -1.0], [0.0, 0.0, 0.0]
    assert [round(m - s, 6) for m, s in zip(macd, sig)] == [1.0, 0.0, -1.0]
    assert not _cross_down(macd, sig, 1)        # bar 1 to samo dotkniecie
    assert _cross_down(macd, sig, 2)
    assert not any(_cross_up(macd, sig, i) for i in (1, 2))


def test_pltr_regression_2026_02_18_19():
    """Realny przypadek: plytkie przeciecie t=0.0087 przesuwalo kropke na bar i-1."""
    macd = [-10.624, -10.199]
    sig = [-10.620, -10.655]
    assert round(macd[0] - sig[0], 3) == -0.004
    assert round(macd[1] - sig[1], 3) == 0.456
    assert _cross_up(macd, sig, 1)             # zdarzenie na barze i
    d0, d1 = macd[0] - sig[0], macd[1] - sig[1]
    t = d0 / (d0 - d1)
    assert t < 0.01                            # stara interpolacja: prawie na i-1
    html = _html()
    body = html[html.index("Markery przeciec MACD/Signal"):html.index("---- RSI:")]
    assert "xOf(i,i0,i1,W)" in body and "xOf(i-1" not in body


def test_marker_and_tooltip_read_same_index():
    html = _html()
    marker = html[html.index("Markery przeciec MACD/Signal"):html.index("---- RSI:")]
    tip = html[html.index("const cu=S.macd_cross_signal_up"):]
    tip = tip[:tip.index("el.style.display")]
    for frag in (marker, tip):
        assert "macd_cross_signal_up" in frag
        assert "[i]" in frag                   # oba czytaja ten sam indeks
    assert "S.macd_cross_signal_up[i]" in marker
    assert "S.macd_cross_signal_up[i]" in tip


def test_events_survive_display_window_trim():
    """Po przycieciu do 250 barow event i seria sa przesuwane razem."""
    p, _bars, batch = _payload(400)
    full = batch.features
    n = len(p["series"]["macd"])
    for i in range(n):
        j = len(full) - n + i
        assert p["series"]["macd"][i] == CV._clean(full["macd"].iloc[j])
        if "macd_cross_signal_up" in p["series"]:
            assert (p["series"]["macd_cross_signal_up"][i]
                    == bool(full["macd_cross_signal_up"].iloc[j]))


def test_ad_shares_time_scale_with_other_panels():
    html = _html()
    assert "P.ad={y:y,h:ad}" in html
    assert "bot=P.ad.y+P.ad.h" in html               # crosshair i siatka do dolu A/D
    assert "line(S.ad,i0,i1" in html                 # ten sam zakres indeksow

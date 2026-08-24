"""backend/v3/tests/test_tf_switcher.py — przelacznik 30m | 1H | 2H | 4H | 1D (offline).

Zero sieci, zero Massive. Testy sprawdzaja ZACHOWANIE: kanoniczna agregacje z jednego
zrodla 30m, kompletnosc 6 x 5 = 30 par, selektywne budowanie brakujacych interwalow oraz
zachowanie dashboardu przy zmianie interwalu.

Kontrakt niezmieniony wzgledem r591: historyczne wychylenia MACD wylacznie na 1D,
zdarzenie przeciecia przypisane do zamknietego bara potwierdzajacego, bez interpolacji.
"""

import datetime as _dt
import os
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

os.environ.setdefault("V3_NO_BROWSER", "1")

from v3.market_data import us_calendar as CAL      # noqa: E402
from v3.market_data import us_multi_tf as MTF      # noqa: E402
from v3.tools import fast_segmentation as FS       # noqa: E402
from v3.tests.test_fast_segmentation import _fake_payloads, _row  # noqa: E402

TFS = ("30m", "1H", "2H", "4H", "1D")


# ---------------------------------------------------------------- pomocnicze
def _sessions(y, m, d, count):
    """`count` kolejnych sesji NYSE poczawszy od podanej daty."""
    day, out = _dt.date(y, m, d), []
    while len(out) < count:
        if CAL.session_schedule(day):
            out.append(day)
        day += _dt.timedelta(days=1)
    return out


def _short_session():
    """Pierwsza sesja skrocona w listopadzie/grudniu 2025 (znaleziona z kalendarza)."""
    day = _dt.date(2025, 11, 1)
    while day < _dt.date(2026, 1, 5):
        s = CAL.session_schedule(day)
        if s and (pd.Timestamp(s["close_utc"]) - pd.Timestamp(s["open_utc"])
                  < pd.Timedelta(hours=6, minutes=30)):
            return day
        day += _dt.timedelta(days=1)
    return None


def _m30(days, drop=()):
    """Kanoniczne bary 30m tych sesji; `drop` usuwa wskazane otwarcia (luka w danych)."""
    idx, rows = [], []
    for day in days:
        for i, t in enumerate(MTF.expected_source_opens(day)):
            if t in drop:
                continue
            idx.append(pd.Timestamp(t))
            base = 100.0 + i
            rows.append((base, base + 1.0, base - 1.0, base + 0.5, 1000.0 + i))
    return pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"],
                        index=pd.DatetimeIndex(idx, name="bar_open_utc"))


def _dashboard(tmp, payloads, timeframes=TFS):
    FS._write_all(tmp, payloads, [], [], {}, "RUNNING", timeframes=timeframes)
    return open(os.path.join(tmp, "index.html"), "r", encoding="utf-8").read()


def _all_five(sym):
    return _fake_payloads(sym, TFS)


# ---------------------------------------------------------------- agregacja
def test_canonical_30m_drops_pre_and_after_hours():
    day = _sessions(2025, 1, 13, 1)[0]
    sched = CAL.session_schedule(day)
    bars = _m30([day])
    extra = pd.DataFrame(
        [(1.0, 1.0, 1.0, 1.0, 1.0), (2.0, 2.0, 2.0, 2.0, 2.0)],
        columns=["open", "high", "low", "close", "volume"],
        index=pd.DatetimeIndex([pd.Timestamp(sched["open_utc"]) - pd.Timedelta(minutes=30),
                                pd.Timestamp(sched["close_utc"])]))
    m30 = MTF.canonical_30m(pd.concat([extra, bars]).sort_index())
    assert len(m30) == len(bars)                       # PRE i AH odsiane
    assert m30.index.min() == pd.Timestamp(sched["open_utc"])
    assert m30.index.max() < pd.Timestamp(sched["close_utc"])


def test_buckets_anchored_at_session_open():
    day = _sessions(2025, 1, 13, 1)[0]
    open_utc = pd.Timestamp(CAL.session_schedule(day)["open_utc"])
    for minutes in (30, 60, 120, 240):
        assert MTF.expected_buckets(day, minutes)[0][0] == open_utc, minutes


def test_half_open_interval_no_bucket_at_close():
    day = _sessions(2025, 1, 13, 1)[0]
    close_utc = pd.Timestamp(CAL.session_schedule(day)["close_utc"])
    for minutes in (30, 60, 120, 240):
        starts = [b[0] for b in MTF.expected_buckets(day, minutes)]
        assert all(s < close_utc for s in starts), minutes
        assert MTF.expected_buckets(day, minutes)[-1][1] == close_utc, minutes


def test_last_bucket_is_shorter_when_session_does_not_divide():
    day = _sessions(2025, 1, 13, 1)[0]
    for minutes, expected in ((60, 7), (120, 4), (240, 2)):
        buckets = MTF.expected_buckets(day, minutes)
        assert len(buckets) == expected, minutes
        last = buckets[-1][1] - buckets[-1][0]
        assert last < pd.Timedelta(minutes=minutes), minutes   # krotszy, nie bledny


def test_short_session_has_fewer_and_shorter_buckets():
    short = _short_session()
    assert short is not None, "kalendarz musi znac sesje skrocona"
    full = _sessions(2025, 1, 13, 1)[0]
    assert len(MTF.expected_buckets(short, 120)) < len(MTF.expected_buckets(full, 120))
    assert len(MTF.expected_source_opens(short)) < len(MTF.expected_source_opens(full))


def test_dst_changes_utc_anchor_not_local_open():
    winter = pd.Timestamp(CAL.session_schedule(_sessions(2025, 1, 13, 1)[0])["open_utc"])
    summer = pd.Timestamp(CAL.session_schedule(_sessions(2025, 7, 14, 1)[0])["open_utc"])
    assert winter.hour != summer.hour                  # UTC sie przesuwa
    assert (winter.tz_convert(CAL.NY).hour, winter.tz_convert(CAL.NY).minute) \
        == (summer.tz_convert(CAL.NY).hour, summer.tz_convert(CAL.NY).minute)


def test_all_intraday_built_from_one_30m_source():
    day = _sessions(2025, 1, 13, 1)[0]
    m30 = MTF.canonical_30m(_m30([day]))
    counts = {}
    for tf_minutes, expected in ((60, 7), (120, 4), (240, 2)):
        frame, skipped = MTF.aggregate_from_lower(m30, tf_minutes)
        counts[tf_minutes] = len(frame)
        assert skipped == [], tf_minutes
        assert len(frame) == expected, tf_minutes
    assert len(m30) == 13                              # 6,5h = 13 barow 30m
    assert counts[240] == 2


def test_aggregate_uses_first_open_max_high_min_low_last_close():
    day = _sessions(2025, 1, 13, 1)[0]
    m30 = MTF.canonical_30m(_m30([day]))
    frame, _ = MTF.aggregate_from_lower(m30, 240)
    first = frame.iloc[0]
    src = m30.iloc[:8]                                 # 4h = 8 barow 30m
    assert first["open"] == src["open"].iloc[0]
    assert first["high"] == src["high"].max()
    assert first["low"] == src["low"].min()
    assert first["close"] == src["close"].iloc[-1]
    assert first["volume"] == src["volume"].sum()


def test_2h_and_4h_come_from_30m_not_from_1h():
    day = _sessions(2025, 1, 13, 1)[0]
    lower = _m30([day])
    m30 = MTF.canonical_30m(lower)
    now = pd.Timestamp(CAL.session_schedule(day)["close_utc"]) + pd.Timedelta(days=1)
    for tf, minutes in (("2H", 120), ("4H", 240)):
        direct, _ = MTF.aggregate_from_lower(m30, minutes)
        built = FS._canonical_intraday("TEST", tf, lower, now)
        assert list(built.index) == list(direct.index), tf
        assert list(built["close"]) == list(direct["close"]), tf
    assert MTF.provenance(120) == "MASSIVE_30M_RTH_AGGREGATED_120M"
    assert MTF.provenance(240) == "MASSIVE_30M_RTH_AGGREGATED_240M"
    assert MTF.SOURCE_MINUTES == 30


def test_no_bucket_mixes_two_sessions():
    days = _sessions(2025, 1, 13, 2)
    m30 = MTF.canonical_30m(_m30(days))
    frame, _ = MTF.aggregate_from_lower(m30, 240)
    for ts, row in frame.iterrows():
        assert pd.Timestamp(ts).tz_convert(CAL.NY).date() == row["session_date"]
        assert pd.Timestamp(row["bar_close_utc"]).tz_convert(CAL.NY).date() \
            == row["session_date"]
    assert len(frame) == 4                             # 2 sesje x 2 kubelki 4H


def test_incomplete_bucket_is_skipped_fail_closed():
    day = _sessions(2025, 1, 13, 1)[0]
    opens = MTF.expected_source_opens(day)
    m30 = MTF.canonical_30m(_m30([day], drop=(opens[2],)))
    frame, skipped = MTF.aggregate_from_lower(m30, 240)
    assert len(skipped) == 1
    assert skipped[0][1] == pd.Timestamp(CAL.session_schedule(day)["open_utc"])
    assert len(frame) == 1                             # pierwszy kubelek pominiety
    assert pd.Timestamp(CAL.session_schedule(day)["open_utc"]) not in frame.index


def test_unclosed_bucket_is_not_final():
    day = _sessions(2025, 1, 13, 1)[0]
    sched = CAL.session_schedule(day)
    lower = _m30([day])
    now = pd.Timestamp(sched["open_utc"]) + pd.Timedelta(hours=5)
    bars = FS._canonical_intraday("TEST", "4H", lower, now)
    assert list(bars["is_final"]) == [True, False]     # bar w budowie nie jest final


def test_30m_payload_source_is_canonical_30m():
    day = _sessions(2025, 1, 13, 1)[0]
    lower = _m30([day])
    now = pd.Timestamp(CAL.session_schedule(day)["close_utc"]) + pd.Timedelta(days=1)
    bars = FS._canonical_intraday("TEST", "30m", lower, now)
    assert len(bars) == 13 and bool(bars["is_final"].all())
    assert list(bars.index) == list(MTF.canonical_30m(lower).index)


# ---------------------------------------------------------------- kompletnosc
def test_thirty_pairs_are_required():
    wanted = list(FS.FAST_SET)
    with tempfile.TemporaryDirectory() as tmp:
        saved = {}
        for sym in wanted:
            saved.update(_all_five(sym))
        FS._save_payloads(tmp, saved)
        pc = FS.pair_completeness(tmp, wanted, TFS)
        assert pc["need"] == 30 and pc["have"] == 30
        assert pc["missing_pairs"] == []
        assert FS.final_status(tmp, wanted, "COMPLETE", TFS)[0] == "COMPLETE"


def test_one_missing_pair_blocks_complete_and_is_named():
    wanted = list(FS.FAST_SET)
    with tempfile.TemporaryDirectory() as tmp:
        saved = {}
        for sym in wanted:
            tfs = tuple(t for t in TFS if t != "2H") if sym == "PLTR" else TFS
            saved.update(_fake_payloads(sym, tfs))
        FS._save_payloads(tmp, saved)
        pc = FS.pair_completeness(tmp, wanted, TFS)
        assert pc["have"] == 29
        assert pc["missing_pairs"] == [("PLTR", "2H")]      # dokladna para, nie sam symbol
        assert "PLTR" not in pc["ready_symbols"]
        status, missing = FS.final_status(tmp, wanted, "COMPLETE", TFS)
        assert status == "PARTIAL_COMPLETE" and missing == ["PLTR"]


def test_missing_report_row_blocks_skip_with_pair_name():
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _all_five("RBLX"))
        rows = [_row("RBLX", "1D")] + [_row("RBLX", t) for t in ("30m", "1H", "2H")]
        todo = FS.missing_timeframes(tmp, "RBLX", TFS, rows)
        assert todo == ["4H"]                              # brak wiersza 4H
        ok, why = FS.validate_done(tmp, "RBLX", TFS, rows)
        assert ok is False and "MISSING_ROW" in why


def test_selective_build_only_missing_timeframes():
    """Stan r591: aktualne 1D i 1H. Budujemy wylacznie 30m, 2H i 4H."""
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _fake_payloads("RBLX", ("1D", "1H")))
        rows = [_row("RBLX", "1D"), _row("RBLX", "1H")]
        todo = FS.missing_timeframes(tmp, "RBLX", TFS, rows)
        assert todo == ["30m", "2H", "4H"]
        assert "1D" not in todo and "1H" not in todo


def test_complete_symbol_is_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _all_five("RBLX"))
        rows = [_row("RBLX", t) for t in TFS]
        assert FS.missing_timeframes(tmp, "RBLX", TFS, rows) == []
        ok, why = FS.validate_done(tmp, "RBLX", TFS, rows)
        assert ok is True and why == "OK"


def test_symbol_with_only_1d_and_1h_is_not_done():
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _fake_payloads("RBLX", ("1D", "1H")))
        ok, _why = FS.validate_done(tmp, "RBLX", TFS,
                                    [_row("RBLX", "1D"), _row("RBLX", "1H")])
        assert ok is False


def test_existing_1d_is_not_downloaded_again():
    """need_daily=False => zero zapytan o dzienne, nawet gdy pobieranie by wybuchlo."""
    real = FS.CV._aggs

    def boom(*a, **kw):
        raise AssertionError("zbedne pobranie 1D")

    FS.CV._aggs = boom
    try:
        daily, lower, diag = FS._fetch("RBLX", pd.Timestamp.now(tz="UTC"),
                                       need_daily=False, need_lower=False)
    finally:
        FS.CV._aggs = real
    assert daily is None and lower is None
    assert diag["requests"] == 0


def test_at_most_one_30m_fetch_per_symbol():
    calls = []
    real = FS._fetch

    def counting(symbol, now, need_daily=True, need_lower=True):
        calls.append((symbol, need_daily, need_lower))
        raise RuntimeError("stop po pobraniu")

    FS._fetch = counting
    try:
        try:
            FS.process_symbol("RBLX", pd.Timestamp.now(tz="UTC"), TFS)
        except RuntimeError:
            pass
    finally:
        FS._fetch = real
    assert len(calls) == 1                              # jedno pobranie na symbol
    assert calls[0][2] is True                          # 30m = jedyne zrodlo intraday


def test_interrupted_run_resumes_from_partial_storage():
    with tempfile.TemporaryDirectory() as tmp:
        done = ("1D", "1H", "30m")
        FS._save_payloads(tmp, _fake_payloads("RBLX", done))
        rows = [_row("RBLX", t) for t in done]
        assert FS.missing_timeframes(tmp, "RBLX", TFS, rows) == ["2H", "4H"]
        FS._save_payloads(tmp, _fake_payloads("RBLX", ("2H", "4H")))
        rows += [_row("RBLX", "2H"), _row("RBLX", "4H")]
        assert FS.missing_timeframes(tmp, "RBLX", TFS, rows) == []


def test_payloads_csv_report_and_dashboard_agree():
    wanted = list(FS.FAST_SET)
    with tempfile.TemporaryDirectory() as tmp:
        real = FS.process_symbol

        def stub(sym, now=None, timeframes=TFS):
            return (_fake_payloads(sym, tuple(timeframes)),
                    [_row(sym, t) for t in timeframes],
                    {"fetch": 0.0, "build": 0.0, "variants": 0.0, "total": 0.0,
                     "requests": 7})

        FS.process_symbol = stub
        FS.CV.load_universe_rows = lambda: [{"symbol": s} for s in wanted]
        try:
            res = FS.run(tmp, wanted, TFS, resume=False)
        finally:
            FS.process_symbol = real
        assert res["status"] == "COMPLETE" and res["complete"] is True
        assert FS.pair_completeness(tmp, wanted, TFS)["have"] == 30
        rows, _stale = FS._load_rows(tmp)
        for tf in TFS:
            assert len([r for r in rows if r["tf"] == tf]) == 6, tf
        report = open(os.path.join(tmp, "report.md"), "r", encoding="utf-8").read()
        for tf in TFS:
            assert report.count("| %s |" % tf) == 6, tf
        html = open(os.path.join(tmp, "index.html"), "r", encoding="utf-8").read()
        assert "6/6 symboli" in html and "TF 30/30" in html


# ---------------------------------------------------------------- UI
def test_five_buttons_in_contract_order():
    with tempfile.TemporaryDirectory() as tmp:
        html = _dashboard(tmp, _all_five("RBLX"))
        order = [html.index('data-tf="%s"' % tf) for tf in TFS]
        assert order == sorted(order), "kolejnosc musi byc 30m, 1H, 2H, 4H, 1D"
        for tf in TFS:
            assert '>%s<' % tf in html, tf
        assert html.count('data-tf=') == 5


def test_no_dropdown_for_timeframe():
    with tempfile.TemporaryDirectory() as tmp:
        html = _dashboard(tmp, _all_five("RBLX"))
        selects = html.count("<select")
        assert selects == 1                     # wylacznie selektor segmentacji
        assert 'id="segsel"' in html
        assert 'id="tfsel"' not in html


# --- pasek TF nie moze obcinac zadnego interwalu (regresja r594: 4H i 1D znikaly) ---
def _css(html):
    return html[html.index("<style>"):html.index("</style>")]


def _rule(css, selector):
    i = css.index(selector + "{")
    return css[i + len(selector) + 1:css.index("}", i)]


def test_tf_bar_cannot_shrink_or_clip_buttons():
    with tempfile.TemporaryDirectory() as tmp:
        css = _css(_dashboard(tmp, _all_five("RBLX")))
        bar = _rule(css, ".tf")
        assert "flex:0 0 auto" in bar            # pasek nie kurczy sie w #top
        assert "overflow:visible" in bar         # ...i nie wycina wystajacych dzieci
        assert "overflow:hidden" not in bar
        btn = _rule(css, ".tf button")
        assert "flex:0 0 auto" in btn
        assert "white-space:nowrap" in btn       # etykieta nie zawija sie do zera


def test_no_timeframe_button_is_hidden():
    with tempfile.TemporaryDirectory() as tmp:
        html = _dashboard(tmp, _all_five("RBLX"))
        bar = html[html.index('<div class="tf">'):]
        bar = bar[:bar.index("</div>")]
        assert bar.count("<button") == 5
        for bad in ("display:none", "visibility:hidden", "hidden", "width:0"):
            assert bad not in bar, bad
        from v3.tools.chart_validation_template import _PAGE
        assert "style.display='none'" not in _PAGE[_PAGE.index("function setTf("):
                                                   _PAGE.index("function xOf(")]


def test_neighbouring_controls_do_not_squeeze_the_bar():
    with tempfile.TemporaryDirectory() as tmp:
        css = _css(_dashboard(tmp, _all_five("RBLX")))
        assert "flex:0 0 auto" in _rule(css, "#reset")        # Reset nie nachodzi
        assert "text-overflow:ellipsis" in _rule(css, "#tName")  # nazwa spolki ustepuje
        build = _rule(css, "#build")
        assert "flex:0 1 auto" in build and "text-overflow:ellipsis" in build


def test_tf_bar_fits_1920_top_row_budget():
    """Arytmetyka szerokosci dla 1920x1080: pasek TF ma zapas nawet przy skalowaniu 125%.

    #nav 172 + #side 236 => #top ma 1512 px przy 100% i ~1210 px przy 125%.
    Pasek TF: 5 x (2 x 10 padding + ~22 tekst) + ramka = ~212 px.
    """
    with tempfile.TemporaryDirectory() as tmp:
        css = _css(_dashboard(tmp, _all_five("RBLX")))
        assert "padding:3px 10px" in _rule(css, ".tf button")
        top_at_125 = (1920 / 1.25) - 172 - 236
        tf_bar = 5 * (2 * 10 + 22) + 2
        assert tf_bar < top_at_125 / 2                # polowa paska zostaje wolna


def test_active_button_keeps_blue_background():
    with tempfile.TemporaryDirectory() as tmp:
        css = _css(_dashboard(tmp, _all_five("RBLX")))
        assert "background:var(--macd)" in _rule(css, ".tf button.on")


def test_chart_geometry_untouched():
    from v3.tools.chart_validation_template import _PAGE
    assert "#charts{flex:1;position:relative;min-height:0;cursor:crosshair}" in _PAGE
    assert "canvas{position:absolute;inset:0;width:100%;height:100%}" in _PAGE


def test_switch_to_4h_and_1d_loads_matching_payload():
    with tempfile.TemporaryDirectory() as tmp:
        html = _dashboard(tmp, _all_five("RBLX"))
        for tf in ("4H", "1D"):
            assert '"RBLX|%s"' % tf in html, tf
        from v3.tools.chart_validation_template import _PAGE
        assert "function setTf(t){if(!D[sym+'|'+t])return;tf=t;" in _PAGE
        assert "function cur(){return D[sym+'|'+tf]}" in _PAGE
        assert "b.onclick=()=>setTf(b.dataset.tf)" in _PAGE   # nie tylko etykieta


def test_every_symbol_offers_all_five_timeframes():
    wanted = list(FS.FAST_SET)
    with tempfile.TemporaryDirectory() as tmp:
        saved = {}
        for sym in wanted:
            saved.update(_all_five(sym))
        html = _dashboard(tmp, saved)
        for sym in wanted:
            for tf in TFS:
                assert '"%s|%s"' % (sym, tf) in html, (sym, tf)


def test_rebuild_from_existing_payloads_does_not_fetch():
    """Naprawa UI wymaga tylko przebudowy: zero pobierania, zero liczenia wykresow."""
    wanted = list(FS.FAST_SET)
    with tempfile.TemporaryDirectory() as tmp:
        saved = {}
        for sym in wanted:
            saved.update(_all_five(sym))
        FS._save_payloads(tmp, saved)
        rows = [_row(s, t) for s in wanted for t in TFS]
        FS._write_all(tmp, {}, rows, [], {}, "RUNNING", timeframes=TFS)
        real_fetch, real_proc = FS._fetch, FS.process_symbol

        def boom(*a, **kw):
            raise AssertionError("przebudowa nie moze pobierac danych")

        FS._fetch = boom
        FS.process_symbol = boom
        try:
            res = FS.rebuild(tmp)
        finally:
            FS._fetch, FS.process_symbol = real_fetch, real_proc
        assert sorted(res["symbols"]) == sorted(wanted)
        html = open(os.path.join(tmp, "index.html"), "r", encoding="utf-8").read()
        assert "TF 30/30" in html and "6/6 symboli" in html
        for tf in TFS:
            assert 'data-tf="%s"' % tf in html, tf


def test_active_button_is_marked_and_missing_one_disabled():
    from v3.tools.chart_validation_template import _PAGE
    assert "b.classList.toggle('on',tf===t)" in _PAGE
    assert "b.disabled=!ok" in _PAGE
    assert "'brak payloadu '+sym+' '+t" in _PAGE


def test_switching_tf_does_not_fetch_or_recompute():
    from v3.tools.chart_validation_template import _PAGE
    body = _PAGE[_PAGE.index("function setTf("):]
    body = body[:body.index("tfButtons().forEach")]
    for bad in ("fetch(", "XMLHttpRequest", "compute", "ema(", "macd("):
        assert bad not in body, bad
    assert "D[sym+'|'+t]" in body               # gotowy payload z pamieci strony


def test_switching_tf_clears_previous_state():
    from v3.tools.chart_validation_template import _PAGE
    body = _PAGE[_PAGE.index("function setTf("):]
    body = body[:body.index("tfButtons().forEach")]
    for part in ("view=null", "hover=-1", "hidetip()", "render()"):
        assert part in body, part


def test_missing_payload_shows_named_pair_not_empty_chart():
    from v3.tools.chart_validation_template import _PAGE
    assert "BRAK PAYLOADU '+sym+' '+tf" in _PAGE
    with tempfile.TemporaryDirectory() as tmp:
        html = _dashboard(tmp, _fake_payloads("RBLX", ("1D", "1H")))
        assert "BRAK PAYLOADU" in html
        assert '"RBLX|2H"' not in html          # payloadu po prostu nie ma


def test_symbol_change_keeps_selected_timeframe():
    from v3.tools.chart_validation_template import _PAGE
    line = [x for x in _PAGE.splitlines() if "el.onclick=()=>{sym=r.symbol" in x]
    assert line, "handler wyboru spolki"
    assert "tf=" not in line[0]                 # zmiana spolki nie rusza interwalu


def test_reset_applies_to_current_symbol_and_tf():
    from v3.tools.chart_validation_template import _PAGE
    assert "document.getElementById('reset').onclick=()=>{view=null;hover=-1;render()}" \
        in _PAGE
    assert "function cur(){return D[sym+'|'+tf]}" in _PAGE


def test_timeframe_setting_uses_versioned_key():
    from v3.tools.chart_validation_template import _PAGE
    assert "const TF_KEY='v3chart.tf.v3'" in _PAGE
    assert "if(TFS.indexOf(s)>=0)tf=s" in _PAGE      # nieznana wartosc => 1D
    assert "let sym=null,tf='1D'" in _PAGE           # domyslny interwal jak w r591


def test_one_renderer_for_all_timeframes():
    from v3.tools.chart_validation_template import _PAGE
    assert _PAGE.count("function draw(d){") == 1
    assert _PAGE.count("function render(){") == 1


# ---------------------------------------------------------------- MACD
def _events(diffs):
    """Zdarzenia przeciec z produkcyjnej definicji dla zadanej roznicy MACD-Signal."""
    from v3.indicators.macd import detect_macd_events
    idx = pd.RangeIndex(len(diffs))
    macd = pd.Series([float(d) for d in diffs], index=idx)
    signal = pd.Series([0.0] * len(diffs), index=idx)
    hist = macd - signal
    ev = detect_macd_events(macd, signal, hist)
    return ([i for i in idx if ev["macd_cross_signal_up"].iloc[i]],
            [i for i in idx if ev["macd_cross_signal_down"].iloc[i]])


def test_cross_up_and_down_are_assigned_to_confirming_bar_on_every_tf():
    for tf in TFS:
        up, down = _events([-1.0, 1.0, -1.0])
        assert up == [1], tf                    # potwierdzenie na zamknietym barze i
        assert down == [2], tf


def test_zero_touch_four_cases_unchanged():
    assert _events([-1.0, 0.0, -1.0]) == ([], [2])
    assert _events([-1.0, 0.0, 1.0]) == ([2], [])
    assert _events([1.0, 0.0, 1.0]) == ([2], [])
    assert _events([1.0, 0.0, -1.0]) == ([], [2])


def test_marker_crosshair_and_tooltip_share_one_index():
    from v3.tools.chart_validation_template import _PAGE
    assert "dot(xOf(i,i0,i1,W),yOf(v,mlo,mhi,P.macd),up?'#00c853':'#ff1744',3.6)" in _PAGE
    assert "const cu=S.macd_cross_signal_up&&S.macd_cross_signal_up[i];" in _PAGE
    assert "function idxAt(px,i0,i1,W)" in _PAGE     # crosshair z tego samego indeksu


def test_no_interpolation_in_renderer_for_any_tf():
    from v3.tools.chart_validation_template import _PAGE
    from v3.tools.macd_segmentation_template import _MARKER_JS, _TIP_JS
    for src in (_PAGE, _MARKER_JS, _TIP_JS):
        for bad in ("d0/(d0-d1)", "xOf(i-1", "i-0.5", "i+0.5"):
            assert bad not in src, bad


def test_every_tf_payload_carries_cross_series():
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _all_five("RBLX"))
        for tf in TFS:
            pl = FS.load_all_payloads(tmp)["RBLX|%s" % tf]
            assert pl["tf"] == tf


# ---------------------------------------------------------------- wychylenia
def test_historical_excursion_only_on_1d():
    with tempfile.TemporaryDirectory() as tmp:
        FS._save_payloads(tmp, _all_five("RBLX"))
        saved = FS.load_all_payloads(tmp)
        assert saved["RBLX|1D"]["top_excursion"] is not None
        for tf in ("30m", "1H", "2H", "4H"):
            pl = saved["RBLX|%s" % tf]
            assert pl["top_excursion"] is None, tf
            assert pl["local_valleys"] == [], tf


def test_intraday_payload_has_no_excursion_source_for_tooltip():
    from v3.tools.macd_segmentation_template import _INIT_JS, _TIP_JS
    assert "TOP2=(d.top_excursion||null)" in _TIP_JS
    assert "if(!is1D){sel.disabled=true" in _INIT_JS
    assert _INIT_JS.count("historyczne wychylenia wylaczone") == 1
    for tf in ("30m", "2H", "4H"):
        pl = _fake_payloads("RBLX", (tf,))["RBLX|%s" % tf]
        assert pl["top_excursion"] is None and pl["local_valleys"] == []


def test_excursion_control_follows_every_tf_button():
    from v3.tools.macd_segmentation_template import _INIT_JS
    assert "document.querySelectorAll('#top .tf button[data-tf]')" in _INIT_JS
    assert "sync()" in _INIT_JS


def test_segmentation_timeframe_contract_untouched():
    src = open(os.path.join(os.path.dirname(os.path.abspath(FS.__file__)),
                            "fast_segmentation.py"), "r", encoding="utf-8").read()
    assert 'SEGMENTATION_TIMEFRAME = "1D"' in src
    assert "if tf != SEGMENTATION_TIMEFRAME:" in src
    assert FS.ALL_TIMEFRAMES == TFS
    assert FS.INTRADAY_TIMEFRAMES == ("30m", "1H", "2H", "4H")

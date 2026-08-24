# CHANGELOG V3 — Skaner wykresów giełdowych

`config.VERSION` to wyłącznie krótki identyfikator buildu (np. `2026-08-16-r591`).
Opis zmian mieszka tutaj.

## r594 — 2026-08-16 — pasek interwałów obcinał 4H i 1D (naprawa CSS)
ROOT CAUSE: `chart_validation_template._PAGE`, reguła `.tf{display:flex;…;overflow:hidden}`.
`#top` jest kontenerem flex, a `.tf` nie miał `flex-shrink:0` ani przyciski `flex:none` —
przy ciasnym pasku kontener kurczył się poniżej sumy szerokości przycisków, a
`overflow:hidden` (dodany tylko dla zaokrąglonych narożników) wycinał wystające dzieci
bez śladu: 4H i 1D. Przy dwóch przyciskach r591 próg nigdy nie był przekraczany.

Poprawka wyłącznie w CSS paska: `.tf{flex:0 0 auto;overflow:visible}`, `.tf button{flex:0 0 auto;
white-space:nowrap}`, zaokrąglenie przeniesione na `:first-child`/`:last-child`, padding
przycisków 13→10 px, `#reset{flex:0 0 auto}`, `#tName` i `#build` skracane elipsą — miejsca
ustępuje nazwa spółki, nigdy interwał. Aktywny interwał nadal na niebieskim
`var(--macd)`. Geometria wykresów, payloady, agregacja, MACD/Signal, segmentacja B 0,25
i reguła wychyleń tylko na 1D — nietknięte.

Naprawa nie wymaga skanu: `PRZEBUDUJ-DASHBOARD-SEGMENTACJI.bat` (`--rebuild`) odtwarza
dashboard z 30 zapisanych payloadów bez pobierania i bez przeliczania.

11 nowych testów w `test_tf_switcher.py`: brak kurczenia i obcinania paska, pięć
widocznych przycisków bez `display:none`, sąsiednie kontrolki nie ściskają paska,
arytmetyka szerokości dla 1920×1080 przy skalowaniu 125%, niebieskie tło aktywnego,
nietknięta geometria wykresów, 4H i 1D ładują własny payload, każdy symbol ma pięć
interwałów, przebudowa bez pobierania.

## r593 — 2026-08-16 — poprawka fixture jednego testu r591
Kod produkcyjny NIETKNIETY. `test_all_six_symbols_have_1h_row_and_control` zakladal
jeszcze 6 x 2 = 12 par i wolal `pair_completeness()` bez argumentu `timeframes`, wiec
zderzal fixture 1D+1H z produkcyjnym kontraktem 30 par (have 12 z 30). Fixture zostal
rozszerzony do pelnych 6 x 5 = 30 payloadow i 30 wierszy raportu; cel regresyjny bez
zmian — szesc kompletnych warstw 1H (payload, wiersz, aktywna kontrolka) wewnatrz
kompletu 30/30. Kontraktu 30/30 nie oslabiono w zadnym miejscu.

## r592 — 2026-08-16 — przełącznik interwałów 30m | 1H | 2H | 4H | 1D
Zakres tej wersji to WYŁĄCZNIE przełącznik interwałów. COMPACT i UI Cykle V3 nie są
wdrożone — pozostają osobnymi zadaniami produktowymi wymagającymi specyfikacji.

**Dane i agregacja.** Podłączone istniejące `v3/market_data/us_multi_tf.py` — bez drugiej
implementacji. Nowe `fast_segmentation._canonical_intraday()` buduje każdy interwał
intraday z JEDNEGO kanonicznego zbioru 30m: 1H nadal zatwierdzoną ścieżką
`us_rth.aggregate_1h_from_lower`, 2H i 4H bezpośrednio z 30m (nigdy z gotowego 1H).
Kontrakt bez zmian: kotwica na otwarciu sesji, kubełki `[open, close)`, krótszy ostatni
kubełek, sesje skrócone i DST z kalendarza, brak mieszania sesji, fail closed.
`_fetch()` przyjmuje `need_daily` / `need_lower` — istniejące 1D nie jest pobierane
ponownie; 30m pobierane maksymalnie raz na symbol w przebiegu.

**Kompletność i wznowienie.** `ALL_TIMEFRAMES = ("30m","1H","2H","4H","1D")` jest jednym
źródłem prawdy dla skanu, kompletności i UI. Wymagane 6 × 5 = 30 par; `PAYLOAD_SCHEMA`
→ `FAST_SEG_PAYLOAD_3`. Nowe `missing_timeframes()` decyduje o budowie osobno dla
każdego interwału, więc symbol z aktualnym 1D i 1H buduje tylko 30m, 2H i 4H.
Logi rozróżniają `SKIP_ALREADY_DONE`, `BUILD_MISSING_TF`, `REPAIR_MISSING_ROW`,
`STALE_SCHEMA`, `MISSING_PAYLOAD`, `MISSING_REPORT_ROW` i podają dokładną parę
(np. `PLTR 2H`). `COMPLETE` nadal wymaga zgodności payloadów, `results.csv`, `report.md`
i dashboardu.

**Dashboard.** Pięć przycisków w kolejności `30m | 1H | 2H | 4H | 1D` (`data-tf`), bez listy
rozwijanej, jeden renderer. `setTf()` czyta gotowy payload: zero pobierania, zero liczenia
wskaźników w przeglądarce; kasuje zoom, hover i tooltip, więc nie zostaje żadna wartość
z poprzedniego interwału. Domyślny interwał nadal 1D; ustawienie w wersjonowanym kluczu
`v3chart.tf.v3`, nieznana wartość wraca do 1D. Brak payloadu = przycisk nieaktywny
i komunikat `BRAK PAYLOADU <SYMBOL> <TF>` zamiast pustego wykresu. Zmiana spółki
zachowuje wybrany interwał.

**Nietknięte.** Definicja przecięcia MACD/Signal (event na zamkniętym barze `i`, bez
interpolacji, cztery zatwierdzone przypadki dotknięcia zera), historyczne wychylenia
wyłącznie na 1D (30m/1H/2H/4H bez markera i bez linii w tooltipie), segmentacja B 0,25,
kolory, palety, wysokości i układ paneli, legendy, fonty.

**Rozszerzone listy interwałów.** `features/schema.ALLOWED_TIMEFRAMES` i walidacja
`warmup.WarmupMeta` obejmują teraz 30m/1H/2H/4H/1D.

**Testy.** Nowy `v3/tests/test_tf_switcher.py` (agregacja, kompletność 30 par, selektywna
budowa, UI, MACD na pięciu interwałach, wychylenia tylko 1D) dopisany do
`run_market_data_tests.MODULES`. Testy r591 zależne od dwóch interwałów dostały jawne
`("1D","1H")` — kontrakt liczników zmienił się z 12 na 30 par.

## r591 — 2026-08-16 — dwa testy przecięć dopasowane do kontraktu
Zero zmian w kodzie produkcyjnym, MACD/Signal, B 0,25, wychyleniach, kolorach
i paletach.

`test_macd_marker_uses_interpolated_crossing_point` → `..._uses_event_bar_not_interpolation`.
Stary test wymagał formuły `d0/(d0-d1)`, usuniętej świadomie w r590. Sprawdza teraz
zachowanie: event czytany po indeksie `i`, marker na `dot(xOf(i,...))`, tooltip i crosshair
na tym samym `i`, brak `xOf(i-1` i brak interpolacji w ścieżce markera.

Błędny fixture `[+1, 0, +1]` opisany jako „dotknięcie bez przecięcia" rozbity na cztery
przypadki różnicy `MACD − Signal`. Weryfikacja wobec zatwierdzonej definicji ujawniła, że
dotknięcie zera zalicza się do obu stron przez `<=` i `>=`, więc:

| różnica | cross up | cross down |
|---|---|---|
| `[-1, 0, -1]` | brak | **bar 2** |
| `[-1, 0, +1]` | **bar 2** | brak |
| `[+1, 0, +1]` | **bar 2** | brak |
| `[+1, 0, -1]` | brak | **bar 2** |

Testy odzwierciedlają ten wynik z komentarzem — definicja produkcyjna nietknięta.

## r590 — 2026-08-16 — wyrównanie markerów przecięć MACD/Signal
Wyłącznie pozycja kropki. Zero zmian w MACD, Signal, eventach, B 0,25, wychyleniu
historycznym, kolorach momentum, paletach i kompletności 12/12.

**ROOT CAUSE: interpolacja dodana w r557.** Marker był rysowany w geometrycznym punkcie
przecięcia odcinków MACD i Signal:
`x = xOf(i-1) + (xOf(i) - xOf(i-1)) * t`, gdzie `t = d0/(d0-d1)`.

Dla PLTR 1D `2026-02-18/19`: `d0 = −10,624 − (−10,620) = −0,004`, `d1 = −10,199 −
(−10,655) = +0,456`, więc `t = 0,0087` — kropka lądowała na **0,9% odległości** od bara
`i−1`, czyli wizualnie na barze poprzednim. Im płytsze przecięcie, tym większe
przesunięcie. Tooltip i crosshair czytały `[i]`, marker rysował się przy `i−1` — dwie
warstwy rozjeżdżały się mimo jednej tablicy zdarzeń.

Interpolacja usunięta. Kropka siedzi na `xOf(i)` — dokładnie tam, gdzie crosshair, OHLC
i komunikat tooltipa. Źródłem pozostają wyłącznie locked eventy `macd_cross_signal_up/down`
z payloadu; renderer nie wykrywa przecięć samodzielnie i nie stosuje żadnego `±1`.

7 nowych testów: marker na barze `i` bez interpolacji, syntetyczne przecięcia w górę i w
dół, dotknięcie linii bez przejścia nie tworzy zdarzenia, regresja PLTR `2026-02-18/19`,
marker i tooltip czytają ten sam indeks, zdarzenia przetrwają przycięcie do 250 barów.

## r589 — 2026-08-16 — samonaprawa brakujących wierszy z payloadów
Kontrola `NIESPOJNOSC` nietknięta. Zero zmian w B 0,25, markerach, kolorach i interwałach.

**ROOT CAUSE potwierdzony.** `SKIP_ALREADY_DONE` opierał się wyłącznie na payloadach.
PLTR i ADTN miały komplet 1D+1H, ale odziedziczony `results.csv` nie miał ich wierszy 1H —
symbole były pomijane, zanim cokolwiek mogło je naprawić.

1. `validate_done()` przyjmuje teraz `rows` i wymaga wierszy dla **wszystkich** interwałów;
   brak daje `STALE_DONE_MISSING_ROW (1H)`.
2. **Samonaprawa przed pętlą**: `repair_missing_rows()` odtwarza brakujący wiersz
   z istniejącego payloadu przez `row_from_payload()`. Zero zapytań do Massive, zero
   przeliczania wskaźników i wykresu. Log: `REPAIR_MISSING_ROW PLTR 1H FROM_PAYLOAD`.
   Zapis atomowy, `report.md` i `index.html` przebudowywane.
3. Payload w starym schemacie albo bez `local_valleys` nie nadaje się na źródło — symbol
   trafia do przeliczenia z jawną przyczyną, nigdy do cichego `SKIP`.

4 nowe testy, w tym odtworzenie rzeczywistego stanu po r585 (12 payloadów, 6 wierszy 1D,
4 wiersze 1H): potwierdzają odtworzenie dwóch brakujących wierszy, brak jakiegokolwiek
pobierania, `COMPLETE`, zgodność CSV, raportu, dashboardu i liczników oraz legalny `SKIP`
przy drugim przebiegu.

## r588 — 2026-08-16 — niepełne fixture'y w dwóch testach migracji
Kontrola spójności z r587 zadziałała poprawnie — to fixture'y były niepełne. Zero
osłabienia kontroli, zero zmian w kodzie produkcyjnym.

**Diagnoza.** Oba testy tworzyły payloady 1D i 1H (`_fake_payloads` daje oba), ale wiersze
raportu tylko dla 1D: wspólna atrapa `_run_with_stub` zwracała jednoelementową listę.
Do tego INTU, pomijany jako gotowy, nie miał żadnych wierszy — `process_symbol` nie jest
dla niego wołany, więc nikt ich nie tworzył. Stąd `NIESPOJNOSC: INTU 1D, INTU 1H, RBLX 1H`
i słuszne `PARTIAL_COMPLETE`.

**Naprawa fixture'ów.** Atrapa zwraca teraz wiersze obu interwałów, tak jak rzeczywisty
przebieg po r587. Nowy `_seed_rows()` zasiewa komplet wierszy dla symboli, które mają
zostać pominięte. Stary rekord sprzed migracji dokleja `_write_legacy_csv_append()`, żeby
nie kasować zasianych wierszy.

Wzmocnione asercje: obok `complete=True` sprawdzane są `status == "COMPLETE"`, brak
wierszy sprzed migracji oraz zgodność liczby wierszy 1D i 1H z liczbą symboli
w payloadach.

## r587 — 2026-08-16 — brakujące wiersze 1H w raporcie
Zero zmian w algorytmie B 0,25 i w wyglądzie wykresów.

**ROOT CAUSE.** Gałąź 1H w `process_symbol()` robiła `continue` **przed** `rows.append()`.
Payload 1H powstawał i trafiał na dysk, więc `pair_completeness()` słusznie widziało
12/12, ale wiersz raportu nie istniał — stąd `spolki 1H: 4`, cztery wiersze w
`results.csv` i `report.md` oraz pusta kontrolka 1H przy PLTR i ADTN. Pięć warstw
rozjeżdżało się, bo tylko jedna z nich była zasilana w tej gałęzi.

Wiersz 1H jest teraz zapisywany przed `continue`. Dodatkowo `COMPLETE` wymaga zgodności
warstw: jeśli payloady są kompletne, a brakuje wierszy raportu, status schodzi do
`PARTIAL_COMPLETE` z logiem `NIESPOJNOSC` i listą brakujących par.

Instrukcja końcowa w skrypcie produkcyjnym zastąpiona treścią zgodną z produkcją
(B 0,25, jedno wychylenie na 1D, wyłączone na 1H, znaczenie kropek). Usunięte diakrytyki
z komunikatów konsoli, które psuły się w CP1250 (`sieŠ`, `wykresˇw`).

3 nowe testy: sześć wierszy 1H w `results.csv`, `report.md`, payloadach i kontrolce
dashboardu; payloady bez wierszy nie dają `COMPLETE`; instrukcja BAT zgodna z produkcją.

## r586 — 2026-08-16 — diagnostyka wychyleń: dlaczego spółka nie ma punktu
Próg i algorytm B 0,25 **nietknięte** — zgodnie z poleceniem najpierw liczby.

Nowe `v3/tools/excursion_diagnostics.py` + `DIAGNOSTYKA-WYCHYLEN-MACD.bat`. Dla każdej
spółki na **pełnej historii 1D po rozgrzewce**, przed jakimkolwiek przycięciem do okna 250:
liczba barów, zakres dat, `std(MACD)`, próg `0,25 × std`, **wszystkie** surowe minima
lokalne, a dla każdego: indeks, data, wartość MACD, lewe i prawe odbicie, prominencja,
`PASS/REJECT` i jawny powód odrzucenia — z podaniem, jaki procent progu osiągnęła
prominencja albo że brakuje odbicia po którejś stronie.

UI: gdy `top_excursion` nie istnieje, opcja „pokaż największe historyczne wychylenie" jest
wyłączona i ukryta, nie tylko selektor nieaktywny.

5 nowych testów: przebieg jak PLTR/ADTN z wyraźną doliną **musi** dać `top_excursion`
(sprawdzane w detektorze i w `_variants`), minimum bez prawego odbicia odrzucane z jawnym
powodem, diagnostyka liczy na pełnej serii a nie na oknie, każde odrzucenie ma powód
liczbowy, opcja UI ukryta bez punktu.

## r585 — 2026-08-16 — siedem testów dopasowanych do kontraktu r584
Zero zmian w kodzie produkcyjnym, algorytmie B 0,25, kolorach momentum, paletach
i zasadzie jednego markera.

Wszystkie siedem sprawdzało stan sprzed r584. Zamiast poluzować asercje, każdy generuje
teraz dashboard w katalogu tymczasowym i czyta wynik:

1. `test_variant_switch_hides_only_segmentation_markers` — dwie nowe opcje w HTML, brak
   nazw wariantów, kropki przecięć obecne w rendererze i nieobecne w warstwie segmentacji.
2. `test_production_selector_has_no_diagnostic_variants` — dokładnie dwa `<option>`,
   payload 1H bez źródła markera.
3. `test_out_of_view_point_is_not_replaced` — komunikat „poza widocznym oknem", ten sam
   `index_full`, żadna lokalna dolina nie awansuje na marker.
4. `test_status_cannot_be_complete_with_missing_symbols` — 12 wymaganych par, 10 obecnych,
   brakujące dokładnie `PLTR 1H` i `ADTN 1H`, cztery gotowe symbole.
5. `test_final_status_counts_payloads_not_loop_state` — pętla obsługuje sześć symboli,
   ale przy 10/12 wynik zostaje `PARTIAL_COMPLETE` i `complete=False`.
6. `test_old_diagnostic_fields_are_stripped_on_load` — `_stale` istnieje tylko w pamięci
   i nie trafia do CSV, raportu, payloadu ani dashboardu.
7. `test_build_header_shows_progress_counter` — `4/6 symboli · TF 8/12 · PARTIAL_COMPLETE`
   oraz `6/6 symboli · TF 12/12` bez `PARTIAL_COMPLETE`.

## r584 — 2026-08-16 — kompletność na parach symbol–TF i selektor na 1D
Zero zmian w algorytmie B 0,25, kolorach momentum i paletach RSI/Stochastic.

**Kompletność.** `pair_completeness()` liczy pary symbol–interwał: 6 spółek × 2 = 12
wymaganych payloadów. Symbol z samym 1D nie jest gotowy, więc nagłówek nie pokaże już
`6/6` przy dziesięciu parach — pokazuje `4/6 symboli · TF 10/12`. `COMPLETE` i kod 0
tylko przy 12/12.

**Brakujące interwały widoczne.** Po przebiegu symbolu sprawdzane jest, czy wróciły
wszystkie interwały; brak któregokolwiek trafia do listy błędów jako
`BRAK PAYLOADU 1H - symbol niekompletny` i loguje `NIEKOMPLETNY`. Wcześniej PLTR 1H
i ADTN 1H znikały bez śladu.

**Zera z migracji.** Wiersz sprzed migracji dostaje znacznik `_stale` i trafia do raportu
jako `(do przeliczenia)`, nie jako policzone `0`. Znacznik nie przecieka do CSV.

**Selektor na 1D.** Komunikat „historyczne wychylenia wylaczone dla tego interwalu"
pojawia się **wyłącznie na 1H**. Na 1D z istniejącym `top_excursion` selektor jest aktywny
i ma dwie opcje: „bez markera historycznego" oraz „pokaż największe historyczne
wychylenie". Punkt poza oknem daje komunikat „poza widocznym oknem" i nie jest zastępowany
lokalnym minimum.

5 nowych testów: 12 par z wykryciem braku PLTR 1H i ADTN 1H, nagłówek z parami TF, zera
z migracji nieraportowane jako dane, aktywny selektor na 1D, komunikat poza oknem.

## r583 — 2026-08-16 — przeciek nazw wariantów do raportu produkcyjnego
Jedna linia w `_report()`. Zero zmian w algorytmie, migracji i renderowaniu.

Sekcja „## Segmentacja" w `report.md` kończyła się zdaniem „Warianty A, B 0,50 i C:
wylacznie raport diagnostyczny…" — zaszytą stałą, nie danymi ze starego rekordu.
Test behawioralny z r582 słusznie to złapał: produkcyjny raport nie może wymieniać
wariantów diagnostycznych.

Zastąpione neutralnym odsyłaczem:

```
Oddzielne narzedzie diagnostyczne:
wyniki-v3-2/porownanie-wariantow/
```

Komunikat asercji podaje teraz ścieżkę sprawdzanego pliku, więc przy kolejnym takim
błędzie od razu widać, który raport został odczytany.

## r582 — 2026-08-16 — ostatni test przepisany na zachowanie
Zero zmian w migracji. `test_production_report_has_no_diagnostic_columns` skanował źródło
i wywracał się na `b050`, który **musi** tam być — to nazwa starej kolumny potrzebna do
rozpoznania i oczyszczenia danych historycznych.

Test uruchamia teraz migrację w katalogu tymczasowym i czyta **wygenerowane pliki**:
nagłówek `results.csv` równy dokładnie `REQUIRED_ROW_FIELDS`, tabelę w `report.md`, dane
w `index.html` i zapisane payloady. Potwierdza brak wszystkich ośmiu dawnych kolumn,
wyboru A/B/C i `DECISION_REQUIRED`. Osobny test pilnuje, że lista starych nazw **zostaje**
w kodzie migracji.

Komunikat końcowy skanu i opis CLI: `SZYBKI PRZEGLAD SEGMENTACJI` → `SZYBKI SKAN
PRODUKCYJNY`. Nowy test przechwytuje wygenerowane wyjście zamiast skanować źródło. Nazwa
diagnostyczna zostaje wyłącznie w `segmentation_compare.py`.

## r581 — 2026-08-16 — realny błąd zapisu zmigrowanych rekordów
Test behawioralny z r580 zrobił dokładnie to, do czego służy: ujawnił wyjątek wykonania,
którego asercja tekstowa nigdy by nie złapała.

`ValueError: dict contains fields not in fieldnames: 'a', 'b025', 'b050', ...` —
`_load_rows()` uzupełniał brakujące pola, ale zostawiał w rekordzie **dawne kolumny
diagnostyczne**, a `DictWriter` nowego schematu ich nie zna.

1. Rekord budowany **od nowa** wyłącznie z `REQUIRED_ROW_FIELDS` — stare pola nie
   przechodzą dalej.
2. Przebudowany rekord **zastępuje** stary wpis tego samego symbolu i interwału, zamiast
   go duplikować.
3. `OPEN_DASHBOARD` sterowane zmienną `V3_NO_BROWSER`; testy ustawiają ją na starcie, więc
   nie otwierają przeglądarki na katalogu tymczasowym (stąd `ERR_FILE_NOT_FOUND` po
   sprzątnięciu katalogu).
4. `SZYBKI PRZEGLAD SEGMENTACJI` → `SZYBKI SKAN PRODUKCYJNY` w skrypcie produkcyjnym.

2 nowe testy: normalizacja odcina wszystkie osiem dawnych kolumn i zostawia dokładnie
siedem pól schematu; testy nie otwierają przeglądarki. Test behawioralny sprawdza dodatkowo
brak duplikatu symbolu i brak starych pól po migracji.

## r580 — 2026-08-16 — dwa ostatnie testy przepisane na zachowanie
Zero zmian w kodzie produkcyjnym. Oba testy sprawdzały zapis implementacji zamiast wyniku.

`test_stale_row_is_not_skipped_on_resume` wymagał dosłownego `elif sym in stale_rows:`.
Uruchamia teraz `run(resume=True)` w katalogu tymczasowym z podmienionym pobieraniem
(bez sieci i bez Massive): RBLX ma stary rekord r573, INTU komplet poprawnych payloadów.
Sprawdza, że RBLX trafił do przebudowy, INTU został pominięty, payload RBLX ma aktualny
schemat i listę dolin, a po przebiegu nie ma już wierszy sprzed migracji.

`test_migration_needs_no_manual_cleanup` wycinał źródło między nazwami funkcji i wywracał
się na `ValueError: substring not found` po zmianie kolejności definicji. Teraz zapisuje
stary `results.csv`, **nie rusza go ręcznie**, uruchamia migrację, potwierdza brak wyjątku,
automatyczną przebudowę i plik w nowym schemacie, a drugie uruchomienie potwierdza legalny
`SKIP_ALREADY_DONE`.

Pomocnicze `_fake_payloads()` i `_run_with_stub()` podmieniają `process_symbol`
i `load_universe_rows`, więc testy nie dotykają sieci ani bazy.

## r579 — 2026-08-16 — migracja starego results.csv
`_load_rows()` czytał `r[k]` bezwarunkowo, więc `results.csv` z r573 — bez kolumn
`local_valleys`, `top_date`, `top_prominence` i `macd_std` — wywracał cały przebieg
z `KeyError`.

Brakujące pola dostają jawne wartości domyślne (`REQUIRED_ROW_FIELDS`), a symbol trafia
do zbioru STALE. Brak nowego pola **nie** jest dowodem aktualności: wiersz sprzed migracji
ma pierwszeństwo przed `done_before`, więc symbol jest przebudowywany, nie pomijany przez
`SKIP_ALREADY_DONE`. Log podaje symbol i przyczynę:
`REBUILD_STALE_SCHEMA  RBLX  brakuje kolumn: local_valleys, top_date, ...`.

Nieczytelny `results.csv` nie przerywa batcha — tabela liczy się od nowa z komunikatem.
Migracja nie wymaga kasowania danych ani `--fresh`. Po przebudowie raport, payloady
i dashboard używają wyłącznie schematu r579.

`URUCHOM-SKAN-MACD-V3-FAST.bat`: „SZYBKA DIAGNOSTYKA" → **„SZYBKI SKAN PRODUKCYJNY"** —
diagnostyka A/B/C jest osobnym narzędziem.

7 nowych testów: zgłoszony przypadek (stary CSV z r573 bez wyjątku), brak **każdej**
z czterech nowych kolumn osobno, stale nie daje SKIP, uszkodzony plik nie przerywa batcha,
brak pliku nie jest błędem, raport tylko w nowym schemacie, migracja bez ręcznego
sprzątania.

## r578 — 2026-08-16 — pięć testów przepisanych na zachowanie
Cztery z pięciu błędów brały się z testów sprawdzających dosłowne fragmenty JavaScriptu
zamiast wyniku. Zero zmian w algorytmie B 0,25, kolorach momentum i zamianie palet.

1. `test_variant_switch_hides_only_segmentation_markers` — szukał tekstu w `_INIT_JS`,
   podczas gdy przeniósł się on do `_SELECTOR` jako `<option>`. Sprawdza teraz, że warstwa
   segmentacji nie dotyka `macd_cross_signal_up`, a marker to jeden punkt z payloadu.
2. `test_production_dashboard_has_no_not_approved_banner` — wymuszał dawną strukturę
   `segwarn`, który wypełnia się dynamicznie. Dodany osobny statyczny element
   `id="segrule"`: „segmentacja: wariant B · 0,25 × std(MACD)".
3. `test_production_selector_has_no_diagnostic_variants` — `0,50` występowało wyłącznie
   w komentarzu opisującym, czego w produkcji nie ma. Wzmianka usunięta, żeby produkcyjny
   kod nie zawierał nawet śladu po B 0,50.
4. `test_variant_switch_cannot_restore_markers_on_1h` i
5. `test_1h_tooltip_has_no_excursion_line` — obie sprawdzały literalny zapis kodu.
   Sprawdzają teraz wynik: payload 1H ma `top_excursion: None` i pustą listę dolin,
   a renderer czyta wyłącznie z payloadu, więc brak źródła oznacza brak markera i brak
   linii w tooltipie niezależnie od stanu w `localStorage` czy URL.

## r577 — 2026-08-16 — domknięte wszystkie stałe JS w szablonie
Ten sam błąd wystąpił trzy razy z rzędu, bo naprawiałem po jednym zamknięciu zamiast
sprawdzić wszystkie naraz. Edycje z r574 wycinały stare bloki razem z ich zamykającym
`"""`, przez co kolejne stałe „zjadały" się nawzajem: `_MARKER_JS` pochłaniał `_TIP_JS`,
potem `_TIP_JS` pochłaniał `_INIT_JS`, a na końcu `_INIT_JS` sięgał do `render_review`.
Kod JavaScript trafiał do parsera Pythona — stąd `IndentationError`, a po pierwszej
poprawce `SyntaxError` na komentarzu `//`.

Fragment z linii 70 należy do generowanego JavaScriptu i jest teraz wewnątrz `_INIT_JS`,
nie w kodzie Pythona.

Wszystkie cztery stałe (`_SELECTOR`, `_MARKER_JS`, `_TIP_JS`, `_INIT_JS`) domknięte
i zweryfikowane symulacją tokenizera, która śledzi stan łańcucha linia po linii i wykrywa
JavaScript poza łańcuchem (`//`, `(function(){`, `const/let/var`). Ta sama kontrola
przeszła na wszystkich ośmiu plikach edytowanych w r574–r576.

Zero zmian w logice, algorytmie B 0,25 i kolorach momentum.

## r576 — 2026-08-16 — naprawa COMPILE FAIL
`_MARKER_JS` w `macd_segmentation_template.py` nie miał zamykającego `"""` — edycja
z r574 ucięła je razem ze starym blokiem. Wszystko od linii 49 stawało się kodem Pythona,
stąd `IndentationError` w linii 52.

Domknięte. Sprawdzony cały plik i pozostałe pliki edytowane w r574–r575: parzystość
potrójnych cudzysłowów, domknięcie każdej stałej `_SELECTOR` / `_MARKER_JS` / `_TIP_JS` /
`_INIT_JS`, brak tabulatorów, obecność `render_review` i wszystkich czterech stałych.

Zero zmian w logice, algorytmie B 0,25 i kolorach momentum.

## r575 — 2026-08-16 — fałszywy status COMPLETE przy niekompletnym dashboardzie
Realny błąd, nie tylko brak testu. Status brał się z przebiegu pętli, a nie z zawartości
partial storage, więc przebieg kończący się czterema spółkami w dashboardzie i tak
raportował `COMPLETE` oraz kod wyjścia 0.

`final_status()` liczy komplet z plików na dysku: brakujące symbole dają
`PARTIAL_COMPLETE` z ich listą, a `main()` zwraca kod różny od zera. Podsumowanie pokazuje
`w dashboardzie: X/Y symboli` i wypisuje, czego brakuje.

3 nowe testy domykające punkt 2 (4 spółki nie dają COMPLETE ani 6/6, kod wyjścia ≠ 0,
status liczony z payloadów a nie ze stanu pętli). Pozostałe sześć punktów było już pokryte
w r574 — łącznie 18 testów regresyjnych na siedem wymagań.

## r574 — 2026-08-16 — jedno największe wychylenie, wznowienie, rozdział trybów
Detektor B 0,25 i jego próg bez zmian. Kolory momentum bez zmian.

**Nowa semantyka.** „Historyczne wychylenia" przestały oznaczać wszystkie lokalne minima:
- `local_valleys` — wszystkie kandydaty B 0,25, w payloadzie, zasilają profil, średnią,
  medianę i ranking; **niewidoczne** na wykresie produkcyjnym,
- `top_excursion` — dokładnie jeden punkt na symbol, o największej prominencji (remis →
  nowszy), wyznaczany na **pełnej historii po rozgrzewce**, nie na widocznych 250 barach.
  Zoom nie zmienia wyboru. Punkt poza widokiem nie jest zastępowany innym dołkiem —
  panel pokazuje komunikat z datą i wartościami.

**Markery domyślnie ukryte.** Wersjonowany klucz `v3seg.markers.v2` z migracją kasującą
stare ustawienia, więc nowa wersja startuje bez markerów niezależnie od tego, co
użytkownik miał zapisane. Selektor ma dwie opcje: „bez markerow segmentacji" i
„Najwieksze historyczne wychylenie MACD · B 0,25". Warianty A, B 0,50 i C nie istnieją
w produkcyjnym UI — nie da się ich przywrócić przez kontrolkę, storage ani query string.
Kropki przecięć MACD/Signal pozostają niezależne.

**Tooltip** jednego markera: jeden nagłówek, data, MACD minimum, `std(MACD)`, próg,
lewe i prawe odbicie, prominencja, wynik porównania z progiem, „1 z N lokalnych dolin".
Nowe czyste funkcje `prominence_details()` i `largest_excursion()` w detektorze —
liczą składowe, nie zmieniają decyzji.

**Wznowienie.** Sam znacznik `done` nie powoduje już `SKIP` — to była przyczyna znikania
RBLX i AAOI z dashboardu. `validate_done()` wymaga kompletu czytelnych payloadów 1D i 1H,
zgodności symbolu, interwału, schematu (`FAST_SEG_PAYLOAD_2`) i konfiguracji segmentacji,
obecności wychyleń w 1D i ich braku w 1H. Niespełnienie daje precyzyjny powód
(`STALE_DONE_MISSING_PAYLOAD`, `_CORRUPT_PAYLOAD`, `_SCHEMA_MISMATCH`,
`_SEGMENTATION_CHANGED`, `_1H_HAS_EXCURSIONS`) i przeliczenie. Nowy
`--force-symbol RBLX AAOI` — bez ręcznego kasowania plików.

**Rozdział trybów.** Raport produkcyjny: tylko B 0,25, kolumny „lokalnych dolin",
„największe wychylenie", „prominencja", „std(MACD)"; 1H ma status „historyczne wychylenia
wylaczone" zamiast sztucznych zer; zero `DECISION_REQUIRED`. Diagnostyka A/B/C żyje
wyłącznie w `wyniki-v3-2/porownanie-wariantow`.

**Palety RSI i Stochastic zamienione** (istniejące tokeny, żadnych nowych kolorów):
RSI ← `#4dd0e1` (dawny %K), średnia RSI ← `#ff8a65` (dawny %D), %K ← `#b39ddb` (dawny
RSI), %D ← `rgba(201,162,39,.7)` (dawna średnia). Zamiana objęła linie, legendy, etykiety
prawej osi i tooltipy. Poziomy 30/70 i 20/80, wypełnienia i geometria bez zmian.

## r573 — 2026-08-16 — krucha asercja w teście narzędzia produkcyjnego
Wyłącznie `v3/tests/test_fast_segmentation.py`. Zero zmian w kodzie produkcyjnym,
algorytmie i pozostałych testach.

Asercja `out[key]["idx"] != DET_candidates_050(series)` była krucha z natury: na wielu
seriach progi 0,25 i 0,50 dają identyczny zbiór dolin, więc żądanie różnicy nie opisywało
żadnego kontraktu. Usunięta wraz z pomocniczą funkcją `DET_candidates_050`.

Test sprawdza teraz to, co faktycznie jest kontraktem: `_variants()` zwraca dokładnie
jeden klucz równy `VARIANT_B@0.25`, `APPROVED_LEVEL == 0.25`,
`APPROVED_MIN_BARS_APART == 0`, wynik pochodzi z wywołania detektora z tymi parametrami,
a żaden wariant z `DIAGNOSTIC_ONLY_VARIANTS` nie pojawia się w ścieżce produkcyjnej.

## r572 — 2026-08-16 — skrypty .bat zgodne z decyzją B 0,25
Zero zmian w logice produkcyjnej i w algorytmie segmentacji.

`URUCHOM-SKAN-MACD-V3-FAST.bat` miał smoke test `assert not m.SEGMENTATION_APPROVED`
z czasów przed decyzją — po zatwierdzeniu B 0,25 kończył dwuklik komunikatem
„FAIL - smoke testy nie przeszly". Teraz wymaga pełnego kontraktu: `SEGMENTATION_APPROVED
is True`, `APPROVED_VARIANT == VARIANT_B`, `APPROVED_LEVEL == 0.25`,
`APPROVED_MIN_BARS_APART == 0`, `APPROVED_TIMEFRAME == "1D"` — każdy warunek z własnym
komunikatem błędu.

`URUCHOM-SKAN-MACD-V3.bat` sprawdzał tylko samą flagę; preflight weryfikuje teraz
wszystkie pięć warunków. `POROWNAJ-WARIANTY-SEGMENTACJI.bat` nie zakłada żadnego stanu —
diagnostyka A/B/C działa niezależnie od decyzji produkcyjnej.

Trzy testy pilnujące, żeby to nie zgniło ponownie: brak `assert not
m.SEGMENTATION_APPROVED`, „NIEZATWIERDZONA" i „tryb przegladu" w jakimkolwiek `.bat`;
obecność wszystkich pięciu warunków w skryptach produkcyjnych; brak założeń o stanie
w skrypcie diagnostycznym. Zaktualizowany `v3/macd_excursions/README.md`.

## r571 — 2026-08-16 — naprawa 2 FAIL z r570
Zero zmian w algorytmie segmentacji. Reguła B 0,25 bez zmian.

**FAIL 1** `test_approved_candidates_use_b_025` — **błąd fixture'a, nie implementacji.**
Próg wariantu B jest z definicji relatywny do odchylenia tej samej serii. Fixture `MICRO`
zawierał wyłącznie mikroszum, więc jego własne odchylenie wynosiło 0,00748, a próg
0,00187 — dołek o prominencji 0,02 był wobec tej skali 10× większy od progu i słusznie
przechodził. Dodany `MICRO_IN_CONTEXT`: ten sam mikroszum osadzony w realnych ruchach
(odchylenie 3,9067, próg 0,9767) — dołek 0,02 wypada poniżej progu i jest odrzucany.

**FAIL 2** `test_fast_tool_uses_only_approved_variant` — **zbyt szerokie sprawdzanie
tekstowe.** Test zabraniał literału `0.50` w całym pliku i wywracał się na komentarzu
opisującym tryb diagnostyczny (linia 98) oraz na martwej stałej `FAST_B_LEVELS` (linia 47,
nieużywanej od r570). Stała usunięta; test sprawdza teraz zachowanie: `_variants()` zwraca
dokładnie jeden klucz, równy zatwierdzonemu wariantowi, i jego wynik różni się od B 0,50.
Brak banera diagnostycznego wydzielony do osobnego testu.

## r570 — 2026-08-16 — DECYZJA WŁAŚCICIELA: segmentacja B 0,25 wdrożona produkcyjnie

**Zatwierdzony wariant**: B — prominencja topograficzna, próg `0,25 × std(MACD)` dla
danego instrumentu i interwału, **bez minimalnej odległości** w barach, historyczne
wychylenia **wyłącznie na 1D**.

Stałe w `v3/macd_excursions/__init__.py`: `SEGMENTATION_APPROVED = True`,
`APPROVED_VARIANT = VARIANT_B`, `APPROVED_LEVEL = 0.25`, `APPROVED_MIN_BARS_APART = 0`,
`APPROVED_TIMEFRAME = "1D"`, plus `approved_candidates()` jako jedyne wejście produkcyjne.

Finalny skan nie jest już blokowany. `build_profile` domyślnie bierze stan produkcyjny
z modułu: profil liczony wariantem B dostaje status `OK`, profil z wariantu
diagnostycznego nadal `SEGMENTATION_NOT_APPROVED`. Zabezpieczenie przed uruchomieniem
bez zatwierdzenia zostaje — wywołane z `False` nadal zwraca `REQUIRES_OWNER_DECISION`.

Skan produkcyjny (`fast_segmentation.py`) liczy wyłącznie wariant zatwierdzony. **A,
B 0,50 i C nie zniknęły** — żyją w trybie diagnostycznym `segmentation_compare.py`
i są tam nadal w pełni dostępne.

Dashboard: usunięte „DIAGNOSTIC ONLY — NOT APPROVED" z paska, markerów i tooltipa;
w ich miejsce opis zatwierdzonej reguły. Tooltip pokazuje „Historyczne wychylenie MACD"
bez słowa „kandydat".

Opcja w selektorze przemianowana na **„(bez markerow segmentacji)"** — ukrywa wyłącznie
rombiki wychyleń. Zielone i czerwone kropki przecięć MACD/Signal pozostają widoczne, bo
to osobny, zamknięty element kontraktu (locked events); rysuje je główny renderer, nie
warstwa segmentacji. Zachowanie opisane w kodzie i pokryte testem.

Kolory momentum z r568 nietknięte.

## r569 — 2026-08-16 — porównanie wariantów segmentacji
Nowe `v3/tools/segmentation_compare.py` + `POROWNAJ-WARIANTY-SEGMENTACJI.bat`.
**Żaden wariant nie jest ustawiany jako domyślny** — `SEGMENTATION_APPROVED` nadal `False`.

Liczy A / B 0,25 / B 0,50 / C na identycznych danych, każdy w dwóch odmianach (bez
ograniczenia i z minimalną odległością w barach), osobno dla 1D i 1H, dla RBLX, AAOI
i INTU. Jedno pobranie na spółkę; warianty liczone w pamięci, więc przełączanie na
dashboardzie nie pobiera i nie przelicza danych.

Raport `porownanie-wariantow.md` odpowiada na wszystkie siedem punktów: algorytmy
i warunki matematyczne, znaczenie progów (mnożniki własnego odchylenia MACD, nie wartości
bezwzględne), charakter progu (normalizowany, nie procentowy względem ceny), brak warunku
zera i wygładzania w każdym wariancie, liczby wykryć, przykłady sygnałów usuniętych
i zachowanych względem A, wyniki rozdzielone na 1D i 1H.

Minimalna odległość: propozycja **5 barów dla 1D** (tydzień handlowy) i **7 dla 1H**
(jedna pełna sesja) — celowo różne, bo bar 1D to cała sesja, a bar 1H jedna z siedmiu jej
części. Raport pokazuje osobno liczby bez ograniczenia, z ograniczeniem i ile minimów
zostało połączonych lub odrzuconych. Scalanie działa dziś wyłącznie w wariancie B; dla
A i C kolumny są równe i raport to jawnie odnotowuje.

Dashboard porównawczy pokazuje warianty na obu interwałach — to osobny artefakt
diagnostyczny; reguła „wychylenia tylko na 1D" z r567 dotyczy dashboardu przeglądowego
i pozostaje niezmieniona. 9 nowych testów.

## r568 — 2026-08-16 — histogram momentum: czterostanowe kolorowanie
Wyłącznie klasyfikacja i renderowanie koloru. Zero zmian w wartościach MACD, Signal,
histogramu, parametrach obliczeń i logice analitycznej.

Poprzednio histogram miał dwa stany (dodatni/ujemny) i to w kolorach dziedziczonych po
palecie świec, z 45% krycia. Teraz cztery stany przy pełnym kryciu:

| Warunek | Token | HEX |
|---|---|---|
| `hist[i] >= 0 && hist[i] > hist[i-1]` | `MOMENTUM_POSITIVE_RISING` | `#00BCD4` |
| `hist[i] >= 0 && hist[i] < hist[i-1]` | `MOMENTUM_POSITIVE_FALLING` | `#2962FF` |
| `hist[i] < 0 && hist[i] < hist[i-1]` | `MOMENTUM_NEGATIVE_FALLING` | `#F23645` |
| `hist[i] < 0 && hist[i] > hist[i-1]` | `MOMENTUM_NEGATIVE_RISING` | `#880E4F` |

Przypadki graniczne: wartość identyczna z poprzednią zachowuje kolor poprzedniego słupka;
brak poprzedniej wartości daje `#2962FF` dla `>= 0` i `#880E4F` dla `< 0`. Kolor każdego
słupka jest wyliczany i zapisywany niezależnie (`momentumColors` buduje tablicę raz),
więc pojawienie się nowego słupka nie przemalowuje historii.

Rozdział tokenów: momentum używa wyłącznie tych czterech kolorów, wolumen zachowuje
niezmienioną paletę zielono-czerwoną. Żadnej przezroczystości, rozjaśniania, mieszania
ani dziedziczenia z koloru świec. Jedna funkcja obsługuje 1D i 1H identycznie.

11 nowych testów: cztery kombinacje znaku i kierunku, przejścia `#00BCD4 → #2962FF`
i `#F23645 → #880E4F`, przejścia przez zero w obie strony, wartości identyczne, pierwszy
słupek, brak przemalowania historii, niezależność od świec i wolumenu, zgodność 1D/1H.

## r567 — 2026-08-16 — historyczne wychylenia MACD wyłącznie na 1D
Zero zmian w obliczeniach MACD i w logice analitycznej 1D.

**Źródło błędu: payload, nie renderer.** Pętla po interwałach przypisywała
`payload["segmentation"]` niezależnie od interwału, więc 1H dostawał kandydatów tak samo
jak 1D — renderer tylko wiernie je rysował.

**Fix w warstwie danych** (`fast_segmentation.py`, `macd_segmentation_review.py`): stała
`SEGMENTATION_TIMEFRAME = "1D"`; dla pozostałych interwałów warianty nie są w ogóle
liczone, a payload dostaje pustą `segmentation`, pustą `segmentation_overlap` i status
„NIE DOTYCZY — wychylenia tylko na 1D". Renderer nie ma czego narysować, więc znikają
zarówno romby, jak i linia tooltipa.

**Zabezpieczenie w UI**: selektor metody chowa się przy pustej segmentacji i nie ustawia
klucza — przełączanie A/B/C na 1H nie może przywrócić markerów.

4 nowe testy: blokada w warstwie danych, payload 1D ma kandydatów a 1H nie, selektor nie
przywraca markerów, tooltip 1H bez linii wychylenia.

## r566 — 2026-08-16 — dashboard rośnie z każdą gotową spółką
Wyłącznie mechanizm zapisu partial. Zero zmian w MACD, wariantach A/B/C, parametrach,
danych canonical i rendererze.

**ROOT CAUSE**: dashboard był składany z tego, co akurat siedziało w pamięci procesu.
Przy przerwaniu, restarcie albo wznowieniu (`resume` pomija ukończone spółki, więc nie
trafiają one do `payloads`) lista w pamięci nie zawierała wcześniejszych wyników — i
`index.html` był nadpisywany węższym zestawem.

**Fix**: canonical partial storage `fast-segmentation/payloads/<SYMBOL>_<TF>.json`, zapis
atomowy z `fsync`. Dashboard budowany ZAWSZE z kompletu plików odczytanych z dysku, nigdy
ze stanu w pamięci — nawet wywołany z pustym słownikiem daje pełną listę. Uszkodzony plik
jest pomijany z komunikatem, reszta zostaje. Wiersze raportu wczytywane z `results.csv`
przy wznowieniu, więc tabela też nie gubi wcześniejszych spółek.

Log po każdej aktualizacji: ścieżka `index.html` i lista spółek w nim zawartych. Nagłówek
dashboardu pokazuje `BUILD … · HH:MM:SS · X/6 gotowe`, więc widać, czy przeglądarka ma
aktualny plik. `progress.json` zawiera `dashboard_symbols`.

Nowe `PRZEBUDUJ-DASHBOARD-SEGMENTACJI.bat` i flaga `--rebuild`: odtworzenie dashboardu
z zapisanych wyników bez pobierania i bez przeliczania — sekundy. 7 nowych testów
(dashboard rośnie RBLX → +AAOI → +INTU, budowa z dysku a nie z pamięci, oba interwały,
przetrwanie restartu, licznik postępu, uszkodzony plik).

## r565 — 2026-08-16 — szybki przegląd segmentacji (FAST MODE)
Nowe `v3/tools/fast_segmentation.py` + `URUCHOM-SKAN-MACD-V3-FAST.bat`. Zero zmian
w wariantach A/B/C, parametrach segmentacji, formułach wskaźników, polityce H/L
i kontraktach.

**Skąd przyspieszenie**: MACD liczy się z ceny zamknięcia, a ta pochodzi z natywnego bara
dziennego — jednego zapytania. Bary 30m są potrzebne wyłącznie do analitycznego H/L świec
i do 1H, czyli do tego, co widać w oknie. Pełny przebieg pobierał 30m za ~2,7 roku
(~17 zapytań), choć segmentacja nie korzysta z nich w ogóle. FAST pobiera 30m tylko pod
okno wyświetlania (250 sesji ≈ 1 rok, ~6 kawałków) i dzieli je między 1D i 1H — razem
~7 zapytań na spółkę zamiast ~17. Przy pauzie 13 s na zapytanie: ~1,5 min na spółkę,
~10 min na sześć.

Zestaw: RBLX, AAOI, INTU, NVDA, PLTR, ADTN. Dashboard po pierwszej spółce, checkpoint
i atomowy zapis po każdej (`index.html`, `progress.json`, `results.csv`, `report.md`),
resume po `diag_version`, twardy limit 55 min z `PARTIAL_COMPLETE`, ostrzeżenie i
redukcja zestawu gdy szacowany czas przekracza budżet. B w dashboardzie: 0,25 i 0,50
(pełna siatka zostaje w backendzie). Log etapów z czasem i liczbą zapytań; podsumowanie
z udziałem czasu sieci i najwolniejszą spółką.

**Kompromis, świadomy**: okno 250 barów zamiast 120 daje więcej materiału do oceny dolin,
ale historia analitycznego H/L sięga roku wstecz — starsze sesje mają H/L niedostępne
(fail closed, bez zmiany polityki). Nie dotyczy to MACD, który liczy się z pełnej
historii dziennej.

## r564 — 2026-08-16 — diagnostyka wykonania: podwójne pobieranie 30m
Wyłącznie warstwa wykonania. Zero zmian w MACD, wariantach A/B/C, parametrach segmentacji,
canonical data i testach analitycznych.

**ROOT CAUSE**: `build_payload` liczył każdy interwał osobno, a ścieżka 1H wołała
`fetch_canonical_1h(symbol, None, ...)` — czyli pobierała te same ~17 kawałków 30m po raz
drugi. Razem ~20 zapytań na spółkę; przy limicie Massive to kilka minut ciszy, bo
`build_payload` nie logował żadnego etapu. Proces nie był zawieszony — czekał na sieć.

**Fix**: `build_payloads_for_symbol` pobiera 30m RAZ i dzieli je między 1D i 1H
(~17 zapytań zamiast ~20, zero powtórzeń). Dashboard zapisywany raz na spółkę, nie po
każdym interwale. Pełny log etapów z czasem: START/END SYMBOL, DATA LOAD (z liczbą wierszy
i zakresem dat), MACD, VARIANTS, DASHBOARD WRITE. Limit 420 s na spółkę — po przekroczeniu
`TIMEOUT` z etapem i czasem, i przejście dalej. Wyjątki wypisywane z pełnym traceback,
nie ukrywane.

## r563 — 2026-08-16 — test regresyjny na importowalność config.py
`test_config_is_importable_and_compiles`: `py_compile` + import + kontrola, że wartości
stałych są krótkimi jednoliniowymi napisami (≤60 znaków). Wcześniej awarię z r561 wykrywał
tylko pośrednio inny test, który przypadkiem importował `config`.

## r562 — 2026-08-16 — naprawa 7 FAIL
Jedna realna usterka kodu, sześć nieaktualnych asercji w testach. Zero zmian w logice.

**KRYTYCZNE — `config.py` nie dawał się zaimportować.** Edycja z r561 podmieniła samą linię
`VERSION`, ale poprzednia wartość była wieloliniowym opisem zmian — jego ogon (od
„Przebudowany dashboard…") został doklejony za nową stałą `LEGACY_V2_READ_ONLY_LABEL`,
dając `SyntaxError: invalid decimal literal` w linii 23. Usunięty. To dokładnie ten typ
awarii, przed którym miało chronić skrócenie `VERSION` w r552 — resztka pochodziła jeszcze
z r549.

**Nieaktualne testy wykresu** (sprawdzały stan sprzed r557–r560, nie realny kontrakt):
`guide(P.rsi,70,0,100` → `OSC_LO,OSC_HI`; `h:osc` → `h:rsi`/`h:stoch` (od r559 równa się
kanał, nie pudełko); zakaz `S.macd[i-1]` (od r557 służy interpolacji pozycji markera, nie
detekcji przecięcia — detekcja nadal wyłącznie z locked eventów); `Przeciecie MACD / Signal`
→ `PRZECIECIE MACD / SIGNAL`.

**Dwa testy wariantu B miały błędne oczekiwania, nie kod.** Prominencja w wariancie B jest
**relatywna do własnej skali MACD** instrumentu, więc seria `5.00 4.99 4.98 4.99 5.00`
wzięta osobno ma własną skalę ~0,008 i jej dołek nie jest wobec siebie szumem — szumem
staje się dopiero w kontekście większych ruchów. Test przepisany na mikroszum osadzony
w serii z realnymi wychyleniami (tam B go odrzuca na wszystkich poziomach ≥0,25).
Drugi test oczekiwał 2 dolin w `[0,−5,0,5,2,5,0,−6,0]`, a poprawny wynik to 3: dolina
o wartości `+2` leży powyżej zera i zgodnie z §15 NIE może być pomijana.

## r561 — 2026-08-16 — V3 RESET + V3.2A infrastruktura i diagnostyka segmentacji

### V3 RESET (tryb przejściowy wg decyzji właściciela)
- `config.LEGACY_V2_DECISIONS_ACTIVE = False` — Legacy NON STOP wychodzi z `run()` przed
  jakąkolwiek logiką decyzyjną: nie otwiera pozycji, nie tworzy zleceń, nie generuje
  rekomendacji. Dane użytkownika nietknięte, żadne zlecenie oczekujące nie jest anulowane.
- `config.LEGACY_V2_CYCLES_READ_ONLY = True` + etykieta „LEGACY V2 — TYLKO ODCZYT".
  Zakładka Cykle zostaje widoczna do pierwszego poprawnego skanu V3.2A.
- Kod Legacy fizycznie w repo, bez refaktoru — odłączone tylko decyzje.

### Canonical 30m / 2H / 4H — `v3/market_data/us_multi_tf.py`
30m jako pełnoprawny interwał (tylko `[open, close)`, bez PRE i AH). 2H i 4H budowane
deterministycznie z 30m, kotwiczone na **faktycznym otwarciu sesji NYSE**, nie na pełnych
godzinach UTC. Ostatni kubełek bywa krótszy (6,5h nie dzieli się przez 2h ani 4h) i to jest
poprawny bar. Sesje skrócone dają automatycznie mniej kubełków. Niekompletne pokrycie =
kubełek pominięty (fail closed), nigdy doszacowany. Native 2H/4H dostawcy nieużywane.
Kanoniczne 1H nietknięte.

### Moduł `v3/macd_excursions/`
`schema.py` (`V3_MACD_EXCURSION_PROFILE_1`, statusy fail-closed, `ScanRun`),
`detector.py` (trzy warianty diagnostyczne), `profile.py` (średnia i mediana **równolegle**,
X z N, rekord, etykieta historii), `repository.py` (tabele `v3_*`, checkpoint, resume —
klucz unieważniany zmianą segmentacji), `scanner.py` (preflight blokujący finalny skan,
błąd jednej spółki nie zatrzymuje batcha), `README.md`.

### Segmentacja — DIAGNOSTIC ONLY, NOT APPROVED
Trzy rodziny metod do porównania wizualnego, żadna nierekomendowana:
**A** surowe punkty zwrotne (bez progu, bez warunku zera) · **B** prominencja w mnożnikach
własnego odchylenia MACD spółki, siatka 0,10 / 0,25 / 0,50 / 1,00 · **C** jedno minimum
w odcinku między locked przecięciami MACD/Signal (bez nowych liczb).
Wspólnie: surowy MACD, zero jako **nie**-warunek, brak wygładzania i danych cenowych.

### Dashboard diagnostyczny
`v3/tools/macd_segmentation_review.py` + `macd_segmentation_template.py` — **ten sam**
renderer V3.1B, wzbogacony o przełącznik metody i markery kandydatów (pusty rombik, celowo
inny od zatwierdzonych kropek przecięć). Raport `macd-segmentation-candidate-counts.md`:
liczby kandydatów per metoda i przecięcie zbiorów, bez oceny jakości.
`URUCHOM-SKAN-MACD-V3.bat` — preflight, a przy niezatwierdzonej segmentacji
`STOPPED: MACD_EXCURSION_SEGMENTATION REQUIRES_OWNER_DECISION` zamiast finalnego skanu.

### Testy
`test_multi_tf.py` (20), `test_macd_excursions.py` (28), `test_legacy_isolation.py` (8).

## r560 — 2026-08-15 — skala panelu MACD
Wyłącznie renderer. Zero zmian w formule MACD, wartościach i eventach.
- **Problem**: przy dużym wychyleniu ujemnym (np. RBLX 1H) autoscale dopasowywał panel
  niemal wyłącznie do dolnej części zakresu — dodatnie słupki histogramu i wychylenia
  MACD/Signal nad zerem były spłaszczone do cienkiego pasa.
- **Fix**: nowa funkcja `macdScale` — autoscale po widocznych barach, wspólna oś Y dla
  histogramu, MACD i Signal, plus zapas 10% od ekstremów. Każda strona zera ma
  gwarantowane minimum 28% wysokości panelu (`MIN_SIDE_SHARE`); jeśli dane dają mniej,
  brakująca strona dostaje headroom.
- **Bez wymuszania 50/50**: asymetria danych zostaje. Zakres −8…+1 nadal ma dominującą
  część ujemną (~66%), ale dodatnia dostaje czytelne ~34% zamiast ~11%. Zakres −4…+4
  pozostaje naturalnie symetryczny.
- Wysokość słupka pozostaje liniową reprezentacją wartości w bieżącej skali — żadnego
  sztywnego limitu pikseli. Żadna seria nie dotyka krawędzi panelu. Pozycja linii zera
  wynika ze skali, nie jest przypięta do stałej wysokości.
- Kropki przecięć bez zmian (kolory, rozmiar, interpolowany punkt przecięcia) — automatycznie
  korzystają z nowej skali.
- 7 nowych testów: stałe i podłączenie skali, trzy przypadki (dominacja ujemna, dodatnia,
  zrównoważony), brak wymuszania 50/50, brak dotykania krawędzi, tylko widoczny zakres.

## r559 — 2026-08-15 — wysokość RSI wynika z kanału, nie z pudełka
Wyłącznie geometria renderera RSI. Zero zmian w danych, wskaźnikach i pozostałych panelach.
- **Poprzednie kryterium było błędne.** Równa wysokość paneli przy skali 0–100 zawsze daje
  mniejszy kanał RSI: 30–70 to 40% panelu, a Stochastic 20–80 aż 60%.
- **Nowy kontrakt**: panel RSI jest 1,5× wyższy od Stochastic, więc `0,40 × 1,5 = 0,60` —
  kanał 30–70 ma tyle samo pikseli co 20–80, a nadwyżka wysokości daje RSI realne miejsce
  nad 70 i pod 30 na wychylenia. `CHANNEL_RATIO = 1,00`.
- Skala RSI pozostaje 0–100, poziomy 30/50/70, linia, średnia, wypełnienia poza kanałem
  i etykieta wartości — bez zmian matematycznych. Żadnego zawężania domeny do 20–80.
- Reszta z zaokrągleń nadal ląduje w panelu ceny (`price = inner − macd − ad − rsi − stoch`).
- Stochastic, MACD, panel ceny, EMA, wolumen, A/D, tooltip: nietknięte.

## r558 — 2026-08-15 — fix wysokości panelu RSI
Wyłącznie geometria renderera. Zero zmian w danych, wskaźnikach i pozostałych panelach.
- **Root cause**: panele RSI i Stochastic miały już równą wysokość, ale RSI rysował się
  w poszerzonej skali (−6…106) wprowadzonej w r557 dla „oddechu". Przy tej samej liczbie
  pikseli kanał 30/70 zajmował więc ~36% wysokości, a 20/80 na Stochastic pełne 60% —
  RSI wyglądał na pionowo ściśnięty. Problem nie leżał w wysokości kontenera.
- **Fix**: jedna skala `OSC_LO=0`, `OSC_HI=100` dla obu paneli, na pełnej wysokości
  obszaru rysowania. Żaden z nich nie ma dodatkowych marginesów wewnętrznych, nagłówek
  legendy i etykiety osi są w obu identyczne, więc obszary wykresu są równe co do piksela.
- Reszta z zaokrągleń wysokości ląduje teraz w panelu ceny (`price = inner − macd − ad
  − 2·osc`), a nie w oscylatorach — `osc` jest tą samą liczbą dla RSI i Stochastic.
- Stochastic, MACD, panel ceny i A/D nietknięte. RSI zachowuje zakres 0–100, poziomy
  30/50/70, linię, średnią, wypełnienia poza kanałem i etykietę bieżącej wartości.

## r557 — 2026-08-15 — V3.1B-UI ostatnia korekta ergonomii
Wyłącznie renderer. Mechanizm zapisu po każdej spółce i auto-otwarcia bez zmian.
- **RSI dokładnie równy Stochastic**: oba panele biorą wysokość z jednej wartości `osc`.
- **Oddech w panelu RSI**: skala rysowania od −6 do 106, więc wypełnienia przy 70 i 30 nie
  kleją się do krawędzi. Wartości RSI, poziomy i logika wypełnień bez zmian.
- **Kropki MACD większe (3.6 z 3.0, +20%) i o wyższym kontraście** — czysta zieleń
  `#00c853` w górę, czysta czerwień `#ff1744` w dół. Bez glow i halo.
- **Kropka siada w geometrycznym punkcie przecięcia**: renderer interpoluje odcinki
  MACD i Signal między t−1 i t (`t = d0/(d0−d1)`) i rysuje marker w tym miejscu. To
  wyłącznie korekta wizualna — timestamp zdarzenia, dane i kontrakty bez zmian.
  Interpolacja uruchamia się TYLKO gdy istnieje locked event; samo matematyczne
  przecięcie bez eventu nie tworzy kropki.
- **Informacja o przecięciu w tooltipie w kolorze markera** (zielona lub czerwona,
  wyróżniona, na końcu), reszta tooltipa neutralna. Nadal bez słów kup/sprzedaj.
- **Czytelniejszy panel A/D**: bardzo subtelne neutralne tło, 3 delikatne poziomy siatki
  z autoscale (bez hardkodowanych wartości), etykieta bieżącej wartości bez zmian.
  Żadnego kanału analitycznego — brak górnej/dolnej wstęgi, koperty i odchylenia
  standardowego; to wymagałoby osobnej decyzji.
- 6 nowych testów (oddech RSI, rozmiar i kontrast kropek, interpolacja tylko przy
  evencie, kolor linii w tooltipie, siatka A/D bez kanału).

## r556 — 2026-08-15 — V3.1B-UI zamknięcie wyglądu
Wyłącznie warstwa wizualna. Mechanizm zapisu po każdej spółce z r555 zostaje bez zmian.
- **RSI i Stochastic mają dokładnie tę samą wysokość** (jedna wartość `osc` dla obu paneli),
  więc kanał 30/50/70 jest równie czytelny jak 20/50/80.
- **Panel A/D nieco wyższy** (~8,5%), z etykietą bieżącej wartości na prawej osi w kolorze
  serii i formatem K/M/B (formatowanie tylko w UI; dane bez zaokrągleń). Nadal wyraźnie
  niższy niż oscylatory.
- **Markery przecięcia MACD/Signal**: zielona kropka przy `macd_cross_signal_up`, czerwona
  przy `macd_cross_signal_down` — wartości brane wprost z locked eventów
  `CM_ULT_MTF_TV_V1` przekazanych w payloadzie. Renderer nie liczy przecięć od nowa i nie
  używa odwrócenia histogramu ani „prawie przecięcia". Tooltip: „Przeciecie MACD / Signal
  — kierunek: w gore / w dol", bez słów kup/sprzedaj.
- **Niebieskie markery ważnych informacji** przy dolnej krawędzi panelu ceny: renderer
  przyjmuje gotową listę `{timestamp|session_date, title, description, type}`. Brak
  payloadu = brak markerów (żadnego nowego API, fetchu ani Event Engine). 1D wiąże po
  `session_date`, 1H po timestampie; zdarzenie z samą datą trafia na pierwszy bar tej sesji
  — godzina nie jest wymyślana. Tooltip pokazuje tytuł i opis, bez oceny wpływu.
- Markery wyłącznie potwierdzają istniejące zdarzenia: nie ma ich w `V3_FEATURE_ATOMIC_1`,
  nie tworzą sygnału ani scoringu, nie zmieniają danych.
- 10 nowych testów struktury (równa wysokość RSI/Stoch, wysokość i etykieta A/D, źródło
  markerów MACD, brak markera bez eventu, puste zdarzenia, kolor i tooltip, brak wpływu na
  dane i schemat, brak wymyślonej godziny).

## r555 — 2026-08-15
Wyłącznie mechanizm zapisu — zero zmian w wykresach, danych i wskaźnikach.
- Dashboard zapisywany **po każdej spółce**, nie na końcu całego przebiegu. Gotowe wykresy
  można oglądać natychmiast; kolejne spółki doklejają się do tego samego pliku, wystarczy
  odświeżyć stronę (F5).
- Po pierwszej gotowej spółce dashboard **otwiera się automatycznie**.
- Zapis atomowy (plik `.tmp` + podmiana), więc odświeżenie w trakcie zapisu nigdy nie
  trafia na uciętą stronę.
- W nagłówku `BUILD` widnieje `· w toku (N gotowych)`, dopóki przebieg trwa.

## r554 — 2026-08-15 — V3.1B-UI finalne dopracowanie
Wyłącznie prezentacja. Zero zmian w canonical data, MACD, RSI, Stochastic i Feature Engine.
- **EMA w trzech rozpoznawalnych kolorach**: EMA20 czerwonawa, EMA50 pomarańczowo-złota,
  EMA100 turkusowa — nadal cienkie (1 px), półprzejrzyste i słabsze niż świece. Legenda
  w nagłówku panelu ceny w kolorach odpowiadających liniom.
- **RSI: koniec stałych pasów tła.** Usunięty helper `zone()`. Kolor pojawia się TYLKO tam,
  gdzie linia faktycznie wychodzi poza kanał: wypełnienie między RSI i poziomem 70 dla
  RSI > 70 (chłodne) oraz między RSI i 30 dla RSI < 30 (ciepłe). Przerwa w serii zamyka
  obszar, więc nie ma sklejania rozłącznych wyjść.
- **Prawa oś pokazuje bieżące wartości, nie granice skali**: etykieta RSI oraz K i D na
  panelu Stochastic. Zniknęła numeryczna siatka z 0 i 100 — zostały prowadnice 70/50/30
  i 20/50/80 z małymi opisami.
- **Nowy, bardzo niski panel Akumulacja/Dystrybucja** (~7% wysokości): standardowa A/D
  Line, `CLV = ((C−L)−(H−C))/(H−L)`, `MFV = CLV × wolumen`, `AD[t] = AD[t−1] + MFV[t]`;
  przy `H == L` wkład zero (bez dzielenia przez zero). Skumulowana, więc liczona na pełnej
  serii canonical przed przycięciem do okna 120. Jedna cienka linia, bez histogramu i stref.
  Wartość bezwzględna zależy od pierwszego bara historii — do walidacji służy przebieg,
  nie zgodność liczby z TradingView.
- Nowe proporcje: cena ~54%, MACD ~17%, RSI ~11,5%, Stochastic ~10,5%, A/D ~7%. Wspólna
  oś czasu, siatka pionowa i crosshair obejmują teraz pięć paneli; tooltip pokazuje A/D.
- EMA, A/D oraz poziomy RSI i Stochastic są renderer-only: nie ma ich w
  `V3_FEATURE_ATOMIC_1`, w eventach ani w scoringu. Formatowanie K/M/B tylko w UI.
- 13 nowych testów struktury (kolory EMA, brak pasów tła, wypełnienie tylko poza kanałem,
  etykiety wartości, formuła A/D, `H == L`, skumulowanie przed oknem, brak w Feature Schema,
  wspólna oś czasu).

## r553 — 2026-08-15
Stary dashboard nie może już zostać wzięty za nowy. Zero zmian w logice wykresów i danych.
- Generator **usuwa** stary `index.html` i pliki `data/*.json` ZANIM zacznie pracę —
  nieudany przebieg nie zostawia artefaktu do przypadkowego otwarcia.
- `BUILD <wersja> · <data i godzina>` widoczne w prawym rogu górnego paska dashboardu;
  generator wypisuje tę samą linię w konsoli po zapisie pliku.
- `TEST-V3-WYKRESY.bat` otwiera dashboard **wyłącznie** przy exit code 0; przy błędzie
  wypisuje, gdzie szukać szczegółów.
- Numer wersji czytany wprost z `config.py` (`findstr`), więc komunikaty startowe modułu
  nie podmieniają go już w nagłówku okna.
- Nowy `TEST-V3-WYKRESY-RBLX.bat` — próba na jednej spółce (`--only RBLX`), bez regresji
  i bez pozostałych 18 spółek.

## r552 — 2026-08-15
Naprawa uruchamialności, zero zmian w logice.
- `config.VERSION` skrócony do jednoliniowego identyfikatora; changelog przeniesiony do
  tego pliku (długi, wielozdaniowy opis w `VERSION` łamał parsowanie pliku).
- `TEST-V3-WYKRESY.bat`: `pushd "%~dp0"` / `popd`, wszystkie ścieżki cytowane, odczyt
  wersji przez plik tymczasowy — ścieżka projektu ze spacją (`C:\Skaner wykresów\`) nie
  rozbija już poleceń.

## r551 — 2026-08-15
Poprawka odczytu numeru wersji w BAT (stary `for /f` rozbijał się o spację w ścieżce).

## r550 — 2026-08-15
Widoczny postęp generacji wykresów: numer wersji na starcie, wyjście kroku [3] na żywo
w oknie (Tee-Object), pasek postępu `[####....] N/19` z czasem i szacowanym pozostałym
czasem.

## r549 — 2026-08-15 — V3.1B-UI WYKRESY WALIDACYJNE
Sprint wyłącznie prezentacyjny. Dominujący panel ceny (~57%) ze świecami, wolumenem,
EMA 20/50/100 (renderer-only) i kropkowaną linią ostatniego FINAL zamknięcia z etykietą
na prawej osi. Pod spodem oddzielone panele MACD (~17%), RSI (~12,5%) i Stochastic
z kompaktowymi legendami. Wspólna oś czasu i pionowa siatka, subtelna siatka pozioma,
crosshair przez cały stos z jednym tooltipem, zoom kółkiem, pan przeciąganiem, Reset
widoku. RSI dostał kanał 30/50/70 ze strefami tła, Stochastic 20/50/80 — poziomy i strefy
są WYŁĄCZNIE prowadnicami wizualnymi. Prawy panel zwężony do 236 px, lewa lista do 172 px.
EMA liczona z canonical FINAL CLOSE na pełnej serii z pre-rollem, potem tail(120).
Zero zmian w MACD, RSI, Stochastic, Feature Engine, `V3_FEATURE_ATOMIC_1`,
`V3_BAR_CONTRACT_1`, canonical market data, H/L policy, pre-roll i warmup.

## r548 — 2026-08-15
Poprawka błędnej asercji w `test_1h_reuses_shared_30m_without_second_fetch` (sprawdzała
pozycję kolumn zamiast ich obecności). Zero zmian w kodzie produkcyjnym.

## r546–r547 — 2026-08-15 — ROOT CAUSE canonical 1D H/L
Warstwa POBIERANIA: jedno zapytanie o 30m za ~2,7 roku było ucinane limitem odpowiedzi
Massive, więc starsza historia nie miała barów 30m i sesje trafiały w fail closed
(RBLX 575/681, INTU 544/681). Fix: pobieranie 30m w kawałkach 60-dniowych pokrywających
cały zakres 1D; jeden dataset 30m zasila analityczne H/L dnia i canonical 1H. Raport
rozdziela brak pokrycia (`SOURCE_MISSING`) od niepełnej sesji (`INCOMPLETE_LOWER_TF`).
Zapisane wymaganie `WYMAGANIE-V3-1B-UI.md`.

## r545 — 2026-08-15 — V3.1B KONTROLA WYKRESÓW
Harness walidacyjny: 19 spółek właściciela rozwiązywanych z bazy Universe (read only),
Massive READ ONLY, canonical 1D i 1H, wskaźniki i cechy przez V3.1A, samowystarczalny
dashboard HTML bez nowych zależności.

## r544 — 2026-08-15 — V3.1A PODSTAWOWE CECHY RYNKU
Atomic Feature Engine: `v3/features` — neutralny, deterministyczny opis każdego bara FINAL
wg `V3_FEATURE_ATOMIC_1` (39 kolumn). Jeden entry point `build_atomic_features`; zero
lookahead, zero scoringu, zero fetch i persistence.

## r541–r543 — 2026-08-15 — zamknięcie V3.0D
Daily quality policy (RAW + CANONICAL ANALYSIS VIEW), production pre-roll 500 (LOCKED)
obok empirycznego 250, spójność dokumentacji i raportów z tymi decyzjami.

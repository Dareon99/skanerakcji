# AUDIT — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
STATUS: PASS WITH CONFLICTS / USER DECISIONS REQUIRED
AUDIT DATE: 2026-08-23
AUDITED VERSION: r599 frozen evidence + SKOOP foundation placeholder
READ-ONLY: YES
```

## 1. Preflight

| Kontrola | Oczekiwane | Rzeczywiste | Wynik | Dowód |
|---|---|---|---|---|
| źródła projektu | MASTER + STAN + AS-BUILT | dostępne i odczytane | PASS | hashe w §7 |
| OLD | frozen/read-only | nie modyfikowano | PASS | brak zapisu i brak uruchamiania |
| Massive | brak użycia w tej paczce | zero żądań i brak sekretu | PASS | zakres działań |
| nowa baza SKOOP | jeszcze nie istnieje | nie utworzono | PASS | STAN + inspection |
| aktywna paczka | najwyżej jedna | jedna nowa paczka | PASS | `03-AKTYWNE-PACZKI/` |
| Git | stan opisany jako initialized | w tym mirrorze brak `.git` | CONFLICT | polecenie read-only zakończone `not a git repository` |
| porty 8000/8001 | nie są przedmiotem paczki | w chwili audytu brak listenerów | INFO | read-only socket inspection |

Brak listenerów nie jest błędem tego pakietu: użytkownik nie zlecił uruchamiania UI,
a kontrakt danych nie wymaga aktywnego runtime.

## 2. Frozen `scanner.db` — stan rzeczywisty

Źródło read-only:
`C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\DATA-SQLITE-BACKUP\scanner.db`.

Tabela `universe` ma pola:

```text
symbol, name, sector, exchange, market_cap, avg_dollar_volume, updated_at,
ipo, debut_date, ipo_price, first_close, spark_d, spark_ts,
base_ok, base_reason, base_evaluated_at
```

Pokrycie snapshotu:

| Metryka | Liczba |
|---|---:|
| wszystkie rekordy universe | 9 903 |
| `base_ok=1` | 4 933 |
| `ipo=1` | 345 |
| nazwa obecna | 9 903 |
| giełda obecna | 9 857 |
| stare pole sektor/branża obecne | 9 613 |
| kapitalizacja > 0 | 5 015 |
| średni obrót > 0 | 8 934 |

Ustalenia:

- stary model przechowuje kilka odpowiedzialności w jednej tabeli;
- symbol jest kluczem roboczym, ale nie ma trwałego `instrument_id`;
- nie istnieją osobne wersjonowane statusy BASE i IPO;
- klasyfikacja nie rozróżnia kanonicznie sektora i branży zgodnie z przyszłą taksonomią;
- brak kapitalizacji dotyczy 4 888 rekordów, więc nie wolno uznać starej listy BASE za
  pełny dowód nowej kwalifikacji;
- tabela `universe` nie ma kolumn kanonicznych linków TradingView/Investing;
- `custom_stocks` ma tylko `symbol`, `name`, `sector`, `exchange`, `created_at`.

## 3. Frozen `market.db` — stan rzeczywisty

Źródło read-only:
`C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\DATA-SQLITE-BACKUP\market.db`.

| TF | Rekordy | Unikalne symbole |
|---|---:|---:|
| `1d` | 165 982 | 13 042 |
| `30m` | 3 504 105 | 2 272 |
| `20m` | 1 705 126 | 750 |
| `10m` | 3 474 732 | 750 |
| razem | 8 849 945 | 13 042 unikalne ogółem |

Ustalenie: odzyskany stan dowodzi praktycznego rozwarstwienia danych — szerokie
pokrycie `1d` i węższe intraday. Nie dowodzi jednak, że dokładnie te same zakresy mają
obowiązywać w nowym SKOOP.

## 4. Kod/UI OLD — ustalenia istotne dla kontraktu

Read-only inspection oryginalnego `ui/index.html` potwierdził:

- listing z sortowaniem i wyborem spółki;
- kolumny m.in. symbol, nazwa, giełda, branża, cena, zmiana, kapitalizacja, wskaźniki,
  obrót, alert/score, linki i watchlista;
- prawy sidebar z ceną, kapitalizacją, obrotem, wskaźnikami i lokalnymi wykresami;
- powiększanie wykresów;
- link TradingView rozwiązywany przez ręczną korektę, zapisany URL lub resolver;
- fallback Investing był wyszukiwaniem `search/?q=<ticker>`, nie dowodem prawidłowego
  bezpośredniego instrumentu;
- frontend potrafił edytować linki, ale pełny universe nie przechowuje ich w frozen DB.

Wniosek: układ listingu i sidebara jest wartościową referencją, ale stary resolver
Investing nie spełnia aktualnego wymagania „niezmyślony, prawidłowy URL”.

## 5. Dokumentacja odzyskana

Architektura V4.4 potwierdza:

- rozdzielenie po właścicielu zapisu: `market.db`, `core.db`, `companies.db`, `news.db`,
  `portfolio.db`;
- `universe_symbols` jako własność odkrywania universe;
- `base_state` jako wynik oceny bez sieci;
- `company_ipo` jako osobny wynik, bez `UPDATE universe SET ipo=0`;
- `company_base_input` przed pełnym profilem;
- publikację wersjonowaną z zachowaniem ostatniej poprawnej wersji;
- priorytety wpływające na kolejność, nigdy na kwalifikację;
- GET bez sieci i bez ciężkich obliczeń.

MASTER zawiera wcześniejsze założenie `BASE_OK = base_ok=1 AND ipo=0`, natomiast
aktualne wymaganie użytkownika dopuszcza jednoczesny status BASE i IPO. Konflikt jest
materialny i wymaga trwałej decyzji.

## 6. Testy wykresów i listing analityczny

- V3: 6 spółek × 5 TF, `30/30` payloadów, historyczny wynik `394 PASS / 0 FAIL`;
- V3 nie jest zintegrowany z nowym SKOOP;
- odzyskany `Cykle 1D` potwierdza potrzebę miniwykresów ceny/MACD/RSI i przejścia do
  pełnego wykresu, ale jest kontraktem późniejszego listingu analitycznego, nie
  kwalifikacji BASE.

## 7. Hashe dowodów

```text
BEB2810F670FF837B68092B30DC9858BA8C07F5A6FDF30A26AA0B84E21CA0C40  MASTER-PROJEKT.md
02733B03015E67E6E8CB18D4A8A328F7254D6BCB6729A6AB5F07DF3430309AB8  STAN-AKTUALNY.md
B9C4BDB3258FFACF52CCD37B55E3AC5E12970EC38FC8F4702AD5A7D5C45AFFA6  ARCHITEKTURA-ZASOBOW-V4.4-FINAL.txt
7BD1FB15E942B824F00C188854C54EE405585B7F137B4C081CAF7A9D6C7D59F2  WYKRESY/FINAL-AS-BUILT-SPEC.md
6A559D384F33B7A39BD98EEC2F1F9EFAD320CC13B9036F0628BA8FB8F1E07F51  SKANER-CYKLE-1D/RECOVERED-SPEC.md
A1D2512AC200AC00ED868A9E110E01902D9518B089CEA3C8E2ED536BBBD925D8  frozen scanner.db
659AD89960373747ED44D4177ABF60A42B84DC29AD67FCA5F8AA7B7FAA335FDB  frozen market.db
```

## 8. Konkluzja

`AUDIT PASS WITH CONFLICTS / CONFLICT REPORT REQUIRED / USER DECISIONS REQUIRED`.

Można zatwierdzić logiczny kierunek SPEC. Nie można jeszcze utworzyć Implementation
Contract ani kodu nowej bazy, ponieważ otwarte decyzje wpływają na zakres danych,
semantykę BASE i cykl życia IPO.

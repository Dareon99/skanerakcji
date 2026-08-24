# MASTER PROJEKT — SKANER WYKRESÓW

> Status dokumentu: pierwsza wersja odzyskana z dostępnej rozmowy i znanego stanu projektu  
> Data utworzenia: 2026-08-21  
> Stan odniesienia: `VERSION 2026-08-21-r599`  
> Rola dokumentu: nadrzędne, trwałe źródło prawdy i indeks dokumentacji projektu

---

## 0. Jak czytać ten dokument

### 0.1. Zasada nadrzędna

`MASTER-PROJEKT.md` jest mapą projektu: opisuje cel, aktualny stan, potwierdzoną architekturę, reguły pracy, roadmapę oraz wskazuje, gdzie znajdują się szczegółowe dowody i specyfikacje. Nie zastępuje kodu, raportów testowych, screenshotów, eksportów rozmów ani specyfikacji AS-BUILT. Indeksuje je i określa ich status.

Projekt nie może opierać się na pamięci ChatGPT, Claude ani historii pojedynczego czatu. Źródłem prawdy są pliki zapisane w repozytorium i lokalnym archiwum projektu.

### 0.2. Statusy wiarygodności

Każde odzyskiwane ustalenie musi mieć jeden z poniższych statusów:

- `CONFIRMED` — potwierdzone w dostępnej rozmowie, wyniku audytu, kodzie albo istniejącym artefakcie.
- `PARTIAL` — kierunek lub część rozwiązania jest potwierdzona, ale brakuje kompletnej specyfikacji albo dowodu końcowej implementacji.
- `UNVERIFIED` — informacja pojawiła się jako możliwość lub nie ma obecnie wystarczającego dowodu.
- `TO RECOVER` — element wiadomo, że był projektowany lub tworzony, lecz trzeba go odzyskać z lokalnych plików, starszych rozmów, screenshotów albo archiwów.

Status dokumentacyjny nie jest statusem wdrożenia. `CONFIRMED` może oznaczać potwierdzoną specyfikację, a nie działającą funkcję produkcyjną. Każdy wpis musi jasno wskazywać, co dokładnie zostało potwierdzone.

### 0.3. Zakaz zgadywania

Brak danych nie może być uzupełniany z pamięci modelu ani przez „rozsądne domysły”. Brakujące ustalenie otrzymuje status `UNVERIFIED`, `TO RECOVER` albo `DECISION REQUIRED`.

### 0.4. Hierarchia źródeł prawdy

W razie rozbieżności obowiązuje kolejność:

1. zaakceptowany, zamrożony kod i jego hashe;
2. `FINAL-AS-BUILT-SPEC.md` właściwego sprintu;
3. zaakceptowane decyzje użytkownika w `DECYZJE-PROJEKTOWE.md`;
4. wyniki realnie wykonanych testów i audytów;
5. `STAN-AKTUALNY.md`;
6. niniejszy MASTER;
7. pierwotny SPEC i Implementation Contract;
8. eksporty rozmów i notatki robocze;
9. pamięć modelu — nigdy jako samodzielny dowód.

Jeżeli nowsza zaakceptowana decyzja zmienia starszą, starszego wpisu nie usuwa się. Otrzymuje status `SUPERSEDED` z odwołaniem do decyzji zastępującej.

### 0.5. Pakiet źródłowy „Skaner sygnałów kupna”

Pakiet `Skaner-sygnalow-kupna-ARCHIWUM.zip` został zaimportowany 2026-08-21 i zamrożony w `DOKUMENTACJA/ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/SOURCE-ARCHIVE/`. SHA-256 oryginalnego ZIP: `f2075b20dd16f4cdcfb783f670e7e920a80396eef26b840622fdaff066f3529a`.

Pliki `README-START-HERE.md`, `MASTER-PROJEKT.md` i `STAN-AKTUALNY.md` z tego pakietu są zaakceptowanym źródłem historycznym i źródłem pochodzenia ustaleń. Nie zastępują nowszych frozen AS-BUILT, kodu ani niniejszego scalonego MASTER-a. Importowany MASTER ma SHA-256 `242302fbd5bcc24327617a7ab89f8f3e32f9ec598034ac9a296c2b32ab6d65d2`, identyczny z wcześniej zachowanym `MASTER-SOURCE-USER-2026-08-21.md`.

Ograniczenie pakietu jest jawne: nie jest to surowy transcript rozmowy 1:1. Brakujące oryginalne raporty, skrypty aktywacyjne, logi i załączniki pozostają `TO RECOVER`; treść rekonstrukcji nie może sama udowodnić istnienia nieodnalezionego pliku.

---

## 1. Cel produktu

### 1.1. Cel główny — `CONFIRMED`

„Skaner wykresów” ma być systemem, który prowadzi użytkownika przez cały przepływ:

`UNIVERSE SPÓŁEK`  
→ kwalifikacja bazowa  
→ profil IPO  
→ sektor i branża  
→ dane rynkowe  
→ mechanizm skanera  
→ scoring i sygnały  
→ ranking/listing wyników  
→ wybór spółki  
→ ekran szczegółowy  
→ wykresy  
→ interpretacja, etap, skuteczność/confidence i alarmy.

Wykresy nie są osobnym dodatkiem. Są częścią wyniku pracy skanera. Warstwa infrastrukturalna r598/r599 ma zapewnić dostęp do danych w sposób, który chroni ruch interaktywny i zapobiega wzajemnemu zagłuszaniu się zadań.

### 1.2. Docelowe możliwości — stan wiedzy

| Obszar | Oczekiwany rezultat | Status |
|---|---|---|
| Universe spółek | Stabilna populacja spółek z kwalifikacją bazową, IPO i klasyfikacją | `PARTIAL` |
| Skaner | Wybór spółek/sygnałów według reguł, filtrów i scoringu | `PARTIAL` — kierunek potwierdzony, kompletna logika do odzyskania/zaprojektowania |
| Listing | Ranking wyników, filtrowanie, sortowanie i wybór spółki | `PARTIAL` |
| Ekran spółki | Identyfikacja, klasyfikacja, wynik, etap, skuteczność i metryki | `PARTIAL` |
| Wykresy | Wykres 1D z ustalonym zestawem średnich i paneli wskaźnikowych | `PARTIAL` — zestaw potwierdzony, finalna kalibracja do odzyskania |
| Integracja | Kliknięcie wyniku → dane → wykres → interpretacja | `PARTIAL` |
| Alarmy | Alarmy oparte na wynikach skanera i stanie sygnału | `PARTIAL` — istnienie obszaru potwierdzone, reguły `TO RECOVER` |

### 1.3. Granice obecnej wiedzy

Po recovery `PROJECT-RECOVERY-001` potwierdzono znaczną część mechanizmu `Cykle 1D` i finalnego renderera V3. Nadal nie są potwierdzone: pełny algorytm pozostałych zakładek skanera, dokładny model skuteczności/confidence starego UI, komplet reguł alarmów, wszystkie kolumny listingu poza odzyskanym zakresem `Cykle 1D` oraz produkcyjny kontrakt integracji V3 z głównym ekranem. Nie wolno ich implementować jako „odzyskane” bez audytu źródeł.

---

## 2. Aktualny stan projektu

### 2.1. Snapshot r599 przed aktywacją — `CONFIRMED / HISTORICAL`

| Pole | Stan |
|---|---|
| Wersja | `2026-08-21-r599` |
| Etap | r599 zaakceptowany technicznie przy managerze OFF |
| Audyt | `PASS 181 / FAIL 0` |
| `test_massive_traffic.py` | kod 0, `FAIL 0` |
| `test_massive_telemetry.py` | kod 0, `FAIL 0` |
| Massive Traffic Manager | `OFF` |
| Flaga managera | `massive_traffic_manager_enabled = 0` |
| Flaga pomiaru r598 | `massive_traffic_measurement_enabled = 0`, bez zmiany |
| `provider_state.db` | nieutworzony przy managerze OFF — stan prawidłowy |
| Mutacje baz biznesowych podczas audytu | zero |
| Następny etap w tym snapshocie | kontrolowana aktywacja managera — wykonana później |
| r600 / C3A | nie rozpoczęto |

### 2.1.1. Stan procesu w dniu recovery — `CONFIRMED`

| Pole | Stan |
|---|---|
| Główny serwer na porcie 8000 | `OFF` — brak procesu nasłuchującego |
| Zadania autostartu `SkanerWykresow*` | nie znaleziono |
| Kod `C:\Skaner wykresów` | obecny, zinwentaryzowany read-only |
| Dane `C:\skaner-dane` | obecne; `scanner.db` i `market.db` zachowane |
| Główny wykres UI | starszy endpoint `/candles/{symbol}` |
| Finalny dashboard V3 | odzyskany offline, `6 × 5 TF = 30/30` |
| Integracja V3 z głównym UI | `NOT IMPLEMENTED` |

Serwer OFF jest niezależny od konfiguracji managera. Brak serwera jest bezpośrednim powodem, dla którego główny interfejs nie może obecnie ładować wykresów. Manager jest zaakceptowany jako ON, lecz nie działa bez uruchomionego procesu.

### 2.1.2. Kontrolowana aktywacja r599 — `CONFIRMED / ACCEPTED`

Ponowny audit 2026-08-21 wykazał stan późniejszy niż snapshot recovery:

| Pole | Stan |
|---|---|
| `config.py` LastWrite | 2026-08-21 14:33:46 |
| Różnica wobec backupu sprzed aktywacji | dokładnie jedna linia: manager `0 → 1` |
| VERSION | bez zmiany, `2026-08-21-r599` |
| `provider_state.db` | utworzony 14:36:25, `integrity_check=ok`, `user_version=1`, WAL |
| Schema | `traffic_state`, `priority_tickets` |
| Stan 429 | `count_429=0`, brak aktywnego cooldownu |
| Runtime podczas audytu | OFF, brak procesu i portu 8000 |
| Live acceptance | PASS po starcie, około 13 i około 20 minutach |
| Wynik | `ACTIVATION ACCEPTED`, manager pozostawiony ON |

Zachowany backup `_backup-r599-MASSIVE-TRAFFIC-ACTIVATION-001/config.py.przed-aktywacja`, hashe BEFORE/AFTER, trzy statusy live i odzyskany MASTER użytkownika potwierdzają zaakceptowaną aktywację. Pełny AS-BUILT: `DOKUMENTACJA/ARCHIWUM/R599-MASSIVE-TRAFFIC-ACTIVATION-001/FINAL-AS-BUILT-SPEC.md`.

### 2.2. Znaczenie akceptacji przed aktywacją — `HISTORICAL`

Ten warunek obowiązywał w snapshocie pre-activation: r599 był wtedy zaakceptowany wyłącznie przy managerze OFF. Został później superseded przez pomyślną kontrolowaną aktywację `r599-MASSIVE-TRAFFIC-ACTIVATION-001`.

### 2.3. Wykonana zmiana aktywacyjna — `DONE`

Oczekiwany semantyczny zakres kontrolowanej aktywacji:

```text
massive_traffic_manager_enabled = 0
->
massive_traffic_manager_enabled = 1
```

Wykonanie spełniło kontrakt: zmieniono tylko tę flagę, bez zmiany VERSION i parametrów managera. Hash BEFORE: `5a1acf...675c9`; hash AFTER: `08e51f...ceb8`.

### 2.4. Warunki aktywacji — `DONE / ACCEPTED`

Aktywacja musi być osobnym, małym, odwracalnym pakietem. Musi obejmować co najmniej:

1. preflight ścieżki projektu, wersji, flagi OFF, importów, testów i braku source drift;
2. backup każdego zmienianego pliku — oczekiwany wyłącznie `config.py`;
3. kontrolowaną zmianę flagi;
4. restart wszystkich procesów, które odczytują flagę lub korzystają z providera;
5. potwierdzenie dokładnej topologii procesów; obecne nazwy/liczba procesów są `TO RECOVER`;
6. pierwszy kwalifikowany request i weryfikację lazy-create `C:\skaner-dane\provider_state.db`;
7. kontrolę SQLite: otwarcie, `integrity_check`, `user_version = 1`, WAL, schema i poprawny stan;
8. kontrolę logów: wyjątki, importy, retry storm, 429, FAIL-OPEN;
9. krótki kontrolowany live test;
10. akceptację albo natychmiastowy rollback z zachowaniem `provider_state.db` jako dowodu diagnostycznego.

Live test został wykonany i sprawdzony po około 20 minutach; `OVERALL PASS`, exit code 0, SQLite i business DB safety PASS, 429=0.

---

## 3. Architektura — stan potwierdzony

### 3.1. Ścieżki środowiska — `CONFIRMED` dla lokalnego stanu r599

```text
Projekt:      C:\Skaner wykresów
Backend:      C:\Skaner wykresów\backend
Dane:         C:\skaner-dane
Interpreter:  C:\Skaner wykresów\backend\.venv\Scripts\python.exe
```

Uwaga: wcześniejsze logi pokazywały również błędną formę bez separatora `backend.venv`; audyt r599 potwierdził, że poprawna forma zawiera `backend\.venv`. Skrypty `.bat` mają budować ścieżki względem `%~dp0` i nie mogą polegać na interpreterze systemowym.

### 3.2. Warstwy logiczne

Potwierdzony kierunek architektury:

1. **Źródło/provider danych rynkowych** — aktualny kod odnosi się do Massive przez `polygon_source.py`.
2. **Cross-process Massive Traffic Manager** — wspólna koordynacja zapytań w `core/massive_traffic.py`.
3. **Bazy biznesowe** — odseparowane od bazy managera; obowiązuje zasada jednego właściciela zapisu.
4. **Fundament spółek** — `companies.db`, kwalifikacja `BASE_OK`, IPO, SIC, sektor i branża.
5. **Mechanizm skanera** — wybór, filtry, scoring, sygnały i ranking; pełna implementacja `TO RECOVER/PLANNED`.
6. **Listing i ekran spółki** — UI wyników i szczegółów; specyfikacja częściowa.
7. **Generator/warstwa wykresów** — potwierdzony zestaw wskaźników, finalna kalibracja `TO RECOVER`.
8. **Interpretacja i alarmy** — docelowa warstwa; szczegóły `TO RECOVER`.

Nazwy procesów, endpointy, dokładne granice modułów i pełny diagram zależności są `TO RECOVER` z repozytorium.

### 3.3. Massive Traffic Manager r599 — `CONFIRMED`

| Parametr | Wartość |
|---|---|
| Wspólny stan | `C:\skaner-dane\provider_state.db` |
| Model | jeden współdzielony cross-process token bucket |
| Refill | `30 tokens/s` |
| Capacity | `90` |
| Początkowy bucket | `90` |
| SQLite schema | `user_version = 1` |
| Journal mode | `WAL` |
| Busy timeout | `0.25 s` |
| TTL P0 | `3 s` |
| TTL P1 | `10 s` |
| TTL P2 | `45 s` |
| TTL P3 | `180 s` |
| Kolejność | `P0 < P1 < P2 < P3` |
| Kolejka | ticket queue, FIFO w ramach priorytetu |
| Cooldown 429 | współdzielony, `13 s` |
| Rezerwacje | brak |
| Fail-open | istniejący kontrakt r599 |
| Tworzenie DB | lazy-create przy pierwszym kwalifikowanym acquire przy managerze ON |

Manager nie może importować sieci, korzystać z baz biznesowych ani uruchamiać wątków tła. Audyt potwierdził `BEGIN IMMEDIATE`, współdzielenie stanu między procesami, obsługę stale tickets, TTL, cooldown i brak nadprodukcji tokenów.

### 3.4. Priorytety P0–P3

| Priorytet | Znaczenie | TTL | Status definicji |
|---|---|---:|---|
| P0 | `INTERACTIVE_MARKET`; obejmuje interaktywny rynek/wykresy | 3 s | `CONFIRMED` |
| P1 | `SCANNER_CRITICAL` | 10 s | `CONFIRMED` w importowanym MASTER i kodzie `core/massive_telemetry.py` |
| P2 | `MAINTENANCE` | 45 s | `CONFIRMED` w importowanym MASTER i kodzie `core/massive_telemetry.py` |
| P3 | `COMPANY_BACKGROUND`; bez zarezerwowanej capacity, ustępuje wyższym priorytetom | 180 s | `CONFIRMED` w importowanym MASTER i kodzie `core/massive_telemetry.py` |

Zasady:

- niższy numer oznacza wyższy priorytet;
- P0 musi być uprzywilejowany względem cięższych prac w tle;
- w ramach jednego priorytetu niższy `ticket_id` otrzymuje grant pierwszy;
- cooldown 429 blokuje również P0 zgodnie z kontraktem;
- nie wolno zmieniać mapowania operacji na P0–P3 bez SPEC, audytu i decyzji użytkownika;
- nie wolno tworzyć kategorii `INTERACTIVE_CHART` bez decyzji — audyt potwierdził, że nie występuje w runtime enumach; interaktywny wykres należy do potwierdzonego `INTERACTIVE_MARKET`.

### 3.5. Bazy danych

| Baza | Rola | Stan wiedzy |
|---|---|---|
| `C:\skaner-dane\provider_state.db` | wyłącznie współdzielony stan managera ruchu | `CONFIRMED`; istnieje, integrity OK, user_version 1, WAL |
| `market.db` | W3, świece i stan synchronizacji rynku | `CONFIRMED`; plik istnieje, rola potwierdzona w architekturze V4.4 i kodzie |
| `scanner.db` / docelowo `core.db` | bieżący core pipeline/universe oraz docelowa baza łańcucha pipeline'u | `PARTIAL`; `scanner.db` istnieje, migracja/nazwa `core.db` pozostaje stanem architektury docelowej |
| `companies.db` | W0/W8/W11, profil i klasyfikacja spółek | `CONFIRMED` jako kontrakt V4.4 i kod; plik produkcyjny obecnie nie istnieje, pełny stan wdrożenia `TO RECOVER` |
| `news.db` | W10, wiadomości odseparowane od skanu | `CONFIRMED` jako kontrakt V4.4; wdrożenie produkcyjne `TO RECOVER` |
| `portfolio.db` | W12 i akcje użytkownika; dane transakcyjne poza łańcuchem | `CONFIRMED` jako kontrakt V4.4; wdrożenie produkcyjne `TO RECOVER` |

Obowiązują następujące zasady:

- baza managera jest oddzielona od baz biznesowych;
- brak `ATTACH` między `provider_state.db` i bazami biznesowymi;
- tabela managera nie może powstać w bazie biznesowej;
- bazy biznesowe mają zasadę jednego właściciela zapisu;
- odczyty UI/GET nie powinny wykonywać zapisu ani sieci — potwierdzone jako kierunek dla modułu spółek, pełny audit `TO RECOVER`;
- publikacja danych ma być atomowa, a konsumenci mają korzystać z `last-good`; szczegóły implementacji `TO RECOVER`.

### 3.6. Fail-open, last-good i bezpieczeństwo

- `FAIL-OPEN` jest kontrolowanym zachowaniem managera przy niedostępności koordynacji; nie może maskować zwykłego braku tokenów.
- Pojedynczy izolowany FAIL-OPEN może być ostrzeżeniem wymagającym analizy; ciągły FAIL-OPEN w normalnym ruchu jest kandydatem do nieudanej aktywacji. Dokładny próg liczbowy: `UNVERIFIED/DECISION REQUIRED`.
- Po 429 wspólny cooldown ma zostać zapisany. Lokalny `sleep(13)` u callera jest fallbackiem tylko wtedy, gdy wspólny zapis się nie uda.
- `last-good` ma chronić konsumentów danych przed chwilowymi problemami providera. Pełny kontrakt per moduł: `TO RECOVER`.
- Rollback aktywacji nie może automatycznie usuwać `provider_state.db`; baza może być dowodem diagnostycznym.

---

## 4. Fundament spółek i klasyfikacja

### 4.1. Potwierdzone elementy

- istnieje osobny fundament danych spółek oparty na `companies.db`;
- populacja bazowa była określona jako `BASE_OK = base_ok=1 AND ipo=0`;
- IPO jest traktowane osobno i nie powinno samodzielnie zmieniać statusu bazowego;
- dla populacji bazowej pobierano/uzupełniano `sic_code`;
- SIC zasila mapowanie do sektora i branży;
- katalog miał dokładnie `20` sektorów i `129` branż;
- walidacja wymaga, aby każda branża należała do istniejącego sektora;
- nierozpoznane pozycje mają stan `UNRESOLVED`;
- zabroniony jest fałszywy fallback wszystkiego do `Miscellaneous`;
- kierunek taksonomii był kompatybilny/inspirowany TradingView;
- istniał obszar `listing_scope`, ale jego pełny kontrakt jest `TO RECOVER`.

### 4.2. Do odzyskania

- pełny schemat `companies.db`;
- komplet 20 sektorów i 129 branż wraz z mapowaniami;
- dokładny algorytm oraz źródło uzupełniania SIC;
- reguły stanów poza `BASE_OK`, IPO i `UNRESOLVED`;
- zasady publikacji atomowej i `last-good` dla tego obszaru;
- granice i znaczenie `listing_scope`;
- pełne pokrycie universe i kryteria włączenia/wyłączenia spółki.

---

## 5. Odzyskane elementy skanera, listingu i wykresów

### 5.1. Skaner i ekran spółki

| Element | Status | Co jest potwierdzone / czego brakuje |
|---|---|---|
| Ciemny interfejs `STOCK SCANNER` | `CONFIRMED` | screenshot zachowany w `PROJECT-RECOVERY-001/REFERENCES/SCANNER-ADMA-NOISE-EXAMPLE.png` |
| Moduł/zakładka `SKANER` | `CONFIRMED` | widoczna w referencji |
| Prezentacja wybranej spółki | `CONFIRMED` | przykład HUMA / Humacyte |
| Identyfikacja | `CONFIRMED` | ticker, pełna nazwa, giełda, kraj, branża |
| Wynik interpretacyjny | `CONFIRMED` jako element starego UI | przykład `ODBIJA`; nie jest częścią odzyskanego kontraktu `Cykle 1D` |
| Etap sygnału | `CONFIRMED` jako element starego UI | przykład `ETAP: WCZEŚNIE`; użytkownik zdecydował, że `Cykle 1D` ma obecnie działać bez faz |
| Skuteczność/confidence | `CONFIRMED` tylko jako element starego UI | przykład `Skuteczność 67%`; algorytm `TO RECOVER`, pole ma być usunięte z bieżącego `Cykle 1D` |
| Filtry | `PARTIAL` | potwierdzone obszary: cykle, trendy, branże, alarmy, IPO i dane; dokładne pola/reguły `TO RECOVER` |
| Wykresy na ekranie analizy | `CONFIRMED` | obecne w referencji; zachowanie interaktywne `TO RECOVER` |
| Metryki szczegółowe | `PARTIAL` | ich obecność jest widoczna, komplet i definicje `TO RECOVER` |

### 5.2. Listing spółek

Potwierdzony jest kierunek: lista/ranking wyników skanera ma umożliwiać filtrowanie, sortowanie, wybór spółki, ocenę aktualności danych i przejście do szczegółów. Zachowany screenshot potwierdza zakładki `Cycles`, `Trends`, `Sectors`, `Alarm`, `IPO`, `Data` oraz osobne wskazania m.in. aktywnych cykli 1D i 1H.

Dla listy `Cykle 1D` odzyskano konkretny kontrakt pól: identyfikacja spółki, miniwykres ceny, MACD/histogram, RSI, względna głębokość, bieżący/minimalny MACD, historyczna średnia i mediana, minimalny RSI/Stoch w cyklu, trend histogramu, daty minimum i przecięcia, sesje od przecięcia oraz przejście do pełnego wykresu/TradingView.

`TO RECOVER`:

- wszystkie kolumny;
- kolejność i szerokości kolumn;
- domyślne sortowanie i tie-breakery;
- kombinacje filtrów;
- paginacja/liczba rekordów;
- zachowanie kliknięcia;
- badge, statusy, hover i responsywność;
- model odświeżania i prezentacja wieku danych;
- tie-breakery rankingu;
- kompletna specyfikacja UX pozostałych zakładek.

Do czasu odzyskania tych danych nie wolno oznaczać listingu jako gotowego AS-BUILT.

### 5.3. Mechanizm skanera

`CONFIRMED` jako planowany zakres:

- reguły wyboru spółek;
- filtry;
- scoring;
- cykle/trendy;
- statusy wynikowe;
- ranking/kolejność;
- alarmy;
- przekazanie wybranej spółki i danych do warstwy wykresów.

#### Odzyskany kontrakt `Cykle 1D` — `CONFIRMED`

- jeden status `Cykle 1D`; bez faz, BUY i generycznej skuteczności;
- aktywny ujemny cykl MACD;
- maksymalna osiągnięta głębokość bieżącego cyklu co najmniej równa zarówno historycznej medianie, jak i średniej zakończonych cykli;
- w cyklu wystąpiły `RSI <= 32` oraz `Stoch %K <= 22`; warunki są pamiętane przez cały cykl;
- pierwsze skrócenie ujemnego histogramu (`hist[t] < 0` i `hist[t] > hist[t-1]`) otwiera kwalifikację;
- jeżeli histogram przed przecięciem znowu się pogłębia, wczesny sygnał jest anulowany do nowego skrócenia;
- po wzrostowym przecięciu spółka pozostaje najwyżej pięć zamkniętych sesji tylko przy dodatnim i rosnącym histogramie;
- ranking po `achieved_max_negative_depth / max(historical_mean, historical_median)`;
- tylko zamknięte świece 1D, 250 sesji na widoku, preferowane minimum pięć zakończonych cykli historycznych;
- bieżący niezakończony cykl nie wchodzi do średniej/mediany historycznej;
- wolumen jest kontekstem, nie początkowym twardym filtrem; robocze `RVOL20 = current / median(previous 20)`;
- `RBLX` jest wzorcem pożądanym, `ADMA` przykładem szumu przy głębokości około 55% typowej excursion.

Pełny dokument dowodowy: `ARCHIWUM/PROJECT-RECOVERY-001/SKANER-CYKLE-1D/RECOVERED-SPEC.md`.

`TO RECOVER`: tie-breakery, polityka przy mniej niż pięciu cyklach, model luk/braków danych, dokładny kontrakt API/cache, pozostałe zakładki i interwały, alarmy, cooldown/deduplikacja oraz testy golden-master całego universe.

### 5.4. Wykresy — odzyskany kontrakt funkcjonalny

`CONFIRMED` po recovery:

- interwały `30m`, `1H`, `2H`, `4H`, `1D`; domyślnie `1D`;
- świece OHLC;
- wolumen;
- `WMA 9`;
- `EMA 20`;
- `EMA 50`;
- `EMA 100`;
- `EMA 200`;
- panel `MACD`;
- panel `RSI 14 close`;
- panel `Stochastic 14/3/3`;
- panel `Accumulation/Distribution`;
- ciemne tło;
- oś ceny po prawej;
- układ: panel główny ceny i wolumenu, niżej osobno MACD, RSI, Stochastic i A/D;
- referencje TradingView zachowane dla `RBLX`, `AAOI`, `CRM`, `INTU`, `HUBS`;
- walidacja objęła 19 spółek: `RBLX`, `INTU`, `NVDA`, `ADTN`, `PLTR`, `ORCL`, `NBIS`, `FIG`, `LITE`, `AAOI`, `ZS`, `DDOG`, `COHR`, `AAPL`, `SMCI`, `DAL`, `MS`, `BAC`, `NVO`;
- finalny szybki dashboard obejmuje `RBLX`, `AAOI`, `INTU`, `NVDA`, `PLTR`, `ADTN`;
- finalny szybki dashboard ma komplet `30/30` payloadów i został odbudowany offline w 6,93 s;
- finalny zapis regresji: `394 PASS / 0 FAIL`.

Finalne reguły AS-BUILT obejmują m.in.: 250 świec widoku fast dashboardu; historie 1100 dni dla 1D i 400 dni dla niższych TF; `V3_FEATURE_ATOMIC_1`; RSI wypełniany tylko poza 30/70; Stoch 20/50/80; panel RSI 1,5× Stoch; autoskalę MACD widocznego zakresu z zapasem; segmentację B z progiem `0,25 × std(MACD)`; marker przecięcia na barze zdarzenia; historyczne excursion tylko na 1D; resume/self-repair i rebuild z payloadów.

`PARTIAL/TO RECOVER`: formalna końcowa zgodność 1:1 z TradingView dla całego universe, pierwotna dziesiątka referencyjna oraz produkcyjny kontrakt API/UI.

Najważniejsza granica: V3 było osobnym narzędziem walidacyjnym i **nie zostało zintegrowane z główną aplikacją**. Główne UI nadal korzysta ze starszego `/candles/{symbol}`. Pełny dowód: `ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/FINAL-AS-BUILT-SPEC.md`.

### 5.5. Alarmy

`CONFIRMED` jako część docelowego produktu i obszar filtra UI.

`TO RECOVER`:

- warunki tworzenia alarmu;
- kanały i sposób prezentacji;
- poziomy ważności;
- deduplikacja;
- cooldown/wygaszanie;
- potwierdzanie przez użytkownika;
- powiązanie z etapem, scoringiem i skutecznością;
- trwałość i baza danych;
- testy oraz wymagania czasu dostarczenia.

---

## 6. Roadmapa od r599 do produktu

Roadmapa wskazuje kolejność, nie upoważnia do łączenia etapów w jedną paczkę. Każdy etap wymaga osobnego SPEC i małych izolowanych pakietów.

### R0 — Utrwalenie projektu i recovery — `DONE`

Cel: przenieść pamięć projektu z rozmów do repozytorium.

Zakres:

- utworzyć i zatwierdzić niniejszy MASTER;
- utworzyć `STAN-AKTUALNY.md`, `ZASADY-PROJEKTU.md`, `DECYZJE-PROJEKTOWE.md`;
- zinwentaryzować lokalne repo i archiwa w trybie read-only;
- odzyskać dokumenty r595–r599;
- odzyskać pliki skanera, listingu, generatora wykresów, konfiguracje i screenshoty;
- utworzyć rejestr artefaktów z hashami;
- opracować `FINAL-AS-BUILT-SPEC.md` dla odzyskanych obszarów tylko w zakresie udowodnionym.

Akceptacja: wszystkie braki mają jawny status; żaden element nie jest dopisany z pamięci jako fakt.

Stan 2026-08-21: `PROJECT-RECOVERY-001` odzyskał generator V3, dashboard 6 × 5 TF, źródła/testy/referencje, reguły `Cykle 1D` i architekturę V4.4. Utworzono `STAN-AKTUALNY.md`, raport recovery, wykresowy FINAL-AS-BUILT i rejestr artefaktów. Pozostałe braki są jawne.

### R1 — Kontrolowana aktywacja r599 — `DONE / ACCEPTED`

Cel: włączyć zaakceptowany manager bez zmiany kontraktu r599.

Kolejność:

1. SPEC aktywacji;
2. audit aktualnego źródła i topologii procesów;
3. Conflict Report;
4. decyzje użytkownika;
5. Implementation Contract;
6. mała izolowana paczka aktywacyjna;
7. lokalny preflight;
8. backup;
9. dokładnie jedna zaakceptowana zmiana flagi;
10. kontrolowany restart;
11. health check;
12. krótki live test;
13. acceptance albo rollback;
14. archiwum sprintu i FINAL-AS-BUILT.

Wynik: dokładnie jeden PID Uvicorn (`12024`), port 8000, realny skan 5088 spółek, lazy-create zdrowej bazy managera i PASS po około 20 minutach. Manager pozostawiony ON. Serwer został później zatrzymany.

### R1.5 — Przywrócenie działania wykresów w starym runtime — `SUPERSEDED / CANCELLED`

Pierwotny cel polegał na kontrolowanym uruchomieniu r599 i weryfikacji starszej ścieżki `/candles/{symbol}`. Decyzja D-006 zastąpiła ten plan: stary system zostaje OLD i nie wolno go restartować. Odzyskany V3 zostanie wykorzystany dopiero w izolowanym nowym produkcie SKOOP.

### R2 — Recovery i domknięcie fundamentu spółek — `PLANNED`

Cel: potwierdzić universe, klasyfikację i kontrakt danych dla listingu.

Zakres: `companies.db`, `BASE_OK`, IPO, SIC, 20 sektorów, 129 branż, `UNRESOLVED`, `listing_scope`, atomic publish i last-good.

Akceptacja: pełny AS-BUILT schematu, źródeł, transformacji i testów; zero fałszywego fallbacku.

### R3 — Mechanizm skanera — `PLANNED`

Cel: zbudować lub odzyskać właściwą logikę selekcji i rankingu.

Zakres: wejścia, reguły, filtry, scoring, cykle/trendy, statusy, etapy, ranking, confidence i kontrakt alarmów.

Zalecany pierwszy pionowy przepływ: jedna spółka → dane → wynik skanera → udokumentowany powód wyniku. Rozszerzenie dopiero po akceptacji tego pakietu.

### R4 — Listing spółek — `PLANNED`

Cel: stabilny ekran wyników skanera.

Zakres: kolumny, filtry, sortowanie, ranking, status danych, paginacja, wybór spółki, stany błędów i last-good.

Warunek startu: odzyskana lub zatwierdzona od nowa pełna UI-SPEC.

### R5 — Ekran szczegółowy spółki — `PLANNED`

Cel: pokazać identyfikację, klasyfikację, wynik, etap, confidence i kluczowe metryki.

Warunek: wynik skanera i jego pola muszą mieć stabilny kontrakt.

### R6 — Recovery i integracja generatora wykresów — `PLANNED`

Cel: wykorzystać istniejący generator, bez kalibrowania od zera.

Kolejność:

1. `DONE` — read-only inventory lokalnych plików;
2. `DONE` — odtworzenie konfiguracji AS-BUILT i offline rebuild;
3. `DONE` — identyfikacja finalnego zestawu 6 i wcześniejszej walidacji 19 spółek;
4. `PARTIAL` — zachowanie dostępnych referencji TradingView;
5. `DONE` — wykresowy `FINAL-AS-BUILT-SPEC.md`; formalna akceptacja 1:1 pozostaje otwarta;
6. `NEXT IN SKOOP` — pionowy przepływ: jedna spółka → dane 5 TF → payload → wykres w nowej aplikacji;
7. integracja z listingiem;
8. rozszerzenie na wyniki skanera.

Ruch wykresowy ma klasę P0/`INTERACTIVE_MARKET`.

### R7 — Integracja skaner → listing → wykres — `PLANNED`

Cel: kliknięcie spółki na liście ładuje właściwe dane i pokazuje wykres oraz wynik skanera.

Wymagania: P0, last-good, jawny wiek danych, brak zapisu/sieci w nieuprawnionych GET-ach, obsłużone błędy providera i spójny kontrakt identyfikatora spółki.

### R8 — Alarmy i analiza końcowa — `PLANNED`

Cel: zdefiniowane, testowalne alarmy powiązane z wynikiem, etapem i confidence oraz finalny UX interpretacji.

Warunek: reguły alarmów muszą zostać odzyskane lub zatwierdzone decyzją użytkownika.

### R9 — Finalna akceptacja systemu — `PLANNED`

Cel: end-to-end acceptance, dokumentacja operatora, rollbacki, pełne FINAL-AS-BUILT i zamrożony release.

---

## 7. Obowiązkowy workflow każdej zmiany

Każdy sprint i każdy pakiet musi przejść dokładnie:

```text
SPEC
→ AUDIT
→ CONFLICT REPORT
→ USER DECISIONS
→ IMPLEMENTATION CONTRACT
→ SMALL PACKAGE
→ TEST
→ ACCEPTANCE
→ NEXT PACKAGE
```

### 7.1. SPEC

Musi zawierać: cel, zakres, poza zakresem, stan wejściowy, wymagania, ograniczenia, kryteria akceptacji, rollback assumptions, dowody potrzebne do potwierdzenia i listę `UNVERIFIED`.

### 7.2. AUDIT

Read-only sprawdzenie rzeczywistego kodu, danych, konfiguracji, procesów i dokumentów. Audit nie może zmieniać produkcji ani „przy okazji naprawiać”.

### 7.3. CONFLICT REPORT

Każda sprzeczność między SPEC, kodem, testami, dokumentacją i starszymi decyzjami musi zostać wypisana. Brak konfliktów także musi być jawnie zaraportowany.

### 7.4. USER DECISIONS

Model nie podejmuje po cichu decyzji zmieniających architekturę, zachowanie produktu, dane, wersję, priorytety ani zakres. Każda decyzja otrzymuje trwałe ID, uzasadnienie i skutki.

### 7.5. IMPLEMENTATION CONTRACT

Musi wskazywać dokładne pliki, dozwolone zmiany, zakazane zmiany, testy, backup, rollback, kryteria STOP, package ID i końcowy format raportu.

### 7.6. SMALL PACKAGE

Jedna paczka realizuje jeden zatwierdzony cel. Nie łączy nowych funkcji, refaktoru, migracji i poprawek niezwiązanych z celem.

### 7.7. TEST I ACCEPTANCE

Test musi być wykonany realnie tam, gdzie środowisko na to pozwala. „Test napisany” nie oznacza `PASS`. Acceptance wymaga dowodów, wyników, akceptacji użytkownika i archiwum.

### 7.8. NEXT PACKAGE

Następna paczka rozpoczyna się dopiero po zamknięciu poprzedniej. Wyjątek wymaga jawnej decyzji i udokumentowania ryzyka.

---

## 8. STOP rule

Jeżeli podczas preflightu, implementacji, instalacji, restartu, health checku, live testu albo audytu pojawi się nowy `FAIL`:

1. `STOP`;
2. nie twórz automatycznie fixa, nowego release ani kolejnej paczki;
3. nie modyfikuj produkcji;
4. wykonaj wyłącznie read-only diagnosis;
5. zabezpiecz pełny wynik, logi i stan wejściowy;
6. sklasyfikuj problem;
7. przedstaw dowód, opcje i rekomendację;
8. czekaj na decyzję użytkownika;
9. nowa paczka dopiero po zatwierdzonym kontrakcie.

Dozwolone klasyfikacje:

- `ACTIVATION PROCEDURE DEFECT`;
- `TEST DEFECT`;
- `PRODUCTION DEFECT`;
- `ENVIRONMENTAL DEFECT`;
- `AUDIT/WRAPPER DEFECT`;
- `UNPROVEN`.

Jeżeli problem nie dotyczy aktywacji, pierwszą kategorię pomija się. Nie wolno wybierać kategorii bez dowodu.

---

## 9. Package isolation

Każda paczka musi mieć unikalny `PACKAGE_ID`, używany identycznie w folderze, instalatorze, README, raporcie, nagłówkach, logach, backupie i hashach.

Zasady:

- zero zależności od starych folderów Temp, fixów lub poprzednich paczek;
- paczka zawiera tylko pliki niezbędne do zatwierdzonego celu;
- źródło i target są jawne;
- instalator weryfikuje wersję, stan wejściowy i source drift przed zapisem;
- backup obejmuje tylko zmieniane pliki;
- żadna porażka nie może prowadzić do częściowego komunikatu sukcesu;
- każdy subprocess ma sprawdzony return code;
- żadna asercja nie może zaliczać pustego wyniku jako PASS, jeśli kontrakt wymaga danych;
- paczka przygotowana przez AI pozostaje `READY FOR LOCAL ...`, a nie `ACTIVATED`, dopóki użytkownik faktycznie jej nie wykona i nie zaakceptuje wyniku.

Preferowany ID aktywacji r599, o ile audit nie wykaże konfliktu:

`r599-MASSIVE-TRAFFIC-ACTIVATION-001`

---

## 10. Mandatory quality gate

Po **ostatnim zapisie** i przed wydaniem każdej paczki obowiązuje kolejność:

```text
LAST WRITE
→ py_compile EVERY .py
→ AST EVERY .py
→ invalid escape / SyntaxWarning / static / sanity
→ tests
→ package integrity
→ hashes
→ FREEZE
```

Rozwinięcie obowiązkowego gate:

1. `py_compile` każdego finalnego `.py` właściwym interpreterem projektu;
2. `ast.parse` każdego finalnego `.py`;
3. `-W error::SyntaxWarning` tam, gdzie właściwe;
4. scan `invalid escape`;
5. undefined names i missing imports;
6. use-before-assignment i błędy shadowingu;
7. exact flag review;
8. exact VERSION review;
9. exact PACKAGE_ID review;
10. exact path review;
11. kontrola nazw plików, funkcji, zmiennych i env;
12. kontrola quoting i przepływu `.bat`;
13. kontrola wszystkich return codes;
14. kontrola propagacji PASS/FAIL;
15. kontrola backupu i rollbacku;
16. kontrola read-only status tools;
17. kontrola lazy-create;
18. kontrola SQLite w trybie bezpiecznym/read-only tam, gdzie wymagane;
19. kontrola procesu/PID i zakaz vacuous PASS;
20. weryfikacja dokładnego diffu;
21. self-test/dry-run instalatora;
22. symulacja rollbacku;
23. realne testy fixture/integration dostępne w środowisku;
24. kontrola kompletności i izolacji paczki;
25. wygenerowanie hashy;
26. `FREEZE`.

### 10.1. Manual typo pass

`py_compile PASS` nie oznacza braku literówek. Finalne pliki trzeba przeczytać linia po linii i sprawdzić dokładne identyfikatory, ścieżki, quotes, brackets, colons, commas, commands, output labels i return codes.

### 10.2. LAST WRITE / HASH rule

Jeżeli po compile, AST, testach, review albo hashach zmieni się choć jeden bajt, odpowiednie wyniki są nieważne. Po zmianie po `HASHES` należy ponownie wykonać quality gate, testy, package integrity, hashe i FREEZE. Nie wolno poprawiać nawet README po freeze bez ponowienia wymaganych etapów.

### 10.3. Windows/BAT contract dla paczek, które używają BAT

- ASCII;
- CRLF only;
- NO BOM;
- ścieżki budowane z `%~dp0`;
- pełne quoting;
- interpreter projektu `.venv`;
- zero fallbacku do `py`, `py -3`, `python`, `python3`;
- nie wpisywać literalnie ścieżki projektu w BAT, jeśli może zostać wyprowadzona z lokalizacji paczki;
- nie mylić `backend\.venv` z `backend.venv`.

---

## 11. Archiwum sprintów i Definition of Done

### 11.1. Zasada bezwzględna

> Sprint nie jest zakończony, dopóki nie istnieje kompletne archiwum sprintu i `FINAL-AS-BUILT-SPEC.md`.

### 11.2. Minimalna zawartość archiwum sprintu

```text
01-SPEC.md
02-AUDIT.md
03-CONFLICT-REPORT.md
04-DECISIONS.md
05-IMPLEMENTATION-CONTRACT.md
06-CHANGES.md
07-TESTS-AND-RESULTS.md
08-ACCEPTANCE.md
09-FINAL-AS-BUILT-SPEC.md
10-ROLLBACK.md
11-NEXT-STEPS.md
HASHES.txt
```

Dla UI i wykresów dodatkowo:

```text
REFERENCES/
CALIBRATION.md
ACCEPTED-REFERENCE.*
```

Nazwy mogą zachować starszą numerację, jeżeli istniejące archiwum już ją ma, ale semantycznie żaden element nie może zniknąć.

### 11.3. FINAL-AS-BUILT-SPEC

Dokument opisuje to, co faktycznie istnieje po wszystkich poprawkach i kalibracjach, a nie pierwotny zamiar. Musi zawierać:

- zakres rzeczywiście wdrożony;
- zakres niewdrożony;
- finalną architekturę i przepływy;
- finalne parametry i konfiguracje;
- schema/API/kontrakty danych;
- listę zmienionych plików;
- zachowanie UI;
- obsługę błędów i last-good;
- wykonane testy z wynikami;
- znane ograniczenia;
- backup i rollback;
- hashe zamrożonych artefaktów;
- status akceptacji i datę;
- odwołania do dowodów.

### 11.4. Definition of Done

Sprint nie jest `DONE` bez:

- spełnionych kryteriów akceptacji;
- realnych wyników testów;
- decyzji `ACCEPTED`;
- FINAL-AS-BUILT;
- rollbacku;
- hashy;
- aktualizacji MASTER;
- aktualizacji `STAN-AKTUALNY.md`;
- aktualizacji roadmapy i rejestru decyzji;
- zapisania wszystkich referencji i logów w archiwum.

---

## 12. Docelowa struktura repozytorium i ARCHIWUM

Poniższa struktura jest kontraktem organizacyjnym. Po audycie istniejącego repo może zostać dopasowana wyłącznie jawnie, bez przenoszenia lub kasowania dowodów przed wykonaniem backupu.

```text
Skaner-wykresow/
├── MASTER-PROJEKT.md
├── STAN-AKTUALNY.md
├── ROADMAPA.md
├── ZASADY-PROJEKTU.md
├── DECYZJE-PROJEKTOWE.md
├── REJESTR-ARTEFAKTOW.md
├── ARCHIWUM/
│   ├── r595/
│   ├── r596/
│   ├── r597/
│   ├── r598/
│   ├── r599/
│   │   ├── 01-SPEC.md
│   │   ├── 02-AUDIT.md
│   │   ├── 03-CONFLICT-REPORT.md
│   │   ├── 04-DECISIONS.md
│   │   ├── 05-IMPLEMENTATION-CONTRACT.md
│   │   ├── 06-CHANGES.md
│   │   ├── 07-TESTS-AND-RESULTS.md
│   │   ├── 08-ACCEPTANCE.md
│   │   ├── 09-FINAL-AS-BUILT-SPEC.md
│   │   ├── 10-ROLLBACK.md
│   │   ├── 11-NEXT-STEPS.md
│   │   └── HASHES.txt
│   ├── PROJECT-RECOVERY-001/
│   ├── SKANER-LISTING/
│   │   ├── RECOVERY-SOURCES.md
│   │   ├── SPEC.md
│   │   ├── UI-SPEC.md
│   │   ├── FINAL-AS-BUILT-SPEC.md
│   │   └── REFERENCES/
│   ├── WYKRESY/
│   │   ├── RECOVERY-SOURCES.md
│   │   ├── SPEC.md
│   │   ├── CALIBRATION.md
│   │   ├── FINAL-AS-BUILT-SPEC.md
│   │   └── REFERENCES/
│   └── ROZMOWY/
├── DOCS/
│   ├── ARCHITEKTURA.md
│   ├── BAZY-DANYCH.md
│   ├── API.md
│   └── PROCESS-TOPOLOGY.md
└── backend/
```

Lokalny projekt `C:\Skaner wykresów` został odnaleziony, zaudytowany i zamrożony. Powyższa struktura dokumentacji została w nim zainstalowana dla produktu OLD. Nowy produkt otrzyma odrębną strukturę dopiero w `C:\SKOOP Skaner wykresów`; nie wolno mieszać obu repozytoriów.

---

## 13. Rejestr artefaktów i załączników

### 13.1. Reguła

MASTER nie osadza bezpośrednio dużych grafik, ZIP-ów, baz, logów ani eksportów rozmów. Każdy artefakt jest zapisany jako oddzielny plik i zarejestrowany z dokładną ścieżką, statusem oraz hashem.

### 13.2. Wymagane pola rejestru

| Pole | Znaczenie |
|---|---|
| `ARTIFACT_ID` | trwały unikalny identyfikator |
| Obszar | r599 / skaner / listing / wykresy / alarmy / rozmowy |
| Typ | kod / dokument / screenshot / log / DB snapshot / ZIP / raport |
| Ścieżka | ścieżka względna w repo lub jawna ścieżka zewnętrzna |
| Źródło | skąd artefakt pochodzi |
| Data | data utworzenia/pozyskania, jeśli znana |
| Status | CONFIRMED / PARTIAL / UNVERIFIED / TO RECOVER |
| Hash | SHA-256 po pozyskaniu |
| Powiązany sprint | ID sprintu |
| Uwagi | znaczenie, ograniczenia, relacja do innych dowodów |

### 13.3. Znane artefakty do odzyskania

| ARTIFACT_ID | Opis | Docelowa ścieżka | Status |
|---|---|---|---|
| `ART-UI-SCANNER-001` | screenshot własnego dark UI z HUMA | `ARCHIWUM/SKANER-LISTING/REFERENCES/` | `TO RECOVER` |
| `ART-TV-ADTN` | referencja TradingView ADTN | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-AIRO` | referencja TradingView AIRO | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-AMZN` | referencja TradingView AMZN | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-CRM` | referencja TradingView CRM | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-DYN` | referencja TradingView DYN | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-FIG` | referencja TradingView FIG | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-GLW` | referencja TradingView GLW | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-TV-RBLX` | referencja TradingView RBLX | `ARCHIWUM/WYKRESY/REFERENCES/` | `TO RECOVER` |
| `ART-CHART-GENERATOR` | lokalny generator, testy i konfiguracje | `ARCHIWUM/WYKRESY/RECOVERY-SOURCES/` lub indeks ścieżki źródłowej | `TO RECOVER` |
| `ART-R599-AUDIT` | pełny wynik `PASS 181 / FAIL 0` | `ARCHIWUM/r599/07-TESTS-AND-RESULTS.md` | `PARTIAL` — wynik znany, plik źródłowy do odzyskania |
| `ART-CONVERSATION-001` | eksport rozmowy „Skaner sygnałów kupna” | `ARCHIWUM/ROZMOWY/` | `TO RECOVER` |

Dwóch brakujących tickerów z grupy dziesięciu nie wolno zgadywać.

### 13.4. Procedura pozyskania artefaktu

1. kopiuj w trybie zachowującym oryginał;
2. nie modyfikuj źródła przed inwentaryzacją;
3. zapisz rozmiar, daty i hash SHA-256;
4. nadaj `ARTIFACT_ID`;
5. zapisz relację do sprintu i decyzji;
6. oznacz, co artefakt rzeczywiście dowodzi;
7. nie podnoś statusu na `CONFIRMED`, jeżeli artefakt potwierdza tylko część ustalenia.

---

## 14. Rejestr sprintów — stan początkowy

| Sprint/release | Status | Potwierdzony wynik | Archiwum |
|---|---|---|---|
| r595 / C0 | `RESULT CONFIRMED / ARCHIVE TO RECOVER` | `119 PASS / 0 FAIL` według zaakceptowanego pakietu źródłowego; surowy raport `TO RECOVER` | `ARCHIWUM/r595/` — do odzyskania |
| r596 / C1 | `RESULT CONFIRMED / ARCHIVE TO RECOVER` | `90 PASS / 0 FAIL`; surowy raport `TO RECOVER` | `ARCHIWUM/r596/` |
| r597 / C2 | `RESULT CONFIRMED / ARCHIVE TO RECOVER` | `189 PASS / 0 FAIL`; surowy raport `TO RECOVER` | `ARCHIWUM/r597/` |
| CORE | `RESULT CONFIRMED / ARCHIVE TO RECOVER` | `47 OK / 0 BŁĄD`; surowy raport `TO RECOVER` | archiwum do odzyskania |
| r598 | `PARTIAL` | `177 PASS / 0 FAIL`, acceptance gates `112 / 0 FAIL`, run telemetry `20260819T200429Z-5c74e9`; surowe artefakty i pełny AS-BUILT `TO RECOVER` | `ARCHIWUM/r598/` |
| r599 | `ACCEPTED + ACTIVATED` | VERSION `2026-08-21-r599`, audit `PASS 181 / FAIL 0`, manager ON, telemetry OFF | `ARCHIWUM/R599-MASSIVE-TRAFFIC-ACTIVATION-001/` |
| r599 activation | `ACCEPTED` | live OVERALL PASS po około 20 min, 1 PID, provider DB healthy, 429=0 | `ARCHIWUM/R599-MASSIVE-TRAFFIC-ACTIVATION-001/` |
| PROJECT-RECOVERY-001 | `FROZEN` | V3 6×5 TF, Cykle 1D, referencje, testy, 59 hashy PASS | `ARCHIWUM/PROJECT-RECOVERY-001/` |

W rozmowie pojawiały się FIX-009 i FIX-010 związane z soft-importem. Końcowy stan r599 potwierdza wdrożenie FIX-010 i pełny PASS, ale szczegółowe archiwa obu fixów są `TO RECOVER`.

---

## 15. Procedura rozpoczęcia każdej nowej sesji ChatGPT/Claude

### 15.1. Obowiązkowa kolejność czytania

Przed analizą, propozycją zmiany lub napisaniem kodu model musi przeczytać w całości:

1. `MASTER-PROJEKT.md`;
2. `STAN-AKTUALNY.md`;
3. `ZASADY-PROJEKTU.md`;
4. `DECYZJE-PROJEKTOWE.md`;
5. odpowiedni `FINAL-AS-BUILT-SPEC.md` poprzedniego zaakceptowanego sprintu;
6. SPEC aktualnego sprintu;
7. Implementation Contract aktualnej paczki, jeżeli istnieje;
8. powiązane artefakty wskazane w rejestrze.

Minimalne wymaganie użytkownika wskazuje MASTER + STAN-AKTUALNY + odpowiedni AS-BUILT; pozostałe pliki są obowiązkowym rozszerzeniem, jeżeli istnieją.

### 15.2. Session opening report

Po lekturze model ma najpierw zwrócić krótki raport:

```text
SESSION CONTEXT LOADED

CURRENT VERSION:
<dokładna>

CURRENT ACCEPTED STATE:
<dokładny>

CURRENT PACKAGE/SPRINT:
<ID lub NONE>

MANAGER:
ON/OFF/UNVERIFIED

NEXT AUTHORIZED STEP:
<dokładny>

FILES READ:
<lista>

CONFLICTS:
NONE / <lista>

UNVERIFIED / TO RECOVER:
<lista istotna dla zadania>

WRITE AUTHORIZATION:
YES/NO — z czego wynika
```

### 15.3. Zakazy dla AI

Model nie może:

- rekonstruować brakujących decyzji z pamięci;
- uznać treści rozmowy za ważniejszą od frozen AS-BUILT i kodu;
- rozpocząć implementacji bez audytu i zaakceptowanego kontraktu;
- modyfikować plików podczas read-only recovery;
- łączyć pakietów;
- naprawiać nowego FAIL bez diagnozy i decyzji;
- raportować PASS dla niewykonanego testu;
- podawać nieistniejących endpointów, procesów, tabel lub nazw plików;
- uznać załącznika za odzyskany, dopóki nie jest zapisany, zindeksowany i zahashowany.

### 15.4. Zamknięcie sesji/sprintu

Przed zakończeniem pracy model musi wskazać:

- co faktycznie zmieniono;
- co przetestowano i z jakim wynikiem;
- czego nie zweryfikowano;
- status acceptance;
- gdzie znajduje się archiwum;
- czy zaktualizowano MASTER i STAN-AKTUALNY;
- dokładnie jeden następny krok.

---

## 16. Otwarte kwestie i recovery backlog

### P0 — przed aktywacją managera

- odzyskać/zweryfikować aktualne frozen hashe r599;
- potwierdzić dokładną topologię procesów i kolejność restartu;
- potwierdzić, że jedyną zmianą jest flaga w `config.py`;
- rozstrzygnąć czas kontrolowanego live testu;
- skompletować archiwum r599;
- `DONE` — utworzyć `STAN-AKTUALNY.md`.

### P1 — przed mechanizmem skanera

- pełny audit `companies.db`;
- odzyskać mapowanie 20/129 i `listing_scope`;
- `PARTIAL` — odzyskano specyfikację `Cykle 1D`; pozostały scoring i zakładki są `TO RECOVER`;
- zdefiniować stabilny kontrakt danych skanera;
- `DONE` — odzyskano nazwy P1/P2/P3; pełne mapowanie wszystkich caller contexts/operation IDs do priorytetów nadal `TO RECOVER`.

### P2 — przed listingiem i wykresami

- `DONE` — odzyskano screenshoty własnego UI i listingu;
- `PARTIAL` — odzyskano UI-SPEC `Cykle 1D`, pełna specyfikacja pozostałych zakładek jest otwarta;
- `DONE` — zinwentaryzowano generator wykresów read-only;
- `DONE` — odzyskano finalny zestaw 6 i walidacyjny zestaw 19; pierwotna dziesiątka pozostaje historycznym `TO RECOVER`;
- `PARTIAL` — zachowano referencje TradingView, formalne pary akceptacyjne 1:1 pozostają otwarte;
- `DONE` — utworzono wykresowy `FINAL-AS-BUILT-SPEC.md`.

### P3 — przed alarmami i finalnym UX

- odzyskać/ustalić reguły alarmów;
- zdefiniować confidence/skuteczność;
- określić trwałość, deduplikację i wygaszanie alarmów;
- przeprowadzić end-to-end acceptance.

Uwaga: P0–P3 w tej sekcji oznaczają priorytet backlogu dokumentacyjnego, nie klasy ruchu Massive Traffic Manager. Nie wolno mieszać tych dwóch znaczeń.

---

## 17. Zasady aktualizacji MASTER-a

MASTER aktualizuje się:

- po każdej zaakceptowanej decyzji zmieniającej kierunek;
- po każdym zakończonym sprincie;
- po aktywacji/rollbacku;
- po odzyskaniu ważnego artefaktu;
- po zmianie statusu `UNVERIFIED/TO RECOVER`;
- po zmianie roadmapy;
- po wykryciu konfliktu wpływającego na źródło prawdy.

Każda aktualizacja musi:

1. zachować historię decyzji;
2. zmienić tylko sekcje poparte dowodem;
3. zaktualizować status i odwołanie do artefaktu;
4. nie kopiować do MASTER-a dużych logów lub obrazów;
5. wskazać odpowiedni FINAL-AS-BUILT;
6. przejść review spójności z `STAN-AKTUALNY.md`;
7. zostać objęta hashem/commitem zgodnie z procesem repozytorium.

Repozytorium online może pełnić rolę archiwum i historii, ale dostęp ChatGPT/Claude do prywatnego repo nie jest gwarantowany. Każda sesja musi otrzymać rzeczywisty dostęp albo komplet wymaganych plików wejściowych.

---

## 18. Aktualna deklaracja źródła prawdy

Na dzień 2026-08-21 potwierdzony stan brzmi:

```text
PROJECT:
Skaner wykresów

VERSION:
2026-08-21-r599

AUDIT:
PASS 181 / FAIL 0

MASSIVE TRAFFIC MANAGER:
ACCEPTED + ACTIVATED
CURRENT CONFIG: ON
LIVE ACCEPTANCE: PASS AFTER ~20 MIN

PROVIDER STATE DB:
PRESENT; INTEGRITY OK; USER_VERSION 1; WAL

BUSINESS DB MUTATION DURING AUDIT:
ZERO

CURRENT STAGE:
r599 IS HISTORICAL ACCEPTED STATE;
LEGACY RUNTIME STOPPED AND NOT TO RESTART;
0 LEGACY PROCESSES; 0 PORT 8000 LISTENERS;
PROJECT AND DATA SNAPSHOTTED AS
C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001;
OLD IS REFERENCE/READ-ONLY AND MUST HAVE ZERO MASSIVE TRAFFIC

CURRENT LOCAL SHELL:
C:\SKOOP Skaner wykresów;
SKOOP PLACEHOLDER + STOCK SCANNER OLD READ ONLY;
LAUNCHERS REDIRECTED; 127.0.0.1 ONLY;
MASSIVE DISABLED; LEGACY WORKERS DISABLED;
NO FURTHER DOWNLOADS ON THIS COMPUTER BY D-007

NEXT AUTHORIZED PROGRAM STAGE AFTER ACCEPTANCE:
SKOOP-FOUNDATION-002 OR USER-SELECTED SMALL PACKAGE

SCANNER/LISTING/CHARTS:
V3 CHARTS AND CYCLES 1D RECOVERED;
MAIN-UI INTEGRATION NOT IMPLEMENTED;
OTHER AREAS PARTIAL / TO RECOVER

MISSING DETAIL POLICY:
UNVERIFIED / TO RECOVER — NEVER GUESS
```

---

## 19. Historia zmian dokumentu

| Data | Wersja dokumentu | Zmiana | Status |
|---|---|---|---|
| 2026-08-21 | 0.1 | Pierwszy MASTER utworzony z dostępnej rozmowy; r599, architektura, workflow, roadmapa i recovery register | DRAFT DO REVIEW |
| 2026-08-21 | 0.2 | PROJECT-RECOVERY-001: stan runtime, V3 6×5 TF, 19-symbol validation, Cykle 1D, V4.4, artefakty i granica integracji | RECOVERED WITH KNOWN GAPS |
| 2026-08-21 | 0.3 | Ponowny audit: config manager ON, provider_state obecny i poprawny, runtime OFF; acceptance aktywacji do odzyskania | CURRENT STATE RECONCILIATION REQUIRED |
| 2026-08-21 | 0.4 | Odzyskano MASTER użytkownika: r599 ACTIVATION ACCEPTED, live PASS po 20 min; zapisano finalny AS-BUILT aktywacji | CONFIRMED |
| 2026-08-21 | 0.5 | Scalono pełny pakiet `Skaner-sygnalow-kupna-ARCHIWUM.zip`; zapisano provenance, priorytety P1–P3, kontrakt baz V4.4 i historyczne wyniki release bez udawania odzyskania surowych raportów | CONFIRMED WITH DECLARED GAPS |
| 2026-08-21 | 0.6 | D-006: zatrzymano i zamrożono stary runtime, wykonano snapshot projektu/danych oraz backupy SQLite, zastąpiono restart OLD roadmapą niezależnego SKOOP | CONFIRMED / LEGACY FROZEN |
| 2026-08-22 | 0.7 | D-007: zaakceptowano istniejącą próbkę bez dalszego pobierania; zainstalowano lokalny SKOOP placeholder i Stock Scanner OLD read-only; launchery przekierowane | CONFIRMED / OFFLINE SHELL INSTALLED |

---

## 20. Kanoniczny system pracy i przechowywania

### 20.1. Lokalizacja

Kanoniczną lokalizacją dokumentacji zamrożonego produktu OLD jest:

```text
C:\Skaner wykresów\DOKUMENTACJA
```

Katalog zarządzany przez Codex jest stagingiem/roboczą kopią recovery, a nie docelowym jedynym magazynem projektu.

Zewnętrznym dowodem freeze OLD jest `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001`. Lokalny fundament/placeholder nowego produktu znajduje się w `C:\SKOOP Skaner wykresów`. Pełny model danych nowego SKOOP nadal nie został utworzony.

### 20.2. Obowiązkowe dokumenty wejściowe

1. `DOKUMENTACJA/MASTER-PROJEKT.md`;
2. `DOKUMENTACJA/STAN-AKTUALNY.md`;
3. `DOKUMENTACJA/00-STEROWANIE/ZASADY-PROJEKTU.md`;
4. `DOKUMENTACJA/04-DECYZJE/DECYZJE-PROJEKTOWE.md`;
5. właściwy AS-BUILT;
6. aktywna paczka i ostatni handoff.

### 20.3. Flow

```text
SPEC → AUDIT → CONFLICT REPORT → USER DECISIONS →
IMPLEMENTATION CONTRACT → SMALL PACKAGE → TEST →
ACCEPTANCE → FINAL-AS-BUILT → HASHES → FREEZE →
ARCHIWUM → GIT COMMIT/TAG → NEXT PACKAGE
```

### 20.4. Wersjonowanie

- produkt: `YYYY-MM-DD-rNNN`;
- dokumentacja: `DOCS-YYYY-MM-DD-NN`;
- paczka: `<AREA>-YYYYMMDD-###`;
- decyzje i rejestry: append-only;
- frozen archiwum: immutable;
- remote/push: wyłącznie po osobnej decyzji użytkownika.

### 20.5. AI i dostęp

ChatGPT/Codex/Claude nie mają gwarantowanej wspólnej pamięci ani automatycznego dostępu do prywatnego repozytorium. Ciągłość zapewniają pliki, protokół startowy oraz faktyczne udostępnienie folderu/repozytorium. Sekrety i bazy nigdy nie wchodzą do Git ani dokumentacji.

### 20.6. Historia

| Data | Wersja dokumentacji | Zmiana | Decyzja |
|---|---|---|---|
| 2026-08-21 | DOCS-2026-08-21-01 | kompletny system flow, dostępu, aktualizacji, sesji AI, paczek i Git | D-003 |
| 2026-08-21 | DOCS-2026-08-21-02 | import i scalenie archiwum „Skaner sygnałów kupna”; conflict report, provenance i rozpoczęcie kolejnej fazy recovery | D-005 |
| 2026-08-21 | DOCS-2026-08-21-03 | freeze OLD, snapshot projektu i danych, handoff Claude oraz roadmapa niezależnego SKOOP | D-006 |
| 2026-08-22 | DOCS-2026-08-22-01 | lokalna powłoka SKOOP/OLD, brak dalszych pobrań i przekierowanie launcherów | D-007 |

---

## 21. Rozdzielenie OLD i SKOOP — obowiązujące od D-006

### 21.1. `Stock Scanner OLD`

- źródło: `C:\Skaner wykresów`;
- dane źródłowe: `C:\skaner-dane`;
- status: `FROZEN / LEGACY / NOT TO RESTART`;
- snapshot: `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001`;
- zastosowanie: recovery, porównania, inspiracje, testy, statyczne demo;
- zabronione: Massive, odświeżanie, worker non-stop, scheduler, zapis do starych baz, przypadkowy restart;
- OLD UI czyta zamrożone dane read-only i jest technicznie odseparowane od starego runtime — `DONE 2026-08-22`;
- pełny żywy skaner z pełniejszymi zasobami pozostaje na drugim komputerze; brak automatycznej synchronizacji.

### 21.2. `SKOOP Skaner wykresów`

- root: `C:\SKOOP Skaner wykresów`;
- planowany root danych: `C:\SKOOP-skaner-dane` — `DECISION REQUIRED`;
- status: `FOUNDATION PLACEHOLDER + OFFLINE OLD INSTALLED`;
- wersja powłoki: `2026-08-21-offline-old-001`;
- następna paczka: `SKOOP-FOUNDATION-002` albo zakres wskazany przez użytkownika;
- zasada: brak kopiowania całego starego backendu; odzyskiwany jest wyłącznie jawnie zaakceptowany kontrakt funkcjonalny;
- sekrety: klucz Massive wyłącznie poza dokumentacją, kodem, logami i Git;
- kolejność: foundation → Massive access → universe/resources → company model → listing → V3 charts → scanner mechanisms → alerts.

### 21.2.1. Obowiązujący kontrakt lokalnej powłoki — D-007

- jeden launcher otwiera `http://localhost:8000`;
- ekran początkowy: placeholder SKOOP;
- przełącznik: `Stock Scanner OLD`;
- OLD korzysta wyłącznie z `DATA-SQLITE-BACKUP` wcześniejszego freeze;
- SQLite: `mode=ro&immutable=1`, `query_only=ON`;
- bind: wyłącznie `127.0.0.1`;
- mutacje HTTP: `405 OFFLINE_READ_ONLY`;
- brak modułów Massive, starego `run.py`, scanner workerów i schedulerów;
- dalsze pobieranie na tym komputerze: `CANCELLED / NOT REQUIRED`;
- pełniejsze żywe dane: drugi komputer, bez automatycznej synchronizacji.

### 21.3. Źródło prawdy dla nowej sesji Claude/ChatGPT

Przed pracą nad SKOOP AI czyta w tej kolejności:

1. niniejszy `MASTER-PROJEKT.md`;
2. `STAN-AKTUALNY.md`;
3. `00-STEROWANIE/ZASADY-PROJEKTU.md`;
4. `04-DECYZJE/DECYZJE-PROJEKTOWE.md`, w szczególności D-006;
5. `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PACKAGE\FINAL-AS-BUILT-SPEC.md`;
6. `CLAUDE-PROCESS-OLD-FREEZE.md`;
7. `CLAUDE-ROADMAP-SKOOP.md`;
8. AS-BUILT odzyskanego V3 lub Cykle 1D tylko wtedy, gdy aktywna paczka ich dotyczy.

Brak dostępu do dowolnego dokumentu oznacza `BLOCKED / TO PROVIDE`, a nie zgodę na zgadywanie.

## 22. Korekta kontraktu Stock Scanner OLD — D-008

Obowiązujący kontrakt zastępuje wyłącznie implementację OLD opisaną w 21.2.1:

- nowy SKOOP jest widokiem domyślnym pod `localhost:8000`;
- kliknięcie `Stock Scanner OLD` otwiera oryginalny frontend r599 1:1 na 8001;
- OLD zachowuje wygląd, zakładki, panele, listingi, projekty wykresów,
  portfele, cykle, IPO, alerty historyczne i pozostałe lokalne zasoby;
- pełny kod OLD jest uruchamiany wyłącznie z roboczej kopii
  `C:\SKOOP Skaner wykresów\OLD-r599-1TO1`;
- immutable źródło pozostaje w `PROJECT-1TO1` i nie jest wykonywane;
- kopie baz runtime są otwierane immutable/query-only i mają hashe zgodne 3/3
  z `DATA-SQLITE-BACKUP`;
- dostępy Massive/Yahoo, workery i mutacje pozostają zablokowane;
- lokalne React/ReactDOM są częścią paczki, więc wygląd nie zależy od CDN;
- jedyne zmiany wizualne w OLD to oznaczenie `OLD/FROZEN` i przycisk powrotu
  do nowego SKOOP.

Zakaz „kopiowania całego starego backendu” z sekcji 21.2 nie obowiązuje dla
izolowanej, zamrożonej kopii demonstracyjnej OLD. Nadal obowiązuje dla kodu
nowego SKOOP: nowe mechanizmy nie mogą dziedziczyć logiki OLD automatycznie.

Dowód wykonania: `02-AS-BUILT/OLD-R599-1TO1-FROZEN-AS-BUILT.md`.


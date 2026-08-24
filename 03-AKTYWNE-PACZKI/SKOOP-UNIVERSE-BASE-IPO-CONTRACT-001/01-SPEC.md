# SPEC — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
STATUS: READY FOR USER DECISIONS
AREA: COMPANY-DATA
OWNER: USER
PRODUCT VERSION BEFORE: SKOOP FOUNDATION PLACEHOLDER / NO PRODUCT VERSION
TARGET VERSION: NO RUNTIME CHANGE — DATA CONTRACT ONLY
DOCS VERSION: DOCS-2026-08-23-01-DRAFT
```

## 1. Problem i oczekiwany rezultat

**Problem:** nowy SKOOP nie ma jeszcze zatwierdzonego kontraktu, który jednoznacznie
opisuje pełny katalog instrumentów, kwalifikację BASE, okno IPO oraz pola listingu.
Stary r599 łączył identyfikację spółki, wynik BASE, IPO i część profilu w jednej tabeli,
a część reguł jest sprzeczna z aktualnym kierunkiem produktu.

**Oczekiwany rezultat:** zatwierdzony logiczny kontrakt danych i zachowania UI, na
podstawie którego będzie można przygotować osobny `IMPLEMENTATION CONTRACT` dla
schematu nowego produktu. Dokument nie tworzy bazy, nie pobiera danych i nie uruchamia
Massive.

**Dlaczego teraz:** UNIVERSE, BASE i IPO są wejściem dla listingu, wykresów, strategii,
sygnałów i późniejszych alarmów. Błąd w tym kontrakcie powieliłby się we wszystkich
warstwach produktu.

## 2. In scope

- znaczenie i relacje `UNIVERSE`, `BASE` i `IPO`;
- jedna tożsamość instrumentu i brak duplikowania danych między zbiorami;
- obowiązkowe pola identyfikacji, klasyfikacji, wielkości i aktualności danych;
- statusy oraz powody kwalifikacji BASE;
- cykl życia IPO liczony w zamkniętych sesjach giełdowych;
- minimalny kontrakt pól listingu UNIVERSE/BASE/IPO;
- kontrakt braków, nieaktualnych danych, ostatniej poprawnej wersji i wersjonowania;
- kontrakt linków TradingView i Investing bez zmyślonych adresów;
- wymagania dla późniejszego powiązania z wykresami V3;
- kryteria akceptacji przyszłej implementacji kontraktu.

## 3. Out of scope

- klucz Massive, limity planu i jakiekolwiek żądania sieciowe;
- fizyczny schemat SQL, migracje i utworzenie nowych baz;
- implementacja importerów, workerów, API i UI;
- finalne wartości progów BASE;
- pobieranie pełnego UNIVERSE;
- integracja wykresów V3;
- strategie, scoring, sygnały, cykle i alarmy;
- uruchamianie lub modyfikowanie `Stock Scanner OLD`;
- modyfikowanie frozen archiwów i baz r599.

## 4. Źródła prawdy

| Źródło | Wersja/hash | Zakres |
|---|---|---|
| `MASTER-PROJEKT.md` | SHA-256 `BEB2810F...21CA0C40` | workflow, roadmapa, architektura, statusy wiedzy |
| `STAN-AKTUALNY.md` | SHA-256 `02733B03...0309AB8` | stan OLD/SKOOP i zakaz dalszych pobrań OLD |
| `ARCHITEKTURA-ZASOBOW-V4.4-FINAL.txt` | SHA-256 `B9C4BDB3...C45AFFA6` | docelowy podział zasobów, workerów, TTL i publikacji |
| `WYKRESY/FINAL-AS-BUILT-SPEC.md` | SHA-256 `7BD1FB15...C7D59F2` | payload V3 i pięć TF |
| `SKANER-CYKLE-1D/RECOVERED-SPEC.md` | SHA-256 `6A559D38...1E07F51` | odzyskane pola listingu analitycznego |
| frozen `scanner.db` | SHA-256 `A1D2512A...BD925D8` | rzeczywista historyczna struktura i pokrycie danych |
| frozen `market.db` | SHA-256 `659AD899...335FDB` | rzeczywista historyczna warstwa świec |
| bieżące wymagania użytkownika | 2026-08-22/23 | jeden pełny UNIVERSE, BASE obserwacyjne, IPO 180 sesji, listing i wykresy |

Pełne ścieżki i wyniki read-only znajdują się w `02-AUDIT.md`.

## 5. Model pojęciowy

### 5.1. Jedna tożsamość instrumentu

Każdy instrument ma jeden niezmienny wewnętrzny `instrument_id`. Symbol giełdowy nie
może być jedynym kluczem, ponieważ może zmienić się, powtórzyć na innej giełdzie albo
zostać ponownie użyty.

Minimalna unikalność zewnętrzna musi uwzględniać co najmniej dostawcę, symbol dostawcy
i rynek/MIC. Dokładny format `instrument_id` jest decyzją techniczną przyszłego
Implementation Contract.

### 5.2. Relacje zbiorów

`UNIVERSE` jest katalogiem wszystkich instrumentów objętych zatwierdzonym zakresem.
`BASE` i `IPO` są niezależnymi, wersjonowanymi statusami/widokami tego katalogu.

| Przypadek | UNIVERSE | BASE | IPO |
|---|---:|---:|---:|
| zwykła spółka zakwalifikowana | 1 | 1 | 0 |
| nowe IPO spełniające BASE | 1 | 1 | 1 |
| nowe IPO niespełniające lub oczekujące na BASE | 1 | 0/PENDING | 1 |
| spółka poza BASE | 1 | 0 | 0 |

Nie wolno kopiować profilu, linków ani świec do osobnych tabel „universe”, „base” i
„ipo”. Widoki odwołują się do tego samego `instrument_id`.

### 5.3. Warstwy odpowiedzialności

| Warstwa logiczna | Właściciel danych | Znaczenie |
|---|---|---|
| tożsamość/universe | `core.db` + `companies.db` docelowo | istnienie instrumentu i jego stabilna identyfikacja |
| BASE | `core.db/base_state` docelowo | wynik reguł kwalifikacji; zero sieci podczas oceny |
| profil/IPO/linki | `companies.db` docelowo | klasyfikacja, wielkość, debiut i kanoniczne linki |
| świece | `market.db` docelowo | jedno wspólne źródło danych wykresowych |

Fizyczny schemat i nazwy tabel wymagają późniejszego kontraktu implementacyjnego.

## 6. Kontrakt pól

### 6.1. Tożsamość i członkostwo UNIVERSE

| Pole logiczne | Wymaganie | Brak | Uwagi |
|---|---|---|---|
| `instrument_id` | obowiązkowe, trwałe | rekord niepublikowalny | nie symbol jako jedyny klucz |
| `provider_ticker` | obowiązkowe | rekord niepublikowalny | dokładny ticker źródła |
| `symbol_display` | obowiązkowe | rekord niepublikowalny | symbol dla użytkownika |
| `name` | obowiązkowe docelowo | `MISSING`, nigdy symbol jako fałszywa nazwa | fallback może być tylko jawnie oznaczony |
| `primary_exchange_code` | wymagane | `UNRESOLVED` | kod kanoniczny, nie dowolny tekst |
| `mic` | preferowane | `UNRESOLVED` | potrzebne do rozróżnienia instrumentu i linków |
| `country` / `locale` | wymagane dla pełnego zakresu | `UNRESOLVED` | zakres zgodny z zaakceptowanym UD-01; wartość konkretnego rekordu nadal wymaga źródła |
| `currency` | obowiązkowe dla wartości finansowych | `UNRESOLVED` | nie wolno zakładać USD |
| `asset_type` | obowiązkowe | `UNRESOLVED` | jawna klasyfikacja wymagana przez zaakceptowane UD-01 |
| `active` | obowiązkowe | `UNVERIFIED` | delisting nie usuwa historii |
| `source` | obowiązkowe | rekord niepublikowalny | pochodzenie pola/rekordu |
| `source_updated_at` | obowiązkowe | `MISSING` | czas źródła, jeśli dostępny |
| `published_version` | obowiązkowe | rekord niepublikowalny | bezpieczne udostępnienie sprawdzonej wersji |

### 6.2. Klasyfikacja

| Pole | Wymaganie | Status braku |
|---|---|---|
| `sector_code`, `sector_name` | wymagane docelowo | `UNRESOLVED` |
| `industry_code`, `industry_name` | wymagane docelowo | `UNRESOLVED` |
| `sub_industry` | opcjonalne do czasu zatwierdzenia taksonomii | `MISSING` |
| `sic` | wymagane, jeśli źródło udostępnia | `MISSING` |
| `taxonomy_version` | obowiązkowe po mapowaniu | brak = klasyfikacja niekanoniczna |
| `classification_source` | obowiązkowe | brak = niepublikowalne jako zweryfikowane |
| `classification_updated_at` | obowiązkowe | `MISSING` |

Stare pola `sector`/`industry` nie są automatycznie uznawane za kanoniczne 20/129.
Mapowanie pozostaje `TO RECOVER/DECISION REQUIRED`.

### 6.3. Wielkość i dane ostatniej sesji

| Pole | Semantyka |
|---|---|
| `last_completed_session` | data ostatniej zamkniętej sesji właściwego rynku |
| `last_close_native` | cena zamknięcia w walucie instrumentu |
| `last_trade_price_native` | opcjonalna cena bieżąca; nie zastępuje zamknięcia |
| `day_volume_shares` | liczba akcji z ostatniej zamkniętej sesji |
| `day_turnover_native` | suma/estymacja obrotu w walucie instrumentu; metoda musi być jawna |
| `day_turnover_usd` | wartość porównawcza po jawnie wersjonowanym FX |
| `adv20_usd` | średni/medianowy obrót 20 sesji; dokładna metoda do decyzji w regułach BASE |
| `market_cap_native` | kapitalizacja w walucie instrumentu |
| `market_cap_usd` | kapitalizacja porównawcza z jawnie zapisanym FX/as-of |
| `change_1d_pct` | zmiana ostatniej zamkniętej sesji |
| `data_status` | `READY`, `STALE`, `INCOMPLETE`, `ERROR` |
| `last_updated`, `version`, `source` | aktualność i pochodzenie bloku |

Brak wartości prezentujemy jako `—` wraz ze statusem. Nigdy jako `0`.

Zgodnie z zaakceptowanym UD-06:

- wartość źródłowa i kod waluty instrumentu są zachowane bez nadpisania;
- USD jest osobną wartością porównawczą z `fx_rate`, `fx_source`, `fx_as_of` i
  wersją metody przeliczenia;
- cena akcji jest domyślnie pokazywana w walucie notowania;
- kapitalizacja, obrót i ADV mogą być filtrowane/sortowane po wartości USD;
- prawy panel udostępnia wartość natywną oraz odpowiednik USD;
- dane historyczne używają kursu właściwego dla okresu, nie bieżącego kursu;
- brak właściwego FX oznacza `PENDING_FX`/brak wartości porównawczej, nigdy zero;
- UI umożliwia przełączenie widoku natywnego i porównawczego.

### 6.4. BASE

Minimalny kontrakt `base_state`:

- `instrument_id`;
- `base_status`;
- `reason_codes[]`;
- `ruleset_version`;
- `input_version`;
- `evaluated_at`;
- `effective_from`;
- `is_manual_override` i uzasadnienie, jeżeli override zostanie dopuszczony;
- historia zmiany statusu albo wersjonowany snapshot umożliwiający audyt.

Proponowane statusy:

- `QUALIFIED`;
- `NOT_QUALIFIED`;
- `PENDING_DATA`;
- `EXCLUDED_BY_SCOPE`;
- `UNVERIFIED`.

Minimalne powody diagnostyczne:

- `BASE_OK`;
- `PRICE_TOO_LOW`;
- `MARKET_CAP_TOO_LOW`;
- `ADV_TOO_LOW`;
- `MISSING_PRICE`;
- `MISSING_MARKET_CAP`;
- `MISSING_ADV`;
- `INSUFFICIENT_HISTORY`;
- `ASSET_TYPE_EXCLUDED`;
- `MARKET_EXCLUDED`;
- `INACTIVE_OR_DELISTED`.

Lista progów i formuł nie jest częścią tego SPEC i pozostaje do osobnej decyzji.
Ocena BASE nie wykonuje sieci i nie zmienia członkostwa UNIVERSE ani historii IPO.

Zgodnie z zaakceptowanym UD-03 brak ceny, kapitalizacji lub ADV daje
`base_status=PENDING_DATA` wraz z odpowiednim `reason_code`. Taki rekord pozostaje
w UNIVERSE, nie otrzymuje statusu `QUALIFIED` ani `NOT_QUALIFIED`, trafia do kolejki
uzupełniania i jest automatycznie oceniany ponownie po opublikowaniu poprawnych
danych wejściowych. Brak nie może zostać zapisany ani pokazany jako zero.

Pierwsza BASE powstaje zgodnie z zaakceptowanym UD-02:

1. pełny UNIVERSE zostaje pobrany i przechodzi raport kompletności/jakości;
2. proponowane warianty progów są liczone próbnie dla całego UNIVERSE;
3. raport pokazuje liczbę `QUALIFIED`, `NOT_QUALIFIED` i `PENDING_DATA` oraz powody;
4. próbny wynik nie nadaje jeszcze członkostwa BASE i nie uruchamia strategii;
5. użytkownik porównuje warianty i zatwierdza reguły/progi;
6. dopiero zaakceptowany ruleset tworzy pierwszą wersję `base_state`.

Nie kopiujemy statusów `base_ok` ani historycznych kwalifikacji r599. Mogą one
służyć wyłącznie do późniejszego porównania wyników, jeśli zostanie to jawnie
zlecone w osobnym audycie.

### 6.5. IPO

Minimalny kontrakt `ipo_state`:

- `instrument_id`;
- `debut_date_reported`;
- `first_trading_session`;
- `ipo_price` i waluta, jeżeli potwierdzone;
- `first_close`;
- `sessions_since_debut`;
- `ipo_window_status`: `IN_WINDOW`, `GRADUATED`, `UNVERIFIED`;
- `source`, `confidence/status`, `last_updated`, `version`.

Zgodnie z zaakceptowanym UD-04 po zamknięciu 180. właściwej sesji
`ipo_window_status` przechodzi do `GRADUATED` i spółka znika z aktywnego listingu
IPO. Następnie uruchamiana jest zwykła ocena BASE na aktualnym rulesecie:

- spółka spełniająca reguły pozostaje albo wchodzi do BASE;
- spółka niespełniająca reguł pozostaje tylko w UNIVERSE;
- istniejący status BASE nie jest odbierany wyłącznie z powodu końca IPO;
- sesja 181 nie nadaje BASE automatycznie.

Zgodnie z zaakceptowanym UD-05 wykresy IPO są aktualizowane następująco:

- każde aktywne IPO otrzymuje po sesji aktualny `1D` i przebieg od debiutu;
- IPO będące w BASE korzysta z pełnej regularnej aktualizacji BASE;
- IPO poza BASE nie utrzymuje stale pełnego intraday;
- kliknięcie spółki uruchamia T0 dla `30m`, `1H`, `2H` i `4H`, a wynik zostaje
  w cache z jawnym czasem aktualizacji;
- sygnał, obserwacja lub portfel uruchamia odpowiednio T1–T3 niezależnie od samego
  statusu IPO;
- nieaktualny albo niepełny wykres ma jawny status i nie udaje danych bieżących.

Okno IPO jest liczone wyłącznie według kalendarza właściwej giełdy i zamkniętych sesji.
Nie wolno liczyć dni kalendarzowych. Zachowanie na sesji 181 i relacja z BASE wymagają
potwierdzenia w UD-04.

### 6.6. Linki zewnętrzne

Każdy link musi mieć:

- `provider`: `TRADINGVIEW` albo `INVESTING`;
- identyfikator instrumentu w danym serwisie, jeżeli dostępny;
- pełny URL;
- `link_status`: `VERIFIED`, `NEEDS_REVIEW`, `UNRESOLVED`;
- `source`, `verified_at`, opcjonalnie `manual_override`.

Kolejność użycia: ręcznie zatwierdzona korekta → zweryfikowany URL → zweryfikowany
resolver giełda+symbol → `UNRESOLVED`. Wyszukiwarka po tickerze może być osobną akcją
`Szukaj`, ale nie może udawać prawidłowego bezpośredniego linku.

## 7. Kontrakt listingu

### 7.1. Widoki

- `UNIVERSE` — uproszczony listing zasobów, pełny katalog w zatwierdzonym zakresie;
- `BASE` — inwestycyjny listing spółek `base_status=QUALIFIED`, z układem rozwijanym
  na bazie sprawdzonego wyglądu OLD, ale bez kopiowania starej logiki;
- `IPO` — wyspecjalizowany listing `ipo_window_status=IN_WINDOW`, z polami
  dotyczącymi debiutu odzyskanymi z OLD;
- odznaki BASE i IPO mogą wystąpić jednocześnie w każdym widoku.

### 7.2. Listing UNIVERSE — audyt zasobów

Obowiązkowo: symbol, nazwa, giełda, kraj, sektor, branża, kapitalizacja, ostatnia
cena zamknięcia, wolumen ostatniej sesji, obrót ostatniej sesji, ADV20, liczba akcji
w obrocie oraz liczba akcji wyemitowanych (`shares_outstanding`) jako dwa różne pola,
zysk netto ostatniego raportowanego kwartału, zysk netto TTM/ostatnich 12 miesięcy,
status BASE, status IPO, kompletność oraz ostatnie udane odświeżenie.

Finanse dla pełnego UNIVERSE są blokiem P3 i nie mogą blokować publikacji katalogu.
Brak zysku pokazujemy jako `— / MISSING`, nigdy jako zero. Dokładna definicja
„zysku kwartalnego” i „zysku rocznego” musi wskazywać okres, walutę i źródło.

### 7.3. Listing BASE — widok inwestycyjny

Obowiązkowo: wszystkie podstawowe dane identyfikacyjne i finansowe dostępne dla
spółki, powody kwalifikacji BASE, aktualność, obrót/płynność, linki, miniwykres oraz
prawy panel z pełnym wykresem. Można odzyskać układ, kolejność pracy i ergonomię OLD,
ale nie wolno automatycznie przenosić starego scoringu, sygnałów ani alertów.

Kolumny strategii, cykli i sygnałów będą dodawane dopiero przez ich własne
zatwierdzone kontrakty.

### 7.4. Listing IPO — pola odzyskane z OLD

Potwierdzone pola referencyjne OLD:

- symbol, nazwa, giełda, sektor;
- data debiutu i liczba sesji od debiutu `X/180`;
- miniwykres ceny od debiutu;
- kapitalizacja;
- cena IPO, pierwsze zamknięcie i aktualna cena;
- zmiana pierwszego zamknięcia względem ceny IPO;
- zmiana aktualnej ceny względem IPO;
- wolumen w sztukach, obrót dzienny i średni obrót;
- RSI i MACD, gdy historia jest wystarczająca;
- zweryfikowane linki zewnętrzne;
- status danych i czas ostatniego udanego odświeżenia.

Przycisk BUY i stara logika inwestycyjna nie są częścią tego kontraktu.

### 7.5. Filtry i sortowanie

Wymagane: wyszukiwanie symbol/nazwa, giełda, kraj, sektor, branża, typ instrumentu,
przedziały ceny, kapitalizacji i obrotu, status/powód BASE, status IPO i zakres sesji,
kompletność/aktualność danych oraz stan wykresu.

Sortowanie musi działać po stronie zasobu/API. UI nie może wczytywać całych 9000+
rekordów w celu lokalnego sortowania.

### 7.6. Miniwykres i panel spółki

Listing nie renderuje pełnych wykresów dla wszystkich rekordów. Miniwykres korzysta z
gotowego lekkiego payloadu dla widocznych wierszy. Wybór spółki otwiera prawy panel.
Pełny kontrakt panelu i V3 należy do późniejszych paczek.

Ten sam prawy panel musi być dostępny po kliknięciu **każdej** spółki niezależnie od
tego, czy użytkownik jest w UNIVERSE, BASE czy IPO. Panel korzysta z jednego
`instrument_id`, a sekcje BASE/IPO pojawiają się zależnie od statusów. Dla spółki
UNIVERSE bez gorącego wykresu panel pokazuje ostatni cache i akcję `Włącz wykres`.

Wiązanie na przyszłość:

- wspólne `instrument_id`;
- status wykresu `COLD`, `QUEUED`, `READY`, `STALE`, `INCOMPLETE`, `ERROR`;
- ostatnia poprawna wersja pozostaje dostępna podczas odświeżania;
- interaktywny ruch wykresowy ma P0 `INTERACTIVE_MARKET`;
- przeglądarka renderuje gotowy payload; nie pobiera rynku i nie liczy wskaźników.

### 7.7. Obowiązkowa aktualność przy każdej spółce — prosty widok

Każdy wiersz i prawy panel muszą zawsze pokazywać prosty napis, np.:

```text
Aktualizacja: 16:45, 12.07.2026
```

Jest to data i godzina danych prezentowanych przy spółce, zawsze przeliczona na czas
lokalny użytkownika ustawiony w SKOOP. Nie pokazujemy tu czasu giełdy. Nie wymagamy od
użytkownika otwierania diagnostyki. Sam napis „5 min temu” nie wystarcza.

W bazie czas zapisujemy w UTC, aby uniknąć błędów zmiany czasu, a UI przelicza go na
strefę użytkownika. Data sesji giełdowej pozostaje osobnym polem.

Ponieważ bloki mają różne częstotliwości, przechowujemy osobno:

- `source_as_of` — moment, którego dotyczą dane źródłowe;
- `last_success_at` — ostatnia udana aktualizacja;
- `last_attempt_at` — ostatnia próba, także nieudana;
- `published_at` — moment udostępnienia wersji w SKOOP;
- `status`, `source`, `version` oraz ostatni błąd.

Powyższe pola techniczne pozostają w tle do diagnostyki. Domyślny UI pokazuje jeden
prosty czas. Szczegółowe czasy: rynek, profil, finanse, IPO i wykres są dostępne dopiero
w opcjonalnym widoku diagnostycznym. Nie wolno nadpisać `last_success_at` czasem
nieudanej próby.

### 7.8. Ręczne edycje i korekty

Każda spółka ma akcję `Edytuj/Koryguj` w prawym panelu, niezależnie od listingu.
Korekta nie może kasować ani nadpisywać surowej wartości dostawcy.

Model wartości:

```text
wartość źródłowa dostawcy
        + aktywna korekta użytkownika
        = wartość efektywna pokazywana w SKOOP
```

Każda zmiana dopisuje nowy wpis do historii; wcześniejszych wpisów nie usuwamy:

- `instrument_id` i pole;
- poprzednią i nową wartość;
- `changed_at` z datą, godziną i strefą;
- `changed_by=USER_LOCAL` albo identyfikator użytkownika;
- opcjonalne/obowiązkowe uzasadnienie zależne od pola;
- status `ACTIVE`, `REVERTED` albo `SUPERSEDED`.

UI pokazuje znacznik, np. `Ręczna korekta · 18:22, 23.08.2026`. Musi istnieć historia
i możliwość cofnięcia korekty bez usuwania dowodu.

Dozwolone ręczne korekty obejmują profil, klasyfikację, linki, dane IPO, notatki oraz
kontrolowany override BASE. Surowych świec, cen i wolumenów nie edytujemy bezpośrednio;
błąd rynku oznaczamy i naprawiamy osobnym procesem korekty danych z audytem, aby ręczna
zmiana nie zafałszowała wskaźników i sygnałów.

### 7.9. Obowiązkowy projekt graficzny przed implementacją listingu

Wygląd listingu nie może powstać jako improwizacja podczas kodowania. Po zamknięciu
kontraktu danych, a przed paczką implementacyjną listingu, powstaje osobna izolowana
paczka `SKOOP-COMPANY-LISTING-DESIGN-001`.

Paczka projektu graficznego musi zawierać co najmniej:

- pełny widok desktopowy UNIVERSE, BASE i IPO;
- wspólny prawy panel spółki otwierany z każdego listingu;
- miniwykres w tabeli i pełny wykres po powiększeniu;
- filtry, sortowanie, paginację, wyszukiwanie i ręczną edycję;
- stany `ładowanie`, `aktualizuję`, `ostatnie poprawne dane`, `brak danych`, `błąd`,
  `wykres zimny`, `wykres w kolejce`, `wykres gotowy` i `ręczna korekta`;
- odznaki BASE, IPO, sygnału, obserwacji, portfela i zlecenia oczekującego;
- prostą prezentację czasu aktualizacji w lokalnej strefie użytkownika;
- projekt zachowania panelu i tabeli przy różnych szerokościach ekranu;
- mapowanie każdego elementu widoku na pole lub status z kontraktu danych;
- design tokens: kolory, typografia, odstępy, rozmiary, stany hover/focus/disabled;
- specyfikację interakcji i klikalny projekt lub równoważny prototyp;
- screenshoty PNG oraz pliki źródłowe/HTML umożliwiające Claude jednoznaczne
  odtworzenie projektu.

OLD r599 i odzyskane wykresy V3 są materiałem referencyjnym dla ergonomii, układu
i sprawdzonych rozwiązań. Nie oznacza to kopiowania starego wyglądu bez przeglądu ani
przeniesienia starej logiki biznesowej.

Projekt graficzny wymaga osobnej wizualnej akceptacji użytkownika. Paczka
implementacyjna listingu nie może powstać, dopóki projekt nie ma statusu `ACCEPTED`,
testów stanów i kompletnego handoffu dla Claude.

## 8. Publikacja, aktualność i błędy

- każdy GET czyta ostatnią opublikowaną wersję; zero sieci w GET;
- członkostwo UNIVERSE i wynik reguł BASE mogą mieć wersję zbioru + wskaźnik `current`;
- dane listingu, profil, finanse, IPO i linki publikowane są **rekord po rekordzie** po
  walidacji; nie czekamy na aktualizację 5000–9000 spółek;
- każda grupa pól ma własne `last_updated`, `status`, `version` i `source`;
- `STALE` jest informacją i nie usuwa ostatnich poprawnych danych;
- błąd nowej aktualizacji nie może zastąpić poprawnej wcześniejszej wersji;
- priorytet pobierania wpływa wyłącznie na kolejność, nigdy na kwalifikację BASE;
- frontend może jedynie ustawić `focus`; pobrania i przeliczenia są kolejkami/jobami.

### 8.0. Płynny listing zamiast oczekiwania na pełny przebieg

Po wejściu użytkownik natychmiast widzi kompletny listing z ostatniej zakończonej
sesji. W nagłówku znajduje się informacja, np.:

```text
Dane bazowe: sesja 22.08.2026 · trwa aktualizacja 1247/4933 · błędy 4
```

Kiedy nowy rekord przejdzie walidację, zastępuje tylko poprzednią wersję tej spółki.
Pozostałe wiersze nadal pokazują ostatnie poprawne dane wraz z własnym czasem aktualizacji.

Aby lista nie przeskakiwała podczas czytania i sortowania:

- aktywny widok użytkownika zachowuje kolejność;
- UI pokazuje `Nowe dane dostępne dla N spółek`;
- ponowne sortowanie/odświeżenie następuje po decyzji użytkownika albo bezpiecznej
  zmianie strony/filtra;
- aktualizowana właśnie spółka nie znika i nie pokazuje pustego wiersza;
- błąd jednej spółki nie blokuje żadnej innej.

Nowy rekord najpierw sprawdzamy w tle, a dopiero potem bezpiecznie zastępujemy nim
poprzedni rekord tej spółki. Użytkownik widzi pełne poprzednie dane albo pełne nowe
dane, nigdy rekord w połowie nadpisany. Nie czekamy na zakończenie całego universe.

### 8.1. Zaakceptowany harmonogram i łańcuch procesów

Harmonogram został zaakceptowany w UD-09. Rozdziela **skład zbioru** od **danych rynkowych i wykresów**. BASE może
mieć świece aktualizowane w sesji co 5 minut, ale jego kanoniczna kwalifikacja nie
powinna przez to zmieniać się co 5 minut.

| Zasób/proces | Kiedy | Co zmienia | Czego nie zmienia |
|---|---|---|---|
| `UNIVERSE_DISCOVERY` | 1× dziennie o 04:00 ET; dodatkowo po pierwszym kluczu, ręcznym żądaniu lub recovery | nowe/zmienione/inaktywne instrumenty i wersję universe | BASE, IPO, profil i świece |
| dzienny snapshot rynku | po potwierdzonym zamknięciu właściwej sesji | ostatnie close, volume, obrót i finalny bar 1D | tożsamość i kryteria BASE |
| `BASE_INPUT` | natychmiast dla nowych symboli; pozostałe rekordy ciągłą wznawialną kolejką bez biznesowego limitu top-N | minimalne mcap albo shares; cena/ADV z market.db | pełny profil i wynik BASE |
| `BASE_EVAL` | po nowej wersji universe, finalnym 1D/base_input oraz zmianie progów | nową wersję `base_state`; zero sieci | UNIVERSE i IPO |
| `IPO_TRACKER` | jedno planowe odświeżenie dziennie **po rozpoczęciu** regularnej sesji USA, z konfigurowalnym opóźnieniem ustalonym po teście źródła; dodatkowo start przy pustej bazie, ręczne recovery i retry po błędzie; licznik sesji po finalnym 1D | `company_ipo`, pierwszą sesję/close i `X/180` | BASE i UNIVERSE |
| intraday BASE | co 5 min w aktywnej sesji; nocny reconcile luk | świece/payloady BASE | kanoniczny status BASE |
| listing | poprzednia sesja dostępna natychmiast; rekordy zastępowane pojedynczo po sprawdzeniu; widoczny postęp | ostatnie poprawne i bieżące dane spółki | danych źródłowych |
| janitor/backup | poza sesją, rekomendowane 23:30 ET | prune, checkpoint, integrity, backup | logiki produktu |

Łańcuch zdarzeniowy:

```text
04:00 ET: UNIVERSE_DISCOVERY
       → kolejka braków BASE_INPUT
       → BASE_EVAL na dostępnej wersji

potwierdzone zamknięcie sesji:
finalny 1D dla pełnego UNIVERSE
       → obliczenie close/volume/turnover/ADV
       → odświeżenie wymaganych BASE_INPUT
       → BASE_EVAL
       → aktualizacja licznika IPO X/180
       → płynna publikacja poprawnych rekordów i postępu

w trakcie sesji:
BASE market sync co 5 min
       → gotowe dane wykresowe
       → później technika/skaner
```

Jeżeli jeden etap nie powiedzie się, użytkownik nadal widzi poprzednią poprawną wersję.
Nie wolno wstrzymywać całego listingu z powodu braku profilu jednej spółki.

„Jedno odświeżenie dziennie” oznacza jeden planowy poprawny wynik. Nieudana próba
może zostać ponowiona zgodnie z backoffem i nie powoduje utraty poprzedniego kalendarza.
Dokładne opóźnienie po otwarciu USA pozostaje `UNVERIFIED` do smoke testu Massive:
zadanie ma wystartować dopiero wtedy, gdy źródło publikuje faktycznie handlujące nowe
IPO, a nie o arbitralnej, zgadniętej minucie.

Guardrails UD-09:

- sesje i finalne `1D` są liczone według kalendarza właściwej giełdy;
- PRE/POST USA są przechowywane i prezentowane oddzielnie od REGULAR;
- kolejność T0–T4 działa płynnie, a przerwana praca jest wznawiana;
- listing nie czeka na pełny przebieg i zawsze pokazuje ostatnie poprawne dane;
- dokładne odstępy, limity i opóźnienia wymagają smoke testu aktualnego planu Massive;
- kontrola ceny i wykonanie oczekujących zleceń pozostają osobną ścieżką bezpieczeństwa.

### 8.2. Dwa niezależne rodzaje priorytetu

**A. Priorytet ruchu do Massive P0–P3** określa, jak długo żądanie może czekać:

| Klasa | Zastosowanie w nowym SKOOP | TTL r599 |
|---|---|---:|
| P0 `INTERACTIVE_MARKET` | spółka/wykres właśnie otwarty przez użytkownika | 3 s |
| P1 `SCANNER_CRITICAL` | przyrostowe dane aktualnego BASE i później aktywny skaner; ograniczone krytyczne braki nowych symboli | 10 s |
| P2 `MAINTENANCE` | discovery UNIVERSE, grouped daily, IPO calendar, gap reconcile i masowe uzupełnianie BASE_INPUT | 45 s |
| P3 `COMPANY_BACKGROUND` | pełny profil, klasyfikacja dodatkowa, linki i pozostałe wolne wzbogacanie | 180 s |

BASE_EVAL oraz licznik sesji IPO nie pobierają danych i dlatego nie używają klasy
ruchu Massive.

**B. Priorytet spółki w kolejce** jest nowym porządkiem SKOOP wskazanym przez
użytkownika. Ważniejsza jest trwała kolejność poziomów niż przypadkowe liczby:

| Poziom | Spółki | Reguła |
|---:|---|---|
| T0 | aktualnie kliknięta/otwarta spółka | zawsze przed wszystkimi zwykłymi aktualizacjami; `focus` aktywny podczas otwartego panelu i krótko po nim |
| T1 | spółki z aktywnymi sygnałami | tylko sygnały aktualne; wygasły sygnał usuwa ten powód priorytetu |
| T2 | spółki obserwowane | aktywna watchlista/obserwacja użytkownika |
| T3 | spółki w aktywnych portfelach | otwarte pozycje oraz spółki z oczekującymi zleceniami dla danych profilu/wykresu |
| T4 | wszystkie pozostałe spółki w jednej płynnej kolejce | najpierw USA od najwyższego `ADV20_USD` do najniższego, bez progu, limitu liczby spółek i bloków; potem pozostały universe według zatwierdzonej kolejności rynków |

Jeżeli spółka spełnia kilka warunków, obowiązuje najwyższy poziom, a wszystkie powody
są zachowane diagnostycznie. Kolejka zmienia się zdarzeniowo:

- kliknięcie spółki — natychmiast;
- publikacja/wygaśnięcie sygnału — natychmiast;
- dodanie/usunięcie obserwacji — natychmiast;
- otwarcie/zamknięcie pozycji lub zlecenia — natychmiast;
- ranking wszystkich spółek USA według płynności — raz po finalnej sesji 1D;
- watchdog okresowo sprawdza, czy wskazówki nie utknęły.

T4 nie jest zbiorem ani paczką „najbardziej płynnych”. To jedna nieprzerwana kolejka:

```text
najwyższy ADV20_USD
        ↓
kolejna spółka
        ↓
kolejna spółka
        ↓
...
        ↓
najniższy ADV20_USD
```

Proces idzie płynnie od góry do dołu i nie zatrzymuje się po 100, 500 czy 1000
spółkach. Kliknięcie, sygnał, obserwacja albo zmiana portfela może w każdej chwili
wstawić pilniejszą spółkę na początek; po jej obsłużeniu kolejka wraca do miejsca, w
którym była. Błąd jednego rekordu odkłada go do ponownej próby i nie blokuje następnych.

Kliknięcie nie czyści ekranu i nie czeka na sieć: panel pokazuje ostatnie poprawne dane, oznacza
`Aktualizuję…`, a stale bloki tej spółki trafiają na początek odpowiednich kolejek.
Jeżeli dane są świeże według TTL, nie wykonujemy zbędnego żądania.

Kalendarz IPO jest osobnym zadaniem dziennym i nie konkuruje z tą kolejką. Konkretna
spółka IPO dziedziczy najwyższy pasujący poziom T0–T4.

Obsługa wykonania oczekującego zlecenia jest osobną ścieżką bezpieczeństwa, niezależną
od kolejki profilu. Cena potrzebna do wykonania zlecenia nie może czekać za zwykłym
wzbogacaniem spółek. W kolejce profilu spółka ze zleceniem należy do T3; w procesorze
zleceń obowiązuje jego własny najwyższy priorytet i bramka jakości ceny.

Priorytet aktualizacji nigdy nie może sam nadać statusu BASE ani IPO.

### 8.3. Kalendarze giełd i fazy sesji

Każdy instrument wskazuje kanoniczną giełdę/MIC, strefę czasu i właściwy kalendarz.
System nie może stosować jednego harmonogramu USA do wszystkich giełd.

Minimalne stany sesji:

- `PRE_MARKET` — tylko tam, gdzie giełda, źródło i późniejszy broker go wspierają;
- `REGULAR`;
- `POST_MARKET` — analogicznie zależny od rynku/brokera;
- `CLOSED`, `HOLIDAY`, `EARLY_CLOSE`;
- `HALTED` albo `UNKNOWN`, gdy nie można bezpiecznie potwierdzić handlu.

Kalendarz określa również otwarcie/zamknięcie aukcji i skrócone sesje, jeżeli jest to
potrzebne dla danego rynku. Nie każda giełda ma dostępny pre/post-market; brak obsługi
nie może być zastąpiony założeniem.

Wykresy i wskaźniki regularnej sesji nie mogą domyślnie mieszać świec pre/post z RTH.
Dane rozszerzonej sesji przechowujemy z `session_scope` i pokazujemy oddzielnie.

### 8.4. Zlecenia oczekujące a otwarte pozycje

Zlecenie złożone po zamknięciu rynku nie jest jeszcze otwartą pozycją. Musi otrzymać
osobny stan, np. `PENDING_MARKET_CLOSED`, i czekać na następną dozwoloną fazę sesji.

Minimalne przyszłe statusy: `PENDING_MARKET_CLOSED`, `PENDING_PRICE`,
`PENDING_LIMIT`, `READY_TO_EXECUTE`, `FILLED`, `CANCELLED`, `REJECTED`, `EXPIRED`.
Zlecenie przechowuje czas złożenia, dozwolony zakres sesji, limit, ostatnią sprawdzoną
cenę i jej czas. `FILLED` dopiero tworzy otwartą pozycję.

Odzyskana waga `800` pozostaje dla otwartej pozycji. Rekomendacja dla oczekującego
zlecenia to osobna waga `900`, ponieważ wymaga kontroli ceny przed wykonaniem, ale nie
może być fałszywie oznaczone jako pozycja. Jest to `DECISION REQUIRED`.

### 8.5. Hierarchia interwałów wykresowych

Priorytet analityczny:

1. `1D` — główny interwał decyzji średnioterminowej;
2. `1H` — główny interwał szukania miejsca na inwestycję i sygnału kupna;
3. `30m` — wspierający/wyprzedzający dla `1H`, używany do wcześniejszego ostrzeżenia
   o możliwym miejscu wejścia lub sygnale kupna;
4. `2H` i `4H` — wspierające/wyprzedzające dla `1D`; szybsze wskaźniki mogą wcześniej
   pokazać rozwijający się układ, zanim potwierdzi go zamknięta świeca 1D.

`30m` jest przechowywane nie dlatego, że ma wyższy priorytet od `1H`, lecz dlatego,
że z dwóch poprawnie wyrównanych, zamkniętych świec 30m można zbudować 1H, a następnie
2H/4H bez kolejnych pobrań. `1D` pozostaje osobną kanoniczną świecą dzienną.

Rekomendowany model:

- źródłowo przechowujemy kanoniczne `30m` i `1D` z `session_scope`;
- materializujemy/cachujemy `1H` jako główny wynik analityczny;
- `2H` i `4H` budujemy z tego samego zamkniętego strumienia i wersjonujemy pochodzenie;
- żadna agregacja nie łączy PRE, REGULAR i POST w jedną świecę bez jawnej strategii;
- renderer dostaje gotowe payloady wszystkich pięciu TF i niczego nie liczy w UI.

Sygnał z interwału wspierającego ma status `EARLY/UNCONFIRMED`. Potwierdzenie następuje
dopiero na zamkniętej świecy głównego TF. Bieżąca, niezamknięta świeca może być widoczna,
ale nie może udawać potwierdzonego sygnału, ponieważ może się zmienić.

## 9. Wymagania i acceptance criteria

| ID | Wymaganie | Dowód akceptacji przyszłej implementacji |
|---|---|---|
| AC-01 | jeden instrument ma jeden `instrument_id` | test duplikatów i unikalności PASS |
| AC-02 | UNIVERSE/BASE/IPO są nakładającymi się statusami | fixtures czterech przypadków z §5.2 PASS |
| AC-03 | każda decyzja BASE ma status, powody i wersję reguł | 100% ocenionych rekordów ma audytowalny wynik |
| AC-04 | brak danych nie jest prezentowany jako zero | test API/UI dla braków PASS |
| AC-05 | IPO liczy zamknięte sesje właściwego rynku | test weekendów, świąt i sesji 180/181 PASS |
| AC-06 | link bez potwierdzenia nie udaje bezpośredniego URL | test `UNRESOLVED`/search/direct PASS |
| AC-07 | listing udostępnia wszystkie zatwierdzone kolumny i filtry | macierz pól API→UI PASS |
| AC-08 | sortowanie/paginacja nie wymagają pobrania pełnej tabeli do UI | test kontraktu zapytań PASS |
| AC-09 | GET nie wykonuje sieci ani zapisu | test side effects PASS |
| AC-10 | błąd odświeżenia zachowuje ostatnie poprawne dane | test bezpiecznego zastąpienia rekordu PASS |
| AC-11 | OLD i jego frozen bazy nie są zmieniane | porównanie hashy i test połączeń PASS |
| AC-12 | pełna implementacja ma FINAL-AS-BUILT i realne testy | komplet archiwum sprintu |
| AC-13 | trzy listingi mają odrębne kontrakty i wspólną tożsamość spółki | test pól UNIVERSE/BASE/IPO PASS |
| AC-14 | każda spółka pokazuje datę/godzinę ostatniego sukcesu | test braków, błędów i stref czasu PASS |
| AC-15 | każda giełda używa własnego kalendarza i faz sesji | testy wielu MIC, świąt i early close PASS |
| AC-16 | pending order nie jest otwartą pozycją | test przejść statusów i market-closed PASS |
| AC-17 | 1D/1H są główne, a 30m/2H/4H zachowują poprawne pochodzenie i session scope | test agregacji i granic sesji PASS |
| AC-18 | listing działa na poprzedniej sesji podczas aktualizacji rekordowej | test 5000 rekordów, postępu i ostatnich poprawnych danych PASS |
| AC-19 | ręczna korekta nie niszczy danych źródłowych i ma pełną historię | test edit/revert/audit PASS |
| AC-20 | prawy panel otwiera się z każdego z trzech listingów | test UNIVERSE/BASE/IPO dla tego samego instrument_id PASS |
| AC-21 | wspierający TF nie udaje potwierdzenia głównego TF | test `EARLY/UNCONFIRMED` i closed-bar PASS |
| AC-22 | priorytety spółek działają T0→T4, a najwyższy powód wygrywa | test click/signal/watch/portfolio/liquidity PASS |
| AC-23 | kliknięcie daje pierwszeństwo bez czyszczenia ostatnich poprawnych danych | test focus, TTL i stanu `Aktualizuję…` PASS |
| AC-24 | procesor zleceń nie czeka za kolejką profilu | test izolacji execution/profile PASS |
| AC-25 | kolejka T4 przechodzi przez wszystkie spółki USA od największego do najmniejszego ADV20 bez bloków | test ciągłości, pierwszeństwa, wznowienia i retry PASS |
| AC-26 | listing jest implementowany wyłącznie z zaakceptowanego projektu graficznego | komplet widoków UNIVERSE/BASE/IPO, panel, stany, tokens, prototyp i wizualne acceptance PASS |
| AC-27 | pierwsza BASE nie powstaje przed raportem UNIVERSE, próbnym wyliczeniem i akceptacją progów | test braku członkostwa po symulacji; zaakceptowany ruleset tworzy wersję BASE PASS |

## 10. Ryzyka i skutki uboczne

- **sieć:** brak w obecnej paczce; przyszły scope zależy od zatwierdzonego UNIVERSE;
- **bazy:** brak zapisu w obecnej paczce; przyszła implementacja tworzy nowe zasoby SKOOP;
- **runtime:** bez zmian; OLD i SKOOP shell pozostają w zastanym stanie;
- **sekrety:** brak; klucz Massive należy do osobnej paczki;
- **kompatybilność:** nowe statusy nie są kompatybilne 1:1 ze starym `base_ok/ipo`;
- **wydajność:** pełny profil i pełne intraday dla wszystkich 9000+ instrumentów mogą
  przekroczyć budżet; wymagane warstwy aktualizacji i priorytety;
- **jakość:** stary snapshot ma niepełną kapitalizację i niekanoniczną klasyfikację;
- **linki:** stare UI miało fallbacki wyszukiwarki, a baza universe nie przechowuje
  pełnego zestawu zweryfikowanych URL.

## 11. Rollback assumptions

Obecna paczka zmienia wyłącznie dokumentację aktywną. Rollback oznacza przeniesienie
lub oznaczenie paczki jako `REJECTED/SUPERSEDED`; nie dotyczy kodu, baz ani runtime.
Frozen archiwa nie są modyfikowane.

## 12. Braki i bramka

- `ACCEPTED — UD-01`: pełny katalog aktywnych spółek z zatwierdzonego zakresu Massive, z jawną klasyfikacją i bez automatycznego kopiowania OLD;
- `ACCEPTED — UD-02`: pełny UNIVERSE → raport jakości → próbne warianty BASE bez członkostwa → akceptacja progów → pierwsza BASE;
- `ACCEPTED — UD-03`: brak ceny, kapitalizacji lub ADV oznacza `PENDING_DATA`, jawny powód, uzupełnienie i ponowną ocenę; nigdy zero/fail-open/reject;
- `ACCEPTED — UD-04`: po 180. sesji koniec aktywnego IPO i ponowna ocena BASE; członkostwo wyłącznie według reguł, bez automatycznego wejścia;
- `ACCEPTED — UD-05`: IPO poza BASE ma sesyjny `1D` i przebieg od debiutu; intraday na T0 po kliknięciu lub według T1–T3; IPO w BASE aktualizowane jak BASE;
- `ACCEPTED — UD-06`: zachowanie wartości natywnej oraz oddzielnej wartości USD z audytem FX; cena natywna, porównanie kapitalizacji/obrotu/ADV w USD; brak FX = `PENDING_FX`;
- `TO RECOVER`: finalne mapowanie 20 sektorów / 129 branż;
- `TO RECOVER`: pełny historyczny `listing_scope`;
- `UNVERIFIED`: aktualne możliwości i limity planu Massive;
- `UNVERIFIED`: źródło pozwalające pokryć bezpośrednie linki Investing.

**Gate:** decyzje i konflikty logiczne tej paczki zamknięto 2026-08-24. Implementacja
nadal jest zabroniona do czasu końcowego acceptance tego SPEC oraz osobnego,
dokładnego Implementation Contract dla każdej małej paczki kodowej.

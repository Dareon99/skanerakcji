# SPEC — SKOOP-MASSIVE-ACCESS-001

```text
STATUS: CONTRACT ACCEPTED REV. 2 — GATE A AUTHORIZED / GATE B BLOCKED
AREA: PROVIDER-ACCESS (MASSIVE)
OWNER: USER
PRODUCT VERSION BEFORE: SKOOP FOUNDATION PLACEHOLDER / NO PRODUCT VERSION
TARGET: ACCESS CONTRACT ONLY — NO RUNTIME CHANGE IN THIS PACKAGE
DOCS BASE: repo Dareon99/skanerakcji @ 6fe1bcc; frozen spec @ c76014c
```

## 1. Problem i oczekiwany rezultat

Nowy SKOOP nie ma jeszcze żadnej warstwy dostępu do Massive: nie ma ustalonego
miejsca klucza, sposobu jego podania, limitów, obsługi błędów, kill switcha ani
kryteriów, które muszą być spełnione zanim zacznie się pobieranie UNIVERSE
(zaakceptowany kontrakt D-009/UD-01). Rezultatem tej paczki jest zatwierdzony
kontrakt dostępu; osobna paczka implementacyjna wykona kod i jeden kontrolowany
smoke test.

## 2. In scope

Punkty 1–18 poniżej: sekret, warstwy, test połączenia, smoke test, limity,
błędy, ochrona API, logowanie, kill switch, tryb testowy, backup/rollback,
izolacja OLD, kryteria akceptacji, mapowanie danych kontraktu na endpointy,
koszty, kontrola pól, natywność danych i zasady czasu.

## 3. Out of scope

- wpisanie/odczyt/zapis prawdziwego klucza lub sekretu;
- jakiekolwiek żądanie sieciowe do Massive/Yahoo/innych;
- kod, SQL, nowe bazy, workery, scheduler, UI;
- pobranie UNIVERSE (osobna paczka `SKOOP-UNIVERSE-IMPORT-001`);
- uruchamianie OLD/r599 w jakiejkolwiek formie;
- finalne wartości limitów — zależą od smoke testu.

## 4. Kontrakt szczegółowy

### 4.1. Przechowanie klucza (pkt 1)

Klucz Massive żyje wyłącznie poza repozytorium i poza dokumentacją:

- lokalizacja: katalog danych SKOOP poza folderem produktu i poza Git
  (propozycje w UD-M-01; wzorzec OLD `..\skaner-dane\polygon_key.txt`
  jest referencją, nie decyzją);
- plik/mechanizm objęty `.gitignore` i secret-scanem przed każdym commitem;
- dokumentacja może wymieniać nazwę pliku/zmiennej, nigdy wartość;
- rotacja: podmiana wartości u źródła bez zmiany kodu; stary klucz nie jest
  archiwizowany w projekcie;
- wykrycie sekretu w repo = STOP + rotacja klucza (zgodnie z
  `DOSTEPY-I-BEZPIECZENSTWO.md` §2).

### 4.2. Podanie klucza aplikacji bez ujawnienia (pkt 2)

- aplikacja czyta klucz raz przy starcie z zatwierdzonej lokalizacji;
- wartość nigdy nie trafia do: logów, komunikatów błędów, UI, raportów,
  testów, stack trace'ów, adresów URL zapisywanych w logach ani plików tymczasowych;
- log techniczny może zapisać wyłącznie: `key_present=true/false` oraz
  `key_fingerprint` = skrót SHA-256 ograniczony do 8 znaków (bez części jawnej klucza);
- każdy zapis URL do logu przechodzi przez maskowanie parametru klucza;
- testy używają klucza wyłącznie w locie; asercje porównują fingerprint.

### 4.3. Rozdzielenie warstw (pkt 3)

```text
config (lokalizacja klucza, limity, flagi)
  → connection (HTTP, autoryzacja, timeouty, maskowanie)
    → fetch (endpointy, paginacja, walidacja odpowiedzi)
      → persistence (zapis do baz — POZA tą paczką)
```

Zasady: connection nie zna baz; fetch nie zna UI; persistence nie zna klucza;
GET produktu nigdy nie wykonuje sieci (zgodnie z frozen kontraktem §8).

### 4.4. Minimalny test połączenia (pkt 4)

Jeden najtańszy możliwy request potwierdzający autoryzację (np. odczyt
metadanych/jednego instrumentu). Kontrakt: dokładnie 1 żądanie, zero zapisu do
baz produkcyjnych, wynik = kod HTTP + zmierzone opóźnienie + fingerprint klucza.
Wybór dokładnego endpointu: `UNVERIFIED — TO VERIFY DURING AUTHORIZED SMOKE TEST`.

### 4.5. Smoke test endpointów i subskrypcji (pkt 5)

Kontrolowana, budżetowana seria pojedynczych żądań (limit łączny w UD-M-05),
po jednym na każdą kategorię danych z §4.14. Wynikiem jest tabela:
endpoint → dostępny/niedostępny, kod odpowiedzi, opóźnienie danych,
zakres rynków, paginacja, pola obecne/nieobecne. Zero pełnego pobierania.

### 4.6. Rozpoznanie limitów i uprawnień (pkt 6)

Nie zakładamy żadnego planu Massive. Smoke test ma ustalić: realny limit
zapytań (nagłówki rate-limit, zachowanie 429), opóźnienie danych (real-time /
delayed / EOD), dostępne rynki i typy instrumentów, głębokość historii.
Do czasu testu wszystko: `UNVERIFIED — TO VERIFY DURING AUTHORIZED SMOKE TEST`.

### 4.7. Obsługa błędów (pkt 7)

| Odpowiedź | Zachowanie kontraktowe |
|---|---|
| 401 | STOP kategorii auth: nie ponawiać, oznaczyć klucz jako odrzucony, zgłosić |
| 403 | brak uprawnienia planu: nie ponawiać tego endpointu, zapisać w mapie subskrypcji |
| 404 | brak zasobu: nie ponawiać w pętli; oznaczyć rekord `MISSING_AT_SOURCE` |
| 429 | wspólny cooldown (wartość do smoke testu; referencja r599: 13 s), potem retry |
| timeout | retry z backoffem i limitem prób; potem `ERROR` bez utraty last-good |
| sieć/DNS | jak timeout; seria porażek eskaluje do kill switcha (§4.10) |

Żaden błąd nie może nadpisać ostatnich poprawnych danych (frozen kontrakt AC-10).

### 4.8. Ochrona przed niekontrolowanym zużyciem (pkt 8)

- centralny limiter wszystkich żądań SKOOP → Massive (jedno miejsce, żadnych
  obejść); parametry startowe w UD-M-02;
- kolejka z priorytetami ruchu P0–P3 zgodnie z frozen kontraktem §8.2
  (nazwy klas potwierdzone: INTERACTIVE_MARKET, SCANNER_CRITICAL,
  MAINTENANCE, COMPANY_BACKGROUND);
- retry z wykładniczym backoffem i twardym limitem prób;
- cache z TTL per kategoria danych; świeże dane nie generują żądania;
- dzienny licznik żądań + configurowalny twardy sufit dzienny (bezpiecznik);
- mechanizmy r599 (token bucket 30/s, capacity 90, cooldown 13 s) są wyłącznie
  referencją OLD — nowe wartości wymagają UD-M-02 i smoke testu.

### 4.9. Logowanie techniczne bez sekretu (pkt 9)

Log per żądanie: czas UTC, endpoint (zamaskowany URL), kategoria/priorytet,
kod odpowiedzi, opóźnienie, liczność wyniku, licznik dzienny; log błędów z
pełnym kontekstem minus sekret; poziom szczegółowości i retencja w UD-M-07.

### 4.10. Kill switch (pkt 10)

Jeden przełącznik zatrzymujący natychmiast całą komunikację z Massive:

- działa bez restartu procesu (sprawdzany przed każdym żądaniem);
- ustawiany ręcznie przez użytkownika oraz automatycznie po przekroczeniu
  progów bezpieczeństwa (sufit dzienny, seria 401/403, sztorm błędów);
- stan jest trwały (przeżywa restart) i jawnie widoczny w statusie;
- wyłączenie kill switcha wymaga świadomej akcji użytkownika;
- semantyka domyślna (fail-open vs fail-closed przy awarii samego mechanizmu)
  — decyzja UD-M-03.

### 4.11. Tryb testowy (pkt 11)

Tryb, w którym warstwa fetch działa, ale persistence pisze wyłącznie do
izolowanej lokalizacji testowej (UD-M-06), nigdy do przyszłych baz
produkcyjnych SKOOP ani do żadnej frozen bazy OLD. Wyjścia trybu testowego są
oznaczone i odizolowane od danych produktu. Usunięcie wymaga zachowania dowodów,
kontroli integralności, wskazania dokładnej ścieżki i osobnej akceptacji użytkownika.

### 4.12. Backup, rollback, izolacja OLD (pkt 12)

- przed jakąkolwiek przyszłą zmianą plików: backup zmienianych plików + hashe
  BEFORE/AFTER (wzorzec r599);
- rollback = przywrócenie backupu + weryfikacja hash + test, że żadna
  komunikacja Massive nie startuje samoczynnie;
- OLD: zero zmian w `C:\Skaner wykresów`, `C:\skaner-dane`,
  `OLD-r599-1TO1`, `OLD-RUNTIME-DATA` i frozen archiwach; OLD ma nadal
  ZERO ruchu Massive; potwierdzenie = brak procesów OLD + hash frozen baz;
- klucz nie jest częścią backupu paczki.

### 4.13. Kryteria akceptacji dostępu (pkt 13)

Dostęp uznaje się za zaakceptowany (i dopiero wtedy wolno planować
`SKOOP-UNIVERSE-IMPORT-001`), gdy wszystkie poniższe mają dowód:

| AC | Kryterium |
|---|---|
| AC-M-01 | klucz czytany z zatwierdzonej lokalizacji; secret-scan repo = 0 trafień |
| AC-M-02 | test połączenia = dokładnie 1 żądanie, HTTP 200, zero zapisu produkcyjnego |
| AC-M-03 | smoke test wypełnił mapę subskrypcji (endpointy/limity/opóźnienia/rynki) |
| AC-M-04 | 401/403/404/429/timeout obsłużone zgodnie z §4.7 (testy z atrapą) |
| AC-M-05 | limiter + sufit dzienny + kolejka priorytetów działają (test bez sieci) |
| AC-M-06 | kill switch zatrzymuje ruch natychmiast i przeżywa restart |
| AC-M-07 | log nie zawiera sekretu (scan logów = 0 trafień) |
| AC-M-08 | tryb testowy nie dotknął żadnej bazy produkcyjnej/frozen (hashe) |
| AC-M-09 | OLD bez zmian i bez ruchu (hashe + brak procesów) |
| AC-M-10 | mapowanie §4.14 używa wyłącznie sześciu statusów z kontraktu §3.2; `CONFIRMED` tylko po dowodzie |

### 4.14. Dane kontraktu UNIVERSE–BASE–IPO → endpointy Massive (pkt 14)

Wszystkie wiersze mają dziś status `UNVERIFIED — TO VERIFY DURING AUTHORIZED
SMOKE TEST`. Nie zakładamy nazw endpointów ani zawartości planu.

| Dane wymagane przez frozen kontrakt | Źródło w kontrakcie | Status |
|---|---|---|
| katalog aktywnych instrumentów (ticker, nazwa, giełda/MIC, kraj, waluta, typ, active) | §6.1, D-009 | UNVERIFIED — TO VERIFY |
| klasyfikacja (SIC / sektor / branża) | §6.2 | UNVERIFIED — TO VERIFY |
| kapitalizacja i liczba akcji (outstanding vs w obrocie, dwa pola) | §6.3, §7.2 | UNVERIFIED — TO VERIFY |
| zysk netto kwartalny i TTM | §7.2 | UNVERIFIED — TO VERIFY |
| kalendarz/status IPO, data debiutu, cena IPO | §6.5, D-013/D-014 | UNVERIFIED — TO VERIFY |
| świece 1D (pełny UNIVERSE, finalny bar po zamknięciu) | §8.1, D-016 | UNVERIFIED — TO VERIFY |
| świece 30m (kanoniczne intraday; 1H/2H/4H budowane lokalnie) | §8.5 | UNVERIFIED — TO VERIFY |
| fazy sesji / kalendarze giełd / święta | §8.3 | UNVERIFIED — TO VERIFY |
| kursy FX do wartości porównawczych USD | §6.3, D-015 | UNVERIFIED — TO VERIFY (może wymagać innego źródła) |
| splity/dywidendy (korekty świec) | pochodna §8.5 | UNVERIFIED — TO VERIFY |

### 4.15. Koszty i ryzyko liczby zapytań (pkt 15)

Rachunek strukturalny bez zakładania limitów planu:

- discovery UNIVERSE: rząd 1–N żądań stronicowanych dziennie (N zależy od paginacji);
- finalny 1D dla ~9000 spółek: do ~9000 żądań/dzień, o ile plan nie udostępnia
  odpowiedzi zbiorczej (grouped/bulk) — istnienie takiej odpowiedzi: TO VERIFY;
- intraday 30m tylko dla BASE (~5000 wg OLD, realnie wg nowych progów) co ~5 min
  w sesji — to największy składnik kosztu; wymaga odpowiedzi zbiorczej albo
  ograniczenia zakresu: TO VERIFY;
- profil/finanse: P3, wolne wzbogacanie, rozłożone w czasie;
- ryzyka: paginacja mnożąca żądania, retry storm po awarii, brak odpowiedzi
  zbiorczych w planie, opóźnienie danych czyniące 5-minutowy rytm bezcelowym.
  Każde z tych ryzyk rozstrzyga smoke test, nie założenie.

### 4.16. Kontrola pól dostarczanych przez Massive (pkt 16)

Dla każdej kategorii z §4.14 smoke test pobiera 1 przykładowy rekord i porównuje
pola z kontraktem §6 frozen SPEC. Wynik trafia do macierzy pole→obecne/brak/
wymaga-innego-źródła. Pole nieobecne u dostawcy dostaje w kontrakcie danych
status `MISSING_AT_SOURCE` i jawną decyzję co dalej — nigdy zgadywanie.

### 4.17. Dane natywne vs przeliczenia (pkt 17)

Warstwa fetch zapisuje wyłącznie wartości natywne dostawcy (waluta instrumentu,
oryginalne pola, czas źródła). Przeliczenia USD są osobnym, późniejszym i
wersjonowanym krokiem zgodnie z D-015 (`fx_rate`, `fx_source`, `fx_as_of`,
wersja metody; brak FX = `PENDING_FX`). Żadne przeliczenie nie nadpisuje
wartości źródłowej.

### 4.18. Zasady czasu (pkt 18)

Zgodnie z zamrożonym kontraktem (§7.7, §8.3, UD-19):

- zapis techniczny: zawsze UTC;
- harmonogramy: strefa/kalendarz właściwej giełdy (MIC), nigdy jeden kalendarz USA
  dla wszystkich rynków;
- prezentacja w UI: zawsze czas lokalny użytkownika;
- data sesji giełdowej jest osobnym polem i nie podlega konwersji strefy;
- `source_as_of`, `last_success_at`, `last_attempt_at`, `published_at`
  rozdzielone; porażka nigdy nie nadpisuje `last_success_at`.

## 5. Ryzyka i skutki uboczne

- sieć: żadna w tej paczce; przyszły smoke test = pojedyncze budżetowane żądania;
- sekret: żaden nie jest czytany ani zapisywany; ryzyko wycieku adresowane w §4.1–4.2;
- bazy: brak zapisu; tryb testowy odizolowany;
- OLD: nietknięty; dodatkowe potwierdzenie w kryteriach AC-M-09;
- największa niepewność: rzeczywisty plan Massive użytkownika — wszystko co od
  niego zależy jest jawnie UNVERIFIED.

## 6. Rollback assumptions

Paczka dokumentacyjna: rollback = `REJECTED/SUPERSEDED`, bez dotykania kodu,
baz i runtime. Frozen archiwa nieruszane.

## 7. Braki (jawne)

- `UNVERIFIED`: plan Massive, limity, opóźnienia, endpointy, odpowiedzi zbiorcze,
  głębokość historii, pokrycie rynków, dostępność FX u dostawcy;
- `TO RECOVER`: dokładna konfiguracja `polygon_source.py` OLD jako referencja
  (kod OLD niedostępny w repo dokumentacji);
- `DECISIONS ACCEPTED`: UD-M-01…UD-M-07 (patrz `04-USER-DECISIONS.md`).

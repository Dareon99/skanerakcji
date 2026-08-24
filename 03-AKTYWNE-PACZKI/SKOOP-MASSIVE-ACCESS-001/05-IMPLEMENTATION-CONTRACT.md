# IMPLEMENTATION CONTRACT — SKOOP-MASSIVE-ACCESS-001

```text
STATUS: ACCEPTED — GATE A AUTHORIZED (OFFLINE ONLY) / GATE B BLOCKED
REVISION: 2 (2026-08-24; korekty użytkownika PASS WITH REQUIRED CORRECTIONS)
PRODUCT VERSION BEFORE: SKOOP FOUNDATION PLACEHOLDER / NO PRODUCT VERSION
PRODUCT VERSION AFTER: SKOOP-MASSIVE-ACCESS-001 AS-BUILT (bez zmiany wersji OLD r599)
AUTHORIZED RUNTIME LEVEL AFTER ACCEPTANCE: Gate A = L2–L3 offline; Gate B = L4 po osobnej zgodzie
DECISIONS: UD-M-01…UD-M-07 ACCEPTED 2026-08-24; CM-01…CM-05 CLOSED
```

Do chwili jawnej akceptacji tego kontraktu obowiązuje L0: zero kodu, klucza,
sieci i zapisu baz.

## 1. Dokładny zakres plików

### 1.1. Nowe pliki kodu — katalog paczki

Lokalizacja kodu (potwierdzona przez użytkownika):

```text
C:\SKOOP Skaner wykresów\PACKAGES\SKOOP-MASSIVE-ACCESS-001\
```

Kod paczki nie może znajdować się w OLD ani importować modułów OLD.
Dane pozostają oddzielnie w `C:\SKOOP-dane\`.

| Plik | Rola | Zmiana |
|---|---|---|
| `config_access.py` | ścieżka klucza (UD-M-01), limity smoke testu, ścieżki sandbox/logów, flaga kill switch | CREATE |
| `secret_loader.py` | odczyt `C:\SKOOP-dane\secrets\massive_key.txt`; fingerprint SHA-256/8; zero echa wartości | CREATE |
| `massive_connection.py` | HTTP, autoryzacja, timeouty, maskowanie URL, klasyfikacja odpowiedzi wg §3.2 | CREATE |
| `massive_fetch.py` | pojedyncze żądania kategorii mapy SPEC §4.14; paginacja czytana, nie podążana poza budżet | CREATE |
| `traffic_guard.py` | licznik żądań, twardy sufit 50, sekwencyjność, FAIL-CLOSED, kill switch (plik-flaga trwały) | CREATE |
| `access_log.py` | log per żądanie wg UD-M-07 do `C:\SKOOP-dane\logs\massive\`; rotacja; retencja 30 dni | CREATE |
| `sandbox_store.py` | zapis wyników wyłącznie do `C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\` (SQLite + JSON dowody) | CREATE |
| `smoke_test.py` | scenariusz §3; STOP po każdym FAIL; start tylko po otwarciu Gate B | CREATE |
| `test_access_offline.py` | testy jednostkowe BEZ sieci (atrapy odpowiedzi) | CREATE |
| `KILL-SWITCH-ON.bat` / `KILL-SWITCH-OFF.bat` | ręczne sterowanie przełącznikiem | CREATE |
| `README-URUCHOMIENIE.md` | instrukcja krok po kroku dla użytkownika | CREATE |

### 1.2. Istniejące pliki dokumentacji — kontrolowana aktualizacja (append-only / po akceptacji wyników)

| Plik (źródło prawdy, repo/lokalna DOKUMENTACJA) | Zmiana | Kiedy |
|---|---|---|
| `04-DECYZJE/DECYZJE-PROJEKTOWE.md` | append-only ANEKS do D-007 (treść w §2.2) | PRZED pierwszym żądaniem sieciowym (warunek Gate B) |

Łącznie: **12 plików fizycznych** (9 Python, 2 BAT, 1 README).
| `MASTER-PROJEKT.md` | aktualizacja stanu/rejestru sprintów | dopiero PO akceptacji wyników paczki |
| `STAN-AKTUALNY.md` | aktualizacja stanu operacyjnego | dopiero PO akceptacji wyników paczki |
| dokumentacja tej paczki (06/07/08/HASHES/FREEZE) | wyniki, acceptance, AS-BUILT, manifest, freeze | zgodnie z workflow |

Wpisy do repozytorium wykonuje użytkownik/operator lokalny; Claude nie robi
commit/push.

### 1.3. Katalogi danych tworzone dopiero przez implementację (lazy-create, poza produktem)

- `C:\SKOOP-dane\secrets\` — katalog; sam plik klucza tworzy WYŁĄCZNIE użytkownik;
- `C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\`;
- `C:\SKOOP-dane\logs\massive\`.

### 1.4. Zmiany zakazane

Jakikolwiek plik OLD (`C:\Skaner wykresów`, `OLD-r599-1TO1`, `OLD-RUNTIME-DATA`,
`C:\skaner-dane`, frozen archiwa), placeholder SKOOP poza katalogiem `PACKAGES\...`,
zamrożona paczka UNIVERSE–BASE–IPO, jakakolwiek istniejąca baza; commit/push przez
Claude; import modułów OLD z kodu paczki.

## 2. Sekret i aneks D-007

### 2.1. Sekret

- kod czyta wyłącznie `C:\SKOOP-dane\secrets\massive_key.txt`; dostęp do pliku
  wyłącznie dla bieżącego użytkownika Windows;
- klucz tworzy i zapisuje lokalnie WYŁĄCZNIE użytkownik; nie wolno prosić
  o wklejenie klucza do rozmowy, Claude, GitHuba ani dokumentacji;
- brak/pusty plik = czytelny komunikat i STOP (fail-closed), zero żądań;
- każdy artefakt (kod, log, raport, dokument, test) przechodzi secret-scan;
  wynik wymagany: 0 trafień.

### 2.2. Aneks do D-007 (append-only, przed pierwszym żądaniem)

Aneks w `DECYZJE-PROJEKTOWE.md` ma jednoznacznie stanowić:

- zakaz pobierania pozostaje bezterminowo w mocy dla OLD;
- OLD pozostaje zamrożony, offline i bez dostępu do Massive;
- nowy SKOOP na tym komputerze może korzystać z Massive wyłącznie w ramach
  osobno zaakceptowanych paczek;
- aneks nie uruchamia pobierania i nie jest samodzielną zgodą na nieograniczony
  ruch sieciowy.

## 3. Smoke test (wykonywany wyłącznie w Gate B)

### 3.1. Kroki i budżet (UD-M-05, sufit 50 żądań, sekwencyjnie)

| Krok | Kategoria (SPEC §4.14) | Żądań plan/max | Wynik zapisywany |
|---|---|---:|---|
| S0 | test połączenia/autoryzacji (najtańszy odczyt) | 1/2 | kod HTTP, opóźnienie, fingerprint klucza |
| S1 | katalog aktywnych instrumentów (1 strona) | 1/2 | pola, paginacja, liczność, rynki |
| S2 | szczegóły 1 instrumentu (nazwa, giełda/MIC, waluta, typ, kraj, active) | 1/2 | macierz pól §6.1 |
| S3 | klasyfikacja (SIC/sektor/branża) | 1/2 | macierz pól §6.2 |
| S4 | kapitalizacja + liczba akcji (outstanding vs w obrocie) | 1/2 | macierz pól §6.3 |
| S5 | zyski kwartalne/TTM dla 1 spółki | 1/2 | dostępność finansów |
| S6 | kalendarz/status IPO | 1/2 | dostępność, pola debiutu/ceny |
| S7 | świece 1D dla 1 spółki (krótki zakres) | 1/2 | pola OHLCV, opóźnienie danych |
| S7b | odpowiedź zbiorcza dziennych danych (grouped/bulk), jeśli plan ją ma | 1/2 | istnienie odpowiedzi zbiorczej |
| S8 | świece 30m dla 1 spółki (krótki zakres) | 1/2 | dostępność intraday |
| S9 | kalendarz sesji/święta | 1/2 | dostępność faz sesji |
| S10 | FX (1 para) | 1/2 | czy FX jest u dostawcy |
| S11 | splity/dywidendy dla 1 spółki | 1/2 | dostępność korekt |
| S12 | zakres historii: 1 żądanie 1D daleko wstecz | 1/2 | głębokość planu |
| S13 | odczyt nagłówków rate-limit z odpowiedzi S0–S12 | 0 | limity deklarowane; 429 pasywnie, bez prowokacji |

Plan bazowy 14 żądań; max 1 retry na krok wyłącznie dla `TRANSIENT_ERROR`;
twardy sufit globalny 50 egzekwowany przez `traffic_guard` — osiągnięcie sufitu
zatrzymuje test natychmiast. Test NIE uruchamia importu UNIVERSE i nie podąża
za paginacją.

### 3.2. Klasyfikacja wyników (obowiązująca; zastępuje wcześniejszą trójstanową)

| Status | Znaczenie | Reakcja |
|---|---|---|
| `CONFIRMED` | endpoint i wymagane dane potwierdzone | zapis do mapy |
| `UNAVAILABLE_IN_CURRENT_PLAN` | endpoint/dane niedostępne w posiadanej subskrypcji (m.in. 403) | zapis; bez retry |
| `MISSING_AT_SOURCE` | endpoint odpowiedział poprawnie, ale wymagane pole/dane nie występują | zapis macierzy pól |
| `UNVERIFIED` | brak jednoznacznego wyniku | zapis; do wyjaśnienia |
| `TRANSIENT_ERROR` | timeout, 429, 5xx lub inny błąd przejściowy | max 1 kontrolowany retry; potem zapis |
| `AUTHORIZATION_FAILED` | 401 albo błąd klucza | natychmiastowy STOP całego testu |

403 nigdy nie jest automatycznie klasyfikowane jako `MISSING_AT_SOURCE`.

## 4. Dwa oddzielne gate'y

### Gate A — implementacja offline (otwiera go akceptacja tego kontraktu)

Obejmuje wyłącznie:

- utworzenie nowych plików kodu z §1.1;
- testy z atrapami odpowiedzi (klasyfikacja §3.2, w tym 401/403/404/429/timeout);
- testy limitera (sufit 50, sekwencyjność, stop po limicie);
- testy kill switcha (stop natychmiastowy, trwałość po restarcie, stan
  niejednoznaczny = zero żądań);
- testy maskowania sekretu (scan logu z atrapą klucza = 0 trafień);
- testy zapisu wyłącznie do sandboxu (inna ścieżka = wyjątek);
- `py_compile`, AST i pozostałe testy statyczne;
- ZERO prawdziwego klucza; ZERO połączeń z Massive.

### Gate B — kontrolowany smoke test online (zablokowany do spełnienia WSZYSTKICH warunków)

1. wszystkie testy Gate A = PASS;
2. wyniki Gate A przedstawione użytkownikowi;
3. aneks do D-007 wpisany do źródła prawdy (`DECYZJE-PROJEKTOWE.md`);
4. sprawdzenie dokładnych ścieżek (klucz, sandbox, logi, katalog kodu);
5. potwierdzone działanie kill switcha;
6. osobna, jawna zgoda użytkownika na użycie lokalnego klucza i maksymalnie
   50 żądań.

Niespełnienie któregokolwiek warunku = Gate B pozostaje zamknięty.

## 5. Backup i rollback

- kod: wyłącznie nowe pliki w `PACKAGES\SKOOP-MASSIVE-ACCESS-001\`; backupem
  stanu wejściowego jest lista + hashe SHA-256 katalogów docelowych PRZED
  instalacją; manifest hashy nowych plików PO (BEFORE = brak, AFTER = manifest);
- dokumenty źródła prawdy: aneks D-007 jest append-only — rollback aneksu to
  wpis korygujący `SUPERSEDES`, nigdy kasowanie ani force-push;
- rollback kodu: usunięcie nowych plików wg manifestu + weryfikacja identycznych
  hashy OLD/frozen/placeholdera przed i po;
- sandbox i logi NIE są kasowane w rollbacku (dowód diagnostyczny; usunięcie
  wyłącznie wg procedury UD-M-06);
- plik klucza użytkownika nie jest częścią backupu ani rollbacku.

## 6. Obowiązkowy quality gate (Gate A, przed jakąkolwiek siecią)

```text
LAST WRITE
→ py_compile
→ AST
→ invalid escape / static / sanity
→ testy offline
→ secret-scan
→ kontrola braku importów i dostępu do OLD
→ kontrola dozwolonych ścieżek zapisu
→ test kill switcha i FAIL-CLOSED
→ package integrity
→ hashes
→ GATE A EVIDENCE SNAPSHOT (NO FREEZE)
```

Smoke test online nie może rozpocząć się, jeżeli którykolwiek element Gate A
zakończy się wynikiem innym niż PASS. Zmiana choćby jednego bajta po HASHES
unieważnia gate i wymaga jego powtórzenia (MASTER §10.2).


Finalny `FREEZE` pozostaje zabroniony w Gate A i następuje dopiero po Gate B,
akceptacji wyników oraz przygotowaniu FINAL-AS-BUILT.
## 7. Kryteria akceptacji

AC-M-01…AC-M-10 ze SPEC §4.13 z doprecyzowaniami decyzji (sufit 50, FAIL-CLOSED,
sandbox bez automatycznego kasowania, katalog logów i lista zakazów treści) oraz:

| AC | Kryterium |
|---|---|
| AC-M-11 | aneks do D-007 wpisany do rejestru decyzji przed pierwszym żądaniem |
| AC-M-12 | raport smoke testu: kompletna mapa S0–S13 wyłącznie ze statusami §3.2, bez zgadywania |
| AC-M-13 | raport per endpoint: status → dostępne pola → zakres historii → opóźnienie danych |
| AC-M-14 | zapisana dokładna liczba wykonanych żądań (licznik `traffic_guard` vs log = zgodne) |
| AC-M-15 | porównanie hashy OLD/frozen przed i po = identyczne |
| AC-M-16 | kompletne archiwum paczki: FINAL-AS-BUILT-SPEC, manifest SHA-256, FREEZE |
| AC-M-17 | `MASTER-PROJEKT.md` i `STAN-AKTUALNY.md` zaktualizowane dopiero PO akceptacji wyników |

## 8. STOP conditions

Każdy nowy FAIL testu; `AUTHORIZATION_FAILED` na dowolnym kroku; osiągnięcie
sufitu żądań; wykrycie sekretu w jakimkolwiek artefakcie; zapis poza
sandbox/logami; jakakolwiek zmiana pliku OLD/frozen; niejednoznaczny stan kill
switcha; source drift między akceptacją a wykonaniem; próba otwarcia Gate B bez
kompletu warunków §4. Po STOP: wyłącznie read-only diagnoza, klasyfikacja wg
MASTER §8, decyzja użytkownika.

## 9. Archiwum i AS-BUILT (obowiązkowe zamknięcie paczki)

- archiwizacja całej paczki (dokumentacja + kod + dowody) wg MASTER §11;
- `FINAL-AS-BUILT-SPEC` opisujący stan faktyczny po wszystkich poprawkach;
- manifest SHA-256 wszystkich artefaktów;
- porównanie hashy OLD przed i po;
- dokładna liczba wykonanych żądań;
- raport endpoint → status → dostępne pola → zakres historii → opóźnienie;
- aktualizacja `MASTER-PROJEKT.md` i `STAN-AKTUALNY.md` dopiero po akceptacji
  wyników przez użytkownika.

## 10. Zgoda

Zapis 1:1 akceptacji użytkownika z 2026-08-24:

```text
SKOOP-MASSIVE-ACCESS-001
CORRECTED IMPLEMENTATION CONTRACT REVISION 2 — AKCEPTUJĘ
AUTORYZOWANY ZAKRES: GATE A — IMPLEMENTACJA I TESTY OFFLINE
GATE B — SMOKE TEST ONLINE: NIEAUTORYZOWANY / BLOCKED
```

```text
DATE: 2026-08-24
ACCEPTED: UD-M-01–UD-M-07, skorygowany zakres plików, backup, rollback,
AC-M-01–AC-M-17, pełny quality gate.
DODATKOWE WARUNKI UŻYTKOWNIKA:
- przed implementacją: akceptacja w dokumentacji, aneks D-007, publikacja paczki
  w 03-AKTYWNE-PACZKI/, kontrola + secret-scan, jeden commit dokumentacyjny
  "SKOOP-MASSIVE-ACCESS-001: accept revision 2 and authorize offline Gate A",
  push wyłącznie dokumentacji do Dareon99/skanerakcji@main, kontrola HEAD;
- Gate A wyłącznie przy rzeczywistym, zweryfikowanym dostępie do
  C:\SKOOP Skaner wykresów\ i C:\SKOOP-dane\; w przeciwnym razie STOP rule,
  zero pozorowanej implementacji, kompletny handoff dla lokalnego wykonawcy;
- bezwzględne blokady Gate A: zero prawdziwego klucza, zero tworzenia pliku
  klucza za użytkownika, zero połączeń z dostawcami, zero UNIVERSE, zero zmian
  i uruchomień OLD, zero zapisu do frozen baz, zero Gate B, bez aktualizacji
  MASTER/STAN wynikami implementacji;
- quality gate Gate A bez finalnego FREEZE — FREEZE dopiero po Gate B,
  akceptacji wyników i FINAL-AS-BUILT;
- po Gate A: raport 10-punktowy i STOP; następny krok:
  USER AUTHORIZATION OF CONTROLLED GATE B SMOKE TEST.
```

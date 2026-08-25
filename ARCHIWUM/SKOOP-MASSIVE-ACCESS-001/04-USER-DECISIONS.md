# USER DECISIONS — SKOOP-MASSIVE-ACCESS-001

Dokument append-only. Rozstrzygnięcia użytkownika z 2026-08-24 dopisane w sekcji
„Rozstrzygnięcia" na końcu; pierwotne opisy opcji pozostają bez zmian.

## UD-M-01 — Gdzie i w jakiej formie żyje klucz Massive dla SKOOP?

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | plik tekstowy w dedykowanym katalogu danych SKOOP poza produktem i poza Git, np. `C:\SKOOP-dane\secrets\massive_key.txt` (dokładna ścieżka do potwierdzenia przez użytkownika) | plik jawny na dysku; wymaga dyscypliny .gitignore i secret-scanu |
| B | zmienna środowiskowa użytkownika Windows | trudniejsza rotacja; wyciek przez zrzuty środowiska/diagnostykę |
| C | Windows Credential Manager / DPAPI | najbezpieczniejsze, ale bardziej złożony kod i trudniejsza diagnostyka |

**Rekomendacja: A** — powtarza sprawdzony, prosty wzorzec OLD, ale w katalogu
danych SKOOP (izolacja od OLD), z secret-scanem i zapisem lokalizacji (nie wartości)
w dokumentacji. Migracja do C możliwa później bez zmiany kontraktu warstw.

## UD-M-02 — Limity startowe zanim smoke test zweryfikuje plan

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | start konserwatywny: pojedyncze żądania sekwencyjne, twardy sufit dzienny (np. 50 żądań na cały smoke test), bez równoległości; dopiero wynik testu ustala robocze limity | wolniejszy smoke test; bardzo niskie ryzyko 429/blokady |
| B | przyjąć parametry r599 (30 tok/s / capacity 90 / cooldown 13 s) jako start | kalibracja pod inny plan; ryzyko natychmiastowych 429 i zaburzenia wyniku testu |

**Rekomendacja: A** — smoke test ma mierzyć plan, a nie go obciążać; parametry
r599 pozostają punktem odniesienia przy ustalaniu limitów PO teście.

## UD-M-03 — Semantyka bezpieczeństwa: fail-open czy fail-closed?

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | warstwa dostępu SKOOP jest **fail-closed**: awaria limitera/koordynacji lub niejasny stan kill switcha = brak ruchu | możliwe przestoje pobierania przy usterce lokalnej |
| B | fail-open jak r599: awaria koordynacji przepuszcza ruch z licznikiem i logiem | ruch może iść mimo intencji zatrzymania; osłabia kill switch |

**Rekomendacja: A** — dla nowego produktu ochrona konta/kosztów jest ważniejsza
niż ciągłość pobierania; ciągłość zapewnia last-good z frozen kontraktu.
Kill switch zawsze nadrzędny i fail-closed niezależnie od wyboru.

## UD-M-04 — Który komputer wykonuje smoke test i przyszłe pobieranie SKOOP?

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | ten komputer: D-007 zostaje doprecyzowane, że zakaz pobrań dotyczył danych OLD, a SKOOP ma osobną, jawną zgodę | wymaga korekty/aneksu decyzji D-007 w rejestrze |
| B | drugi komputer (ten z „pełnym żywym skanerem"): tu tylko dokumentacja | logistyka; dokumentacja i wykonanie rozjadą się na dwa środowiska |

**Rekomendacja: A z jawnym aneksem do D-007** — roadmapa SKOOP (STAN §5) była
pisana dla tego środowiska; bez aneksu każdy przyszły kontrakt będzie kolidował
z literalnym zapisem MASTER §18.

## UD-M-05 — Zakres i budżet smoke testu

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | pełna mapa: po 1–2 żądania na każdą z 10 kategorii z SPEC §4.14 + test 429 pasywny (bez prowokowania); budżet całkowity ≤ 50 żądań | dłuższa lista, ale jednorazowa |
| B | minimum: tylko autoryzacja + katalog instrumentów + 1D; reszta później | kolejne paczki będą wracać po brakujące odpowiedzi; mapa niepełna |

**Rekomendacja: A** — jednorazowy, budżetowany przegląd całej mapy §4.14 daje
kompletne wejście dla UNIVERSE-IMPORT i eliminuje zgadywanie w kolejnych paczkach.

## UD-M-06 — Gdzie pisze tryb testowy?

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | osobny katalog sandbox w danych SKOOP, np. `C:\SKOOP-dane\sandbox\` z własnym plikiem SQLite; kasowalny w całości | żadnych istotnych |
| B | te same przyszłe bazy produkcyjne z flagą `test=1` w rekordach | zanieczyszczenie danych produkcyjnych; trudny rollback |

**Rekomendacja: A** — twarda fizyczna izolacja jest zgodna z zasadą jednego
właściciela zapisu i upraszcza dowód AC-M-08.

## UD-M-07 — Logowanie: szczegółowość i retencja

| Opcja | Opis | Ryzyka |
|---|---|---|
| A | log per żądanie (czas UTC, endpoint zamaskowany, priorytet, kod, opóźnienie, licznik dzienny) + osobny log błędów; retencja 30 dni; rotacja plików | większa objętość plików |
| B | tylko log błędów i liczniki dzienne | za mało dowodów przy diagnozie limitów/kosztów |

**Rekomendacja: A** — pierwsze tygodnie dostępu wymagają pełnej rozliczalności
każdego żądania; retencję można skrócić po stabilizacji.

## Rozstrzygnięcia — 2026-08-24 (zapis 1:1 odpowiedzi użytkownika)

### UD-M-01 — ACCEPTED — OPTION A
```text
ŚCIEŻKA KLUCZA: C:\SKOOP-dane\secrets\massive_key.txt
DOPRECYZOWANIE:
- plik poza repozytorium, kodem produktu, dokumentacją i archiwami projektu;
- dostęp do pliku wyłącznie dla bieżącego użytkownika Windows;
- klucz nie może pojawić się w logach, raportach, testach, komunikatach ani interfejsie;
- plik i jego zawartość muszą być objęte kontrolą secret-scan oraz wykluczeniami Git i archiwizacji projektu.
```

### UD-M-02 — ACCEPTED — OPTION A
```text
RUCH: sekwencyjny, bez równoległości
SUFIT CAŁEGO SMOKE TESTU: 50 żądań
Po osiągnięciu limitu system ma zatrzymać test, a nie kontynuować.
Parametry docelowe wolno ustalić dopiero na podstawie wyników testu.
```

### UD-M-03 — ACCEPTED — OPTION A
```text
TRYB: FAIL-CLOSED
KILL SWITCH: nadrzędny i również FAIL-CLOSED
Awaria lub niejednoznaczny stan zabezpieczeń oznacza ZERO nowych żądań do Massive.
Interfejs może nadal pokazywać ostatnie poprawne dane z czytelną informacją o czasie ich aktualizacji.
```

### UD-M-04 — ACCEPTED — OPTION A
```text
KOMPUTER WYKONAWCZY: ten komputer
ANEKS DO D-007: TAK

D-007 pozostaje bez zmian dla OLD:
- OLD nie może pobierać ani aktualizować danych;
- OLD pozostaje lokalny, zamrożony i odizolowany od Massive.

Nowa decyzja ma zezwalać wyłącznie nowemu SKOOP na kontrolowany ruch sieciowy,
każdorazowo w granicach zaakceptowanej paczki i Implementation Contract.
```
Uwaga wykonawcza: aneks (nowa decyzja D-0xx) wpisuje użytkownik/operator do
`04-DECYZJE/DECYZJE-PROJEKTOWE.md` w repozytorium; Claude nie modyfikuje repo.

### UD-M-05 — ACCEPTED — OPTION A
```text
ZAKRES: pełna mapa kategorii danych wskazanych w SPEC
BUDŻET CAŁKOWITY: maksymalnie 50 żądań
429 nie wolno celowo prowokować.

Test ma tylko rozpoznać:
- dostępność endpointów;
- zakres subskrypcji;
- dostępne rynki;
- opóźnienia danych;
- obecność wymaganych pól;
- zakres historii;
- kody błędów i zachowanie dostawcy.

Test nie może uruchamiać pełnego importu UNIVERSE.
```

### UD-M-06 — ACCEPTED — OPTION A
```text
ŚCIEŻKA SANDBOX:
C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\

Sandbox musi być fizycznie odseparowany od OLD oraz przyszłych baz produkcyjnych SKOOP.

Usunięcie sandboxu może nastąpić wyłącznie po:
- zapisaniu dowodów testowych;
- kontroli integralności;
- akceptacji użytkownika;
- wskazaniu dokładnej ścieżki przeznaczonej do usunięcia.

Brak automatycznego kasowania.
```
Korekta względem pierwotnego opisu opcji A: określenie „kasowalny bez śladu"
zostaje wycofane; obowiązuje powyższa procedura usunięcia.

### UD-M-07 — ACCEPTED — OPTION A
```text
RETENCJA LOGÓW: 30 dni
ROTACJA: obowiązkowa
KATALOG: C:\SKOOP-dane\logs\massive\

Log może zawierać: czas UTC; nazwę lub szablon endpointu; kategorię i priorytet
żądania; kod odpowiedzi; czas odpowiedzi; liczbę otrzymanych rekordów; licznik
żądań; kod błędu i bezpieczny kontekst diagnostyczny.

Log nie może zawierać: klucza API; nagłówków autoryzacyjnych; pełnego URL
z parametrami autoryzacyjnymi; pełnych odpowiedzi API; sekretów ani danych
umożliwiających ich odtworzenie.

Obowiązkowy test po smoke teście:
liczba wystąpień rzeczywistego klucza w kodzie, logach, raportach i dokumentacji = 0.
```

## Gate

- wszystkie pytania rozstrzygnięte: **YES — UD-M-01…UD-M-07 ACCEPTED 2026-08-24**;
- można przygotować Implementation Contract: **YES — przygotowany; czeka na osobną akceptację**;
- Gate A offline: **AUTHORIZED**;
- można używać prawdziwego klucza/sieci: **NO — Gate B wymaga osobnej jawnej zgody po PASS Gate A**.

# CONFLICT REPORT — SKOOP-MASSIVE-ACCESS-001

```text
STATUS: CLOSED FOR THIS PACKAGE — ALL DECISIONS ACCEPTED 2026-08-24
STOP ACTIVE: YES — UNTIL EXPLICIT USER ACCEPTANCE OF IMPLEMENTATION CONTRACT
```

| ID | Źródło A | Źródło B | Konflikt | Wpływ | Decyzja |
|---|---|---|---|---|---|
| CM-01 | wzorzec OLD: klucz w `skaner-dane\polygon_key.txt` obok danych OLD | wymaganie izolacji SKOOP od OLD (D-006) | lokalizacja i forma sekretu nowego SKOOP nie jest ustalona; współdzielenie katalogu OLD mieszałoby produkty | bezpieczeństwo, rotacja, .gitignore, backupy | **RESOLVED 2026-08-24 — UD-M-01 A**: `C:\SKOOP-dane\secrets\massive_key.txt`, dostęp tylko bieżący użytkownik, pełne wykluczenia |
| CM-02 | parametry r599 (30 tok/s, 90, cooldown 13 s) skalibrowane pod plan OLD | wymóg „nie zakładaj planu Massive"; limity mają wyjść ze smoke testu | jakich limitów startowych użyć ZANIM smoke test je zweryfikuje | ochrona API i koszt | **RESOLVED 2026-08-24 — UD-M-02 A**: sekwencyjnie, sufit 50 żądań, twardy stop po limicie |
| CM-03 | r599: FAIL-OPEN jako kontrakt managera (D-002) | nowe wymagania: kill switch i ochrona przed niekontrolowanym zużyciem | fail-open przy awarii koordynacji może przepuszczać ruch mimo intencji zatrzymania | semantyka bezpieczeństwa | **RESOLVED 2026-08-24 — UD-M-03 A**: FAIL-CLOSED; kill switch nadrzędny i fail-closed |
| CM-04 | MASTER §18 / D-007: `NO FURTHER DOWNLOADS ON THIS COMPUTER`; „pełny żywy skaner na drugim komputerze" | STAN §5: `SKOOP-MASSIVE-ACCESS-001` jako krok 3 roadmapy SKOOP | nie jest zapisane, KTÓRY komputer wykona smoke test i przyszłe pobieranie SKOOP; D-007 dotyczył danych OLD, ale zapis w MASTER jest szeroki | miejsce implementacji | **RESOLVED 2026-08-24 — UD-M-04 A**: ten komputer + aneks do D-007 (zakaz zostaje dla OLD; zgoda tylko dla SKOOP per paczka/kontrakt) |
| CM-05 | gate: zero sieci i zero sekretów do akceptacji kontraktu | smoke test wymaga klucza i sieci | smoke test NIE może być częścią tej paczki; musi być jawnie autoryzowany w Implementation Contract kolejnej paczki z budżetem żądań | kolejność paczek | **RESOLVED 2026-08-24 — UD-M-05 A**: pełna mapa, ≤50 żądań, bez prowokowania 429, bez importu UNIVERSE; wykonanie dopiero po akceptacji Implementation Contract |

Pozycje bez konfliktu: **UD-M-06 RESOLVED** (sandbox
`C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\`, bez automatycznego kasowania,
usunięcie wyłącznie po dowodach + akceptacji) i **UD-M-07 RESOLVED**
(pełny log per żądanie, 30 dni, rotacja, katalog `C:\SKOOP-dane\logs\massive\`,
twarda lista zakazów treści + obowiązkowy secret-scan po smoke teście).

Pozostały gate: brak nowych konfliktów; jedyną blokadą implementacji jest
osobna, jawna akceptacja `05-IMPLEMENTATION-CONTRACT.md`.

## Bezpieczny stan podczas STOP

- zero żądań Massive/Yahoo; zero sekretów;
- OLD, frozen bazy i placeholder SKOOP bez zmian;
- paczka zmienia wyłącznie własną dokumentację;
- rollback runtime niepotrzebny.

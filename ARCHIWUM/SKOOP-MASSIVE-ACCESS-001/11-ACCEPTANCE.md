# ACCEPTANCE — SKOOP-MASSIVE-ACCESS-001

~~~text
STATUS: ACCEPTED
DATE: 2026-08-25
USER DECISION: WYNIKI GATE B — AKCEPTUJĘ
PRODUCT VERSION: SKOOP FOUNDATION PLACEHOLDER / MASSIVE ACCESS PACKAGE INSTALLED
DOCS VERSION: DOCS-2026-08-25-01
UNIVERSE IMPORT: NOT AUTHORIZED / NOT STARTED
FINAL KILL SWITCH: ON
~~~

## Kryteria

| Kryterium | Wynik | Dowód |
|---|---|---|
| kontrakt rev. 2 zaakceptowany | PASS | 05-IMPLEMENTATION-CONTRACT.md |
| Gate A offline | PASS | 06-TEST-EVIDENCE.md |
| Gate B kontrolowany | PASS | 07-GATE-B-TEST-EVIDENCE.md |
| limit żądań | PASS — 29/50 | traffic-counter i log lokalny |
| statusy S0–S13 bez zgadywania | PASS | 07-GATE-B-TEST-EVIDENCE.md |
| właściwy wymóg 5 lat historii | CONFIRMED — HTTP 200 | GATE-B-FIVE-YEAR-EVIDENCE.json |
| sektor/branża zgodne z decyzją użytkownika | PASS | 08-GATE-B-USER-CORRECTIONS.md |
| brak importu UNIVERSE | PASS — 0 | raport Gate B |
| brak zmian OLD | PASS | 3/3 frozen DB SHA-256 identyczne; 0 plików OLD zmodyfikowanych podczas testu |
| sekrety w dokumentacji/logach | PASS — 0 | secret scan i safe log |
| package integrity | PASS — 12/12 | GATE-B-CODE-HASHES-SHA256.txt |
| kill switch po teście | PASS — ON | kontrola lokalna |

## Przyjęte ograniczenia

- income statements, w tym kwartalne/TTM, są niedostępne w obecnym planie Massive (`403 / UNAVAILABLE_IN_CURRENT_PLAN`);
- pasywne nagłówki rate-limit nie wystąpiły (`S13 UNVERIFIED`), a 429 nie prowokowano;
- float nie wystąpił w testowanej odpowiedzi szczegółów spółki;
- splity nie zostały zweryfikowane w tej paczce; dywidendy są potwierdzone;
- część pól IPO jest opcjonalna i nie wystąpiła w pierwszej próbce.

## Decyzje wiążące

- SKOOP używa historii do 5 lat; dłuższe okresy użytkownik sprawdza w TradingView;
- Massive dostarcza surową informację klasyfikacyjną, w tym SIC;
- kanoniczne `canonical_sector` i `canonical_industry` nadaje SKOOP;
- nazwy i taksonomia są synchronizowane z TradingView;
- mapowanie ma wersję, źródło, czas zmiany użytkownika i ręczny override.

## Zakres akceptacji

Akceptacja zamyka wyłącznie paczkę dostępu i smoke testu Massive. Nie zezwala
na import UNIVERSE, utworzenie bazy produktu, uruchomienie workerów ani stały
ruch do providera. Każdy taki etap wymaga następnej małej paczki i kontraktu.

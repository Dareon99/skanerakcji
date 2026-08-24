# SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
STATUS: ACCEPTED / FROZEN — LOGICAL SPEC ONLY
AREA: COMPANY-DATA
RUNTIME CHANGE: NONE
NETWORK/MASSIVE: NOT AUTHORIZED
DATABASE WRITE: NOT AUTHORIZED
```

## Cel

Zamknąć logiczny kontrakt pełnego UNIVERSE, kwalifikacji BASE, okna IPO i pól
listingu przed utworzeniem nowej bazy SKOOP.

## Obowiązujący gate

1. `01-SPEC.md` — wszystkie wymagane decyzje zapisane; gotowy do finalnego acceptance;
2. `02-AUDIT.md` — wykonany read-only;
3. `03-CONFLICT-REPORT.md` — zamknięty dla obecnego kontraktu; C-09 jawnie deferred;
4. `04-USER-DECISIONS.md` — wszystkie wymagane decyzje rozstrzygnięte;
5. `05-IMPLEMENTATION-CONTRACT.md` — dokumentacyjne zamknięcie gotowe do acceptance; brak zgody na runtime;
6. `10-CLAUDE-EXECUTION-SPEC.md` — gotowa instrukcja przekazania wykonawcy;
7. `11-CLAUDE-START-COMMAND.md` — gotowe polecenie startowe z kontrolą gate;
8. implementacja, Massive, SQL i UI — zabronione.

## Stan bezpieczny

OLD, jego dane, launchery oraz nowy placeholder SKOOP pozostają bez zmian. Ta paczka
jest wyłącznie dokumentacyjna do końcowego acceptance logicznego SPEC.
Przygotowanie instrukcji dla Claude nie zmienia tego statusu i nie jest zgodą na
kodowanie.

Postęp decyzji i finalny SPEC: `ACCEPTED 2026-08-24`. Implementacja nadal
zabroniona do utworzenia i osobnej akceptacji małej paczki kodowej.

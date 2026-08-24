# PROTOKÓŁ SESJI AI — CHATGPT / CODEX / CLAUDE

## 1. Start sesji

AI czyta kompletnie, w kolejności:

1. `MASTER-PROJEKT.md`;
2. `STAN-AKTUALNY.md`;
3. `00-STEROWANIE/ZASADY-PROJEKTU.md`;
4. `04-DECYZJE/DECYZJE-PROJEKTOWE.md`;
5. właściwy FINAL-AS-BUILT;
6. aktywną paczkę i ostatni handoff sesji;
7. wskazane artefakty — tylko te potrzebne do zadania.

Następnie AI publikuje Session Opening Report:

```text
PROJECT:
VERSION:
RUNTIME:
MANAGER FLAG:
ACTIVE PACKAGE:
LAST ACCEPTED PACKAGE:
CONFIRMED INPUTS:
CONFLICTS:
UNVERIFIED / TO RECOVER:
SAFE NEXT STEP:
USER DECISION REQUIRED:
```

## 2. W trakcie sesji

- zapisuj fakty do `06-SESJE/SESJA-BIEZACA.md`;
- decyzje użytkownika zapisuj od razu w aktywnej paczce;
- nie przepisuj dużych logów do MASTER;
- każdą zmianę zakresu zgłoś przed implementacją;
- po wykryciu konfliktu utwórz Conflict Report i zastosuj STOP;
- podawaj ścieżki do dowodów, nie tylko opis słowny.

## 3. Zamknięcie sesji

Handoff musi zawierać:

```text
SESSION ID / DATE:
PACKAGE:
FILES CHANGED:
STATE CHANGED:
TESTS ACTUALLY RUN:
RESULTS:
DATABASE / NETWORK EFFECTS:
DECISIONS RECORDED:
OPEN RISKS:
ROLLBACK:
EXACT NEXT STEP:
```

Jeśli stan projektu zmienił się, uaktualnij `STAN-AKTUALNY.md`. Jeżeli nie zmienił się, wpisz w handoffie `NO STATE CHANGE`.

## 4. Przekazanie między AI

ChatGPT, Codex i Claude nie dzielą gwarantowanej pamięci rozmów. Przekazanie jest kompletne tylko wtedy, gdy kolejna sesja otrzyma dostęp do repozytorium/katalogu oraz wykona protokół startowy.

Nie należy przekazywać całej historii czatu jako substytutu dokumentacji. Z rozmowy odzyskuje się: decyzje, wymagania, otwarte pytania i linki do artefaktów, a następnie zapisuje je w odpowiednich rejestrach.

## 5. Awaria lub brak dostępu

Jeśli AI nie może przeczytać któregoś obowiązkowego pliku:

1. nie wykonuje zmiany;
2. raportuje brakującą ścieżkę;
3. oznacza sesję `BLOCKED — INCOMPLETE PROJECT CONTEXT`;
4. prosi o udostępnienie pliku lub pełnego pakietu frozen.

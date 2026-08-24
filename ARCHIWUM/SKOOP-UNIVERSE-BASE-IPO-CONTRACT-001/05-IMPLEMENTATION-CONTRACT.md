# IMPLEMENTATION CONTRACT — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
STATUS: DECISION GATE PASSED — READY FOR FINAL SPEC ACCEPTANCE
PRODUCT VERSION BEFORE: SKOOP FOUNDATION PLACEHOLDER / NO PRODUCT VERSION
PRODUCT VERSION AFTER: UNDEFINED
AUTHORIZED RUNTIME LEVEL: L1 — DOCUMENTATION CLOSURE ONLY
```

## Dokładny zakres

| Plik/zasób | Dozwolona zmiana | Niedozwolona zmiana |
|---|---|---|
| aktywna paczka dokumentacyjna | finalna kontrola, acceptance, AS-BUILT, freeze i synchronizacja Git | kod, SQL, baza, runtime, sieć |

Wszystkie decyzje użytkownika UD-01–UD-06 i UD-09 zamknięto 2026-08-24. Konflikty
C-01–C-04 i C-10 są zamknięte; C-09 został jawnie przeniesiony do późniejszej
paczki market-sync.

Ta paczka zamyka wyłącznie kontrakt logiczny i dokumentację. Nie autoryzuje kodu,
SQL, bazy, runtime, sekretu ani ruchu Massive. Po końcowym acceptance zostanie
zamrożona jako wejście do osobnych małych paczek implementacyjnych.

Ten kontrakt danych nie autoryzuje implementacji wyglądu listingu. Przed kodowaniem
listingu obowiązuje zaakceptowana paczka `SKOOP-COMPANY-LISTING-DESIGN-001` zgodnie
z UD-21.

## Kolejność wykonania

1. finalny preflight spójności SPEC/AUDIT/CONFLICT/DECISIONS;
2. kontrola, że OLD, runtime i bazy nie zostały zmienione;
3. LAST WRITE dokumentacji;
4. kontrola integralności Markdown, statusów, hashy i zakresu Git;
5. przedstawienie końcowego SPEC użytkownikowi;
6. acceptance albo korekta;
7. po acceptance: AS-BUILT, FREEZE i synchronizacja Git.

## Backup i rollback

- backup path/nazwa: historia Git dokumentacji, HEAD przed decyzjami `d7772e6`;
- warunek rollbacku: użytkownik odrzuca finalny SPEC lub wykryto rozbieżność;
- dokładna procedura rollbacku: nie force-push; utworzyć korektę/SUPERSEDES w nowej
  wersji dokumentacji albo odrzucić paczkę przed freeze;
- dane pozostające jako dowód: decyzje append-only, conflict report, test evidence i Git diff.

## Test contract

| Test | Polecenie/metoda | Oczekiwane | Skutki uboczne |
|---|---|---|---|
| decyzje | kontrola statusów UD-01–UD-21 | wymagane pozycje rozstrzygnięte | brak |
| konflikty | kontrola C-01–C-17 | brak otwartego konfliktu blokującego obecny kontrakt; C-09 jawnie deferred | brak |
| dokumenty | Markdown fences, odwołania, pending-list i hashe | PASS | brak |
| zakres | Git diff i secret/forbidden-path scan | wyłącznie dokumentacja; 0 sekretów/baz | brak |

## STOP conditions

- source/version drift;
- nieplanowana zmiana pliku/bazy;
- fail testu/gate;
- nieplanowany ruch sieciowy;
- zakres wychodzi poza paczkę;
- rollback nie jest pewny.

## Zgoda

```text
USER ACCEPTANCE OF FINAL LOGICAL SPEC:
FINALNY SPEC UNIVERSE–BASE–IPO — AKCEPTUJĘ
DATE: 2026-08-24
LIMITS/NOTES: akceptacja kontraktu logicznego i dokumentacji; nie jest zgodą na kod, SQL, bazę, runtime, sekret ani Massive
```


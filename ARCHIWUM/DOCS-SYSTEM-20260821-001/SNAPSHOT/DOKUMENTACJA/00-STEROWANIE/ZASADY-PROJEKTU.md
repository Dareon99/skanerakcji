# ZASADY PROJEKTU — KANONICZNE

Zmiana zasady wymaga jawnej decyzji użytkownika wpisanej do `DECYZJE-PROJEKTOWE.md`. Zasady 1–12 odzyskano z r599; kolejne porządkują trwały system dokumentacji.

1. Użytkownik zatwierdza każdą zmianę projektową. Przy niejednoznaczności AI zgłasza `DECISION REQUIRED`.
2. Cykl zmiany: SPEC → AUDIT → CONFLICT REPORT → USER DECISIONS → IMPLEMENTATION CONTRACT → PACKAGE → TESTS → ACCEPTANCE.
3. Każda paczka produkcyjna ma backup podmienianych plików i testowalny rollback.
4. Testy muszą być rzeczywiście uruchomione, jeśli środowisko na to pozwala; inaczej status to `BLOCKED FOR LOCAL ACCEPTANCE`.
5. Finalny sanity review wykonuje się po ostatniej zmianie; zapis po gate/hash unieważnia gate.
6. Zero cross-DB write transactions dla baz biznesowych; jeden executor zapisu na plik biznesowy.
7. `provider_state.db` jest jedynym formalnym wyjątkiem multi-writer, zgodnie z D-001; wyjątek nie dotyczy baz biznesowych.
8. Decyzje są append-only; nowa decyzja zastępuje starą przez `SUPERSEDES`.
9. Wydania kodu mają `VERSION = YYYY-MM-DD-rNNN`; zmiana kodu produkcyjnego bez podbicia VERSION jest zakazana, chyba że zaakceptowany kontrakt jawnie dowodzi wyjątku dokumentacyjnego/test-only.
10. Przy stale/awarii providera konsument utrzymuje last-good; `NULL != 0`.
11. Sekrety nie wchodzą do zdarzeń, stanów, dokumentów, logów ani Git.
12. Import modułów infrastrukturalnych jest wolny od skutków ubocznych.
13. MASTER, STAN i odpowiedni AS-BUILT są obowiązkowym wejściem każdej sesji AI.
14. Jedna zmiana = jedna izolowana paczka; nie wolno naprawiać problemów sąsiednich „przy okazji”.
15. Frozen ARCHIWUM jest immutable; korekta powstaje jako nowa paczka superseding.
16. Duże logi, screenshoty i załączniki pozostają artefaktami; MASTER zawiera opis, identyfikator, ścieżkę i hash.
17. Brak dowodu oznacza `UNVERIFIED/TO RECOVER`, nigdy uzupełnienie z pamięci.
18. Uruchomienie, restart, aktywacja flag, pobieranie produkcyjne i mutacja baz wymagają jawnej zgody oraz kontraktu.
19. Żaden push do zdalnego repozytorium ani publikacja artefaktu nie odbywa się automatycznie.
20. Każde zamknięcie sesji aktualizuje STAN lub jawnie potwierdza `NO STATE CHANGE`.

## Mandatory quality gate

```text
LAST WRITE
→ py_compile
→ AST
→ invalid escape / static / sanity
→ tests
→ package integrity
→ hashes
→ FREEZE
```

Nie wolno oznaczyć paczki `ACCEPTED/FROZEN`, jeśli którykolwiek obowiązkowy krok jest niewykonany, nieudokumentowany albo wykonany przed ostatnim zapisem.

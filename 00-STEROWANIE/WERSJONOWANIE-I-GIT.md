# WERSJONOWANIE I GIT

## 1. Trzy niezależne identyfikatory

| Typ | Format | Przykład | Kiedy zmieniać |
|---|---|---|---|
| wersja produktu | `YYYY-MM-DD-rNNN` | `2026-08-21-r599` | zaakceptowana zmiana kodu produkcyjnego |
| wersja dokumentacji | `DOCS-YYYY-MM-DD-NN` | `DOCS-2026-08-21-01` | zmiana systemu źródła prawdy |
| identyfikator paczki | `<AREA>-YYYYMMDD-###` | `CHARTS-RESTORE-20260821-001` | każda izolowana zmiana |

Numer paczki nie zastępuje VERSION. Dokumentacyjny sprint bez zmiany kodu nie musi zmieniać VERSION produktu.

## 2. Stan bieżący

- dokumentacja ma własne lokalne repozytorium Git na gałęzi `main`;
- zdalny mirror to `https://github.com/Dareon99/skanerakcji.git`;
- pierwszy commit dokumentacji: `5218bf2`, opublikowany 2026-08-24;
- repo-local identity: `Dareon99` i adres GitHub noreply;
- repozytorium zawiera dokumentację i odzyskane referencje, nie runtime ani bazy;
- stan Git starego `C:\Skaner wykresów` jest odrębną sprawą i nie upoważnia do
  uruchomienia lub publikacji kodu OLD.

## 3. Model gałęzi

- `main` — wyłącznie zaakceptowany i zamrożony stan;
- `work/<package-id>` — jedna aktywna paczka;
- `recovery/<package-id>` — recovery bez zmiany produkcji;
- `hotfix/<package-id>` — tylko dla zaakceptowanej naprawy krytycznej.

Bez bezpośrednich commitów implementacyjnych do `main`. Integracja do `main` następuje po acceptance, AS-BUILT i FREEZE.

## 4. Commity

Format:

```text
<PACKAGE-ID>: <krótki rezultat>

Scope: ...
Tests: ...
Decision: D-xxx / none
Risk: ...
```

Zalecane granice commitów:

1. dokumenty SPEC/AUDIT/CONTRACT;
2. mała implementacja;
3. test evidence i AS-BUILT;
4. finalna aktualizacja MASTER/STAN/FREEZE.

## 5. Tagi

- zaakceptowany release produktu: `scanner-r599`;
- frozen paczka bez release: `package/<package-id>`;
- wersja systemu dokumentacji: `docs/DOCS-2026-08-21-01`.

Tag tworzy się dopiero po zgodnych hashach i acceptance. Nie tworzy się tagu dla stanu roboczego.

## 6. Pierwsza inicjalizacja — wymagana kolejność

1. zainstalować `.gitignore` i `.gitattributes`;
2. wykonać secret scan bez wypisywania wartości;
3. `DONE` — `git init -b main`;
4. sprawdzić `git status --short --ignored`;
5. `PENDING` — skonfigurować repo-local `user.name` i `user.email` po decyzji użytkownika;
6. przygotować jawny zakres pierwszego commitu;
7. zatwierdzić pierwszy commit;
8. dopiero potem, osobną decyzją, dodać remote i wykonać push.

## 7. Zakres pierwszego commitu

Pierwszy commit został celowo ograniczony do dokumentacji dostępnej dla Claude:

- MASTER, STAN, zasady, decyzje, aktywna paczka i AS-BUILT;
- repozytoryjny `CLAUDE.md`, `.gitignore` i `.gitattributes`;
- świadomie dołączone frozen artefakty dokumentacyjne, payloady testowe i
  screenshoty w `ARCHIWUM`.

Nie weszły: runtime SKOOP/OLD, `BACKUP-*`, `DATA-*`, `.venv`, produkcyjne bazy,
klucze i logi. Publikacja kodu aplikacji wymaga osobnej paczki i kontraktu.

## 8. Zdalne repozytorium

- provider: GitHub;
- remote: `origin = https://github.com/Dareon99/skanerakcji.git`;
- branch: `main`;
- logowanie: Git Credential Manager konta Windows użytkownika;
- widoczność repozytorium: `UNVERIFIED` w lokalnym audycie — nie wolno zakładać,
  że repo jest publiczne lub prywatne bez sprawdzenia ustawień GitHub;
- każdy kolejny push pozostaje operacją L6 i wymaga jawnego zakresu oraz zgody.

## 9. Recovery Git

Po każdym zaakceptowanym sprincie:

```text
acceptance → AS-BUILT → hashes → FREEZE → commit → tag → opcjonalny push
```

Jeśli Git i dokumentacja wskazują różne wersje, obowiązuje STOP i Conflict Report.

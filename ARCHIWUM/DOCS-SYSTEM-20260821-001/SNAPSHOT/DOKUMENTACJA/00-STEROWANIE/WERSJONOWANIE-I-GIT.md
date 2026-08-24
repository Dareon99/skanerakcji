# WERSJONOWANIE I GIT

## 1. Trzy niezależne identyfikatory

| Typ | Format | Przykład | Kiedy zmieniać |
|---|---|---|---|
| wersja produktu | `YYYY-MM-DD-rNNN` | `2026-08-21-r599` | zaakceptowana zmiana kodu produkcyjnego |
| wersja dokumentacji | `DOCS-YYYY-MM-DD-NN` | `DOCS-2026-08-21-01` | zmiana systemu źródła prawdy |
| identyfikator paczki | `<AREA>-YYYYMMDD-###` | `CHARTS-RESTORE-20260821-001` | każda izolowana zmiana |

Numer paczki nie zastępuje VERSION. Dokumentacyjny sprint bez zmiany kodu nie musi zmieniać VERSION produktu.

## 2. Stan bieżący

- `C:\Skaner wykresów` ma lokalne repozytorium Git na gałęzi `main`;
- repozytorium jest puste: pliki nie zostały dodane i nie wykonano pierwszego commitu;
- globalne `user.name` i `user.email` nie są skonfigurowane;
- zdalne repozytorium nie jest skonfigurowane;
- pierwsza inicjalizacja nie może automatycznie publikować kodu.

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

Do pierwszego commitu powinny wejść:

- bieżący kod `backend` bez cache, backupów, baz i sekretów;
- `DOKUMENTACJA`;
- root `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.gitattributes`;
- niezbędne pliki uruchomieniowe i referencje tekstowe.

Nie powinny wejść: `BACKUP-*`, `DATA-*`, stare paczki instalacyjne, `.venv`, wyniki generowane, bazy, klucze i logi. Wyjątek stanowią świadomie dołączone frozen artefakty w `DOKUMENTACJA/ARCHIWUM`.

## 8. Zdalne repozytorium

Provider, URL, prywatność, metoda logowania i zasady backupu są `DECISION REQUIRED`. Do czasu decyzji:

- nie dodawać remote;
- nie wykonywać push;
- lokalny Git może zapewniać historię, ale nie stanowi kopii zapasowej poza komputerem.

## 9. Recovery Git

Po każdym zaakceptowanym sprincie:

```text
acceptance → AS-BUILT → hashes → FREEZE → commit → tag → opcjonalny push
```

Jeśli Git i dokumentacja wskazują różne wersje, obowiązuje STOP i Conflict Report.

# DOSTĘPY I BEZPIECZEŃSTWO

## 1. Macierz dostępu

| Zasób | Właściciel | Użytkownik | ChatGPT/Codex | Claude | Git remote | Status |
|---|---|---|---|---|---|---|
| `C:\Skaner wykresów` | użytkownik | RW | zależnie od udostępnionego workspace | zależnie od udostępnionego folderu | brak | `LOCAL ONLY` |
| `C:\skaner-dane` | użytkownik | RW | read/write tylko po kontrakcie i zgodzie | jw. | zakazane | `PRODUCTION DATA` |
| `DOKUMENTACJA` | użytkownik | RW | RW w zakresie zadania | RW w zakresie zadania | docelowo tak | `CANONICAL` |
| `DOKUMENTACJA/ARCHIWUM` | użytkownik | RW administracyjne | read-only po FREEZE | read-only po FREEZE | tak, jeśli rozmiar/zasady pozwalają | `IMMUTABLE` |
| Konto/klucz Massive | użytkownik | zarządza | nie ujawniać | nie ujawniać | zakazane | `SECRET` |
| `Dareon99/skanerakcji` | użytkownik | zarządza | push tylko po jawnej zgodzie L6 | odczyt przez udostępniony GitHub | dokumentacja bez sekretów i baz | `CONNECTED / PUBLISHED` |

RW oznacza możliwość zapisu, ale nie autoryzuje zmiany produkcyjnej. Autoryzację określa aktywna paczka i Implementation Contract.

## 2. Zasady sekretów

- klucz API nigdy nie trafia do Markdown, raportu, screenshotu, commit message ani outputu testów;
- Git ignoruje `.env`, pliki kluczy, credentials i dane bazowe;
- dokumentacja może zawierać nazwę zmiennej lub lokalizację mechanizmu, ale nie wartość;
- przed pierwszym `git add` obowiązuje secret scan;
- wykrycie sekretu w historii Git oznacza STOP, rotację sekretu i czyszczenie historii w osobnej procedurze.

Aktualny audit recovery nie wykrył niepustego hardcoded klucza w bieżącym `backend/config.py`. Jest to snapshot, nie stała gwarancja.

## 3. Poziomy operacji

| Poziom | Przykład | Wymagana zgoda |
|---|---|---|
| L0 — read-only | czytanie kodu, logów, dokumentów | w zakresie zadania |
| L1 — dokumentacja | aktualizacja MASTER/STAN/rejestrów | aktywna paczka lub jawne zlecenie dokumentacyjne |
| L2 — kod offline | zmiana kodu bez uruchomienia runtime | Implementation Contract |
| L3 — test lokalny | test mogący tworzyć pliki tymczasowe | kontrakt testu |
| L4 — runtime | start/restart aplikacji, scheduler, provider | jawna zgoda użytkownika |
| L5 — produkcyjne dane/flagi | manager ON, migracja, zapis baz | osobna zgoda, backup, rollback, monitoring |
| L6 — publikacja | push, release, wysłanie artefaktu | jawna zgoda użytkownika |

## 4. Udostępnianie nowej sesji

Minimalny pakiet dostępu:

- repozytorium lub folder `C:\Skaner wykresów`;
- komplet `DOKUMENTACJA`;
- bezpośrednio dostępny odpowiedni AS-BUILT;
- aktywna paczka;
- dane tylko wtedy, gdy zadanie ich wymaga i użytkownik je udostępnił.

Jeśli repozytorium online nie jest dostępne dla danego AI, użytkownik przekazuje frozen pakiet lub otwiera sesję w workspace zawierającym projekt.

## 5. Rejestr dostępu

Zmiany w dostępie zapisuje się jako wpis w tym dokumencie lub osobnej zaakceptowanej decyzji:

| Data | Zasób | Zmiana | Zatwierdził | Dowód |
|---|---|---|---|---|
| 2026-08-21 | lokalny projekt | stan początkowy: lokalnie, bez remote Git | użytkownik / recovery | `PROJECT-RECOVERY-001` |
| 2026-08-24 | dokumentacja SKOOP | pierwszy push `main` do `Dareon99/skanerakcji`; dostęp Claude przez repo | użytkownik | commit `5218bf2`; `02-AS-BUILT/GITHUB-DOCS-PUBLISH-20260824-001-AS-BUILT.md` |

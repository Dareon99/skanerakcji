# AGENTS.md — obowiązkowe zasady pracy AI

Dotyczy całego repozytorium „Skaner wykresów”.

## 1. Obowiązkowy start każdej sesji

Przed analizą lub zmianą przeczytaj w kolejności:

1. `DOKUMENTACJA/MASTER-PROJEKT.md`;
2. `DOKUMENTACJA/STAN-AKTUALNY.md`;
3. `DOKUMENTACJA/00-STEROWANIE/ZASADY-PROJEKTU.md`;
4. `DOKUMENTACJA/04-DECYZJE/DECYZJE-PROJEKTOWE.md`;
5. odpowiedni AS-BUILT wskazany w STAN;
6. kompletną aktywną paczkę, jeżeli istnieje.

Następnie przedstaw krótki Session Opening Report: wersja, stan runtime, aktywna paczka, potwierdzone źródła, konflikty, braki i dokładnie jeden następny krok.

## 2. Źródła prawdy

Kolejność ważności:

1. jawna najnowsza decyzja użytkownika;
2. zaakceptowany Implementation Contract aktywnej paczki;
3. `DECYZJE-PROJEKTOWE.md` — append-only;
4. `MASTER-PROJEKT.md`;
5. `STAN-AKTUALNY.md`;
6. odpowiedni FINAL-AS-BUILT;
7. frozen artefakty i testy;
8. kod produkcyjny;
9. starsze raporty i rozmowy.

Konflikt między źródłami wymaga CONFLICT REPORT i `STOP`.

## 3. Zakaz pracy bez paczki

Zmiana kodu, konfiguracji, schematu, danych, runtime albo kontraktu dokumentacji wymaga jednej aktywnej paczki w `DOKUMENTACJA/03-AKTYWNE-PACZKI/<PACKAGE-ID>/`.

Obowiązkowy workflow:

`SPEC → AUDIT → CONFLICT REPORT → USER DECISIONS → IMPLEMENTATION CONTRACT → SMALL PACKAGE → TEST → ACCEPTANCE → NEXT PACKAGE`.

Nie łącz niezależnych problemów. Brak zgody, drift, błąd gate lub niejednoznaczność oznaczają `STOP`.

## 4. Granice bezpieczeństwa

- Nie uruchamiaj skanera, nie restartuj aplikacji i nie włączaj managera bez jawnej zgody użytkownika oraz kontraktu.
- Nie zapisuj sekretów, kluczy API, tokenów ani danych logowania w repozytorium, raportach lub logach.
- Nie wersjonuj baz, WAL/SHM, `.venv`, cache, logów runtime ani kopii kluczy.
- Nie modyfikuj frozen `DOKUMENTACJA/ARCHIWUM`; korekta wymaga nowej paczki superseding.
- Nie uznawaj `UNVERIFIED` albo `TO RECOVER` za fakt.
- Nie wykonuj zmian produkcyjnych podczas audytu lub recovery read-only.

## 5. Quality gate

Po ostatnim zapisie wykonaj w tej kolejności:

`LAST WRITE → py_compile → AST → invalid escape/static/sanity → tests → package integrity → hashes → FREEZE`.

Każda zmiana po gate lub po hashach unieważnia wynik i wymaga powtórzenia kontroli.

## 6. Zamknięcie sesji

Przed zakończeniem zaktualizuj odpowiednio:

- `STAN-AKTUALNY.md`;
- dziennik aktywnej sesji;
- rejestr decyzji, jeśli użytkownik podjął decyzję;
- rejestr sprintów;
- MASTER tylko wtedy, gdy zmieniło się trwałe źródło prawdy;
- FINAL-AS-BUILT po akceptacji implementacji;
- hashe i FREEZE po ostatnim zapisie.

W finalnym handoffie wskaż: co zmieniono, co przetestowano, czego nie wykonano, aktualne ryzyko, rollback i jeden następny pakiet.

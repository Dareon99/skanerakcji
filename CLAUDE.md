# CLAUDE — START Z REPOZYTORIUM DOKUMENTACJI SKOOP

To repozytorium zawiera kanoniczną dokumentację projektu, odzyskane dowody i
referencje. Nie zawiera działającego runtime SKOOP ani produkcyjnych baz danych.

## Obowiązkowy start

Przeczytaj w całości, w tej kolejności:

1. `README.md`;
2. `MASTER-PROJEKT.md`;
3. `STAN-AKTUALNY.md`;
4. `00-STEROWANIE/ZASADY-PROJEKTU.md`;
5. `00-STEROWANIE/PROTOKOL-SESJI-AI.md`;
6. `04-DECYZJE/DECYZJE-PROJEKTOWE.md`;
7. wszystkie pliki aktywnej paczki wskazanej w
   `03-AKTYWNE-PACZKI/README.md`.

Dla bieżącego kontraktu przeczytaj szczególnie:

- `03-AKTYWNE-PACZKI/SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001/10-CLAUDE-EXECUTION-SPEC.md`;
- `03-AKTYWNE-PACZKI/SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001/11-CLAUDE-START-COMMAND.md`.

## Zasady dostępu przez GitHub

- katalog główny repozytorium jest w tej sesji źródłem prawdy;
- ścieżki `C:\...` zapisane w dokumentach opisują komputer właściciela projektu;
  ich niedostępność w środowisku GitHub nie jest sama w sobie konfliktem;
- nie zakładaj dostępu do lokalnego kodu, baz, OLD ani klucza Massive;
- nie twórz zamienników brakujących zasobów i nie uzupełniaj faktów domysłem;
- brak oznacz `UNVERIFIED` albo `TO RECOVER`, a konflikt `STOP`;
- dokumenty OLD i archiwalne roadmapy są referencją, nie zgodą na przeniesienie
  starych mechanizmów do SKOOP.

## Bieżący gate

Kontrakt `SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001` ma status `ACCEPTED/FROZEN` jako
logiczny SPEC. Nie istnieje jeszcze aktywna paczka implementacyjna. Kod, SQL, baza,
runtime, sekret i Massive pozostają nieautoryzowane do jawnej akceptacji osobnego
kontraktu małej paczki.

Bez takiej akceptacji nie zmieniaj kodu, SQL, bazy, runtime ani konfiguracji, nie
używaj Massive i nie uruchamiaj workerów. Najpierw zwróć raport otwarcia sesji
określony w `10-CLAUDE-EXECUTION-SPEC.md`.

`UD-01–UD-06` i `UD-09` zostały zaakceptowane 2026-08-24 i zapisane jako
`D-009` oraz `D-011–D-016`.

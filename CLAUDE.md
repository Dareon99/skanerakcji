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

Dla ostatniej ukończonej paczki przeczytaj szczególnie:

- `ARCHIWUM/SKOOP-MASSIVE-ACCESS-001/12-FINAL-AS-BUILT-SPEC.md`;
- `ARCHIWUM/SKOOP-MASSIVE-ACCESS-001/11-ACCEPTANCE.md`;
- `ARCHIWUM/SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001/08-FINAL-AS-BUILT.md`.

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

`SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001` oraz `SKOOP-MASSIVE-ACCESS-001` mają
status `ACCEPTED/FROZEN`. Gate B zakończył się licznikiem 29/50, kill switch ON,
bez importu UNIVERSE i bez zmian OLD. Pięć lat historii 1D jest potwierdzone.
Sektor/branża są kanonicznym mapowaniem SKOOP synchronizowanym z TradingView;
SIC Massive jest informacją pomocniczą.

Nie istnieje aktywna paczka implementacyjna. Następna paczka jest tylko
proponowana: `SKOOP-UNIVERSE-IMPORT-001`. Bez jej SPEC, audytu, decyzji i
zaakceptowanego Implementation Contract nie wolno wykonywać importu, paginacji,
tworzyć bazy produktu, uruchamiać workerów ani stałego ruchu Massive.

Decyzje wiążące: D-009–D-019, z zachowaniem ich zakresów i SUPERSEDES.

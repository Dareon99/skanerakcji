# AKTYWNE PACZKI

W jednym czasie może istnieć najwyżej jedna paczka ze statusem `IN PROGRESS`,
chyba że użytkownik zatwierdzi izolowaną pracę równoległą.

Aktualny stan: **brak aktywnej paczki implementacyjnej**.

Ostatnia ukończona paczka:

~~~text
SKOOP-MASSIVE-ACCESS-001
STATUS: ACCEPTED / FROZEN
MASSIVE: 29/50 CONTROLLED REQUESTS
UNIVERSE IMPORT: NOT STARTED
FINAL KILL SWITCH: ON
ARCHIVE: ARCHIWUM/SKOOP-MASSIVE-ACCESS-001
~~~

Poprzedni kontrakt `SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001` pozostaje
`ACCEPTED/FROZEN` jako logiczne źródło prawdy.

Następna paczka jest wyłącznie proponowana:
`SKOOP-UNIVERSE-IMPORT-001`. Nie została utworzona ani autoryzowana.

Samo istnienie zaakceptowanej paczki dostępu nie autoryzuje importu, paginacji,
tworzenia bazy produktu, workerów ani stałego ruchu do Massive.

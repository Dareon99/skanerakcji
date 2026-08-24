# AKTYWNE PACZKI

W jednym czasie może istnieć najwyżej jedna paczka ze statusem `IN PROGRESS`, chyba że użytkownik zatwierdzi izolowaną pracę równoległą.

Aktualny stan: **brak aktywnej paczki implementacyjnej**.

Rekomendowany następny identyfikator:

```text
CHARTS-RESTORE-20260821-001
```

Cel: kontrolowany start zaakceptowanego r599 z managerem ON oraz test starej ścieżki `/candles/{symbol}` dla jednego symbolu. Nie łączyć startu runtime z integracją V3.

Nową paczkę tworzy narzędzie:

```powershell
DOKUMENTACJA\TOOLS\New-Package.ps1 -PackageId CHARTS-RESTORE-20260821-001 -Area CHARTS
```

Samo utworzenie dokumentów nie autoryzuje runtime ani implementacji.

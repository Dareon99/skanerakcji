# TEST EVIDENCE — DOCS-SYSTEM-20260821-001

| Kontrola | Wynik |
|---|---|
| wymagane pliki | PASS |
| VERSION | `2026-08-21-r599` |
| manager flag | `1 / ON` |
| measurement flag | `0 / OFF` |
| MASTER ↔ VERSION | PASS |
| STAN ↔ VERSION | PASS |
| PROJECT-RECOVERY manifest | PASS, 59 wpisów |
| r599 activation manifest | PASS, 4 wpisy |
| PowerShell scripts parser | PASS |
| Windows PowerShell execution | PASS |
| hardcoded key w current config | nie wykryto |
| Git | initialized, branch main |
| Git candidate audit | 436 plików, 15 994 114 B |
| DB/key/pkl/zip candidate risk | 0 |
| runtime | OFF |
| kod produkcyjny | bez zmian przez pakiet dokumentacyjny |
| bazy produkcyjne | bez zmian przez pakiet dokumentacyjny |

Oczekiwane ostrzeżenia kontroli:

1. worktree ma niezatwierdzone pliki, ponieważ pierwszy commit jest pending;
2. remote nie jest skonfigurowany.

Nie są to błędy systemu. Wymagają danych/decyzji użytkownika.

```text
FAIL: 0
QUALITY GATE: PASS WITH 2 EXPECTED WARNINGS
```

# TEST EVIDENCE — SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001

```text
LAST WRITE TIMESTAMP: 2026-08-24 11:45 CEST
TEST ENVIRONMENT: Windows / PowerShell / documentation-only validation
NETWORK USED: NO
BUSINESS DB MUTATION: NO
```

| Gate | Polecenie/metoda | Wynik | Exit code | Artefakt/log |
|---|---|---|---:|---|
| py_compile | brak zmian Python | `N/A — DOCUMENTATION ONLY` | 0 | brak plików Python w zakresie |
| AST | brak zmian Python | `N/A — DOCUMENTATION ONLY` | 0 | brak plików Python w zakresie |
| invalid escape/static/sanity | wyszukanie niedozwolonej terminologii; kontrola statusu gate i ID decyzji | `PASS` | 0 | 0 trafień niedozwolonego terminu; ID zgodne w SPEC i promptcie |
| testy jednostkowe | brak kodu/runtime | `N/A — IMPLEMENTATION BLOCKED` | 0 | nie uruchamiano produktu |
| testy regresji | brak kodu/runtime | `N/A — IMPLEMENTATION BLOCKED` | 0 | nie uruchamiano produktu |
| package integrity | obecność 12 plików paczki; parzystość bloków Markdown; istnienie czterech ścieżek wejściowych | `PASS` | 0 | 12/12 plików; 12/12 plików z poprawną parzystością; ścieżki 4/4 |
| hashes | SHA-256 artefaktów Claude po zamknięciu wszystkich decyzji i gate projektu UI | `PASS` | 0 | `10`: `267D5B22...92678E`; `11`: `2C984E31...972E8D` |

## Podsumowanie

```text
PASS: 3 kontrole dokumentacyjne
FAIL: 0
SKIP: 4 kontrole kodu/runtime — poza zakresem i bez autoryzacji
UNVERIFIED: działanie przyszłej implementacji — nie istnieje w tej paczce
QUALITY GATE: PASS
SCOPE: DOCUMENTATION ONLY / IMPLEMENTATION REMAINS NOT AUTHORIZED
```

Każda zmiana zawartości paczki po zapisanym `LAST WRITE TIMESTAMP` unieważnia wynik.
Wyjątkiem są generowane po gate pliki `HASHES-SHA256.txt` i `FREEZE.md`, które są
ostatnim krokiem kontrolowanego zamrożenia i nie zmieniają zaakceptowanego kontraktu.


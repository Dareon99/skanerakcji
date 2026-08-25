# REJESTR ARTEFAKTÓW

| ID | Typ | Opis | Ścieżka | Status | Hash/manifest | Powiązanie |
|---|---|---|---|---|---|---|
| ART-001 | dashboard HTML | odzyskany V3, 6 spółek × 5 TF | `../ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/v3-fast-segmentation/index.html` | `OFFLINE VERIFIED` | manifest recovery | PROJECT-RECOVERY-001 |
| ART-002 | payloads JSON | 30/30 par symbol/TF | `../ARCHIWUM/PROJECT-RECOVERY-001/WYKRESY/v3-fast-segmentation/payloads/` | `FROZEN` | manifest recovery | PROJECT-RECOVERY-001 |
| ART-003 | screenshoty | 8 referencji UI/TradingView | `../ARCHIWUM/PROJECT-RECOVERY-001/REFERENCES/` | `FROZEN` | manifest recovery | PROJECT-RECOVERY-001 |
| ART-004 | source snapshot | V3, testy, raporty i architektura V4.4 | `../ARCHIWUM/PROJECT-RECOVERY-001/SOURCE-SNAPSHOT/` | `FROZEN` | manifest recovery | PROJECT-RECOVERY-001 |
| ART-005 | recovery report | diagnoza zatrzymania procesu | `../ARCHIWUM/PROJECT-RECOVERY-001/RECOVERY-REPORT-2026-08-21.md` | `FROZEN` | manifest recovery | PROJECT-RECOVERY-001 |
| ART-006 | MASTER użytkownika | brakujący pełny zapis live aktywacji r599 | `../ARCHIWUM/R599-MASSIVE-TRAFFIC-ACTIVATION-001/MASTER-SOURCE-USER-2026-08-21.md` | `FROZEN SOURCE` | SHA-256 `242302...d65d2` | r599-MASSIVE-TRAFFIC-ACTIVATION-001 |
| ART-007 | activation AS-BUILT | finalny kontrakt aktywacji managera ON | `../ARCHIWUM/R599-MASSIVE-TRAFFIC-ACTIVATION-001/FINAL-AS-BUILT-SPEC.md` | `FROZEN` | manifest activation | r599-MASSIVE-TRAFFIC-ACTIVATION-001 |
| ART-008 | ZIP źródłowy | archiwum „Skaner sygnałów kupna” dostarczone przez użytkownika | `../ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/SOURCE-ARCHIVE/Skaner-sygnalow-kupna-ARCHIWUM.zip` | `FROZEN SOURCE` | SHA-256 `f2075b...529a` | PROJECT-RECOVERY-ARCHIVE-20260821-002 |
| ART-009 | rozpakowany pakiet dokumentacji | 15 plików; README/MASTER/STAN, chronologia, zasady, roadmapa i r599 | `../ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/SOURCE-ARCHIVE/EXTRACTED/` | `FROZEN SOURCE` | manifest pakietu + manifest wewnętrzny 14/14 PASS | PROJECT-RECOVERY-ARCHIVE-20260821-002 |
| ART-010 | conflict report | porównanie importu z kanonicznym stanem i reguły scalenia | `../ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/03-CONFLICT-REPORT.md` | `FROZEN` | manifest pakietu | PROJECT-RECOVERY-ARCHIVE-20260821-002 |
| ART-011 | snapshot projektu | pełna kopia starego projektu po stop | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PROJECT-1TO1` | `FROZEN` | `MANIFEST-PROJECT-SHA256.txt` | LEGACY-SCANNER-FREEZE-AND-ISOLATION-20260821-001 |
| ART-012 | snapshot danych RAW | 11 plików, 2535842688 bajtów; stan przed efektem sidecar narzędzia SQLite | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\DATA-RAW` | `FROZEN` | `MANIFEST-DATA-RAW-SHA256.txt` | LEGACY-SCANNER-FREEZE-AND-ISOLATION-20260821-001 |
| ART-013 | backupy SQLite | spójne backupy `scanner.db`, `market.db`, `provider_state.db`; integrity/quick PASS | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\DATA-SQLITE-BACKUP` | `FROZEN` | `MANIFEST-DATA-SQLITE-BACKUP-SHA256.txt` | LEGACY-SCANNER-FREEZE-AND-ISOLATION-20260821-001 |
| ART-014 | handoff Claude | proces OLD freeze i roadmapa SKOOP | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PACKAGE` | `FROZEN` | `MANIFEST-PACKAGE-SHA256.txt` | LEGACY-SCANNER-FREEZE-AND-ISOLATION-20260821-001 |
| ART-015 | AS-BUILT freeze | finalny opis faktycznie wykonanego zamrożenia | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PACKAGE\FINAL-AS-BUILT-SPEC.md` | `FROZEN` | manifest pakietu | LEGACY-SCANNER-FREEZE-AND-ISOLATION-20260821-001 |
| ART-016 | lokalna aplikacja | placeholder SKOOP + Stock Scanner OLD read-only | `C:\SKOOP Skaner wykresów` | `TESTED / FROZEN` | manifest offline shell | LEGACY-DATA-COMPLETION-AND-OFFLINE-SHELL-20260821-001 |
| ART-017 | launcher redirect | stare URUCHOM/start przekierowane na SKOOP | `C:\Skaner wykresów\backend\URUCHOM.bat` | `INSTALLED` | manifest offline shell | LEGACY-DATA-COMPLETION-AND-OFFLINE-SHELL-20260821-001 |
| ART-018 | AS-BUILT offline shell | finalny kontrakt lokalnego OLD bez Massive | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\OFFLINE-SHELL-PACKAGE\FINAL-AS-BUILT-SPEC.md` | `FROZEN` | manifest pakietu | LEGACY-DATA-COMPLETION-AND-OFFLINE-SHELL-20260821-001 |
| ART-019 | runtime OLD 1:1 | oryginalny frontend i backend r599 w izolowanej kopii FROZEN | `C:\SKOOP Skaner wykresów\OLD-r599-1TO1` | `TESTED / FROZEN` | manifest OLD restore | OLD-R599-1TO1-RESTORE-20260822-001 |
| ART-020 | visual evidence | pełny render OLD 1920×1080 z wykresem NVDA | `C:\SKOOP-ARCHIWUM\OLD-R599-1TO1-RESTORE-20260822-001\EVIDENCE\PODGLAD-OLD-r599-VERIFIED.png` | `VERIFIED` | manifest OLD restore | OLD-R599-1TO1-RESTORE-20260822-001 |
| ART-021 | AS-BUILT OLD 1:1 | finalny kontrakt i quality gate | `C:\SKOOP-ARCHIWUM\OLD-R599-1TO1-RESTORE-20260822-001\FINAL-AS-BUILT-SPEC.md` | `FROZEN` | manifest OLD restore | OLD-R599-1TO1-RESTORE-20260822-001 |


| ART-022 | FINAL AS-BUILT Massive access | finalny kontrakt lokalnej paczki dostępu i wyniki planu | `../ARCHIWUM/SKOOP-MASSIVE-ACCESS-001/12-FINAL-AS-BUILT-SPEC.md` | `FROZEN` | `HASHES-SHA256.txt` | SKOOP-MASSIVE-ACCESS-001 |
| ART-023 | oczyszczone dowody Gate B | statusy/pola bez wartości, plan endpointów, manifest kodu i test 5 lat | `../ARCHIWUM/SKOOP-MASSIVE-ACCESS-001/EVIDENCE-SNAPSHOT/` | `FROZEN / NO SECRETS` | `HASHES-SHA256.txt` | SKOOP-MASSIVE-ACCESS-001 |
| ART-024 | snapshot kodu paczki | 12 plików izolowanego dostępu Massive, bez klucza, logów i baz | `../ARCHIWUM/SKOOP-MASSIVE-ACCESS-001/CODE-SNAPSHOT/` | `FROZEN / 12 FILES` | `HASHES-SHA256.txt` | SKOOP-MASSIVE-ACCESS-001 |

Każdy nowy artefakt otrzymuje następny numer `ART-NNN`, opis, dokładną ścieżkę, status, hash/manifest i Package ID. Załączników nie osadza się w MASTER.

# FINAL AS-BUILT — STOCK SCANNER OLD r599 1:1 FROZEN

**Package ID:** `OLD-R599-1TO1-RESTORE-20260822-001`  
**Data:** 2026-08-22  
**Status:** `ACCEPTED TECHNICALLY / FROZEN`  
**Decyzja:** `D-008`

## 1. Powód poprawki

Pierwsza lokalna powłoka zachowała snapshot danych, ale zastąpiła oryginalny
interfejs OLD uproszczonym widokiem. Było to niezgodne z zaakceptowanym
kontraktem: `Stock Scanner OLD` ma zachować wygląd, zakładki, projekty wykresów
i lokalne zasoby r599 1:1. Uproszczony widok OLD zostaje `SUPERSEDED`.

## 2. Stan wdrożony

- domyślny adres `http://127.0.0.1:8000/` otwiera nowy SKOOP;
- przycisk `Stock Scanner OLD` przechodzi do `http://127.0.0.1:8001/`;
- port 8001 serwuje oryginalny frontend r599 (`ui/index.html` + `support.js`);
- zachowano oryginalne zakładki, panele, listingi, portfele, cykle, IPO,
  wykresy i szczegóły spółek;
- w OLD dodano wyłącznie identyfikację `OLD`, status zamrożenia i przycisk
  powrotu do nowego SKOOP;
- React i ReactDOM zapisano lokalnie, aby wygląd OLD nie zależał od CDN;
- stary folder `C:\Skaner wykresów` i immutable archiwum 1:1 nie zostały
  zmodyfikowane.

## 3. Ścieżki

| Element | Ścieżka |
|---|---|
| nowy SKOOP / domyślny widok | `C:\SKOOP Skaner wykresów` |
| runtime OLD 1:1 | `C:\SKOOP Skaner wykresów\OLD-r599-1TO1` |
| robocza kopia danych OLD | `C:\SKOOP Skaner wykresów\OLD-RUNTIME-DATA` |
| immutable kod źródłowy | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\PROJECT-1TO1` |
| immutable backup SQLite | `C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001\DATA-SQLITE-BACKUP` |
| wspólny launcher | `C:\SKOOP Skaner wykresów\URUCHOM-SKOOP.bat` |
| warstwa bezpieczeństwa | `C:\SKOOP Skaner wykresów\OLD-r599-1TO1\frozen_app.py` |

## 4. Twarde blokady OLD

- Massive/Polygon: `DISABLED_FROZEN`;
- Yahoo/yfinance: funkcje sieciowe zastąpione pustym źródłem;
- indeksy live: wyłączone, wynik lokalny `frozen`;
- workery i daemon threads starego skanera: blokowane;
- metody `POST`, `PUT`, `PATCH`, `DELETE`: HTTP `405`;
- bazy runtime: SQLite `mode=ro&immutable=1` + `PRAGMA query_only=ON`;
- bind: wyłącznie `127.0.0.1`;
- nowy SKOOP nie importuje mechanizmów OLD.

## 5. Quality gate

| Kontrola | Wynik |
|---|---|
| składnia `launcher.py` i `frozen_app.py` | `PASS` |
| start SKOOP na 8000 | `PASS` |
| start oryginalnego OLD na 8001 | `PASS` |
| oryginalny `support.js` i lokalne React/ReactDOM | `HTTP 200 / PASS` |
| pełny render OLD w 1920×1080 | `PASS` |
| zakładki/panele/listing/wykres NVDA widoczne | `PASS` |
| endpointy odczytowe: universe, signals, candles, portfolios, cycles | `HTTP 200 / PASS` |
| próba `POST /data/sync` | `HTTP 405 / PASS` |
| zewnętrzne połączenia procesu OLD | `0 / PASS` |
| SHA-256 `scanner.db` runtime = archive | `PASS` |
| SHA-256 `market.db` runtime = archive | `PASS` |
| SHA-256 `provider_state.db` runtime = archive | `PASS` |

Hash snapshotu:

- `scanner.db`: `A1D2512AC200AC00ED868A9E110E01902D9518B089CEA3C8E2ED536BBBD925D8`
- `market.db`: `659AD89960373747ED44D4177ABF60A42B84DC29AD67FCA5F8AA7B7FAA335FDB`
- `provider_state.db`: `6B56DAA18B26B9AB2024D63E5701757D101BA2C8B116637C6FB8C4B4245368CF`

## 6. Świadome ograniczenia

- Kontrolki historycznie uruchamiające zapis lub pobieranie pozostają widoczne
  jako część oryginalnego projektu, lecz ich wywołania są blokowane.
- Indeksy i ceny wymagające żywego źródła nie są odświeżane.
- OLD pokazuje tylko dane zapisane w lokalnym snapshotcie 2026-08-21.
- Pełniejszy żywy skaner pozostaje na drugim komputerze zgodnie z D-007.

## 7. Acceptance

`ACCEPT`: nowy SKOOP jest widokiem domyślnym, a kliknięcie OLD otwiera
oryginalny r599 z zachowanym wyglądem i lokalnymi zasobami, bez uruchamiania
starego procesu inwestycyjnego lub dostępu do providerów.


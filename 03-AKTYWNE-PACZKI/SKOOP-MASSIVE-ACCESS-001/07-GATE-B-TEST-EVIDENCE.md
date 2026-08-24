# TEST EVIDENCE — SKOOP-MASSIVE-ACCESS-001 / GATE B — REV. 2

~~~text
STATUS: PASS WITH SOURCE/PLAN LIMITATIONS — AWAITING USER ACCEPTANCE
DATE: 2026-08-24
EXECUTOR: local Codex
PROVIDER: MASSIVE ONLY
REQUESTS: 29 / HARD CEILING 50
UNIVERSE IMPORT: NO
OLD ACCESS OR WRITE: NO
FINAL KILL SWITCH: ON
KEY: LOCAL USE ONLY; VALUE NOT STORED IN EVIDENCE OR LOGS
FREEZE: NOT PERFORMED — REQUIRES USER ACCEPTANCE OF RESULTS
~~~

## Przebieg

Pierwszy kontrolowany przebieg wykonał 14 scenariuszy i potwierdził dostęp.
Drugi przebieg 14 scenariuszy, po rozszerzeniu zapisu wyłącznie o nazwy pól,
domknął macierz dowodową bez zapisywania wartości. Po korekcie użytkownika
wykonano jedno dodatkowe zapytanie sprawdzające właściwy wymóg produktu:
5 lat historii. Łącznie 29 żądań, bez retry, bez paginacji i bez importu.

## Wyniki S0–S13

| ID | Status | HTTP | Wynik użyteczny dla projektu |
|---|---|---:|---|
| S0 | CONFIRMED | 200 | autoryzacja działa; status rynku zawiera market, exchanges, earlyHours i afterHours |
| S1 | CONFIRMED | 200 | katalog aktywnych instrumentów działa; ticker, nazwa, giełda/MIC, waluta, typ, active, CIK/FIGI i last_updated_utc; next_url nieużyte |
| S2 | CONFIRMED | 200 | szczegóły spółki: nazwa, giełda, waluta, typ, active, opis, data listingu, identyfikatory, adres i branding |
| S3 | CONFIRMED / SUPPORTING ONLY | 200 | SIC i sic_description są dostępne jako informacja pomocnicza; kanoniczne sektor/branża nadaje SKOOP według mapowania synchronizowanego z TradingView |
| S4 | CONFIRMED / PARTIAL | 200 | market_cap, share_class_shares_outstanding i weighted_shares_outstanding potwierdzone; float nie wystąpił — UNVERIFIED |
| S5 | UNAVAILABLE_IN_CURRENT_PLAN | 403 | income statements, w tym kwartalne/TTM, niedostępne w bieżącym planie |
| S6 | CONFIRMED / PARTIAL | 200 | IPO działa; issuer_name, ticker, ipo_status, primary_exchange, security_type, announced_date i total_offer_size; część opcjonalnych pól ceny/daty nie wystąpiła w próbce |
| S7 | CONFIRMED | 200 | świece 1D: OHLCV, VWAP, liczba transakcji, timestamp, adjusted |
| S7b | CONFIRMED | 200 | zbiorcza odpowiedź dzienna USA: ticker + OHLCV/VWAP; nic nie zapisano do UNIVERSE |
| S8 | CONFIRMED | 200 | świece 30m: OHLCV/VWAP/timestamp; next_url nieużyte |
| S9 | CONFIRMED / PARTIAL | 200 | kalendarz świąt: data, giełda, nazwa, status; open/close nie wystąpiły w pierwszym rekordzie |
| S10 | CONFIRMED | 200 | FX dla jednej pary działa; OHLCV/VWAP/timestamp |
| S11 | CONFIRMED / PARTIAL | 200 | dywidendy: kwoty, waluta, daty, częstotliwość, typ i adjustment factors; splity pozostały UNVERIFIED w tym teście |
| S12 | CONFIRMED | 200 | właściwy wymóg produktu: 5 lat historii 1D potwierdzone zakresem z 2021 r.; próba 2010 była wyłącznie diagnostyczna i nie jest wymaganiem SKOOP |
| S13 | UNVERIFIED | — | brak pasywnych nagłówków rate-limit; 429 nie prowokowano |

403 oznacza wyłącznie brak dostępu w bieżącym planie, a nie brak danych u źródła.

## Wiążące doprecyzowania użytkownika

- historia przechowywana i używana przez SKOOP: do 5 lat;
- dłuższe okresy użytkownik sprawdza w TradingView;
- Massive dostarcza surowe dane pomocnicze klasyfikacji, w tym SIC;
- SKOOP sam nadaje kanoniczne sektor i branżę;
- nazwy i taksonomia sektorów/branż mają być synchronizowane z TradingView;
- rekord mapowania ma zawierać źródło, wersję mapowania, datę zmiany i obsługiwać ręczną korektę.

## Quality gate

| Etap | Wynik |
|---|---|
| py_compile / AST | PASS 9/9 / 9/9 |
| testy offline | PASS 9/9 |
| test zapisu struktury pól bez wartości | PASS |
| licznik traffic_guard = log | PASS — 29 = 29, sekwencja 1…29 |
| sekrety w logu | PASS — 0 znaczników wartości klucza/tokena |
| importy i ścieżki OLD w Pythonie | PASS — 0 trafień |
| package integrity | PASS — 12/12, missing 0, extra 0 |
| kill switch | PASS — OFF/ON bez błędu, stan końcowy ON |

## Integralność OLD

- scanner.db: A1D2512AC200AC00ED868A9E110E01902D9518B089CEA3C8E2ED536BBBD925D8 — identyczny z BEFORE;
- market.db: 659AD89960373747ED44D4177ABF60A42B84DC29AD67FCA5F8AA7B7FAA335FDB — identyczny z BEFORE;
- provider_state.db: 6B56DAA18B26B9AB2024D63E5701757D101BA2C8B116637C6FB8C4B4245368CF — identyczny z BEFORE;
- OLD-r599-1TO1: 457 plików, 0 modyfikacji podczas Gate B;
- C:\Skaner wykresów: 792 pliki według reguły Gate A, 0 modyfikacji podczas Gate B;
- OLD-RUNTIME-DATA: 0 modyfikacji podczas Gate B;
- stary plik klucza OLD nie był odczytywany ani haszowany.

## Dowody lokalne

- GATE-B-FINAL-EVIDENCE.json — SHA-256 61D288B5A086F22C0ADBEB7F97F7CA384C3D9463827FA0D9DBA5828F73EEAEA0;
- GATE-B-FIVE-YEAR-EVIDENCE.json — SHA-256 8DF25BB42577C0AAE2EEA5959687BDEAF3B6B2B6F77E02EABFF8891D24B9DEAF;
- GATE-B-CODE-HASHES-SHA256.txt — SHA-256 8CADB0A9D40AC1F287D420D324DD433D13DEBB7EF7D8F1D741C9A6A3B6A5DC53;
- GATE-B-ENDPOINT-PLAN.json — SHA-256 E90C8E642610D0B7FB1CB82A0705481C05B3316B4156F38822A22A78BE8AA1E9;
- massive-access.jsonl: 29 bezpiecznych wpisów bez URL query i bez sekretu.

Lokalizacja: C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\ oraz
C:\SKOOP-dane\logs\massive\.

## Następny gate

Nie rozpoczęto importu UNIVERSE ani budowy bazy produktu. MASTER/STAN,
FINAL-AS-BUILT-SPEC, archiwizacja i FREEZE pozostają zablokowane do jawnej
akceptacji wyników przez użytkownika.

Dokładnie jeden następny krok: USER ACCEPTANCE OF GATE B RESULTS.

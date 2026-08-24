# GATE A — HANDOFF DLA LOKALNEGO WYKONAWCY

```text
PACKAGE: SKOOP-MASSIVE-ACCESS-001
CONTRACT: 05-IMPLEMENTATION-CONTRACT.md — ACCEPTED REV. 2 (2026-08-24)
AUTHORIZED: GATE A ONLY (offline); GATE B BLOCKED
POWÓD HANDOFFU: środowisko Claude nie ma dostępu do C:\SKOOP Skaner wykresów\
ani C:\SKOOP-dane\ oraz nie wykonuje commit/push — STOP rule zgodnie z
warunkiem §2 akceptacji; zero pozorowanej implementacji w innym katalogu.
```

## KROK 0 — Publikacja dokumentacji (przed implementacją)

1. skopiuj CAŁĄ paczkę `SKOOP-MASSIVE-ACCESS-001/` (bez tego pliku, jeśli
   lokalny proces tego wymaga — rekomendacja: z tym plikiem) do:
   `DOKUMENTACJA\03-AKTYWNE-PACZKI\SKOOP-MASSIVE-ACCESS-001\`;
2. dopisz aneks D-007 wg `ANEKS-D-007-DO-WPISANIA.md` (append-only) do
   `04-DECYZJE/DECYZJE-PROJEKTOWE.md`; potwierdź numer D-017 wobec rejestru;
3. kontrola dokumentacji: parzystość bloków Markdown, obecność 9 plików paczki,
   spójność statusów (ACCEPTED / GATE B BLOCKED);
4. secret-scan katalogu dokumentacji: 0 trafień wartości klucza/sekretów;
5. jeden commit dokumentacyjny:
   `SKOOP-MASSIVE-ACCESS-001: accept revision 2 and authorize offline Gate A`;
6. push wyłącznie dokumentacji do `Dareon99/skanerakcji`, gałąź `main`;
7. potwierdź `git rev-parse HEAD` == `origin/main`.

Zakaz: klucz, sekrety, logi, sandbox i lokalne pliki konfiguracyjne nie
wchodzą do repozytorium.

## KROK 1 — Warunek dostępu

Gate A wolno rozpocząć wyłącznie po potwierdzeniu rzeczywistego dostępu do:
`C:\SKOOP Skaner wykresów\` i `C:\SKOOP-dane\`. Brak dostępu = STOP.

## KROK 2 — Implementacja (wyłącznie pliki z kontraktu §1.1)

Katalog: `C:\SKOOP Skaner wykresów\PACKAGES\SKOOP-MASSIVE-ACCESS-001\`.
Pliki: config_access.py, secret_loader.py, massive_connection.py,
massive_fetch.py, traffic_guard.py, access_log.py, sandbox_store.py,
smoke_test.py, test_access_offline.py, KILL-SWITCH-ON.bat, KILL-SWITCH-OFF.bat,
README-URUCHOMIENIE.md. Wymagania funkcjonalne: kontrakt §1–§3 (w tym
sześciostanowa klasyfikacja §3.2 i sufit 50 w traffic_guard).

Bezwzględne blokady Gate A: zero prawdziwego klucza (nie tworzyć pliku klucza
za użytkownika, nie prosić o wklejenie); zero połączeń Massive/Yahoo/innych;
zero pobierania UNIVERSE; zero zmian/uruchomień OLD; frozen bazy tylko
read-only; zero Gate B; bez aktualizacji MASTER/STAN wynikami implementacji.

## KROK 3 — Quality gate Gate A (dokładnie w tej kolejności)

```text
LAST WRITE
→ py_compile
→ AST
→ invalid escape / static / sanity
→ komplet testów offline
→ secret-scan
→ kontrola braku importów i dostępu do OLD
→ kontrola dozwolonych ścieżek zapisu
→ test kill switcha
→ test FAIL-CLOSED
→ kontrola liczby i zakresu plików
→ package integrity
→ hashes
```

BEZ finalnego FREEZE paczki — FREEZE dopiero po Gate B, akceptacji wyników
i FINAL-AS-BUILT. Zmiana bajta po HASHES = powtórzenie gate.

## KROK 4 — Raport po Gate A (10 punktów) i STOP

1. dokładna lista utworzonych i zmienionych plików;
2. wynik każdego elementu quality gate;
3. wyniki wszystkich testów offline;
4. wynik secret-scanu;
5. porównanie hashy OLD i frozen przed/po;
6. potwierdzenie liczby połączeń zewnętrznych: 0;
7. potwierdzenie, że prawdziwy klucz nie został użyty;
8. stan kill switcha;
9. gotowość albo brak gotowości do Gate B;
10. pełny raport odchyleń od kontraktu.

Po raporcie STOP. Dokładnie jeden następny krok po prawidłowym PASS Gate A:

```text
USER AUTHORIZATION OF CONTROLLED GATE B SMOKE TEST
```

# SKOOP Massive Access — uruchomienie

~~~text
PACKAGE: SKOOP-MASSIVE-ACCESS-001
STATE: ACCEPTED / FROZEN
GATE A: PASS
GATE B: ACCEPTED
NETWORK DEFAULT: DISABLED
FINAL REQUEST COUNTER: 29 / 50
FINAL KILL SWITCH: ON
UNIVERSE IMPORT: NOT STARTED
~~~

## Bezpieczeństwo

- kod nie importuje ani nie uruchamia OLD;
- wszystkie ścieżki danych należą do C:\SKOOP-dane;
- domyślna konfiguracja nie zawiera hosta, sposobu autoryzacji ani zgody na sieć;
- pliku C:\SKOOP-dane\secrets\massive_key.txt nie tworzy aplikacja;
- klucza nie wolno wklejać do rozmowy, GitHuba, raportu ani logu;
- zaakceptowana paczka jest zamrożona i nie jest zgodą na dalszy ruch.

## Testy offline

W katalogu tej paczki:

~~~text
python -m py_compile *.py
python -m unittest -v test_access_offline.py
~~~

Testy używają wyłącznie lokalnego, sztucznego klucza w katalogu tymczasowym
oraz atrap odpowiedzi HTTP. Nie otwierają połączenia z dostawcą.

## Kill switch

- KILL-SWITCH-ON.bat tworzy trwałą flagę STOP;
- KILL-SWITCH-OFF.bat usuwa wyłącznie dokładną flagę STOP;
- każdy istniejący albo niejednoznaczny stan flagi oznacza brak ruchu;
- stan końcowy zaakceptowanej paczki: ON.

## Gate B — stan końcowy

Gate B wykonał 29 kontrolowanych żądań z twardym sufitem 50. Potwierdził m.in.
katalog instrumentów, szczegóły spółki, IPO, 1D, 30m, grouped daily, FX,
dywidendy i pięć lat historii 1D. Finanse kwartalne/TTM są niedostępne w
bieżącym planie. Pełna macierz jest w repozytoryjnym FINAL-AS-BUILT.

Nie uruchamiaj ponownie smoke_test.py. Dalszy dostęp i import wymagają nowej,
osobno zaakceptowanej paczki. Klucz pozostaje lokalny i nie należy do archiwum.

## Dozwolone zapisy tej paczki

~~~text
C:\SKOOP-dane\sandbox\SKOOP-MASSIVE-ACCESS-001\
C:\SKOOP-dane\logs\massive\
C:\SKOOP-dane\massive.kill-switch
~~~

Każda próba zapisu poza tym zakresem jest błędem kontraktu i uruchamia STOP rule.

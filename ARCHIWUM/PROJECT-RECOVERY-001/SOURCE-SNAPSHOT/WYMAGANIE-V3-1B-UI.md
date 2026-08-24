# WYMAGANIE (ZAPISANE, NIEIMPLEMENTOWANE)
# V3.1B-UI — DOPRACOWANIE WYKRESU WALIDACYJNEGO

STATUS: RECORDED_ONLY — NOT_IMPLEMENTED
WARUNEK STARTU: canonical H/L bug naprawiony i zweryfikowany przez właściciela
KOLEJNOŚĆ: najpierw DATA CORRECTNESS, potem VISUAL QUALITY

Cel: wykres przejrzysty, estetyczny i ergonomicznie zbliżony do klasycznego układu
TradingView. Nie kopiowanie 1:1 — jakość prezentacji.

## Obecny problem UX
Panele wizualnie posklejane. Brak wyraźnego oddzielenia, oddechu pionowego, czytelnej
hierarchii, separacji price / MACD / RSI / Stochastic i właściwych proporcji wysokości.

## Docelowy układ
Price największy panel; Volume bezpośrednio przy price, ale wizualnie oddzielony;
MACD, RSI, Stochastic jako osobne panele; wszystkie na wspólnej osi czasu. Panele nie
mogą się zlewać.

## RSI — docelowy kanał wizualny
Linia RSI, helper/średnia, poziomy 70 / 50 / 30 oraz subtelne strefy:
70–100 delikatne chłodne (niebieskawe), 30–70 neutralne bardzo delikatne tło kanału,
0–30 delikatne ciepłe (czerwone). Użytkownik ma natychmiast widzieć, czy RSI jest nad
kanałem, w kanale, czy pod nim. Wyjście powyżej 70 i poniżej 30 łatwo widoczne —
najważniejsze jest tło stref, nie kolorowanie samej wartości.

WAŻNE: poziomy 70 i 50 są WYŁĄCZNIE CHART VISUAL GUIDES. Nie stają się progiem
algorytmicznym, eventem, feature, scoringiem, warunkiem WATCH ani BUY. Locked RSI logic
bez zmian; 30 nadal może wynikać z istniejącej locked RSI semantics.

## Stochastic
Analogicznie: K, D, poziomy 20 / 50 / 80, subtelne strefy i linie pomocnicze, bez
scoringu i interpretacji.

## MACD
Wyraźna linia 0, histogram, MACD, Signal. Panel nie może być przyklejony do price
ani do RSI.

## Separacja paneli
Każdy panel: subtelny separator, własny nagłówek, własna czytelna skala Y. Bez dużych
kart, ramek i dashboardowych boxów — charakter charting terminal.

## Proporcje (hierarchia, nie hard contract CSS)
PRICE + VOLUME 55–60%, MACD 18–20%, RSI 10–12%, STOCHASTIC 10–12%.
Price zdecydowanie największy.

## Odstępy
Niewielki, ale wyraźny spacing / divider między panelami — bez wyglądu jednego
sklejonego wykresu i bez marnowania dużej ilości miejsca.

## Wspólny crosshair
Hover / crosshair synchronizuje ten sam timestamp na PRICE, MACD, RSI, STOCHASTIC.
Bardzo ważne przy porównaniu z TradingView.

## Legendy wartości
Kompaktowy nagłówek każdego panelu z bieżącymi wartościami, np.
`MACD 13.99 | Signal 11.02 | Hist 2.97`, `RSI 63.9 | Średnia 63.2`,
`Stochastic K 71.9 | D 86.9`. Bez dużych kart.

## Prawy panel
Podstawowe cechy / status danych są użyteczne diagnostycznie, ale zabierają szerokość
wykresu. Do rozważenia: węższy panel, zwijanie, kompaktowa sekcja, drawer. NIE
implementować bez osobnego sprintu. Priorytet: wykres ma mieć więcej miejsca.

## Estetyka
Czysty, profesjonalny, gęsty informacyjnie, czytelny, spokojny wizualnie.
Nie: prototyp developerski, duże kafelki, jaskrawe ozdobniki, przypadkowe kolory.

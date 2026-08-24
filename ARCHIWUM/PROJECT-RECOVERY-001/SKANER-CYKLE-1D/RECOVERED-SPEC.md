# RECOVERED SPEC — SKANER „CYKLE 1D”

**Status:** `CONFIRMED FROM CONVERSATION`  
**Zakres:** kryteria obecności na liście i prezentacja karty; bez alarmów i bez rekomendacji transakcyjnej  
**Zasada:** brak faz na obecnym etapie

## 1. Cel listy

Lista ma wychwycić spółkę:

- 1–3 dni przed minimum ujemnej excursion MACD;
- w dniu maksymalnej głębokości;
- przy wzrostowym przecięciu MACD/Signal oznaczonym zieloną kropką;
- maksymalnie 3–5 zamkniętych sesji po przecięciu, dopóki dodatni histogram jest jasnoniebieski i rośnie.

Nazwa jednego aktywnego stanu: **Cykle 1D**. Na tym etapie nie wolno wprowadzać nazw faz, przycisku BUY ani obietnicy skuteczności.

## 2. Kwalifikacja do listy

Wszystkie poniższe warunki muszą być spełnione:

1. istnieje aktywny ujemny cykl MACD;
2. maksymalna osiągnięta głębokość bieżącego cyklu jest nie mniejsza niż historyczna mediana zakończonych cykli;
3. maksymalna osiągnięta głębokość bieżącego cyklu jest nie mniejsza niż historyczna średnia zakończonych cykli;
4. w dowolnym momencie bieżącego cyklu wystąpiło `RSI <= 32`;
5. w dowolnym momencie bieżącego cyklu wystąpiło `Stoch %K <= 22`;
6. pojawia się pierwsze skrócenie ujemnego histogramu: `hist[t] < 0` oraz `hist[t] > hist[t-1]`.

RSI i Stochastic są warunkami zapamiętywanymi przez cały aktywny cykl. Nie muszą spełniać progów na aktualnej świecy.

## 3. Utrzymanie i usunięcie z listy

Spółka pozostaje widoczna przez minimum, przecięcie wzrostowe i najwyżej pięć zamkniętych sesji po przecięciu, jeżeli:

- histogram jest dodatni: `hist[t] > 0`;
- histogram nadal rośnie: `hist[t] > hist[t-1]`.

Spółka znika, gdy zachodzi którekolwiek:

- dodatni momentum histogramu słabnie;
- histogram wraca poniżej zera;
- minęło więcej niż pięć zamkniętych sesji od przecięcia.

Jeżeli przed przecięciem histogram zaczyna ponownie się pogłębiać, wczesny sygnał zostaje anulowany. System czeka na nowe pierwsze skrócenie; nie utrzymuje starego sygnału siłą.

## 4. Ranking

Nie wolno sortować po surowej wartości MACD, ponieważ zależy ona od skali ceny.

Wskaźnik głębokości względnej:

```text
relative_depth = achieved_max_negative_depth
                 / max(historical_mean_depth, historical_median_depth)
```

Ranking malejący według `relative_depth`. Tie-breakery są `TO RECOVER/DECISION REQUIRED`.

Do średniej i mediany historycznej wchodzą wyłącznie zakończone cykle. Bieżący, niezakończony cykl nie może zanieczyszczać profilu historycznego.

## 5. Dane historyczne

- wyłącznie zamknięte świece 1D;
- na wykresie widoczne 250 sesji;
- preferowane minimum pięć zakończonych cykli historycznych;
- zachowanie przy mniej niż pięciu cyklach: `TO RECOVER/DECISION REQUIRED`;
- czas i strefa uznania sesji za zamkniętą: `TO RECOVER`.

## 6. Zawartość karty/listingu

### Obowiązkowe

- ticker, nazwa, giełda, branża;
- miniwykres ceny;
- miniwykres MACD/histogramu;
- miniwykres RSI;
- względna głębokość;
- bieżący MACD i minimalny MACD cyklu;
- historyczna średnia i mediana głębokości;
- minimalny RSI i minimalny Stoch w cyklu;
- kierunek/trend histogramu;
- data minimum;
- data wzrostowego przecięcia;
- liczba zamkniętych sesji od przecięcia;
- przejście do TradingView albo pełnego wykresu.

### Usunąć/nie używać na tym etapie

- przycisk BUY;
- cena docelowa;
- generyczna „skuteczność 67%” bez odzyskanej formuły;
- nazwy faz.

## 7. Wolumen

Wolumen jest kontekstem i wzmacnia/obniża zaufanie, ale nie jest początkowym twardym filtrem usuwającym spółkę.

Odzyskana definicja robocza:

```text
RVOL20 = wolumen bieżącej sesji / mediana wolumenu 20 poprzednich sesji
```

Progi robocze, jeszcze niezamrożone:

- `< 0,8` — niski;
- `0,8–1,2` — typowy;
- `1,2–1,5` — podwyższony;
- `>= 1,5` — silny;
- `>= 2,0` — możliwy selling climax.

Status progów: `PARTIAL/DECISION REQUIRED`. Wolumen może pomagać rozróżnić presję sprzedaży, kulminację sprzedaży, wygasanie podaży i pojawienie się popytu, ale nie zastępuje warunków MACD/RSI/Stoch.

## 8. Przykłady akceptacyjne

- `RBLX` — wzorzec pożądanej głębokiej struktury cyklu;
- `ADMA` — przykład szumu, który nie powinien kwalifikować się przy głębokości około 55% typowej excursion.

Te symbole są przykładami wizualnymi, nie sztywną whitelistą/blacklistą.

## 9. Braki

- dokładna definicja początku i końca „cyklu MACD” w kodzie poza zachowanym rendererem;
- tie-breakery rankingu;
- polityka przy mniej niż pięciu cyklach;
- model brakujących danych i luk sesyjnych;
- reguły alarmu, cooldown i deduplikacja;
- sposób materializacji/cache/listing API;
- testy golden-master dla pełnego universe;
- reguły 1H i pozostałych interwałów listingu.

Wszystkie powyższe mają status `TO RECOVER`; nie wolno ich domyślać.

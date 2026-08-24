# GATE B — WIĄŻĄCE KOREKTY UŻYTKOWNIKA / 2026-08-24

Status: ACCEPTED USER CLARIFICATIONS — BINDING FOR NEXT PACKAGES.

## Horyzont danych

- SKOOP potrzebuje i utrzymuje historię maksymalnie 5 lat;
- próba roku 2010 była wyłącznie diagnostycznym pomiarem planu i nie tworzy wymagania produktu;
- dłuższe horyzonty użytkownik sprawdza bezpośrednio w TradingView;
- pięcioletnia historia 1D została potwierdzona w Gate B: CONFIRMED / HTTP 200.

## Sektor i branża

- Massive dostarcza informacje pomocnicze, w szczególności SIC i opis SIC;
- pola kanoniczne SKOOP to canonical_sector i canonical_industry;
- wartości kanoniczne nadaje warstwa mapowania SKOOP, nie dostawca Massive;
- celem mapowania jest zgodność nazw i taksonomii z TradingView;
- należy zachować raw_provider_classification obok klasyfikacji kanonicznej;
- rekord mapowania musi zawierać mapping_version, mapping_source,
  changed_at_user_time oraz informację o ręcznej korekcie;
- ręczna korekta użytkownika ma pierwszeństwo przed automatycznym mapowaniem
  do czasu jej jawnego cofnięcia lub zastąpienia.

Niniejszy dokument koryguje interpretację S3 i S12 we wcześniejszych raportach
tej paczki i ma pierwszeństwo w przypadku rozbieżności.

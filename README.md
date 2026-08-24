# DOKUMENTACJA — INDEKS KANONICZNY

> **Start Claude z GitHub:** przeczytaj najpierw `CLAUDE.md`, a następnie dokumenty
> wejściowe w kolejności poniżej. Repozytorium zawiera dokumentację i referencje,
> nie działający runtime ani produkcyjne bazy.

> **Stan 2026-08-22:** nowy SKOOP jest widokiem domyślnym na porcie 8000. `Stock Scanner OLD` otwiera oryginalny interfejs r599 1:1 na porcie 8001, z zamrożonymi zasobami i twardą blokadą providerów, workerów oraz zapisu (D-008). Dalsze pobieranie danych na tym komputerze pozostaje anulowane decyzją D-007; pełny żywy skaner pozostaje na drugim komputerze.

## Dokumenty wejściowe

| Kolejność | Dokument | Rola | Aktualizacja |
|---:|---|---|---|
| 1 | `MASTER-PROJEKT.md` | trwałe źródło prawdy i roadmapa | po decyzji, akceptacji lub odzyskaniu faktu |
| 2 | `STAN-AKTUALNY.md` | krótki snapshot operacyjny | przy każdym istotnym handoffie |
| 3 | `00-STEROWANIE/ZASADY-PROJEKTU.md` | niezmienne reguły pracy | tylko po decyzji użytkownika |
| 4 | `04-DECYZJE/DECYZJE-PROJEKTOWE.md` | append-only log decyzji | natychmiast po decyzji |
| 5 | właściwy FINAL-AS-BUILT | dowód, jak moduł naprawdę działa | po acceptance |
| 6 | aktywna paczka | jedyny bieżący zakres zmiany | w trakcie sprintu |

Importowane pakiety historyczne są dowodami pochodzenia, nie równoległymi MASTER-ami. Pakiet „Skaner sygnałów kupna” znajduje się w `ARCHIWUM/PROJECT-RECOVERY-ARCHIVE-20260821-002/SOURCE-ARCHIVE/`; jego trzy dokumenty startowe zostały scalone z nowszym stanem przez `03-CONFLICT-REPORT.md` i `FINAL-AS-BUILT-SPEC.md` tej paczki.

Aktualne instrukcje przekazania do Claude znajdują się w `CLAUDE.md` oraz w aktywnej
paczce jako `10-CLAUDE-EXECUTION-SPEC.md` i `11-CLAUDE-START-COMMAND.md`. Materiały
w zewnętrznym archiwum freeze są starszym źródłem referencyjnym. Claude ma zacząć
od bieżących MASTER + STAN + aktywnej paczki, a dopiero potem czytać odpowiedni
AS-BUILT i roadmapę. Dokumenty starego projektu nie upoważniają do jego restartu.

## Struktura

```text
DOKUMENTACJA/
├── CLAUDE.md
├── MASTER-PROJEKT.md
├── STAN-AKTUALNY.md
├── 00-STEROWANIE/
│   ├── SYSTEM-PRACY.md
│   ├── ZASADY-PROJEKTU.md
│   ├── PROTOKOL-SESJI-AI.md
│   ├── WERSJONOWANIE-I-GIT.md
│   └── DOSTEPY-I-BEZPIECZENSTWO.md
├── 02-AS-BUILT/
│   └── INDEX.md
├── 03-AKTYWNE-PACZKI/
│   └── README.md
├── 04-DECYZJE/
│   └── DECYZJE-PROJEKTOWE.md
├── 05-REJESTRY/
│   ├── REJESTR-SPRINTOW.md
│   ├── REJESTR-ARTEFAKTOW.md
│   └── CHANGELOG-DOKUMENTACJI.md
├── 06-SESJE/
│   └── SESJA-BIEZACA.md
├── 07-SZABLONY/
├── TOOLS/
└── ARCHIWUM/
```

`ARCHIWUM` jest immutable po FREEZE. Poprawka do archiwum powstaje jako nowa paczka, która wskazuje `SUPERSEDES`; nie edytuje starego dowodu.

## Statusy

- `CONFIRMED` — potwierdzone źródłem;
- `PARTIAL` — część potwierdzona, część brakująca;
- `UNVERIFIED` — wymaga weryfikacji;
- `TO RECOVER` — istnieje przesłanka, ale brak dowodu;
- `DECISION REQUIRED` — potrzebna decyzja użytkownika;
- `BLOCKED` — nie można bezpiecznie kontynuować;
- `ACCEPTED` — zaakceptowane przez użytkownika;
- `FROZEN` — zamrożone po hashach.

## Czego tu nie przechowujemy

Kluczy API, haseł, tokenów, baz danych, WAL/SHM, `.venv`, cache, nieoczyszczonych zrzutów logów ani prywatnych danych kont. Rejestr dostępu zawiera tylko typ dostępu i instrukcję uzyskania go, nigdy sekret.

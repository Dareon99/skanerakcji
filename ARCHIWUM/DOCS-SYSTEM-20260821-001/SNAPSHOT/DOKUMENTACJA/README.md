# DOKUMENTACJA — INDEKS KANONICZNY

## Dokumenty wejściowe

| Kolejność | Dokument | Rola | Aktualizacja |
|---:|---|---|---|
| 1 | `MASTER-PROJEKT.md` | trwałe źródło prawdy i roadmapa | po decyzji, akceptacji lub odzyskaniu faktu |
| 2 | `STAN-AKTUALNY.md` | krótki snapshot operacyjny | przy każdym istotnym handoffie |
| 3 | `00-STEROWANIE/ZASADY-PROJEKTU.md` | niezmienne reguły pracy | tylko po decyzji użytkownika |
| 4 | `04-DECYZJE/DECYZJE-PROJEKTOWE.md` | append-only log decyzji | natychmiast po decyzji |
| 5 | właściwy FINAL-AS-BUILT | dowód, jak moduł naprawdę działa | po acceptance |
| 6 | aktywna paczka | jedyny bieżący zakres zmiany | w trakcie sprintu |

## Struktura

```text
DOKUMENTACJA/
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

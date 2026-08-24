# SYSTEM PRACY NAD SKANEREM WYKRESÓW

**Wersja systemu:** `DOCS-2026-08-21-01`  
**Właściciel decyzji:** użytkownik  
**Stan:** `BASELINE PREPARED`

## 1. Cel systemu

System ma zapewnić, że kod, decyzje, wyniki testów, załączniki i kontekst AI tworzą jeden ciąg dowodowy. Żaden czat nie jest źródłem prawdy sam w sobie. Wiedza z rozmowy staje się trwała dopiero po zapisaniu w odpowiednim dokumencie i — jeśli dotyczy zmiany — po przejściu acceptance oraz FREEZE.

## 2. Przepływ informacji

```text
ROZMOWA / POMYSŁ / PROBLEM
          │
          ▼
     AKTYWNA PACZKA
          │
          ├─ 01-SPEC
          ├─ 02-AUDIT
          ├─ 03-CONFLICT-REPORT
          ├─ 04-USER-DECISIONS
          ├─ 05-IMPLEMENTATION-CONTRACT
          ├─ 06-IMPLEMENTATION + BACKUP/ROLLBACK
          ├─ 07-TESTS
          └─ 08-ACCEPTANCE
                    │
                    ▼
              FINAL-AS-BUILT
                    │
             ┌──────┴──────┐
             ▼             ▼
      MASTER / STAN   REJESTRY / CHANGELOG
             └──────┬──────┘
                    ▼
         HASHES → FREEZE → ARCHIWUM
                    │
                    ▼
              GIT COMMIT / TAG
```

## 3. Rola dokumentów

### MASTER

Przechowuje trwały cel, architekturę, roadmapę, reguły i status odzyskanych obszarów. Nie zawiera dużych logów, obrazów ani pełnych wyników testów.

### STAN-AKTUALNY

Odpowiada na pytanie „co jest prawdą teraz?”: VERSION, runtime ON/OFF, aktywne flagi, aktualna paczka, blokery, ostatni acceptance i następny bezpieczny krok.

### DECYZJE

Log append-only. Starych decyzji nie usuwa się. Nowa decyzja wskazuje `SUPERSEDES: D-xxx`.

### AKTYWNA PACZKA

Jedyny obszar, w którym wolno prowadzić zmianę. W jednym czasie może istnieć tylko jedna paczka o statusie `IN PROGRESS`, chyba że użytkownik jawnie zatwierdzi niezależną pracę równoległą.

### FINAL-AS-BUILT

Opisuje stan faktycznie wdrożony i zaakceptowany: pliki, zachowanie, konfigurację, testy, ograniczenia, operacje, rollback i hashe.

### ARCHIWUM

Zawiera zamrożony komplet sprintu wraz z dowodami. Obrazy i duże logi są przechowywane tutaj, a MASTER zawiera do nich odwołania.

## 4. Cykl aktualizacji

### Po decyzji użytkownika

1. dopisz decyzję do aktywnej paczki;
2. dopisz wpis do `DECYZJE-PROJEKTOWE.md`;
3. zaktualizuj MASTER tylko jeżeli decyzja zmienia trwały kontrakt;
4. nie implementuj, dopóki Implementation Contract nie jest kompletny.

### Po zmianie kodu

1. zanotuj dokładne pliki i zakres;
2. zachowaj backup i rollback;
3. wykonaj pełny quality gate po ostatnim zapisie;
4. uzupełnij test evidence;
5. przedstaw acceptance użytkownikowi.

### Po acceptance

1. utwórz FINAL-AS-BUILT;
2. zaktualizuj MASTER, STAN, rejestr sprintów i artefaktów;
3. wygeneruj hashe;
4. utwórz FREEZE;
5. przenieś kompletną paczkę do ARCHIWUM;
6. wykonaj kontrolę systemu;
7. commit i tag zgodnie z polityką Git.

## 5. STOP rule

Natychmiast zatrzymaj zmianę, gdy:

- rzeczywisty kod lub VERSION odbiega od preflight;
- występuje konflikt źródeł prawdy;
- zakres wymaga dodatkowej decyzji;
- test lub gate nie przechodzi;
- backup/rollback nie jest wiarygodny;
- pojawia się nieplanowana mutacja bazy albo ruch sieciowy;
- paczka zaczyna obejmować niezależny problem;
- zmieniono plik po hashach/FREEZE.

Raport STOP musi zawierać: dowód, wpływ, co pozostaje bezpieczne, opcje i decyzję wymaganą od użytkownika.

## 6. Odpowiedzialności

| Rola | Odpowiedzialność |
|---|---|
| Użytkownik | kierunek produktu, decyzje, zgoda na runtime/produkcję, acceptance |
| AI wykonujące | audit, dokumentacja, implementacja wyłącznie w kontrakcie, testy, jawne braki |
| MASTER | trwały kontrakt projektu |
| STAN | aktualny snapshot operacyjny |
| Git | historia zmian tekstowych i kodu, nie pamięć rozmowy |
| ARCHIWUM | frozen dowody i duże artefakty |

## 7. Granice

Ten system nie daje automatycznie dostępu innemu AI do dysku ani prywatnego repozytorium. Dostęp musi zostać faktycznie udostępniony przez folder projektu, konektor lub przekazany pakiet. Procedura startowa wymusza jednak odtworzenie tego samego kontekstu z plików.

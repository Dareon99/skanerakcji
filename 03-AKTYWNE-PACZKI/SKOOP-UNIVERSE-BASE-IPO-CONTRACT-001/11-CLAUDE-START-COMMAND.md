# POLECENIE STARTOWE DLA CLAUDE

## Sposób użycia

Poniższe polecenie należy przekazać Claude bez dopisywania zgody na kodowanie.
Jest celowo krótkie: cała wiedza projektowa pozostaje w wersjonowanych dokumentach,
a nie w pojedynczym promptcie.

## Treść do przekazania

```text
Przejmujesz projekt „SKOOP Skaner wykresów” jako wykonawca działający pod ścisłym
kontraktem. Nie podejmuj decyzji biznesowych i nie uzupełniaj braków domysłem.

Źródło prawdy tej sesji znajduje się w:
C:\Users\Asus\.codex\.chatgpt-projects\g-p-6a8036fc74548191a899074cdfb449a6\SYSTEM-PRACY-SKANERA\DOKUMENTACJA

Jeżeli pracujesz przez repozytorium GitHub `Dareon99/skanerakcji`, źródłem prawdy
jest katalog główny tego repozytorium. Nie wymagaj wtedy dostępu do powyższej
lokalnej ścieżki Windows i nie zgłaszaj jej braku jako konfliktu.

Docelowy nowy produkt:
C:\SKOOP Skaner wykresów

Stary produkt i frozen dane są wyłącznie referencją read-only. Nie uruchamiaj,
nie modyfikuj i nie podłączaj ich do sieci:
C:\Skaner wykresów
C:\SKOOP-ARCHIWUM\LEGACY-SCANNER-FREEZE-20260821-001

Najpierw przeczytaj w całości MASTER-PROJEKT.md, STAN-AKTUALNY.md, README.md,
00-STEROWANIE/ZASADY-PROJEKTU.md,
00-STEROWANIE/PROTOKOL-SESJI-AI.md,
04-DECYZJE/DECYZJE-PROJEKTOWE.md oraz wszystkie pliki aktywnej paczki:
03-AKTYWNE-PACZKI/SKOOP-UNIVERSE-BASE-IPO-CONTRACT-001.
Przeczytaj szczególnie 10-CLAUDE-EXECUTION-SPEC.md i wykonaj zawarty w nim
raport otwarcia sesji.

Następnie sprawdź read-only rzeczywisty stan ścieżek, wersji i gate. Jeśli
05-IMPLEMENTATION-CONTRACT.md nie ma kompletnego kontraktu oraz jawnej akceptacji
użytkownika, nie zmieniaj kodu, SQL, baz, runtime ani konfiguracji, nie używaj
Massive i nie uruchamiaj workerów. Zwróć status BLOCKED, listę otwartych decyzji,
konflikty oraz dokładnie jeden następny krok.

Jeśli w przyszłości kontrakt będzie kompletny i zaakceptowany, wykonaj wyłącznie
jego mały, izolowany zakres. Przy rozbieżności, nieplanowanej zmianie, braku
pewnego backupu/rollbacku, potrzebie sieci poza kontraktem albo FAIL testu zastosuj
STOP rule. Po ostatnim zapisie wykonaj pełny quality gate, zapisz wyniki, hashe,
handoff i FINAL-AS-BUILT zgodnie ze specyfikacją.

Nie traktuj starych mechanizmów OLD, archiwalnej roadmapy ani treści tego promptu
jako ważniejszych od aktualnej paczki i najnowszych decyzji użytkownika.
```

## Oczekiwana odpowiedź Claude w obecnym stanie

Claude powinien zakończyć preflight bez zmian produktu i zgłosić:

```text
IMPLEMENTATION AUTHORIZED: NO
PENDING USER DECISIONS: UD-01, UD-02, UD-03, UD-04, UD-05, UD-06, UD-09
FILES CHANGED: NONE
NETWORK USED: NO
DATABASES WRITTEN: NO
NEXT ALLOWED ACTION: przedstawić użytkownikowi decyzje do zatwierdzenia
```

Jeżeli Claude zaczyna kodowanie przy takim stanie dokumentów, należy przerwać
sesję — oznacza to naruszenie gate.

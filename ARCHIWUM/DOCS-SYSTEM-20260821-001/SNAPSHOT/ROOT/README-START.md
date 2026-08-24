# SKANER WYKRESÓW — START SYSTEMU PRACY

Ten katalog jest gotowym pakietem sterowania projektem. Po instalacji przy kodzie jego kanoniczną lokalizacją będzie:

```text
C:\Skaner wykresów\DOKUMENTACJA
```

## Zawsze zaczynaj tutaj

1. `DOKUMENTACJA/MASTER-PROJEKT.md`
2. `DOKUMENTACJA/STAN-AKTUALNY.md`
3. `DOKUMENTACJA/00-STEROWANIE/PROTOKOL-SESJI-AI.md`
4. AS-BUILT właściwego modułu wskazany przez `STAN-AKTUALNY.md`
5. aktywna paczka w `DOKUMENTACJA/03-AKTYWNE-PACZKI/`, jeśli istnieje

## Jedna prosta zasada

Kod i dokumentacja mogą zmienić się wyłącznie w ramach jednej nazwanej paczki przechodzącej pełny proces:

```text
SPEC → AUDIT → CONFLICT REPORT → USER DECISIONS →
IMPLEMENTATION CONTRACT → SMALL PACKAGE → TEST →
ACCEPTANCE → AS-BUILT → HASHES → FREEZE → ARCHIWUM
```

Brak decyzji lub konflikt oznacza `STOP`, nie zgadywanie.

## Szybka kontrola

Po instalacji uruchom `SPRAWDZ-SYSTEM.bat`. Kontrola jest tylko odczytowa: sprawdza komplet dokumentów, zgodność VERSION, stan Git i manifesty SHA-256.

## Status pierwszej wersji

- system dokumentacji: przygotowany;
- odzyskane dokumenty: dołączone;
- Git w projekcie źródłowym: nie był dotąd zainicjalizowany;
- zdalne repozytorium: `TO CONFIGURE`;
- tożsamość Git użytkownika: `TO CONFIGURE`;
- sekrety i bazy: muszą pozostać poza Git.

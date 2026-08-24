@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0DOKUMENTACJA\TOOLS\Check-ProjectSystem.ps1"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo SYSTEM DOKUMENTACJI: PASS
) else (
  echo SYSTEM DOKUMENTACJI: WYMAGA UWAGI ^(kod %RC%^)
)
pause
exit /b %RC%

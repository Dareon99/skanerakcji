@echo off
setlocal
powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path 'C:\SKOOP-dane' | Out-Null; Set-Content -LiteralPath 'C:\SKOOP-dane\massive.kill-switch' -Value '{\"state\":\"ON\",\"reason\":\"manual user action\"}' -Encoding UTF8"
if errorlevel 1 exit /b 1
echo Massive kill switch: ON
exit /b 0

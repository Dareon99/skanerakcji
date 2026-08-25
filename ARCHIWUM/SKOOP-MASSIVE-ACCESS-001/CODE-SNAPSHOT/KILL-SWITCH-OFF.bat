@echo off
setlocal
set "FLAG=C:\SKOOP-dane\massive.kill-switch"
powershell -NoProfile -Command "Remove-Item -LiteralPath 'C:\SKOOP-dane\massive.kill-switch' -Force -ErrorAction Stop"
if errorlevel 1 exit /b 1
echo Massive kill switch: OFF
exit /b 0

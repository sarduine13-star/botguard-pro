@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt --upgrade >nul 2>&1

echo.
echo [BGP] Launching server...
start "" http://127.0.0.1:8000/health
start "" http://127.0.0.1:8000/docs
start "" python -m uvicorn app:app --host 127.0.0.1 --port 8000

echo [BGP] Waiting for API to respond...
setlocal enabledelayedexpansion
for /l %%i in (1,1,30) do (
  for /f "delims=" %%H in ('curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/health') do set HC=%%H
  if "!HC!"=="200" goto RUNTESTS
  timeout /t 1 >nul
)

echo [BGP] API not reachable after 30 s. Exiting.
pause
exit /b 1

:RUNTESTS
echo [BGP] API online — running rule tests...
call test_rules.bat
echo [BGP] Tests complete. Starting live log tail...
echo ------------------------------------------------------------
echo (Press CTRL+C to stop tailing logs)
echo ------------------------------------------------------------
powershell -Command "Get-Content 'logs\\alerts.log' -Wait -Tail 30"

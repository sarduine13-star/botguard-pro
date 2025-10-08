@echo off
setlocal
set PYTHONUNBUFFERED=1
set APP_VERSION=0.1.0
set RULES_PATH=rules.yml
set PORT=8000
call "%~dp0.venv\Scripts\activate.bat"
uvicorn app:app --host 0.0.0.0 --port %PORT% --proxy-headers

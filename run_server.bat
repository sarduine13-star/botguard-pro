@echo off
cd /d "%~dp0"
call ".venv\Scripts\activate"
python -m uvicorn app:app --host 0.0.0.0 --port 8080

@echo off
REM === Navigate to backend folder ===
cd /d "%~dp0"

REM === Activate virtual environment ===
call .venv\Scripts\activate

REM === Upgrade pip just in case ===
python -m pip install --upgrade pip

REM === Install required Python packages ===
pip install -r requirements.txt

REM === Run BotGuard backend with Uvicorn ===
python -m uvicorn app:app --host 0.0.0.0 --port 8080

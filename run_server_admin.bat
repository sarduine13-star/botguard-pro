@echo off
REM Run Bot Guard Pro server as Administrator

cd /d "C:\Users\sardu\OneDrive\Documents\Bot-Guard-Pro-v1.0\backend"

echo Starting Bot Guard Pro on port 9000...
uvicorn app:app --host 127.0.0.1 --port 9000 --reload

pause

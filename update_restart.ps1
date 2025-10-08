cd "C:\Users\sardu\OneDrive\Documents\Bot-Guard-Pro-v1.0\backend"
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
git pull 2>$null
nssm restart BotGuardPro 2>$null

@echo off
title BotGuardPro Auto-Fix + Deploy
cd /d "C:\Users\Redwine\Projects\BotGuardPro\backend"

echo === Updating backend FastAPI root and enabling CORS ===
(
echo from fastapi import FastAPI
echo from fastapi.middleware.cors import CORSMiddleware
echo.
echo app = FastAPI()
echo.
echo app.add_middleware(
echo.    CORSMiddleware,
echo.    allow_origins=["*"],
echo.    allow_methods=["*"],
echo.    allow_headers=["*"],
echo )
echo.
echo @app.get("/", include_in_schema=False)
echo def root():
echo.    return {"status": "Backend is live"}
) > app.py

echo.
echo === Committing and pushing to GitHub ===
git add app.py
git commit -m "Auto fix backend root and CORS"
git push

echo.
echo === Triggering redeploy on Render ===
set API_KEY=rnd_S8wdHGgnOeXDKSSRTxgmEjFgGWZI
curl -X POST https://api.render.com/v1/services/botguard-pro-13/deploys ^
     -H "Accept: application/json" ^
     -H "Authorization: Bearer %API_KEY%"

echo.
echo === Waiting 60 seconds for Render build ===
timeout /t 60 >nul

echo.
echo === Checking backend status ===
curl https://botguard-pro-13.onrender.com/

echo.
echo === Finished. Backend redeployed and verified. ===
pause

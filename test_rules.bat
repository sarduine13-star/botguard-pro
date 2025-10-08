@echo off
setlocal
cd /d %~dp0

rem === config ===
set TOKEN=devtoken
set BASE=http://127.0.0.1:8080

echo [BGP TEST] Reloading rules...
curl -s -X POST -H "Authorization: Bearer %TOKEN%" %BASE%/rules/reload & echo.

echo [BGP TEST] Listing rules...
curl -s -H "Authorization: Bearer %TOKEN%" %BASE%/rules & echo. & echo ----------------------------

echo [1/4] SQL injection rule
curl -s -X POST %BASE%/events ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"nginx\",\"ip\":\"127.0.0.1\",\"message\":\"SELECT * FROM users\",\"tags\":[\"web\"],\"count\":1}"
echo.
timeout /t 1 >nul

echo [2/4] Failed logins rule (3 events to hit threshold)
for /l %%i in (1,1,3) do (
  curl -s -X POST %BASE%/events ^
    -H "Authorization: Bearer %TOKEN%" ^
    -H "Content-Type: application/json" ^
    -d "{\"source\":\"auth-service\",\"ip\":\"127.0.0.1\",\"message\":\"failed login for user\",\"tags\":[\"auth\"],\"count\":1}"
  echo.
  timeout /t 1 >nul
)

echo [3/4] Bad IP range rule (192.168.66.5)
curl -s -X POST %BASE%/events ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"scanner\",\"ip\":\"192.168.66.5\",\"message\":\"scan detected\",\"tags\":[\"net\"],\"count\":1}"
echo.
timeout /t 1 >nul

echo [4/4] Block bad IPs rule (10.0.0.5)
curl -s -X POST %BASE%/events ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"nginx\",\"ip\":\"10.0.0.5\",\"message\":\"sql injection attempt\",\"tags\":[\"web\"],\"count\":1}"
echo.

echo ----------------------------
echo Last 10 alerts from logs\alerts.log
powershell -NoProfile -Command "Get-Content '.\logs\alerts.log' -Tail 10"
echo.
echo Done. Press any key to close...
pause >nul
endlocal

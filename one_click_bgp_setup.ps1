
param(
  [string]$ServiceName = "BotGuardPro",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
  Write-Host ">> $msg"
}

# Resolve project path to the folder containing this script
$Project = Split-Path -Parent $PSCommandPath
if (-not $Project) { $Project = Get-Location }

Write-Step "Project: $Project"

# Ensure logs dir exists
New-Item -ItemType Directory -Force -Path "$Project\logs" | Out-Null

# Python venv and deps
Write-Step "Ensuring Python venv and dependencies..."
if (!(Test-Path "$Project\.venv")) {
  Write-Step "Creating venv (.venv)..."
  python -m venv "$Project\.venv"
}
& "$Project\.venv\Scripts\python.exe" -m pip install --upgrade pip
if (Test-Path "$Project\requirements.txt") {
  & "$Project\.venv\Scripts\pip.exe" install -r "$Project\requirements.txt"
}

# Create/overwrite run_botguard.bat pinned to port
Write-Step "Writing run_botguard.bat (port $Port)..."
$bat = @"
@echo off
setlocal
set PYTHONUNBUFFERED=1
set APP_VERSION=0.1.0
set RULES_PATH=rules.yml
set PORT=$Port
call "%~dp0.venv\Scripts\activate.bat"
uvicorn app:app --host 0.0.0.0 --port %PORT% --proxy-headers
"@
Set-Content -Path "$Project\run_botguard.bat" -Value $bat -Encoding ascii

# Install NSSM if available; require chocolatey else skip with message
function Ensure-Nssm {
  if (Get-Command nssm -ErrorAction SilentlyContinue) { return $true }
  if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Step "Installing NSSM via Chocolatey..."
    choco install nssm -y | Out-Null
    return $true
  } else {
    Write-Warning "NSSM is not installed and Chocolatey not found. Install NSSM manually from https://nssm.cc/download and re-run."
    return $false
  }
}

# Create/replace service
if (Ensure-Nssm) {
  Write-Step "Configuring Windows Service '$ServiceName'..."
  & nssm remove $ServiceName confirm | Out-Null 2>$null
  & nssm install $ServiceName "$Project\run_botguard.bat" | Out-Null
  & nssm set $ServiceName AppDirectory "$Project" | Out-Null
  & nssm set $ServiceName AppStdout "$Project\logs\botguard.out.log" | Out-Null
  & nssm set $ServiceName AppStderr "$Project\logs\botguard.err.log" | Out-Null
  & nssm set $ServiceName Start SERVICE_AUTO_START | Out-Null
  & nssm set $ServiceName AppThrottle 1500 | Out-Null
  & nssm restart $ServiceName | Out-Null
}

# Firewall rules (idempotent)
Write-Step "Ensuring firewall rules..."
$allowName = "BotGuardPro Inbound $Port"
$blockName = "Block BotGuardPro Public $Port"
if (-not (Get-NetFirewallRule -DisplayName $allowName -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -DisplayName $allowName -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -Profile Private | Out-Null
}
if (-not (Get-NetFirewallRule -DisplayName $blockName -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -DisplayName $blockName -Direction Inbound -Action Block -Protocol TCP -LocalPort $Port -Profile Public | Out-Null
}

# Nightly update+restart job
Write-Step "Creating nightly update script and scheduled task..."
$update = @"
cd "$Project"
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
git pull 2>`$null
nssm restart $ServiceName 2>`$null
"@
Set-Content "$Project\update_restart.ps1" $update -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Project\update_restart.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 3:05am
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U -RunLevel Highest
Unregister-ScheduledTask -TaskName "BotGuardPro Nightly Update" -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
Register-ScheduledTask -TaskName "BotGuardPro Nightly Update" -Action $action -Trigger $trigger -Principal $principal | Out-Null

# Sign-rules helper (idempotent overwrite)
Write-Step "Writing sign_rules.py helper..."
$sign = @"
import hashlib, hmac, sys, os
key = os.environ.get('RULES_SIGNING_KEY','dev-key-change').encode()
p = sys.argv[1] if len(sys.argv)>1 else 'rules.yml'
b = open(p,'rb').read().rstrip(b'\n')
sig = hmac.new(key, b, hashlib.sha256).hexdigest()
open(p,'wb').write(b + b'\n# sig=' + sig.encode() + b'\n')
print(sig)
"@
Set-Content "$Project\sign_rules.py" $sign -Encoding UTF8

# Smoke test (if service running)
Write-Step "Health check..."
try {
  $resp = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$Port/health" -TimeoutSec 4
  Write-Host "Health: $($resp.StatusCode) ($($resp.Content))"
} catch {
  Write-Warning "Service not responding yet. If this is first run, give it a few seconds or check logs."
}

Write-Step "Done."

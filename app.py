from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict
import ipaddress
import os

# ----- CONFIG -----
BLOCKLIST_FILE = Path("blocklist.txt")
API_KEY = os.getenv("BOTGUARD_API_KEY", "test-key")
        # <- read exactly this env var
BETA_LIMIT = int(os.getenv("BETA_LIMIT", "5"))
# -------------------

app = FastAPI(
    title="Bot Guard Pro",
    swagger_ui_parameters={"persistAuthorization": True},
)

# Security header (shows "Authorize" in Swagger)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# in-memory per-key usage (resets on restart)
usage = defaultdict(int)

class TrafficLog(BaseModel):
    ip: str
    user_agent: str | None = None

def load_blocked() -> set[str]:
    if not BLOCKLIST_FILE.exists():
        return set()
    with open(BLOCKLIST_FILE, "r", encoding="utf-8") as f:
        return {
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        }

BLOCKED_IPS = load_blocked()

def is_blocked(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        # invalid IP → treat as blocked
        return True
    return ip in BLOCKED_IPS

def require_key(x_api_key: str | None):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    if usage[x_api_key] >= BETA_LIMIT:
        raise HTTPException(status_code=402, detail="Beta limit reached")
    usage[x_api_key] += 1

@app.post("/check")
async def check_traffic(
    log: TrafficLog,
    x_api_key: str | None = Security(api_key_header)
):
    require_key(x_api_key)
    blocked = is_blocked(log.ip)
    return {"ip": log.ip, "blocked": blocked, "reason": "In blocklist" if blocked else "Allowed"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/reload")
def reload_blocklist(x_api_key: str | None = Security(api_key_header)):
    require_key(x_api_key)
    global BLOCKED_IPS
    BLOCKED_IPS = load_blocked()
    return {"blocked_count": len(BLOCKED_IPS)}

@app.get("/usage")
def get_usage(x_api_key: str | None = Security(api_key_header)):
    require_key(x_api_key)
    return {"used": usage.get(x_api_key, 0), "limit": BETA_LIMIT}

@app.post("/reset_usage")
def reset_usage(x_api_key: str | None = Security(api_key_header)):
    # Only owner (you) can reset usage counters
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Not allowed")
    usage.clear()
    return {"message": "Usage counters reset to 0"}

# (Optional) Quick debug endpoint to confirm header receipt
@app.get("/whoami")
def whoami(x_api_key: str | None = Security(api_key_header)):
    return {"received_header": x_api_key, "server_has_api_key": bool(API_KEY)}

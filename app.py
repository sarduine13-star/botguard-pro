from fastapi import FastAPI, HTTPException
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
import ipaddress, os

load_dotenv()  # pulls BOTGUARD_API_KEY and BETA_LIMIT from .env

app = FastAPI(
    title="Bot Guard Pro",
    swagger_ui_parameters={"persistAuthorization": True},
)

# ====== CONFIG ======
BLOCKLIST_FILE = Path("blocklist.txt")
API_KEY = os.getenv("BOTGUARD_API_KEY", "test-key")
BETA_LIMIT = int(os.getenv("BETA_LIMIT", "5"))
# ====================

# Declare API Key security (this makes the Swagger "Authorize" button appear)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# simple per-key in-memory usage counter (resets on restart)
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
        return True
    return ip in BLOCKED_IPS

def require_key(x_api_key: str | None):
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
    usage[x_api_key] -= 1  # don’t charge for checking usage
    return {"used": usage[x_api_key], "limit": BETA_LIMIT}

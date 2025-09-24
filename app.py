from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from pathlib import Path
from collections import defaultdict
import ipaddress, os, json

# ----- CONFIG -----
BLOCKLIST_FILE = Path("blocklist.txt")
KEYS_FILE = Path(os.getenv("KEYS_FILE", "keys.json"))  # NEW
DEFAULT_BETA_LIMIT = int(os.getenv("BETA_LIMIT", "5"))
# -------------------

app = FastAPI(title="Bot Guard Pro", swagger_ui_parameters={"persistAuthorization": True})

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

usage = defaultdict(int)  # usage per key

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

# ---- MULTI-KEY SUPPORT ----
# Expected keys.json format:
# [
#   {"tier":"free",  "key":"free-key",  "limit":25},
#   {"tier":"pro",   "key":"pro-key",   "limit":500},
#   {"tier":"elite", "key":"elite-key", "limit":1000000000}
# ]
def load_keys():
    if not KEYS_FILE.exists():
        return []
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # normalize
    out = []
    for row in data:
        if isinstance(row, dict) and "key" in row:
            out.append({
                "tier":  row.get("tier", "unknown"),
                "key":   str(row["key"]).strip().strip('"').strip("'"),
                "limit": int(row.get("limit", DEFAULT_BETA_LIMIT)),
            })
    return out

KEYBOOK = load_keys()  # list of {tier,key,limit}

def find_key_info(key: str | None):
    clean = (key or "").strip().strip('"').strip("'")
    for row in KEYBOOK:
        if clean == row["key"]:
            return row  # {"tier":..., "key":..., "limit":...}
    return None
# ---------------------------

def is_blocked(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return True
    return ip in BLOCKED_IPS

def require_key(x_api_key: str | None):
    info = find_key_info(x_api_key)
    if not info:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    k = info["key"]
    lim = info["limit"]
    if usage[k] >= lim:
        raise HTTPException(status_code=402, detail="Beta limit reached")
    usage[k] += 1
    return info  # return tier/limit if you need it downstream

@app.post("/check")
async def check_traffic(log: TrafficLog, x_api_key: str | None = Security(api_key_header)):
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
    info = require_key(x_api_key)
    k = info["key"]
    return {"used": usage.get(k, 0), "limit": info["limit"], "tier": info["tier"]}

@app.post("/reset_usage")
def reset_usage(x_api_key: str | None = Security(api_key_header)):
    info = require_key(x_api_key)
    # only elite can reset (example policy)
    if info["tier"] != "elite":
        raise HTTPException(status_code=403, detail="Not allowed")
    usage.clear()
    return {"message": "Usage counters reset to 0"}

@app.get("/whoami")
def whoami(x_api_key: str | None = Security(api_key_header)):
    info = find_key_info(x_api_key)
    return {"received_header": (x_api_key or ""), "recognized": bool(info), "tier": info["tier"] if info else None}

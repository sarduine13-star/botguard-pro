# app.py
from __future__ import annotations

import json
import os
import sqlite3
import time
import ipaddress
from pathlib import Path
from typing import Dict, Tuple

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Bot Guard Pro", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["X-API-Key", "X-Forwarded-For", "Content-Type"],
)

# ---------- config ----------
HERE = Path(__file__).resolve().parent
KEYS_PATH = Path(os.environ.get("KEYS_FILE") or (HERE / "keys.json"))
BLOCKLIST_PATH = HERE / "blocklist.txt"
TIER_LIMITS: Dict[str, int] = {"free": 30, "pro": 300, "enterprise": 3000}

# ---------- loaders ----------
def load_keys() -> Dict[str, Dict[str, str]]:
    if not KEYS_PATH.exists():
        raise RuntimeError(f"keys.json missing at {KEYS_PATH}")
    try:
        data = json.loads(KEYS_PATH.read_text())
        return data  # {"<api_key>": {"tier": "...", "owner": "..."}}
    except Exception as e:
        raise RuntimeError(f"invalid keys.json: {e}")

def load_blocklist() -> tuple[set[str], list[ipaddress._BaseNetwork]]:
    if not BLOCKLIST_PATH.exists():
        BLOCKLIST_PATH.write_text("")
    ips: set[str] = set()
    nets: list[ipaddress._BaseNetwork] = []
    for raw in BLOCKLIST_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if "/" in line:
                nets.append(ipaddress.ip_network(line, strict=False))
            else:
                ipaddress.ip_address(line)
                ips.add(line)
        except ValueError:
            continue  # ignore malformed
    return ips, nets

KEYS = load_keys()
BL_IPS, BL_NETS = load_blocklist()

# ---------- usage tracking (SQLite, per-minute window) ----------
DB_PATH = HERE / "usage.db"

def _db():
    conn = getattr(app.state, "db", None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage (
              api_key TEXT NOT NULL,
              window  INTEGER NOT NULL,
              count   INTEGER NOT NULL,
              PRIMARY KEY (api_key, window)
            );
            """
        )
        app.state.db = conn
    return conn

def _window_now() -> int:
    now = int(time.time())
    return now - (now % 60)

def get_count(key: str, window: int) -> int:
    cur = _db().execute(
        "SELECT count FROM usage WHERE api_key=? AND window=?", (key, window)
    )
    row = cur.fetchone()
    return row[0] if row else 0

def set_count(key: str, window: int, value: int) -> None:
    _db().execute(
        "INSERT INTO usage(api_key,window,count) VALUES(?,?,?) "
        "ON CONFLICT(api_key,window) DO UPDATE SET count=excluded.count",
        (key, window, value),
    )
    _db().commit()

def check_and_count(key: str, tier: str) -> None:
    limit = TIER_LIMITS.get(tier, 0)
    if limit <= 0:
        raise HTTPException(status_code=403, detail="key tier disabled")
    w = _window_now()
    cnt = get_count(key, w)
    if cnt + 1 > limit:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    set_count(key, w, cnt + 1)

# ---------- helpers ----------
def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"

def is_blocked(ip: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if ip in BL_IPS:
        return True
    return any(ip_obj in net for net in BL_NETS)

def auth_from_header(x_api_key: str | None) -> tuple[str, str]:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="missing X-API-Key")
    rec = KEYS.get(x_api_key)
    if not rec:
        raise HTTPException(status_code=401, detail="invalid API key")
    return x_api_key, rec.get("tier", "free")

# ---------- routes ----------
@app.get("/")
def root():
    return {"ok": True, "service": "Bot Guard Pro"}

@app.get("/health")
def health():
    return {"status": "up"}

@app.get("/protected")
def protected(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_forwarded_for: str | None = Header(default=None, alias="X-Forwarded-For"),
):
    key, tier = auth_from_header(x_api_key)
    ip = x_forwarded_for or client_ip(request)
    if is_blocked(ip):
        raise HTTPException(status_code=403, detail="ip blocked")
    check_and_count(key, tier)
    remaining = TIER_LIMITS[tier] - get_count(key, _window_now())
    return {"ok": True, "ip": ip, "tier": tier, "remaining_per_min": remaining}

# optional: hot reload configs
@app.post("/admin/reload")
def reload_configs(x_secret: str | None = Header(None)):
    if x_secret != "dev-only":
        raise HTTPException(status_code=401, detail="unauthorized")
    global KEYS, BL_IPS, BL_NETS
    KEYS = load_keys()
    BL_IPS, BL_NETS = load_blocklist()
    return {"reloaded": True, "keys": len(KEYS), "ips": len(BL_IPS), "nets": len(BL_NETS)}

# ---------- OpenAPI: Authorize for X-API-Key ----------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
        "type": "apiKey", "in": "header", "name": "X-API-Key"
    }
    schema["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
@app.get("/admin/usage/{api_key}")
def get_usage(api_key: str):
    # returns current window count and remaining for this key
    rec = KEYS.get(api_key)
    if not rec:
        raise HTTPException(status_code=404, detail="unknown key")
    tier = rec.get("tier", "free")
    w = _window_now()
    used = get_count(api_key, w)
    limit = TIER_LIMITS.get(tier, 0)
    remaining = max(limit - used, 0)
    return {"api_key": api_key, "tier": tier, "window": w, "used": used, "limit": limit, "remaining": remaining}

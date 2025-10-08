# app.py — proof mode
from fastapi import FastAPI
import os, sys
print("[BGP] app.py loaded from:", __file__)
print("[BGP] cwd:", os.getcwd())

# --- INLINE RULES ENDPOINT (works even if imports fail) ---
from fastapi import APIRouter
from pathlib import Path
import json
try:
    import yaml
except Exception:
    yaml = None

rules_router = APIRouter()
@rules_router.get("/rules", tags=["rules"])
def _rules_inline():
    d = Path(__file__).parent / "rules"
    items = []
    for p in d.glob("*.*"):
        if p.suffix.lower() in {".yaml", ".yml", ".json"}:
            try:
                data = (json.loads(p.read_text(encoding="utf-8"))
                        if p.suffix.lower()==".json"
                        else (yaml.safe_load(p.read_text(encoding="utf-8")) if yaml else {"note":"install pyyaml"}))
            except Exception as e:
                data = {"error": str(e)}
            items.append({"file": p.name, "size": p.stat().st_size, "data": data})
    return {"count": len(items), "items": items}
# ----------------------------------------------------------

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
app = FastAPI(title="Bot Guard Pro")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    return {"ok": True}

# ✅ MOUNT the rules router (inline) under /api/v1
app.include_router(rules_router, prefix=API_PREFIX)

# extra probe route so we can spot this build in Swagger
@app.get("/ping123")
def ping123():
    return {"pong": 123}

# dump all routes at startup so we can SEE them
@app.on_event("startup")
async def _dump_routes():
    print("[BGP] Routes:")
    for r in app.routes:
        try:
            print("  ", r.methods, r.path)
        except Exception:
            pass

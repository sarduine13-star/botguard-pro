# app.py  — minimal, known-good
from fastapi import FastAPI
import os

# ⬇️ import the router you just created
from rules_api import router as rules_router

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

app = FastAPI(title="Bot Guard Pro")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    return {"ok": True}

# ⬇️ mount rules under /api/v1
app.include_router(rules_router, prefix=API_PREFIX)

# Debug: print all routes at startup
@app.on_event("startup")
async def _dump_routes():
    print("[BGP] Routes:")
    for r in app.routes:
        try:
            print("   ", r.methods, r.path)from fastapi import APIRouter
import importlib
import app  # your main FastAPI app module

router = APIRouter()

@router.get("/reload", tags=["rules"])
def reload_rules():
    try:
        importlib.reload(app)  # reloads the app and rules dynamically
        return {"status": "reloaded"}
    except Exception as e:
        return {"error": str(e)}

        except Exception:
            pass

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
from fastapi.responses import HTMLResponse  # <-- add this import near your other imports

LANDING_HTML = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>BotGuard Pro — Block junk traffic before it hits your app</title>
<script src="https://cdn.tailwindcss.com"></script>
</head><body class="bg-gray-50 text-gray-900">
<header class="max-w-6xl mx-auto px-6 py-10">
  <h1 class="text-3xl md:text-4xl font-extrabold">BotGuard Pro</h1>
  <p class="text-lg mt-3 max-w-3xl">Lightweight FastAPI WAF — block junk traffic, throttle abusers, and hot-reload signed rules.</p>
  <div class="mt-6 flex flex-wrap gap-3">
    <a href="/health" class="px-5 py-3 rounded-xl bg-green-600 text-white">Live Health</a>
    <a href="/docs"   class="px-5 py-3 rounded-xl bg-gray-800 text-white">API Docs</a>
    <a href="#pricing" class="px-5 py-3 rounded-xl bg-indigo-600 text-white">Pricing</a>
  </div>
</header>
<main class="max-w-6xl mx-auto px-6 space-y-12 pb-20">
  <section class="grid md:grid-cols-3 gap-6">
    <div class="p-6 bg-white rounded-2xl shadow"><h3 class="font-bold">Drop-in</h3><p class="mt-2 text-gray-600">Behind Nginx/Traefik or as an API gateway.</p></div>
    <div class="p-6 bg-white rounded-2xl shadow"><h3 class="font-bold">Signed rules</h3><p class="mt-2 text-gray-600">Hot-reload YAML packs safely.</p></div>
    <div class="p-6 bg-white rounded-2xl shadow"><h3 class="font-bold">Observability</h3><p class="mt-2 text-gray-600">/metrics + JSON logs.</p></div>
  </section>
  <section id="pricing" class="bg-white p-8 rounded-2xl shadow">
    <h2 class="text-2xl font-bold mb-4">Pricing</h2>
    <div class="grid md:grid-cols-3 gap-6">
      <div class="border rounded-2xl p-6"><h3 class="font-bold">Starter</h3><p>50k req/mo</p><p class="text-3xl font-extrabold mt-3">$19</p></div>
      <div class="border-2 border-indigo-600 rounded-2xl p-6"><h3 class="font-bold">Pro</h3><p>500k req/mo · alerts</p><p class="text-3xl font-extrabold mt-3">$39</p></div>
      <div class="border rounded-2xl p-6"><h3 class="font-bold">Scale</h3><p>SLA · priority support</p><p class="text-3xl font-extrabold mt-3">Talk to us</p></div>
    </div>
  </section>
</main>
<footer class="max-w-6xl mx-auto px-6 py-8 text-sm text-gray-500">© BotGuard Pro.</footer>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def landing():
    return LANDING_HTML

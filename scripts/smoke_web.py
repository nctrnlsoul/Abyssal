"""Exercise every route in-process. No server, no port, no flake."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from web.app import app

c = TestClient(app)
ok = True

def check(label, cond, detail=""):
    global ok
    ok = ok and cond
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{'  ' + detail if detail else ''}")

r = c.get("/")
check("GET / returns 200", r.status_code == 200, f"{len(r.text)} bytes")
check("CSP present", "Content-Security-Policy" in r.headers)
check("CSP has no unsafe-inline for script",
      "unsafe-inline" not in r.headers["Content-Security-Policy"].split("style-src")[0])
check("HSTS present", "Strict-Transport-Security" in r.headers)
check("nosniff present", r.headers.get("X-Content-Type-Options") == "nosniff")
check("frame deny", r.headers.get("X-Frame-Options") == "DENY")

r = c.get("/api/bands")
b = r.json()
check("GET /api/bands 200", r.status_code == 200)
check("5 segments", len(b["segments"]) == 5)
check("trigger inside very low",
      abs(b["trigger_pct"] - 33.98) < 0.05, f"{b['trigger_pct']}%")

r = c.get("/api/run")
d = r.json()
check("GET /api/run 200", r.status_code == 200)
check("run is labelled recorded", d.get("mode") == "recorded" and d.get("live") is False)
check("citations verified", d["verification"]["passed"] == d["verification"]["checked"],
      f"{d['verification']['passed']}/{d['verification']['checked']}")
check("no-store on run", r.headers.get("Cache-Control") == "no-store")

r = c.get("/healthz")
check("GET /healthz 200", r.status_code == 200)

r = c.get("/nope")
check("404 is generic", r.status_code == 404 and r.json() == {"error": "not available"})
check("404 still carries headers", "Content-Security-Policy" in r.headers)

print("\nOVERALL:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

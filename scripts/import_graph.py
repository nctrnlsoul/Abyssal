"""What does the console ACTUALLY import? Measured in a fresh interpreter.

The deployed image installs only what this proves is needed. A public,
unauthenticated URL has no business loading an agent framework, and the
previous project asserted exactly this after review found the console pulling
in google.adk through its import chain.
"""
import subprocess, sys, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CODE = r"""
import sys, json
sys.path.insert(0, r"%s")
from fastapi.testclient import TestClient
from web.app import app
c = TestClient(app)
for path in ("/", "/api/run", "/api/bands", "/api/waveform", "/api/source-image", "/healthz", "/nope"):
    c.get(path)
banned = sorted(m for m in sys.modules if m.split(".")[0] in
                ("google", "pymupdf", "fitz", "numpy", "pandas"))
print(json.dumps({"banned_loaded": banned, "total_modules": len(sys.modules)}))
""" % ROOT

r = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, cwd=ROOT)
line = [l for l in r.stdout.splitlines() if l.startswith("{")]
if not line:
    print("FAILED to run probe"); print(r.stdout[-2000:]); print(r.stderr[-2000:]); raise SystemExit(1)
d = json.loads(line[-1])
print(f"modules loaded after exercising every route: {d['total_modules']}")
if d["banned_loaded"]:
    print("HEAVY DEPENDENCIES REACHED BY THE CONSOLE:")
    for m in d["banned_loaded"][:40]:
        print("   ", m)
    raise SystemExit(1)
print("CLEAN: the console reaches no google-adk, no pymupdf, no numpy.")

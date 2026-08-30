"""The public console. Deploys to Cloud Run as-is.

SECURITY POSTURE, stated plainly because this is a PUBLIC, UNAUTHENTICATED URL:

  - It is KEYLESS AND SPENDLESS. No GOOGLE_API_KEY is read here, none is baked
    into the image, and none is set on the Cloud Run service. A visitor cannot
    cause a model call, so a visitor cannot spend money.

    This matters more here than it did on the previous project. A full Abyssal
    run costs about $0.42 and reads a 532-page document. An unauthenticated
    endpoint that spends that per click is denial-of-wallet, and it is exactly
    what the Gemini-authored draft shipped: no auth, no rate limit, an unbounded
    in-memory job dict, and a live client constructed on every request.

  - So the console serves a RECORDED REAL RUN, labelled as recorded on its face,
    with its real timings and real outputs. The live path is agents/pipeline.py
    and scripts/record_run.py, in the repo, and it is what produced the file.

  - Every route is GET. There is no job creation, so there is no job store to
    exhaust.
  - Inputs are clamped, not trusted. Errors are generic.
  - CSP allows NO inline script. The one inline <script> is allowed by its
    sha256 hash, computed at startup from the shipped file so it cannot drift.

Known limit, deliberately not hidden: the rate limiter is in-process, so it is
per-instance rather than per-service. --max-instances on the deploy bounds the
real total.
"""
from __future__ import annotations
import base64, hashlib, json, os, re, time
from collections import OrderedDict, deque
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response

from core.synthesis import (
    FL_CLOSURE_TRIGGER_CELLS_PER_L, ruler_segments, trigger_position_pct,
)
from core.waveform import envelope
from core.sites import POSITIONING_NOTE, SITES_ON_IMAGE

app = FastAPI(title="Abyssal", docs_url=None, redoc_url=None, openapi_url=None)

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
_PAGE = (_HERE / "index.html").read_text(encoding="utf-8")
# Read ONCE at import, and the CSP hash is derived from it, so an edited
# index.html is served stale until the process restarts. uvicorn --reload
# watches .py files, not .html, so editing the page alone does not reload.
# Touch this file or restart after any markup change.

_RUN_PATH = _ROOT / "docs" / "recorded-run.json"
_RUN = json.loads(_RUN_PATH.read_text(encoding="utf-8")) if _RUN_PATH.exists() else {}


def _inline_script_hashes(html: str) -> list[str]:
    """sha256 of every inline <script> body, in CSP form.

    Derived at startup from the shipped file. Hard-coding a hash means the CSP
    silently breaks the console the first time anyone edits the script, and the
    usual fix for that is pasting in 'unsafe-inline', which throws the whole
    protection away. So it is computed, not written down.
    """
    bodies = re.findall(
        r"<script(?![^>]*\bsrc=)(?![^>]*\btype=\"application/json\")[^>]*>(.*?)</script>",
        html, re.S)
    return ["'sha256-" + base64.b64encode(
        hashlib.sha256(b.encode("utf-8")).digest()).decode() + "'" for b in bodies]


_CSP = "; ".join([
    "default-src 'none'",
    "script-src 'self' " + " ".join(_inline_script_hashes(_PAGE)),
    # style-src keeps 'unsafe-inline' for the one <style> block. Inline STYLE is
    # a far weaker vector than inline script, and script-src above carries no
    # 'unsafe-inline' at all. No font-src or connect-src to a third party
    # because the page makes ZERO external requests, by design: every external
    # asset in the draft this replaces failed to load.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "connect-src 'self'",
    "base-uri 'none'",
    "form-action 'none'",
    "frame-ancestors 'none'",
    "object-src 'none'",
])

_HEADERS = {
    "Content-Security-Policy": _CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}

# --- rate limiting -----------------------------------------------------------
_WINDOW_S = 60
_MAX_PER_CLIENT = 60
_MAX_GLOBAL = 600
_MAX_KEYS = 20_000


def _hops() -> int:
    """Parse once, safely. int(os.environ[...]) at module scope turns a typo in
    an operator knob into a container that never binds, which is a Cloud Run
    crash loop. A negative value is worse: it makes the length guard vacuously
    true and indexes parts[0], restoring the leftmost-hop bug this exists to
    prevent."""
    try:
        return max(0, int(os.environ.get("ABYSSAL_TRUSTED_PROXY_HOPS", "0")))
    except (TypeError, ValueError):
        return 0


_TRUSTED_PROXY_HOPS = _hops()
_hits: "OrderedDict[str, deque[float]]" = OrderedDict()
_global: deque[float] = deque()


def _client(request: Request) -> str:
    """Count from the END of X-Forwarded-For, never the start.

    Google documents the header for its external load balancer and documents
    NOTHING for a bare run.app service, which is what deploy.ps1 creates. An
    undocumented platform behavior is not a foundation for a security control,
    so this does not guess a hop count. 0 means read the LAST entry, which is
    written by infrastructure under every chain and never by the caller.
    """
    parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",")]
    parts = [p for p in parts if p]
    if len(parts) >= _TRUSTED_PROXY_HOPS + 1:
        return parts[-(_TRUSTED_PROXY_HOPS + 1)][:64]
    peer = request.client.host if request.client else ""
    return (peer or "unknown")[:64]


def _prune(q: deque[float], now: float) -> None:
    while q and now - q[0] > _WINDOW_S:
        q.popleft()


def _over_limit(key: str) -> str | None:
    """Returns the rule that tripped, or None.

    Three versions of this on the previous project, and the second was the fix
    for the first. v1 inserted above the checks and evicted below, so eviction
    ran only for ALLOWED requests while only REJECTED ones grew the table. v2
    evicted on every path, which made eviction attacker-driven: enough distinct
    keys could push a real client's bucket out and hand it a fresh one. v3, this
    one, looks up WITHOUT inserting and inserts only on the path about to
    append, so growth and cleanup are on one path BY CONSTRUCTION.

    Client check FIRST, and charge nothing until both pass. Charging the global
    window before the per-client check let 600 requests from one address, 540
    already rejected, consume the whole instance budget and 429 everyone else.
    A rate limiter a rejected request can pay for is a DoS amplifier.
    """
    now = time.monotonic()
    q = _hits.get(key)
    if q is not None:
        _hits.move_to_end(key)
        _prune(q, now)
    _prune(_global, now)

    if q is not None and len(q) >= _MAX_PER_CLIENT:
        return "client"
    if len(_global) >= _MAX_GLOBAL:
        return "global"

    if q is None:
        q = _hits[key] = deque()
    q.append(now)
    _global.append(now)
    while len(_hits) > _MAX_KEYS:
        _hits.popitem(last=False)
    return None


def _json(payload: dict, status: int) -> JSONResponse:
    r = JSONResponse(payload, status_code=status)
    r.headers.update(_HEADERS)
    return r


@app.exception_handler(RequestValidationError)
async def _bad_request(request: Request, exc: RequestValidationError) -> JSONResponse:
    """FastAPI's default 422 echoes the offending input and names the pydantic
    error type, which fingerprints the stack and reflects attacker text."""
    return _json({"error": "bad request"}, 400)


@app.exception_handler(StarletteHTTPException)
async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """404 and 405 otherwise return Starlette's {"detail": ...}, which
    fingerprints the framework for the same reason the 422 was overridden.
    Overriding one and not the others is half a fix."""
    return _json({"error": "not available"}, exc.status_code)


@app.middleware("http")
async def guard(request: Request, call_next):
    try:
        tripped = _over_limit(_client(request))
        if tripped:
            return _json({"error": "rate limited"}, 429)
        response = await call_next(request)
    except Exception:
        # _client and _over_limit sit INSIDE this try on purpose. On the
        # previous project they sat outside, a bad proxy-hops value made
        # _client raise, and the response was a bare text/plain 500 with every
        # security header missing. The one path where the server is confused
        # was the one path with no protection on it.
        return _json({"error": "request could not be completed"}, 500)
    response.headers.update(_HEADERS)
    if "cache-control" not in response.headers:
        # A redeploy must not serve yesterday's console out of heuristic
        # browser cache. Routes that want caching set their own header.
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.head("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _PAGE


@app.get("/api/run")
def run() -> JSONResponse:
    """The recorded run. Labelled recorded in the payload AND on the page."""
    if not _RUN:
        return _json({"error": "no recorded run available"}, 503)
    r = _json({**_RUN, "mode": "recorded", "live": False}, 200)
    r.headers["Cache-Control"] = "no-store"
    return r


@app.get("/api/bands")
def bands() -> JSONResponse:
    """The ruler geometry, computed server-side from the published bands so the
    graphic and the numbers cannot drift apart."""
    return _json({
        "segments": ruler_segments(),
        "trigger_pct": trigger_position_pct(),
        "trigger_cells_per_l": FL_CLOSURE_TRIGGER_CELLS_PER_L,
    }, 200)


_CLIP = _ROOT / "data" / "reef_window_a.wav"
try:
    # Computed once at import. It is a fixed committed clip, so recomputing it
    # per request would be waste, and failing to serve it must not take the
    # console down: the waveform is an enrichment, the citations are the point.
    _WAVE = envelope(str(_CLIP)) if _CLIP.exists() else None
except Exception:
    _WAVE = None


@app.get("/api/waveform")
def waveform() -> JSONResponse:
    """Peak envelope of the actual hydrophone clip the acoustic agent read.

    Real data, not a decorative sine wave. If it is unavailable the page draws
    nothing rather than drawing something invented.
    """
    if not _WAVE:
        return _json({"error": "waveform unavailable"}, 503)
    return _json({**_WAVE, "source": "NOAA/Navy SanctSound FK04, Florida Keys NMS"}, 200)


_HAB = _ROOT / "data" / "hab_forecast_cellcounts.png"


@app.get("/api/source-image")
def source_image() -> Response:
    """The exact NOAA frame the vision agent read.

    Served so a viewer can check the agent's reading against the source rather
    than taking the structured output on trust. Same principle as the citation
    verifier: the claim and the thing it was made from, side by side.
    """
    if not _HAB.exists():
        return _json({"error": "source image unavailable"}, 503)
    r = Response(_HAB.read_bytes(), media_type="image/png")
    r.headers.update(_HEADERS)
    r.headers["Cache-Control"] = "public, max-age=3600"
    return r


# /health, NOT /healthz.
#
# MEASURED ON THE DEPLOYED SERVICE 2026-08-29: the Google Front End intercepts
# /healthz on Cloud Run and returns its OWN 404 page. The request never reaches
# the container. Proved by comparing bodies from the live URL:
#
#   /healthz      404, body is Google's "That's an error" HTML  -> GFE
#   /nope         404, body is {"error":"not available"}        -> our app
#   /health       404, body is {"error":"not available"}        -> our app
#   /api/healthz  404, body is {"error":"not available"}        -> our app
#
# So the path itself is reserved upstream, and any liveness check pointed at
# /healthz would report the service down while it is perfectly healthy. This
# also explains the identical symptom on the previous project, which was
# wrongly attributed there to a stale revision.
@app.get("/api/sites")
def sites() -> JSONResponse:
    """The imagery agent's reading, positioned on the frame it read.

    Positions are approximate by design and the payload says so; the page
    prints the same caveat next to the markers. The categories are the same
    verified reading the schematic renderer uses, and a test pins the two
    tables together.
    """
    return _json({
        "sites": SITES_ON_IMAGE,
        "positioning": POSITIONING_NOTE,
        "image": "api/source-image",
    }, 200)


@app.get("/health")
def health() -> dict:
    return {"ok": True}

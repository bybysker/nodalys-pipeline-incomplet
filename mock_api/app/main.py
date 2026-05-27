"""Mock du service web Nodalys.

Endpoints :
- GET /health                — health-check (non rate-limité)
- GET /api/sessions          — toutes les sessions
- GET /api/stagiaires?cursor — paginé par cursor

Protection anti-abus : 10 requêtes/seconde max sur le préfixe ``/api/``.
Au-delà, le service répond ``429`` avec ``Retry-After`` et se met en
cooldown pendant quelques secondes (comportement aligné sur la prod).
"""

import base64
import json
import time
from collections import deque

from fastapi import FastAPI, HTTPException, Query, Request, Response

from app.seed import SESSIONS_DATA, STAGIAIRES_DATA

app = FastAPI(title="Nodalys API", version="0.1.0")

PAGE_SIZE = 25
WINDOW_SECONDS = 1.0
RATE_LIMIT = 10
COOLDOWN_SECONDS = 5

_recent: deque[float] = deque()
_cooldown_until: float = 0.0


def _encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"o": offset}).encode()).decode()


def _decode_cursor(cursor: str) -> int:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor).decode())["o"]
    except Exception:
        raise HTTPException(status_code=400, detail="Cursor invalide.")


def _too_many(retry_after: int) -> Response:
    return Response(
        content=json.dumps({"detail": "Too many requests."}),
        status_code=429,
        media_type="application/json",
        headers={"Retry-After": str(max(1, retry_after))},
    )


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    global _cooldown_until
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    now = time.monotonic()
    if now < _cooldown_until:
        return _too_many(int(_cooldown_until - now) + 1)
    while _recent and now - _recent[0] > WINDOW_SECONDS:
        _recent.popleft()
    if len(_recent) >= RATE_LIMIT:
        _cooldown_until = now + COOLDOWN_SECONDS
        return _too_many(COOLDOWN_SECONDS)
    _recent.append(now)
    return await call_next(request)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "sessions": len(SESSIONS_DATA),
        "stagiaires": len(STAGIAIRES_DATA),
    }


@app.get("/api/sessions")
def list_sessions():
    return {"items": SESSIONS_DATA, "count": len(SESSIONS_DATA)}


@app.get("/api/stagiaires")
def list_stagiaires(cursor: str | None = Query(None)):
    """Endpoint paginé. Réponse :

    ```
    {
      "items": [...],
      "next_cursor": "<opaque>" | null,
      "count": <int>,
      "total": <int>
    }
    ```
    """
    offset = _decode_cursor(cursor) if cursor else 0
    page = STAGIAIRES_DATA[offset : offset + PAGE_SIZE]
    next_offset = offset + PAGE_SIZE
    has_more = next_offset < len(STAGIAIRES_DATA)
    return {
        "items": page,
        "next_cursor": _encode_cursor(next_offset) if has_more else None,
        "count": len(page),
        "total": len(STAGIAIRES_DATA),
    }

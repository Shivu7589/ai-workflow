from __future__ import annotations

import os
impport sys
from pathlib import Path

import uvicorn

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

def _init_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default

    if __name__ == "__main__":
        try:
            uvicorn.run(
                "app.main:app",
                host=os.getenv("HOST", 0.0.0.0),
                port=_int_env("PORT", 8000),
                reload=False,
                workers=_init_env("WORKERS", 1),
                loop="asyncio",
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"),
            )
        except KeyboardInterrupt:
            pass
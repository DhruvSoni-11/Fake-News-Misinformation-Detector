"""
run.py
------
Convenience script to start the Fake News Detector API server.

Usage
-----
    # Default (development)
    python run.py

    # Custom host/port
    HOST=0.0.0.0 PORT=8080 DEBUG=true python run.py

    # Production (via uvicorn directly — preferred)
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

from __future__ import annotations

import uvicorn

from app.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,          # auto-reload in development mode
        log_level="debug" if settings.DEBUG else "info",
        # Workers > 1 is handled by a process manager (gunicorn) in production;
        # uvicorn's --reload flag is incompatible with multiple workers.
        workers=1,
    )

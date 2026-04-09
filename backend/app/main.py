"""
app/main.py
-----------
FastAPI application factory and entry point.

Responsibilities
----------------
- Create and configure the FastAPI application instance.
- Register CORS middleware.
- Mount the API router.
- Configure structured logging for the whole application.
- Expose a lifespan context manager for startup / shutdown hooks.
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

import nltk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings


# ── Logging setup ─────────────────────────────────────────────────────────────

def configure_logging() -> None:
    """
    Set up a clean, consistent logging format for the entire application.
    Uses StreamHandler (stdout) so logs surface correctly in Docker / cloud envs.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Silence overly verbose third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("newspaper").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


configure_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Async context manager that wraps the application's lifespan.

    Startup:
      - Warm up NLTK resources (already downloaded by nlp_service at import
        time, but we log confirmation here).
      - Any future startup tasks (DB connection pools, ML model loading) go here.

    Shutdown:
      - Clean teardown (DB pool close, etc.) would go here.
    """
    logger.info("═══════════════════════════════════════")
    logger.info("  %s  v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("═══════════════════════════════════════")
    logger.info("Starting up…")

    # Trigger nlp_service import so NLTK data is downloaded before the first request
    try:
        from app.services import nlp_service  # noqa: F401
        logger.info("NLP service initialised successfully.")
    except Exception as exc:
        logger.error("Failed to initialise NLP service: %s", exc)

    logger.info("Server ready on http://%s:%d", settings.HOST, settings.PORT)
    logger.info("API docs available at http://%s:%d/docs", settings.HOST, settings.PORT)

    yield  # ← application runs here

    logger.info("Shutting down %s…", settings.APP_NAME)


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Construct and return the configured FastAPI application.
    Keeping this in a factory function makes the app easy to test in isolation.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A production-ready API that analyses news articles for signs of "
            "misinformation and returns a credibility score with an explanatory label."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(router, prefix="/api/v1")

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:  # type: ignore[type-arg]
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal error occurred."},
        )

    return app


# Singleton exported to uvicorn
app = create_app()

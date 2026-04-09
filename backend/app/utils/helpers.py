"""
app/utils/helpers.py
--------------------
Generic utility functions shared across the application.
Nothing domain-specific lives here — this is the catch-all for truly
reusable helpers.
"""

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable


logger = logging.getLogger(__name__)


# ── Timing ────────────────────────────────────────────────────────────────────

def timer(func: Callable) -> Callable:
    """
    Decorator that logs how long a (sync) function takes to execute.
    Useful during development and for performance profiling.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug("'%s' executed in %.4f seconds.", func.__name__, elapsed)
        return result
    return wrapper


# ── Text Utilities ────────────────────────────────────────────────────────────

def truncate(text: str, max_chars: int = 200, suffix: str = "…") -> str:
    """
    Truncate *text* to at most *max_chars* characters, appending *suffix*
    if truncation occurred.  Safe for display in logs or error messages.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + suffix


def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """Return numerator / denominator, or *fallback* if denominator is zero."""
    if denominator == 0:
        return fallback
    return numerator / denominator


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp *value* to the inclusive range [*lo*, *hi*]."""
    return max(lo, min(hi, value))


# ── Validation ────────────────────────────────────────────────────────────────

def is_valid_url(url: str) -> bool:
    """
    Lightweight URL validation — checks for scheme + netloc without importing
    a heavy validator library.  For strict validation Pydantic's HttpUrl is used
    in the schema layer.
    """
    import re
    pattern = re.compile(
        r"^(https?://)"           # scheme
        r"([a-zA-Z0-9\-\.]+)"    # domain
        r"(\.[a-zA-Z]{2,})"      # TLD
        r"(:\d+)?"                # optional port
        r"(/.*)?$"                # optional path
    )
    return bool(pattern.match(url.strip()))

"""B2B in-memory cache with TTL. Thread-safe for asyncio (single-threaded event loop)."""

import time
from typing import Any


_cache: dict[str, tuple[float, Any]] = {}


def get(key: str, ttl: float = 60.0) -> Any | None:
    """Return cached value if not expired, else None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.monotonic() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def put(key: str, value: Any, ttl: float = 60.0) -> None:
    """Store value with TTL seconds."""
    _cache[key] = (time.monotonic() + ttl, value)


def invalidate(key: str) -> None:
    """Remove a single cache entry."""
    _cache.pop(key, None)


def invalidate_prefix(prefix: str) -> None:
    """Remove all entries whose key starts with prefix."""
    keys = [k for k in _cache if k.startswith(prefix)]
    for k in keys:
        _cache.pop(k, None)

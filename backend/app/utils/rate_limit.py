import asyncio
import time
from typing import Dict, List

from fastapi import HTTPException, Request
from ..config import get_settings


class RateLimiter:
    def __init__(self, rate: int, per_seconds: int):
        self.rate = rate
        self.per = per_seconds
        self.hits: Dict[str, List[float]] = {}
        self.lock = asyncio.Lock()

    async def check(self, key: str):
        now = time.time()
        async with self.lock:
            window = [t for t in self.hits.get(key, []) if now - t < self.per]
            if len(window) >= self.rate:
                raise HTTPException(status_code=429, detail="Too many requests")
            window.append(now)
            self.hits[key] = window

settings = get_settings()
rate_limiter = RateLimiter(rate=settings.rate_limit_per_min, per_seconds=60)
_cached_rate: int | None = settings.rate_limit_per_min

async def rate_limit_dep(request: Request):
    # Sync limiter configuration with current settings and reset window if changed.
    current_rate = get_settings().rate_limit_per_min
    global _cached_rate
    if _cached_rate != current_rate:
        _cached_rate = current_rate
        rate_limiter.rate = current_rate
        rate_limiter.hits.clear()

    ident = request.client.host if request.client else "global"
    await rate_limiter.check(ident)

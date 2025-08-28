import time, asyncio
from typing import Dict, List
from fastapi import HTTPException, Request

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

rate_limiter = RateLimiter(rate=20, per_seconds=60)

async def rate_limit_dep(request: Request):
    ident = request.client.host if request.client else "global"
    await rate_limiter.check(ident)

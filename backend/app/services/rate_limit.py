import redis
from fastapi import HTTPException
from app.core.config import settings

r = redis.from_url(settings.redis_url)

# Counts requests in the CURRENT window and rejects once the count passes max_requests
def check_rate_limit(user_id: int, action: str, max_requests: int, window_seconds: int) -> None:
    key = f"ratelimit:{action}:{user_id}"
    current = r.incr(key)

    if current == 1:
        r.expire(key, window_seconds)
    
    if current > max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {max_requests} requests per {window_seconds} seconds",
        )

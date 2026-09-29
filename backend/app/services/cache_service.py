import redis
import json
from app.core import settings

r = redis.from_url(settings.redis_url)

def get_cached_report(video_id: str) -> dict | None:
    cached = r.get(f"report:{video_id}")
    return json.loads(cached) if cached else None


def cache_report(video_id: str, report:dict) -> None:
    r.set(f"report:{video_id}", json.dumps(report), ex=86400)
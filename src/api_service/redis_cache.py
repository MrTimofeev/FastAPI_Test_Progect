from redis import asyncio as aioredis
from datetime import datetime, timedelta

REDIS_URL = "redis://redis"

def get_redis_ttl():
    now = datetime.now()
    target_time = now.replace(hour=14, minute=11, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    return int((target_time - now).total_seconds())

async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)
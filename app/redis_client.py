import redis.asyncio as redis

# Adres z Twojego Docker Compose
REDIS_URL = "redis://localhost:6379"

# Tworzymy asynchronicznego klienta Redisa
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    return redis_client

import os
import redis

# Nếu Docker Compose đã cung cấp REDIS_URL, ví dụ "redis://redis:6379/0"
redis_url = os.getenv("REDIS_URL")
if redis_url:
    # from_url tự parse host, port và db (ở đây db=0)
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
else:
    # Fallback: đọc riêng host và port
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=True
    )

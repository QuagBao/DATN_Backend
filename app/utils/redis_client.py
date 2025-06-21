import redis

redis_client = redis.Redis(
    host='redis-10576.c337.australia-southeast1-1.gce.redns.redis-cloud.com',
    port=10576,
    username='default',
    password='dVAZRl6Ae33jhQP6UHAtE7X8DDDsEYFm',
    db=0,
    decode_responses=True
)

# Test kết nối
try:
    pong = redis_client.ping()
    print("Redis Connected:", pong)
except redis.exceptions.RedisError as e:
    print("Redis Connection Error:", e)

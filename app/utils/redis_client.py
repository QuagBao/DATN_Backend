import redis

redis_client = redis.Redis(
    host='redis-11457.c15.us-east-1-4.ec2.redns.redis-cloud.com',
    port=11457,
    username='default',
    password='9FuROefquF9YGIDpmyWQY3gdPqK1vGeY',
    db=0,
    decode_responses=True
)

# Test kết nối
try:
    pong = redis_client.ping()
    print("Redis Connected:", pong)
except redis.exceptions.RedisError as e:
    print("Redis Connection Error:", e)



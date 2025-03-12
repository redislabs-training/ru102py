# Uncomment for Challenge #7
import datetime
import random
from redis.client import Redis
import time
from redisolar.dao.base import RateLimiterDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.dao.redis.key_schema import KeySchema

# Uncomment for Challenge #7
from redisolar.dao.base import RateLimitExceededException


class SlidingWindowRateLimiter(RateLimiterDaoBase, RedisDaoBase):
    """A sliding-window rate-limiter."""
    def __init__(self,
                 window_size_ms: float,
                 max_hits: int,
                 redis_client: Redis,
                 key_schema: KeySchema = None,
                 **kwargs):
        self.window_size_ms = window_size_ms
        self.max_hits = max_hits
        super().__init__(redis_client, key_schema, **kwargs)

    def hit(self, name: str):
        """Record a hit using the rate-limiter."""
        # Get the current timestamp in milliseconds.
        now = int(time.time() * 1000)
        
        # Generate the key for the sliding window rate limiter.
        # Key format: limiter:[name]:[window_size_ms]:[max_hits]
        key = self.key_schema.fixed_rate_limiter_key(name, int(self.window_size_ms), self.max_hits)
        
        # Start a pipeline to perform the following operations atomically.
        pipe = self.redis.pipeline()
        
        # Create a unique member for this hit.
        # Instead of using uuid, we use a random integer to ensure uniqueness.
        member = f"{now}-{random.randint(0, 1000000)}"
        
        # 1. Add the current hit to the sorted set with the timestamp as its score.
        pipe.zadd(key, {member: now})
        
        # 2. Remove all entries older than the current sliding window.
        cutoff = now - self.window_size_ms
        pipe.zremrangebyscore(key, 0, cutoff)
        
        # 3. Get the current count of entries in the sorted set.
        pipe.zcard(key)
        
        # Execute the pipeline.
        results = pipe.execute()
        
        # The third result is the count from ZCARD.
        count = results[2]
        if count > self.max_hits:
            raise RateLimitExceededException(f"Rate limit exceeded: {count} hits in {self.window_size_ms}ms")
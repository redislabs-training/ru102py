
def test_without_transaction(redis):
    redis.hset("candies:tootsie-rolls", mapping={"flavor": "delicious"})
    # Expire in 1 hour...
    redis.expire("candies:tootsie-rolls", 3600)
    redis.sadd("candies", "tootsie-rolls")


def test_with_transaction(redis):
    pipeline = redis.pipeline()
    pipeline.hset("candies:tootsie-rolls", mapping={"flavor": "delicious"})
    # Expire in 1 hour...
    pipeline.expire("candies:tootsie-rolls", 3600)
    pipeline.sadd("candies", "tootsie-rolls")
    pipeline.execute()

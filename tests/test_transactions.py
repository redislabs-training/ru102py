
def test_without_transaction(redis):
    redis.hset("candies:tootsie-rolls", mapping={"flavor": "delicious"})
    redis.sadd("candies", "tootsie-rolls")


def test_with_transaction(redis):
    pipeline = redis.pipeline()
    pipeline.hset("candies:tootsie-rolls", mapping={"flavor": "delicious"})
    pipeline.sadd("candies", "tootsie-rolls")
    pipeline.execute()

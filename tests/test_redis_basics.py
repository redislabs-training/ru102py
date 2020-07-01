PLANETS = [
    "Mercury", "Mercury", "Venus", "Earth", "Earth", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto"
]
EARTH_KEY = "earth"


def test_hello(redis, key_schema):
    key = key_schema.hello_key()
    result = redis.set(key, "world")
    value = redis.get(key)

    assert result is True
    assert value == "world"


def test_redis_list(redis, key_schema):
    key = key_schema.planets_list_key()

    assert len(PLANETS) == 11

    # Add all test planets to a Redis list
    result = redis.rpush(key, *PLANETS)

    # Check that the length of the list in Redis is the same
    assert result == len(PLANETS)

    # Get the planets from the list
    # Note: LRANGE is an O(n) command. Be careful running this command
    # with high-cardinality sets.
    planets = redis.lrange(key, 0, -1)
    assert planets == PLANETS

    # Remove the elements that we know are duplicates
    # Note: O(n) operation.
    redis.lrem(key, 1, "Mercury")
    redis.lrem(key, 1, "Earth")

    planet = redis.rpop(key)
    assert planet == "Pluto"

    assert redis.llen(key) == 8


def test_redis_set(redis, key_schema):
    key = key_schema.planets_set_key()

    # Add planets to a Redis set
    redis.sadd(key, *PLANETS)

    # Return the cardinality of the set
    assert redis.scard(key) == 9

    # Fetch all values from the set
    # Note: SMEMBERS is an O(n) command. Be careful running this command
    # with high-cardinality sets. Consider SSCAN as an alternative.
    assert redis.smembers(key) == set(PLANETS)

    # Pluto is, of course, no longer a first-class planet. Remove it.
    response = redis.srem(key, "Pluto")
    assert response == 1

    # Now we have 8 planets, as expected.
    assert redis.scard(key) == 8


def test_redis_hash(redis):
    earth_properties = {
        "diameter_km": "12756",
        "day_length_hrs": "24",
        "mean_temp_c": "15",
        "moon_count": "1"
    }

    # Set the fields of the hash.
    redis.hset(EARTH_KEY, mapping=earth_properties)

    # Get the hash we just created back from Redis.
    stored_properties = redis.hgetall(EARTH_KEY)
    assert stored_properties == earth_properties

    # Test that we can get a single property.
    assert redis.hget(EARTH_KEY, "diameter_km") == earth_properties["diameter_km"]

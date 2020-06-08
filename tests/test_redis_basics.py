PLANETS = [
    "Mercury", "Mercury", "Venus", "Earth", "Earth", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto"
]
PLANETS_LIST_KEY = "ru102py-test:planets:list"
PLANETS_SET_KEY = "ru102py-test:planets:set"
EARTH_KEY = "earth"


def test_hello(redis):
    result = redis.set("hello", "world")
    value = redis.get("hello")

    assert result is True
    assert value == "world"


def test_redis_list(redis):
    assert len(PLANETS) == 11
    
    # Add all test planets to a Redis list
    result = redis.rpush(PLANETS_LIST_KEY, *PLANETS)

    # Check that the length of the list in Redis is the same
    assert result == len(PLANETS)

    # Get the planets from the list
    # Note: LRANGE is an O(n) command. Be careful running this command
    # with high-cardinality sets.
    planets = redis.lrange(PLANETS_LIST_KEY, 0, -1)
    assert planets == PLANETS

    # Remove the elements that we know are duplicates
    # Note: O(n) operation.
    redis.lrem(PLANETS_LIST_KEY, 1, "Mercury")
    redis.lrem(PLANETS_LIST_KEY, 1, "Earth")

    planet = redis.rpop(PLANETS_LIST_KEY)
    assert planet == "Pluto"

    assert redis.llen(PLANETS_LIST_KEY) == 8


def test_redis_set(redis):
    # Add planets to a Redis set
    redis.sadd(PLANETS_SET_KEY, *PLANETS)

    # Return the cardinality of the set
    assert redis.scard(PLANETS_SET_KEY) == 9

    # Fetch all values from the set
    # Note: SMEMBERS is an O(n) command. Be careful running this command
    # with high-cardinality sets. Consider SSCAN as an alternative.
    assert redis.smembers(PLANETS_SET_KEY) == set(PLANETS)

    # Pluto is, of course, no longer a first-class planet. Remove it.
    response = redis.srem(PLANETS_SET_KEY, "Pluto")
    assert response == 1

    # Now we have 8 planets, as expected.
    assert redis.scard(PLANETS_SET_KEY) == 8


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


def test_hello(redis):
    result = redis.set("hello", "world")
    value = redis.get("hello")

    assert result is True
    assert value == "world"

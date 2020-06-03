import pytest

from redisolar.scripts.update_if_lowest import UpdateIfLowestScript


def test_update_if_lowest(redis):
    redis.set("test-lua", "100")

    script = UpdateIfLowestScript(redis)
    result = script.update_if_lowest("test-lua", "50")

    assert result is True
    assert redis.get("test-lua") == "50"

def test_update_if_lowest_unchanged(redis):
    redis.set("test-lua", "100")

    script = UpdateIfLowestScript(redis)
    result = script.update_if_lowest("test-lua", "200")

    assert result is False
    assert redis.get("test-lua") == "100"

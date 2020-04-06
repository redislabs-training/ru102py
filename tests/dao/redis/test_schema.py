from redisolar.dao.redis.key_schema import KeySchema


def test_configurable_prefix(app):
    key_schema = KeySchema('prefix-test')
    assert key_schema.site_hash_key(1) == "prefix-test:sites:info:1"


def test_site_hash_key(app, key_schema):
    assert key_schema.site_hash_key(1) == "test:sites:info:1"


def test_site_ids_key(app, key_schema):
    assert key_schema.site_ids_key() == "test:sites:ids"

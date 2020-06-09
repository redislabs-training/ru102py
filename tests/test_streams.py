NUMBER_OF_SOLAR_SITES = 300
MEASUREMENTS_PER_HOUR = 60
HOURS_PER_DAY = 24
MAX_DAYS = 14
STREAM_KEY = "ru102py-test:stream"


def test_stream(redis):
    max_stream_entries = NUMBER_OF_SOLAR_SITES * MEASUREMENTS_PER_HOUR * HOURS_PER_DAY * MAX_DAYS
    entry = {
        "site_id": "1",
        "temp_c": "18.0"
    }

    redis.xadd(STREAM_KEY, entry, max_stream_entries)
    results = redis.xrevrange(STREAM_KEY, count=1)

    assert len(results) == 1
    _, result = results[0]
    assert result == entry


def test_stream_with_pipeline(redis):
    p = redis.pipeline(transaction=False)
    entry1 = {
        "site_id": "1",
    }
    entry2 = {
        "site_id": "2",
    }
    p.xadd(STREAM_KEY, entry1)
    p.xadd(STREAM_KEY, entry2)
    p.xrange(STREAM_KEY, count=2)

    results = p.execute()
    ids = results[0:2]
    entries = results[2]

    assert len(entries) == 2
    assert ids == [e[0] for e in entries]


def test_stream_with_transaction(redis):
    t = redis.pipeline()
    entry1 = {
        "site_id": "1",
    }
    entry2 = {
        "site_id": "2",
    }
    t.xadd(STREAM_KEY, entry1)
    t.xadd(STREAM_KEY, entry2)
    t.xrange(STREAM_KEY, count=2)

    results = t.execute()
    entries = results[2]

    assert len(entries) == 2

import pytest
from redis import client as redis_client

from redisolar import create_app
from redisolar.core.connections import get_redis_connection
from redisolar.dao.redis.key_schema import KeySchema

TEST_CONFIG = 'testing.cfg'
CI_CONFIG = 'ci.cfg'


def pytest_addoption(parser):
    parser.addoption(
        "--ci",
        action="store_true",
        help="use the CI configuration",
    )


def make_app(request, config):
    """Yield a Flask app from the config file specified in `config`."""
    if request.config.getoption('ci'):
        config = CI_CONFIG

    app = create_app(config)

    with app.app_context():
        yield app


@pytest.fixture
def app(request):
    yield from make_app(request, TEST_CONFIG)


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def redis(app):
    yield get_redis_connection(app.config['REDIS_HOST'], app.config['REDIS_PORT'])


@pytest.fixture
def key_schema(app):
    yield KeySchema(app.config['REDIS_KEY_PREFIX'])


def _delete_test_keys(prefix: str, conn: redis_client.Redis):
    for key in conn.scan_iter(f"{prefix}:*"):
        conn.delete(key)


@pytest.fixture(scope="function", autouse=True)
def delete_test_keys(request):
    def cleanup():
        app = next(make_app(request, TEST_CONFIG))
        conn = get_redis_connection(app.config['REDIS_HOST'], app.config['REDIS_PORT'])
        _delete_test_keys(app.config['REDIS_KEY_PREFIX'], conn)

    request.addfinalizer(cleanup)

import redis
from redis.sentinel import Sentinel
from rediscluster import RedisCluster


def connection_examples():
    # Connect to a standard Redis deployment.
    client = redis.Redis("localhost", port=6379, decode_responses=True,
                         max_connections=20)

    # Read and write through the client.
    client.set("foo", "bar")
    client.get("foo")


    # Connect to a Redis Sentinel deployment.
    sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    master = sentinel.master_for("cache", socket_timeout=0.1)
    slave = sentinel.slave_for("cache", socket_timeout=0.1)

    # Run write operations with the master.
    master.set("foo", "bar")

    # Run read operations with the slave.
    slave.get("foo")

    # Connect to a Redis Cluster deployment.
    #
    # NOTE: This requires a separate library built on top of redis-py, called
    # redis-py-cluster. At the time we built this course, redis-py-cluster
    # depended on too old a version of redis-py for us to include it as a
    # dependency in this project, so we've commented out the example.
    #
    # from rediscluster import RedisCluster
    # startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]
    # cluster = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

    # Read and write through the cluster client.
    # cluster.set("foo", "bar")
    # cluster.get("foo")

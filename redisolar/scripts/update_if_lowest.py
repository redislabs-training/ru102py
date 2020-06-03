import os

from redis import Redis

PARENT_DIR = os.path.abspath(os.path.dirname(__file__))
SCRIPT_PATH = os.path.join(PARENT_DIR, 'update_if_lowest.lua')


class UpdateIfLowestScript:
    def __init__(self, redis: Redis):
        with open(SCRIPT_PATH) as f:
            script = f.read()
        self.script = redis.register_script(script)
        self.redis = redis

    def update_if_lowest(self, key: str, value: int) -> bool:
        response = self.script(keys=[key], args=[str(value)], client=self.redis)
        return int(response) == 1

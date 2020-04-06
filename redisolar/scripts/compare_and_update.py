import os
from enum import Enum

from redis import Redis
from redis.client import Pipeline

PARENT_DIR = os.path.abspath(os.path.dirname(__file__))
SCRIPT_PATH = os.path.join(PARENT_DIR, 'compare_and_update.lua')


class ScriptOperation(Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"


class CompareAndUpdateScript:
    def __init__(self, redis: Redis):
        with open(SCRIPT_PATH) as f:
            script = f.read()
        self.script = redis.register_script(script)
        self.redis = redis

    def update_if_greater(self, pipeline: Pipeline, key: str, field: str,
                          value: float) -> None:
        self.update(pipeline, key, field, value, ScriptOperation.GREATER_THAN)

    def update_if_less(self, pipeline: Pipeline, key: str, field: str,
                       value: float) -> None:
        self.update(pipeline, key, field, value, ScriptOperation.LESS_THAN)

    def update(self, pipeline: Pipeline, key: str, field: str, value: float,
               op: ScriptOperation) -> None:
        self.script(keys=[key], args=[field, str(value), op.value],
                    client=pipeline)

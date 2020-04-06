from typing import Any

from flask_restful import Resource


class DaoResource(Resource):
    def __init__(self, dao: Any, *args, **kwargs):
        self.dao = dao
        super().__init__(*args, **kwargs)

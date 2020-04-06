import os

from flask import Flask
from flask_cors import CORS

from redisolar import api

DEV_CONFIG = 'dev.cfg'


def create_app(config_path=DEV_CONFIG):
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join('instance', config_path))

    app.register_blueprint(api.blueprint)
    api.configure(app)

    CORS(app)

    @app.route('/')
    def root():  # pylint: disable=unused-variable
        """Load a page that initializes the Vue.js frontend."""
        return app.send_static_file('index.html')

    return app

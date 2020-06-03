import os

from flask import Flask
from flask_cors import CORS

from redisolar import api
from redisolar import command

DEV_CONFIG = 'dev.cfg'


def create_app(config_file=DEV_CONFIG):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_file)

    app.register_blueprint(api.blueprint)
    api.configure(app)

    app.register_blueprint(command.blueprint)

    CORS(app)

    @app.route('/')
    def root():  # pylint: disable=unused-variable
        """Load a page that initializes the Vue.js frontend."""
        return app.send_static_file('index.html')

    return app

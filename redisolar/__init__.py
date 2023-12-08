import os

from flask import Flask
from flask_cors import CORS

from redisolar import api
from redisolar import command

DEV_CONFIG = 'dev.cfg'


def create_app(config_file=DEV_CONFIG):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_file)

    # Override configuration with environment variables if they exist
    redis_host = os.environ.get('REDIS_HOST')
    if redis_host:
        app.config['REDIS_HOST'] = redis_host

    redis_port = os.environ.get('REDIS_PORT')
    if redis_port:
        app.config['REDIS_PORT'] = redis_port

    app.register_blueprint(api.blueprint)
    api.configure(app)

    app.register_blueprint(command.blueprint)

    CORS(app)

    @app.route('/')
    def root():  # pylint: disable=unused-variable
        """Load a page that initializes the Vue.js frontend."""
        return app.send_static_file('index.html')

    return app

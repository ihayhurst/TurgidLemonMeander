from flask import Flask
from .website.views import website

# from extensidbons import *
# Set Globals


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Production')
    app.config.from_pyfile('flask.cfg', silent=True)

    with app.app_context():
        app.register_blueprint(website, url_prefix="/")
        # Initialise Globals
    return app

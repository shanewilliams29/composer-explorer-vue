from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from flask_caching import Cache
from flask_login import LoginManager
from flask_moment import Moment
from app.classes import SpotifyAPI

db = SQLAlchemy()
login = LoginManager()
mobility = Mobility()
cache = Cache()
moment = Moment()
sp = SpotifyAPI(Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URL)


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../dist', static_url_path='/', template_folder='templates')
    app.config.from_object(config_class)

    # enable CORS in development mode
    if Config.MODE == "DEVELOPMENT":
        CORS(app, automatic_options=True, support_credentials=True)

    db.init_app(app)
    login.init_app(app)
    mobility.init_app(app)
    cache.init_app(app)
    moment.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from app.forum import bp as forum_bp
    app.register_blueprint(forum_bp)

    return app


from app import models

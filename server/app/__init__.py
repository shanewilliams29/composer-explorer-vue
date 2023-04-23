from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from flask_caching import Cache
from flask_login import LoginManager
from flask_moment import Moment
from app.spotify import SpotifyAPI
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from google.cloud import logging, storage


db = SQLAlchemy()
login = LoginManager()
mobility = Mobility()
cache = Cache()
moment = Moment()
bootstrap = Bootstrap4()
migrate = Migrate()
log = logging.Client()
storage_client = storage.Client(project='composer-explorer')
sp = SpotifyAPI(Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URL)


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../dist', static_url_path='/', template_folder='templates')
    app.config.from_object(config_class)

    app.jinja_env.add_extension('jinja2.ext.do')

    # enable CORS in development mode
    if Config.MODE == "DEVELOPMENT":
        CORS(app, automatic_options=True, support_credentials=True)

    db.init_app(app)
    login.init_app(app)
    mobility.init_app(app)
    cache.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from app.forum import bp as forum_bp
    app.register_blueprint(forum_bp)

    from app.cron import bp as cron_bp
    app.register_blueprint(cron_bp)

    from app.cron_old import bp as cron_old_bp
    app.register_blueprint(cron_old_bp)

    return app


from app import models

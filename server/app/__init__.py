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
from elasticsearch import Elasticsearch
import boto3


db = SQLAlchemy()
login = LoginManager()
mobility = Mobility()
cache = Cache()
moment = Moment()
bootstrap = Bootstrap4()
migrate = Migrate()
# log = logging.Client(project='composer-explorer')

sp = SpotifyAPI(Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URL)
# twilio = Client(Config.TWILIO_SID, Config.TWILIO_AUTH_TOKEN)


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../dist', static_url_path='/', template_folder='templates')
    app.config.from_object(config_class)

    # elasticsearchg
    app.elasticsearch = Elasticsearch(
        app.config["ELASTICSEARCH_URL"],
        ca_certs=app.config["ELASTICSEARCH_CA"],   # not ELASTICSEARCH_CERTS
        basic_auth=(app.config["ELASTICSEARCH_USER"],
                    app.config["ELASTICSEARCH_PASS"]),
        verify_certs=True,
    )

    # bucket storage
    app.s3_client = boto3.client(
        's3',
        endpoint_url=app.config['CONTABO_ENDPOINT'],
        aws_access_key_id=app.config['CONTABO_ACCESS_KEY'],
        aws_secret_access_key=app.config['CONTABO_SECRET_KEY']
    )
    app.bucket_name = app.config['CONTABO_BUCKET']

    # misc
    app.jinja_env.add_extension('jinja2.ext.do')
    app.json.sort_keys = False

    # enable CORS in development mode
    if Config.MODE == "DEVELOPMENT":
        CORS(app, automatic_options=True, support_credentials=True)

    if Config.MODE == "PRODUCTION":
        CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:8000"}})

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

    return app


from app import models

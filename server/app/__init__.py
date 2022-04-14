from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility


# instantiate the app
app = Flask(__name__, static_folder='../dist', static_url_path='/', template_folder='../dist')
app.config.from_object(Config)
db = SQLAlchemy(app)
Mobility(app)

from app.classes import SpotifyAPI
sp = SpotifyAPI(Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET, Config.SPOTIFY_REDIRECT_URL)

# enable CORS in development mode
if Config.MODE == "DEVELOPMENT":
    CORS(app, automatic_options=True, support_credentials=True)

from app import routes, models, classes

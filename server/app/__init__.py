from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# instantiate the app
app = Flask(__name__, static_folder='../dist', static_url_path='/')
app.config.from_object(Config)
db = SQLAlchemy(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

from app import routes, models

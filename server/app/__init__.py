from flask import Flask
from flask_cors import CORS

# instantiate the app
app = Flask(__name__, static_folder='../dist', static_url_path='/')

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

from app import routes

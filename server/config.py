import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MODE = os.environ.get('MODE')

    JSON_SORT_KEYS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URL = os.environ.get('SPOTIFY_REDIRECT_URL')

    STATIC = 'https://storage.googleapis.com/composer-explorer.appspot.com/'

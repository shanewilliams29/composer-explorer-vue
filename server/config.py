from dotenv import load_dotenv

load_dotenv()

import os


class Config(object):
    MAX_CONTENT_LENGTH = 1024 * 1024 * 5
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MODE = os.environ.get('MODE')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URL = os.environ.get('SPOTIFY_REDIRECT_URL')

    GOOGLE_KNOWLEDGE_GRAPH_API_KEY = os.environ.get('GOOGLE_KNOWLEDGE_GRAPH_API_KEY')

    STATIC = 'https://usc1.contabostorage.com/a36ba68caf9842799883275ab3ad3a88:composer-explorer.bucket/static/'

    TWILIO_SID = os.environ.get('TWILIO_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    SOURCE_PHONE = os.environ.get('SOURCE_PHONE')
    TARGET_PHONE = os.environ.get('TARGET_PHONE')

    CACHE_TYPE = 'FileSystemCache'  # Flask-Caching related configs
    CACHE_THRESHOLD = 10000
    CACHE_DEFAULT_TIMEOUT = 86400
    CACHE_DIR = '/tmp/flaskcache'

    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER")
    ELASTICSEARCH_PASS = os.environ.get("ELASTICSEARCH_PASS")
    ELASTICSEARCH_CA = os.environ.get("ELASTICSEARCH_CA")

    CONTABO_ENDPOINT = os.environ.get("CONTABO_ENDPOINT")
    CONTABO_ACCESS_KEY = os.environ.get("CONTABO_ACCESS_KEY")
    CONTABO_SECRET_KEY = os.environ.get("CONTABO_SECRET_KEY")
    CONTABO_BUCKET = os.environ.get("CONTABO_BUCKET")
    CONTABO_PUBLIC_BASE = os.environ.get("CONTABO_PUBLIC_BASE")
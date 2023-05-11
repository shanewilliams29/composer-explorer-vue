import os


class Config(object):
    MAX_CONTENT_LENGTH = 1024 * 1024 * 5
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MODE = os.environ.get('MODE')

    JSON_SORT_KEYS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URL = os.environ.get('SPOTIFY_REDIRECT_URL')

    GOOGLE_KNOWLEDGE_GRAPH_API_KEY = os.environ.get('GOOGLE_KNOWLEDGE_GRAPH_API_KEY')

    STATIC = 'https://storage.googleapis.com/composer-explorer.appspot.com/'

    TWILIO_SID = os.environ.get('TWILIO_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

    if MODE == 'DEVELOPMENT':
        CACHE_TYPE = 'FileSystemCache'  # Flask-Caching related configs
        CACHE_THRESHOLD = 10000
        CACHE_DEFAULT_TIMEOUT = 86400
        CACHE_DIR = '/tmp/flaskcache'
    else:
        CACHE_TYPE = 'MemcachedCache'  # Flask-Caching related configs
        CACHE_DEFAULT_TIMEOUT = 86400
        CACHE_KEY_PREFIX = 'composer_explorer_cache'
        CACHE_MEMCACHED_SERVERS = '10.21.0.3:11211'
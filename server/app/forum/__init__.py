from flask import Blueprint

bp = Blueprint('forum', __name__)

from app.forum import routes

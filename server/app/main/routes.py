from app import db, sp
from flask import request, redirect, session, render_template, send_from_directory, current_app
from flask_login import current_user
from config import Config
from app.models import User
from datetime import datetime, timedelta, timezone
from app.main import bp
from app.functions import is_mobile


@bp.before_app_request
def before_app_request():
    
    # mobile view
    if not session.get('mobile'):
        session['mobile'] = None

    # get spotify token
    if not session.get('spotify_token'):
        session['spotify_token'] = None

    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = (datetime.now(timezone.utc) 
                                            + timedelta(minutes=50))


@bp.route('/', defaults={'path': ''})
@bp.route("/<string:path>")
def index(path):
    if is_mobile() and not session.get('mobile', False):
        session['mobile'] = 'true'
        if Config.MODE == "DEVELOPMENT":
            return redirect('http://localhost:8080/mobile')
        else:
            return redirect('https://composerexplorer.com/mobile')

    # user last seen
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    # return render_template("index.html")
    return current_app.send_static_file('index.html')


@bp.route('/user_list')
def user_list():

    users = User.query.order_by(User.last_seen.desc()).all()
    usercount = User.query.count()
    onlinecheck = datetime.utcnow() - timedelta(minutes=5)

    return render_template("userlist.html", title='User List', onlinecheck=onlinecheck, users=users, usercount=usercount)


# @bp.route("/privacy")
# def privacy():
#     return render_template('privacy.html')


# @bp.route("/.well-known/assetlinks.json")
# def assetlinks():
#     return send_from_directory('static', 'assetlinks.json')


# @bp.route("/custom.css")
# def custom_css():
#     return send_from_directory('static', 'custom.css')


# @bp.route("/forum.css")
# def forum_css():
#     return send_from_directory('static', 'forum.css')


# @bp.route("/favicon.ico")
# def favico():
#     return send_from_directory('static', 'favicon.ico')

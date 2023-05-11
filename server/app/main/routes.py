from app import db, sp, cache
from flask import request, redirect, session, render_template, send_from_directory, current_app
from flask_login import current_user
from config import Config
from app.models import User, Performers, performer_albums, ComposerList
from datetime import datetime, timedelta, timezone
from app.main import bp
from sqlalchemy import func, text, or_


@bp.before_app_request
def before_app_request():
    
    # redirect to https
    if "localhost" in request.url:  # removed :5000
        pass
    else:
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)

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

    # ensure artist list is in cache
    if not cache.get('artists'):

        artist_list = []

        artists = db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, func.count(Performers.id).label('total'))\
            .join(performer_albums)\
            .filter(or_(Performers.hidden == False, Performers.hidden == None))\
            .group_by(Performers.id).order_by(text('total DESC')).all()

        composers = db.session.query(ComposerList.name_full).all()
        composer_names = set(composer for (composer,) in composers)
        
        # remove composer exceptions who were also conductors and performance artists
        exceptions_list = ['Leonard Bernstein', 'Pierre Boulez', 'Steve Reich']
        for exception in exceptions_list:
            composer_names.remove(exception)

        # remove composers and bad results
        for _id, artist, img, description, count in artists:
            if artist not in composer_names and "/" not in artist:
                artist_list.append({'id': _id, 'name': artist, 'img': img, 'description': description})

        cache.set('artists', artist_list)


@bp.route('/', defaults={'path': ''})
@bp.route("/<string:path>")
def index(path):
    if request.MOBILE and not session['mobile']:
        session['mobile'] = 'true'
        if Config.MODE == "DEVELOPMENT":
            return redirect('http://localhost:8080/mobile')
        else:
            return redirect('https://www.composerexplorer.com/mobile')

    # user last seen
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    # return render_template("index.html")
    return current_app.send_static_file('index.html')


@bp.route("/privacy")
def privacy():
    return render_template('privacy.html')


@bp.route("/.well-known/assetlinks.json")
def assetlinks():
    return send_from_directory('static', 'assetlinks.json')


@bp.route("/custom.css")
def custom_css():
    return send_from_directory('static', 'custom.css')


@bp.route("/forum.css")
def forum_css():
    return send_from_directory('static', 'forum.css')


@bp.route('/user_list')
def user_list():

    users = User.query.order_by(User.last_seen.desc()).all()
    usercount = User.query.count()
    onlinecheck = datetime.utcnow() - timedelta(minutes=5)

    return render_template("userlist.html", title='User List', onlinecheck=onlinecheck, users=users, usercount=usercount)

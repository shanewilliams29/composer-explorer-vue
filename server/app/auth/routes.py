from app import db, sp, cache
from flask import jsonify, request, redirect, session, render_template, abort, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required
from config import Config
from app.functions import get_avatar, upload_avatar
from app.auth import bp
from app.models import User
from app.classes import ChangeAvatar
from datetime import datetime, timedelta, timezone
import random


@bp.route('/connect_spotify')
def connect_spotify():
    url = sp.authorize()
    return redirect(url)


@bp.route('/spotify')  # landing page from Spotify auth, app deep link
def spotify():
    code = request.args.get('code')

    if not code:
        return redirect(url_for('main.index'))

    url = '/login?code=' + code
    return redirect(url)


@bp.route('/login')  # log in the user
def login():

    # get access token
    code = request.args.get('code')
    response = sp.get_token(code)
    if response == "INVALID":
        response_object = {
            'status': 'error',
            'info': 'Spotify authorization failed.'
        }
        return jsonify(response_object)

    session['spotify_token'] = response.json()['access_token']
    session['refresh_token'] = response.json()['refresh_token']
    session['spotify_token_expire_time'] = (datetime.now((timezone.utc)) 
                                            + timedelta(minutes=0))  # always get new token when called

    response = sp.get_user()
    try:
        info = response.json()
    except Exception:
        abort(403)
    
    try:
        username = info['id']
    except Exception:
        abort(403)

    if info['product'] == "premium":
        session['premium'] = True
    else:
        session['premium'] = False

    user = User.query.filter_by(username=username).first()
    if user is None:
        display_name = info['display_name']
        try:
            image_url = info['images'][0]['url']
            response = get_avatar(username, image_url)
            image = response[0]
        except Exception:
            image = None

        duplicateuser = User.query.filter_by(display_name=display_name).first()
        if duplicateuser:
            display_name = display_name + str(random.randint(1, 9999))

        user = User(username=username, 
                    email=info['email'], 
                    display_name=display_name, 
                    img=image, 
                    country=info['country'],
                    product=info['product'])
        user.set_password(username)
        db.session.add(user)
        db.session.commit()
        login_user(user)
    login_user(user)

    if Config.MODE == "DEVELOPMENT":
        cache.set('token', session['spotify_token'])  # store in cache for dev
        
    if session['mobile']:
        if Config.MODE == "DEVELOPMENT":
            return redirect('http://localhost:8080/mobile')
        else:
            return redirect('https://www.composerexplorer.com/mobile')
    else:
        if Config.MODE == "DEVELOPMENT":
            return redirect("http://localhost:8080/")
        else:
            return redirect("/")


@bp.route('/log_out')
def log_out():
    session.clear()
    logout_user()
    if Config.MODE == "DEVELOPMENT":
        return redirect("http://localhost:8080/")
    if request.MOBILE:
        return redirect("/mobile")
    else:
        return redirect("/")


@bp.route('/api/get_token')
def get_token():

    if session['spotify_token'] or session['app_token']:

        # token expiry and refresh
        if session['app_token_expire_time'] < datetime.now((timezone.utc)):
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = ((datetime.now((timezone.utc)) 
                                                + timedelta(minutes=0)))  # always get new token when called
        if session['spotify_token']:
            if session['spotify_token_expire_time'] \
                    < datetime.now((timezone.utc)):
                session['spotify_token'] = sp.refresh_token()
                session['spotify_token_expire_time'] \
                    = datetime.now((timezone.utc)) + timedelta(minutes=0)  # always get new token when called

        response_object = {'status': 'success'}
        response_object['client_token'] = session['spotify_token']
        response_object['app_token'] = session['app_token']
        response_object['knowledge_api'] = Config.GOOGLE_KNOWLEDGE_GRAPH_API_KEY
        if current_user.is_authenticated:
            response_object['user_id'] = current_user.username
            response_object['premium'] = session['premium']
            response_object['avatar'] = current_user.avatar(140)
            response_object['patreon'] = current_user.patreon
        else:
            response_object['user_id'] = None
            response_object['premium'] = False
            response_object['avatar'] = None
        response = jsonify(response_object)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    response_object = {
        'status': 'error',
        'info': 'Missing token, Spotify not authorized.'
    }
    response = jsonify(response_object)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@ bp.route('/disable_patreon_link')
@ login_required
def disable_patreon_link():
    if current_user.is_authenticated:
        user = User.query.filter(User.id == current_user.id).first_or_404()
        user.patreon = True
        db.session.commit()
        return redirect(url_for('main.index'))
    return redirect(url_for('main.index'))


@bp.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():

    if Config.MODE == "DEVELOPMENT":
        user = User.query.filter_by(username='12173954849').first()
        login_user(user)

    form = ChangeAvatar()
    if request.method == 'POST':
        if form.choice.data == "remove":
            current_user.img = ""
            db.session.commit()
        if form.choice.data == "restore":
            response = sp.get_user()
            info = response.json()
            try:
                image_url = info['images'][0]['url']
                response = get_avatar(current_user.username, image_url)
                image = response[0]
            except Exception:
                flash("Error: Could not retrieve a photo from Spotify.", 'danger')
                return redirect(url_for('auth.change_avatar'))
            current_user.img = image
            db.session.commit()
        if form.choice.data == "upload":
            if form.link.data:
                response = get_avatar(current_user.username, form.link.data)
                if response[1] == 200:
                    current_user.img = response[0]
                    db.session.commit()
                else:
                    flash(response[0], 'danger')
                    return redirect(url_for('auth.change_avatar'))
            else:
                uploaded_file = request.files['file']
                response = upload_avatar(current_user.username, uploaded_file)
                if response[1] == 200:
                    current_user.img = response[0]
                    db.session.commit()
                else:
                    flash(response[0], 'danger')
                    return redirect(url_for('auth.change_avatar'))

        return redirect(url_for('main.index'))
    return render_template('change_avatar.html', title='Change Profile Picture',
                           form=form)
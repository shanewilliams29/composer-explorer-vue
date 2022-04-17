from app import app, db, sp
from flask import jsonify, request, redirect, session, render_template, abort
from config import Config
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike, Spotify, Artists
from app.classes import SortFilter
from sqlalchemy import func, text
from datetime import datetime, timedelta
import json
import jsonpickle


@app.before_request
def before_request():
    # get spotify token
    if not session.get('spotify_token'):
        session['spotify_token'] = None

    if not session.get('mobile'):
        session['mobile'] = None


# @app.route('/')
# def index():
#     return app.send_static_file('index.html')

@app.route('/', defaults={'path': ''})
@app.route("/<string:path>")
def index(path):
    if request.MOBILE and not session['mobile']:
        session['mobile'] = 'true'
        return redirect('/mobile')

    return render_template("index.html")
    # return app.send_static_file('index.html')


# @app.route('/mobile')
# def index_mobile():
#     return send_from_directory('../dist-mobile', 'index.html')


@app.route('/connect_spotify')
def connect_spotify():
    url = sp.authorize()
    return redirect(url)


@app.route('/spotify')
def spotify():

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
    session['spotify_token_expire_time'] = datetime.now() + timedelta(hours=1)

    mode = Config.MODE

    if mode == "DEVELOPMENT":
        return redirect("http://localhost:8080/")
    else:
        if session['mobile']:
            return redirect("/mobile")
        else:
            return redirect("/")


@app.route('/log_out')
def log_out():
    session.clear()
    return redirect("/")


@app.route('/api/get_token')
def get_token():
    # add check for expiry
    if session['spotify_token']:
        token = session['spotify_token']
        # return response
        response_object = {'status': 'success'}
        response_object['token'] = token
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


@app.route('/api/composers', methods=['GET'])
def get_composers():
    # look for search item
    search_item = request.args.get('search')
    composer_filter = request.args.get('filter')

    eras = ['common', 'early', 'baroque', 'classical', 'romantic', '20th']

    # retrieve composers from database
    if search_item:
        search = "%{}%".format(search_item)
        composer_list = ComposerList.query \
            .filter(ComposerList.name_norm.ilike(search)) \
            .order_by(ComposerList.region, ComposerList.born).all()
        if len(composer_list) < 1:
            response_object = {'status': 'success'}
            response_object['composers'] = composer_list
            response = jsonify(response_object)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response

    elif composer_filter:
        if composer_filter == "women":
            composer_list = ComposerList.query \
                .filter(ComposerList.female == True) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "catalogued":
            composer_list = db.session.query(ComposerList)\
                .join(WorkList, ComposerList.name_short == WorkList.composer)\
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "all":
            composer_list = db.session.query(ComposerList)\
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "alphabet":
            composer_list = db.session.query(ComposerList)\
                .order_by(ComposerList.name_short, ComposerList.born).all()
        if composer_filter == "popular":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.catalogued == True) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter in eras:
            sortfilter = SortFilter()
            date_minmax_sort = sortfilter.get_era_filter(composer_filter)
            datemin = date_minmax_sort[0]
            datemax = date_minmax_sort[1]
            print(datemin, datemax)
            composer_list = ComposerList.query \
                .filter(ComposerList.born >= datemin, ComposerList.born < datemax) \
                .order_by(ComposerList.region, ComposerList.born).all()

    else:
        composer_list = db.session.query(ComposerList)\
            .filter(ComposerList.catalogued == True) \
            .order_by(ComposerList.region, ComposerList.born).all()

    # get era colours, flag icons, and proper region names
    with open('app/static/eras.json') as f:
        eras = json.load(f)

    with open('app/static/countries.json') as f:
        flags = json.load(f)

    with open('app/static/regions.json') as f:
        region_names = json.load(f)

    # create COMPOSERS object for jsonifying
    COMPOSERS = []
    for composer in composer_list:

        median_age = (composer.died - composer.born) / 2
        median_year = median_age + composer.born
        for era in eras:
            if median_year > era[1]:
                era_color = era[3]
        region_name = region_names[composer.region]
        flag = flags[composer.nationality].lower()

        info = {
            'id': composer.id,
            'name_short': composer.name_short,
            'name_full': composer.name_full,
            'born': composer.born,
            'died': composer.died,
            'flag': app.config['STATIC'] + 'flags/1x1/' + flag + '.svg',
            'img': app.config['STATIC'] + 'img/' + composer.name_short + '.jpg',
            'region': region_name,
            'color': era_color,
            'popular': composer.catalogued
        }
        COMPOSERS.append(info)

    if composer_filter == "alphabet":
        # group onto alphabet
        composers_by_region = {}
        composers_in_region = []
        i = 0
        prev_region = COMPOSERS[i]['name_short'][0].upper()

        while i < len(COMPOSERS):
            region = COMPOSERS[i]['name_short'][0].upper()
            if region == prev_region:
                composers_in_region.append(COMPOSERS[i])
                i += 1
                if i == len(COMPOSERS):
                    composers_by_region[prev_region] = composers_in_region
            else:
                composers_by_region[prev_region] = composers_in_region
                composers_in_region = []
                composers_in_region.append(COMPOSERS[i])
                prev_region = region
                i += 1
                if i == len(COMPOSERS):
                    composers_by_region[prev_region] = composers_in_region
    else:
       # group onto regions
        composers_by_region = {}
        composers_in_region = []
        i = 0
        prev_region = COMPOSERS[i]['region']

        while i < len(COMPOSERS):
            region = COMPOSERS[i]['region']
            if region == prev_region:
                composers_in_region.append(COMPOSERS[i])
                i += 1
                if i == len(COMPOSERS):
                    composers_by_region[prev_region] = composers_in_region
            else:
                composers_by_region[prev_region] = composers_in_region
                composers_in_region = []
                composers_in_region.append(COMPOSERS[i])
                prev_region = region
                i += 1
                if i == len(COMPOSERS):
                    composers_by_region[prev_region] = composers_in_region

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response = jsonify(response_object)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/works/<name>', methods=['GET'])
def get_works(name):
    filter_method = request.args.get('filter')
    search = request.args.get('search')

    # old ordering: WorkList.order, WorkList.genre, WorkList.date, WorkList.cat, WorkList.id

    if search:
        search_term = "%{}%".format(search)
        works_list = WorkList.query.filter_by(composer=name)\
            .filter(WorkList.genre.ilike(search_term)) \
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        if not works_list:
            works_list = WorkList.query.filter_by(composer=name)\
                .filter(WorkList.title.ilike(search_term)) \
                .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        if not works_list:
            works_list = WorkList.query.filter_by(composer=name)\
                .filter(WorkList.cat.ilike(search_term)) \
                .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        if not works_list:
            works_list = WorkList.query.filter_by(composer=name)\
                .filter(WorkList.nickname.ilike(search_term)) \
                .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    elif filter_method:
        if filter_method == "recommended":
            works_list = WorkList.query.filter_by(composer=name, recommend=True).order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        else:
            works_list = WorkList.query.filter_by(composer=name)\
                .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
    else:
        works_list = WorkList.query.filter_by(composer=name, recommend=True)\
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = works_list
        response = jsonify(response_object)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    WORKS = []
    for work in works_list:
        info = {
            'id': work.id,
            'genre': work.genre,
            'cat': work.cat,
            'recommend': work.recommend,
            'title': work.title,
            'nickname': work.nickname,
            'date': work.date,
            'album_count': work.album_count
        }
        WORKS.append(info)

    # group onto genres
    works_by_genre = {}
    works_in_genre = []
    i = 0
    prev_genre = WORKS[i]['genre']

    while i < len(WORKS):
        genre = WORKS[i]['genre']
        if genre == prev_genre:
            works_in_genre.append(WORKS[i])
            i += 1
            if i == len(WORKS):
                works_by_genre[prev_genre] = works_in_genre
        else:
            works_by_genre[prev_genre] = works_in_genre
            works_in_genre = []
            works_in_genre.append(WORKS[i])
            prev_genre = genre
            i += 1
            if i == len(WORKS):
                works_by_genre[prev_genre] = works_in_genre

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre

    response = jsonify(response_object)

    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/albums/<work_id>', methods=['GET'])
def get_albums(work_id):
    page = request.args.get('page', 1, type=int)

    # get filter and search arguments
    artistselect = request.args.get('artist')
    searchselect = request.args.get('search')
    search = None

    if artistselect:
        search = "%{}%".format(artistselect)
    elif searchselect:
        search = "%{}%".format(searchselect)

    if search:
        albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
            .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True, WorkAlbums.artists.ilike(search)) \
            .outerjoin(AlbumLike).group_by(WorkAlbums) \
            .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(page, 1000, False)

    else:
        albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
            .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True)\
            .outerjoin(AlbumLike).group_by(WorkAlbums) \
            .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(page, 1000, False)

    if not albums.items:
        response_object = {'status': 'success'}
        response_object['albums'] = []
        response = jsonify(response_object)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # artist list
    work_artists = db.session.query(Artists, func.count(Artists.count).label('total')) \
        .filter(Artists.workid == work_id).group_by(Artists.name) \
        .order_by(text('total DESC'), Artists.name).all()

    artist_list = {}

    for artist in work_artists:
        artist_list[artist[0].name] = artist[1]

    album_list = []
    duplicates_list = []
    match_string = ""

    for tup in albums.items:
        item = jsonpickle.decode(tup[0].data)
        item['likes'] = tup[1]
        item['id'] = tup[0].id

        artists_string = ''.join(sorted(item['all_artists'].strip()))  # put alphabetically
        match_string = artists_string + str(item['release_date'])
        # match_string = item['artists'].strip() + str(item['release_date'])

        if match_string in duplicates_list:
            continue
        else:
            duplicates_list.append(match_string)

        # de-rate newer, crappy albums
        if int(item['release_date']) >= 2020:
            item['score'] = item['score'] / 4

        # add to album list
        album_list.append(item)

        # re-sort the album list on popularity and likes
        sorted_list = sorted(album_list, key=lambda d: d['score'], reverse=True)
        sorted_list = sorted(sorted_list, key=lambda d: d['likes'], reverse=True)

        # return paginated items - NEED TO IMPLEMENT INFINITY SCROLL
        if not session['mobile']:
            sorted_list = sorted_list[0:50]

        # return less items for mobile
        if session['mobile']:
            sorted_list = sorted_list[0:25]

    response_object = {'status': 'success'}
    response_object['albums'] = sorted_list
    response_object['artists'] = artist_list
    response = jsonify(response_object)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/composerinfo/<composer>', methods=['GET'])
def get_composerinfo(composer):
    composer_info = db.session.query(ComposerList)\
        .filter(ComposerList.name_short == composer).first()
    composer_info.image = app.config['STATIC'] + 'img/' + composer + '.jpg'
    response_object = {'status': 'success'}
    response_object['info'] = composer_info
    response = jsonify(response_object)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/albuminfo/<album_id>', methods=['GET'])
def get_albuminfo(album_id):
    album = db.session.query(WorkAlbums)\
        .filter(WorkAlbums.id == album_id)\
        .first()
    # return jsonpickle.encode(album)

    album_details = jsonpickle.decode(album.data)

    ALBUM = {
        'id': album.id,
        'album_img': album_details['album_img'],
        'album_name': album_details['album_name'],
        'album_uri': album_details['album_uri'],
        'all_artists': album_details['all_artists'],
        'artists': album_details['artists'],
        'minor_artists': album_details['minor_artists'],
        'release_date': album_details['release_date'],
        'tracks': album_details['tracks'],
        'track_count': album_details['track_count']
    }

    response_object = {'status': 'success'}
    response_object['album'] = ALBUM
    response = jsonify(response_object)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# @app.route('/api/composerinfo/<composer>', methods=['GET'])
# def get_composerinfo():

#     composer = ComposerList.query.filter_by(name_short=composer).first_or_404()

#     return jsonpickle.encode(composer)

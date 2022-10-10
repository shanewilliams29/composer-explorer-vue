from app import db, sp, cache
from flask import jsonify, request, session, abort, current_app
from flask_login import current_user, login_required
from config import Config
from app.functions import prepare_composers, group_composers_by_region
from app.functions import prepare_works
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike, Artists
from app.models import ArtistList, User
from app.classes import SortFilter
from sqlalchemy import func, text, or_
from app.api import bp
import json
import jsonpickle
import random


@bp.route('/api/composers', methods=['GET'])
# @cache.cached(query_string=True)
def get_composers():
    # look for search item
    search_item = request.args.get('search')
    composer_filter = request.args.get('filter')
    # get_genres = request.args.get('genres')

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
                .filter(ComposerList.catalogued == True) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "alphabet":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.catalogued == True) \
                .order_by(ComposerList.name_short, ComposerList.born).all()
        if composer_filter == "popular":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.tier == 1) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "tier2":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.tier == 2, ComposerList.catalogued == True) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "tier3":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.tier == 3) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter == "tier4":
            composer_list = db.session.query(ComposerList)\
                .filter(ComposerList.tier == None) \
                .order_by(ComposerList.region, ComposerList.born).all()
        if composer_filter in eras:
            sortfilter = SortFilter()
            date_minmax_sort = sortfilter.get_era_filter(composer_filter)
            datemin = date_minmax_sort[0]
            datemax = date_minmax_sort[1]

            composer_list = ComposerList.query \
                .filter(ComposerList.born >= datemin, ComposerList.born < datemax, ComposerList.catalogued == True) \
                .order_by(ComposerList.region, ComposerList.born).all()

    else:
        composer_list = db.session.query(ComposerList)\
            .filter(ComposerList.tier == 1) \
            .order_by(ComposerList.region, ComposerList.born).all()

    # prepare list for display
    COMPOSERS = prepare_composers(composer_list)

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
        composers_by_region = group_composers_by_region(COMPOSERS)

    # get genres (for radio)
    search_list = []
    for composer in composer_list:
        search_list.append(composer.name_short)
    
    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    genre_list = sorted(genre_list)

    session['radio_composers'] = search_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', search_list)  # store in cache for dev server

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/favoritescomposers', methods=['GET'])
def get_favoritescomposers():
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    composer_list = db.session.query(ComposerList).join(WorkAlbums).join(AlbumLike)\
        .filter(AlbumLike.user_id == user_id)\
        .order_by(ComposerList.region, ComposerList.born).all()

    search_list = []
    for composer in composer_list:
        search_list.append(composer.name_short)

    session['radio_composers'] = search_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', search_list)  # store in cache for dev server 

    if not composer_list:
        response_object = {'status': 'success'}
        response_object['composers'] = []
        response_object['genres'] = []
        response = jsonify(response_object)
        return response

    # prepare list for display
    COMPOSERS = prepare_composers(composer_list)
    composers_by_region = group_composers_by_region(COMPOSERS)

    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    genre_list = sorted(genre_list)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/multicomposers', methods=['POST'])  # used in radio mode
def get_multicomposers():
    # get composers
    composers = request.get_json()

    search_list = []
    for composer in composers:
        search_list.append(composer['value'])

    # store composers in session
    session['radio_composers'] = search_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', search_list)

    composer_list = db.session.query(ComposerList)\
        .filter(ComposerList.name_short.in_(search_list)) \
        .order_by(ComposerList.region, ComposerList.born).all()

    # prepare list for display
    COMPOSERS = prepare_composers(composer_list)
    composers_by_region = group_composers_by_region(COMPOSERS)

    # genre categories
    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    general_genre_list = sorted(genre_list)

    # genres for these specific composers
    genres = db.session.query(WorkList.genre)\
        .filter(WorkList.composer.in_(search_list)).order_by(WorkList.genre).distinct()

    composer_genre_list = []
    for (item,) in genres:
        composer_genre_list.append(item)

    # match on general genre list
    final_genre_list = []
    for genre in general_genre_list:
        if genre.lower() in ' '.join(composer_genre_list).lower():
            final_genre_list.append(genre)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = final_genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/composersradio', methods=['GET'])
@cache.cached()
def get_composersradio():
    # look for search item

    composer_list = db.session.query(ComposerList)\
        .filter(ComposerList.catalogued == True) \
        .order_by(ComposerList.name_short).all()

    name_list = []
    for composer in composer_list:
        name_list.append(composer.name_short)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = name_list
    response = jsonify(response_object)
    return response


@bp.route('/api/works/<name>', methods=['GET'])
# @cache.cached(query_string=True)
def get_works(name):
    filter_method = request.args.get('filter')
    search = request.args.get('search')

    # old ordering: WorkList.order, WorkList.genre, WorkList.date, WorkList.cat, WorkList.id

    if search:
        works_list = WorkList.query.filter_by(composer=name)\
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

        return_list = []

        for work in works_list:
            search_string = str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
            if search.lower() in search_string.lower():
                return_list.append(work)

        works_list = return_list

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
        return response

    # get liked works
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    if user_id:
        liked_works = db.session.query(WorkList).join(WorkAlbums).join(AlbumLike)\
            .filter(AlbumLike.user_id == user_id, WorkList.composer == name).all()
    else:
        liked_works = []

    liked_works_ids = []
    for work in liked_works:
        liked_works_ids.append(work.id)

    # generate works list
    works_by_genre = prepare_works(works_list, liked_works_ids)

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/favoriteworks/<name>', methods=['GET'])
# @cache.cached(query_string=True)
def get_favoriteworks(name):

    # get liked works
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    works_list = db.session.query(WorkList).join(WorkAlbums).join(AlbumLike)\
        .filter(AlbumLike.user_id == user_id, WorkList.composer == name).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = works_list
        response = jsonify(response_object)
        return response

    liked_works = works_list

    liked_works_ids = []
    for work in liked_works:
        liked_works_ids.append(work.id)

    # generate works list
    works_by_genre = prepare_works(works_list, liked_works_ids)

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/worksbygenre', methods=['POST'])  # used in radio mode
def get_worksbygenre():
    # get genres
    payload = request.get_json()

    search_list = []
    for genre in payload['genres']:
        search_list.append(genre['value'])

    work_filter = payload['filter']
    search_term = payload['search']
    artist_name = payload['artist']
    radio_type = payload['radio_type']

    # get composers selected
    if not session.get('radio_composers'):
        composer_list = cache.get('composers')   # for dev server testing
    else:
        composer_list = session['radio_composers']

    if not composer_list:
        response_object = {'status': 'success'}
        response_object['works'] = []
        response_object['playlist'] = []
        response = jsonify(response_object)
        return response

    if search_list[0] == "all":
        if artist_name:
            if work_filter == 'recommended':
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), WorkList.recommend == True)\
                    .order_by(WorkList.genre, WorkList.id).all()  # don't order by order no. in multi mode
            elif work_filter == 'obscure':
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), or_(WorkList.recommend == None, WorkList.recommend != True), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()
            else:
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()
        else:
            if work_filter == 'recommended':
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), WorkList.recommend == True)\
                    .order_by(WorkList.genre, WorkList.id).all()  # don't order by order no. in multi mode
            elif work_filter == 'obscure':
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(WorkList.recommend == None, WorkList.recommend != True), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()
            else:
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()

    else:

        conditions = []
        for genre in search_list:
            conditions.append(WorkList.genre.ilike('%{}%'.format(genre)))

        for genre in search_list:
            conditions.append(WorkList.search.ilike('%{}%'.format(genre)))

        for genre in search_list:
            conditions.append(WorkList.title.ilike('%{}%'.format(genre)))

        for genre in search_list:
            conditions.append(WorkList.nickname.ilike('%{}%'.format(genre)))

        if artist_name:
            if work_filter == 'recommended':
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), or_(*conditions), WorkList.recommend == True)\
                    .order_by(WorkList.genre, WorkList.id).all()  # don't order by order no. in multi mode

            elif work_filter == 'obscure':
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), or_(*conditions), WorkList.recommend == None, WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()

            else:
                works_list = db.session.query(WorkList).join(Artists)\
                    .filter(Artists.name == artist_name, WorkList.composer.in_(composer_list), or_(*conditions), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()  
        else:
            if work_filter == 'recommended':
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), WorkList.recommend == True)\
                    .order_by(WorkList.genre, WorkList.id).all()  # don't order by order no. in multi mode

            elif work_filter == 'obscure':
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), WorkList.recommend == None, WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()

            else:
                works_list = db.session.query(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), WorkList.album_count > 0)\
                    .order_by(WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = []
        response_object['playlist'] = []
        response = jsonify(response_object)
        return response

    if search_term:
        return_list = []
        # search filtering
        for work in works_list:
            search_string = str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
            if search_term.lower() in search_string.lower():
                return_list.append(work)

        if not return_list:
            response_object = {'status': 'success'}
            response_object['works'] = []
            response_object['playlist'] = []
            response = jsonify(response_object)
            return response
        else:
            works_list = return_list

    # get liked works
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    if user_id:
        liked_works = db.session.query(WorkList).join(WorkAlbums).join(AlbumLike)\
            .filter(AlbumLike.user_id == user_id, WorkList.composer.in_(composer_list)).all()
    else:
        liked_works = []

    liked_works_ids = []
    for work in liked_works:
        liked_works_ids.append(work.id)

    # filter out liked works only in favorites radio
    final_works = []
    if radio_type == 'favorites' and user_id:
        for work in works_list:
            if work.id in liked_works_ids:
                final_works.append(work)
            else:
                pass
    else:
        final_works = works_list

    # generate works list
    works_by_genre = prepare_works(final_works, liked_works_ids)

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = final_works  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/exportplaylist', methods=['POST'])  # used in radio mode
@login_required
def exportplaylist():
    # get genres
    payload = request.get_json()

    search_list = []
    for genre in payload['genres']:
        search_list.append(genre['value'])

    work_filter = payload['filter']
    search_term = payload['search']
    limit = payload['limit']
    name = payload['name']
    prefetch = payload['prefetch']
    random_album = payload['random']
    performer = payload['performer']
    radio_type = payload['radio_type']

    if prefetch:
        # get composers selected
        if not session.get('radio_composers'):
            composer_list = cache.get('composers')  # for dev server testing
            user_id = 85
        else:
            composer_list = session['radio_composers']
            user_id = current_user.id

        # ALL GENRES
        if search_list[0] == "all":

            conditions = []
            conditions2 = []

            if search_term: 
                conditions.append(WorkList.genre.ilike('%{}%'.format(search_term)))
                conditions.append(WorkList.search.ilike('%{}%'.format(search_term)))
                conditions.append(WorkList.title.ilike('%{}%'.format(search_term)))
                conditions.append(WorkList.nickname.ilike('%{}%'.format(search_term)))
                conditions.append(WorkList.cat.ilike('%{}%'.format(search_term)))

            if performer: 
                conditions2.append(WorkAlbums.artists.ilike('%{}%'.format(performer)))

            if radio_type == 'favorites': 
                conditions2.append(AlbumLike.user_id == user_id)
                limit = 1000

            if work_filter == 'recommended':
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), WorkList.album_count > 0, WorkList.recommend == True, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

            elif work_filter == 'obscure':
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), WorkList.album_count > 0, WorkList.recommend == None, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

            else:
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), WorkList.album_count > 0, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

        # SELECTED GENRES
        else:
            conditions = []
            conditions2 = []
            conditions3 = []

            for genre in search_list:
                conditions.append(WorkList.genre.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.search.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.title.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.nickname.ilike('%{}%'.format(genre)))               

            if search_term: 
                conditions2.append(WorkList.genre.ilike('%{}%'.format(search_term)))
                conditions2.append(WorkList.search.ilike('%{}%'.format(search_term)))
                conditions2.append(WorkList.title.ilike('%{}%'.format(search_term)))
                conditions2.append(WorkList.nickname.ilike('%{}%'.format(search_term)))
                conditions2.append(WorkList.cat.ilike('%{}%'.format(search_term)))

            if performer: 
                conditions3.append(WorkAlbums.artists.ilike('%{}%'.format(performer)))

            if radio_type == 'favorites': 
                conditions3.append(AlbumLike.user_id == user_id)
                limit = 1000

            if work_filter == 'recommended':
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), or_(*conditions3), WorkList.album_count > 0, WorkList.recommend == True, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

            elif work_filter == 'obscure':
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), or_(*conditions3), WorkList.album_count > 0, WorkList.recommend == None, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

            else:
                album_list = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')).join(WorkList)\
                    .filter(WorkList.composer.in_(composer_list), or_(*conditions), or_(*conditions2), or_(*conditions3), WorkList.album_count > 0, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
                    .outerjoin(AlbumLike).group_by(WorkAlbums) \
                    .order_by(WorkList.genre, WorkList.id, text('total DESC'), WorkAlbums.score.desc()).all()

        if not album_list:
            abort(404)

        hold_albums = []
        best_albums = []
        prev_album_workid = ""
        for tup in album_list:
            if tup[0].workid == prev_album_workid:
                if random_album:  # for randomizing albums
                    hold_albums.append(tup[0])
                else:
                    pass
            else:
                if random_album and len(best_albums) > 0 and len(hold_albums) > 0:
                    integer = random.randint(0, len(hold_albums) - 1)  # replace with random
                    best_albums[-1] = hold_albums[integer]
                    hold_albums = []

                # if search_term:  # search filter screening
                #     search_string = str(tup[0].work.genre) + str(tup[0].work.cat) + str(tup[0].work.suite) + str(tup[0].work.title) + str(tup[0].work.nickname) + str(tup[0].work.search)
                #     if search_term.lower() in search_string.lower():
                #         best_albums.append(tup[0])
                #         prev_album_workid = tup[0].workid
                else:
                    best_albums.append(tup[0])
                    prev_album_workid = tup[0].workid

        # last replacement
        if random_album and len(best_albums) > 0 and len(hold_albums) > 0:
            integer = random.randint(0, len(hold_albums) - 1)  # replace with random
            best_albums[-1] = hold_albums[integer]
    
        tracklist = []
        for album in best_albums:
            album = json.loads(album.data)

            for track in album['tracks']:
                tracklist.append(track[1])

        cache.set('tracks', tracklist)

        response_object = {'status': 'success'}
        response_object['track_count'] = len(tracklist)
        response = jsonify(response_object)

        return response

    # submit to Spotify

    if Config.MODE == "DEVELOPMENT":
        session['spotify_token'] = cache.get('token')  # store in cache for dev
        user_id = '12173954849'
    else:
        user_id = current_user.username
    
    tracklist = cache.get('tracks')

    try:
        response = sp.create_playlist(name, user_id)
        playlist_id = response.json()['id']
    except:
        return response.json()

    i = 0
    k = 0
    uristring = ""
    for track in tracklist:
        i += 1
        k += 1

        if i == 50 or k == len(tracklist):
            track = "spotify:track:" + track + ","
            uristring = uristring + track
            response = sp.add_to_playlist(playlist_id, uristring)
            i = 0
            uristring = ""
        else:
            track = "spotify:track:" + track + ","
            uristring = uristring + track
            #print(str(i) + " " + str(k) + " " + str(len(tracklist)))

    return response.json()

    # if search_term:
    #     return_list = []
    #     # search filtering
    #     for work in works_list:
    #         search_string = str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
    #         if search_term.lower() in search_string.lower():
    #             return_list.append(work)

    #     if not return_list:
    #         response_object = {'status': 'success'}
    #         response_object['works'] = return_list
    #         response = jsonify(response_object)
    #         return response
    #     else:
    #         works_list = return_list

    # need playlist


@bp.route('/api/albums/<work_id>', methods=['GET'])
def get_albums(work_id):
    page = request.args.get('page', 1, type=int)

    # get filter and search arguments
    artistselect = request.args.get('artist')
    sort = request.args.get('sort')
    limit = request.args.get('limit', default=100)
    favorites = request.args.get('favorites', default=None)
    search = None

    if artistselect:
        search = "%{}%".format(artistselect)

    if search:
        albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
            .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True, WorkAlbums.artists.ilike(search), WorkAlbums.work_track_count <= limit, WorkAlbums.album_type != "compilation") \
            .outerjoin(AlbumLike).group_by(WorkAlbums) \
            .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 1000, False)

        if not albums.items:  # return complilation albums if no results
            albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
                .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True, WorkAlbums.artists.ilike(search), WorkAlbums.work_track_count <= limit) \
                .outerjoin(AlbumLike).group_by(WorkAlbums) \
                .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 1000, False)

    elif not favorites:
        albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
            .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)\
            .outerjoin(AlbumLike).group_by(WorkAlbums) \
            .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 1000, False)

        if not albums.items:  # return complilation albums if no results
            albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
                .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True, WorkAlbums.work_track_count <= limit)\
                .outerjoin(AlbumLike).group_by(WorkAlbums) \
                .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 1000, False)

    else:  # user favorites albums, for radio mode
        if current_user.is_authenticated:
            user_id = current_user.id
        elif Config.MODE == 'DEVELOPMENT':
            user_id = 85
        else:
            user_id = None

        albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
            .join(AlbumLike).group_by(WorkAlbums) \
            .filter(WorkAlbums.workid == work_id, AlbumLike.user_id == user_id)\
            .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 1000, False)

    if not albums.items:
        response_object = {'status': 'error'}
        response_object['albums'] = []
        response = jsonify(response_object)
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
        item['img_big'] = tup[0].img
        item['label'] = tup[0].label
        item['track_count'] = tup[0].track_count
        item['composer'] = tup[0].composer

        # de-rate newer, crappy albums
        if item['track_count']:
            if item['track_count'] > 50 and int(item['release_date'][0:4]) > 2019:
                item['score'] = item['score'] / 4

        # filter out repeat albums
        artists_string = ''.join(sorted(item['artists'].strip()))  # put alphabetically
        if search:  # return more repeat results for performer filter
            match_string = artists_string + str(item['release_date'])
        else:  # return more unique artists otherwise
            match_string = artists_string

        if match_string in duplicates_list:
            continue
        else:
            duplicates_list.append(match_string)
        # add to album list
        album_list.append(item)

    if sort == 'dateascending':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'])
    elif sort == 'datedescending':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'], reverse=True)
    else:
        # sort the album list on popularity and likes (recommended)
        sorted_list = sorted(album_list, key=lambda d: d['score'], reverse=True)
        sorted_list = sorted(sorted_list, key=lambda d: d['likes'], reverse=True)

    # return paginated items
    results_per_page = 30
    list_start = page * results_per_page - results_per_page
    list_end = page * results_per_page

    sorted_list = sorted_list[list_start:list_end]

    # get list of current_user's liked albums:
    search = "%{}%".format(work_id)

    if current_user.is_authenticated:
        albumlikes = db.session.query(AlbumLike)\
            .filter(AlbumLike.user_id == current_user.id, 
                    AlbumLike.album_id.ilike(search)).all()
    elif Config.MODE == 'DEVELOPMENT':
        albumlikes = db.session.query(AlbumLike)\
            .filter(AlbumLike.user_id == '85', 
                    AlbumLike.album_id.ilike(search)).all()
    else:
        albumlikes = []

    liked_albums = []
    for album in albumlikes:
        liked_albums.append(album.album_id)

    response_object = {'status': 'success'}
    response_object['albums'] = sorted_list
    response_object['artists'] = artist_list
    if sorted_list:
        response_object['composer'] = sorted_list[0]['composer']
    response_object['liked_albums'] = liked_albums
    response = jsonify(response_object)
    return response


@bp.route('/api/like/<album_id>/<action>')
def like_action(album_id, action):
    if current_user.is_authenticated:
        album = WorkAlbums.query.filter_by(id=album_id).first()
        if action == 'like':
            current_user.like_album(album)
            db.session.commit()
        if action == 'unlike':
            current_user.unlike_album(album)
            db.session.commit()
        response_object = {'status': 'success'}
        response = jsonify(response_object)
        return response
    elif Config.MODE == 'DEVELOPMENT':
        user = User.query.filter_by(id=85).first()
        album = WorkAlbums.query.filter_by(id=album_id).first()
        if action == 'like':
            user.like_album(album)
            db.session.commit()
        if action == 'unlike':
            user.unlike_album(album)
            db.session.commit()
        response_object = {'status': 'success'}
        response = jsonify(response_object)
        return response

    response_object = {'error': 'must be logged in to like albums'}
    response = jsonify(response_object)
    return response


@bp.route('/api/composerinfo/<composer>', methods=['GET'])
@cache.cached(query_string=True)
def get_composerinfo(composer):
    composer_info = db.session.query(ComposerList)\
        .filter(ComposerList.name_short == composer).first()
    composer_info.image = current_app.config['STATIC'] + 'img/' + composer + '.jpg'

    with open('app/static/countries.json') as f:
        flags = json.load(f)
        flag = flags[composer_info.nationality].lower()

    composer_info.region = current_app.config['STATIC'] + 'flags/1x1/' + flag + '.svg'

    response_object = {'status': 'success'}
    response_object['info'] = composer_info
    response = jsonify(response_object)
    return response


@bp.route('/api/workinfo/<work_id>', methods=['GET'])
@cache.cached(query_string=True)
def get_workinfo(work_id):
    work = db.session.query(WorkList)\
        .filter(WorkList.id == work_id).first()

    if work.genre == "Opera" or work.genre == "Stage Work" or work.genre == "Ballet":
        work.search = current_app.config['STATIC'] + 'headers/' + work.title + '.jpg'  # use for image
    elif "piano concerto" in work.title.lower():
        work.search = current_app.config['STATIC'] + 'headers/' + 'pianoconcerto' + '.jpg'
    else:
        work.search = current_app.config['STATIC'] + 'headers/' + work.genre.split()[0] + '.jpg'  # use for image

    response_object = {'status': 'success'}
    response_object['info'] = work
    response = jsonify(response_object)
    return response


@bp.route('/api/albuminfo/<album_id>', methods=['GET'])
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
    return response


@bp.route('/api/artistcomposers/<artist_name>', methods=['GET'])
# @cache.cached(query_string=True)
def get_artistcomposers(artist_name):

    composers = db.session.query(ComposerList).join(Artists, ComposerList.name_short == Artists.composer)\
        .filter(Artists.name == artist_name)\
        .order_by(ComposerList.region, ComposerList.born).all()

    search_list = []
    for composer in composers:
        search_list.append(composer.name_short)

    session['radio_composers'] = search_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', search_list)  # store in cache for dev server  

    # prepare list for display
    COMPOSERS = prepare_composers(composers)

    # group onto regions
    composers_by_region = group_composers_by_region(COMPOSERS)

    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    genre_list = sorted(genre_list)

    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/artistworks', methods=['GET'])
def get_artistworks():
    artist_name = request.args.get('artist')
    composer_name = request.args.get('composer')

    works_list = db.session.query(WorkList).join(Artists)\
        .filter(Artists.name == artist_name, WorkList.composer == composer_name)\
        .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = works_list
        response = jsonify(response_object)
        return response

    # get liked works
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    if user_id:
        liked_albums = db.session.query(WorkAlbums).join(AlbumLike).join(User)\
            .filter(User.id == user_id, WorkAlbums.composer == composer_name).all()
    else:
        liked_albums = []

    liked_works = []
    for album in liked_albums:
        liked_works.append(album.workid)

    # generate works list
    works_by_genre = prepare_works(works_list, liked_works)

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/artistlist', methods=['GET'])
@cache.cached()
def get_artistlist():
    artists = db.session.query(ArtistList).first()

    artist_list = artists.content

    response_object = {'status': 'success'}
    response_object['artists'] = artist_list
    response = jsonify(response_object)
    return response


@bp.route('/api/topartists', methods=['GET'])  # used to build json list, not accessible
def get_topartists():
    # albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
    #     .join(AlbumLike).group_by(WorkAlbums) \
    #     .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(1, 100, False)

    artists = db.session.query(Artists, func.count(Artists.id).label('total'))\
        .group_by(Artists.name).order_by(text('total DESC')).paginate(1, 160, False)

    artist_list = []
    exclude_list = ['baroque', 'augsburger', 'antiqua', 'milano', 'quartet', 'beethoven', 'carl philipp emanuel bach', 'orchest', 'philharm', 'symphony', 'concert', 'chamber', 'anonymous', 'academy', 'staats', 'consort', 'chopin', 'mozart', 'symphoniker', 'covent garden', 'choir', 'akademie', 'stuttgart', 'llscher']

    flag = False
    for artist in artists.items:
        for item in exclude_list:
            if item in artist[0].name.lower():
                flag = True
            else:
                pass
        if not flag:
            item = ['', '', '']
            item[0] = artist[0].name
            item[1] = artist[1]
            item[2] = random.randint(0, 2)
            artist_list.append(item)
            print(item[0] + " " + str(item[1]))
        flag = False

    response = jsonify(artist_list)
    return response

    # ranking = []
    # this_rank = 1
    # ranking.append(this_rank)
    # for i in range(1, len(artist_list)):
    #     if artist_list[i]['recordings'] == artist_list[i - 1]['recordings']:
    #         ranking.append(this_rank)
    #     else:
    #         this_rank += 1
    #         ranking.append(this_rank)

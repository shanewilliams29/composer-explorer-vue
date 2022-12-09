from app import db, sp, cache
from flask import jsonify, request, session, abort, current_app
from flask_login import current_user, login_required
from config import Config
from app.functions import prepare_composers, group_composers_by_region, group_composers_by_alphabet
from app.functions import prepare_works
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike, Artists
from app.models import ArtistList, User
from sqlalchemy import func, text, or_, and_
from sqlalchemy.orm import aliased
from app.api import bp
from unidecode import unidecode
import json
import jsonpickle
import random
import re


@bp.route('/api/composers', methods=['GET'])  # main composer list
# @cache.cached(query_string=True)
def get_composers():
    # look for search term or filter term
    search_item = request.args.get('search')
    composer_filter = request.args.get('filter')

    eras = {
        'common': (1500, 1907),
        'early': (1000, 1600),
        'baroque': (1550, 1725),
        'classical': (1711, 1800),
        'romantic': (1770, 1875),
        '20th': (1850, 2051),

    }
    datemin = 0
    datemax = 0

    # first search for composers if search term is present
    if search_item:
        search = "%{}%".format(search_item)
        composer_list = ComposerList.query \
            .filter(ComposerList.name_norm.ilike(search)) \
            .order_by(ComposerList.region, ComposerList.born).all()
        if len(composer_list) < 1:
            response_object = {'status': 'success'}
            response_object['composers'] = []
            response = jsonify(response_object)
            return response

    # if no search, filter composers
    elif composer_filter:

        # get datemin and datemax for era filtering
        if composer_filter in eras:
            datemin, datemax = eras[composer_filter]

        # define a dictionary that maps filter names to the corresponding query
        filter_queries = {
            'women': ComposerList.query.filter_by(female=True),
            'catalogued': ComposerList.query.join(WorkList, ComposerList.name_short == WorkList.composer),
            'all': ComposerList.query.filter_by(catalogued=True),
            'alphabet': ComposerList.query.filter_by(catalogued=True).order_by(ComposerList.name_short),
            'popular': ComposerList.query.filter_by(tier=1, catalogued=True),
            'tier2': ComposerList.query.filter_by(tier=2, catalogued=True),
            'tier3': ComposerList.query.filter_by(tier=3, catalogued=True),
            'tier4': ComposerList.query.filter_by(tier=None, catalogued=True),
            'common': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
            'early': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
            'baroque': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
            'classical': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
            'romantic': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
            '20th': ComposerList.query.filter(ComposerList.catalogued == True, ComposerList.born >= datemin, ComposerList.born < datemax),
        }

        # retrieve the appropriate query based on the filter name and sort
        query = filter_queries.get(composer_filter)
        composer_list = query.order_by(ComposerList.region, ComposerList.born).all()

    else:
        # default to Tier 1 composers
        composer_list = db.session.query(ComposerList)\
            .filter(ComposerList.tier == 1) \
            .order_by(ComposerList.region, ComposerList.born).all()

    # prepare key info from list for JSON response
    COMPOSERS = prepare_composers(composer_list)

    # group onto alphabet
    if composer_filter == "alphabet":
        composers_by_region = group_composers_by_alphabet(COMPOSERS)
    
    # group onto regions
    else:
        composers_by_region = group_composers_by_region(COMPOSERS)

    # store list of composers in session for radio use
    composer_name_list = []
    for composer in composer_list:
        composer_name_list.append(composer.name_short)

    session['radio_composers'] = composer_name_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', composer_name_list)  # store in cache for dev server

    # get genres (for radio)
    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    genre_list = sorted(genre_list)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/favoritescomposers', methods=['GET'])  # favorites mode composer list
def get_favoritescomposers():
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  #85
    else:
        user_id = None

    # get favorite composers from database
    composer_list = db.session.query(ComposerList).join(WorkAlbums).join(AlbumLike)\
        .filter(AlbumLike.user_id == user_id)\
        .order_by(ComposerList.region, ComposerList.born).all()

    if not composer_list:
        response_object = {'status': 'success'}
        response_object['composers'] = []
        response_object['genres'] = []
        response = jsonify(response_object)
        return response

    # store list of composers in session for radio use
    composer_name_list = []
    for composer in composer_list:
        composer_name_list.append(composer.name_short)

    session['radio_composers'] = composer_name_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', composer_name_list)  # store in cache for dev server

    # prepare list for display
    COMPOSERS = prepare_composers(composer_list)
    composers_by_region = group_composers_by_region(COMPOSERS)

    # get genres (for radio)
    with open('app/static/genres.json') as f:
        genre_list = json.load(f)
    genre_list = sorted(genre_list)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    response_object['genres'] = genre_list
    response = jsonify(response_object)
    return response


@bp.route('/api/multicomposers', methods=['POST'])  # used in radio mode composer multi-select
def get_multicomposers():
    # get composers and put in list
    composers = request.get_json()
    search_list = []
    for composer in composers:
        search_list.append(composer['value'])

    # store list of composers in session for radio use
    session['radio_composers'] = search_list
    if Config.MODE == "DEVELOPMENT":
        cache.set('composers', search_list)

    # get selected composers from database
    composer_list = db.session.query(ComposerList)\
        .filter(ComposerList.name_short.in_(search_list)) \
        .order_by(ComposerList.region, ComposerList.born).all()

    # prepare list for display
    COMPOSERS = prepare_composers(composer_list)
    composers_by_region = group_composers_by_region(COMPOSERS)

    # get genre categories
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


@bp.route('/api/composersradio', methods=['GET'])  # used by radio to populate composer multiselect
#@cache.cached()
def get_composersradio():
    composer_list = db.session.query(ComposerList.name_short)\
        .filter(ComposerList.catalogued == True) \
        .order_by(ComposerList.name_short).all()

    name_list = []
    for (item,) in composer_list:
        name_list.append(item)

    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = name_list
    response = jsonify(response_object)
    return response


@bp.route('/api/works/<name>', methods=['GET'])  # main works list API
def get_works(name):
    # get filter and search terms
    search = request.args.get('search')
    filter_method = request.args.get('filter')

    # first filter based on search term if present
    if search:
        works_list = WorkList.query.filter_by(composer=name)\
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

        return_list = []

        for work in works_list:
            search_string = str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
            if search.lower() in unidecode(search_string.lower()):
                return_list.append(work)

        works_list = return_list

    # next filter on filter item if present
    elif filter_method:
        if filter_method == "recommended":
            works_list = WorkList.query.filter_by(composer=name, recommend=True).order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        else:
            works_list = WorkList.query.filter_by(composer=name)\
                .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
    
    # default to recommended works if no search or filter present
    else:
        works_list = WorkList.query.filter_by(composer=name, recommend=True)\
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = []
        response = jsonify(response_object)
        return response

    # get the user's liked works
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    if user_id:
        liked_works = db.session.query(WorkList.id).join(WorkAlbums).join(AlbumLike)\
            .filter(AlbumLike.user_id == user_id, WorkList.composer == name).all()
    else:
        liked_works = []

    # create list of liked work ids
    liked_works_ids = []
    for (item,) in liked_works:
        liked_works_ids.append(item)

    # generate works list for JSON response
    works_by_genre = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre  # for display
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/favoriteworks/<name>', methods=['GET'])  # used in favorites mode
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
        response_object['works'] = []
        response = jsonify(response_object)
        return response

    # generate works list
    liked_works_ids = [work.id for work in works_list]
    works_by_genre = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/worksbygenre', methods=['POST'])  # used in radio mode for populating work list
def get_worksbygenre():
    # get selected genres
    payload = request.get_json()

    genre_list = []
    for genre in payload['genres']:
        genre_list.append(genre['value'])

    work_filter = payload['filter']
    search_term = payload['search']
    artist_name = payload['artist']
    radio_type = payload['radio_type']

    # get composers selected from session
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

    # create the base query
    query = db.session.query(WorkList)

    # filter the query based on the composer list
    query = query.filter(WorkList.composer.in_(composer_list))

    # filter the query based on the artist name
    if artist_name:
        query = query.join(Artists).filter(Artists.name == artist_name)

    # filter the query based on the genre list
    if genre_list[0] != "all":
        conditions = []
        for genre in genre_list:
            conditions.append(WorkList.genre.ilike('%{}%'.format(genre)))
            conditions.append(WorkList.search.ilike('%{}%'.format(genre)))
            conditions.append(WorkList.title.ilike('%{}%'.format(genre)))
            conditions.append(WorkList.nickname.ilike('%{}%'.format(genre)))
        
        query = query.filter(or_(*conditions))

    # filter the query based on the work filter value
    filter_map = {
        "all": WorkList.album_count > 0,
        "recommended": WorkList.recommend == True,
        "obscure": and_(or_(WorkList.recommend == None, WorkList.recommend != True), WorkList.album_count > 0)
    }

    query_filter = filter_map.get(work_filter)
    query = query.filter(query_filter)

    # order the query results by genre and id
    works_list = query.order_by(WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = []
        response_object['playlist'] = []
        response = jsonify(response_object)
        return response

    # get liked works and filter out others if in favorites mode
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        user_id = None

    liked_works = query.join(WorkAlbums).join(AlbumLike)\
        .order_by(WorkList.genre, WorkList.id)\
        .filter(AlbumLike.user_id == user_id).all()

    if radio_type == "favorites" and user_id:
        works_list = liked_works

    liked_works_ids = []
    for work in liked_works:
        liked_works_ids.append(work.id)

    # further filter results by search term if present
    if search_term:
        pattern = re.compile(search_term, re.IGNORECASE)
        return_list = [work for work in works_list if pattern.search(unidecode(str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)))]

        if not return_list:
            response_object = {'status': 'success'}
            response_object['works'] = []
            response_object['playlist'] = []
            response = jsonify(response_object)
            return response
        else:
            works_list = return_list

    # generate works list
    works_by_genre = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = works_list  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/exportplaylist', methods=['POST'])  # used in radio mode
# @login_required
def exportplaylist():
    # get genres
    payload = request.get_json()

    genre_list = []
    for genre in payload['genres']:
        genre_list.append(genre['value'])

    work_filter = payload['filter']
    search_term = payload['search']
    limit = payload['limit']
    name = payload['name']
    prefetch = payload['prefetch']
    random_album = payload['random']
    performer = payload['performer']
    radio_type = payload['radio_type']

    # get composers selected
    if not session.get('radio_composers'):
        composer_list = cache.get('composers')  # for dev server testing
        user_id = 85
    else:
        composer_list = session['radio_composers']
        user_id = current_user.id

    if prefetch:

        # create the base query
        query = db.session.query(WorkAlbums)

        # filter the query based on the composer list
        query = query.filter(WorkList.composer.in_(composer_list))

        # filter based on performer
        if performer:
            query = query.join(Artists).filter(Artists.name == performer)
            # query = query.filter(WorkAlbums.artists.ilike('%{}%'.format(performer)))

        # filter the query based on the genre list
        if genre_list[0] != "all":
            conditions = []
            for genre in genre_list:
                conditions.append(WorkList.genre.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.search.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.title.ilike('%{}%'.format(genre)))
                conditions.append(WorkList.nickname.ilike('%{}%'.format(genre)))
            
            query = query.join(WorkList).filter(or_(*conditions))
        else:
            query = query.join(WorkList)

        if search_term: 
            conditions2 = []
            conditions2.append(WorkList.genre.ilike('%{}%'.format(search_term)))
            conditions2.append(WorkList.search.ilike('%{}%'.format(search_term)))
            conditions2.append(WorkList.title.ilike('%{}%'.format(search_term)))
            conditions2.append(WorkList.nickname.ilike('%{}%'.format(search_term)))
            conditions2.append(WorkList.cat.ilike('%{}%'.format(search_term)))
            query = query.filter(or_(*conditions2))

        # filter the query based on the work filter value
        filter_map = {
            "all": WorkList.album_count > 0,
            "recommended": WorkList.recommend == True,
            "obscure": and_(or_(WorkList.recommend == None, WorkList.recommend != True), WorkList.album_count > 0)
        }

        query_filter = filter_map.get(work_filter)
        query = query.filter(query_filter)

        # filter out favorites or limited albums
        if radio_type == 'favorites': 
            query = query.filter(AlbumLike.user_id == user_id, WorkList.album_count > 0, WorkAlbums.hidden != True)
        else:
            query = query.filter(WorkList.album_count > 0, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)

        # order the query results
        query = query.outerjoin(AlbumLike)\
            .group_by(WorkAlbums.id)\
            .order_by(WorkList.genre, WorkList.id, func.count(AlbumLike.id).desc(), WorkAlbums.score.desc())

        # execute
        sql = query.statement.compile(compile_kwargs={"literal_binds": True})
        # explain = db.session.execute(f'EXPLAIN {sql}').all()
        print(sql)

        album_list = query.all()

        if not album_list:
            abort(404)

        hold_albums = []
        best_albums = []
        prev_album_workid = ""
        for album in album_list:
            if album.workid == prev_album_workid:
                if random_album:  # for randomizing albums
                    hold_albums.append(album)
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
                    best_albums.append(album)
                    prev_album_workid = album.workid

        # last replacement
        if random_album and len(best_albums) > 0 and len(hold_albums) > 0:
            integer = random.randint(0, len(hold_albums) - 1)  # replace with random
            best_albums[-1] = hold_albums[integer]
    
        tracklist = []
        for album in best_albums:
            album = json.loads(album.data)

            for track in album['tracks']:
                tracklist.append(track[1])

        print("DONE")

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
#@cache.cached(query_string=True)
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
#@cache.cached(query_string=True)
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
#@cache.cached()
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

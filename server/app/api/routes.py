from app import db, sp, cache, storage_client
from flask import jsonify, request, session, abort, current_app
from flask_login import current_user, login_required
from config import Config
from app.functions import prepare_composers, group_composers_by_region, group_composers_by_alphabet
from app.functions import prepare_works, prepare_works_with_durations
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike, Artists, Performers, performer_albums
from app.models import ArtistList, User
from sqlalchemy import func, text, or_, and_
from app.api import bp
from unidecode import unidecode
import json
import random
import re
import time


@bp.route('/api/userdata', methods=['GET'])  # main composer list
def get_userdata():
    if current_user.is_authenticated:
        new_posts = current_user.new_posts()
        if new_posts < 1:
            new_posts = None
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
        user = db.session.query(User).filter_by(id=user_id).first()
        new_posts = user.new_posts()
        if new_posts < 1:
            new_posts = None
    else:
        new_posts = None

    response_object = {'status': 'success'}
    response_object['new_posts'] = new_posts
    response = jsonify(response_object)
    return response


@bp.route('/api/omnisearch', methods=['GET'])  # main composer list
def omnisearch():
    # Start the timer
    start_time = time.time()

    # look for search term or filter term
    search_item = request.args.get('search')
    search_terms = search_item.split()

    search_words = [term for term in search_terms if not term.isdigit()]
    search_nums = [int(term) for term in search_terms if term.isdigit()]

    # first search for composers if word search term is present
    if search_words:
        query = db.session.query(ComposerList)

        conditions = []
        for word in search_words:
            conditions.append(ComposerList.name_norm.ilike('{}%'.format(word)))
        for word in search_words:
            conditions.append(ComposerList.name_short.ilike('{}%'.format(word)))
        
        composer_list = query.filter(or_(*conditions), ComposerList.catalogued == True).limit(10).all()  
    else:
        composer_list = [] 
    
    if len(composer_list) < 1:
        composers = []
    else:
        composers = prepare_composers(composer_list)

    # search for works
    # filter by composers if relevant
    conditions = []
    composer_array = []
    if composers:
        for composer in composers:
            composer_array.append(composer['name_full'])
            conditions.append(WorkList.composer == composer['name_short'])

    works_list = WorkList.query.filter(or_(*conditions), WorkList.album_count > 0).order_by(WorkList.album_count.desc()).all()
 
    return_works = []
    i = 0
    for work in works_list:
        search_string = str(work.composer) + str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
        j = 0
        for word in search_words:
            if word.lower() in unidecode(search_string.lower()):
                j += 1
        for num in search_nums:
            pattern = r'(?<!\d)' + str(num) + r'(?!\d)'
            match = re.search(pattern, search_string)
            if match:
                j += 1
        if j == len(search_terms):
            return_works.append(work)
            i += 1
        if i > 10:
            break

    # moved to javascript
    # artists = db.session.query(ArtistList).first()
    # artist_list = json.loads(artists.content)

    # return_list = []
    # i = 0
    # pattern = r"\b" + search_item.lower() + r"\w*"
    # for artist in artist_list:
    #     match = re.search(pattern, unidecode(artist.lower()))
    #     if match:
    #         if artist not in composer_array: # remove composers from performers list
    #             return_list.append(artist.strip())
    #         i += 1
    #     if i > 10:
    #         break

    # Calculate the time taken
    end_time = time.time()
    time_taken = end_time - start_time

    # Print the time taken
    print('Time taken:', time_taken)
   
    # return response
    response_object = {'status': 'success'}
    response_object['composers'] = composers
    response_object['works'] = return_works
    # response_object['artists'] = return_list
    response_object['query_time'] = time_taken
    response = jsonify(response_object)
    return response


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
            '1': ComposerList.query.filter_by(tier=1, catalogued=True),
            '2': ComposerList.query.filter_by(tier=2, catalogued=True),
            '3': ComposerList.query.filter_by(tier=3, catalogued=True),
            '4': ComposerList.query.filter_by(tier=None, catalogued=True),
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

    # get genres list (for radio)
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
@cache.cached()
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
        search_terms = search.split()

        search_words = [term for term in search_terms if not term.isdigit()]
        search_nums = [int(term) for term in search_terms if term.isdigit()]

        works_list = WorkList.query.filter(WorkList.composer == name, WorkList.album_count > 0)\
            .order_by(WorkList.order, WorkList.genre, WorkList.id).all()
     
        return_list = []
        for work in works_list:
            search_string = str(work.composer) + str(work.genre) + str(work.cat) + str(work.suite) + str(work.title) + str(work.nickname) + str(work.search)
            j = 0
            for word in search_words:
                if word.lower() in unidecode(search_string.lower()):
                    j += 1
            for num in search_nums:
                pattern = r'(?<!\d)' + str(num) + r'(?!\d)'
                match = re.search(pattern, search_string)
                if match:
                    j += 1
            if j == len(search_terms):
                return_list.append(work)

        works_list = return_list

    # next filter on filter item if present
    elif filter_method:
        if filter_method == "recommended":
            works_list = WorkList.query.filter_by(composer=name, recommend=True).order_by(WorkList.order, WorkList.genre, WorkList.id).all()
        else:
            works_list = WorkList.query.filter(WorkList.composer == name, WorkList.album_count > 0)\
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
    works_by_genre, playlist = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre  # for display
    response_object['playlist'] = playlist  # for back and previous playing
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
        .filter(AlbumLike.user_id == user_id, WorkList.composer == name)\
        .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    if not works_list:
        response_object = {'status': 'success'}
        response_object['works'] = []
        response = jsonify(response_object)
        return response

    # generate works list
    liked_works_ids = [work.id for work in works_list]
    works_by_genre, playlist = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = playlist  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/radioworks', methods=['POST'])  # used in radio mode for populating work list
def get_radioworks():
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
    works_by_genre, playlist = prepare_works(works_list, liked_works_ids)

    # return response
    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = playlist  # for back and previous playing
    response = jsonify(response_object)
    return response


@bp.route('/api/exportplaylist', methods=['POST'])  # used in radio mode
def exportplaylist():
    if current_user.is_authenticated:
        user_id = current_user.id
    elif Config.MODE == 'DEVELOPMENT':
        user_id = 85  # 85
    else:
        abort(401)

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

    # build the database query while user types in playlist name
    if prefetch:

        # create the base query
        query = db.session.query(WorkAlbums.workid, WorkAlbums.data)

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

        # filter the query based on the work obscurity filter value
        filter_map = {
            "all": WorkList.album_count > 0,
            "recommended": WorkList.recommend == True,
            "obscure": or_(WorkList.recommend == None, WorkList.recommend != True)
        }

        query_filter = filter_map.get(work_filter)
        query = query.filter(query_filter)

        # filter out favorites or limited albums
        if radio_type == 'favorites': 
            query = query.filter(AlbumLike.user_id == user_id, WorkList.album_count > 0, WorkAlbums.hidden != True)
        else:
            query = query.filter(WorkList.album_count > 0, WorkAlbums.hidden != True, WorkAlbums.album_type != "compilation", WorkAlbums.work_track_count <= limit)

        # order the query results either randomly or top album for each work
        query = query.outerjoin(AlbumLike).group_by(WorkAlbums.id)

        if random_album:
            query = query.order_by(WorkList.genre, WorkList.id, func.random())
        else:
            query = query.order_by(WorkList.genre, WorkList.id, func.count(AlbumLike.id).desc(), WorkAlbums.album_type, WorkAlbums.score.desc())

        # make subquery and get first album of each work
        t = query.subquery('t')
        query = db.session.query(t).group_by(t.c.workid)

        # execute the query
        album_list = query.all()

        if not album_list:
            abort(404)

        # Get album tracks
        tracklist = []
        for album in album_list:
            album = json.loads(album.data)

            for track in album['tracks']:
                tracklist.append(track[1])

        cache.set('tracks', tracklist)

        # return response
        response_object = {'status': 'success'}
        response_object['track_count'] = len(tracklist)
        response = jsonify(response_object)

        return response

    # submit to Spotify when user presses submit
    if Config.MODE == "DEVELOPMENT":
        session['spotify_token'] = cache.get('token')  # store in cache for dev
        user_id = '12173954849'
    else:
        user_id = current_user.username
    
    tracklist = cache.get('tracks')

    try:
        response = sp.create_playlist(name, user_id)
        playlist_id = response.json()['id']
    except Exception:
        return response.json()

    # send in batches of 50 tracks to Spotify
    uristring = ""
    response = None
    for k, track in enumerate(tracklist):
        track = "spotify:track:" + track + ","
        uristring = uristring + track
        if (k + 1) % 50 == 0 or k == len(tracklist) - 1:
            response = sp.add_to_playlist(playlist_id, uristring)
            uristring = ""

    return response.json()


@bp.route('/api/albums/<work_id>', methods=['GET'])  # retrieves albums for a given work
def get_albums(work_id):
    page = request.args.get('page', 1, type=int)

    # get filter and search arguments
    artist_name = request.args.get('artist')
    sort = request.args.get('sort')
    limit = request.args.get('limit', default=100)
    favorites = request.args.get('favorites', default=None)

    # base query
    query = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total'))\
        .outerjoin(AlbumLike).group_by(WorkAlbums.id)

    # filter by criteria
    query = query.filter(WorkAlbums.workid == work_id, 
                         WorkAlbums.hidden != True, 
                         WorkAlbums.work_track_count <= limit)

    # filter by user favorites, if present
    if favorites:
        if current_user.is_authenticated:
            user_id = current_user.id
        elif Config.MODE == 'DEVELOPMENT':
            user_id = 85
        else:
            user_id = None
        query = query.filter(AlbumLike.user_id == user_id)

    # make subquery
    t = query.subquery('t')
    query = db.session.query(t)

    # filter by artist, if present. Allow compilation albums if artist mode
    if artist_name:
        # new Performers table
        temp = query\
            .select_from(t.join(performer_albums, t.c.id == performer_albums.c.album_id))\
            .join(Performers, performer_albums.c.performer_id == Performers.id)\
            .filter(Performers.name == artist_name)
        
        # use old Artists table if no results
        test_query = temp.all()
        if len(test_query) < 1:
            query = query.join(Artists).filter(Artists.name == artist_name)
        else:
            query = temp
    
    elif favorites:
        # allow compilation albums in user favorites
        pass
    
    else:
        # disallow compilation albums unless user favorited
        query = query.filter(or_(t.c.album_type != "compilation", t.c.total > 0))

    # sort the results. Album type sort rates albums ahead of compilations and singles
    query = query.order_by(t.c.total.desc(), t.c.album_type, t.c.score.desc())

    # execute the query
    albums = query.all()

    if not albums:
        response_object = {'status': 'error'}
        response_object['albums'] = []
        response = jsonify(response_object)
        return response

    # artist list
    work_artists = db.session.query(Performers.name, func.count(Performers.id).label('total')) \
        .join(performer_albums)\
        .join(WorkAlbums)\
        .filter(WorkAlbums.workid == work_id)\
        .group_by(Performers.id)\
        .order_by(text('total DESC'), Performers.name).all()

    # remove composer from list of artists (assume to be first)
    if len(work_artists) > 1:
        work_artists.pop(0)

    # get artists from old Artists table if no results
    if len(work_artists) < 1:
        work_artists = db.session.query(Artists.name, func.count(Artists.count).label('total')) \
            .filter(Artists.workid == work_id).group_by(Artists.name) \
            .order_by(text('total DESC'), Artists.name).all()  # hidden or compilation???

    # put artists in dictionary
    artist_list = {}
    artist_list.update(work_artists)

    # decode JSON album data and prepare JSON
    album_list = []
    duplicates_set = set()
    match_string = ""

    for album in albums:
        item = json.loads(album.data)
        item['likes'] = album.total
        item['id'] = album.id
        item['img_big'] = album.img
        item['label'] = album.label
        item['track_count'] = album.track_count
        item['composer'] = album.composer
        item['duration'] = album.duration

        # de-rate newer, crappy albums
        if item['track_count']:
            if item['track_count'] > 50 and int(item['release_date'][0:4]) > 2019:
                item['score'] = item['score'] / 4

        # # filter out repeat albums
        artists_string = "".join(sorted(re.sub(r'[^\w\s]', '', item['artists']).replace(" ", "").lower()))

        if artist_name:  # return more repeat results for performer filter (allow distinct years)
            match_string = artists_string + str(item['release_date'])
        else:  # return more unique artists otherwise
            match_string = artists_string

        # do not include in album list if duplicate, unless it has favorites
        if match_string in duplicates_set:
            if(album.total == 0):
                continue
        else:
            duplicates_set.add(match_string)
        # add to album list
        album_list.append(item)

        # order so that conductor before orchestra
        orchestra_list = ['baroque', 'augsburger', 'antiqua', 'milano', 'quartet', 'orchest', 'philharm', 'symphony', 'concert', 'chamber', 'academy', 'staats', 'consort', 'symphoniker', 'covent garden', 'choir', 'akademie', 'stuttgart', 'llscher']
        two_artists = item['artists'].split(', ')

        for term in orchestra_list:
            if term.lower() in two_artists[0].lower():
                two_artists.reverse()
                item['artists'] = ", ".join(two_artists)
                break
        
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
        albumlikes = db.session.query(AlbumLike.album_id)\
            .filter(AlbumLike.user_id == current_user.id, 
                    AlbumLike.album_id.ilike(search)).all()
    elif Config.MODE == 'DEVELOPMENT':
        albumlikes = db.session.query(AlbumLike.album_id)\
            .filter(AlbumLike.user_id == '85', 
                    AlbumLike.album_id.ilike(search)).all()
    else:
        albumlikes = []

    liked_albums = [album.album_id for album in albumlikes]

    # return response
    response_object = {'status': 'success'}
    response_object['albums'] = sorted_list
    response_object['artists'] = artist_list
    response_object['liked_albums'] = liked_albums

    if sorted_list:
        composer = ComposerList.query.filter_by(name_short=sorted_list[0]['composer']).first()
        return_composer = prepare_composers([composer])
        response_object['composer'] = return_composer

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
# @cache.cached(query_string=True)
def get_workinfo(work_id):
    work = db.session.query(WorkList)\
        .filter(WorkList.id == work_id).first()

    if work.genre == "Opera" or work.genre == "Stage Work" or work.genre == "Ballet":
        file_name = 'headers/' + work.title + '.jpg'  # use for image
    elif "piano concerto" in work.title.lower():
        file_name = 'headers/' + 'pianoconcerto' + '.jpg'
    else:
        file_name = 'headers/' + work.genre.split()[0] + '.jpg'  # use for image

    def file_exists():
        bucket = storage_client.get_bucket('composer-explorer.appspot.com')
        blob = bucket.blob(file_name)
        return blob.exists()

    if file_exists():
        work.search = current_app.config['STATIC'] + file_name
    else:
        work.search = current_app.config['STATIC'] + 'headers/' + 'Orchestral' + '.jpg'

    response_object = {'status': 'success'}
    response_object['info'] = work
    response = jsonify(response_object)
    return response


@bp.route('/api/albuminfo/<album_id>', methods=['GET'])
# @cache.cached(query_string=True)
def get_albuminfo(album_id):
    result = db.session.query(WorkAlbums, ComposerList.name_full)\
        .join(ComposerList)\
        .filter(WorkAlbums.id == album_id)\
        .all()

    for album, composer_name in result:
        album_details = json.loads(album.data)
        composer_name = composer_name

    # query new artist table first
    artists = Performers.query.join(performer_albums).join(WorkAlbums)\
        .filter(WorkAlbums.id == album_id).all()

    # retrive from old artist table if no record in new
    if not artists:
        artists = db.session.query(Artists)\
                .filter(Artists.album_id == album_id)\
                .all()

    # remove composer from artist list
    if len(artists) > 1:
        for artist in artists:
            if artist.name == composer_name:
                artists.remove(artist)

    ALBUM = {
        'composer': album.composer,
        'id': album.id,
        'album_img': album_details['album_img'],
        'img_big': album.img,
        'album_name': album_details['album_name'],
        'album_uri': album_details['album_uri'],
        'all_artists': album_details['all_artists'],
        'artists': album_details['artists'],
        'minor_artists': album_details['minor_artists'],
        'release_date': album_details['release_date'],
        'tracks': album_details['tracks'],
        'track_count': album_details['track_count'],
        'artist_details': artists,
    }

    # order so that conductor before orchestra
    orchestra_list = ['baroque', 'augsburger', 'antiqua', 'milano', 'quartet', 'orchest', 'philharm', 'symphony', 'concert', 'chamber', 'academy', 'staats', 'consort', 'symphoniker', 'covent garden', 'choir', 'akademie', 'stuttgart', 'llscher']
    two_artists = ALBUM['artists'].split(', ')

    for term in orchestra_list:
        if term.lower() in two_artists[0].lower():
            two_artists.reverse()
            ALBUM['artists'] = ", ".join(two_artists)
            break

    response_object = {'status': 'success'}
    response_object['album'] = ALBUM
    response = jsonify(response_object)
    return response


@bp.route('/api/artistcomposers/<artist_name>', methods=['GET'])  # for performer mode composers
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


@bp.route('/api/artistworks', methods=['GET'])  # for performer mode works
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

    liked_works_ids = []
    for album in liked_albums:
        liked_works_ids.append(album.workid)

    # generate works list
    works_by_genre, playlist = prepare_works(works_list, liked_works_ids)

    response_object = {'status': 'success'}
    response_object['works'] = works_by_genre
    response_object['playlist'] = playlist
    response = jsonify(response_object)
    return response


@bp.route('/api/artistlist', methods=['GET'])  # artist list for performer view
#@cache.cached()
def get_artistlist():
    # artists = db.session.query(ArtistList).first()
    # artist_list = artists.content

    # response_object = {'status': 'success'}
    # response_object['artists'] = artist_list
    # response = jsonify(response_object)
    # return response

    i = 0
    artist_list = []

    artists = db.session.query(Performers.name, Performers.img, Performers.description, func.count(Performers.id).label('total'))\
        .join(performer_albums)\
        .filter(or_(Performers.hidden == False, Performers.hidden == None))\
        .group_by(Performers.id).order_by(text('total DESC')).all()

    composers = db.session.query(ComposerList.name_full).all()

    composer_names = set(composer for (composer,) in composers)

    # remove composers and bad results
    for artist, img, description, count in artists:
        if artist not in composer_names and "/" not in artist:
            artist_list.append({'name': artist, 'img': img, 'description': description})
        # if i < 100:
        #     print(item[0] + " " + str(item[1]))
        # i += 1

    response_object = {'status': 'success'}
    response_object['artists'] = artist_list
    response = jsonify(response_object)
    return response


@bp.route('/api/topartists', methods=['GET'])  # used to build json list for word cloud
@login_required
def get_topartists():
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
        flag = False

    response = jsonify(artist_list)
    return response

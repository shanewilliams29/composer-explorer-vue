from app import db, sp, cache
from flask import jsonify, request, session, abort, current_app
from flask_login import current_user
from config import Config
from app.functions import prepare_composers, group_composers_by_region, group_composers_by_alphabet, is_image_url_alive
from app.functions import prepare_works, retrieve_artist_list_from_db
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike, Performers, performer_albums
from app.models import User
from sqlalchemy import func, text, or_, and_
from app.api import bp
from unidecode import unidecode
import json
import re


@bp.route('/api/getperformer', methods=['GET'])  # get performer details from id
def get_performer(): 
    performer_id = request.args.get('id')

    performer = db.session.get(Performers, performer_id)

    if not performer:
        response_object = {'status': 'error'}
        response_object['message'] = 'performer not found for id'
        response = jsonify(response_object)
        return response

    response_object = {'status': 'success'}
    response_object['artist'] = performer
    response = jsonify(response_object)
    return response


@bp.route('/api/getperformerbyname', methods=['GET'])  # get performer details from id
def get_performerbyname():
    performer_name = request.args.get('name')

    performer = Performers.query.filter_by(name=performer_name).first()

    if not performer:
        response_object = {'status': 'error'}
        response_object['message'] = 'performer not found for name'
        response = jsonify(response_object)
        return response

    response_object = {'status': 'success'}
    response_object['artist'] = performer
    response = jsonify(response_object)
    return response


@bp.route('/api/getalbumworks', methods=['GET'])  # work list for selected album in albums view
def get_albumworks():
    album_id = request.args.get('album_id')
    works = db.session.query(WorkList, WorkAlbums.data, func.count(AlbumLike.id).label('total'))\
        .select_from(WorkAlbums)\
        .filter(WorkAlbums.album_id == album_id)\
        .join(WorkList)\
        .outerjoin(AlbumLike, WorkAlbums.id == AlbumLike.album_id)\
        .group_by(WorkAlbums.id)\
        .order_by(WorkList.id).all()
    
    temp_list = []
    for (work, data, likes) in works:
        temp_list.append([work, json.loads(data), likes])

    works_list = []
    for [work, data, likes] in temp_list:
        data['likes'] = likes
        data['id'] = work.id + data['album_id']
        works_list.append([work, data])

    search = "%{}%".format(album_id)

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

    response_object = {'status': 'success'}
    response_object['works'] = works_list
    response_object['liked_albums'] = liked_albums
    response = jsonify(response_object)
    return response


@bp.route('/api/getonealbum', methods=['GET'])  # used in links to albums
def get_onealbum():
    album_id = request.args.get('id')

    # get workalbums for album id
    albums = [db.session.query(WorkAlbums).filter(WorkAlbums.album_id == album_id).first()]

    if not albums:
        response_object = {'status': 'error'}
        response_object['albums'] = []
        response = jsonify(response_object)
        return response

    # decode JSON album data and prepare JSON
    album_list = []

    for album in albums:
        item = json.loads(album.data)
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
        
    # sort the album list on score
    sorted_list = sorted(album_list, key=lambda d: d['score'], reverse=True)

    # return response
    response_object = {'status': 'success'}
    response_object['albums'] = sorted_list

    if sorted_list:
        composer = ComposerList.query.filter_by(name_short=sorted_list[0]['composer']).first()
        return_composer = prepare_composers([composer])
        response_object['composer'] = return_composer

    response = jsonify(response_object)
    return response


@bp.route('/api/albumsview', methods=['GET'])  # populates AlbumsView with albums
#@cache.cached(query_string=True)
def get_albumsview():
    page = request.args.get('page', 1, type=int)
    composer_name = request.args.get('composer')
    artist_name = request.args.get('artist')
    era = request.args.get('period')
    work_title = request.args.get('work')
    sort = request.args.get('sort', default='popular')
    works_list = []

    # base query
    query = db.session.query(WorkAlbums)
    query = query.filter(WorkAlbums.hidden != True, 
                         WorkAlbums.img != None, 
                         WorkAlbums.track_count <100,
                         WorkAlbums.album_type != "compilation")
    
    # filter on composer if present
    if composer_name and composer_name != "all":
        query = query.filter(WorkAlbums.composer == composer_name)

        # get works list for composer
        works = db.session.query(WorkList.title)\
            .filter(WorkList.composer == composer_name)\
            .order_by(WorkList.title).distinct()
        works_list = [work for (work,) in works]

    # filter on era if present
    if era and era != "all":
        eras = {
            'common': (1500, 1907),
            'early': (1000, 1600),
            'baroque': (1550, 1725),
            'classical': (1711, 1800),
            'romantic': (1770, 1875),
            '20th': (1850, 2051),
        }
        datemin, datemax = eras.get(era)
        query = query.join(ComposerList).filter(ComposerList.born >= datemin, ComposerList.born < datemax)

        # get works list for era
        works = db.session.query(WorkList.title)\
            .join(ComposerList, ComposerList.name_short == WorkList.composer)\
            .filter(ComposerList.born >= datemin, ComposerList.born < datemax)\
            .order_by(WorkList.title).distinct()
        works_list = [work for (work,) in works]
    
    # filter on artist if present
    if artist_name:
        query = query.join(performer_albums).join(Performers)\
            .filter(Performers.name == artist_name)

    # filter on work if present
    if work_title:
        query = query.join(WorkList)\
            .filter(WorkList.title == work_title)

    # sort and get the results. limit cases where many albums.
    if not composer_name and not artist_name and not work_title:
        query = query.order_by(WorkAlbums.score.desc())
        albums = query.limit(page * 400).all()
    else:
        # will be sorted below
        albums = query.all()

    if not albums:
        response_object = {'status': 'error'}
        response_object['albums'] = []
        response_object['works'] = []
        response = jsonify(response_object)
        return response

    # decode JSON album data and prepare JSON
    album_list = []
    duplicates_set = set()

    for album in albums:
        item = json.loads(album.data)
        item['id'] = album.id
        item['album_id'] = album.album_id
        item['img_big'] = album.img
        item['label'] = album.label
        item['track_count'] = album.track_count
        item['composer'] = album.composer
        item['duration'] = album.duration

        # de-rate newer, crappy albums
        if item['track_count']:
            if item['track_count'] > 50 and int(item['release_date'][0:4]) > 2019:
                item['score'] = item['score'] / 4

        # get unique albums only
        if item['album_id'] in duplicates_set:
            continue
        else:
            duplicates_set.add(item['album_id'])

        album_list.append(item)

    # apply sorting
    if sort == 'popular':
        sorted_list = sorted(album_list, key=lambda d: d['score'], reverse=True)
    elif sort == 'newest':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'], reverse=True)
    elif sort == 'oldest':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'])
    else:
        # sort the album list on score
        sorted_list = sorted(album_list, key=lambda d: d['score'], reverse=True)

    # return paginated items
    results_per_page = 50
    list_start = page * results_per_page - results_per_page
    list_end = page * results_per_page

    sorted_list = sorted_list[list_start:list_end]

    # return response
    response_object = {'status': 'success'}
    response_object['albums'] = sorted_list
    response_object['works'] = works_list
    response = jsonify(response_object)
    return response


@bp.route('/api/workslist', methods=['GET'])  # work list for album view search dropdown
@cache.cached()
def get_workslist():
    works_list = []

    works = db.session.query(WorkList.title).order_by(WorkList.album_count.desc()).distinct()

    works_list = [work for (work,) in works]

    response_object = {'status': 'success'}
    response_object['works'] = works_list
    response = jsonify(response_object)
    return response


@bp.route('/api/userdata', methods=['GET'])
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


@bp.route('/api/elasticsearch', methods=['GET'])
def elasticsearch():

    def match_beginning_of_words(string, word_beginning):
        pattern = r'\b' + word_beginning  # '\b' matches at the boundary (beginning) of a word
        matches = re.findall(pattern, string, re.IGNORECASE)
        return matches

    def search_artists(search_words):
        artist_list = cache.get('artists') or retrieve_artist_list_from_db()
        cache.set('artists', artist_list)

        exclusion_list = ['symphony', 'quartet', 'concerto']

        all_artist_matches = [item for item in artist_list for word in search_words if unidecode(word.lower()) in unidecode(item['name'].lower()) and unidecode(word.lower()) not in exclusion_list]

        return refine_artists(all_artist_matches, search_words)

    def refine_artists(all_artist_matches, search_words):
        artist_duplicate_ids = set()
        return_artists = []
        for artist in all_artist_matches:
            if artist['id'] in artist_duplicate_ids:
                continue

            artist_duplicate_ids.add(artist['id'])
            if any(match_beginning_of_words(unidecode(artist['name'].lower()), unidecode(word)) for word in search_words):
                return_artists.append(artist)

        return return_artists[:10]

    def refine_albums(albums):
        albums_no_duplicates = []
        duplicates_set = set()

        for album in albums:
            if len(albums_no_duplicates) >= 10:
                break

            if album.album_id not in duplicates_set:
                albums_no_duplicates.append(album)
                duplicates_set.add(album.album_id)

        return albums_no_duplicates
    
    # search terms
    q = unidecode(request.args.get('search')).lower()
    search_terms = q.split()

    # composers
    composer_list, total = ComposerList.elasticsearch(q, 1, 10)
    composers = prepare_composers(composer_list) if composer_list else []

    # works
    works, total = WorkList.elasticsearch(q, 1, 1000, 'album_count')

    # artists
    artists = search_artists(search_terms)

    # albums
    albums, total = WorkAlbums.elasticsearch(q, 1, 1000, 'score')
    albums = refine_albums(albums)

    # response
    response_object = {'status': 'success', 
                       'composers': composers, 
                       'works': works[:10], 
                       'artists': artists, 
                       'albums': albums}

    return jsonify(response_object)

# old omnisearch, not used. use api/elasticsearch instead
@bp.route('/api/omnisearch', methods=['GET'])  
def omnisearch():
    def match_beginning_of_words(string, word_beginning):
        pattern = r'\b' + word_beginning  # '\b' matches at the boundary (beginning) of a word
        matches = re.findall(pattern, string, re.IGNORECASE)
        return matches

    def search_composers(search_words):
        if not search_words:
            return []

        conditions = []
        for word in search_words:
            conditions.append(ComposerList.name_norm.ilike('{}%'.format(word)))
            conditions.append(ComposerList.name_short.ilike('{}%'.format(word)))    
        
        composer_list = db.session.query(ComposerList).filter(or_(*conditions), ComposerList.catalogued == True).limit(10).all()

        return prepare_composers(composer_list) if composer_list else []

    def search_works(search_words, search_nums, composers, artists):
        conditions = [WorkList.composer == composer['name_short'] for composer in composers] if composers else []

        works_list = WorkList.query.filter(or_(*conditions), WorkList.album_count > 0).order_by(WorkList.album_count.desc())

        return filter_works(search_words, search_nums, works_list)

    def filter_works(search_words, search_nums, works_list):
        return_works = []

        # remove artists from search words
        composer_list = [unidecode(composer['name_short'].lower()) for composer in composers]
        exclusion_list = ['symphony', 'quartet', 'concerto']
        artist_match = set()

        for word in search_words:
            if unidecode(word.lower()) not in exclusion_list and unidecode(word.lower()) not in composer_list:
                for artist in artists:
                    if unidecode(word.lower()) in unidecode(artist['name'].lower()):
                        artist_match.add(word)
        
        # print("matched with artists: " + str(artist_match))

        keep_items = set()
        if artist_match:
            for work in works_list:
                for item in artist_match:
                    if item in unidecode(work.title.lower()):
                        keep_items.add(item)
                        # print("matched work: " + work.title)

        # print("keep items: " + str(keep_items))
        remove_items = artist_match - keep_items
        # print("remove items: " + str(remove_items))

        if remove_items:
            for item in remove_items:
                try:
                    search_words.remove(item)
                except ValueError:
                    pass
        
        # perform search
        # print("search words to use: " + str(search_words))

        for work in works_list:
            if len(return_works) > 10:
                break

            search_string = " ".join(map(str, [work.composer, work.genre, work.cat, work.suite, work.title, work.nickname, work.search]))

            i = 0
            j = 0
            for word in search_words:
                if match_beginning_of_words(unidecode(search_string), unidecode(word)):
                    i += 1

            for num in search_nums:
                pattern = r'(?<!\d)' + str(num) + r'(?!\d)'
                match = re.search(pattern, search_string)
                if match:
                    j += 1

            if len(search_nums) > 0:
                if j >= 1 and i > len(search_words) - 1:
                    return_works.append(work)
            elif len(composers) > 0 and len(search_words) > 1:
                if i > 1:
                    return_works.append(work)
            else:
                if i > 0:
                    return_works.append(work)
        
        return return_works, remove_items

    def search_artists(search_words):
        artist_list = cache.get('artists') or retrieve_artist_list_from_db()
        cache.set('artists', artist_list)

        exclusion_list = ['symphony', 'quartet', 'concerto']

        all_artist_matches = [item for item in artist_list for word in search_words if unidecode(word.lower()) in unidecode(item['name'].lower()) and unidecode(word.lower()) not in exclusion_list]

        return refine_artists(all_artist_matches, search_words)

    def refine_artists(all_artist_matches, search_words):
        artist_duplicate_ids = set()
        return_artists = []
        for artist in all_artist_matches:
            if artist['id'] in artist_duplicate_ids:
                continue

            artist_duplicate_ids.add(artist['id'])
            if any(match_beginning_of_words(unidecode(artist['name'].lower()), unidecode(word)) for word in search_words):
                return_artists.append(artist)

        return return_artists[:10]

    def search_albums(search_words, composers, artists, works, artist_match):
        if not composers and not artists and not works:
            return []

        conditions = []
        conditions2 = []
        if composers:
            conditions.append(WorkAlbums.composer == composers[0]['name_short'])
        if artist_match:
            conditions.append(Performers.id == artists[0]['id'])
        if works:
            for work in works:
                conditions2.append(WorkAlbums.workid == work.id)

        albums_query = db.session.query(WorkAlbums).join(performer_albums).join(Performers).filter(
            and_(*conditions), 
            or_(*conditions2), 
            WorkAlbums.track_count < 100, 
            WorkAlbums.hidden != True, 
            WorkAlbums.album_type != "compilation"
        ).order_by(WorkAlbums.score.desc())

        return refine_albums(albums_query)

    def refine_albums(albums_query):
        albums_no_duplicates = []
        duplicates_set = set()

        for album in albums_query:
            if len(albums_no_duplicates) >= 10:
                break

            if album.album_id not in duplicates_set:
                albums_no_duplicates.append(album)
                duplicates_set.add(album.album_id)

        return albums_no_duplicates

    search_item = request.args.get('search')
    search_terms = search_item.split()

    search_words = [term for term in search_terms if not term.isdigit()]
    search_nums = [int(term) for term in search_terms if term.isdigit()]

    composers = search_composers(search_words)
    artists = search_artists(search_words)
    works, artist_match = search_works(search_words, search_nums, composers, artists)
    albums = search_albums(search_words, composers, artists, works, artist_match)

    response_object = {'status': 'success', 
                       'composers': composers, 
                       'works': works, 
                       'artists': artists, 
                       'albums': albums}

    return jsonify(response_object)


@bp.route('/api/searchperformers', methods=['GET'])
def searchperformers():

    # look for search term or filter term
    search_item = request.args.get('search')
    search_terms = search_item.split()

    search_words = [term for term in search_terms if not term.isdigit()]

    # search for performers
    artist_list = cache.get('artists')

    # cache miss
    if artist_list is None:
        artist_list = retrieve_artist_list_from_db()
        cache.set('artists', artist_list)

    for word in search_words:
        artist_matches = [item for item in artist_list if word.lower() in unidecode(item['name'].lower())]

    # further refine list of artists to return, match on beginning of word and number of words
    def match_beginning_of_words(string, word_beginning):
        pattern = r'\b' + word_beginning  # '\b' matches at the boundary (beginning) of a word
        matches = re.findall(pattern, string, re.IGNORECASE)
        return matches

    return_artists = []

    for artist in artist_matches:
        matches = []
        search_string = unidecode(artist['name'].lower())
        for word in search_words:
            matches.extend(match_beginning_of_words(search_string, unidecode(word)))
        if len(matches) == len(search_terms):
            return_artists.append(artist)

    first_10_artists = return_artists[:20]
    
    # return response
    response_object = {'status': 'success'}
    response_object['artists'] = first_10_artists
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
    if Config.MODE == "DEVELOPMENT" or Config.SECRET_KEY == 'abcde':
        cache.set('composers', composer_name_list)  # store in cache for dev server and testing

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
        query = query.join(WorkAlbums).join(performer_albums).join(Performers)\
            .filter(Performers.name == artist_name)

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

    if artist_name:
        liked_works = query.join(AlbumLike)\
            .order_by(WorkList.genre, WorkList.id)\
            .filter(AlbumLike.user_id == user_id).all()
    else:
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
            query = query.join(performer_albums).join(Performers)\
                .filter(Performers.name == performer)

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

        # Execute the query
        sorted_albums = query.all()

        # Process the sorted albums in Python
        top_albums_per_work = {}
        for album in sorted_albums:
            workid = album.workid
            if workid not in top_albums_per_work:
                top_albums_per_work[workid] = album

        # Convert the dictionary values to a list
        album_list = list(top_albums_per_work.values())

        if not album_list:
            abort(404)

        # get album tracks
        tracklist = []
        for album in album_list:
            album = json.loads(album.data)

            for track in album['tracks']:
                tracklist.append(track[1])

        # temporarily store tracks in cache
        if Config.MODE == "DEVELOPMENT":
            user_id = '12173954849'
        else:
            user_id = current_user.username

        cache.set(user_id, tracklist)

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
    
    # get tracks from cache
    tracklist = cache.get(user_id)

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
        query = query\
            .select_from(t.join(performer_albums, t.c.id == performer_albums.c.album_id))\
            .join(Performers, performer_albums.c.performer_id == Performers.id)\
            .filter(Performers.name == artist_name)
    
    elif favorites:
        # allow compilation albums in user favorites
        pass
    
    else:
        # disallow compilation albums unless user favorited
        query = query.filter(or_(t.c.album_type != "compilation", t.c.total > 0))

    # sort the results. Album type sort rates albums ahead of compilations and singles
    query = query.order_by(t.c.album_type, t.c.score.desc())

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

    # put artists in dictionary
    artist_list = {}
    artist_list.update(work_artists)

    # get work duration
    (work_duration,) = db.session.query(WorkList.duration).filter(WorkList.id == work_id).first()

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

        if work_duration:
            # determine if full performance or excerpt
            if work_duration > 600000 and album.duration < work_duration / 1.5:
                item['full_performance'] = False
            else:
                item['full_performance'] = True
        else:
            item['full_performance'] = True
            
        # de-rate newer, crappy albums
        if item['track_count']:
            if item['track_count'] > 50 and int(item['release_date'][0:4]) > 2019:
                item['score'] = item['score'] / 4

        # # filter out repeat albums
        artists_string = "".join(sorted(re.sub(r'[^\w\s]', '', item['artists']).replace(" ", "").lower()))

        if artist_name or 'WAGNER' in work_id:  # return more repeat results for performer filter (allow distinct years)
            match_string = artists_string + str(item['release_date'])
        else:  # return more unique artists otherwise
            match_string = artists_string 

        # do not include in album list if duplicate, unless it has favorites
        if match_string in duplicates_set:
            if (album.total == 0):
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
        
    # album sorting
    if sort == 'dateascending':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'])
    elif sort == 'datedescending':
        sorted_list = sorted(album_list, key=lambda d: d['release_date'], reverse=True)
    elif sort == 'durationascending':
        sorted_list = sorted(album_list, key=lambda d: d['duration'])
        sorted_list = sorted(sorted_list, key=lambda d: d['full_performance'], reverse=True)
    elif sort == 'durationdescending':
        sorted_list = sorted(album_list, key=lambda d: d['duration'], reverse=True)
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
        print(user)
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

    response_object = {'status': 'error'}
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
        .filter(WorkList.id == work_id).first_or_404()

    # determine the desired header image filename
    title_lower = work.title.lower()
    if work.genre in ("Opera", "Stage Work", "Ballet"):
        file_name = f"headers_small/{work.title}.jpg"
    elif "piano concerto" in title_lower:
        file_name = "headers_small/pianoconcerto.jpg"
    else:
        file_name = f"headers_small/{work.genre.split()[0]}.jpg"

    base_url = current_app.config['STATIC']
    candidate_url = base_url + file_name
    fallback_url = base_url + "headers_small/Orchestral.jpg"

    # check remote existence
    if is_image_url_alive(candidate_url):
        work.search = candidate_url
    else:
        work.search = fallback_url

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

    # get artists
    artists = Performers.query.join(performer_albums).join(WorkAlbums)\
        .filter(WorkAlbums.id == album_id).all()

    # remove composer from artist list
    if len(artists) > 1:
        for artist in artists:
            if artist.name == composer_name:
                artists.remove(artist)

    ALBUM = {
        'composer': album.composer,
        'id': album.id,
        'album_id': album.album_id,
        'work_id': album.workid,
        'spotify_id': album.album_id,
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
        'label': album.label,
        'artist_details': artists,
    }

    work = db.session.get(WorkList, ALBUM['work_id'])

    # order so that conductor before orchestra
    orchestra_list = ['baroque', 'augsburger', 'antiqua', 'milano', 'quartet', 'orchest', 'philharm', 'symphony', 'concert', 'chamber', 'academy', 'staats', 'consort', 'symphoniker', 'covent garden', 'choir', 'akademie', 'stuttgart', 'llscher']
    two_artists = ALBUM['artists'].split(', ')

    for term in orchestra_list:
        if term.lower() in two_artists[0].lower():
            two_artists.reverse()
            # ALBUM['artists'] = ", ".join(two_artists)
            break

    print_artists = []
    for artist_name in two_artists:
        for artist in artists:
            if artist.name == artist_name:
                print_artists.append({'id': artist.id, 'name': artist.name})

    response_object = {'status': 'success'}
    response_object['album'] = ALBUM
    response_object['work'] = work
    response_object['print_artists'] = print_artists
    response = jsonify(response_object)
    return response


@bp.route('/api/artistcomposers/<artist_id>', methods=['GET'])  # for performer mode composers
def get_artistcomposers(artist_id):

    composers = db.session.query(ComposerList).join(WorkAlbums).join(performer_albums).join(Performers)\
        .filter(Performers.id == artist_id)\
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
    artist_id = request.args.get('artist')
    composer_name = request.args.get('composer')

    works_list = db.session.query(WorkList).join(WorkAlbums).join(performer_albums).join(Performers)\
        .filter(Performers.id == artist_id, WorkList.composer == composer_name)\
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
def get_artistlist():

    artist_list = cache.get('artists')

    # cache miss
    if artist_list is None:
        artist_list = retrieve_artist_list_from_db()
        cache.set('artists', artist_list)

    return_list = []

    for artist in artist_list:
        return_list.append(artist['name'])

    response_object = {'status': 'success'}
    response_object['artists'] = return_list
    response = jsonify(response_object)
    return response


@bp.route('/api/topartists/<artist_type>', methods=['GET'])  # used to build json lists for performance view
def get_topartists(artist_type):

    def get_artists():
        if artist_type == "orchestras":
            return db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, Performers.wiki_link, func.count(Performers.id).label('total'))\
                .join(performer_albums)\
                .filter(or_(Performers.hidden == False, Performers.hidden == None))\
                .filter(or_(Performers.description.ilike('%{}%'.format('orchestra')),
                            Performers.description.ilike('%{}%'.format('quartet'))))\
                .group_by(Performers.id).order_by(text('total DESC')).limit(100).all()

        if artist_type == "conductors":
            return db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, Performers.wiki_link, func.count(Performers.id).label('total'))\
                .join(performer_albums)\
                .filter(or_(Performers.hidden == False, Performers.hidden == None))\
                .filter(Performers.description.ilike('%{}%'.format('conductor')))\
                .group_by(Performers.id).order_by(text('total DESC')).limit(100).all()
        
        if artist_type == "soloists":
            return db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, Performers.wiki_link, func.count(Performers.id).label('total'))\
                .join(performer_albums)\
                .filter(or_(Performers.hidden == False, Performers.hidden == None))\
                .filter(or_(Performers.description.ilike('%{}%'.format('pianist')),
                            Performers.description.ilike('%{}%'.format('violinist'))))\
                .group_by(Performers.id).order_by(text('total DESC')).limit(100).all()
        if artist_type == "vocalists":
            return db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, Performers.wiki_link, func.count(Performers.id).label('total'))\
                .join(performer_albums)\
                .filter(or_(Performers.hidden == False, Performers.hidden == None))\
                .filter(or_(Performers.description.ilike('%{}%'.format('singer')),
                            Performers.description.ilike('%{}%'.format('bass')),
                            Performers.description.ilike('%{}%'.format('baritone')),
                            Performers.description.ilike('%{}%'.format('tenor')),
                            Performers.description.ilike('%{}%'.format('mezzo')),
                            Performers.description.ilike('%{}%'.format('soprano')),
                            Performers.description.ilike('%{}%'.format('vocalist'))))\
                .group_by(Performers.id).order_by(text('total DESC')).limit(100).all()

    def get_composers():
        return db.session.query(ComposerList.name_full).all()

    def is_excluded_artist(artist, composer_list):
        if artist in composer_list:
            return True
        return False

    def create_artist_list(artists, composer_list):
        artist_list = []
        for (_id, name, img, desc, wiki_link, count) in artists:
            if not is_excluded_artist(name, composer_list):
                item = {}
                item['id'] = _id
                item['name'] = name
                item['img'] = img
                item['description'] = desc
                item['wiki_link'] = wiki_link
                artist_list.append(item)
        return artist_list

    artists = get_artists()
    composers = get_composers()
    composer_list = [composer for (composer,) in composers]
    
    artist_list = create_artist_list(artists, composer_list)
    response = jsonify(artist_list)
    return response

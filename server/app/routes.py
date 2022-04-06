from app import app, db
from flask import jsonify, request
from app.models import ComposerList, WorkList, WorkAlbums, AlbumLike
from sqlalchemy import func, text
import json
import jsonpickle


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/api/composers', methods=['GET'])
def get_composers():
    # retrieve composers from database
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
    return jsonify(response_object)


@app.route('/api/works/<name>', methods=['GET'])
def get_works(name):
    # check if composer has been catalogued or return error if not
    try:
        work = WorkList.query.filter_by(composer=name).first_or_404()
    except:
        response_object = {
            'status': 'error',
            'info': 'composer not found in catalogue'
        }
        return jsonify(response_object)

    works_list = WorkList.query.filter_by(composer=name, recommend=True)\
        .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

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
    return jsonify(response_object)


@app.route('/api/albums/<work_id>', methods=['GET'])
def get_albums(work_id):
    page = request.args.get('page', 1, type=int)

    albums = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('total')) \
        .filter(WorkAlbums.workid == work_id, WorkAlbums.hidden != True).outerjoin(AlbumLike).group_by(WorkAlbums) \
        .order_by(text('total DESC'), WorkAlbums.score.desc()).paginate(page, 25, False)

    album_list = []
    for tup in albums.items:
        item = jsonpickle.decode(tup[0].data)
        item['likes'] = tup[1]
        item['hidden'] = tup[0].hidden
        album_list.append(item)

    # split off first 5 tracks for collapsible display
    for item in album_list:
        item['firstfive'] = item['tracks'][:5]
        item['tracks'] = item['tracks'][5:]

    response_object = {'status': 'success'}
    response_object['albums'] = album_list
    return jsonify(response_object)


@app.route('/api/composerinfo/<composer>', methods=['GET'])
def get_composerinfo(composer):
    composer_info = db.session.query(ComposerList)\
        .filter(ComposerList.name_short == composer).first()
    composer_info.image = app.config['STATIC'] + 'img/' + composer + '.jpg'
    response_object = {'status': 'success'}
    response_object['data'] = composer_info
    return jsonify(response_object)

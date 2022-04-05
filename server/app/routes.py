from app import app, db
from flask import jsonify
from app.models import ComposerList, WorkList
import json


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
            'flag': 'https://storage.googleapis.com/composer-explorer.appspot.com/flags/1x1/' + flag + '.svg',
            'img': 'https://storage.googleapis.com/composer-explorer.appspot.com/img/' + composer.name_short + '.jpg',
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


@app.route('/api/albums/<id>', methods=['GET'])
def get_albums(id):
    response_object = {'status': 'success'}
    return jsonify(response_object)
    # check if composer has been catalogued or return error if not

    # try:
    #     work = WorkList.query.filter_by(composer=name).first_or_404()
    # except:
    #     response_object = {
    #         'status': 'error',
    #         'info': 'composer not found in catalogue'
    #     }
    #     return jsonify(response_object)

    # works_list = WorkList.query.filter_by(composer=name, recommend=True)\
    #     .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    # WORKS = []
    # for work in works_list:
    #     info = {
    #         'id': work.id,
    #         'genre': work.genre,
    #         'cat': work.cat,
    #         'recommend': work.recommend,
    #         'title': work.title,
    #         'nickname': work.nickname,
    #         'date': work.date,
    #         'album_count': work.album_count
    #     }
    #     WORKS.append(info)

    # # group onto genres
    # works_by_genre = {}
    # works_in_genre = []
    # i = 0
    # prev_genre = WORKS[i]['genre']

    # while i < len(WORKS):
    #     genre = WORKS[i]['genre']
    #     if genre == prev_genre:
    #         works_in_genre.append(WORKS[i])
    #         i += 1
    #     else:
    #         works_by_genre[prev_genre] = works_in_genre
    #         works_in_genre = []
    #         works_in_genre.append(WORKS[i])
    #         prev_genre = genre
    #         i += 1
    #         if i == len(WORKS):
    #             works_by_genre[prev_genre] = works_in_genre

    # response_object = {'status': 'success'}
    # response_object['works'] = works_by_genre
    # return jsonify(response_object)

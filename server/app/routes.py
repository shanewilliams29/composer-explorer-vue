from app import app, db
from flask import jsonify
from app.models import ComposerList
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
        # map era colours, flags, and region names
        median_age = (composer.died - composer.born) / 2
        median_year = median_age + composer.born
        for era in eras:
            if median_year > era[1]:
                era_color = era[3]
        region_name = region_names[composer.region]
        flag = flags[composer.nationality].lower()

        info = {
            'id': composer.id,
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

    # COMPOSERS = [
    #     {
    #         'id': 3,
    #         'name_full': 'Johann Sebastian Bach',
    #         'born': 1685,
    #         'died': 1750,
    #         'flag': 'https://storage.googleapis.com/composer-explorer.appspot.com/flags/1x1/de.svg',
    #         'img': 'https://storage.googleapis.com/composer-explorer.appspot.com/img/Bach.jpg',
    #         'region': 'A Austria-Germany',
    #         'color': 'gold',
    #         'popular': 'true'
    #     },
    #     {
    #         'id': 1,
    #         'name_full': 'Ludwig van Beethoven',
    #         'born': 1770,
    #         'died': 1827,
    #         'flag': 'https://storage.googleapis.com/composer-explorer.appspot.com/flags/1x1/de.svg',
    #         'img': 'https://storage.googleapis.com/composer-explorer.appspot.com/img/Beethoven.jpg',
    #         'region': 'A Austria-Germany',
    #         'color': 'darkgreen',
    #         'popular': 'true'
    #     },
    #     {
    #         'id': 14,
    #         'name_full': 'Claude Debussy',
    #         'born': 1862,
    #         'died': 1918,
    #         'flag': 'https://storage.googleapis.com/composer-explorer.appspot.com/flags/1x1/fr.svg',
    #         'img': 'https://storage.googleapis.com/composer-explorer.appspot.com/img/Debussy.jpg',
    #         'region': 'B France-Belgium',
    #         'color': 'purple',
    #         'popular': 'true'
    #     }
    # ]

    composers_by_region = {}
    composers_in_region = []
    i = 0
    prev_region = COMPOSERS[i]['region']

    while i < len(COMPOSERS):
        region = COMPOSERS[i]['region']  # Need to convert to display region
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

    response_object = {'status': 'success'}
    response_object['composers'] = composers_by_region
    return jsonify(response_object)

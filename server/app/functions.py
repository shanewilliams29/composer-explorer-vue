import json
from app import storage_client
import requests
from PIL import Image
import io
from flask import current_app
from collections import defaultdict
import random


def prepare_composers(composer_list):

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
            'flag': current_app.config['STATIC'] + 'flags/1x1/' + flag + '.svg',
            'img': current_app.config['STATIC'] + 'img/' + composer.name_short + '.jpg',
            'region': region_name,
            'color': era_color,
            'catalogued': composer.catalogued
        }
        COMPOSERS.append(info)

    return COMPOSERS


def group_composers_by_region(COMPOSERS):
    composers_by_region = defaultdict(list)

    for composer in COMPOSERS:
        region = composer['region']
        composers_by_region[region].append(composer)

    return composers_by_region


def group_composers_by_alphabet(COMPOSERS): 
    composers_by_alphabet = defaultdict(list)

    for composer in COMPOSERS:
        region = composer['name_short'][0].upper()
        composers_by_alphabet[region].append(composer)

    return composers_by_alphabet


def prepare_works(works_list, liked_list):
    WORKS = []
    PLAYLIST = []
    
    i = 0
    for work in works_list:

        info = {
            'index': i,
            'shuffle': random.randint(0, 1000),
            'id': work.id,
            'composer': work.composer,
            'genre': work.genre,
            'cat': work.cat,
            'recommend': work.recommend,
            'title': work.title,
            'nickname': work.nickname,
            'date': work.date,
            'album_count': work.album_count,
        }

        if work.id in liked_list:
            info['liked'] = True
        else:
            info['liked'] = None

        WORKS.append(info)
        PLAYLIST.append(info)
        i += 1

    # group onto genres
    works_by_genre = defaultdict(list)

    for work in WORKS:
        genre = work['genre']
        works_by_genre[genre].append(work)

    return works_by_genre, PLAYLIST


def get_avatar(username, imgurl):

    try:
        response = requests.head(imgurl)
    except:
        return "Error: Invalid URL specified.", 403
    try:
        filetype = response.headers['content-type']
        filesize = float(response.headers['content-length']) / 1048576
    except:
        return "Error: Invalid image link.", 403

    if "image/jpeg" not in filetype and "image/png" not in filetype:
        return "Error: Link is not to a .jpg or .png file", 403

    if filesize > 5:
        return "Error: Image file size is too large. Max size is 5 MB.", 403

    client = storage_client
    bucket = client.get_bucket('composer-explorer.appspot.com')
    blob = bucket.blob('avatars/{}.jpg'.format(username))

    image = Image.open(requests.get(imgurl, stream=True).raw)
    image.thumbnail((200, 200))
    image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    blob.cache_control = 'public, max-age=0'
    blob.upload_from_string(img_byte_arr, content_type='image/jpeg')

    return current_app.config['STATIC'] + 'avatars/{}.jpg'.format(username), 200


def upload_avatar(username, file):

    client = storage_client
    bucket = client.get_bucket('composer-explorer.appspot.com')
    blob = bucket.blob('avatars/{}.jpg'.format(username))
    
    try:
        image = Image.open(file)
    except:
        return "Error: Invalid or no image file specified.", 403

    image.thumbnail((200, 200))
    image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    blob.cache_control = 'public, max-age=0'
    blob.upload_from_string(img_byte_arr, content_type='image/jpeg')

    return current_app.config['STATIC'] + 'avatars/{}.jpg'.format(username), 200
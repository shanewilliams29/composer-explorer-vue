from app import app
import json
from google.cloud import storage
import requests
from PIL import Image
import io

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
            'flag': app.config['STATIC'] + 'flags/1x1/' + flag + '.svg',
            'img': app.config['STATIC'] + 'img/' + composer.name_short + '.jpg',
            'region': region_name,
            'color': era_color,
            'popular': composer.catalogued
        }
        COMPOSERS.append(info)

    return COMPOSERS


def group_composers_by_region(COMPOSERS):
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

    return composers_by_region


def prepare_works(works_list, liked_list):
    WORKS = []
    i = 0
    for work in works_list:

        info = {
            'index': i,
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
        i += 1

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

    return works_by_genre


# used if works likst with likes is returned
# def new_prepare_works(works_list):
#     WORKS = []
#     for (work, likes) in works_list:

#         info = {
#             'id': work.id,
#             'genre': work.genre,
#             'cat': work.cat,
#             'recommend': work.recommend,
#             'title': work.title,
#             'nickname': work.nickname,
#             'date': work.date,
#             'album_count': work.album_count,
#             'likes': likes
#         }
#         WORKS.append(info)

#     # group onto genres
#     works_by_genre = {}
#     works_in_genre = []
#     i = 0
#     prev_genre = WORKS[i]['genre']

#     while i < len(WORKS):
#         genre = WORKS[i]['genre']
#         if genre == prev_genre:
#             works_in_genre.append(WORKS[i])
#             i += 1
#             if i == len(WORKS):
#                 works_by_genre[prev_genre] = works_in_genre
#         else:
#             works_by_genre[prev_genre] = works_in_genre
#             works_in_genre = []
#             works_in_genre.append(WORKS[i])
#             prev_genre = genre
#             i += 1
#             if i == len(WORKS):
#                 works_by_genre[prev_genre] = works_in_genre

#     return works_by_genre


def get_avatar(username, imgurl):

    try:
        response = requests.head(imgurl)
    except:
        return "Error: Invalid URL specified.", 403
    try:
        filetype = response.headers['content-type']
        filesize = float(response.headers['content-length']) / 5242880
    except:
        return "Error: Invalid image link.", 403

    if "image/jpeg" not in filetype and "image/png" not in filetype:
        return "Error: Link is not to a .jpg or .png file", 403

    if filesize > 5:
        return "Error: Image size is too large. Max size is 5 MB.", 403

    client = storage.Client(project='composer-explorer')
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

    return app.config['STATIC'] + 'avatars/{}.jpg'.format(username), 200
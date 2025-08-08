import json
from app import db
import requests
from PIL import Image
import io
from flask import current_app
from collections import defaultdict
from app.models import Performers, ComposerList, performer_albums
from sqlalchemy import func, text, or_
import random
from flask import request
import time


def is_mobile():
    user_agent = request.headers.get('User-Agent', '').lower()
    return 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent


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
            'nationality': composer.nationality,
            'color': era_color,
            'catalogued': composer.catalogued,
            'tier': composer.tier
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
            'duration': work.duration,
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

    image = Image.open(requests.get(imgurl, stream=True).raw)
    image.thumbnail((200, 200))
    image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    filename = f"static/avatars/{username}.jpg"

    # Overwrite existing object (same key)
    current_app.s3_client.upload_fileobj(
        img_byte_arr,
        current_app.config['CONTABO_BUCKET'],
        filename,
        ExtraArgs={
            'ContentType': 'image/jpeg',
            'CacheControl': 'no-cache, no-store, must-revalidate',
            'ACL': 'public-read'
        }
    )

    # Add version param to bypass cache
    file_url = f"{current_app.config['CONTABO_PUBLIC_BASE']}/{filename}?v={int(time.time())}"
    return file_url, 200


def upload_avatar(username, file):
    # Validate that a file was provided and is an image
    try:
        image = Image.open(file)
    except:
        return "Error: Invalid or no image file specified.", 403

    # Resize & convert to JPEG
    image.thumbnail((200, 200))
    image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    # Build the filename
    filename = f"static/avatars/{username}.jpg"

    # Upload to Contabo (overwrite existing)
    current_app.s3_client.upload_fileobj(
        img_byte_arr,
        current_app.config['CONTABO_BUCKET'],
        filename,
        ExtraArgs={
            'ContentType': 'image/jpeg',
            'CacheControl': 'no-cache, no-store, must-revalidate',
            'ACL': 'public-read'
        }
    )

    # Construct the PUBLIC URL (with cache-busting)
    file_url = f"{current_app.config['CONTABO_PUBLIC_BASE']}/{filename}?v={int(time.time())}"
    return file_url, 200


def retrieve_artist_list_from_db():
    artist_list = []

    artists = db.session.query(Performers.id, Performers.name, Performers.img, Performers.description, func.count(Performers.id).label('total'))\
        .join(performer_albums)\
        .filter(or_(Performers.hidden == False, Performers.hidden == None))\
        .group_by(Performers.id).order_by(text('total DESC')).all()

    composers = db.session.query(ComposerList.name_full).all()
    composer_names = set(composer for (composer,) in composers)
    
    # remove composer exceptions who were also conductors and performance artists
    exceptions_list = ['Leonard Bernstein', 'Pierre Boulez', 'Steve Reich']
    for exception in exceptions_list:
        composer_names.remove(exception)

    # remove composers and bad results
    for _id, artist, img, description, count in artists:
        if artist not in composer_names and "/" not in artist:
            artist_list.append({'id': _id, 'name': artist, 'img': img, 'description': description})

    return artist_list


def is_image_url_alive(url, timeout=5):
    """Return True if URL exists, returns 200 and is an image content."""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        if resp.status_code == 405:  # some servers disallow HEAD
            resp = requests.get(url, stream=True, timeout=timeout)
        content_type = resp.headers.get("Content-Type", "")
        return resp.status_code == 200 and content_type.startswith("image/")
    except requests.RequestException:
        return False

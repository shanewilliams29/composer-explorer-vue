from flask import session
from app.models import WorkAlbums, Performers
import re
import httpx
import asyncio
import unidecode
import json
import collections
from urllib.parse import quote
from app.cron.logging_config import logger


def get_general_genres():
    return set(['opera', 'stage work', 'ballet'])


async def search_spotify_httpx(url):

    headers = {
        'Authorization': 'Bearer {}'.format(session['app_token']),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

    return result


async def main(urls):

    tasks = [search_spotify_httpx(url) for url in urls]
    results = await asyncio.gather(*tasks)

    return list(results)


def search_spotify_for_tracks(track_list, search_string):
    logger.debug(f"Searching Spotify... \"{search_string}\"")

    search_urls = []
    for i in range(0, 1000, 50): 
        search_urls.append(f"https://api.spotify.com/v1/search?query={quote(search_string)}&type=track&offset={i}&limit=50")

    result_list = asyncio.run(main(search_urls))

    for result in result_list:
        track_list.extend(result['tracks']['items'])

    return track_list


def retrieve_spotify_tracks_for_work_async(composer, work):

    track_list = []
    general_genres = get_general_genres()

    # search without cat numbers for composer.general or opera/stage work
    if composer.general or work.genre.lower().strip() in general_genres:
        search_string = work.composer + " " + work.title

    # search with cat numbers if not composer.general
    else:
        search_string = work.composer + " " + work.title + " " + work.cat

    track_list = search_spotify_for_tracks(track_list, search_string)

    # do search again for case where opera composer has cat numbers (returns more operas)
    if not composer.general and work.genre.lower().strip() in general_genres:
        search_string = work.composer + " " + work.title + " " + work.cat
    
        track_list = search_spotify_for_tracks(track_list, search_string)

    # do search again on cat number only if a cat number composer
    if not composer.general and work.cat:
        search_string = work.composer + " " + work.cat
    
        track_list = search_spotify_for_tracks(track_list, search_string)

    # do search again on nickname if work has a nickname
    if work.nickname:
        search_string = work.composer + " " + work.nickname
    
        track_list = search_spotify_for_tracks(track_list, search_string)

    logger.debug(f"[ {len(track_list)} ] tracks retrieved!")
    
    return track_list


def drop_unmatched_tracks(composer, work, tracks):

    def is_composer_in_artists(composer, artists):
        for artist in artists:
            if composer.name_full in artist['name']:
                return True
        return False

    def should_check_cat(composer, work):
        if composer.general or not work.cat.strip() or work.genre.lower().strip() in get_general_genres():
            return False
        return True

    def is_cat_found_in_track(work, track):
        cat1 = re.sub(r'\W+', ' ', work.cat.lower().strip()).replace(" ", "") + " "
        cat2 = re.sub(r'\W+', ' ', work.cat.lower().strip()) + " "
        name = re.sub(r'\W+', ' ', track['name'].lower()) + " "

        if cat1 not in name and cat2 not in name:
            return False
        return True

    def is_cat_found_in_track_case_sensitive(work, track):
        cat1 = re.sub(r'\W+', ' ', work.cat.strip()).replace(" ", "") + " "
        cat2 = re.sub(r'\W+', ' ', work.cat.strip()) + " "
        name = re.sub(r'\W+', ' ', track['name']) + " "

        if cat1 not in name and cat2 not in name:
            return False
        return True

    def should_check_no_work(work):
        work_title_string = " " + re.sub(r'\W+', ' ', work.title.lower())

        # exclude Haydn from check due to alternate numbering schemes
        if " no " in work_title_string and work.composer != "Haydn":  
            return True
        return False

    def should_check_no_track(track):
        track_title_string = " " + re.sub(r'\W+', ' ', track['name'].lower())

        if " no " in track_title_string:
            return True
        return False

    def is_no_found_in_track(work, track):  # Sonata No. 4 in C major
        work_title_string = " " + re.sub(r'\W+', ' ', work.title.lower())  # sonata no 4 in c major
        track_string = re.sub(r'\W+', ' ', track['name'].lower())
        
        three_chars_after_no = work_title_string.split(" no ", 1)[1].replace(" ", "")[0:3]  # 4i
        find_digits = re.search(r'\d+', three_chars_after_no)  # re.Match object for digits after " no "

        if find_digits:  # re returns None if digits are not found
            num = find_digits.group()  # 4, result digits from re
        else:
            return False

        no = "no " + num + " "
        
        if no not in track_string + " ":
            return False
        else:
            return True

    def flag_specific_rejections(work_string, track_string):
        # prevents gotterdammerung tracks from being added to siegfried
        if "siegfried" in work_string:
            if "gotterdammerung" in track_string:
                return True
            if "twilight" in track_string:
                return True
        return False

    def is_title_match(work, track):
        # reject tracks with a "no." if the work doesn't have a "no."
        work_no_check = should_check_no_work(work)
        track_no_check = should_check_no_track(track)

        if work_no_check != track_no_check:
            return False

        # change sharps and flats from symbols into words
        work_title_string = work.title.replace("♭", "flat").replace("#", "sharp").lower()
        track_string = track['name'].replace("♭", "flat").replace("#", "sharp").lower()

        # remove symbols and spaces
        work_title_string = re.sub(r'\W+', ' ', work_title_string)
        track_string = re.sub(r'\W+', ' ', track_string)

        work_title_string = unidecode.unidecode(work_title_string).replace(" ", "")
        track_string = unidecode.unidecode(track_string).replace(" ", "")

        if flag_specific_rejections(work_title_string, track_string):
            return False

        if work_title_string.strip() not in track_string.strip():
            return False

        return True

    def is_nickname_match(work, track):
        if not work.nickname:
            return False
            
        # check if track title matches work nickname
        work_nickname_string = re.sub(r'\W+', ' ', work.nickname.lower())
        track_string = re.sub(r'\W+', ' ', track['name'].lower())

        work_nickname_string = unidecode.unidecode(work_nickname_string).replace(" ", "")
        track_string = unidecode.unidecode(track_string).replace(" ", "")

        if work_nickname_string.strip() not in track_string.strip():
            return False

        return True

    good_tracks = []

    for track in tracks:
        # CHECK 1: check that composer appears in artists and skip if not found
        artists = track['artists']
        if not is_composer_in_artists(composer, artists):
            continue

        # CHECK 2: check that cat number appears in work, if relevant. Skip if not found
        if should_check_cat(composer, work):
            if composer.name_short == "Telemann":  # Telemann cat nos. are case-sensitive
                if not is_cat_found_in_track_case_sensitive(work, track):
                    continue
            else:
                if not is_cat_found_in_track(work, track):
                    continue

        # CHECK 3: check that the work no. appears in track name. Pass if there isn't a no. in work
        if should_check_no_work(work):
            if not is_no_found_in_track(work, track):
                continue

        # CHECK 4: check that title or nickname is a match, if no cat number in work, or op. posth.
        if not should_check_cat(composer, work) or work.cat.lower() == "op. posth.":
            if not is_title_match(work, track):
                if not is_nickname_match(work, track):
                    continue

        good_tracks.append(track)

    return good_tracks


def get_album_list_from_tracks(tracks):

    album_ids = set()
    for track in tracks:
        album_ids.add(track['album']['id'])

    logger.debug(f"[ {len(album_ids)} ] unique albums!")
    return list(album_ids)


def check_if_albums_in_database(album_ids, work):

    potential_new_albums = set()
    for album_id in album_ids:
        potential_new_albums.add(work.id + album_id)

    existing_albums = set({album.id for album in WorkAlbums.query.filter_by(workid=work.id).all()})

    new_albums_set = potential_new_albums.difference(existing_albums)

    new_albums_list = []
    for album in new_albums_set:
        new_albums_list.append(album.replace(work.id, ""))

    logger.debug(f"[ {len(new_albums_list)} ] albums not already in database!")

    return new_albums_list


def get_albums_from_ids_async(id_list):

    api_endpoint = 'https://api.spotify.com/v1/albums?ids='
    url_fetch_list = []

    logger.debug("Fetching albums...")

    for i in range(0, len(id_list), 20):
        id_fetch_list = id_list[i:i + 20]
        id_string = ','.join(id_fetch_list)

        url_fetch_list.append(api_endpoint + id_string)

    album_results = asyncio.run(main(url_fetch_list))

    album_list = []
    for album_group in album_results:
        album_list.extend(album_group['albums'])

    logger.debug(f"[ {len(album_list)} ] albums retrieved!")

    return album_list


def retrieve_album_tracks_and_drop(composer, work, albums):

    logger.debug("Processing albums...")

    album_url_dict = {}
    for album in albums:
        if album['album_type'] == "compilation":  # don't bother with compilation albums
            continue

        num_tracks = album['total_tracks']

        url_list = []
        for i in range(50, num_tracks, 50):
            url = f'https://api.spotify.com/v1/albums/{album["id"]}/tracks?offset={i}&limit=50'
            url_list.append(url)

        if num_tracks > 50:
            album_url_dict[album['id']] = url_list

    album_results_dict = {}

    for album_id, urls in album_url_dict.items():
        album_results = asyncio.run(main(urls))
        logger.debug(f"Fetched {len(urls)} pages for {album_id}")
        album_results_dict[album_id] = album_results

    for album in albums:
        tracks = album['tracks']['items']
        results = album_results_dict.get(album['id'])
        if results:
            for result in results:
                tracks.extend(result['items'])

        work_tracks = drop_unmatched_tracks(composer, work, tracks)
        album['work_tracks'] = work_tracks

    logger.debug(f"[ {len(albums)} ] albums prepared for processing!")

    return albums


def prepare_work_albums_and_performers(composer, work, albums, existing_artists):

    def generate_album_data_tracks(track_list):

        work_playlist = []
        for track in track_list:
            work_playlist.append(track['uri'])

        data_tracks = []
        for i, track in enumerate(track_list):
            cut = len(work_playlist) - i
            track_playlist = " ".join(work_playlist[-cut:])
            track_data_item = [track['title'], track['id'], track_playlist, track['duration']]
            data_tracks.append(track_data_item)

        return data_tracks

    def generate_album_data_artists(track_list):

        artist_dict = {}

        raw_artist_list = []
        for track in track_list:
            for artist in track['artists']:
                raw_artist_list.append(artist['name'])

        fixed_artists = []
        for artist in raw_artist_list:
            if '/' in artist:
                split_artists = artist.split('/')
                split_artists = [x.strip() for x in split_artists]  # Trim whitespace from each artist name
                fixed_artists.extend(split_artists)
            else:
                fixed_artists.append(artist)

        no_composer_list = [x for x in fixed_artists if x != composer.name_full]
        if len(no_composer_list) == 0:
            no_composer_list.append(composer.name_full)

        counter = collections.Counter(no_composer_list)
        artist_dict['artists'] = ", ".join(list(dict(counter.most_common(2)).keys()))
        artist_dict['minor_artists'] = ", ".join(list(set((dict(counter.most_common(8)).keys())) - set(dict(counter.most_common(2)).keys())))
        artist_dict['all_artists'] = ", ".join(list(dict(counter).keys()))

        return artist_dict

    def calculate_album_duration(track_list):

        album_duration = 0
        for track in track_list:
            album_duration += int(track['duration'])

        return album_duration

    def calculate_album_score(track_list, popularity):

        album_score = len(track_list)

        if work.genre.lower().strip() in get_general_genres():
            if album_score > 20:
                album_score = 20
            return album_score * 5 + popularity

        if work.composer == "Chopin":
            cutoff = 1
        else:
            cutoff = 3
        if album_score > cutoff:
            album_score = cutoff
        return album_score * 33.3 + popularity

    work_albums_list = []
    work_artist_ids = set()
    dropped_albums_count = 0

    for album in albums:

        # don't process if no work tracks
        if len(album['work_tracks']) == 0:
            dropped_albums_count += 1
            continue

        # Album information
        work_album_id = work.id + album['id']
        work_id = work.id
        spotify_album_id = album['id']
        work_composer = work.composer
        try:
            img_large = album['images'][0]['url']
        except Exception:
            img_large = None
        try:
            img_small = album['images'][1]['url']
        except Exception:
            img_small = None
        label = album['label']
        album_title = album['name']
        album_track_count = album['total_tracks']
        work_track_count = len(album['work_tracks'])
        album_type = album['album_type']
        release_date = album['release_date'].split('-')[0]
        popularity = album['popularity']

        # generate track list
        work_track = {}
        track_list = []
        tracks = album['work_tracks']
        for track in tracks:
            work_track = {
                'id': track['id'],
                'uri': track['uri'],
                'title': track['name'],
                'disc_no': track['disc_number'],
                'track_no': track['track_number'],
                'duration': track['duration_ms'],
                # 'preview_url': track['preview_url'], creating bugs with Spotify
                'artists': track['artists'],
            }
            track_list.append(work_track)

        track_list = sorted(track_list, key=lambda i: (i['disc_no'], i['track_no']))

        # generate album tracks data item
        data_tracks = generate_album_data_tracks(track_list)

        # generate artists tracks data item
        data_artists = generate_album_data_artists(track_list)

        # calculate work durations
        album_duration = calculate_album_duration(track_list)

        # calculate and add score
        score = calculate_album_score(track_list, popularity)

        # prepare album data dict
        data = {
          "album_name": album_title,
          "album_id": spotify_album_id,
          "album_uri": f"spotify:album:{spotify_album_id}",
          "release_date": f"{release_date}",
          "popularity": popularity,
          "album_img": img_small,
          "tracks": data_tracks,
          "artists": data_artists['artists'],
          "track_count": work_track_count,
          "minor_artists": data_artists['minor_artists'],
          "all_artists": data_artists['all_artists'],
          "score": score
        }

        work_album = WorkAlbums(id=work_album_id,
                                workid=work_id,
                                album_id=spotify_album_id,
                                composer=work_composer,
                                score=score,
                                artists=data_artists['all_artists'],
                                data=json.dumps(data),
                                img=img_large,
                                label=label,
                                title=album_title,
                                track_count=album_track_count,
                                work_track_count=work_track_count,
                                album_type=album_type,
                                duration=album_duration)

        work_albums_list.append(work_album)

        # generate performers entries
        unique_album_artists = []
        seen_artist_ids = set()

        for track in track_list:
            for artist in track['artists']:
                if artist['id'] not in seen_artist_ids:
                    unique_album_artists.append(artist)
                    seen_artist_ids.add(artist['id'])
                    work_artist_ids.add(artist['id'])

        for artist in unique_album_artists:
            existing_artist = existing_artists.get(artist['id'])
            if existing_artist:
                # Update the existing artist's album list
                existing_artist.add_album(work_album)
            else:
                # Add a new artist entry
                new_artist = Performers(
                    id=artist['id'],
                    name=artist['name'])
                new_artist.add_album(work_album) 
                existing_artists[new_artist.id] = new_artist

    # drop performers that are not updated
    for id in list(existing_artists.keys()):
        if id not in work_artist_ids:
            del existing_artists[id]

    logger.debug(f"[ {len(work_albums_list)} ] albums processed! [ {dropped_albums_count} ] compilation albums dropped.")
    return work_albums_list, existing_artists

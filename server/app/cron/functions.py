from flask import session
from app import sp
import re
import httpx
import asyncio
import unidecode


def get_general_genres():
    return set(['opera', 'stage work'])


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


def retrieve_spotify_tracks_for_work_async(composer, work):
    
    track_list = []
    general_genres = get_general_genres()

    # search without cat numbers for composer.general or opera/stage work
    if composer.general or work.genre.lower().strip() in general_genres:
        search_string = work.composer + " " + work.title

    # search with cat numbers if not composer.general
    else:
        search_string = work.composer + " " + work.title + " " + work.cat

    print(f"\n    Searching Spotify... \"{search_string}\"")

    search_urls = []
    for i in range(0, 1000, 50): 
        search_urls.append(f"https://api.spotify.com/v1/search?query={search_string}&type=track&offset={i}&limit=50")

    result_list = asyncio.run(main(search_urls))

    for result in result_list:
        track_list.extend(result['tracks']['items'])

    # do search again for case where opera composer has cat numbers (returns more operas)
    if not composer.general and work.genre.lower().strip() in general_genres:
        search_string = work.composer + " " + work.title + " " + work.cat
    
        print(f"    Searching Spotify... \"{search_string}\"")

        search_urls = []
        for i in range(0, 1000, 50): 
            search_urls.append(f"https://api.spotify.com/v1/search?query={search_string}&type=track&offset={i}&limit=50")

        result_list = asyncio.run(main(search_urls))

        for result in result_list:
            track_list.extend(result['tracks']['items'])

    print(f"    [ {len(track_list)} ] tracks retrieved!")
    
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

    def should_check_no_work(work):
        work_title_string = " " + re.sub(r'\W+', ' ', work.title.lower())

        if " no " in work_title_string:
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

        # check if titles match, remove sharps and flats
        work_title_string = re.sub(r'\W+', ' ', work.title.lower()).replace(" sharp", "").replace(" flat", "")
        track_string = re.sub(r'\W+', ' ', track['name'].lower()).replace(" sharp", "").replace(" flat", "")

        work_title_string = unidecode.unidecode(work_title_string).replace(" ", "")
        track_string = unidecode.unidecode(track_string).replace(" ", "")

        if flag_specific_rejections(work_title_string, track_string):
            return False

        if work_title_string.strip() not in track_string.strip():
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
            if not is_cat_found_in_track(work, track):
                continue

        # CHECK 3: check that the work no. appears in track name. Pass if there isn't a no. in work
        if should_check_no_work(work):
            if not is_no_found_in_track(work, track):
                continue

        # CHECK 4: check that title is a match if no cat number in work
        if not should_check_cat(composer, work):
            if not is_title_match(work, track):
                continue

        good_tracks.append(track)

    print(f"    [ {len(good_tracks)} ] matched with work!")

    return good_tracks


def get_album_list_from_tracks(tracks):

    album_ids = set()
    for track in tracks:
        album_ids.add(track['album']['id'])

    print(f"    [ {len(album_ids)} ] unique albums!\n")
    return list(album_ids)


def get_albums_from_ids(id_list):

    album_list = []
    k = 0
    while k < len(id_list):

        i = 0
        id_fetch_list = []

        while i < 20 and k < len(id_list):
            
            id_fetch_list.append(id_list[k])
            i += 1
            k += 1

        id_string = ','.join(id_fetch_list)
        response = sp.get_albums(id_string)
        print(f"    Fetching albums... {k} of {len(id_list)}", end='\r')
        results = response.json()

        if results.get('error'):
            raise Exception(results['error']['message'])  

        album_list.append(results)

    print(f"\n    [ {len(id_list)} ] albums retrieved!\n")

    return album_list

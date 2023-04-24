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

    print(f"Searching Spotify: [{search_string}]")

    search_urls = []
    for i in range(0, 1000, 50): 
        search_urls.append(f"https://api.spotify.com/v1/search?query={search_string}&type=track&offset={i}&limit=50")

    result_list = asyncio.run(main(search_urls))

    for result in result_list:
        track_list.extend(result['tracks']['items'])

    if len(track_list) > 0:
        print(f"{len(track_list)} tracks found!")
    
    return track_list


def retrieve_spotify_tracks_for_work(composer, work):
    
    track_list = []
    general_genres = get_general_genres()

    # search without cat numbers for composer.general or opera/stage work
    if composer.general or work.genre.lower().strip() in general_genres:
        search_string = work.composer + " " + work.title

    # search with cat numbers if not composer.general
    else:
        search_string = work.composer + " " + work.title + " " + work.cat

    response = sp.search(search_string)
    results = response.json()

    if results.get('error'):
        raise Exception(results['error']['status'])

    # do a more general search on just cat. no if no results
    if len(results['tracks']['items']) == 0 and work.cat.strip() and work.cat.strip() != "Op. posth.":
        search_string = work.composer + " " + work.cat
        response = sp.search(search_string)
        results = response.json()

    if results.get('error'):
        raise Exception(results['error']['status'])  

    if len(results['tracks']['items']) == 0:
        raise Exception(404)

    # add items to track list
    track_list.extend(results['tracks']['items'])

    # get next pages of results
    next_url = results['tracks']['next']

    while next_url:
        response = sp.get_next_search_page(next_url)
        results = response.json()
        print(f"Searching Spotify: {next_url}", end='\r')

        if results.get('error'):
            raise Exception(results['error']['status'])

        track_list.extend(results['tracks']['items'])
        next_url = results['tracks']['next']

    print(f"\nSpotify search complete! {len(track_list)} tracks found.")
        
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

        if work_title_string.strip() not in track_string.strip():
            pass
            return False
        else:
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

        # CHECK 4: check that title is an exact match if no cat number in work
        if not should_check_cat(composer, work):
            if not is_title_match(work, track):
                continue

        print(f"MATCH: {work.title} ---> {track['name']}")
        good_tracks.append(track)


    print(f"{len(good_tracks)} matched with work!")

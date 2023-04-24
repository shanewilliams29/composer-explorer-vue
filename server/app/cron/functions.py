from flask import session
from app import sp
import re
import httpx
import asyncio


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

    def should_check_no(work):
        work_title_string = re.sub(r'\W+', ' ', work.title.lower())

        if " no " in work_title_string:
            return True
        return False

    def is_no_found_in_track(work, track): # Sonata No. 4
        work_title_string = re.sub(r'\W+', ' ', work.title.lower())  # sonata no 4
        track_string = re.sub(r'\W+', ' ', track['name'].lower())

        # print(f'\nWORK: {work.title} --> {work_title_string}')
        
        three_chars_after_no = work_title_string.split(" no ", 1)[1].replace(" ", "")[0:3]  # 4
        find_digits = re.search(r'\d+', three_chars_after_no)  # re.Match object for digits after " no "
        if find_digits:  # will return None if digits are not found
            num = find_digits.group()  # 4, result digits from re
        else:
            return False

        no = "no " + num + " "
        # print("M " + no)
        # print("S " + track_string)
        
        if no not in track_string + " ":
            # print('REJECT')
            return False
        else:
            # print('MATCH')
            return True

    for track in tracks:
        
        # CHECK 1: check that composer appears in artists and skip if not
        artists = track['artists']
        if not is_composer_in_artists(composer, artists):
            continue

        # CHECK 2: check that cat number appears in work, if relevant. Skip if not
        if should_check_cat(composer, work):
            if not is_cat_found_in_track(work, track):
                continue

        # CHECK 3: check that the work no. appears in track name. Pass if there isn't a no.
        if should_check_no(work):
            if not is_no_found_in_track(work, track):
                continue
            else:
                print(track['name'])



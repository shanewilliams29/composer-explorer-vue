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

    search_urls = []
    for i in range(0, 1000, 50): 
        search_urls.append(f"https://api.spotify.com/v1/search?query={search_string}&type=track&offset={i}&limit=50")

    result_list = asyncio.run(main(search_urls))

    for result in result_list:
        track_list.extend(result['tracks']['items'])

    if len(track_list) > 0:
        print(f"Spotify search complete! {len(track_list)} tracks found.")
    
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

    def is_cat_found_in_title(work, track):
        cat1 = re.sub(r'\W+', ' ', work.cat.lower().strip()).replace(" ", "") + " "
        cat2 = re.sub(r'\W+', ' ', work.cat.lower().strip()) + " "
        name = re.sub(r'\W+', ' ', track['name'].lower()) + " "

        if cat1 not in name and cat2 not in name:
            return False

        return True
    
    for track in tracks:
        
        # check that composer appears in artists and skip if not
        artists = track['artists']
        if not is_composer_in_artists(composer, artists):
            continue

        # check that cat number appears in work, if relevant
        if should_check_cat(composer, work):
            if not is_cat_found_in_title(work, track):
                continue




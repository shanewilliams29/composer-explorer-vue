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
        

        if results.get('error'):
            raise Exception(results['error']['status'])

        track_list.extend(results['tracks']['items'])
        next_url = results['tracks']['next']

    print(f"\nSpotify search complete! {len(track_list)} tracks found.")
        
    return track_list


def get_albums_from_ids(id_list):
    album_list = []
    
    for i in range(0, len(id_list), 20):
        id_fetch_list = id_list[i:i+20]
        id_string = ','.join(id_fetch_list)

        response = sp.get_albums(id_string)
        print(f"    Fetching albums... {i + len(id_fetch_list)} of {len(id_list)}", end='\r')
        results = response.json()

        if results.get('error'):
            raise Exception(results['error']['message'])

        album_list.append(results)

    print(f"\n    [ {len(id_list)} ] albums retrieved!\n")

    return album_list


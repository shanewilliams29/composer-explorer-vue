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



def retrieve_album_tracks_and_drop(composer, work, albums):

    print("    Processing albums...")

    for i, album in enumerate(albums):

        print(f"    {i} of {len(albums)}", end='\r')

        tracks = album['tracks']['items']
        next_tracks_url = album['tracks']['next']

        if album['album_type'] != "compilation":

            while next_tracks_url:
                response = sp.get_more_album(next_tracks_url)
                results = response.json()
            
                if results.get('error'):
                    raise Exception(results['error']['message'])

                tracks.extend(results['items'])
                next_tracks_url = results['next']

        work_tracks = drop_unmatched_tracks(composer, work, tracks)
        album['work_tracks'] = work_tracks

    print(f"    [ {len(albums)} ] albums prepared for processing!")

    return albums


def get_spotify_albums_and_store(composer_name):
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()

    errors = Errors()

    # get composer
    composer = ComposerList.query.filter_by(name_short=composer_name).first()
    if not composer:
        print(RED + f"\n    ERROR: Composer {composer_name} not found!\n" + RESET)
        exit()

    is_not_general = input("\n    Should load use work catalogue numbers? (y/n): ")

    if is_not_general == "y":
        composer.general = False
    elif is_not_general == "n":
        composer.general = True
    else:
        print(RED + "\n    ERROR: Invalid input entered!\n" + RESET)
        exit()

    composer.catalogued = True
    db.session.commit()

    # get works for composer that haven't been processed
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name, WorkList.spotify_loaded == None)\
        .all()
    if not works:
        print(f"\n    No unprocessed works for {composer_name} found! Skipping.\n")
        return

    print(f"\n    {len(works)} unprocessed works found for {composer_name}. Beginning Spotify data pull...\n")

    works_processed = set()
    while len(works_processed) < len(works):

        timer.set_loop_length(len(works) - len(works_processed))
        i = 0

        for work in works:
            
            if work.id not in works_processed:
                i += 1

                console_width = os.get_terminal_size().columns
                spotify_token.refresh_token()
                
                print("-" * console_width)
                print(BOLD + f"\n    {work.id}\n" + RESET)

                # STEP 1: SEARCH SPOTIFY FOR TRACKS FOR WORK
                try:
                    tracks = retrieve_spotify_tracks_for_work_async(composer, work)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        print(RED + "\n    429 TRACK FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        print(RED + f"\n    {e.response.status_code} TRACK FETCH ERROR: An unexpected error occurred. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                        continue

                if len(tracks) == 0:
                    print("\n    No tracks found for work. Skipping...\n")
                    work.spotify_loaded = True
                    db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 2: PURGE TRACKS THAT DON'T MATCH WORK TITLE
                try:
                    matched_tracks = drop_unmatched_tracks(composer, work, tracks)
                    print(f"    [ {len(matched_tracks)} ] matched with work!")
                except Exception as e:
                    print(RED + f"\n    TRACK MATCH ERROR: {e}. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                if len(matched_tracks) == 0:
                    print("\n    No matching tracks found for work. Skipping...\n")
                    work.spotify_loaded = True
                    db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 3: RETRIEVE ALBUMS FROM SPOTIFY FOR TRACKS MATCHING WORK
                album_id_list = get_album_list_from_tracks(matched_tracks)

                try:
                    albums = get_albums_from_ids_async(album_id_list)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        print(RED + "\n    429 ALBUM FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        print(RED + f"\n    {e.response.status_code} ALBUM FETCH ERROR: An unexpected error occurred. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                        continue

                # STEP 4: RETRIEVE ALL ALBUM TRACKS FROM SPOTIFY AND DROP NON-MATCHING TRACKS
                try:
                    processed_albums = retrieve_album_tracks_and_drop(composer, work, albums)
                except Exception as e:
                    if "429" in str(e):
                        print(RED + "\n\n    429 ALBUMS TRACK FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                    else:
                        print(RED + f"\n    ALBUMS TRACK FETCH ERROR: {e}. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                    continue

                # STEP 5: PREPARE WORK ALBUMS AND PERFORMERS FOR DATABASE STORAGE
                existing_artists = {artist.id: artist for artist in Performers.query.all()}
                try:
                    work_albums, performers = prepare_work_albums_and_performers(composer, work, processed_albums, existing_artists)
                except Exception as e:
                    print(RED + f"\n    ALBUMS INFO PREP ERROR: {e}. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue                

                # STEP 6: STORE ALBUM AND PERFORMERS IN DATABASE
                print("    Storing albums and performers in database...")

                db.session.add_all(work_albums)
                for performer in performers.values():
                    db.session.merge(performer)
                work.album_count = len(work_albums)
                work.spotify_loaded = True
                db.session.commit()            
                
                print(f"    [ {len(work_albums)} ] albums stored in database!")
                print(f"    [ {len(performers)} ] performers updated in database!\n")
                
                works_processed.add(work.id)
                timer.print_status_update(i, errors)
                time.sleep(4)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    print("-" * console_width)
    print(GREEN + f"""
    FINISHED. Spotify data pull for {composer_name} complete!\n
    [ {len(works)} ] works processed,
    [ {errors.rate_error.count} ] resolved rate limit 429 errors,
    [ {errors.misc_error.count} ] resolved misc errors.
    [ {time_taken} ] total time taken.\n""" + RESET)
    print("-" * console_width)
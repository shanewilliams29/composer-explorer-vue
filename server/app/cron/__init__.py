from flask import current_app, Blueprint
from datetime import datetime, timedelta
import os

from app import db, log, sp
from app.cron.classes import Timer, SpotifyToken, Errors
from app.cron.functions import retrieve_spotify_tracks_for_work_async, retrieve_album_tracks_and_drop
from app.cron.functions import get_albums_from_ids_async, drop_unmatched_tracks, get_album_list_from_tracks
from app.cron.functions import prepare_work_albums_and_performers, check_if_albums_in_database
from app.models import WorkList, ComposerList, WorkAlbums, AlbumLike, Performers, ComposerCron
from sqlalchemy import func, or_
from collections import defaultdict

import click
import time
import httpx

bp = Blueprint('cron', __name__)

log_name = "cron-log"
logger = log.logger(log_name)

# console text colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
BOLD = '\033[1m'


# FILLS ALBUMS AND PERFORMER DATA FOR ALL COMPOSERS
@ bp.cli.command()
def auto_load():

    composer_to_fill = db.session.query(ComposerCron).first()

    get_and_store_new_albums(composer_to_fill.id)
    fill_work_durations(composer_to_fill.id)
    count_albums(composer_to_fill.id)
    get_spotify_performers_img()
    print(GREEN + f"    Load for {composer_to_fill.id} complete!\n" + RESET)

    indexed_composers = []
    for value in db.session.query(WorkList.composer).distinct():
        str(indexed_composers.append(value[0]))

    for composer in indexed_composers:
        if composer == composer_to_fill.id:
            index = indexed_composers.index(composer)

            if index == len(indexed_composers) - 1:
                next_index = 0
            else:
                next_index = index + 1

            next_composer = indexed_composers[next_index]
            composer_to_fill.id = next_composer
            db.session.commit()
            break


# FIND AND ADD NEW ALBUMS FOR A COMPOSER
@bp.cli.command()
@click.argument("composer_name")
def load(composer_name):
    get_and_store_new_albums(composer_name)
    fill_work_durations(composer_name)
    count_albums(composer_name)
    get_spotify_performers_img()
    print(GREEN + f"    Load for {composer_name} complete!\n" + RESET)


# Necessary for cron tab to execute properlu
def get_console_width(default=80):
    try:
        console_width = os.get_terminal_size().columns
    except OSError:
        console_width = default
    return console_width


def get_and_store_new_albums(composer_name):
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()
    new_albums_count = 0

    errors = Errors()

    # get composer
    composer = ComposerList.query.filter_by(name_short=composer_name).first()
    if not composer:
        print(RED + f"\n    ERROR: Composer {composer_name} not found!\n" + RESET)
        exit()

    # prompt for composer type if new composer
    if not composer.catalogued:
        is_not_general = input("\n    New composer detected. Should load use work catalogue numbers? (y/n): ")

        if is_not_general.lower() == "y":
            composer.general = False
        elif is_not_general.lower() == "n":
            composer.general = True
        else:
            print(RED + "\n    ERROR: Invalid input entered!\n" + RESET)
            exit()

        composer.catalogued = True
        db.session.commit()

    # get all works for composer
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name)\
        .all()
    if not works:
        print(f"\n    No works for {composer_name} found! Skipping.\n")
        return

    print(f"\n    {len(works)} works found for {composer_name}. Beginning Spotify data pull...\n")

    works_processed = set()
    max_number_of_loops = 5
    loop_counter = 0
    while len(works_processed) < len(works) and loop_counter < max_number_of_loops:

        loop_counter += 1
        timer.set_loop_length(len(works) - len(works_processed))
        i = 0

        for work in works:
            
            if work.id not in works_processed:
                i += 1

                console_width = get_console_width()
                spotify_token.refresh_token()
                
                print("-" * console_width)
                print(BOLD + f"\n    {work.id}\n" + RESET)

                # CHECK IF WORK NOT ALREADY PROCESSED (Less than 24 hours ago)
                if work.last_refresh:
                    current_time = datetime.now()
                    if (current_time - work.last_refresh) <= timedelta(hours=24):
                        print("    Skipping... work recently processed...\n")
                        works_processed.add(work.id)
                        continue

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
                        print(RED + f"\n   TRACK FETCH ERROR: {e}. An unexpected error occurred. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                        continue
                except Exception as e:
                    print(RED + f"\n    TRACK FETCH ERROR: {e}. An unexpected error occurred. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                if len(tracks) == 0:
                    print("\n    No tracks found for work. Skipping...\n")
                    work.last_refresh = datetime.now()
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
                    work.last_refresh = datetime.now()
                    db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 3: GET ALBUM ID LIST AND CHECK IF ALREADY IN DATABASE. THEN GET NEW ALBUMS
                album_id_list = get_album_list_from_tracks(matched_tracks)
                new_ids_list = check_if_albums_in_database(album_id_list, work)

                if len(new_ids_list) == 0:
                    print("    No new albums found for work. Skipping...\n")
                    works_processed.add(work.id)
                    work.last_refresh = datetime.now()
                    db.session.commit()
                    timer.print_status_update(i, errors)
                    time.sleep(2)
                    continue

                try:
                    albums = get_albums_from_ids_async(new_ids_list)
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
                except Exception as e:
                    print(RED + f"\n    ALBUM FETCH ERROR: {e}. An unexpected error occurred. Will try again next loop...\n" + RESET)
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
                work.last_refresh = datetime.now()
                db.session.commit()         
                
                print(f"    [ {len(work_albums)} ] albums stored in database!")
                print(f"    [ {len(performers)} ] performers updated in database!\n")
                
                works_processed.add(work.id)
                new_albums_count += 1
                timer.print_status_update(i, errors)
                time.sleep(4)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    if loop_counter == max_number_of_loops:

        logtext = f"""
    FINISHED WITH UNRESOLVED ERRORS! Spotify data pull for {composer_name} partially complete!\n
    [ {len(works)} ] works processed,
    [ {new_albums_count} ] works with new albums,
    [ {len(works) - len(works_processed)} ] works not completed properly,
    [ {errors.rate_error.count} ] rate limit 429 errors,
    [ {errors.misc_error.count} ] misc errors.
    [ {time_taken} ] total time taken.\n"""

        print("-" * console_width)
        print(RED + logtext + RESET)
        print("-" * console_width)
        logger.log_text(logtext, severity="ERROR")
        return

    logtext = f"""
    FINISHED. Spotify data pull for {composer_name} complete!\n
    [ {len(works)} ] works processed,
    [ {new_albums_count} ] works with new albums,
    [ {errors.rate_error.count} ] resolved rate limit 429 errors,
    [ {errors.misc_error.count} ] resolved misc errors.
    [ {time_taken} ] total time taken.\n"""
    print("-" * console_width)
    print(GREEN + logtext + RESET)
    print("-" * console_width)
    logger.log_text(logtext, severity="NOTICE")


#  FILL WORK DURATIONS WITH ALBUM DATA
def fill_work_durations(composer_name):

    # base query
    query = db.session.query(WorkAlbums, func.count(AlbumLike.id).label('likes'))\
        .outerjoin(AlbumLike).group_by(WorkAlbums.id)

    # filter by criteria
    query = query.filter(WorkAlbums.composer == composer_name, 
                         WorkAlbums.hidden != True, 
                         WorkAlbums.track_count <= 100)

    # make subquery
    t = query.subquery('t')
    query = db.session.query(t)

    # disallow compilation albums unless user favorited
    query = query.filter(or_(t.c.album_type != "compilation", t.c.likes > 0))

    # sort the results. Album type sort rates albums ahead of compilations and singles
    query = query.order_by(t.c.workid, t.c.likes.desc(), t.c.album_type, t.c.score.desc())

    # execute the query
    album_list = query.all()

    # create a dictionary of unique works with the duration of the second longest of the top 5 albums
    durations_dict = defaultdict(list)
    workid_album_counts = {}

    for album in album_list:
        if album.workid not in durations_dict:
            durations_dict[album.workid].append(album.duration)
            workid_album_counts[album.workid] = 1

        else:
            if workid_album_counts[album.workid] < 5:
                durations_dict[album.workid].append(album.duration)
                durations_dict[album.workid].sort(reverse=True)
                if len(durations_dict[album.workid]) > 2:
                    durations_dict[album.workid].pop()
                workid_album_counts[album.workid] += 1

    # Keep only the second longest duration for each work ID
    for workid, durations in durations_dict.items():
        if len(durations) > 1:
            durations_dict[workid] = durations[1]
        else:
            durations_dict[workid] = durations[0]

    # get works from database
    works = db.session.query(WorkList).filter(WorkList.composer == composer_name).all()

    for work in works:
        work.duration = durations_dict.get(work.id)

    db.session.commit()
    print(f"\n    Work durations added to WorkList table for {composer_name}!\n")


# COUNT ALBUMS AND ADD TO WORK LIST
def count_albums(name):
    # delete albums with no tracks.
    db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.score == 0).delete()

    # re-sum album counts
    works = db.session.query(WorkList).filter_by(composer=name).all()

    for work in works:
        work.album_count = work.albums.count()
    
    db.session.commit()

    print("    Album counts added to work list!\n")


# FILL PERFORMER TABLE WITH IMAGES FROM SPOTIFY
def get_spotify_performers_img():
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()

    errors = Errors()

    # get performers without images
    artists = db.session.query(Performers)\
        .filter(Performers.img == None).all()

    if not artists:
        print("    No unprocessed performer images found! Skipping.\n")
        return

    print("    Retrieving performer images from Spotify...\n")
    artist_list = []
    for artist in artists:
        artist_list.append(artist)

    k = 0
    j = 0
    images_found = 0
    timer.set_loop_length(len(artist_list))

    while k < len(artist_list):

        i = 0
        id_fetch_list = []

        # token expiry and refreshing
        spotify_token.refresh_token()

        # get data in batches of 50 artist ids from Spotify
        while i < 50 and k < len(artist_list):
            id_fetch_list.append(artist_list[k].id)
            i += 1
            k += 1

        id_string = ','.join(id_fetch_list)

        response = sp.get_artists(id_string)
        results = response.json()

        if results.get('error'):
            print(results.get('error'))
            errors.register_misc_error()
            continue

        # add image link to database
        m = 0
        while m < len(results['artists']):
            try:
                artist_list[j].img = results['artists'][m]['images'][0]['url']
                images_found += 1
            except Exception:
                artist_list[j].img = "NA"
                pass

            j += 1
            m += 1

        db.session.commit()

        timer.print_status_update_one_line(k)

    # finish
    ctx.pop()
    time_taken = timer.get_elapsed_time()

    print(f"""
    Spotify performer image pull complete!\n
    [ {len(artist_list)} ] performers processed,
    [ {images_found} ] images retrieved.
    [ {errors.misc_error.count} ] errors.
    [ {time_taken} ] total time taken.\n""")

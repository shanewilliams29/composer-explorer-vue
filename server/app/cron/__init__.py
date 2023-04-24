from flask import session, current_app, Blueprint
from datetime import datetime, timedelta

from app import db, log, sp
from app.cron.classes import Timer, SpotifyToken, Errors
from app.cron.functions import retrieve_spotify_tracks_for_work_async, retrieve_album_tracks_and_drop
from app.cron.functions import get_albums_from_ids_async, drop_unmatched_tracks, get_album_list_from_tracks
from app.cron.functions import prepare_work_albums_and_performers
from app.models import WorkList, ComposerList

import click
import time
import jsonpickle
import httpx

bp = Blueprint('cron', __name__)


# LOAD A NEW COMPOSER
@ bp.cli.command()
@ click.argument("composer_name")
def load_new(composer_name):
    get_spotify_albums_and_store(composer_name)
    # clean_up_albums(composer_name)
    # albums_track_count(composer_name)
    # fill_performer_info_from_google(composer_name)
    # store_work_durations(composer_name)


def get_spotify_albums_and_store(composer_name):
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()

    errors = Errors()

    # get composer
    composer = ComposerList.query.filter_by(name_short=composer_name).first()
    if not composer:
        print(f">>> ERROR: Composer {composer_name} not found!")
        exit()

    # get works for composer that haven't been processed
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name, WorkList.spotify_loaded == None)\
        .all()
    if not works:
        print(f">>> ERROR: No unprocessed works for {composer_name} found!")
        exit()

    print(f"\n{len(works)} works found for {composer_name}. Beginning Spotify data pull...\n")

    works_processed = set()
    while len(works_processed) < len(works):

        timer.set_loop_length(len(works) - len(works_processed))
        i = 0

        for work in works:
            
            if work.id not in works_processed:
                i += 1

                spotify_token.refresh_token()
                print(f"--- {work.id} ---------------------------------------------------------------------")

                # STEP 1: SEARCH SPOTIFY FOR TRACKS FOR WORK
                try:
                    tracks = retrieve_spotify_tracks_for_work_async(composer, work)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        print(f"\n>>> 429 TRACK FETCH ERROR: Rate limit exceeded. Will try again next loop...\n")
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        print(f"\n>>> {e.response.status_code} TRACK FETCH ERROR: An unexpected error occurred. Will try again next loop...\n")
                        errors.register_misc_error()
                        continue

                if len(tracks) == 0:
                    print("\n    No tracks found for work. Skipping...\n")
                    # work.spotify_loaded = True
                    # db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 2: PURGE TRACKS THAT DON'T MATCH WORK TITLE
                try:
                    matched_tracks = drop_unmatched_tracks(composer, work, tracks)
                    print(f"    [ {len(matched_tracks)} ] matched with work!")
                except Exception as e:
                    print(f"\n>>> TRACK MATCH ERROR: {e}. Will try again next loop...\n")
                    continue

                if len(matched_tracks) == 0:
                    print("\n    No matching tracks found for work. Skipping...\n")
                    # work.spotify_loaded = True
                    # db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 3: RETRIEVE ALBUMS FROM SPOTIFY FOR TRACKS MATCHING WORK
                album_id_list = get_album_list_from_tracks(matched_tracks)

                try:
                    albums = get_albums_from_ids_async(album_id_list)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        print(f"\n>>> 429 ALBUM FETCH ERROR: Rate limit exceeded. Will try again next loop...\n")
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        print(f"\n>>> {e.response.status_code} ALBUM FETCH ERROR: An unexpected error occurred. Will try again next loop...\n")
                        errors.register_misc_error()
                        continue

                # STEP 4: RETRIEVE ALL ALBUM TRACKS FROM SPOTIFY AND DROP NON-MATCHING TRACKS
                try:
                    processed_albums = retrieve_album_tracks_and_drop(composer, work, albums)
                except Exception as e:
                    print(f"\n>>> ALBUMS TRACK FETCH ERROR: {e}. Will try again next loop...\n")
                    continue

                # STEP 5: PREPARE WORK ALBUMS AND PERFORMERS FOR DATABASE STORAGE
                try:
                    work_albums, performers = prepare_work_albums_and_performers(composer, work, processed_albums)
                except Exception as e:
                    print(f"\n>>> ALBUMS INFO PREP ERROR: {e}. Will try again next loop...\n")
                    continue                


                # STEP 6: STORE ALBUM AND PERFORMERS IN DATABASE



                works_processed.add(work.id)
                
                timer.print_status_update(i)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    print(f"""
    FINISHED. Spotify data pull for {composer_name} complete!\n
    [ {len(works)} ] works processed,
    [ {errors.rate_error.count} ] resolved rate limit 429 errors,
    [ {errors.misc_error.count} ] unresolved misc errors.
    [ {time_taken} ] total time taken.\n""")















from flask import session, current_app, Blueprint
from datetime import datetime, timedelta

from app import db, log, sp
from app.cron.classes import Timer, SpotifyToken, Errors
from app.cron.functions import retrieve_spotify_tracks_for_work_async, drop_unmatched_tracks
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
        print(f"Error: Composer {composer_name} not found!")
        exit()

    # get works for composer that haven't been processed
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name, WorkList.spotify_loaded == None)\
        .all()
    # .filter(WorkList.title == "Symphony No. 5 in C♯ minor")\
    if not works:
        print(f"Error: No unprocessed works for {composer_name} found!")
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
                print(f"<{work.id}, {work.title}>")

                try:
                    tracks = retrieve_spotify_tracks_for_work_async(composer, work)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        print(f"429 ERROR: Rate limit exceeded. Will try again next loop...\n")
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        errors.register_misc_error()
                        print(f"{e.response.status_code} ERROR: An unexpected error occurred. Program terminated.\n")
                        exit()

                if len(tracks) == 0:
                    print("404 ERROR: No tracks found for work. Skipping...\n")
                    errors.register_not_found_error()
                    work.spotify_loaded = True
                    db.session.commit()
                    works_processed.add(work.id)
                    continue

                processed_tracks = drop_unmatched_tracks(composer, work, tracks)

                # temp_albums = create_album_list_from_tracks(work, tracks)

                # albums, performers = fill_albums_and_performers(temp_albums)

                # store_albums(albums)
                # store_performers(performers)
                # work.spotify_loaded = True
                # db.session.commit()
                works_processed.add(work.id)
                
                timer.print_status_update(i)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    print(f"""Spotify data pull for {composer_name} complete!
    {len(works)} works processed,
    {errors.rate_error.count} resolved rate limit 429 errors,
    {errors.not_found_error.count} work not found 404 errors,
    {errors.misc_error.count} unresolved misc errors.
    Total time taken: {time_taken}\n""")















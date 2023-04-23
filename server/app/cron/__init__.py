from flask import session, current_app, Blueprint
from datetime import datetime, timedelta

from app import db, log, sp
from app.cron.classes import Timer, SpotifyToken, Errors
from app.models import WorkList

import click
import time

bp = Blueprint('cron', __name__)


# LOAD A NEW COMPOSER
@ bp.cli.command()
@ click.argument("composer_name")
def load_new(composer_name):
    get_spotify_data_and_store(composer_name)
    # clean_up_albums(composer_name)
    # albums_track_count(composer_name)
    # fill_performer_info_from_google(composer_name)
    # store_work_durations(composer_name)


def get_spotify_data_and_store(composer_name):
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()

    errors = Errors()

    # get works for composer that haven't been processed
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name, WorkList.spotify_loaded == None)\
        .all()

    works_processed = set()
    timer.set_loop_length(len(works))
    print(f"{len(works)} works found for {composer_name}. Beginning Spotify data pull...\n")

    while len(works_processed) < len(works):

        for i, work in enumerate(works):
            
            if work.id not in works_processed:

                spotify_token.refresh_token()
                print(f"<{work.id}, {work.title}>")

                # try:
                #     tracks = retrieve_spotify_tracks_for_work(work)
                # except Exception as e:
                #     print(f"{e}\n)
                #     if e == 429:
                #         errors.register_rate_error()
                #     elif e == 404:
                #         errors.register_not_found_error()
                #         work.spotify_loaded = True
                #         db.session.commit()
                #         works_processed.add(work.id)
                #     else:
                #         errors.register_misc_error()
                #     continue

                # temp_albums = create_album_list_from_tracks(work, tracks)

                # albums, performers = fill_albums_and_performers(temp_albums)

                # store_albums(albums)
                # store_performers(performers)
                # work.spotify_loaded = True
                # db.session.commit()
                works_processed.add(work.id)
                
                timer.print_status_update(i + 1)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    print(f"""Spotify data pull for {composer_name} complete!
    {len(works)} works processed,
    {errors.rate_error.count} rate limit 429 errors,
    {errors.not_found_error.count} work not found 404 errors,
    {errors.misc_error.count} unresolved misc errors.
    Total time taken: {time_taken}\n""")















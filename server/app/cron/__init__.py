from flask import current_app, Blueprint
from datetime import datetime

from app import db
from app.cron.classes import Timer, SpotifyToken, Errors
from app.cron.functions import retrieve_spotify_tracks_for_work_async, retrieve_album_tracks_and_drop
from app.cron.functions import get_albums_from_ids_async, drop_unmatched_tracks, get_album_list_from_tracks
from app.cron.functions import prepare_work_albums_and_performers
from app.models import WorkList, ComposerList, WorkAlbums, AlbumLike, Performers
from sqlalchemy import func, or_
from collections import defaultdict

import click
import time
import httpx

bp = Blueprint('cron', __name__)


# LOAD A NEW COMPOSER
@bp.cli.command()
@click.argument("composer_name")
def load_new(composer_name):
    get_spotify_albums_and_store(composer_name)
    fill_work_durations(composer_name)
    print(f"\nLoad for {composer_name} complete!\n")


def get_spotify_albums_and_store(composer_name):
    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    spotify_token = SpotifyToken()

    errors = Errors()

    # get composer
    composer = ComposerList.query.filter_by(name_short=composer_name).first()
    if not composer:
        print(f">>> ERROR: Composer {composer_name} not found!\n")
        exit()

    is_not_general = input("Should load use work catalogue numbers? (y/n): ")

    if is_not_general == "y":
        composer.general = False
    elif is_not_general == "n":
        composer.general = True
    else:
        print(">>> ERROR: Invalid input entered!\n")
        exit()

    composer.catalogued = True
    db.session.commit()

    # get works for composer that haven't been processed
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name, WorkList.spotify_loaded == None)\
        .all()
    if not works:
        print(f">>> ERROR: No unprocessed works for {composer_name} found!\n")
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
                    work.spotify_loaded = True
                    db.session.commit()
                    works_processed.add(work.id)
                    continue

                # STEP 2: PURGE TRACKS THAT DON'T MATCH WORK TITLE
                try:
                    matched_tracks = drop_unmatched_tracks(composer, work, tracks)
                    print(f"    [ {len(matched_tracks)} ] matched with work!")
                except Exception as e:
                    print(f"\n>>> TRACK MATCH ERROR: {e}. Will try again next loop...\n")
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
                    errors.register_misc_error()
                    continue

                # STEP 5: PREPARE WORK ALBUMS AND PERFORMERS FOR DATABASE STORAGE
                existing_artists = {artist.id: artist for artist in Performers.query.all()}
                try:
                    work_albums, performers = prepare_work_albums_and_performers(composer, work, processed_albums, existing_artists)
                except Exception as e:
                    print(f"\n>>> ALBUMS INFO PREP ERROR: {e}. Will try again next loop...\n")
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
                
                print(f"    [ {len(work_albums)} ] albums stored in database!\n")
                print(f"    [ {len(performers)} ] performers updated in database!\n")
                
                works_processed.add(work.id)
                timer.print_status_update(i)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    print(f"""
    FINISHED. Spotify data pull for {composer_name} complete!\n
    [ {len(works)} ] works processed,
    [ {errors.rate_error.count} ] resolved rate limit 429 errors,
    [ {errors.misc_error.count} ] resolved misc errors.
    [ {time_taken} ] total time taken.\n""")


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
    print(f"Work durations added to WorkList table for {composer_name}!")










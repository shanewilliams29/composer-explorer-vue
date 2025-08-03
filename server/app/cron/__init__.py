from flask import current_app, Blueprint
from datetime import datetime, timedelta
import os

from app import db
# from app import log
from app.cron.classes import Timer, SpotifyToken, Errors
from app.cron.functions import retrieve_spotify_tracks_for_work_async, retrieve_album_tracks_and_drop
from app.cron.functions import get_albums_from_ids_async, drop_unmatched_tracks, get_album_list_from_tracks
from app.cron.functions import prepare_work_albums_and_performers, check_if_albums_in_database
from app.cron.logging_config import logger, setup_logging
from app.models import WorkList, ComposerList, WorkAlbums, AlbumLike, Performers, ComposerCron, performer_albums
from sqlalchemy import func, or_, text
from collections import defaultdict
from config import Config
from urllib.parse import quote
from app.spotify import SpotifyAPI
import click
import time
import httpx
import re
import asyncio


bp = Blueprint('cron', __name__)
sp = SpotifyAPI(Config.SPOTIFY_BACKGROUND_ID, Config.SPOTIFY_BACKGROUND_SECRET, Config.SPOTIFY_BACKGROUND_URL)

# log_name = "cron-log"
# logger = log.logger(log_name)

# console text colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
BOLD = '\033[1m'


@bp.cli.command()
@click.option('--verbose', is_flag=True, help="Increase output verbosity.")
def main(verbose):
    """
    Run the command-line application with optional verbose output.
    """
    setup_logging(verbose)

    logger.info("This is an info message")
    logger.debug("This is a debug message")


# FILLS ALBUMS AND PERFORMER DATA FOR ALL COMPOSERS
@bp.cli.command()
@click.option('--verbose', is_flag=True, help="Increase output verbosity.")
def auto_load(verbose):
    """
    Automatically refresh composer data from Spotify
    """
    composer_to_fill = db.session.query(ComposerCron).first()

    setup_logging(verbose)
    get_and_store_new_albums(composer_to_fill.id)
    fill_work_durations(composer_to_fill.id)
    count_albums(composer_to_fill.id)
    get_spotify_performers_img()
    fill_person_info()
    logger.info(f"\nLoad for {composer_to_fill.id} complete!\n")

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
@click.option('--verbose', is_flag=True, help="Increase output verbosity.")
def load(composer_name, verbose=False):
    """
    Load or refresh composer data for specified composer
    """
    setup_logging(verbose)
    get_and_store_new_albums(composer_name)
    fill_work_durations(composer_name)
    count_albums(composer_name)
    get_spotify_performers_img()
    fill_person_info()
    logger.info(f"\nLoad for {composer_name} complete!\n")


# Necessary for cron-tab to execute properly
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
        logger.error(f"Composer {composer_name} not found!")
        exit()

    # prompt for composer type if new composer
    if not composer.catalogued:
        is_not_general = input("\nNew composer detected. Should load use work catalogue numbers? (y/n): ")

        if is_not_general.lower() == "y":
            composer.general = False
        elif is_not_general.lower() == "n":
            composer.general = True
        else:
            logger.error("Invalid input entered!")
            exit()

        composer.catalogued = True
        db.session.commit()

    # get all works for composer
    works = db.session.query(WorkList)\
        .filter(WorkList.composer == composer_name)\
        .all()
    if not works:
        logger.error(f"No works for {composer_name} found! Exiting.")
        exit()

    logger.info(f"{len(works)} works found for {composer_name}. Starting Spotify data pull...\n")

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

                # console_width = get_console_width()
                spotify_token.refresh_token()
                
                # print("-" * console_width)
                logger.debug(BOLD + f"{work.id}" + RESET)

                # CHECK IF WORK NOT ALREADY PROCESSED (Less than 24 hours ago)
                if work.last_refresh:
                    current_time = datetime.now()
                    if (current_time - work.last_refresh) <= timedelta(hours=24):
                        logger.debug("Skipping... work recently processed...\n")
                        works_processed.add(work.id)
                        continue

                # STEP 1: SEARCH SPOTIFY FOR TRACKS FOR WORK
                try:
                    tracks = retrieve_spotify_tracks_for_work_async(composer, work)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.debug(RED + "429 TRACK FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        logger.debug(RED + f"TRACK FETCH ERROR: {e}. An unexpected error occurred. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                        continue
                except Exception as e:
                    logger.debug(RED + f"TRACK FETCH ERROR: {e}. An unexpected error occurred. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                if len(tracks) == 0:
                    logger.debug("No tracks found for work. Skipping...")
                    work.last_refresh = datetime.now()
                    db.session.commit()
                    works_processed.add(work.id)
                    timer.print_status_update(i, errors)
                    continue

                # STEP 2: PURGE TRACKS THAT DON'T MATCH WORK TITLE
                try:
                    matched_tracks = drop_unmatched_tracks(composer, work, tracks)
                    logger.debug(f"[ {len(matched_tracks)} ] matched with work!")
                except Exception as e:
                    logger.debug(RED + f"TRACK MATCH ERROR: {e}. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                if len(matched_tracks) == 0:
                    logger.debug("No matching tracks found for work. Skipping...")
                    work.last_refresh = datetime.now()
                    db.session.commit()
                    works_processed.add(work.id)
                    timer.print_status_update(i, errors)
                    continue

                # STEP 3: GET ALBUM ID LIST AND CHECK IF ALREADY IN DATABASE. THEN GET NEW ALBUMS
                album_id_list = get_album_list_from_tracks(matched_tracks)
                new_ids_list = check_if_albums_in_database(album_id_list, work)

                if len(new_ids_list) == 0:
                    logger.debug("No new albums found for work. Skipping...")
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
                        logger.debug(RED + "429 ALBUM FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                        continue
                    else:
                        logger.debug(RED + f"{e.response.status_code} ALBUM FETCH ERROR: An unexpected error occurred. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                        continue
                except Exception as e:
                    logger.debug(RED + "ALBUM FETCH ERROR: An unexpected error occurred. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                # STEP 4: RETRIEVE ALL ALBUM TRACKS FROM SPOTIFY AND DROP NON-MATCHING TRACKS
                try:
                    processed_albums = retrieve_album_tracks_and_drop(composer, work, albums)
                except Exception as e:
                    if "429" in str(e):
                        logger.debug(RED + "429 ALBUMS TRACK FETCH ERROR: Rate limit exceeded. Will try again next loop...\n" + RESET)
                        errors.register_rate_error()
                        time.sleep(4)
                    else:
                        logger.debug(RED + f"\nALBUMS TRACK FETCH ERROR: {e}. Will try again next loop...\n" + RESET)
                        errors.register_misc_error()
                    continue

                # STEP 5: PREPARE WORK ALBUMS AND PERFORMERS FOR DATABASE STORAGE
                existing_artists = {artist.id: artist for artist in Performers.query.all()}
                try:
                    work_albums, performers = prepare_work_albums_and_performers(composer, work, processed_albums, existing_artists)
                except Exception as e:
                    logger.debug(RED + f"ALBUMS INFO PREP ERROR: {e}. Will try again next loop...\n" + RESET)
                    errors.register_misc_error()
                    continue

                if len(work_albums) == 0:
                    logger.debug("No new albums found for work. Skipping...")
                    works_processed.add(work.id)
                    work.last_refresh = datetime.now()
                    db.session.commit()
                    timer.print_status_update(i, errors)
                    time.sleep(2)
                    continue

                # STEP 6: STORE ALBUM AND PERFORMERS IN DATABASE
                logger.debug("Storing albums and performers in database...")

                db.session.add_all(work_albums)
                for performer in performers.values():
                    db.session.merge(performer)
                work.last_refresh = datetime.now()
                db.session.commit()
                
                logger.debug(f"[ {len(work_albums)} ] albums stored in database!")
                logger.debug(f"[ {len(performers)} ] performers updated in database!")
                
                works_processed.add(work.id)
                new_albums_count += 1
                timer.print_status_update(i, errors)
                time.sleep(4)

    time_taken = timer.get_elapsed_time()
    ctx.pop()

    if loop_counter == max_number_of_loops:
        logger.info(f"FINISHED WITH UNRESOLVED ERRORS! Spotify data pull for {composer_name} partially complete!")
        logger.info(f"[ {len(works)} ] works processed")
        logger.info(f"[ {new_albums_count} ] works with new albums")
        logger.info(f"[ {len(works) - len(works_processed)} ] works not completed properly")
        logger.info(f"[ {errors.rate_error.count} ] rate limit 429 errors")
        logger.info(f"[ {errors.misc_error.count} ] misc errors")
        logger.info(f"[ {time_taken} ] total time taken\n")

    else:
        logger.info(f"FINISHED. Spotify data pull for {composer_name} complete!")
        logger.info(f"[ {len(works)} ] works processed")
        logger.info(f"[ {new_albums_count} ] works with new albums")
        logger.info(f"[ {errors.rate_error.count} ] rate limit 429 errors")
        logger.info(f"[ {errors.misc_error.count} ] resolved misc errors")
        logger.info(f"[ {time_taken} ] total time taken\n")


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
    logger.info(f"Work durations added to WorkList table for {composer_name}!")


# COUNT ALBUMS AND ADD TO WORK LIST
def count_albums(name):
    # delete albums with no tracks.
    db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.score == 0).delete()

    # re-sum album counts
    works = db.session.query(WorkList).filter_by(composer=name).all()

    for work in works:
        work.album_count = work.albums.count()
    
    db.session.commit()

    logger.info("Album counts added to work list!")


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
        logger.info("No unprocessed performer images found! Skipping.")
        return

    logger.info("Retrieving performer images from Spotify...")
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
            logger.debug(results.get('error'))
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

    logger.info(f"Spotify performer image pull complete! [ {len(artist_list)} ] performers processed, [ {images_found} ] images retrieved. [ {errors.misc_error.count} ] errors.")


#  ASYNC FUNCTION TO FETCH FROM GOOGLE KNOWLEDGE GRAPH
async def get_person_details_httpx(person_name, auth_key):
    person = quote(person_name)
    info = {}

    path = f"https://kgsearch.googleapis.com/v1/entities:search?indent=true&types=Person&types=MusicGroup&query={person} Music&limit=50&key={auth_key}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(path)
            response.raise_for_status()
            data = response.json()
            item_list = data['itemListElement']
        
        if item_list:
            person_match = re.sub(r'^(Sir|Dame) ', '', person).strip()
            
            for item in item_list:
                if person_match in item['result']['name']:
                    info = {'description': item['result'].get('description', 'NA'),
                            'image': item['result']['image'].get('contentUrl', 'NA') if 'image' in item['result'] else 'NA',
                            'link': item['result']['detailedDescription'].get('url', 'NA') if 'detailedDescription' in item['result'] else 'NA'
                            }
                    break
            else:
                info = {'description': 'NA',
                        'image': 'NA',
                        'link': 'NA'
                        }
        else:
            info = {'description': 'NA',
                    'image': 'NA',
                    'link': 'NA'
                    }

        return info
    
    except httpx.HTTPError as e:
        return e.response.status_code


# GETS PERSON INFO FROM GOOGLE AND FILLS IN DATABASE
def fill_person_info():

    async def main(person_names):
        auth_key = Config.GOOGLE_KNOWLEDGE_GRAPH_API_KEY

        tasks = [get_person_details_httpx(person_name, auth_key) for person_name in person_names]
        info_list = await asyncio.gather(*tasks)

        return list(zip(person_names, info_list))

    def get_people_from_db():
        return db.session.query(Performers.name, Performers.id, func.count(Performers.id).label('total')) \
            .join(performer_albums) \
            .filter(or_(Performers.hidden == False, Performers.hidden == None)) \
            .filter(Performers.description == None) \
            .group_by(Performers.id).order_by(text('total DESC')).all()

    logger.info("Beginning collection of performer information from Google Knowledge Graph...")

    ctx = current_app.test_request_context()
    ctx.push()

    timer = Timer(datetime.utcnow())
    errors = Errors()

    # Get all performers in order of album count who have not been filled with Google info
    all_people = get_people_from_db()
    enumerated_list = enumerate(all_people)

    # Create artist dictionary for updating artist information
    all_artist_dict = {artist.id: artist for artist in Performers.query.all()}
    
    person_list = []
    id_list = []
    completed_count = 0
    batch_size = 50
    sleep_time = 5
    timer.set_loop_length(len(all_people))

    # Loop through performers, retrieve info in batches of batch_size from Google
    for count, person in enumerated_list:
        loop_success_count = 0
        loop_error_count = 0

        if (count + 1) % batch_size != 0 and count != len(all_people) - 1:
            person_list.append(person.name)
            id_list.append(person.id)

        else:
            person_list.append(person.name)
            id_list.append(person.id)

            people_with_info = asyncio.run(main(person_list))

            # Update performers database table with retrieved info
            for i, (person, info) in enumerate(people_with_info):
                if not isinstance(info, int):
                    artist_id = id_list[i]
                    artist = all_artist_dict.get(artist_id)
                    artist.description = info['description']
                    artist.google_img = info['image']
                    artist.wiki_link = info['link']
                    completed_count += 1
                    loop_success_count += 1
                elif info == 429:
                    loop_error_count += 1
                    errors.register_rate_error()
                else:
                    logger.error(f'{info}. Exiting...')
                    exit()

            db.session.commit()

            person_list = []
            id_list = []

            timer.print_status_update(completed_count, errors)
            
            # Increase sleep time if too many 429 errors are occuring
            if loop_success_count < batch_size / 2:
                sleep_time = sleep_time * 2
            else:
                sleep_time = 5

            # if loop_error_count:
                # print(RED + f"    [ {loop_error_count} ] 429 Errors! Sleeping for {sleep_time} seconds...\n" + RESET)
            
            time.sleep(sleep_time)

    # finish
    ctx.pop()
    logger.info("Performer info load complete!")

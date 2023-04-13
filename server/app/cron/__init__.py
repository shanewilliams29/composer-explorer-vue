from flask import session, current_app, Blueprint
from app import db, log, sp
from datetime import datetime, timedelta
from app.cron.classes import GroupAlbums, SmartAlbums
from app.models import WorkList, Spotify, WorkAlbums, Artists, ComposerCron
from app.models import ArtistList, Performers, AlbumLike
from app.cron.functions import search_spotify_and_save, search_album
from sqlalchemy import func, or_
import click
import json
from collections import defaultdict

bp = Blueprint('cron', __name__)

log_name = "cron-log"
logger = log.logger(log_name)


# FILLS PERFORMER DATA AND IMAGES FOR ALL COMPOSERS
@ bp.cli.command()
def autoperformerfill():

    while True:

        composer_to_fill = db.session.query(ComposerCron).first()

        fillperformerdata(composer_to_fill.id)
        getspotifyartistimg()
        getworkdurations(composer_to_fill.id)
        print("Completed " + str(composer_to_fill.id) + "!")

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


# FILL PERFORMER TABLES WITH ARTISTS INFO FROM SPOTIFY
def fillperformerdata(name):
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    # get albums for processing
    albums = db.session.query(WorkAlbums)\
        .filter(WorkAlbums.composer == name, 
                or_(WorkAlbums.got_artists == None, 
                    WorkAlbums.got_artists != True, 
                    WorkAlbums.duration == None)).all()

    all_album_list = []
    for album in albums:
        album_dict = {'album': album, 
                      'album_id': album.id, 
                      'work_id': album.workid, 
                      'tracks': [], 
                      'artists': [],
                      'track_durations': [],
                      'album_duration': 0,
                      'got_artists': album.got_artists}
        
        data = json.loads(album.data)
        
        for track in data['tracks']:
            album_dict['tracks'].append(track[1])
        
        all_album_list.append(album_dict)

    print(f"{len(all_album_list)} albums found for {name}.")

    # process albums in batches of 50
    for p in range(0, len(all_album_list), 50):    
        
        errors = True
        while errors:
            errors = False
            album_list = all_album_list[p:p+50]
            k = 0

            while k < len(album_list):
                flag_error = False

                # ignore if artists already populated (ie. during second loop with 429 errors)
                if album_list[k]['artists']:
                    k += 1
                    continue

                # token expiry and refreshing
                if session['app_token_expire_time'] < datetime.now():
                    session['app_token'] = sp.client_authorize()
                    session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

                # retrieve data from Spotify for tracks in batches of 50 
                id_fetch_list = []
                tracks_length = len(album_list[k]['tracks'])

                for n in range(0, tracks_length, 50):
                    current_batch = album_list[k]['tracks'][n:n+50]
                    id_fetch_list.extend(current_batch)

                results = []

                for i in range(0, len(id_fetch_list), 50):
                    current_batch = id_fetch_list[i:i+50]
                    id_string = ','.join(current_batch)
                    
                    # Send a request to the Spotify API
                    response = sp.get_tracks(id_string)
                    batch_results = response.json()

                    if batch_results.get('error'):
                        print("ERROR " + str(batch_results.get('error')))
                        if int(batch_results.get('error')['status']) == 429:
                            # retry if rate limit is exceeded
                            errors = True
                            flag_error = True
                            continue
                        else:
                            # continue if another error
                            logtext = "PERFORMERS FILL ERROR FOR " + name + " " + str(batch_results.get('error'))
                            logger.log_text(logtext, severity="ERROR")
                            print(logtext)
                            errors = True
                            flag_error = True
                            continue
                    else:
                        results.extend(batch_results['tracks'])

                # assign artist results from Spotify to album_list
                m = 0
                while m < len(results):
                    try:
                        album_list[k]['artists'].extend(results[m]['artists'])
                        album_list[k]['track_durations'].append(int(results[m]['duration_ms']))
                        album_list[k]['album_duration'] = int(album_list[k]['album_duration']) + int(results[m]['duration_ms'])
                    except Exception as e:
                        # retry if error
                        print(f"ERROR: {e}")
                        album_list[k]['artists'] = []
                        album_list[k]['track_durations'] = []
                        album_list[k]['album_duration'] = 0
                        errors = True
                        flag_error = True
                        m = len(results)
                    m += 1

                # Remove duplicate artists. Use a set to keep track of the ids we've already seen
                seen_ids = set()

                # Create a new list of entries without duplicates
                unique_entries = []
                for entry in album_list[k]['artists']:
                    if entry['id'] not in seen_ids:
                        unique_entries.append(entry)
                        seen_ids.add(entry['id'])

                album_list[k]['artists'] = unique_entries

                k += 1
                if flag_error is False:
                    print(f"Fetched {k + p} of {len(all_album_list)} for {album_list[k - 1]['work_id']}")
                else:
                    print(f"Error in {k + p}, will retry.")
                    flag_error = False

        print("Data retrieved from Spotify Successfully")

        # Store artists in Performers table
        existing_artists = {artist.id: artist for artist in Performers.query.all()}

        for k, album in enumerate(album_list):
            
            # fill artists if appropriate
            if not album['got_artists']:  
                for artist in album['artists']:
                    # Fetch the existing artist
                    existing_artist = existing_artists.get(artist['id'])

                    if existing_artist:
                        # Update the existing artist's album list
                        existing_artist.add_album(album['album'])
                    else:
                        # Add a new artist entry
                        new_entry = Performers(
                            id=artist['id'],
                            name=artist['name'])
                        new_entry.add_album(album['album'])
                        existing_artists[new_entry.id] = new_entry
                        db.session.merge(new_entry)

                # mark album as processed in WorkAlbums table
                album['album'].got_artists = True

            # fill  durations
            album['album'].duration = album['album_duration']
            album_data = json.loads(album['album'].data)
            
            for j, track in enumerate(album_data['tracks']):
                track.append(album_list[k]['track_durations'][j])
            
            album['album'].data = json.dumps(album_data)

            # Commit after every 10 albums or the last album
            if (k + 1) % 10 == 0 or k == len(album_list) - 1:
                db.session.commit()
                print(f"Stored {k + 1 + p} of {len(all_album_list)}")

        current_time = datetime.utcnow()
        elapsed_time = current_time - start_time
        elapsed = str(timedelta(seconds=round(elapsed_time.total_seconds())))

        total = len(all_album_list)
        completed = k + 1 + p
        remaining = total - completed

        item_per_second = (completed / elapsed_time.total_seconds())
        remaining_time = remaining * (1 / item_per_second)
        remaining = str(timedelta(seconds=round(remaining_time)))

        print("Data stored in database successfully.")
        print("Time elapsed: " + elapsed)
        print("Remaining time: " + remaining)
    
    # finish
    ctx.pop()

    message = f"Performer info data fill complete for {name}!"
    print(message)
    logger.log_text(message, severity="NOTICE")


# FILL DURATION IN WORKS LIST
# @ bp.cli.command()
# @ click.argument("composer_name")
def getworkdurations(composer_name):

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


# FILL PERFORMER TABLE WITH IMAGES FROM SPOTIFY
def getspotifyartistimg():
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    # get performers without images
    artists = db.session.query(Performers)\
        .filter(Performers.img == None).all()

    artist_list = []
    for artist in artists:
        artist_list.append(artist)

    k = 0
    j = 0
    error_count = 0

    while k < len(artist_list):

        i = 0
        id_fetch_list = []

        # token expiry and refreshing
        if session['app_token_expire_time'] < datetime.now():
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

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
            error_count += 1
            continue

        # add image link to database
        m = 0
        while m < len(results['artists']):
            try:
                artist_list[j].img = results['artists'][m]['images'][0]['url']
            except Exception:
                print("NO IMAGE FOUND: " + str(artist_list[j]))
                artist_list[j].img = "NA"
                pass

            j += 1
            m += 1

        db.session.commit()
        print("Completed " + str(k) + " of " + str(len(artist_list)))

        current_time = datetime.utcnow()
        elapsed_time = current_time - start_time
        elapsed = str(timedelta(seconds=round(elapsed_time.total_seconds())))

        total = len(artist_list)
        completed = k
        remaining = total - completed

        item_per_second = (completed / elapsed_time.total_seconds())
        remaining_time = remaining * (1 / item_per_second)
        remaining = str(timedelta(seconds=round(remaining_time)))

        print("Time elapsed: " + elapsed)
        print("Remaining time: " + remaining)

    # finish
    ctx.pop()
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time

    message = "Performers image fetch complete. " + str(error_count) + " unresolved errors."
    print(message)


# LOAD A NEW COMPOSER'S WORKS
@ bp.cli.command()
@ click.argument("name")
def loadnew(name):
    spotifygenerate(name)
    fillalbums(name)
    cleanup(name)
    albumimgs(name)
    spotifypull(name)
    trackcount(name)
    print("LOAD COMPLETE!")


# REFRESH A COMPOSER'S WORKS WITH NEW SPOTIFY ALBUMS
@ bp.cli.command()
def autorefresh():
    indexed_composers = []
    for value in db.session.query(WorkList.composer).distinct():
        str(indexed_composers.append(value[0]))

    composer_to_refresh = db.session.query(ComposerCron).first()

    for composer in indexed_composers:
        if composer == composer_to_refresh.id:
            index = indexed_composers.index(composer)

            if index == len(indexed_composers) - 1:
                next_index = 0
            else:
                next_index = index + 1

            next_composer = indexed_composers[next_index]
            composer_to_refresh.id = next_composer
            db.session.commit()
            break

    refreshalbums(composer)
    fillalbums(composer)
    cleanup(composer)
    albumimgs(composer)
    spotifypull(composer)
    trackcount(composer)
    print("REFRESH COMPLETE!")


# INITIAL RETRIEVAL OF SPOTIFY DATA FOR ALBUMS AND ARTISTS
def spotifygenerate(name):
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    notfound_count = 0
    error_count = 0
    errors = True
    while errors is True:
        errors = False
        i = 1
        composer = name
        # get works not in Spotify table
        works = db.session.query(WorkList).outerjoin(Spotify, Spotify.id == WorkList.id).filter(WorkList.composer == composer, Spotify.updated == None).all()
        # works = WorkList.query.filter_by(composer=composer).all()
        num_works = str(len(works))
        for work in works:
            # token expiry and refreshing
            if session['app_token_expire_time'] < datetime.now():
                session['app_token'] = sp.client_authorize()
                session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

            tracks = search_spotify_and_save(work.id)
            try:
                GroupAlbums(tracks, work)
                print("SUCCESS" + " " + work.id + " " + work.title + " <" + str(i) + " of " + num_works + ">")
            except Exception:
                output = "SPOTIFY GENERATE FAIL - " + work.id + " " + str(tracks) + " " + work.title
                output2 = "SPOTIFY GENERATE FAIL - " + work.id + " " + work.title
                if str(tracks[1]) == "429":
                    print(output)
                    errors = True
                elif str(tracks[1]) == "404":
                    print(output)
                    notfound_count += 1
                else:
                    print(output2)
                    error_count += 1
            i += 1

    # sum album counts
    works = db.session.query(WorkList).filter_by(composer=name).all()

    for work in works:
        work.album_count = work.albums.count()
    db.session.commit()

    # finish
    ctx.pop()
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    minutes = divmod(elapsed_time.total_seconds(), 60)

    message = "Initial load complete for " + name + ", " + str(error_count) + " unresolved errors, " + str(notfound_count) + " works not found. Took " + str(minutes[0]) + " minutes, " + str(minutes[1]) + " seconds."
    print(message)


# FILL IN ALBUMS WITH ALL WORK TRACKS
def fillalbums(name):
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    errors = True
    limit_exceeded_error = 0
    while errors is True:
        i = 1
        error_count = 0
        composer = name
        errors = False
        albums = WorkAlbums.query.filter_by(composer=composer, filled=False).all()

        for album in albums:
            # token expiry and refresh
            if session['app_token_expire_time'] < datetime.now():
                session['app_token'] = sp.client_authorize()
                session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

            db.session.query(Artists).filter_by(album_id=album.id).delete()
            db.session.commit()

            try:
                work = db.session.query(WorkList).filter_by(id=album.workid).first()
                tracks = search_album(album.album_id, work)
                SmartAlbums(tracks, work)

            except Exception as e:
                print("FILL ERROR " + work.id + " " + work.title + " " + album.album_id + " " + str(e))
                # logtext = "FILL ERROR " + work.id + " " + work.title + " " + album.album_id + " " + str(tracks)
                # logger.log_text(logtext, severity="ERROR")
                try:
                    int(tracks)
                    if int(tracks) == 429:
                        errors = True
                        limit_exceeded_error += 1
                        continue
                except Exception:
                    error_count += 1
                    continue

            print("Success " + work.id + " " + work.title + " <" + str(i) + " of " + str(len(albums)) + ">")
            i += 1

    ctx.pop()
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    minutes = divmod(elapsed_time.total_seconds(), 60)
    message = "Album fill complete for " + name + ", " + str(error_count) + " unresolved errors, " + str(limit_exceeded_error) + " resolved 429 errors. Took " + str(minutes[0]) + " minutes, " + str(minutes[1]) + " seconds."
    logger.log_text(message, severity="NOTICE")
    print(message)


# CLEAN UP ALBUMS DATABASE
def cleanup(name):
    # delete albums with no tracks.
    db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.score == 0).delete()
    db.session.commit()

    # delete spotify table records if no albums
    noalbums = db.session.query(Spotify).outerjoin(WorkAlbums, Spotify.id == WorkAlbums.workid).filter(WorkAlbums.id == None).all()
    for album in noalbums:
        db.session.query(Spotify).filter(Spotify.id == album.id).delete()
        db.session.commit()

    # re-sum album counts
    works = db.session.query(WorkList).filter_by(composer=name).all()

    for work in works:
        work.album_count = work.albums.count()
    db.session.commit()


# CHECK SPOTIFY FOR NEW ALBUMS AND RETRIEVE FOR EXISTING WORKS
def refreshalbums(name):
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    # get work list
    works = WorkList.query.filter_by(composer=name).all()
    num_works = str(len(works))

    # get new catalogued albums
    i = 1
    error_count = 0
    album_count = 0

    for work in works:
        newtracks = []
        tracks = []

        # token expiry and refreshing
        if session['app_token_expire_time'] < datetime.now():
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

        try:
            tracks = search_spotify_and_save(work.id)
            test = tracks[0]['album_id']
        except Exception:
            output = "SPOTIFY REFRESH FAIL - " + work.id + " " + work.title
            if str(tracks[1]) == "429":
                print("429 " + output)
                logger.log_text("429 " + output, severity="ERROR")
                error_count += 1
            elif str(tracks[1]) == "404":
                print("404 " + output)
            else:
                print("500 " + output)
                logger.log_text("500 " + output, severity="ERROR")
                error_count += 1
            i += 1
            continue

        for track in tracks:
            albumworkid = work.id + track['album_id']
            exists = db.session.query(WorkAlbums.id).filter_by(id=albumworkid).first() is not None

            if not exists:
                newtracks.append(track)

        if newtracks:
            GroupAlbums(newtracks, work)
            print("NEW ALBUMS " + " " + work.id + " " + work.title + " <" + str(i) + " of " + num_works + ">")
            album_count += 1
        else:
            print("No New Albums" + " " + work.id + " " + work.title + " <" + str(i) + " of " + num_works + ">")
        i += 1

    ctx.pop()
    print('Done!')
    message = str(album_count) + " works with new albums for " + name + ", " + str(error_count) + " unresolved errors."
    logger.log_text(message, severity="NOTICE")


# GET ALBUM IMAGE COVERS FROM SPOTIFY
def albumimgs(name):
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    # get albums for composer
    albums = db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.img == None).all()

    k = 0
    error_count = 0

    while k < len(albums):

        i = 0
        id_list = []
        album_list = []

        # token expiry and refreshing
        if session['app_token_expire_time'] < datetime.now():
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

        while i < 20 and k < len(albums):
            album_list.append(albums[k])
            id_list.append(albums[k].album_id)
            i += 1
            k += 1

        id_string = ','.join(id_list)

        response = sp.get_albums(id_string)

        results = response.json()

        if results.get('error'):
            print('FAIL')
            error_count += 1
            continue

        j = 0
        for album in album_list:
            try:
                album.img = results['albums'][j]['images'][0]['url']
            except Exception:
                pass

            # print(album.id + " - " + str(album.img))
            j += 1

        db.session.commit()
        print("Completed " + str(k) + " of " + str(len(albums)))

    # finish
    ctx.pop()
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    minutes = divmod(elapsed_time.total_seconds(), 60)

    message = "Album image fill complete for " + name + ". " + str(error_count) + " errors. Took " + str(minutes[0]) + " minutes, " + str(minutes[1]) + " seconds."
    logger.log_text(message, severity="NOTICE")
    print(message)


# RETRIEVE ADDITIONAL INFORMATION FROM SPOTIFY FOR ALBUMS
def spotifypull(name):
    start_time = datetime.utcnow()
    ctx = current_app.test_request_context()
    ctx.push()

    # get spotify token
    if not session.get('app_token'):
        session['app_token'] = sp.client_authorize()
        session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    albums = db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.label == None).all()

    k = 0
    error_count = 0

    while k < len(albums):

        i = 0
        id_list = []
        album_list = []

        # token expiry and refreshing
        if session['app_token_expire_time'] < datetime.now():
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

        while i < 20 and k < len(albums):
            album_list.append(albums[k])
            id_list.append(albums[k].album_id)
            i += 1
            k += 1

        id_string = ','.join(id_list)

        response = sp.get_albums(id_string)

        results = response.json()

        if results.get('error'):
            print('FAIL')
            error_count += 1
            continue

        j = 0
        for album in album_list:
            try:
                # album.spotify_data = json.dumps(results['albums'][j]['artists'])
                album.title = results['albums'][j]['name']
                album.label = results['albums'][j]['label']
                album.track_count = results['albums'][j]['total_tracks']
                album.album_type = results['albums'][j]['album_type']
            except Exception:
                pass

            # print(album.id + " - " + str(album.img))
            j += 1

        db.session.commit()
        print("Completed " + str(k) + " of " + str(len(albums)))

    # finish
    ctx.pop()
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    minutes = divmod(elapsed_time.total_seconds(), 60)

    message = "Album data fill complete for " + name + ". " + str(error_count) + " errors. Took " + str(minutes[0]) + " minutes, " + str(minutes[1]) + " seconds."
    logger.log_text(message, severity="NOTICE")
    print(message)


# COUNTS THE TRACKS FOR A COMPOSER'S ALBUMS
def trackcount(name):
    start_time = datetime.utcnow()

    # get albums for composer
    albums = db.session.query(WorkAlbums).filter(WorkAlbums.composer == name, WorkAlbums.work_track_count == None).all()

    k = 0
    error_count = 0

    while k < len(albums):

        i = 0
        album_list = []

        while i < 50 and k < len(albums):
            album_list.append(albums[k])

            i += 1
            k += 1

        j = 0
        for album in album_list:
            try:
                data = json.loads(album.data)
                album.work_track_count = len(data['tracks'])
            except Exception:
                error_count += 1
                pass

            j += 1

        db.session.commit()
        print("Completed " + str(k) + " of " + str(len(albums)))

    # finish
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    minutes = divmod(elapsed_time.total_seconds(), 60)

    message = "Track count complete for " + name + ". " + str(error_count) + " errors. Took " + str(minutes[0]) + " minutes, " + str(minutes[1]) + " seconds."
    logger.log_text(message, severity="NOTICE")
    print(message)


# DEFUNCT: REGENERATE ARTISTS LIST (for old.composerexplorer.com)
@ bp.cli.command()
def regenerateartists():
    composers = []
    for value in db.session.query(Artists.name).order_by(Artists.name).distinct():
        composers.append(value[0])

    artist_list = db.session.query(ArtistList).first()
    artist_list.content = json.dumps(composers, ensure_ascii=False)
    artist_list.timestamp = datetime.utcnow()
    db.session.commit()


# SPLITS WORK TITLES INTO TITLE AND LYRICS
@ bp.cli.command()
@ click.argument("name")
def splitsongs(name):
    works = db.session.query(WorkList).filter_by(composer=name)

    for work in works:
        title = work.title
        splitlist = title.split("(\"")
        try:
            lyrics = splitlist[1]
            lyrics = lyrics.replace("\")", "")
            title = splitlist[0].strip()
            work.nickname = lyrics
            work.title = title

        except Exception:
            pass

    db.session.commit()


# SPLITS WORK TITLES INTO TITLE AND LYRICS
@ bp.cli.command()
@ click.argument("name")
def splitsongs2(name):
    works = db.session.query(WorkList).filter_by(composer=name)

    for work in works:
        title = work.title
        splitlist = title.split("(")
        try:
            lyrics = splitlist[1]
            lyrics = lyrics.replace(")", "")
            title = splitlist[0].strip()
            work.nickname = lyrics
            work.title = title

        except Exception:
            pass

    db.session.commit()


# TRIMS EXCESS WHITESPACE FROM TITLE
@ bp.cli.command()
@ click.argument("name")
def trimtitles(name):
    works = db.session.query(WorkList).filter_by(composer=name)

    for work in works:
        title = work.title
        trimmed = title.strip()
        work.title = trimmed
        print(work.title)

    db.session.commit()


# DELETES AN ARTIST FROM ALBUM DATA (DANGEROUS)
# @ bp.cli.command()
# @ click.argument("name")
def deleteartist(name):
    search = "%{}%".format(name)

    # get albums for composer , WorkAlbums.label == None
    albums = WorkAlbums.query.filter(WorkAlbums.artists.ilike(search)).all()
    print("QUERY DONE")

    for album in albums:
        data = json.loads(album.data)

        artists_list = data['artists'].split(', ')
        minor_artists_list = data['minor_artists'].split(', ')
        all_artists_list = data['all_artists'].split(', ')

        try:
            artists_list.remove(name)
        except Exception:
            pass
        try:
            minor_artists_list.remove(name)
        except Exception:
            pass
        try:
            all_artists_list.remove(name)
        except Exception:
            pass

        parent_artists_list = album.artists.split(', ')

        try:
            parent_artists_list.remove(name)
        except Exception:
            pass

        data['artists'] = ", ".join(artists_list)
        data['minor_artists'] = ", ".join(minor_artists_list)
        data['all_artists'] = ", ".join(all_artists_list)

        album.artists = ", ".join(parent_artists_list)

        album.data = json.dumps(data)

    db.session.commit()
    print("DONE")


# SPLITS WORK TITLES BEARING OPUS INTO OPUS AND TITLE
@ bp.cli.command()
def splitcat():

    name = input("Enter composer short name: ")
    works = WorkList.query.filter_by(composer=name).all()

    for work in works:
        title_array = work.title.rpartition(', op')

        if not title_array[0]:
            work.title = title_array[2].strip()
        else:
            work.title = title_array[0].strip()
            work.cat = "Op" + title_array[2].strip()
        print(work.cat, work.title)

    db.session.commit()
    print("Done! Updated " + str(len(works)) + " works.")


# SPLITS WORK TITLES BEARING "FOR..." INTO TITLE
@ bp.cli.command()
def splittitle():

    name = input("Enter composer short name: ")
    works = WorkList.query.filter_by(composer=name).all()

    for work in works:
        title_array = work.title.rpartition(', for')

        if not title_array[0]:
            work.title = title_array[2].strip()
        else:
            work.title = title_array[0].strip()
        print(work.title)

    db.session.commit()
    print("Done! Updated " + str(len(works)) + " works.")


# UPDATE A GENRE NAME
@ bp.cli.command()
def updategenre():

    while True:
        genre_old = input("Enter old genre name: ")
        genre_new = input('Enter new genre name: ')

        works = WorkList.query.filter_by(genre=genre_old).all()

        for work in works:
            work.genre = genre_new

        db.session.commit()
        print("Done! Updated " + str(len(works)) + " works.")


# ADD A SEARCH TERM FOR A GENRE (ie. Add "Harpsichord" search term for "Keyboard" genres)
@ bp.cli.command()
def updatesearch():

    while True:
        genre = input("Enter genre name: ")
        search_term = input('Enter search term: ')

        # works = WorkList.query.filter_by(genre=genre).all()
        search = "%{}%".format(genre)
        works = WorkList.query.filter(WorkList.genre.ilike(search)).all()

        for work in works:
            print(work.genre)
            work.search = search_term

        db.session.commit()
        print("Done! Updated " + str(len(works)) + " works.")

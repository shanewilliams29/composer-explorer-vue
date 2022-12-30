from app import db, log, sp
from app.models import ComposerList, WorkList, Spotify
import re
import unidecode


def search_spotify_and_save(_id):

    # logging

    log_name = "crawl-log"
    logger = log.logger(log_name)
    logtext = str(_id) + " "
    # logger.log_text(text)

    resultslist = []
    work = WorkList.query.filter_by(id=_id).first_or_404()
    logtext = logtext + str(work) + " "

    composer = ComposerList.query.filter_by(name_short=work.composer).first()
    tracklist = []

    if not composer.general:
        logtext = logtext + "OPUS" + " "
        # logger.log_text(logtext)
        # if work.search:
        #     search_string = work.composer + " " + work.search + " " + work.cat
        # else:
        search_string = work.composer + " " + work.title + " " + work.cat

        response = sp.search(search_string)
        results = response.json()
        resultslist.append(results)

        try:
            test = results['tracks']['items']
        except:
            return "Error with Spotify token.", 403

        # do more general search on opus no. if no results.
        if work.cat.strip() and str(results['tracks']['total']) == "0" and work.cat.strip() != "Op. posth.":
            logtext = logtext + "No-ONLY" + " "
            search_string = work.composer + " " + work.cat
            response = sp.search(search_string)
            results = response.json()
            resultslist.append(results)

        # get more results
        nexturl = results['tracks']['next']
        seconds = 60
        resultslist = sp.get_more_results(resultslist, nexturl, seconds, _id)
        if resultslist == "429":
            logtext = logtext + "<429 RATE EXCEEDED>"
            logger.log_text(logtext, severity="ERROR")
            return "API Rate Limit exceeded", 429

        logtext = logtext + "<200 OK>"
        # logger.log_text(logtext)

        # continue with program
        track = {}
        artistlist = []

        for results in resultslist:
            items = results['tracks']['items']
            track = {}
            artistlist = []

            for item in items:
                # check that composer appears in artists and skip if not
                artists = item['artists']
                checklist = []
                for artist in artists:
                    checklist.append(artist['name'])
                checkstring = ' '.join(checklist)
                if not composer.name_full in checkstring:  # changed to full name
                    continue

                if work.cat.strip():
                    cat1 = re.sub(r'\W+', ' ', work.cat.lower().strip()).replace(" ", "") + " "
                    cat2 = re.sub(r'\W+', ' ', work.cat.lower().strip()) + " "
                    track1 = re.sub(r'\W+', ' ', item['name'].lower()) + " "

                    # print("M " + cat1 + " or " + cat2)
                    # print("S " + track1)
                    if cat1 not in track1:
                        if cat2 not in track1:
                            # print("REJECT " + track1)
                            # print('REJECT')
                            continue

                    # print("KEEP " + track1)
                    # check that the no. appears in track name. Pass if no no.
                    no1 = re.sub(r'\W+', ' ', work.title.lower())
                    try:
                        track1 = re.sub(r'\W+', ' ', item['name'].lower())

                        no1 = no1.split(" no", 1)[1].replace(" ", "")
                        no1 = no1[0:3]
                        no1 = re.search(r'\d+', no1).group()
                        no2 = "no " + no1 + " "
                        no1 = "no" + no1 + " "

                        # print("M " + no1 + " or " + no2)
                        # print("S " + track1)
                        if no1 not in track1:
                            if no2 not in track1:
                                # print('REJECT')
                                continue
                    except:
                        # check that work title appears in track name for some suite heavy composers
                        if work.composer == "Debussy":
                            title1 = " " + re.sub(r'\W+', ' ', work.title.lower())
                            title1 = title1.split(" in ", 1)[0].replace(" ", "")

                            track1 = " " + re.sub(r'\W+', ' ', item['name'].lower())
                            track1 = track1.split(" in ", 1)[0].replace(" ", "")

                            title1 = unidecode.unidecode(title1)
                            track1 = unidecode.unidecode(track1)

                            #print("M " + title1)
                            #print("S " + track1)
                            if title1.strip() not in track1.strip():
                                # print('REJECT')
                                continue
                        else:
                            pass

                    # # second opus check
                    # title = item['name']
                    # titlenos = " ".join(re.findall('\d+', title))
                    # titlenolist = titlenos.split()
                    # titlenolist = [int(i) for i in titlenolist]  # array of numbers in spotify title
                    # #print("s " + str(titlenolist) + " " + title)

                    # mytitle = work.title + " " + work.cat
                    # mytitlenos = " ".join(re.findall('\d+', mytitle))
                    # mytitlenolist = mytitlenos.split()
                    # mytitlenolist = [int(i) for i in mytitlenolist]  # array of numbers in my title
                    # #print("m " + str(mytitlenolist))

                    # flag = False  # check that all integers in my title appear in spotify title
                    # for integer in mytitlenolist:
                    #     if integer not in titlenolist:
                    #         # print("PASS")
                    #         flag = True
                    # if flag:
                    #     flag = False
                    #     continue
                else:
                    # check that title apears in track
                    # if work.search:
                    #     title1 = " " + re.sub(r'\W+', ' ', work.search.lower()).replace(" ", "")
                    #     track1 = " " + re.sub(r'\W+', ' ', item['name'].lower()).replace(" ", "")

                    #     title1 = unidecode.unidecode(title1)
                    #     track1 = unidecode.unidecode(track1)

                    #     # print("M " + title1)
                    #     # print("S " + track1)
                    #     if title1.strip() not in track1.strip():
                    #         # print('REJECT')
                    #         continue

                    # if not work.search:
                    title1 = " " + re.sub(r'\W+', ' ', work.title.lower()).replace(" ", "")
                    track1 = " " + re.sub(r'\W+', ' ', item['name'].lower()).replace(" ", "")

                    title1 = unidecode.unidecode(title1)
                    track1 = unidecode.unidecode(track1)

                    # print("M " + title1)
                    # print("S " + track1)
                    if title1.strip() not in track1.strip():
                        # print('REJECT')
                        continue

                # get relevant info
                track['track_name'] = item['name']
                track['album_name'] = item['album']['name']
                track['album_id'] = item['album']['id']
                track['album_uri'] = item['album']['uri']
                track['release_date'] = item['album']['release_date']
                track['disc_no'] = item['disc_number']
                track['track_no'] = item['track_number']
                track['popularity'] = item['popularity']
                track['track_id'] = item['id']
                track['track_uri'] = item['uri']
                try:
                    track['album_img'] = item['album']['images'][1]['url']
                except:
                    track['album_img'] = ""

                # get album year only
                year = track['release_date'].split('-')[0]
                track['release_date'] = year

                # get list of album artists but remove composer
                for artist in artists:
                    if not work.composer.split()[-1] in artist['name']:
                        artistlist.append(artist['name'].replace("/", ", "))

                track['track_artists'] = ', '.join(artistlist)
                track['track_artists'].replace("/", ", ")
                if not track['track_artists']:
                    track['track_artists'] = composer.name_full
                tracklist.append(track)
                track = {}
                artistlist = []

    # GENERAL SEARCH: perform search without opus if no results or opera
    if composer.general or work.genre.lower().strip() == "opera" or work.genre.lower().strip() == "stage work":
        # if "cake" is "cake":  # is this correct?
        search_string = work.composer + " " + work.title
        response = sp.search(search_string)
        results = response.json()
        if str(results['tracks']['total']) == "0":
            return 'No Spotify tracks found.', 404
        resultslist.append(results)

        # get more results
        nexturl = results['tracks']['next']
        seconds = 60
        resultslist = sp.get_more_results(resultslist, nexturl, seconds, _id)
        if resultslist == "429":
            return "API Rate Limit exceeded", 429

        # loop to extract data
        for results in resultslist:
            items = results['tracks']['items']
            track = {}
            artistlist = []

            for item in items:
                # check that composer appears in artists and skip if not
                artists = item['artists']
                checklist = []
                for artist in artists:
                    checklist.append(artist['name'])
                checkstring = ' '.join(checklist)
                if not composer.name_full in checkstring:
                    continue

                # if work.search:
                #     title1 = " " + re.sub(r'\W+', ' ', work.search.lower()).replace(" ", "")
                #     track1 = " " + re.sub(r'\W+', ' ', item['name'].lower()).replace(" ", "")

                #     title1 = unidecode.unidecode(title1)
                #     track1 = unidecode.unidecode(track1)

                #     # print("M " + title1)
                #     # print("S " + track1)
                #     if title1.strip() not in track1.strip():
                #         # print('REJECT')
                #         continue

                # if not work.search:
                title1 = " " + re.sub(r'\W+', ' ', work.title.lower()).replace(" ", "")
                track1 = " " + re.sub(r'\W+', ' ', item['name'].lower()).replace(" ", "")

                title1 = unidecode.unidecode(title1)
                track1 = unidecode.unidecode(track1)

                # print("M " + title1)
                # print("S " + track1)
                if title1.strip() not in track1.strip():
                    # print('REJECT')
                    continue

                # get relevant info
                track['track_name'] = item['name']
                track['album_name'] = item['album']['name']
                track['album_id'] = item['album']['id']
                track['album_uri'] = item['album']['uri']
                track['release_date'] = item['album']['release_date']
                track['disc_no'] = item['disc_number']
                track['track_no'] = item['track_number']
                track['popularity'] = item['popularity']
                track['track_id'] = item['id']
                track['track_uri'] = item['uri']
                try:
                    track['album_img'] = item['album']['images'][1]['url']
                except:
                    track['album_img'] = ""

                # get album year only
                year = track['release_date'].split('-')[0]
                track['release_date'] = year

                # get list of album artists but remove composer
                for artist in artists:
                    if not work.composer.split()[-1] in artist['name']:
                        artistlist.append(artist['name'].replace("/", ", "))

                track['track_artists'] = ', '.join(artistlist)
                if not track['track_artists']:
                    track['track_artists'] = composer.name_full
                tracklist.append(track)
                track = {}
                artistlist = []
    # sort
    tracklist = sorted(tracklist, key=lambda i: (i['album_id'], i['disc_no'], i['track_no']))

    # get unique tracks
    newtracks = []
    for i in range(0, len(tracklist)):
        if i > 0:
            if tracklist[i]['track_id'] != tracklist[i - 1]['track_id']:
                newtracks.append(tracklist[i])
        else:
            newtracks.append(tracklist[i])

    # check if any results and return error if none
    if not newtracks:
        return 'No Spotify tracks found.', 404

    # encode and store in database

    existingspotify = Spotify.query.filter_by(id=_id).first()
    if existingspotify:
        existingspotify.results = ""
        db.session.commit()
    else:
        spotifydata = Spotify(id=_id, results="", composer=composer.name_short)
        db.session.add(spotifydata)
        db.session.commit()

    return newtracks


def search_album(uri, work):

    resultslist = []

    search_string = uri

    response = sp.get_album(search_string)
    results = response.json()

    try:
        test = results['tracks']
    except:
        return results['error']['status']

    results2 = []
    resultslist.append(results)
    # print(results['tracks']['next'])
    tracks_next = results['tracks']['next']

    while tracks_next:
        response = sp.get_more_album(tracks_next)
        results2 = response.json()
        try:
            nexturl = results2['next']
        except:
            return results2['error']['status']

        resultslist.append(results2)
        tracks_next = results2['next']
        # print("SEARCH MORE")

    composer = ComposerList.query.filter_by(name_short=work.composer).first()

    # continue with program
    track = {}
    tracklist = []
    artistlist = []

    for listitem in resultslist:
        try:
            items = listitem['tracks']['items']
        except:
            items = listitem['items']

        for item in items:
            # print(item)
            # get relevant info
            artists = item['artists']

            # check composer in artists field and skip if not
            if composer.name_full not in str(artists):
                continue

            track['track_name'] = item['name']
            track['album_name'] = results['name']
            track['album_id'] = results['id']
            track['album_uri'] = results['uri']
            track['release_date'] = results['release_date']
            track['disc_no'] = item['disc_number']
            track['track_no'] = item['track_number']
            track['popularity'] = results['popularity']
            track['track_id'] = item['id']
            track['track_uri'] = item['uri']
            try:
                track['album_img'] = results['images'][1]['url']
            except:
                track['album_img'] = ""

            # get album year only
            year = results['release_date'].split('-')[0]
            track['release_date'] = year

            # get list of album artists but remove composer
            count = 0
            for artist in artists:
                if count < 100:
                    if not work.composer in artist['name']:
                        artistlist.append(artist['name'].replace("/", ", "))
                    count += 1
            track['track_artists'] = ', '.join(artistlist)
            track['track_artists'].replace("/", ", ")
            if not track['track_artists']:
                track['track_artists'] = composer.name_full
            tracklist.append(track)
            track = {}
            artistlist = []

    # sort
    tracklist = sorted(tracklist, key=lambda i: (i['album_id'], i['disc_no'], i['track_no']))

    # get unique tracks
    newtracks = []
    for i in range(0, len(tracklist)):
        if i > 0:
            if tracklist[i]['track_id'] != tracklist[i - 1]['track_id']:
                newtracks.append(tracklist[i])
        else:
            newtracks.append(tracklist[i])

    # check if any results and return error if none
    if not newtracks:
        return 'No Spotify tracks found.', 404
    # print(tracklist)
    return tracklist
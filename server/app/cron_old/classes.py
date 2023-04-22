from app import db
import collections
from app.models import WorkAlbums, Artists, ComposerList
import jsonpickle
import hashlib
import re
import unidecode


# groups tracks onto albums and stores in database
class SmartAlbums(object):

    def __init__(self, tracks, work):
        # get unique albums
        newlist = []
        artistlist = []

        # get composer
        composer = ComposerList.query.filter_by(name_short=work.composer).first()

        for i in range(0, len(tracks)):
            if i > 0:
                if tracks[i]['album_id'] != tracks[i - 1]['album_id']:
                    newlist.append(tracks[i])
            else:
                newlist.append(tracks[i])

        for item in newlist:
            item['tracks'] = []
            item['queue'] = []
            item['artists'] = []
            item['track_count'] = 0
            item['popularity'] = 0
            albumartists = []

            for i in range(0, len(tracks)):
                # print(work.title + " in " + tracks[i]['track_name'])

                # check that opus appears in track name
                if work.cat.strip() and work.cat.lower().strip() != "op. posth." and work.genre.lower() != "opera" and work.genre.lower() != "ballet" and not composer.general:
                    cat1 = re.sub(r'\W+', ' ', work.cat.lower().strip()).replace(" ", "") + " "
                    cat2 = re.sub(r'\W+', ' ', work.cat.lower().strip()) + " "
                    track1 = re.sub(r'\W+', ' ', tracks[i]['track_name'].lower()) + " "

                    # print("M " + cat1 + " or " + cat2)
                    # print("S " + track1)
                    if cat1 not in track1:
                        if cat2 not in track1:
                            # print('REJECT')
                            continue

                    # check that the no. appears in track name. Pass if no no.
                    no1 = re.sub(r'\W+', ' ', work.title.lower())

                    try:
                        track1 = re.sub(r'\W+', ' ', tracks[i]['track_name'].lower())

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
                        # check that work title appears in track name for suites
                        # if work.composer == "Debussy":
                        if work.suite:
                            title1 = " " + re.sub(r'\W+', ' ', work.title.lower())
                            # title1 = title1.split(" in ", 1)[0].replace(" ", "")
                            title1 = ''.join([i for i in title1 if not i.isdigit()])  # remove digits

                            track1 = " " + re.sub(r'\W+', ' ', tracks[i]['track_name'].lower())
                            # track1 = track1.split(" in ", 1)[0].replace(" ", "")

                            title1 = unidecode.unidecode(title1)
                            track1 = unidecode.unidecode(track1)

                            # print("M " + title1)
                            # print("S " + track1)
                            if title1.strip() not in track1.strip():
                                # print('REJECT')
                                continue
                        else:
                            pass

                    # print('ACCEPT')
                    if item['album_id'] == tracks[i]['album_id']:
                        item['queue'].append("spotify:track:" + tracks[i]['track_id'])
                        item['tracks'].append([tracks[i]['track_name'], tracks[i]['track_id']])
                        item['track_count'] += 1
                        artists = tracks[i]['track_artists'].split(', ')
                        for artist in artists:
                            albumartists.append(artist)

                        if tracks[i]['popularity'] > item['popularity']:
                            item['popularity'] = tracks[i]['popularity']

                # check that work title appears in track name
                else:
                    titleA = " " + re.sub(r'\W+', ' ', work.title.lower())
                    title1 = titleA.split(" in ", 1)[0].replace(" ", "")
                    try:
                        letter1 = titleA.split(" in ", 1)[1][0]
                    except:
                        letter1 = ""

                    trackA = " " + re.sub(r'\W+', ' ', tracks[i]['track_name'].lower())
                    track1 = trackA.split(" in ", 1)[0].replace(" ", "")
                    try:
                        letter2 = trackA.split(" in ", 1)[1][0]
                    except:
                        letter2 = ""

                    title1 = unidecode.unidecode(title1) + letter1
                    track1 = unidecode.unidecode(track1) + letter2

                    # print("M " + title1)
                    # print("S " + track1)
                    if title1.strip() not in track1.strip():
                        pass
                        # print('REJECT')
                    else:
                        # print('ACCEPT')
                        if item['album_id'] == tracks[i]['album_id']:
                            item['queue'].append("spotify:track:" + tracks[i]['track_id'])
                            item['tracks'].append([tracks[i]['track_name'], tracks[i]['track_id']])
                            item['track_count'] += 1
                            artists = tracks[i]['track_artists'].split(', ')
                            for artist in artists:
                                albumartists.append(artist)

                            if tracks[i]['popularity'] > item['popularity']:
                                item['popularity'] = tracks[i]['popularity']

            counter = collections.Counter(albumartists)
            artists = counter
            item['artists'] = ", ".join(list(dict(counter.most_common(2)).keys()))
            item['minor_artists'] = ", ".join(list(set((dict(counter.most_common(8)).keys())) - set(dict(counter.most_common(2)).keys())))
            item['all_artists'] = ", ".join(list(dict(counter).keys()))
            item['score'] = item['track_count']

            if work.composer == "Chopin":
                cutoff = 1
            else:
                cutoff = 3

            if item['score'] > cutoff:
                item['score'] = cutoff
            item['score'] = item['score'] * 33.3 + item['popularity']

            if work.genre.lower().strip() == "opera" or work.genre.lower().strip() == "ballet":
                item['score'] = item['track_count']
                if item['score'] > 20:
                    item['score'] = 20
                item['score'] = item['score'] * 5 + item['popularity']

            # if work.composer == "Chopin":
            #     item['score'] = item['popularity']

            # cue up the songs
            for i in range(1, len(item['queue']) + 1):
                item['tracks'][-i].append(" ".join(item['queue'][-i:]))
            del(item['queue'])

            # delete unnecessary info
            del(item['track_artists'])
            del(item['track_id'])
            del(item['track_name'])
            del(item['track_no'])
            del(item['track_uri'])

            data = jsonpickle.encode(item)

            album = WorkAlbums(id=work.id + item['album_id'], workid=work.id, album_id=item['album_id'], composer=work.composer, artists=item['all_artists'], score=item['score'], data=data, filled=True)

            for person in artists:
                artist_id = hashlib.md5((person + work.id + item['album_id']).encode('utf-8')).hexdigest()
                artist = Artists(id=artist_id, name=person, workid=work.id, album_id=work.id + item['album_id'], composer=work.composer, count=artists[person])
                artistlist.append(artist)

        db.session.merge(album)
        db.session.add_all(artistlist)
        db.session.commit()


class GroupAlbums(object):

    def __init__(self, tracks, work):
        # get unique albums
        newlist = []
        artistlist = []
        albumlist = []

        for i in range(0, len(tracks)):
            if i > 0:
                if tracks[i]['album_id'] != tracks[i - 1]['album_id']:
                    newlist.append(tracks[i])
            else:
                newlist.append(tracks[i])

        for item in newlist:
            item['tracks'] = []
            item['queue'] = []
            item['artists'] = []
            item['track_count'] = 0
            item['popularity'] = 0
            albumartists = []

            for i in range(0, len(tracks)):
                if item['album_id'] == tracks[i]['album_id']:
                    item['queue'].append("spotify:track:" + tracks[i]['track_id'])
                    item['tracks'].append([tracks[i]['track_name'], tracks[i]['track_id']])
                    item['track_count'] += 1
                    artists = tracks[i]['track_artists'].split(', ')
                    for artist in artists:
                        albumartists.append(artist)

                    if tracks[i]['popularity'] > item['popularity']:
                        item['popularity'] = tracks[i]['popularity']

            counter = collections.Counter(albumartists)
            artists = counter
            item['artists'] = ", ".join(list(dict(counter.most_common(2)).keys()))
            item['minor_artists'] = ", ".join(list(set((dict(counter.most_common(8)).keys())) - set(dict(counter.most_common(2)).keys())))
            item['all_artists'] = ", ".join(list(dict(counter).keys()))
            item['score'] = item['track_count']

            if work.composer == "Chopin":
                cutoff = 1
            else:
                cutoff = 3

            if item['score'] > cutoff:
                item['score'] = cutoff
            item['score'] = item['score'] * 33.3 + item['popularity']

            if work.genre.lower().strip() == "opera" or work.genre.lower().strip() == "ballet":
                item['score'] = item['track_count']
                if item['score'] > 20:
                    item['score'] = 20
                item['score'] = item['score'] * 5 + item['popularity']

            # if work.composer == "Chopin":
            #     item['score'] = item['popularity']

            # cue up the songs
            for i in range(1, len(item['queue']) + 1):
                item['tracks'][-i].append(" ".join(item['queue'][-i:]))
            del(item['queue'])

            # delete unnecessary info
            del(item['track_artists'])
            del(item['track_id'])
            del(item['track_name'])
            del(item['track_no'])
            del(item['track_uri'])

            data = jsonpickle.encode(item)

            album = WorkAlbums(id=work.id + item['album_id'], workid=work.id, album_id=item['album_id'], composer=work.composer, artists=item['all_artists'], score=item['score'], data=data)
            albumlist.append(album)

            for person in artists:
                artist_id = hashlib.md5((person + work.id + item['album_id']).encode('utf-8')).hexdigest()
                artist = Artists(id=artist_id, name=person, workid=work.id, album_id=work.id + item['album_id'], composer=work.composer, count=artists[person])
                artistlist.append(artist)

        db.session.add_all(albumlist)
        db.session.commit()
        db.session.add_all(artistlist)
        db.session.commit()

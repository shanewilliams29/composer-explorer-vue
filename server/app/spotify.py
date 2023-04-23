from flask import session
import six
import base64
import requests
import urllib.parse
from datetime import datetime, timedelta


class SpotifyAPI(object):
    def __init__(self, client_id, client_secret, client_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_url = client_url

    def authorize(self):
        client_url = urllib.parse.quote(self.client_url)
        url = 'https://accounts.spotify.com/authorize?client_id=' + self.client_id + '&response_type=code&redirect_uri=' + client_url + '&scope=streaming app-remote-control user-read-playback-state user-read-playback-position user-modify-playback-state user-read-private playlist-read-private user-read-email playlist-modify-public user-read-currently-playing streaming'
        return url

    def client_authorize(self):
        try:
            OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
            payload = {'grant_type': 'client_credentials'}
            auth_header = base64.b64encode(six.text_type(self.client_id + ":" + self.client_secret).encode("ascii"))
            headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
            response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)

            token = response.json()['access_token']
            return token
        except KeyError:
            return "INVALID"

    def get_token(self, code):
        try:
            OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
            payload = {'grant_type': 'authorization_code',
                       'code': code,
                       'redirect_uri': self.client_url}
            auth_header = base64.b64encode(six.text_type(self.client_id + ":" + self.client_secret).encode("ascii"))
            headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
            response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)
            response.json()['access_token']
            return response
        except KeyError:
            return "INVALID"

    def refresh_token(self):
        try:
            OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
            payload = {'grant_type': 'refresh_token',
                       'refresh_token': session['refresh_token']}
            auth_header = base64.b64encode(six.text_type(self.client_id + ":" + self.client_secret).encode("ascii"))
            headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
            response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)
            token = response.json()['access_token']
            return token
        except:
            return "INVALID"

    def create_playlist(self, new_playlist, userid):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(session['spotify_token']),
        }
        data = '{"name":"' + new_playlist + '","description":"Playlist created with ComposerExplorer.com"}'
        response = requests.post('https://api.spotify.com/v1/users/' + userid + '/playlists', headers=headers, data=data)
        return response

    def add_to_playlist(self, playlist_id, uristring):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(session['spotify_token']),
        }
        params = (
            ('uris', uristring),
        )
        response = requests.post('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', headers=headers, params=params)
        return response

    def get_user(self):
        headers = {
            'Authorization': 'Bearer {}'.format(session['spotify_token']),
        }
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        return response

    def search(self, search_string):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        params = (
            ('q', search_string),
            ('type', 'track'),
            ('limit', '50'),
        )
        response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        return response

    def get_next_search_page(self, nexturl):

        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get(nexturl, headers=headers)
        return response

    def search_spotify_by_url(self, url):

        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get(url, headers=headers)
        return response

    def get_more_results(self, resultslist, nexturl, time, _id):
        stoptime = datetime.now() + timedelta(seconds=time)
        while nexturl and datetime.now() < stoptime:
            headers = {
                'Authorization': 'Bearer {}'.format(session['app_token']),
            }
            response = requests.get(nexturl, headers=headers)
            results = response.json()
            try:
                nexturl = results['tracks']['next']
            except:
                if results['error']['status'] == 429:
                    resultslist = "429"
                    return resultslist
                break
            resultslist.append(results)
        return resultslist

    def get_album(self, albumid):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get('https://api.spotify.com/v1/albums/' + albumid, headers=headers)
        return response

    def get_albums(self, albumids):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get('https://api.spotify.com/v1/albums?ids=' + albumids, headers=headers)
        return response

    def get_more_album(self, url):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get(url, headers=headers)
        return response

    def get_artists(self, artistids):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get('https://api.spotify.com/v1/artists?ids=' + artistids, headers=headers)
        return response

    def get_tracks(self, trackids):
        headers = {
            'Authorization': 'Bearer {}'.format(session['app_token']),
        }
        response = requests.get('https://api.spotify.com/v1/tracks?ids=' + trackids, headers=headers)
        return response
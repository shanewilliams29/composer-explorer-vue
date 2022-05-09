from flask import session
import six
import base64
import requests
import urllib.parse
import json


class SpotifyAPI(object):
    def __init__(self, client_id, client_secret, client_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_url = client_url

    def authorize(self):
        client_url = urllib.parse.quote(self.client_url)
        url = 'https://accounts.spotify.com/authorize?client_id=' + self.client_id + '&response_type=code&redirect_uri=' + client_url + '&scope=user-read-playback-state user-read-playback-position user-modify-playback-state user-read-private playlist-read-private user-read-email playlist-modify-public user-read-currently-playing streaming'
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


class SortFilter(object):

    def get_era_filter(self, period):
        date_minmax = []

        with open('app/static/eras_filter.json') as f:
            periodArray = json.load(f)

            for era in periodArray:
                if era[0] == period:
                    if era[0] == "romantic" or era[0] == "20th":
                        date_minmax = [era[1], era[2], "region"]
                        break
                    else:
                        date_minmax = [era[1], era[2], "birth"]
                        break
                elif period == "common":
                    date_minmax = [1500, 1907, "region"]
                elif period == "early":
                    date_minmax = [1000, 1600, "birth"]
                elif period == "all":
                    date_minmax = [1000, 2051, "region"]
                else:
                    date_minmax = [1500, 2051, "region"]

        return date_minmax

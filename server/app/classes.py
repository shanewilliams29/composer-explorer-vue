from flask import session
import six
import base64
import requests
import urllib.parse


class SpotifyAPI(object):
    def __init__(self, client_id, client_secret, client_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_url = client_url

    def authorize(self):
        client_url = urllib.parse.quote(self.client_url)
        url = 'https://accounts.spotify.com/authorize?client_id=' + self.client_id + '&response_type=code&redirect_uri=' + client_url + '&scope=user-read-playback-state user-modify-playback-state user-read-private playlist-read-private user-read-email playlist-modify-public user-read-currently-playing streaming'
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

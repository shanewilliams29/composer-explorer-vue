from test_secrets import os
import unittest
import json
from app import create_app, db
from app.models import User, WorkAlbums

app = create_app()
print("\nNote: Composer 'Wagner' must be loaded in database for tests to succeed.\n")


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_get_performer(self):

        performer_id = '4irur0XnWruVmdJKoIp2d6'
        response = self.client.get('/api/getperformer', query_string={'id': performer_id})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('name', data['artist'])

    def test_get_performerbyname(self):

        name = 'Waltraud Meier'
        response = self.client.get('/api/getperformerbyname', query_string={'name': name})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('id', data['artist'])

    def test_get_albumworks(self):

        album_id = '6BIzBPVDbAw4DdyMOENCFe'
        response = self.client.get('/api/getalbumworks', query_string={'album_id': album_id})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertIn('liked_albums', data)

    def test_get_onealbum(self):

        album_id = '6BIzBPVDbAw4DdyMOENCFe'
        response = self.client.get('/api/getonealbum', query_string={'id': album_id})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['albums']), 0)
        self.assertGreater(len(data['composer']), 0)

        for album in data['albums']:
            self.assertIn('id', album)
            self.assertIn('img_big', album)
            self.assertIn('label', album)
            self.assertIn('track_count', album)
            self.assertIn('composer', album)
            self.assertIn('duration', album)
            self.assertIn('score', album)
            self.assertIn('artists', album)

    def test_get_albumsview(self):
        query = {
            'page': 1,
            'composer': 'Wagner',
            'artist': 'Sir Georg Solti',
            'era': 'romantic',
            'work': 'Tristan und Isolde',
            'sort': 'popular'
        }
        response = self.client.get('/api/albumsview', query_string=query)

        self.assertEqual(response.status_code, 200)   

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['albums']), 0)
        self.assertGreater(len(data['works']), 0)

    def test_get_workslist(self):
        response = self.client.get('/api/workslist', follow_redirects=True)

        self.assertEqual(response.status_code, 200)   

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)

    def test_get_userdata(self):
        response = self.client.get('/api/userdata', follow_redirects=True)

        self.assertEqual(response.status_code, 200)   

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('new_posts', data)

    def test_omnisearch(self):

        search_string = 'Wagner Tristan'
        response = self.client.get('/api/omnisearch', query_string={'search': search_string})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['works']), 0)

    def test_get_composers(self):

        # Default load
        response = self.client.get('/api/composers')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

        # Filter
        response = self.client.get('/api/composers', query_string={'filter': 'romantic'})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

        # Search
        response = self.client.get('/api/composers', query_string={'search': 'wagner'})

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

    def test_get_favoritescomposers(self):

        # Log in test user
        login_response = self.client.get('/testlogin')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json['status'], 'success')

        # test endpoint
        response = self.client.get('/api/favoritescomposers')
        
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

    def test_get_multicomposers(self):
        composers_data = [
            {"value": "Wagner"},
        ]

        response = self.client.post('api/multicomposers', json=composers_data)
       
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

    def test_get_composersradio(self):
        response = self.client.get('/api/composersradio')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertIn('Wagner', data['composers'])

    def test_get_works(self):

        # Base case
        response = self.client.get('/api/works/Wagner')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

        # Search case
        response = self.client.get('/api/works/Wagner', query_string={'search': 'tristan'})

        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

        # Filter case
        response = self.client.get('/api/works/Wagner', query_string={'filter': 'all'})

        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

    def test_get_favoriteworks(self):

        # Log in test user
        login_response = self.client.get('/testlogin')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json['status'], 'success')

        response = self.client.get('/api/favoriteworks/Wagner')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

    def test_get_radioworks(self):

        # Basic test
        payload = {
            "genres": [{"value": "all"}],
            "filter": "all",
            "search": "",
            "artist": "",
            "radio_type": "composer"
        }

        response = self.client.post('api/radioworks', json=payload)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

        # Test favorites radio
        payload = {
            "genres": [{"value": "all"}],
            "filter": "all",
            "search": "",
            "artist": "",
            "radio_type": "favorites"
        }

        # Log in test user
        login_response = self.client.get('/testlogin')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json['status'], 'success')    
        
        # Get favorites radio
        response = self.client.post('api/radioworks', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

        # Test with specific filter, search term, and artist
        payload = {
            "genres": [{"value": "Opera"}],
            "filter": "recommended",
            "search": "Parsifal",
            "artist": "Waltraud Meier",
            "radio_type": "all"
        }

        response = self.client.post('api/radioworks', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')  
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

        # Test radio export
        payload = {
            "genres": [{"value": "Opera"}],
            "filter": "recommended",
            "search": "Parsifal",
            "performer": "Waltraud Meier",
            "radio_type": "performer",
            "limit": 100,
            "name": "My Spotify Playlist",
            "prefetch": True,
            "random": False
        }

        response = self.client.post('api/exportplaylist', json=payload)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertGreater(data['track_count'], 0)

    def test_get_albums(self):

        # Log in test user
        login_response = self.client.get('/testlogin')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json['status'], 'success') 

        # Basic test
        response = self.client.get('/api/albums/WAGNER00013')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success') 
        self.assertGreater(len(data['artists']), 0)
        self.assertIn('liked_albums', data)
        self.assertIn('composer', data)
        self.assertIn('Wagner', data['composer'][0]['name_short'])

        # With filters
        query = {
            'page': 1,
            'artist': 'Sir Georg Solti',
            'sort': 'durationdescending',
            'limit': 100,
        }
        response = self.client.get('/api/albums/WAGNER00013', query_string=query)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success') 
        self.assertGreater(len(data['artists']), 0)
        self.assertIn('liked_albums', data)
        self.assertIn('composer', data)
        self.assertIn('Wagner', data['composer'][0]['name_short'])

        # Favorites
        query = {
            'favorites': True
        }
        response = self.client.get('/api/albums/WAGNER00013', query_string=query)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_like_action(self):

        # Unauthenticated user
        response = self.client.get('/api/like/WAGNER000096BIzBPVDbAw4DdyMOENCFe/like')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error') 

        # Log in test user
        login_response = self.client.get('/testlogin')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json['status'], 'success') 

        # Test liking an album
        response = self.client.get('/api/like/WAGNER000096BIzBPVDbAw4DdyMOENCFe/like')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')  

        album = db.session.get(WorkAlbums, 'WAGNER000096BIzBPVDbAw4DdyMOENCFe')
        user = db.session.get(User, 85)
        self.assertTrue(user.has_liked_album(album))

        # Test unliking an album
        response = self.client.get('/api/like/WAGNER000096BIzBPVDbAw4DdyMOENCFe/unlike')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')  

        album = db.session.get(WorkAlbums, 'WAGNER000096BIzBPVDbAw4DdyMOENCFe')
        user = db.session.get(User, 85)
        self.assertFalse(user.has_liked_album(album))

    def test_get_composerinfo(self):

        response = self.client.get('/api/composerinfo/Wagner')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Wagner', data['info']['name_short'])

    def test_get_workinfo(self):

        response = self.client.get('/api/workinfo/WAGNER00013')

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['info']['composer'], "Wagner")

    def test_get_albuminfo(self):

        response = self.client.get('/api/albuminfo/WAGNER000096BIzBPVDbAw4DdyMOENCFe')

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['album']['composer'], "Wagner")

    def test_get_artistcomposers(self):

        response = self.client.get('/api/artistcomposers/0dicUFoK5LIbqu6OoHu8VH')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['composers']), 0)
        self.assertGreater(len(data['genres']), 0)

    def test_get_artistworks(self):

        query = {
            'composer': 'Wagner',
            'artist': '0dicUFoK5LIbqu6OoHu8VH',
        }

        response = self.client.get('/api/artistworks', query_string=query)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['works']), 0)
        self.assertGreater(len(data['playlist']), 0)

    def test_get_artistlist(self):

        response = self.client.get('/api/artistlist')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['artists']), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

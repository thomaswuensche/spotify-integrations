import logging
import os
import time
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient(Spotify):

    def __init__(self):
        self.username = os.environ['SPOTIFY_USERNAME']

        scopes = [
            'playlist-modify-private',
            'playlist-read-private',
            'playlist-read-collaborative',
            'user-library-read',
            'user-top-read'
        ]
        scope = ' '.join(scopes)

        self.check_cache()

        auth = SpotifyOAuth(
            client_id = os.environ['CLIENT_ID'],
            client_secret = os.environ['CLIENT_SECRET'],
            redirect_uri = os.environ['REDIRECT_URI'],
            scope = scope,
            username = self.username,
        )

        super().__init__(auth_manager=auth)

    def check_cache(self):
        cache_path = os.path.abspath(f'{os.path.dirname(__file__)}/.cache-{self.username}')

        try:
            cache = open(cache_path)
        except FileNotFoundError:
            logging.debug('.cache not found')

            try:
                data = {
                    'refresh_token': os.environ['REFRESH_TOKEN'],
                    'scope': scope,
                    'expires_at': int(time.time()) - 1
                }

                with open(cache_path, 'w') as cache:
                    cache.write(json.dumps(data))
            except KeyError:
                logging.error('no REFRESH_TOKEN env var')

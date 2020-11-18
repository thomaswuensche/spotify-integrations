import logging
import os
import time
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def set_logging_config():
    logging.basicConfig(
        level=int(os.environ['LOG_LEVEL']),
        format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s'
    )

def spotipy_client():
    username = os.environ['SPOTIFY_USERNAME']
    scope = 'playlist-read-collaborative'

    try:
        cache = open(f'.cache-{username}')
        logging.debug('.cache exists')
    except FileNotFoundError as e:
        logging.debug('.cache not found')

        data = {
            'refresh_token': os.environ['REFRESH_TOKEN'],
            'scope': scope,
            'expires_at': int(time.time()) - 1
        }

        with open(f'.cache-{username}', 'w') as cache:
            cache.write(json.dumps(data))

    auth = SpotifyOAuth(
        client_id = os.environ['CLIENT_ID'],
        client_secret = os.environ['CLIENT_SECRET'],
        redirect_uri = os.environ['REDIRECT_URI'],
        scope = scope,
        username = username,
    )

    return spotipy.Spotify(auth_manager=auth)

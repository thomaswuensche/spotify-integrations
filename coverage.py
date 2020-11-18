import spotipy
from spotipy.oauth2 import SpotifyOAuth
from controller import CoverageController
import logging
import os

logging.basicConfig(
    level=int(os.environ['LOG_LEVEL']),
    format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s'
)

username = os.environ['SPOTIFY_USERNAME']
scope = 'playlist-modify-private playlist-read-private playlist-read-collaborative user-library-read'

auth = SpotifyOAuth(
    client_id = os.environ['CLIENT_ID'],
    client_secret = os.environ['CLIENT_SECRET'],
    redirect_uri = os.environ['REDIRECT_URI'],
    scope = scope,
    username = username,
)

api = spotipy.Spotify(auth_manager=auth)

controller = CoverageController(api, username)

logging.info('getting saved tracks...')
result_lib = api.current_user_saved_tracks(limit=50)
controller.process_coverage(
    result_lib,
    os.environ['PLAYLIST_LIB_COVERAGE'],
)

logging.info('getting tracks from hs...')
result_hs = api.user_playlist_tracks(username, playlist_id=os.environ['PLAYLIST_HS'])
controller.process_coverage(
    result_hs,
    os.environ['PLAYLIST_HS_COVERAGE'],
)

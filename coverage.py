import spotipy
import spotipy.util
import credentials
import helpers
from helpers import CoverageBot
import logging
import os

helpers.setLoggingLevel(logging.INFO)

scope = 'playlist-modify-private playlist-read-collaborative user-library-read'
username = os.environ['SPOTIFY_USERNAME']

token = spotipy.util.prompt_for_user_token(
    username, scope,
    os.environ['CLIENT_ID'],
    os.environ['CLIENT_SECRET'],
    os.environ['REDIRECT_URI']
)

if token:
    api = spotipy.Spotify(auth=token)
    coverageBot = CoverageBot(api, username)

    logging.info('getting saved tracks...')
    result_lib = api.current_user_saved_tracks()
    coverageBot.process_coverage(
        result_lib,
        os.environ['PLAYLIST_LIB_COVERAGE'],
    )

    logging.info('getting tracks from hs...')
    result_hs = api.user_playlist_tracks(username, playlist_id=os.environ['PLAYLIST_HS'])
    coverageBot.process_coverage(
        result_hs,
        os.environ['PLAYLIST_HS_COVERAGE'],
    )

else:
    logging.error("Can't get token for", username)

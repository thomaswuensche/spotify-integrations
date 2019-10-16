import spotipy
import spotipy.util
import credentials
import helpers
from helpers import CoverageBot
import pprint as pp
import logging
import sys

helpers.setLoggingLevel(logging.INFO)

scope = 'playlist-modify-private playlist-read-collaborative user-library-read'
username = 't6am47'

token = spotipy.util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri)

if token:
    api = spotipy.Spotify(auth=token)
    coverageBot = CoverageBot(api, username)

    logging.info('getting saved tracks...')
    result_lib = api.current_user_saved_tracks()
    coverageBot.process_coverage(result_lib,
        'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q',
        from_lib=True)

    logging.info('getting tracks from hs...')
    result_hs = api.user_playlist_tracks(username,
        playlist_id='spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d')
    coverageBot.process_coverage(result_hs,
        'spotify:user:t6am47:playlist:1RUo8WtwUnD6ITVsLNUXl0',
        from_lib=False)

else:
    logging.error("Can't get token for", username)

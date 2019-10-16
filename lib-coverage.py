import spotipy
import spotipy.util
import credentials
import helpers
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

    dict_lib = {}

    logging.info('getting saved tracks...')
    result_lib = api.current_user_saved_tracks()
    helpers.store_result_with_date(api, dict_lib, result_lib, from_lib=True)

    list_covered_tracks = helpers.store_tracks_from_playlists(api, username)

    diff = list(set(dict_lib.keys()) - set(list_covered_tracks))
    logging.info('tracks not covered: ' + str(len(diff)))

    list_upload = helpers.sort_diff_tracks(diff, dict_lib)

    helpers.upload_that_shit(api, username, list_upload,
        'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q')

else:
    logging.error("Can't get token for", username)

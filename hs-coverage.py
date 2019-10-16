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

    dict_hs = {}

    logging.info('getting tracks from hs...')
    result_hs = api.user_playlist_tracks(username,
        playlist_id='spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d')
    helpers.store_result_with_date(api, dict_hs, result_hs)

    list_covered_tracks = helpers.store_tracks_from_playlists(api, username)

    diff = list(set(dict_hs.keys()) - set(list_covered_tracks))
    logging.info('tracks not covered: ' + str(len(diff)))

    list_upload = helpers.sort_diff_tracks(diff, dict_hs)

    helpers.upload_that_shit(api, username, list_upload,
        'spotify:user:t6am47:playlist:1RUo8WtwUnD6ITVsLNUXl0')

else:
    logging.error("Can't get token for", username)

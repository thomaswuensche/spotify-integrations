import spotipy
import spotipy.util
import credentials
import helpers
import pprint as pp
import logging
import sys

helpers.setLoggingLevel(logging.DEBUG)

scope = 'playlist-modify-private playlist-read-collaborative user-library-read'
username = 't6am47'

token = spotipy.util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri)

if token:
    api = spotipy.Spotify(auth=token)

    list_hs = []
    list_pl = []

    result_hs = api.user_playlist_tracks(username,
        playlist_id='spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d')
    helpers.store_result(api, list_hs, result_hs)

    result_pl = api.user_playlists(username)

    for playlist in result_pl['items']:
        if ('_' in playlist['name']) or ('//' in playlist['name']):
            logging.info(playlist['id'] + ' - ' + playlist['name'])

            result_tracks = api.user_playlist_tracks(username,
                playlist_id=playlist['id'])
            helpers.store_result(api, list_pl, result_tracks)

    result_lib = api.current_user_saved_tracks()
    helpers.store_result(api, list_pl, result_lib)

    diff = list(set(list_hs) - set(list_pl))
    # logging.debug(pp.pformat(diff))
    logging.info(len(diff))

    for i in range(0, len(diff), 100):
        if i == 0:
            api.user_playlist_replace_tracks(username,
                'spotify:user:t6am47:playlist:1RUo8WtwUnD6ITVsLNUXl0',
                diff[i : i+100])
        else:
            api.user_playlist_add_tracks(username,
                'spotify:user:t6am47:playlist:1RUo8WtwUnD6ITVsLNUXl0',
                diff[i : i+100])

else:
    logging.error("Can't get token for", username)

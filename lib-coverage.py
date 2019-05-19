import spotipy
import spotipy.util
import credentials
import helpers
import pprint as pp
import logging
import sys

helpers.setLoggingLevel(logging.DEBUG)

scope = 'playlist-modify-private user-library-read'
username = 't6am47'

token = spotipy.util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri)

if token:
    api = spotipy.Spotify(auth=token)

    list_lib = []
    list_pl = []

    result_lib = api.current_user_saved_tracks()

    for track in result_lib['items']:
        if track['added_at'][:4] >= '2018':
            list_lib.append(track['track']['id'])

    while result_lib['next']:
        result_lib = api.next(result_lib)
        for track in result_lib['items']:
            if track['added_at'][:4] >= '2018':
                list_lib.append(track['track']['id'])


    result_pl = api.user_playlists(username)

    for playlist in result_pl['items']:
        if ('_' in playlist['name']) or ('//' in playlist['name']):
            logging.info(playlist['id'] + ' - ' + playlist['name'])

            result_tracks = api.user_playlist_tracks(username,
                playlist_id=playlist['id'])
            helpers.store_result(api, list_pl, result_tracks)

    diff = list(set(list_lib) - set(list_pl))
    # logging.debug(pp.pformat(diff))
    logging.info(len(diff))

    for i in range(0, len(diff), 100):
        if i == 0:
            api.user_playlist_replace_tracks(username,
                'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q',
                diff[i : i+100])
        else:
            api.user_playlist_add_tracks(username,
                'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q',
                diff[i : i+100])

else:
    logging.error("Can't get token for", username)

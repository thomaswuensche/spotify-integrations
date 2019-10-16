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
    list_covered_tracks = []

    logging.info('getting saved tracks...')
    result_lib = api.current_user_saved_tracks()
    helpers.store_result_with_date(api, dict_lib, result_lib, from_lib=True)

    user_playlists = api.user_playlists(username)

    logging.info('getting tracks in playlists...')
    for playlist in user_playlists['items']:
        if ('_' in playlist['name']) or ('//' in playlist['name']):
            logging.info(playlist['id'] + ' - ' + playlist['name'])

            result_tracks = api.user_playlist_tracks(username,
                playlist_id=playlist['id'])
            helpers.store_result(api, list_covered_tracks, result_tracks)

    diff = list(set(dict_lib.keys()) - set(list_covered_tracks))
    logging.info('tracks not covered: ' + str(len(diff)))

    logging.info('sorting tracks by added at...')
    diff_with_added_at = {}
    for item in diff:
        diff_with_added_at.update({item : dict_lib[item]})

    sorted_tuples = sorted(diff_with_added_at.items(), reverse=True, key=lambda x: x[1])
    list_upload = []
    for item in sorted_tuples:
        list_upload.append(item[0])

    logging.info('uploading tracks...')
    for i in range(0, len(list_upload), 100):
        if i == 0:
            api.user_playlist_replace_tracks(username,
                'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q',
                list_upload[i : i+100])
        else:
            api.user_playlist_add_tracks(username,
                'spotify:user:t6am47:playlist:1D6xkvZWaikkFBCNtPT63q',
                list_upload[i : i+100])

else:
    logging.error("Can't get token for", username)

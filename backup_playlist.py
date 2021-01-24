import logging
import os
from pprint import pformat

import util

util.set_logging_config()
api = util.spotipy_client()

def extract_tracks(result):
    tracks = []
    while True:
        for item in result['items']:
            if not item['track']['is_local']:
                track_data = {
                    'id': item['track']['id'],
                    'name': item['track']['name'],
                    'artists': [artist['name'] for artist in item['track']['artists']],
                    'added_at': item['added_at']
                }
                tracks.append(track_data)

        if not result['next']: break
        result = api.next(result)

    return tracks

playlist_id = input('playlist id ? ')

playlist_name = api.playlist(playlist_id, fields='name')['name']

logging.info('getting tracks from playlist...')
result = api.playlist_tracks(playlist_id)
playlist_tracks = extract_tracks(result)

playlist_tracks_size = len(playlist_tracks)
logging.info(f'tracks in playlists: {playlist_tracks_size}')

logging.info('sorting tracks by added at...')
playlist_tracks = sorted(
    playlist_tracks,
    key = lambda track: track['added_at'],
    reverse = True
)

logging.info('writing tracks to file...')
with open(f'{os.path.dirname(os.path.abspath(__file__))}/playlist_backup_{playlist_name}.txt', 'w') as file:
    file.write(pformat(playlist_tracks))

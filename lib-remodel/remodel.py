import logging
import os

# TODO: remove pformat import
from pprint import pformat

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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
                    'added_at': item['added_at']
                }
                tracks.append(track_data)

        if not result['next']: break
        result = api.next(result)

    return tracks


logging.info('getting tracks in library...')
result = api.current_user_saved_tracks(limit=50)
lib_tracks = extract_tracks(result)

criteria = os.environ['PLAYLIST_CRITERIA_REMODEL'].split(',')
filtered_playlists = []
result = api.current_user_playlists()

while True:
    filtered_playlists += list(filter(
        lambda playlist: any(crit in playlist['name'] for crit in criteria) and playlist['owner']['id'] == os.environ['SPOTIFY_USERNAME'],
        result['items']
    ))
    if not result['next']: break
    result = api.next(result)

playlist_tracks = []

logging.info('getting tracks in playlists...')
for playlist in filtered_playlists:
    logging.info(playlist['name'])
    result = api.playlist_tracks(playlist['id'])
    playlist_tracks += extract_tracks(result)

playlist_tracks_size = len(playlist_tracks)
logging.info(f'tracks in playlists: {playlist_tracks_size}')

diff = list(filter(
    lambda track: track['id'] not in [track['id'] for track in lib_tracks],
    playlist_tracks
))

diff_size = len(diff)
diff_percent = round(diff_size / playlist_tracks_size * 100)
logging.info(f'tracks not covered: {diff_size} ({diff_percent}%)')

logging.info('sorting tracks by added at...')
diff = sorted(
    diff,
    key = lambda track: track['added_at']
)

unique_diff = []
for track in diff:
     if not track['id'] in [track['id'] for track in unique_diff]:
         unique_diff.append(track)

logging.info('writing tracks to file...')
with open(f'{os.path.dirname(os.path.abspath(__file__))}/all_tracks.txt', 'w') as file:
    file.write(pformat(diff))
with open(f'{os.path.dirname(os.path.abspath(__file__))}/tracks.txt', 'w') as file:
    file.write(pformat(unique_diff))

# add diff to library

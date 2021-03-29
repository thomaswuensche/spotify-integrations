import os

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from spotify_client import SpotifyClient

api = SpotifyClient()

new_50 = api.current_user_saved_tracks(limit=50)

api.playlist_replace_items(
    os.environ['PLAYLIST_NEW_50'],
    [item['track']['id'] for item in new_50['items']]
)

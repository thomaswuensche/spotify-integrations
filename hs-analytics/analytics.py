import os

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util
from db_controller import DatabaseController
from spotify_client import SpotifyClient
from models.hs_track import HSTrack

util.set_logging_config()
db = DatabaseController()
api = SpotifyClient()

result = api.playlist_tracks(os.environ['PLAYLIST_HS'])
tracks = [HSTrack(track) for track in api.extract_tracks(result)]
tracks = api.store_audio_features(tracks)
HSTrack.bulk_insert(db, tracks)

db.close_conn()

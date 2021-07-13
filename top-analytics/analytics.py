import logging
from datetime import date

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util
from db_controller import DatabaseController
from spotify_client import SpotifyClient
from models.top_track import TopTrack

util.set_logging_config()
db = DatabaseController()
api = SpotifyClient()

for time_range in ['short_term', 'medium_term', 'long_term']:

    logging.info(f'saving top tracks {time_range}...')
    result = api.current_user_top_tracks(limit=50, time_range=time_range)
    tracks = []
    for index, track in enumerate(api.extract_tracks(result), start=1):
        tracks.append(TopTrack(track, date.today(), index, time_range))
    tracks = api.store_audio_features(tracks)
    TopTrack.bulk_insert(db, tracks)

db.close_conn()

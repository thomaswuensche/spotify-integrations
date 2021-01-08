import logging
import os
import json
from controller import CoverageController

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()
api = util.spotipy_client()
controller = CoverageController(api)

logging.info('checking timeline coverage')
result_lib = api.current_user_saved_tracks(limit=50)
controller.process_coverage(
    result_lib,
    '^\w\.\d{2}(\.\d{2})?$',
    os.environ['PLAYLIST_TIMELINE_COVERAGE'],
)

logging.info('checking library coverage')
controller.process_coverage(
    result_lib,
    '^(\d{2}_\w+|^//\w+)$',
    os.environ['PLAYLIST_LIB_COVERAGE'],
)

playlists_to_check = json.loads(os.environ['PLAYLISTS_TO_CHECK'])

for playlist in playlists_to_check:
    logging.info(f"checking {playlist['name']} coverage")
    result_playlist = api.playlist_tracks(playlist['playlist_id'])
    controller.process_coverage(
        result_playlist,
        '^(\d{2}_\w+|^//\w+)$',
        playlist['coverage_id'],
    )

import logging
import os
import json
from controller import CoverageController

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()
controller = CoverageController()

logging.info('checking timeline coverage')
result_lib = controller.current_user_saved_tracks(limit=50)
controller.process_coverage(
    result = result_lib,
    coverage_criteria = '^\w\.\d{2}(\.\d{2})?$',
    destination_playlist = os.environ['PLAYLIST_TIMELINE_COVERAGE'],
    min_date = '2020-01-01'
)

logging.info('checking library coverage')
controller.process_coverage(
    result = result_lib,
    coverage_criteria = '^([_+]?\d{2}_\w+|^//\w+)$',
    destination_playlist = os.environ['PLAYLIST_LIB_COVERAGE']
)

playlists_to_check = json.loads(os.environ['PLAYLISTS_TO_CHECK'])

for playlist in playlists_to_check:
    logging.info(f"checking {playlist['name']} coverage")
    result_playlist = controller.playlist_tracks(playlist['playlist_id'])
    controller.process_coverage(
        result = result_playlist,
        coverage_criteria = '^([_+]?\d{2}_\w+|^//\w+)$',
        destination_playlist = playlist['coverage_id']
    )

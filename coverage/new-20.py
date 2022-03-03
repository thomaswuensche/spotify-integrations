import logging
import os
from controller import CoverageController

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()
controller = CoverageController(rich_logs=False)

logging.info('liked tracks new 20...')
result = controller.current_user_saved_tracks(limit=50)
liked_tracks = controller.extract_from_result(result, limit=500)

diff_tracks = controller.get_coverage_diff(
    tracks_to_check = liked_tracks,
    check_against = '^(\\+?\\d{2}_\\w+|^//\\w+)$',
    type = 'regex'
)
controller.upload_diff(diff_tracks[:20], os.environ['PLAYLIST_LIKED_NEW_20'])


logging.info('hs tracks new 20...')
result = controller.playlist_tracks(os.environ['PLAYLIST_HS'])
hs_tracks = controller.extract_from_result(result)

diff_tracks = controller.get_coverage_diff(
    tracks_to_check = hs_tracks,
    check_against = '^(\\+?\\d{2}_\\w+|^//\\w+)$',
    sort = True,
    type = 'regex'
)
controller.upload_diff(diff_tracks[:20], os.environ['PLAYLIST_HS_NEW_20'])

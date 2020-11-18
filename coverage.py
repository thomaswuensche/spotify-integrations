import logging
import os
import util
from controller import CoverageController

util.set_logging_config()
api = util.spotipy_client()
controller = CoverageController(api)

logging.info('getting saved tracks...')
result_lib = api.current_user_saved_tracks(limit=50)
controller.process_coverage(
    result_lib,
    os.environ['PLAYLIST_LIB_COVERAGE'],
)

logging.info('getting tracks from hs...')
result_hs = api.playlist_tracks(os.environ['PLAYLIST_HS'])
controller.process_coverage(
    result_hs,
    os.environ['PLAYLIST_HS_COVERAGE'],
)

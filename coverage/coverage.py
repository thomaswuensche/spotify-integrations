import logging
import os
import json
import util
from controller import CoverageController

util.set_logging_config()
api = util.spotipy_client()
controller = CoverageController(api)

logging.info('checking library coverage')
result = api.current_user_saved_tracks(limit=50)
controller.process_coverage(
    result,
    os.environ['PLAYLIST_LIB_COVERAGE'],
)

playlists_to_check = json.loads(os.environ['PLAYLISTS_TO_CHECK'])

for playlist in playlists_to_check:
    logging.info(f"checking {playlist['name']} coverage")
    result = api.playlist_tracks(playlist['playlist_id'])
    controller.process_coverage(
        result,
        playlist['coverage_id'],
    )

import logging
import os
import json
import psycopg2 as pg
from controller import AnalyticsController

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()

db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
logging.info(f'connected to db: {db_conn.dsn}')

controller = AnalyticsController(db_conn)

for playlist in json.loads(os.environ['PLAYLISTS_TOP_SONGS']):
    result = controller.playlist_tracks(playlist['playlist_id'])
    controller.process_result(result, playlist['username'])

db_conn.close()
logging.info('db connection closed')

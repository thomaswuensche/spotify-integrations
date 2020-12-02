import logging
import os
import json
import util
import psycopg2 as pg
from analytics_controller import AnalyticsController

util.set_logging_config()
api = util.spotipy_client()

db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
logging.info(f'connected to db: {db_conn.dsn}')

controller = AnalyticsController(api, db_conn)

for playlist in json.loads(os.environ['PLAYLISTS']):
    result = api.playlist_tracks(playlist['playlist_id'])
    controller.process_result(result, playlist['username'])

db_conn.close()
logging.info('db connection closed')

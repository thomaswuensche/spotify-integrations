import logging
import os
import util
import psycopg2 as pg
from controller import AnalyticsController

util.set_logging_config()
api = util.spotipy_client()

db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
logging.info(f'connected to db: {db_conn.dsn}')

result = api.playlist_tracks(os.environ['PLAYLIST_HS'])

controller = AnalyticsController(api, db_conn)
controller.reset_table(os.environ['DB_TABLE'])
controller.process_result(result)

db_conn.close()
logging.info('db connection closed')

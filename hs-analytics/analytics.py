import logging
import os
import psycopg2 as pg
from controller import AnalyticsController

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()

db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
logging.info(f'connected to db: {db_conn.dsn}')

controller = AnalyticsController(db_conn)
controller.reset_table(os.environ['DB_TABLE_HS'])
controller.save_tracks(
    playlist = os.environ['PLAYLIST_HS'],
    destination_table = os.environ['DB_TABLE_HS']
)

db_conn.close()
logging.info('db connection closed')

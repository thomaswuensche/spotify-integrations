import spotipy
import spotipy.util
from controller import AnalyticsController
import logging
import os
import psycopg2 as pg

logging.basicConfig(
    level=int(os.environ['LOG_LEVEL']),
    format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s'
)

username = os.environ['SPOTIFY_USERNAME']
scope = 'playlist-read-collaborative'

token = spotipy.util.prompt_for_user_token(
    username,
    scope,
    os.environ['CLIENT_ID'],
    os.environ['CLIENT_SECRET'],
    os.environ['REDIRECT_URI']
)

if token:
    api = spotipy.Spotify(auth=token)

    db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
    logging.info('connected to db: ' + db_conn.dsn)

    result = api.user_playlist_tracks(
        username,
        playlist_id=os.environ['PLAYLIST_HS'],
        limit=100,
        market="DE"
    )

    controller = AnalyticsController(api, db_conn)
    controller.reset_table(os.environ['DB_TABLE'])
    controller.process_result(result)

    db_conn.close()
    logging.info('db connection closed')

else:
    logging.error("Can't get token for", username)

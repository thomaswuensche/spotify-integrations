import spotipy
import spotipy.util
import credentials
import pprint as pp
import helpers
from helpers import DataHandler
import database
import mysql.connector as mysql
import logging
import sys

helpers.setLoggingLevel(logging.INFO)

# scope is used to determine what data this script (app) wants to access
scope = 'playlist-modify-private playlist-read-collaborative user-library-read'
username = 't6am47'

token = spotipy.util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # registered in app settings

if token:
    api = spotipy.Spotify(auth=token)

    # creates connection to mysql database w/ credentials in separate file
    connection = mysql.connect(user=credentials.user,
        password=credentials.password,
        host=credentials.host,
        database=credentials.database)
    logging.info('connection opened')

    # deletes all data from specified table and resets auto_increment
    # database.wipe_table(connection, credentials.table)

    # create DataHandler object
    dataHandler = DataHandler(api, connection)

    # gets last synced id
    id = database.get_last_id(connection, credentials.table)
    count_local_tracks = database.get_count_local_tracks(connection)

    # returns all tracks in specified playlist
    result = api.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields=None,
        limit=100,
        offset=id + count_local_tracks,
        market="DE")

    # logging.debug(pp.pformat(result))

    # iterates through all items in the result (some other metadata is left out)
    for item in result['items']:
        dataHandler.process_data(item)

    # next block for looping through all tracks (adjust limit in previous request)
    while result['next']:
        result = api.next(result)
        for item in result['items']:
            dataHandler.process_data(item)

    connection.close()
    logging.info('connection closed')

else:
    logging.error("Can't get token for", username)

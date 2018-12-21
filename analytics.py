import spotipy
import spotipy.util
import credentials
import json
import helpers
import database
import mysql.connector as mysql
import logging
import sys


# sets logging configuration, change to debug for more detailed output
logging.basicConfig(level=logging.INFO,
    format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s')

# scope is used to determine what data this script (app) wants to access
scope = 'playlist-read-collaborative'
username = 't6am47'

token = spotipy.util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)

    # creates connection to mysql database w/ credentials in separate file
    connection = mysql.connect(user=credentials.user,
        password=credentials.password,
        host=credentials.host,
        database=credentials.database)
    logging.info('connection opened')

    # deletes all data from specified table and resets auto_increment
    # database.wipe_table(connection, credentials.table)

    # gets last synced id
    id = database.get_last_id(connection, credentials.table)

    # returns all tracks in specified playlist
    result = spotify.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields=None,
        limit=100,
        offset=id,
        market="DE")

    # dump full result (not related to spotipy request returning a JSON file. just used to print out dicts in a better way)
    # logging.debug(json.dumps(result, indent=4))

    # iterates through all items in the result (some other metadata is left out)
    for item in result['items']:
        helpers.process_data(item, spotify, connection)

    # next block for looping through all tracks (adjust limit in previous request)
    while result['next']:
        result = spotify.next(result)
        for item in result['items']:
            helpers.process_data(item, spotify, connection)

    connection.close()
    logging.info('connection closed')

else:
    logging.error("Can't get token for", username)

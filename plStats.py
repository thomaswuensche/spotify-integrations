import spotipy
import spotipy.util as util
import credentials
import json
import t6util
import mysql.connector as mysql

scope = 'playlist-read-collaborative'
username = 't6am47' # argv

token = util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)

    mysqlcnx = mysql.connect(user=credentials.user,
        password=credentials.password,
        host=credentials.host,
        database=credentials.database)

    result = spotify.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields=None,
        limit=2,
        offset=0,
        market="DE")

    # dump full result (not related to spotipy request returning a JSON file. just used to print out dicts in a better way)
    #print(json.dumps(result, indent=4))

    for item in result['items']:
        t6util.get_and_push_data(item, mysqlcnx, spotify)

    # next block for looping through all tracks (adjust limit in previous request)
    '''
    while result['next']:
        result = spotify.next(result)
        for item in result['items']:
            t6util.get_and_push_data(item, mysqlcnx, spotify)
    '''

    mysqlcnx.close()

else:
    print("Can't get token for", username)

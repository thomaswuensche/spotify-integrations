import spotipy
import spotipy.util as util
import credentials
import json
import t6util
import activeRecords
import mysql.connector as mysql

scope = 'playlist-read-collaborative'
username = 't6am47' # argv

token = util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)

    mysqlcnx = mysql.connect(user='root',
        password='',
        host='localhost',
        database='hs-analytics')

    result = spotify.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields=None,
        limit=2,
        offset=0,
        market="DE")

    #print(json.dumps(result, indent=4)) # dump full result (not related to spotipy request returning a JSON file. just used to print out dicts in a better way)

    for item in result['items']:
        track = item['track']

        name = track['name']
        champ = t6util.whodunit(item['added_by']['id'])
        added_at = item['added_at']
        artist_result = spotify.artist(track['artists'][0]['uri'])

        #print(json.dumps(artist_result, indent=4))

        activeTrack = activeRecords.ActiveTrack(name, artist_result, champ, added_at)
        activeTrack.setConnection(mysqlcnx)

        print(activeTrack.toString())
        print(activeTrack.getGenres())

        activeTrack.testConnection(name)

        print("***")

    mysqlcnx.close()

    # next block for looping through all tracks (adjust limit in previous request)
    '''
    while result['next']:
        result = spotify.next(result)
        for item in result['items']:
            track = item['track']
            print(track['name'] + ' - ' + track['artists'][0]['name'])
    '''

else:
    print("Can't get token for", username)

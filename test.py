import spotipy
import spotipy.util as util
import credentials
import json

scope = 'user-library-read'
username = 't6am47'

token = util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)
    result = spotify.current_user_saved_tracks(limit=1)
    print(json.dumps(result, indent=4))
    for item in result['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)

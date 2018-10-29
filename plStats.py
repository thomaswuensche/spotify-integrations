import spotipy
import spotipy.util as util
import credentials
import json

scope = 'playlist-read-collaborative'
username = 't6am47' # argv

token = util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)

    result = spotify.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields=None,
        limit=2,
        offset=0,
        market="DE")
    print(json.dumps(result, indent=4)) # dump full result (not related to spotipy request returning a JSON file. just used to print out dicts in a better way)
    for item in result['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)

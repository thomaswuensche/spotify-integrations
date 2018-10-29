import spotipy
import spotipy.util as util
import credentials

scope = 'playlist-read-collaborative'
username = 't6am47' # argv

token = util.prompt_for_user_token(username, scope,
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uri) # had to be registered in the app settings

if token:
    spotify = spotipy.Spotify(auth=token)
    results = spotify.user_playlist_tracks(username,
        playlist_id="spotify:user:t6am47:playlist:4doQ7lGWMlDDltEOQARV1d",
        fields="tracks",
        limit=30,
        offset=0,
        market="DE")
else:
    print("Can't get token for", username)

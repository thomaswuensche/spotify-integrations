import logging
import os
import time
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient(Spotify):

    def __init__(self):
        self.username = os.environ['SPOTIFY_USERNAME']

        scopes = [
            'playlist-modify-private',
            'playlist-read-private',
            'playlist-read-collaborative',
            'user-library-read',
            'user-top-read'
        ]
        scope = ' '.join(scopes)

        self.check_cache(scope)

        auth = SpotifyOAuth(
            client_id = os.environ['CLIENT_ID'],
            client_secret = os.environ['CLIENT_SECRET'],
            redirect_uri = os.environ['REDIRECT_URI'],
            scope = scope,
            username = self.username,
        )

        super().__init__(auth_manager=auth)
        self.user_playlists = self.get_user_playlists()

    def check_cache(self, scope):
        cache_path = os.path.abspath(f'{os.path.dirname(__file__)}/.cache-{self.username}')

        try:
            cache = open(cache_path)
        except FileNotFoundError:
            logging.debug('.cache not found')

            try:
                data = {
                    'refresh_token': os.environ['REFRESH_TOKEN'],
                    'scope': scope,
                    'expires_at': int(time.time()) - 1
                }

                with open(cache_path, 'w') as cache:
                    cache.write(json.dumps(data))
            except KeyError:
                logging.error('no REFRESH_TOKEN env var')

    def get_user_playlists(self):
        user_playlists = []
        result = self.current_user_playlists()
        while True:
            for playlist in result['items']:
                user_playlists.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'owner': playlist['owner']['id']
                })
            if not result['next']: break
            result = self.next(result)

        return user_playlists

    def extract_tracks(self, result):
        logging.info(f'getting tracks from {self.result_origin(result)}...')
        extracted_tracks = []

        while True:
            extracted_tracks += self.filter_result(result)
            if not result['next']: break
            result = self.next(result)

        return extracted_tracks

    def filter_result(self, result):
        if 'track' in result['items'][0]:
            return list(filter(lambda item: not item['track']['is_local'], result['items']))
        else:
            return list(filter(lambda track: not track['is_local'], result['items']))

    def store_audio_features(self, tracks):
        track_ids = [track.id for track in tracks]
        for i in range(0, len(tracks), 100):
            for item in self.audio_features(track_ids[i : i+100]):
                track = next(filter(lambda track: track.id == item['id'], tracks))
                track.set_audio_features(item)
        return tracks

    def id_origin(self, id):
        if id == 'me' or id == 'library':
            return 'library'
        elif id.startswith('top_tracks'):
            return f"top tracks ({id.split(':')[-1]})"
        else:
            return next(filter(lambda playlist: playlist['id'] == id, self.user_playlists))['name']

    def result_origin(self, result):
        id = result['href'].rsplit('/')[-2]
        return self.id_origin(id)

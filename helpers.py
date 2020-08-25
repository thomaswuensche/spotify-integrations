import models
import logging
import pprint as pp
import credentials
import database
from exceptions import LocalTrackError
import os

def setLoggingLevel(level):
    logging.basicConfig(
        level=level,
        format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s'
    )

def whodunit(id):
    if id == "1163268620":
        return "markus"
    else:
        return "thomas"


class CoverageBot():

    def __init__(self, api, username):
        self.api = api
        self.username = username
        self.flagged_tracks = {}
        self.covered_tracks = {}

    def process_coverage(self, result, destination_playlist):
        tracks_to_check = self.extract_tracks(result)
        covered_tracks = self.get_covered_tracks()
        flagged_tracks = self.get_flagged_tracks()

        diff = list(set(tracks_to_check.keys()) - set(covered_tracks.keys()) - set(flagged_tracks.keys()))
        logging.info('tracks not covered: ' + str(len(diff)))

        list_upload = self.sort_diff_tracks(diff, tracks_to_check)
        self.upload_that_shit(list_upload, destination_playlist)

    def get_flagged_tracks(self):
        logging.info('getting flagged tracks...')

        if not self.flagged_tracks:
            result = self.api.user_playlist_tracks(self.username, playlist_id=os.environ['PLAYLIST_COVERAGE_FLAGGED'])
            self.flagged_tracks = self.extract_tracks(result)

        return self.flagged_tracks

    def get_covered_tracks(self):
        logging.info('getting tracks from playlists...')

        if not self.covered_tracks:
            user_playlists = self.api.user_playlists(self.username)

            for playlist in user_playlists['items']:
                if ('_' in playlist['name']) or ('//' in playlist['name']):
                    logging.info(playlist['id'] + ' - ' + playlist['name'])
                    result = self.api.user_playlist_tracks(self.username, playlist_id=playlist['id'])
                    self.covered_tracks.update(self.extract_tracks(result))

        return self.covered_tracks

    def extract_tracks(self, result):
        tracks = {}
        while True:
            for item in result['items']:
                if not item['track']['is_local']:
                    tracks[item['track']['id']] = item['added_at']

            if not result['next']: break
            result = self.api.next(result)

        return tracks

    def sort_diff_tracks(self, diff, info_dict):
        logging.info('sorting tracks by added at...')
        diff_with_added_at = {}
        for item in diff:
            diff_with_added_at[item] = info_dict[item]

        sorted_tuples = sorted(diff_with_added_at.items(), reverse=True, key=lambda x: x[1])
        list_upload = []
        for item in sorted_tuples:
            list_upload.append(item[0])

        return list_upload

    def upload_that_shit(self, list_upload, playlist_id):
        logging.info('uploading tracks...')
        for i in range(0, len(list_upload), 100):
            if i == 0:
                self.api.user_playlist_replace_tracks(self.username, playlist_id, list_upload[i : i+100])
            else:
                self.api.user_playlist_add_tracks(self.username, playlist_id, list_upload[i : i+100])


class DataHandler():

    def __init__(self, spotify, connection):
        self.spotify = spotify
        self.connection = connection

    def process_data(self, item):
        # logging.debug(pp.pformat(item))
        try:
            track = self.get_track_data(item)
        except LocalTrackError as e:
            logging.warning(e)
        else:
            logging.debug(track.toString())
            track.insert(self.connection)

    def get_track_data(self, item):
        track = item['track']
        name = track['name']

        if item['is_local']:
            database.increment_count_local_tracks(self.connection)
            raise LocalTrackError('LOCAL TRACK NOT IMPORTED: {}'.format(name))

        champ = whodunit(item['added_by']['id'])
        added_raw = item['added_at']
        added_at = item['added_at'][:10]
        added_time = added_raw[11:-1]
        artist_result = self.spotify.artist(track['artists'][0]['uri'])
        explicit = track['explicit']
        release_date = track['album']['release_date']
        release_date_precision = track['album']['release_date_precision']
        duration = track['duration_ms']
        popularity = track['popularity']

        features = self.spotify.audio_features(track['id'])[0]
        danceability = features['danceability']
        energy = features['energy']
        valence = features['valence']
        tempo = features['tempo']

        # logging.debug(pp.pformat(artist_result))
        # logging.debug(pp.pformat(features))

        track = models.ActiveTrack(name, artist_result, champ, added_at, added_time,
            explicit, release_date, release_date_precision, duration, popularity,
            danceability, energy, valence, tempo)
        return track

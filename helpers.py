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

    def process_coverage(self, result, destination_playlist, from_lib):
        dict_with_dates = {}

        self.store_result_with_date(dict_with_dates, result, from_lib)

        covered_tracks = self.get_covered_tracks()
        flagged_tracks = self.get_flagged_tracks()

        diff = list(set(dict_with_dates.keys()) - set(covered_tracks) - set(flagged_tracks))
        logging.info('tracks not covered: ' + str(len(diff)))

        list_upload = self.sort_diff_tracks(diff, dict_with_dates)
        self.upload_that_shit(list_upload, destination_playlist)

    def get_flagged_tracks(self):
        logging.info('getting flagged tracks...')

        flagged_tracks = []
        result_tracks = self.api.user_playlist_tracks(self.username, playlist_id=os.environ['PLAYLIST_COVERAGE_FLAGGED'])
        self.store_result(flagged_tracks, result_tracks, from_lib=False)
        return flagged_tracks

    def get_covered_tracks(self):
        logging.info('getting tracks from playlists...')

        covered_tracks = []
        user_playlists = self.api.user_playlists(self.username)

        for playlist in user_playlists['items']:
            if ('_' in playlist['name']) or ('//' in playlist['name']):
                logging.info(playlist['id'] + ' - ' + playlist['name'])
                result_tracks = self.api.user_playlist_tracks(self.username, playlist_id=playlist['id'])
                self.store_result(covered_tracks, result_tracks, from_lib=False)

        return covered_tracks

    def store_result(self, list, result, from_lib):
        self.store_tracks(list, result['items'], from_lib)

        while result['next']:
            result = self.api.next(result)
            self.store_tracks(list, result['items'], from_lib)

    def store_tracks(self, list, tracks, from_lib):
        for track in tracks:
            if from_lib:
                list.append(track['track']['id'])
            else:
                if not track['is_local']:
                    list.append(track['track']['id'])

    def store_result_with_date(self, dict, result, from_lib):
        self.store_tracks_with_date(dict, result['items'], from_lib)

        while result['next']:
            result = self.api.next(result)
            self.store_tracks_with_date(dict, result['items'], from_lib)

    def store_tracks_with_date(self, dict, tracks, from_lib):
        for track in tracks:
            if from_lib:
                dict.update({track['track']['id'] : track['added_at']})
            else:
                if not track['is_local']:
                    dict.update({track['track']['id'] : track['added_at']})

    def sort_diff_tracks(self, diff, info_dict):
        logging.info('sorting tracks by added at...')
        diff_with_added_at = {}
        for item in diff:
            diff_with_added_at.update({item : info_dict[item]})

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

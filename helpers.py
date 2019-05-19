import models
import logging
import pprint as pp
import credentials
import database
from exceptions import LocalTrackError

def setLoggingLevel(level):
    logging.basicConfig(level=level,
        format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s')

def whodunit(id):
    if id == "1163268620" :
        return "markus"
    else :
        return "thomas"

def store_result(api, list, result):
    store_tracks(list, result['items'])

    while result['next']:
        result = api.next(result)
        store_tracks(list, result['items'])

def store_tracks(list, tracks):
    for track in tracks:
        try:
            if not track['is_local']:
                list.append(track['track']['id'])
        except KeyError as e:
            list.append(track['track']['id'])


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

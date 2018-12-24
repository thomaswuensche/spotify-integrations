import models
import logging
import json
import credentials
from exceptions import LocalTrackError

def setLoggingLevel(level):
    logging.basicConfig(level=level,
        format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s')

def whodunit(id):
    if id == "1163268620" :
        return "markus"
    else :
        return "thomas"

def process_data(item, spotify, connection):
    # logging.debug(json.dumps(item, indent=4))
    try:
        track = get_track_data(item, spotify)
    except LocalTrackError as e:
        logging.warning(e)
    else:
        logging.debug(track.toString())
        track.insert(connection)

def get_track_data(item, spotify):
    track = item['track']
    name = track['name']

    if item['is_local']:
        raise LocalTrackError('LOCAL TRACK NOT IMPORTED: {}'.format(name))

    champ = whodunit(item['added_by']['id'])
    added_raw = item['added_at']
    added_at = item['added_at'][:10]
    added_time = added_raw[11:-1]
    artist_result = spotify.artist(track['artists'][0]['uri'])
    explicit = track['explicit']
    release_date = track['album']['release_date']
    release_date_precision = track['album']['release_date_precision']
    duration = track['duration_ms']
    popularity = track['popularity']

    features = spotify.audio_features(track['id'])[0]
    danceability = features['danceability']
    energy = features['energy']
    valence = features['valence']
    tempo = features['tempo']

    # logging.debug(json.dumps(artist_result, indent=4))
    # logging.debug(json.dumps(features, indent=4))

    track = models.ActiveTrack(name, artist_result, champ, added_at, added_time,
        explicit, release_date, release_date_precision, duration, popularity,
        danceability, energy, valence, tempo)
    return track

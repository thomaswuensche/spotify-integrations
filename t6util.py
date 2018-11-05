import activeRecords
import logging
import json
import credentials

class LocalTrackError(ValueError):
    pass

def whodunit(id):
    if id == "1163268620" :
        return "markus"
    else :
        return "thomas"

def wipe_table(connection):
    cursor = connection.cursor()
    sql = "DELETE FROM {}".format(credentials.table)
    cursor.execute(sql)
    logging.info('wiped table: {}'.format(credentials.table))

    sql = "ALTER TABLE {} AUTO_INCREMENT = 1".format(credentials.table)
    cursor.execute(sql)
    logging.info('reset AUTO_INCREMENT to 1 on table: {}'.format(credentials.table))

    connection.commit()
    cursor.close()


def get_last_id(connection):
    last_id = 0
    cursor = connection.cursor()
    sql = "SELECT id FROM {} ORDER BY id DESC LIMIT 1".format(credentials.table)
    result = cursor.execute(sql)
    for result in cursor:
        last_id = result[0]

    logging.info('last id: {}'.format(last_id))
    cursor.close()
    return last_id


def push_track_to_db(track, connection):
    track.setConnection(connection)
    track.insert()


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

    track = activeRecords.ActiveTrack(name, artist_result, champ, added_at, added_time,
        explicit, release_date, release_date_precision, duration, popularity,
        danceability, energy, valence, tempo)
    return track

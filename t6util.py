import activeRecords
import logging
import json


def whodunit(id):
    if id == "1163268620" :
        return "markus"
    else :
        return "thomas"

def wipe_table(connection, table):
    cursor = connection.cursor()
    sql = "DELETE FROM {}".format(table)
    cursor.execute(sql)
    logging.info('wiped table: {}'.format(table))

    sql = "ALTER TABLE {} AUTO_INCREMENT = 1".format(table)
    cursor.execute(sql)
    logging.info('reset AUTO_INCREMENT to 1 on table: {}'.format(table))

    connection.commit()
    cursor.close()


def get_last_id(connection):
    cursor = connection.cursor()
    sql = "SELECT id FROM pylonen ORDER BY id DESC LIMIT 1"
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
    champ = whodunit(item['added_by']['id'])
    added_raw = item['added_at']
    added_at = item['added_at'][:10]
    added_time = added_raw[11:-1]
    artist_result = spotify.artist(track['artists'][0]['uri'])
    #logging.debug(json.dumps(artist_result, indent=4))
    explicit = track['explicit']
    release_date = track['album']['release_date']
    release_date_precision = track['album']['release_date_precision']
    duration = track['duration_ms']
    popularity = track['popularity']

    features = spotify.audio_features(track['id'])[0]
    # logging.debug(json.dumps(features, indent=4))
    danceability = features['danceability']
    energy = features['energy']
    valence = features['valence']
    tempo = features['tempo']

    track = activeRecords.ActiveTrack(name, artist_result, champ, added_at, added_time,
        explicit, release_date, release_date_precision, duration, popularity,
        danceability, energy, valence, tempo)
    return track

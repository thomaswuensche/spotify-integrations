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
    explicit = track['explicit']

    #logging.debug(json.dumps(artist_result, indent=4))

    track = activeRecords.ActiveTrack(name, artist_result, champ, added_at, added_time,
        explicit)
    return track

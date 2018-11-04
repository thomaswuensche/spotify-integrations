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
    connection.commit()
    cursor.close()


def push_track_to_db(track, connection):
    track.setConnection(connection)
    logging.debug(track.toString())
    track.insert()


def get_track_data(item, spotify):
    track = item['track']

    name = track['name']
    champ = whodunit(item['added_by']['id'])
    added_at = item['added_at']
    artist_result = spotify.artist(track['artists'][0]['uri'])

    #logging.debug(json.dumps(artist_result, indent=4))

    track = activeRecords.ActiveTrack(name, artist_result, champ, added_at)
    return track

import logging

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


def get_last_id(connection, table):
    last_id = 0
    cursor = connection.cursor()
    sql = "SELECT id FROM {} ORDER BY id DESC LIMIT 1".format(table)

    result = cursor.execute(sql)
    for result in cursor:
        last_id = result[0]

    logging.info('last id: {}'.format(last_id))
    cursor.close()
    return last_id

def get_count_local_tracks(connection):
    cursor = connection.cursor()

    sql = "SELECT value FROM metadata WHERE name=%(name)s"
    val = {'name': 'count_local_tracks'}

    cursor.execute(sql, val)
    for result in cursor:
        count_local_tracks = result[0]

    logging.info('count of local tracks: {}'.format(count_local_tracks))
    cursor.close()
    return count_local_tracks

def increment_count_local_tracks(connection):
    cursor = connection.cursor()

    sql = "UPDATE metadata SET value = value+1 WHERE name=%(name)s"
    val = {'name': 'count_local_tracks'}

    cursor.execute(sql, val)

    cursor.close()
    return count_local_tracks

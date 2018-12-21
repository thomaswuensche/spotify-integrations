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

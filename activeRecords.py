import mysql.connector as mysql
import logging

class ActiveTrack():

    name = ""
    artist = None
    artist_name = ""
    champ = ""
    added_at = ""
    connection = None

    def __init__(self, name, artist, champ, added_at):
        self.name = name
        self.artist = artist
        self.artist_name = self.getArtistName()
        self.champ = champ
        self.added_at = added_at

    def setConnection(self, connection):
        self.connection = connection

    def getGenres(self):
        return self.artist['genres']

    def getArtistName(self):
        return self.artist['name']

    def toString(self):
        return self.name + " : " + self.getArtistName() + " : " + self.champ + " : " + self.added_at

    def insert(self):
        cursor = self.connection.cursor()

        sql = '''INSERT INTO pylonen (name, champ, artist, added_at)
            VALUES (%(name)s, %(champ)s, %(artist)s, %(added_at)s)'''
        val = {'name': self.name, 'champ': self.champ, 'artist': self.artist_name,
            'added_at': self.added_at}
        cursor.execute(sql, val)

        self.connection.commit()
        logging.info("1 record inserted, ID: {}".format(cursor.lastrowid))
        cursor.close()

    def testConnection(self):
        cursor = self.connection.cursor()

        query = "SELECT id, name FROM pylonen WHERE name = %(name)s"
        cursor.execute(query, {'name': self.name})

        for (id, name) in cursor:
            logging.info("id : {} - name : {}".format(id, name))

        cursor.close() # conection gets closed in calling script

import mysql.connector as mysql

class ActiveTrack():

    name = ""
    artist = None
    champ = ""
    added_at = ""
    connection = None

    def __init__(self, name, artist, champ, added_at):
        self.name = name
        self.artist = artist
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

    def testConnection(self, name):
        cursor = self.connection.cursor()

        query = ("SELECT id, name FROM tracks WHERE name = %(name)s")

        cursor.execute(query, {'name':name})

        for (id, name) in cursor:
            print("id : {} - name : {}".format(id, name))

        cursor.close() # conection gets closed in calling script

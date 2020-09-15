# import mysql.connector as mysql
import logging
import credentials

class ActiveTrack():

    def __init__(self, name, artist, champ, added_at, added_time, explicit,
        release_date, release_date_precision, duration, popularity,
        danceability, energy, valence, tempo):
        self.name = name
        self.artist = artist
        self.artist_name = self.getArtistName()
        self.champ = champ
        self.added_at = added_at
        self.added_time = added_time
        self.explicit = explicit
        self.release_date = release_date
        self.release_date_precision = release_date_precision
        self.duration = duration
        self.popularity = popularity
        self.danceability = danceability
        self.energy = energy
        self.valence = valence
        self.tempo = tempo

    def setConnection(self, connection):
        self.connection = connection

    def getGenres(self):
        return self.artist['genres']

    def getArtistName(self):
        return self.artist['name']

    def toString(self):
        return '{} : {} : {} : {} : {} : {} : {} : {} : {} : {} : {} : {} : {} : {}'.format(
            self.name,
            self.artist_name,
            self.champ,
            self.added_at,
            self.added_time,
            self.explicit,
            self.release_date,
            self.release_date_precision,
            self.duration,
            self.popularity,
            self.danceability,
            self.energy,
            self.valence,
            self.tempo)

    def insert(self):
        cursor = self.connection.cursor()

        sql = '''INSERT INTO {} (name, artist, champ, added_at,
            added_time, explicit, release_date, release_date_precision,
            duration, popularity, danceability, energy, valence, tempo)
            VALUES (%(name)s, %(artist)s, %(champ)s, %(added_at)s,
            %(added_time)s, %(explicit)s, %(release_date)s, %(release_date_precision)s,
            %(duration)s, %(popularity)s, %(danceability)s, %(energy)s,
            %(valence)s, %(tempo)s)'''.format(credentials.table)

        val = {'name': self.name,
            'artist': self.artist_name,
            'champ': self.champ,
            'added_at': self.added_at,
            'added_time': self.added_time,
            'explicit': self.explicit,
            'release_date': self.release_date,
            'release_date_precision': self.release_date_precision,
            'duration': self.duration,
            'popularity': self.popularity,
            'danceability': self.danceability,
            'energy': self.energy,
            'valence': self.valence,
            'tempo': self.tempo,}

        cursor.execute(sql, val)

        self.connection.commit()
        logging.info("1 record inserted, ID: {} - name: {}".format(cursor.lastrowid,
            self.name))
        cursor.close() # conection gets closed in calling script

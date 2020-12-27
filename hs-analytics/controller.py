import logging
import os
from psycopg2 import DatabaseError
import psycopg2.extras as pgextras

class AnalyticsController():

    def __init__(self, api, db_conn):
        self.api = api
        self.db_conn = db_conn
        self.tracks_to_insert = []
        self.audio_features = {}
        self.rows_inserted = 0

    def process_result(self, result):
        while True:
            items_filtered = list(filter(lambda item: not item['track']['is_local'], result['items']))
            self.store_audio_features(items_filtered)
            for item in items_filtered:
                self.add_track_to_bulk(item)

            self.bulk_insert()
            if not result['next']: break
            result = self.api.next(result)

    def store_audio_features(self, items):
        track_ids = [item['track']['id'] for item in items]
        audio_features_response = self.api.audio_features(track_ids)
        for item in audio_features_response:
            self.audio_features[item['id']] = {
                'danceability': item['danceability'],
                'energy': item['energy'],
                'valence': item['valence'],
                'tempo': item['tempo']
            }

    def bulk_insert(self):
        query = """
            INSERT INTO {}
                (name, artist, added_by_id, added_at, explicit,
                release_date, release_date_precision, duration_ms,
                popularity, danceability, energy, valence, tempo, link)
            VALUES %s
        """.format(os.environ['DB_TABLE'])
        db_cur = self.db_conn.cursor()

        try:
            pgextras.execute_values(db_cur, query, self.tracks_to_insert)
            self.db_conn.commit()
            self.rows_inserted += db_cur.rowcount
            logging.info('bulk_insert done: {} total rows inserted'.format(self.rows_inserted))
        except (DatabaseError) as error:
            logging.error(error)
            self.db_conn.rollback()

        db_cur.close()
        self.tracks_to_insert = []

    def add_track_to_bulk(self, item):
        db_track = {
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name'], # multiple artists
            'added_by_id': item['added_by']['id'],
            'added_at': item['added_at'],
            'explicit': item['track']['explicit'],
            'release_date': item['track']['album']['release_date'],
            'release_date_precision': item['track']['album']['release_date_precision'],
            'duration_ms': item['track']['duration_ms'],
            'popularity': item['track']['popularity'],
            'danceability': self.audio_features[item['track']['id']]['danceability'],
            'energy': self.audio_features[item['track']['id']]['energy'],
            'valence': self.audio_features[item['track']['id']]['valence'],
            'tempo': self.audio_features[item['track']['id']]['tempo'],
            'link': item['track']['external_urls']['spotify']
        }
        self.tracks_to_insert.append(tuple(db_track.values()))

    def reset_table(self, table):
        db_cur = self.db_conn.cursor()
        query = "DELETE FROM {}".format(table)
        db_cur.execute(query)
        logging.info('wipe table: {}'.format(table))

        query = "ALTER SEQUENCE {}_id_seq RESTART".format(table)
        db_cur.execute(query)
        logging.info('reset id sequence on table: {}'.format(table))

        self.db_conn.commit()
        db_cur.close()

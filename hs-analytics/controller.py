import logging
import os
from psycopg2 import DatabaseError
import psycopg2.extras as pgextras

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from spotify_client import SpotifyClient

class AnalyticsController(SpotifyClient):

    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.tracks_to_insert = []
        self.audio_features = {}
        self.rows_inserted = 0

    def save_tracks(self, playlist, destination_table):
        result = self.playlist_tracks(playlist)
        while True:
            items_filtered = list(filter(lambda item: not item['track']['is_local'], result['items']))
            self.store_audio_features(items_filtered)
            for item in items_filtered:
                self.add_track_to_bulk(item)

            self.bulk_insert(destination_table)
            if not result['next']: break
            result = self.next(result)

    def store_audio_features(self, items):
        track_ids = [item['track']['id'] for item in items]
        audio_features_response = super().audio_features(track_ids)
        for item in audio_features_response:
            self.audio_features[item['id']] = {
                'danceability': item['danceability'],
                'energy': item['energy'],
                'valence': item['valence'],
                'tempo': item['tempo']
            }

    def bulk_insert(self, table):
        query = f"""
            INSERT INTO {table}
                (name, artist, added_by_id, added_at, explicit,
                release_date, release_date_precision, duration_ms,
                popularity, danceability, energy, valence, tempo, link)
            VALUES %s
        """
        db_cur = self.db_conn.cursor()

        try:
            pgextras.execute_values(db_cur, query, self.tracks_to_insert)
            self.db_conn.commit()
            self.rows_inserted += db_cur.rowcount
            logging.info(f'bulk_insert done: {self.rows_inserted} total rows inserted')
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
        query = f'DELETE FROM {table}'
        db_cur.execute(query)
        logging.info(f'wipe table: {table}')

        query = f'ALTER SEQUENCE {table}_id_seq RESTART'
        db_cur.execute(query)
        logging.info(f'reset id sequence on table: {table}')

        self.db_conn.commit()
        db_cur.close()

import logging
import os
from psycopg2 import DatabaseError
import psycopg2.extras as pgextras

class CoverageBot():

    def __init__(self, api, username):
        self.api = api
        self.username = username
        self.flagged_tracks = {}
        self.covered_tracks = {}

    def process_coverage(self, result, destination_playlist):
        tracks_to_check = self.extract_tracks(result)
        covered_tracks = self.get_covered_tracks()
        flagged_tracks = self.get_flagged_tracks()

        diff = list(set(tracks_to_check.keys()) - set(covered_tracks.keys()) - set(flagged_tracks.keys()))
        logging.info('tracks not covered: ' + str(len(diff)))

        list_upload = self.sort_diff_tracks(diff, tracks_to_check)
        self.upload_that_shit(list_upload, destination_playlist)

    def get_flagged_tracks(self):
        logging.info('getting flagged tracks...')

        if not self.flagged_tracks:
            result = self.api.user_playlist_tracks(self.username, playlist_id=os.environ['PLAYLIST_COVERAGE_FLAGGED'])
            self.flagged_tracks = self.extract_tracks(result)

        return self.flagged_tracks

    def get_covered_tracks(self):
        logging.info('getting tracks from playlists...')

        if not self.covered_tracks:
            user_playlists = self.api.user_playlists(self.username)

            for playlist in user_playlists['items']:
                if ('_' in playlist['name']) or ('//' in playlist['name']):
                    logging.info(playlist['id'] + ' - ' + playlist['name'])
                    result = self.api.user_playlist_tracks(self.username, playlist_id=playlist['id'])
                    self.covered_tracks.update(self.extract_tracks(result))

        return self.covered_tracks

    def extract_tracks(self, result):
        tracks = {}
        while True:
            for item in result['items']:
                if not item['track']['is_local']:
                    tracks[item['track']['id']] = item['added_at']

            if not result['next']: break
            result = self.api.next(result)

        return tracks

    def sort_diff_tracks(self, diff, info_dict):
        logging.info('sorting tracks by added at...')
        diff_with_added_at = {}
        for item in diff:
            diff_with_added_at[item] = info_dict[item]

        sorted_tuples = sorted(diff_with_added_at.items(), reverse=True, key=lambda x: x[1])
        list_upload = []
        for item in sorted_tuples:
            list_upload.append(item[0])

        return list_upload

    def upload_that_shit(self, list_upload, playlist_id):
        logging.info('uploading tracks...')
        for i in range(0, len(list_upload), 100):
            if i == 0:
                self.api.user_playlist_replace_tracks(self.username, playlist_id, list_upload[i : i+100])
            else:
                self.api.user_playlist_add_tracks(self.username, playlist_id, list_upload[i : i+100])


class DataHandler():

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

    def bulk_insert(self):
        query = '''
            INSERT INTO {}
                (name, artist, added_by_id, added_at, explicit,
                release_date, release_date_precision, duration_ms,
                popularity, danceability, energy, valence, tempo, link)
            VALUES %s
        '''.format(os.environ['DB_TABLE'])
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

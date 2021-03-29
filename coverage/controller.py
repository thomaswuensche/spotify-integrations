import logging
import os
import re

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from spotify_client import SpotifyClient

class CoverageController(SpotifyClient):

    def __init__(self):
        super().__init__()
        self.flagged_tracks = []
        self.covered_tracks = []
        self.last_criteria = None

    def process_coverage(self, result, coverage_criteria, destination_playlist, min_date=None):
        tracks_to_check = self.extract_tracks(result)

        if min_date:
            tracks_to_check = list(filter(
                lambda track: track['added_at'] >= min_date,
                tracks_to_check
            ))

        tracks_to_check_size = len(tracks_to_check)
        logging.info(f'tracks to check: {tracks_to_check_size}')

        covered_tracks = self.get_covered_tracks(coverage_criteria)
        flagged_tracks = self.get_flagged_tracks()

        ids_covered_tracks = [x['id'] for x in covered_tracks]
        ids_flagged_tracks = [x['id'] for x in flagged_tracks]

        diff = list(filter(
            lambda track: track['id'] not in ids_covered_tracks and track['id'] not in ids_flagged_tracks,
            tracks_to_check
        ))

        diff_size = len(diff)
        diff_percent = round(diff_size / tracks_to_check_size * 100)
        logging.info(f'tracks not covered: {diff_size} ({diff_percent}%)')

        sorted_diff = self.sort_diff_tracks(diff)
        self.upload_diff(sorted_diff, destination_playlist)

    def get_flagged_tracks(self):
        logging.info('getting flagged tracks...')

        if not self.flagged_tracks:
            result = self.playlist_tracks(os.environ['PLAYLIST_COVERAGE_FLAGGED'])
            self.flagged_tracks = self.extract_tracks(result)

        return self.flagged_tracks

    def get_covered_tracks(self, criteria):

        if self.last_criteria != criteria:
            logging.info('getting tracks from playlists...')
            self.covered_tracks = []
            for playlist in self.get_filtered_playlists(criteria):
                logging.debug(playlist['id'] + ' - ' + playlist['name'])
                result = self.playlist_tracks(playlist['id'])
                self.covered_tracks += self.extract_tracks(result)
        else:
            logging.info('using cached covered_tracks')

        self.last_criteria = criteria
        return self.covered_tracks

    def get_filtered_playlists(self, criteria):
        filtered_playlists = []

        result = self.current_user_playlists()
        while True:
            filtered_playlists += list(filter(
                lambda playlist: re.search(criteria, playlist['name']) and playlist['owner']['id'] == os.environ['SPOTIFY_USERNAME'],
                result['items']
            ))
            if not result['next']: break
            result = self.next(result)

        excluded_playlists = os.environ['COVERAGE_EXCLUDE'].split(',')
        filtered_playlists = list(filter(
            lambda playlist: all(playlist['name'] != name for name in excluded_playlists),
            filtered_playlists
        ))
        return filtered_playlists

    def extract_tracks(self, result):
        tracks = []
        while True:
            for item in result['items']:
                if not item['track']['is_local']:
                    track_data = {
                        'id': item['track']['id'],
                        'added_at': item['added_at']
                    }
                    tracks.append(track_data)

            if not result['next']: break
            result = self.next(result)

        return tracks

    def sort_diff_tracks(self, diff):
        logging.debug('sorting tracks by added at...')

        return sorted(
            diff,
            reverse = int(os.environ['COVERAGE_REVERSE']),
            key = lambda track: track['added_at']
        )

    def upload_diff(self, diff, playlist):
        ids_to_upload = [x['id'] for x in diff]

        logging.info('removing all tracks from coverage playlist...')
        self.remove_all_from_playlist(playlist)

        if ids_to_upload:
            logging.info('uploading tracks...')
            for i in range(0, len(ids_to_upload), 100):
                self.playlist_add_items(playlist, ids_to_upload[i : i+100])

    def remove_all_from_playlist(self, playlist):
        result = self.playlist_tracks(playlist)
        tracks_to_remove = self.extract_tracks(result)
        ids_to_remove = [x['id'] for x in tracks_to_remove]

        for i in range(0, len(ids_to_remove), 100):
            self.playlist_remove_all_occurrences_of_items(playlist, ids_to_remove[i : i+100])

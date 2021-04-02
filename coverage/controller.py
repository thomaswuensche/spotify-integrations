import logging
import os
import re

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from spotify_client import SpotifyClient

class CoverageController(SpotifyClient):

    def __init__(self):
        super().__init__()
        self.cache = {}
        self.get_user_playlists()

    def check_coverage(self, origin, check_against, diff_pl, min_date=None, type=None):
        tracks_to_check = self.extract_tracks(origin)

        if min_date:
            tracks_to_check = list(filter(
                lambda track: track['added_at'] >= min_date,
                tracks_to_check
            ))

        tracks_to_check_size = len(tracks_to_check)
        logging.info(f'tracks to check: {tracks_to_check_size}')

        if type == 'playlist':
            covered_tracks = self.extract_tracks(check_against)
        else:
            covered_tracks = self.get_covered_tracks(check_against)

        flagged_tracks = self.extract_tracks(
            os.environ['PLAYLIST_COVERAGE_FLAGGED'],
            verbose = False
        )

        ids_covered_tracks = [x['id'] for x in covered_tracks]
        ids_flagged_tracks = [x['id'] for x in flagged_tracks]

        diff_tracks = list(filter(
            lambda track: track['id'] not in ids_covered_tracks and track['id'] not in ids_flagged_tracks,
            tracks_to_check
        ))

        diff_size = len(diff_tracks)
        diff_percent = round(diff_size / tracks_to_check_size * 100)
        logging.info(f'tracks not covered: {diff_size} ({diff_percent}%)')

        sorted_diff = self.sort_diff_tracks(diff_tracks)
        self.upload_diff(sorted_diff, diff_pl)

    def get_covered_tracks(self, criteria):
        logging.info('getting tracks from playlists...')
        covered_tracks = []
        for playlist in self.get_filtered_playlists(criteria):
            covered_tracks += self.extract_tracks(
                playlist['id'],
                verbose = False
            )

        return covered_tracks

    def get_user_playlists(self):
        self.user_playlists = []
        result = self.current_user_playlists()
        while True:
            for playlist in result['items']:
                self.user_playlists.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'owner': playlist['owner']['id']
                })
            if not result['next']: break
            result = self.next(result)

    def get_filtered_playlists(self, criteria):
        filtered_playlists = []

        result = self.current_user_playlists()
        while True:
            filtered_playlists += list(filter(
                lambda playlist: re.search(criteria, playlist['name']) and playlist['owner'] == os.environ['SPOTIFY_USERNAME'],
                self.user_playlists
            ))
            if not result['next']: break
            result = self.next(result)

        excluded_playlists = os.environ['COVERAGE_EXCLUDE'].split(',')
        filtered_playlists = list(filter(
            lambda playlist: all(playlist['name'] != name for name in excluded_playlists),
            filtered_playlists
        ))
        return filtered_playlists

    def extract_tracks(self, id, verbose=True):
        if id not in self.cache:
            if id == 'library':
                result = self.current_user_saved_tracks(limit=50)
                name = 'library'
            else:
                result = self.playlist_tracks(id)
                name = next(filter(lambda playlist: playlist['id'] == id, self.user_playlists))['name']

            if verbose: logging.info(f"extracting tracks from {name}...")

            tracks = []
            while True:
                for item in result['items']:
                    if not item['track']['is_local']:
                        tracks.append({
                            'id': item['track']['id'],
                            'added_at': item['added_at']
                        })

                if not result['next']: break
                result = self.next(result)

            self.cache[id] = tracks

        return self.cache[id]

    def sort_diff_tracks(self, diff_tracks):
        logging.debug('sorting tracks by added at...')

        return sorted(
            diff_tracks,
            reverse = int(os.environ['COVERAGE_REVERSE']),
            key = lambda track: track['added_at']
        )

    def upload_diff(self, diff_tracks, diff_pl):
        ids_to_upload = [x['id'] for x in diff_tracks]

        logging.info('removing all tracks from diff playlist...')
        self.remove_all_from_playlist(diff_pl)

        if ids_to_upload:
            logging.info('uploading tracks to diff playlist...')
            for i in range(0, len(ids_to_upload), 100):
                self.playlist_add_items(diff_pl, ids_to_upload[i : i+100])

    def remove_all_from_playlist(self, playlist_id):
        tracks_to_remove = self.extract_tracks(
            playlist_id,
            verbose=False
        )
        ids_to_remove = [x['id'] for x in tracks_to_remove]

        for i in range(0, len(ids_to_remove), 100):
            self.playlist_remove_all_occurrences_of_items(playlist_id, ids_to_remove[i : i+100])

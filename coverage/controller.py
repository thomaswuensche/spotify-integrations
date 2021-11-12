import logging
import os
import re
from rich.progress import track as track_progress

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

        ids_covered_tracks = self.get_covered_ids(type, check_against)
        ids_flagged_tracks = self.get_flagged_ids()

        diff_tracks = list(filter(
            lambda track: track['id'] not in ids_covered_tracks and track['id'] not in ids_flagged_tracks,
            tracks_to_check
        ))

        diff_size = len(diff_tracks)
        diff_percent = round(diff_size / tracks_to_check_size * 100)
        logging.info(f'tracks not covered: {diff_size} ({diff_percent}%)')

        if not origin.startswith('top_tracks'):
            diff_tracks = self.sort_diff_tracks(diff_tracks)

        self.upload_diff(diff_tracks, diff_pl)

    def get_covered_ids(self, type, check_against):
        if type == 'regex':
            covered_tracks = self.get_covered_tracks_regex(check_against)
        elif type == 'logic':
            covered_tracks = self.get_covered_tracks_logic(check_against)
        else:
            covered_tracks = self.extract_tracks(check_against)
        return [x['id'] for x in covered_tracks]

    def get_covered_tracks_regex(self, regex):
        logging.info('getting tracks from playlists...')
        covered_tracks = []
        for playlist in self.get_filtered_playlists(regex):
            covered_tracks += self.extract_tracks(
                playlist['id'],
                verbose = False
            )
        return covered_tracks

    def get_covered_tracks_logic(self, check_against):
        if check_against == 'timeline_current':
            return self.get_covered_tracks_timeline_current()

    def get_covered_tracks_timeline_current(self):
        timeline_playlists = self.get_filtered_playlists('^\\w\\.\\d{2}(\\.\\d{2})?$')
        timeline_order = ['w', 'f', 's', 'h']
        timeline_playlists = sorted(
            timeline_playlists,
            key = lambda playlist: f"{playlist['name'].split('.')[-1]}-{timeline_order.index(playlist['name'].split('.')[0])}"
        )
        return self.extract_tracks(timeline_playlists[-1]['id'])

    def get_flagged_ids(self):
        flagged_tracks = self.extract_tracks(
            os.environ['PLAYLIST_COVERAGE_FLAGGED'],
            verbose = False
        )
        return [x['id'] for x in flagged_tracks]

    def get_filtered_playlists(self, regex):
        filtered_playlists = list(filter(
            lambda playlist: re.search(regex, playlist['name']) and playlist['owner'] == os.environ['SPOTIFY_USERNAME'],
            self.user_playlists
        ))

        excluded_playlists = os.environ['COVERAGE_EXCLUDE'].split(',')
        return list(filter(
            lambda playlist: all(playlist['name'] != name for name in excluded_playlists),
            filtered_playlists
        ))

    def extract_tracks(self, id, verbose=True):
        if id in self.cache:
            if verbose: logging.info(f'using cached tracks from {self.id_origin(id)}...')
        else:
            if id == 'library':
                result = self.current_user_saved_tracks(limit=50)
            elif id.startswith('top_tracks'):
                result = self.current_user_top_tracks(limit=50, time_range=id.split(':')[-1])
            else:
                result = self.playlist_tracks(id)

            sequence = range(0, result['total'], result['limit'])
            if verbose:
                sequence = track_progress(sequence, description='')
                logging.info(f'extracting tracks from {self.id_origin(id)}...')

            self.cache[id] = self.extract_from_result(result, sequence)

        return self.cache[id]

    def extract_from_result(self, result, sequence):
        tracks = []
        for i in sequence:
            for item in result['items']:
                if 'track' in item:
                    if not item['track']['is_local']:
                        tracks.append({
                            'id': item['track']['id'],
                            'added_at': item['added_at']
                        })
                else:
                    tracks.append({'id': item['id']})

            result = self.next(result)

        return tracks

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

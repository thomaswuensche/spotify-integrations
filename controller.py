import logging
import os

class CoverageController():

    def __init__(self, api):
        self.api = api
        self.flagged_tracks = {}
        self.covered_tracks = {}

    def process_coverage(self, result, destination_playlist):
        tracks_to_check = self.extract_tracks(result)

        tracks_to_check_size = len(tracks_to_check)
        logging.info(f'tracks to check: {tracks_to_check_size}')

        covered_tracks = self.get_covered_tracks()
        flagged_tracks = self.get_flagged_tracks()

        diff = list(set(tracks_to_check.keys()) - set(covered_tracks.keys()) - set(flagged_tracks.keys()))

        diff_size = len(diff)
        diff_percent = round(diff_size / tracks_to_check_size * 100)
        logging.info(f'tracks not covered: {diff_size} ({diff_percent}%)')

        list_upload = self.sort_diff_tracks(diff, tracks_to_check)
        self.upload_that_shit(list_upload, destination_playlist)

    def get_flagged_tracks(self):
        logging.info('getting flagged tracks...')

        if not self.flagged_tracks:
            result = self.api.playlist_tracks(playlist_id=os.environ['PLAYLIST_COVERAGE_FLAGGED'])
            self.flagged_tracks = self.extract_tracks(result)

        return self.flagged_tracks

    def get_covered_tracks(self):
        logging.info('getting tracks from playlists...')

        if not self.covered_tracks:

            for playlist in self.get_filtered_playlists():
                logging.debug(playlist['id'] + ' - ' + playlist['name'])
                result = self.api.playlist_tracks(playlist_id=playlist['id'])
                self.covered_tracks.update(self.extract_tracks(result))

        return self.covered_tracks

    def get_filtered_playlists(self):
        criteria = os.environ['PLAYLIST_CRITERIA'].split(',')
        filtered_playlists = []

        result = self.api.current_user_playlists()
        while True:
            filtered_playlists += list(filter(
                lambda playlist: any(crit in playlist['name'] for crit in criteria) and playlist['owner']['id'] == os.environ['SPOTIFY_USERNAME'],
                result['items']
            ))
            if not result['next']: break
            result = self.api.next(result)

        return filtered_playlists

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
        logging.debug('sorting tracks by added at...')
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
                self.api.playlist_replace_items(playlist_id, list_upload[i : i+100])
            else:
                self.api.playlist_add_items(playlist_id, list_upload[i : i+100])

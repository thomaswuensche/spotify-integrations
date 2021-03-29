import logging
import os
from pprint import pformat
from datetime import datetime

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util
from spotify_client import SpotifyClient

util.set_logging_config()
api = SpotifyClient()

date = datetime.today().strftime('%Y-%m-%d')

try:
    os.mkdir(f'{os.path.dirname(__file__)}/{date}')
except FileExistsError:
    logging.info(f'dir {date} already exists')

for time_range in ['short_term', 'medium_term', 'long_term']:
    result = api.current_user_top_tracks(limit=50, time_range=time_range)
    tracks = [f"{item['name']} - {item['artists'][0]['name']}" for item in result['items']]
    with open(f'{os.path.dirname(__file__)}/{date}/tracks_{time_range}.txt', 'w') as file:
        file.write(pformat(tracks))

    result = api.current_user_top_artists(limit=50, time_range=time_range)
    artists = [item['name'] for item in result['items']]
    with open(f'{os.path.dirname(__file__)}/{date}/artists_{time_range}.txt', 'w') as file:
        file.write(pformat(artists))

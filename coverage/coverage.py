import logging
import os
import json
from controller import CoverageController

import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util

util.set_logging_config()
controller = CoverageController()

with open(os.path.abspath(f'{os.path.dirname(__file__)}/tasks.json')) as file:
    tasks = file.read().replace('hs_id', os.environ['PLAYLIST_HS'])
    for task in json.loads(tasks):
        logging.info(task['name'])

        controller.check_coverage(
            origin = task['origin'],
            check_against = task['check_against'],
            diff_pl = task['diff_pl'],
            min_date = task['min_date'],
            type = task['type']
        )

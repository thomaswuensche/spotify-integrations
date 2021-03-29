import logging
import os

def set_logging_config():
    logging.basicConfig(
        level=int(os.environ['LOG_LEVEL']),
        format='%(levelname)s : %(funcName)s @ %(lineno)s - %(message)s'
    )

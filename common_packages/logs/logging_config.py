import logging
import os


def setup_logger(file):
    log = logging.getLogger(os.path.dirname(os.path.abspath(file)))
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

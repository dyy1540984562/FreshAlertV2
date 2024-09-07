import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logger(name, log_folder):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_file = os.path.join(log_folder, f'{name}.log')
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
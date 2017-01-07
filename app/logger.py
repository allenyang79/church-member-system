# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.handlers  # import  RotatingFileHandler

from app.config import config

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s:%(lineno)d\t[%(thread)8.8s][%(levelname)5.5s] - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

log_path = os.path.join(config.getpath('global', 'logs_dir'), 'log.log')
print log_path
file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=100 * 1000 * 1000, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

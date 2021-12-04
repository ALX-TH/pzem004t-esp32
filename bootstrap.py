#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from app.application import Application

DEBUG = os.environ.get('DEBUG', False)

def entrypoint():

    if DEBUG:
        logging.basicConfig(
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}', 
            level=logging.DEBUG, 
            datefmt='%d-%b-%y %H:%M:%S'
        )
    else: 
        logging.basicConfig(
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}', 
            level=logging.INFO, 
            datefmt='%d-%b-%y %H:%M:%S'
        )

    path = os.path.dirname(os.path.realpath(__file__))
    app = Application(path, logging)

    try:
        logging.info('Application starting')
        app.main()
    except KeyboardInterrupt:
        logging.info('Application interrupted by user request [CRTL+C]')
    finally:
        logging.info('Application stopped')


if __name__ == '__main__':
    entrypoint()
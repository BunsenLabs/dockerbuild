import os
import logging

logging.basicConfig(level=logging.INFO)

DEBUG = logging.DEBUG
LOGGER = logging.getLogger(name=__package__)
LOGGER.setLevel(logging.INFO)

PKGPATH = os.path.dirname(os.path.abspath(__file__))
CONTAINERSCRIPTSPATH = os.path.join(PKGPATH, "containerscripts")

def enable_debug_logging():
    LOGGER.setLevel(logging.DEBUG)

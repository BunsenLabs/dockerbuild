import os
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(name=__package__)
LOGGER.setLevel(logging.INFO)

PKGPATH = os.path.dirname(os.path.abspath(__file__))
OPTIONPATH = os.path.join(PKGPATH, "cli.yml")
CONTAINERSCRIPTSPATH = os.path.join(PKGPATH, "containerscripts")

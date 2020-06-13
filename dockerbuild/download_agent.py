from argparse import Namespace
from functools import partial
from multiprocessing import Process
from pathlib import Path
from typing import Callable
import logging
import os
import requests
import shutil

from dockerbuild.cap import has_caps

logger = logging.getLogger(__name__)

class DownloadAgent:
    def __init__(self, opts: Namespace):
        self.__opts: Namespace = opts

    def download(self, url: str, dest: Path) -> bool:
        parent = dest.parent
        _setgid = lambda: True
        _setuid = lambda: True
        can_setgid = has_caps(os.getpid(), set([ 'CAP_SETGID' ]))
        can_setuid = has_caps(os.getpid(), set([ 'CAP_SETUID' ]))

        if dest.exists():
            logger.error('Download destination already exists, refusing to overwrite')
            return False

        if not parent.is_dir():
            logger.error('Download destination parent is not a directory: %s', dedst)
            return False

        p = Process(target=self.__get, args=(
            _setgid,
            _setuid,
            self.__opts.unpriv_uid,
            self.__opts.unpriv_gid,
            url,
            dest,)
        )
        p.start()
        p.join()
        logger.error("%s %d", str(p), p.exitcode)
        if p.exitcode != 0:
            logger.error('Download process exited with status %d', p.exitcode)
            return False

        if not dest.is_file():
            logger.error('Impossible state: Download successful but destination not a file')
            return False

        return True

    @staticmethod
    def __get(setgid: Callable, setuid: Callable, uid: int, gid: int, url: str, path: Path) -> int:
        if not (setgid() and setuid()):
            raise OSError(f"Failed to drop privileges")
        with path.open("wb") as FILE:
            resp = requests.get(url, stream=True, allow_redirects=True)
            resp.raw.decode_content = True # gunzip
            shutil.copyfileobj(resp.raw, FILE)
            resp.close()
        return 0

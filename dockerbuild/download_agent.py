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

        if has_caps(os.getpid(), set([ 'CAP_SETGID' ])):
            logger.debug("Have CAP_SETGID, preparing privdrop for GID")
            _setgid = lambda: os.setgid(self.__opts.unpriv_gid)
            shutil.chown(dest, group=self.__opts.unpriv_uid)
            dest.chmod(dest.stat().st_mode | 0o00070)
            logger.debug("Changed mode of <%s> to %o for setgid download", dest, dest.stat().st_mode)

        if has_caps(os.getpid(), set([ 'CAP_SETUID' ])):
            logger.debug("Have CAP_SETUID, preparing privdrop for UID")
            _setuid = lambda: os.setuid(self.__opts.unpriv_uid)
            shutil.chown(dest, owner=self.__opts.unpriv_uid)
            dest.chmod(dest.stat().st_mode | 0o00700)
            logger.debug("Changed mode of <%s> to %o for setuid download", dest, dest.stat().st_mode)

        if dest.exists():
            logger.error('Download destination already exists, refusing to overwrite')
            return False

        if not parent.is_dir():
            logger.error('Download destination parent is not a directory: %s', dedst)
            return False

        p = Process(target=self.__get, args=(_setgid, _setuid, url, dest,))
        p.start()
        p.join()

        if p.exitcode != 0:
            logger.error('Download process exited with status %d', p.exitcode)
            return False

        if not dest.is_file():
            logger.error('Impossible state: Download successful but destination not a file')
            return False

        return True

    @staticmethod
    def __get(setgid: Callable, setuid: Callable, url: str, path: Path) -> int:
        assert setgid(), "Failed to call setgid() callable"
        assert setuid(), "Failed to call setuid() callable"
        with path.open("wb") as FILE:
            logger.debug("Opened file for writing: %s", path)
            resp = requests.get(url, stream=True, allow_redirects=True)
            logger.debug("Opened request: %s", url)
            resp.raw.decode_content = True # gunzip
            logger.debug("Writing download...")
            shutil.copyfileobj(resp.raw, FILE)
            logger.debug("Finished writing download")
            resp.close()
        return 0

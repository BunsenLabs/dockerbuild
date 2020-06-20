from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from functools import partial
from pathlib import Path
import grp
import logging
import os
import pwd

from dockerbuild.commands.build import build
from dockerbuild.commands.batch import batch
from dockerbuild import enable_debug_logging

def main() -> int:
    def absolute_path(path: Path) -> Path:
        return path.absolute()

    ap = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    ap.add_argument("-d", "--debug", action="store_true", default=False, help="Enable debug output")
    ap.add_argument("--unpriv-user", default="nobody", type=str, help="Privdrop to this user for untrusted operations")
    ap.add_argument("--unpriv-group", default="nobody", type=str, help="Privdrop to this group for untrusted operations")

    sp = ap.add_subparsers()

    def X(*args, **kwargs):
        _args = list(args)
        parser = _args.pop()
        parser.add_argument(*_args, **kwargs)

    iface = {
        'build': [
            partial(X, '-a', '--architecture', choices=['amd64','i386','armhf','arm64'], default='amd64', help='buildarch'),
            partial(X, '-o', '--output', type=absolute_path, default=Path(os.getcwd()), help='destdir'),
            partial(X, '-s', '--source', required=True, type=absolute_path, help='srcdir'),
            partial(X, '-t', '--timeout', type=int, default=7200, help='dockerd operation timeout'),
        ],
        'batch': [
            partial(X, "project_list", nargs='*'),
            partial(X, "-o", "--output-dir", type=absolute_path, default=Path(os.getcwd())),
            partial(X, "-b", "--build-dir", type=absolute_path, default=Path(os.getcwd())),
        ],
    }

    for cmd in iface:
        parser = sp.add_parser(cmd)
        parser.set_defaults(cmd=cmd)
        for option in iface[cmd]:
            option(parser)

    opts = ap.parse_args()

    if opts.debug:
        enable_debug_logging()

    logger = logging.getLogger(__name__)

    try:
        passwd_ent = pwd.getpwnam(opts.unpriv_user)
        groups_ent = grp.getgrnam(opts.unpriv_group)
        setattr(opts, "unpriv_uid", passwd_ent[2])
        setattr(opts, "unpriv_gid", groups_ent[2])
        logger.debug("Resolved unpriv-{user,group}: %d:%d", opts.unpriv_uid, opts.unpriv_gid)
    except KeyError as err:
        logger.error('UID/GID not found in passwd/groups database: %s', err)
        return 1

    try:
        func = globals()[opts.cmd]
        return func(opts)
    except KeyError:
        return 1

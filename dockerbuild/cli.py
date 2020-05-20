from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from functools import partial
from pathlib import Path
import os

from dockerbuild.commands.build import build
from dockerbuild.commands.batch import batch
from dockerbuild import enable_debug_logging

def main() -> int:
    ap = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    ap.add_argument("-d", "--debug", action="store_true", default=False, help="Enable debug output")

    sp = ap.add_subparsers()

    def X(*args, **kwargs):
        _args = list(args)
        parser = _args.pop()
        parser.add_argument(*_args, **kwargs)

    iface = {
        'build': [
            partial(X, '-a', '--architecture', choices=['amd64','i386','armhf'], default='amd64', help='buildarch'),
            partial(X, '-o', '--output', type=Path, default=Path(os.getcwd()), help='destdir'),
            partial(X, '-s', '--source', required=True, type=Path, help='srcdir'),
            partial(X, '-t', '--timeout', type=int, default=7200, help='dockerd operation timeout'),
        ],
        'batch': [
            partial(X, "project_list", nargs='*'),
            partial(X, "-o", "--output-dir", type=Path, default=Path(os.getcwd())),
            partial(X, "-b", "--build-dir", type=Path, default=Path(os.getcwd())),
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

    try:
        func = globals()[opts.cmd]
        return func(opts)
    except KeyError:
        return 1

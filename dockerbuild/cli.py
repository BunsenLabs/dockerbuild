from dockerbuild import OPTIONPATH
from dockerbuild.build import build
from dockerbuild.utils.options import getopts

def main() -> int:
    opts = getopts(OPTIONPATH)
    build(opts)
    return 0

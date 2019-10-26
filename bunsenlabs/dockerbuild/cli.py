from bunsenlabs.dockerbuild import OPTIONPATH
from bunsenlabs.dockerbuild.build import build
from bunsenlabs.utils.options import getopts

def main() -> int:
    opts = getopts(OPTIONPATH)
    build(opts)
    return 0

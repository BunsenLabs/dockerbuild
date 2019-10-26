from typing import Optional

RELEASE_MAP = {
    'bunsen-hydrogen' : 'jessie',
    'hydrogen'        : 'jessie', # not used
    'helium'          : 'stretch',
    'lithium'         : 'buster',
    'beryllium'       : 'buzz',
}

def get_debian_base_release(bunsenlabs_release: str) -> str:
    return RELEASE_MAP.get(bunsenlabs_release, bunsenlabs_release)

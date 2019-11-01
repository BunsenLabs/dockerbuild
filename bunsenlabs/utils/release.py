RELEASE_MAP = {
    'beryllium'         : 'buzz',
    'bunsen-hydrogen'   : 'jessie',
    'buster-backports'  : 'buster',
    'helium'            : 'stretch',
    'hydrogen'          : 'jessie', # not used
    'jessie-backports'  : 'jessie',
    'lithium'           : 'buster',
    'stretch-backports' : 'stretch',
}

def get_debian_base_release(bunsenlabs_release: str) -> str:
    return RELEASE_MAP.get(bunsenlabs_release, bunsenlabs_release)

from argparse import Namespace
import grp
import os
import pwd

import pytest

@pytest.fixture
def opts_nobody_uid_gid():
        opts = Namespace()
        setattr(opts, "unpriv_uid", pwd.getpwnam("nobody")[2])
        setattr(opts, "unpriv_gid", grp.getgrnam("nobody")[2])
        return opts

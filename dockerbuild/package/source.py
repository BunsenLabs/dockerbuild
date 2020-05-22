from dataclasses import dataclass
from debian.changelog import Changelog
from dockerbuild.utils.release import get_debian_base_release
import hashlib
import os

@dataclass
class PackageSource:
    pkgdir: str
    controlpath: str = ''
    changelogpath: str = ''

    def __post_init__(self):
        self.pkgdir = os.path.abspath(self.pkgdir)
        self.controlpath = os.path.join(self.pkgdir, 'debian', 'control')
        self.changelogpath = os.path.join(self.pkgdir, 'debian', 'changelog')

#    def archive(self) -> PackageSourceArchive:
#        filename = f'{self.name}_{self.release_upstream_version}.orig.tar.gz'
#        if self.is_git:
#            pass
#        else:
#            pass

    @property
    def changelog(self) -> Changelog:
        with open(self.changelogpath, 'r') as FILE:
            return Changelog(FILE)

    @property
    def release_upstream_version(self) -> str:
        return self.changelog[0].version.upstream_version

    @property
    def release_version(self) -> str:
        return self.changelog[0].version.full_version

    @property
    def release_distro(self) -> str:
        return self.changelog[0].distributions

    @property
    def release_debian_distro(self) -> str:
        return get_debian_base_release(self.release_distro)

    @property
    def name(self) -> str:
        return self.changelog[0].package

    @property
    def control_hash(self) -> str:
        h = hashlib.sha256()
        with open(self.controlpath, 'rb') as FILE:
            h.update(FILE.read())
        return h.hexdigest()

    @property
    def source_id(self) -> str:
        return f'{self.release_debian_distro}:{self.control_hash}'

    @property
    def is_git(self) -> bool:
        return os.path.isdir(os.path.join(self.pkgdir, '.git'))

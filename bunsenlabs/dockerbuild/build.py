from bunsenlabs.dockerbuild import CONTAINERSCRIPTSPATH
from bunsenlabs.utils.release import get_debian_base_release
from dataclasses import dataclass
from debian.changelog import Changelog
import docker
import hashlib
import logging
import os
import re

logger = logging.getLogger(name=__name__)

@dataclass
class PackageSourceArchive:
    packagename: str
    version: str
    filename: str
    filedata: str

@dataclass
class PackageSource:
    pkgdir: str
    controlpath: str = None
    changelogpath: str = None

    def __post_init__(self):
        self.pkgdir = os.path.abspath(self.pkgdir)
        self.controlpath = os.path.join(self.pkgdir, 'debian', 'control')
        self.changelogpath = os.path.join(self.pkgdir, 'debian', 'changelog')

    def archive(self) -> PackageSourceArchive:
        filename = f'{self.name}_{self.release_upstream_version}.orig.tar.gz'
        if self.is_git:
            pass
        else:
            pass

    @property
    def changelog(self):
        with open(self.changelogpath, 'r') as FILE:
            return Changelog(FILE)

    @property
    def release_upstream_version(self):
        return self.changelog[0].version.upstream_version

    @property
    def release_version(self):
        return self.changelog[0].version.full_version

    @property
    def release_distro(self):
        return self.changelog[0].distributions

    @property
    def release_debian_distro(self):
        return get_debian_base_release(self.release_distro)

    @property
    def name(self):
        return self.changelog[0].package

    @property
    def control_hash(self):
        h = hashlib.sha256()
        with open(self.controlpath, 'rb') as FILE:
            h.update(FILE.read())
        return h.hexdigest()

    @property
    def source_id(self):
        return f'{self.release_debian_distro}:{self.control_hash}'

    @property
    def is_git(self):
        return os.path.isdir(os.path.join(self.pkgdir, '.git'))

class PackageBuilder:
    def __init__(self, source: PackageSource, output_dir: str, architecture: str = 'amd64'):
        self.__source = source
        self.__output_dir = output_dir
        self.__docker = docker.from_env(timeout=3600)
        self.__architecture = architecture
        logger.info('Source ID for this build: %s', self.source.source_id)

    def create_dependency_image(self):
        """ Creates a Docker layer that contains the build dependencies of the
        source package preinstalled. """
        image = self.find_dependency_image()
        image_tag = f'{self.source.name}:latest'
        if image is not None:
            return image
        logger.info('Building dependency image...')
        container = self.__docker.containers.run(
                self.docker_base_image,
                command = '/mnt/containerscripts/installdependencies.sh',
                detach  = True,
                labels  = self.docker_labels,
                volumes = self.docker_volumes,
        )
        logger.info('Container %s launched, waiting for exit...', container.id)
        status = container.wait(timeout=3600)
        if not (status.get('Error') is None and status.get('StatusCode') == 0):
            logger.error('Container failed with non-zero exit status: %s', status.get('Error'))
            raise Exception('Container run failed')
        container.commit(repository='blsrc')
        return self.find_dependency_image()

    def find_dependency_image(self):
        logger.info('Looking for image using filter: %s', self.docker_dependency_image_filter)
        for image in self.__docker.images.list(filters=self.docker_dependency_image_filter):
            return image
        logger.info('No image found')
        return None

    def build(self):
        image = self.create_dependency_image()
        logging.info('Using dependency image: %s', image.id)
        volumes = self.docker_volumes
        volumes.update({
            self.__output_dir: {
                'bind': '/mnt/output',
                'mode': 'rw'
            }
        })
        logging.info('Using build container volumes: %s', volumes)
        container = self.__docker.containers.run(
                image,
                command='/mnt/containerscripts/build.sh',
                detach=True,
                volumes=volumes
        )
        logging.info('Container launched: %s', container.id)
        status = container.wait(timeout=3600)
        if not (status.get('Error') is None and status.get('StatusCode') == 0):
            logger.error('Container failed with exit status: %d', status.get('StatusCode'))
            logger.error('Error string: %s', status.get('Error'))
            logger.error('Dumping stdout and stderr')
            logger.error('%s', container.logs(stdout=True, stderr=True))
            logger.info('Removing container')
            container.remove()
            raise Exception('Build failed')
        container.remove()

    @property
    def source(self):
        return self.__source

    @property
    def docker_labels(self):
        return {
            'BL_BUILD_ARCH': self.architecture,
            'BL_SOURCE_ID': self.source.source_id,
            'BL_SOURCE_NAME': self.source.name,
            'BL_SOURCE_VERSION': self.source.release_version,
        }

    @property
    def docker_dependency_image_filter(self):
        return { 'label': [
            f'BL_SOURCE_ID={self.source.source_id}',
            f'BL_BUILD_ARCH={self.architecture}',
        ]}

    @property
    def docker_volumes(self):
        return {
            CONTAINERSCRIPTSPATH: {
                'bind': '/mnt/containerscripts',
                'mode': 'ro'
            },
            self.source.pkgdir: {
                'bind': '/mnt/package',
                'mode': 'ro'
            }
        }

    @property
    def architecture(self):
        return self.__architecture

    @property
    def docker_base_image(self):
        prefix = ''
        if self.architecture == 'i386':
            prefix = 'i386/'
        return '{}debian:{}'.format(prefix, self.source.release_debian_distro)

def build(opts):
    logger.info('Beginning package build.')
    logger.info('Initializing source object')
    source = PackageSource(pkgdir=opts.source)
    logger.info('Initializing builder object')
    builder = PackageBuilder(source, opts.output, architecture = opts.architecture)
    logger.info('Beginning build process')
    builder.build()

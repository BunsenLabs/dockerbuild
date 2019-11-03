from bunsenlabs.dockerbuild import CONTAINERSCRIPTSPATH
from bunsenlabs.dockerbuild.package.source import PackageSource
import docker
import logging

DEBIAN_DOCKER_ARCH_MAP = {
    'amd64': '',
    'i386':  'i386',
    'armhf': 'arm32v7'
}

logger = logging.getLogger(name=__name__)

class PackageBuilder:
    def __init__(self, source: PackageSource, output_dir: str,
                 architecture: str = 'amd64', docker_timeout: int = 3600):
        self.__architecture = architecture
        self.__docker = docker.from_env(timeout=docker_timeout)
        self.__docker_wait_timeout = docker_timeout
        self.__output_dir = output_dir
        self.__source = source
        logger.info('Source ID for this build: %s', self.source.source_id)

    def create_dependency_image(self):
        """ Creates a Docker layer that contains the build dependencies of the
        source package preinstalled. """
        image = self.find_dependency_image()
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
        status = container.wait(timeout=self.__docker_wait_timeout)
        if not (status.get('Error') is None and status.get('StatusCode') == 0):
            logger.error('Container failed with non-zero exit status: %s', status.get('Error'))
            raise Exception('Container run failed')
        container.commit()
        container.remove()
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
        status = container.wait(timeout=self.__docker_wait_timeout)
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
        docker_repo = DEBIAN_DOCKER_ARCH_MAP.get(self.architecture, '')
        if len(docker_repo) > 0:
            docker_repo += '/'
        return '{}debian:{}'.format(docker_repo, self.source.release_debian_distro)

def build(opts):
    logger.info('Beginning package build.')

    logger.info('Initializing source object')
    source = PackageSource(pkgdir=opts.source)

    logger.info('Initializing builder object')
    builder = PackageBuilder(
        source, opts.output,
        architecture=opts.architecture,
        docker_timeout=opts.timeout,
    )

    logger.info('Beginning build process')
    builder.build()

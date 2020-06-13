import logging

from dockerbuild import CONTAINERSCRIPTSPATH
from dockerbuild.package.builder import PackageBuilder
from dockerbuild.package.source import PackageSource

logger = logging.getLogger(name=__name__)

def build(opts) -> int:
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

    return 0

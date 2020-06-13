#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
        name                 = "dockerbuild",
        version              = "1.0.0",
        author               = "Jens John",
        author_email         = "dev@2ion.de",
        description          = "Docker-based staged builds of Debian packages",
        entry_points         = { "console_scripts": [ "dockerbuild=dockerbuild.cli:main" ] },
        include_package_data = True,
        install_requires     = [ "docker", "python-debian", "pygithub", "requests" ],
        license              = "GPL3",
        packages             = find_packages(),
        python_requires      = ">=3.8",
        url                  = "https://github.com/BunsenLabs/dockerbuild",
)


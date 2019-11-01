#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
        name = "bl-dockerbuild",
        version = "1.0.6",
        install_requires = [
                "PyYAML>=5.1.0",
                "docker",
                "python-debian",
        ],
        packages = find_packages(),
        entry_points={
                "console_scripts": [
                        "dockerbuild = bunsenlabs.dockerbuild.cli.main"
                ]
        },
        author = "Jens John",
        author_email = "dev@2ion.de",
        description = "Docker-based staged builds of Debian packages",
        license = "GPL3",
        url = "https://github.com/2ion/dockerbuild",
        include_package_data=True,
)


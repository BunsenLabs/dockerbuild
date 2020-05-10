#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
        name = "dockerbuild",
        version = "1.0.0",
        install_requires = [
                "docker",
                "python-debian",
                "pygithub",
                "requests",
        ],
        packages = find_packages(),
        entry_points={
                "console_scripts": [
                        "dockerbuild = dockerbuild.cli:main"
                ]
        },
        author = "Jens John",
        author_email = "dev@2ion.de",
        description = "Docker-based staged builds of Debian packages",
        license = "GPL3",
        url = "https://github.com/2ion/dockerbuild",
        include_package_data=True,
)


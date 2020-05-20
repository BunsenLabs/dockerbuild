dockerbuild is a tool for fast and staged Debian package builds. It replaces
[pbuilder](https://pbuilder-team.pages.debian.net/pbuilder/) by building on the
official Debian images on hub.docker.com, removing debootstrap from the equation
and reducing the number of dependencies required on the build system to just
dockerd and Python. dockerbuild can be used on any Linux distribution that
provides these dependencies.

Effectively, dockerbuild provides a framework for Debian package builds
including cross-compilation to any supported Debian port architecture.

## Motivation

The original motivation was to replace pbuilder because of broken
cross-compilation to ARM architectures under Debian 10.

## Features

The tool is still a work in progress. Please refer to the --help output for the
preliminary semantics of the command line interface.

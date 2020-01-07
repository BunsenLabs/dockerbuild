#!/usr/bin/env bash

SCRIPTDIR=$(readlink -f "$(dirname "$0")")

source "$SCRIPTDIR"/common.sh

xinstall devscripts git

yes | mk-build-deps -i "$PKGDIR"/debian/control
rm -- *build-deps*

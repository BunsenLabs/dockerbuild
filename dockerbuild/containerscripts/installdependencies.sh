#!/usr/bin/env bash

readonly SCRIPTDIR=$(readlink -f "$(dirname "$0")")

# shellcheck source=./common.sh
source "$SCRIPTDIR"/common.sh

xinstall devscripts git

yes | mk-build-deps -i "$PKGDIR"/debian/control
rm -- *build-deps*

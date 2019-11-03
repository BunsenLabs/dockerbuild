#!/usr/bin/env bash

SCRIPTDIR=$(readlink -f "$(dirname "$0")")
source "$SCRIPTDIR"/common.sh

mkdir -p /tmp/build
cp -r -- /mnt/package /tmp/build
cd /tmp/build/package

xgitclean

arch=$(xarch)
lastref=$(xupstreamversion)
gitbranch=$(xcurrentbranch)
pkgbase=$(grep ^Source: debian/control|cut -d" " -f2)

git archive --format=tgz "$gitbranch" > ../"${pkgbase}_${lastref}.orig.tar.gz"
dpkg-buildpackage -F -rfakeroot -us -uc

mkdir -p "$OUTDIR/$arch"
cp -- /tmp/build/*.{deb,dsc,tar.*,changes} "$OUTDIR/$arch"

exit 0

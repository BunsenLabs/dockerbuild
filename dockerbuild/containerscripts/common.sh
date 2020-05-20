#!/usr/bin/env bash

set -x
set -e

export PKGDIR=/mnt/package
export OUTDIR=/mnt/output
export DEBIAN_FRONTEND=noninteractive

source /etc/os-release

xgitclean () {
  git clean -d -f
}

xarch () {
  dpkg --print-architecture
}

xupstreamversion () {
  local lastref=$(git describe --tags --abbrev=0)
  lastref=${lastref%-*}
  echo "$lastref"
}

xcurrentbranch () {
  git rev-parse --abbrev-ref HEAD
  return $?
}

xcleanup () {
  rm -f -- /etc/apt/sources.list.d/sources.list
  apt-get clean
  return $?
}

xinstall () {
  apt-get install -y "$@"
  return $?
}

xinit () {
  trap xcleanup EXIT
  if (( $VERSION_ID <= 8 )); then
    VERSION_CODENAME=$(<<<"$VERSION" tr -dc '[a-z]')
    cat >/etc/apt/sources.list.d/sources.list <<<"
deb-src http://archive.debian.org/debian/ ${VERSION_CODENAME} main contrib non-free";
  else
    cat >/etc/apt/sources.list.d/sources.list <<<"
deb-src http://deb.debian.org/debian/ ${VERSION_CODENAME} main contrib non-free
deb-src http://security.debian.org/ ${VERSION_CODENAME}/updates main contrib non-free";
  fi
  # Prevent automatic building of man pages
  echo "man-db man-db/auto-update boolean false" | debconf-set-selections
  # Speed up dpkg. When running containers in parallel on our build machine,
  # this delivers a huge speed up because the available disk I/O bandwidth is so
  # low.
  echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02speedup
  apt-get update && apt-get upgrade -y
  return $?
}

xinit

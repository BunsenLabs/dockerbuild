#!/usr/bin/env bash

set -x
set -e

export PKGDIR=/mnt/package
export OUTDIR=/mnt/output
export DEBIAN_FRONTEND=noninteractive

source /etc/os-release

xdie () {
  local msg=$1
  printf "ERROR: %s\nABORT.\n" "$msg"
  exit 2
}

xgitclean () {
  git clean -d -f
}

xarch () {
  dpkg --print-architecture
}

xupstreamversion () {
  local lastref
  lastref=$(git describe --tags --abbrev=0)
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
  if [[ $source_is_backport = YES ]]; then
    apt-get install -t "${VERSION_CODENAME}-backports" --no-install-recommends -y "$@"
  else
    apt-get install -y --no-install-recommends "$@"
  fi
  return $?
}

xupgrade() {
  if [[ $source_is_backport = YES ]]; then
    apt-get upgrade -t "${VERSION_CODENAME}-backports" -y
  else
    apt-get upgrade -y
  fi
  return $?
}

xinit () {
  trap xcleanup EXIT
  echo "=================================================="
  echo " ENVIRONMENT"
  echo "=================================================="
  env
  echo "=================================================="
  if (( VERSION_ID <= 8 )); then
    VERSION_CODENAME=$(<<<"$VERSION" tr -dc 'a-z')
    cat >/etc/apt/sources.list.d/sources.list <<<"
deb-src http://archive.debian.org/debian/ ${VERSION_CODENAME} main contrib non-free";
  else
    cat >/etc/apt/sources.list.d/sources.list <<<"
deb-src http://deb.debian.org/debian/ ${VERSION_CODENAME} main contrib non-free
deb-src http://security.debian.org/ ${VERSION_CODENAME}/updates main contrib non-free";
  fi
  if [[ $VERSION_ID -gt 10 && $source_is_backport = "YES" ]]; then
    cat >>/etc/apt/sources.list.d/backports.list <<<"
deb http://deb.debian.org/debian ${VERSION_CODENAME}-backports main
deb-src http://deb.debian.org/debian ${VERSION_CODENAME}-backports main";
  fi
  # Prevent automatic building of man pages
  echo "man-db man-db/auto-update boolean false" | debconf-set-selections
  # Speed up dpkg. When running containers in parallel on our build machine,
  # this delivers a huge speed up because the available disk I/O bandwidth is so
  # low.
  echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02speedup
  apt-get update && xupgrade
  return $?
}

xinit

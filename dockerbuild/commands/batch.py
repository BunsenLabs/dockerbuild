#!/usr/bin/env python3

from argparse import Namespace
from dataclasses import dataclass
from functools import cmp_to_key
from pathlib import Path
from tarfile import TarFile
from tempfile import TemporaryDirectory
from typing import List, Optional
import fnmatch
import logging
import os
import re
import shutil

from debian.debian_support import Version, version_compare
from github import Github
import requests

from dockerbuild.download_agent import DownloadAgent

logger = logging.getLogger(__name__)

@dataclass
class Buildjob:
    project: str
    tag: str
    architectures: List[str]
    version: Optional[Version] = None
    tarball_url: Optional[str] = None

    def resolve(self, github: Github) -> 'Buildjob':
        repo = github.get_repo(self.project)
        tags = repo.get_tags()
        if tags.totalCount == 0:
            raise ValueError(f'<{self.project}> has no tags')
        versions = { Version(t.name) : t.tarball_url for t in tags }
        sorted_versions = sorted(versions.keys(), key=cmp_to_key(version_compare), reverse=True)
        latest_version = sorted_versions[0]
        if self.tag == '?':
            self.tag = str(latest_version)
            self.tarball_url = latest_version.tarball_url
            self.version = latest_version
        else:
            regex = re.compile(fnmatch.translate(self.tag))
            for v in sorted_versions:
                _v = str(v)
                if regex.match(_v):
                    self.tag = _v
                    self.tarball_url = versions[v]
                    self.version = v
        if self.tarball_url is None:
            raise KeyError(f'could not resolve or validate tag for project: {self.project}:{self.tag}')
        return self

    @property
    def name(self) -> str:
        return self.project.split('/')[-1]

def namespace(**kwargs) -> Namespace:
    ns = Namespace()
    for k,v in kwargs.values():
        setattr(ns, k, v)
    return ns

def checktar(tarball: TarFile) -> None:
    """ Check if the specified, untrusted tarball is safe to extract. """
    blacklist = [ '/', '..' ]
    for m in tarball.getmembers():
        assert not (m.name[0] in blacklist)

def getenv(ns: Namespace, *args) -> Namespace:
    for env in args:
        v = os.getenv(env, None)
        if v is None:
            raise ValueError(f'Missing environment variable: {env}')
        setattr(ns, env, v)
    return ns

def download_and_extract_tarball(tarball_url: str, output_path: Path, uid: int, gid: int):
    """ Must be offloaded to a worker process. Pridrops for downloading and
    extracting tarballs. """
    if os.getegid() != gid:
        if os.setgid(gid) != 0:
            raise OSError(f"Failed to set GID: {gid}")
    if os.geteuid() != uid:
        if os.setuid(uid) != 0:
            raise OSError("Failed to set UID: {uid}")

def batch(opts: Namespace) -> int:
    agent = DownloadAgent(opts)
    opts = getenv(opts, 'GITHUB_API_TOKEN')
    github = Github(opts.GITHUB_API_TOKEN)
    buildjobs = []

    logger.info('Parsing project list...')
    # <project>:<tag>:<architectures>
    for p in opts.project_list:
        delim = p.count(':')
        if delim == 2:
            project, tag, architectures = p.split(':', 2)
            architectures = architectures.split(',')
        elif delim == 1:
            project, tag = p.split(':', 1)
            architectures = ['amd64']
        else:
            project = p
            tag = '?'
            architectures = ['amd64']
        buildjobs.append(Buildjob(
            project=project,
            tag=tag, architectures=architectures).resolve(github))

    logger.info('Downloading tarballs...')
    local_jobs = {}
    for job in buildjobs:
        output_filename = f'{job.name}_{job.version.upstream_version}.tar.gz'
        output_path = opts.output_dir / output_filename
        assert agent.download(job.tarball_url, output_path), "Download failed: {} to {}".format(job.tarball_url, output_path)
        local_jobs[job] = output_path

    logger.info('Building projects...')
    for job, tarball_path in local_jobs.items():
        logger.info('Building job %s from tarball %s', job.project, tarball_path)
        with TemporaryDirectory() as DIR:
            logger.debug('Temporary directory is: %s', DIR.name)
            with TarFile(tarball_path) as TAR:
                checktar(TAR)
                TAR.extractall(path=DIR)

    return 0

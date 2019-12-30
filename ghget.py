#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from debian.debian_support import Version, version_compare
from dockerbuild.build import build
from functools import cmp_to_key
from github import Github
from pathlib import Path
from tarfile import TarFile
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional
import os
import requests
import shutil
import sys

@dataclass
class Buildjob:
    project: str
    tag: str
    architectures: List[str]
    tarball_url: str = field(default_factory=str)

    def resolve(self, github: Github) -> object:
        repo = github.get_repo(self.project)
        tags = repo.get_tags()
        if tags.totalCount == 0:
            raise ValueError(f'<{self.project}> has no tags')
        if self.tag == '?':
            versions = sorted(map(lambda t: Version(t.name), tags), key=cmp_to_key(version_compare))
            self.tag = latest = str(versions[-1])
            self.tarball_url = list(filter(lambda t: t.name == latest, tags))[0].tarball_url
            return self
        else:
            for t in tags:
                if self.tag == t.name:
                    self.tarball_url = t.tarball_url
            return self
        raise KeyError(f'could not resolve or validate tag for project: {self.project}:{self.tag}')

def namespace(**kwargs) -> Namespace:
    ns = Namespace()
    for k,v in kwargs.values():
        setattr(ns, k, v)
    return ns

def checktar(tarball: TarFile) -> None:
    blacklist = [ '/', '..' ]
    for m in tarball.getmembers():
        assert not (m.name[0] in blacklist)

def getopts() -> Namespace:
    ap = ArgumentParser()
    ap.add_argument("-o", "--output-dir", type=Path, default=Path(os.getcwd()))
    ap.add_argument("-b", "--build-dir", type=Path, default=Path(os.getcwd()))
    ap.add_argument("project_list", nargs='+', default=[])
    return ap.parse_args()

def getenv(ns: Namespace, *args) -> Namespace:
    for env in args:
        v = os.getenv(env, None)
        if v is None:
            raise ValueError(f'Missing environment variable: {env}')
        setattr(ns, env, v)
    return ns

def main() -> int:
    opts = getopts()
    opts = getenv(opts, 'GITHUB_API_TOKEN')
    github = Github(opts.GITHUB_API_TOKEN)
    projects = []

    print('Parsing project list...')
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
        projects.append(Buildjob(project=project,
            tag=tag, architectures=architectures).resolve(github))


    print('Downloading tarballs...')
    local_jobs = {}
    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=4))
    for project, tarball_url in projects.items():
        project_repo = project.split('/', 1)[-1]
        version_part = tarball_url.split('/')[-1]
        output_filename = f'{project_repo}_{version_part}.tgz'
        output_path = opts.output_dir / output_filename
        with open(output_path, 'wb') as FILE:
            req = session.get(tarball_url, stream=True)
            req.raw.decode_content = True # gunzip
            shutil.copyfileobj(req.raw, FILE)
        print(f'DOWNLOAD OK: {project} => {output_path}')
        local_jobs[project] = output_path


    print('Building projects...')
    for project, tarball_path in local_jobs.items():
        with TemporaryDirectory() as DIR:
            with TarFile(tarball_path) as TAR:
                checktar(TAR)
                TAR.extractall(path=DIR)

    return 0

if __name__ == "__main__":
    sys.exit(main())

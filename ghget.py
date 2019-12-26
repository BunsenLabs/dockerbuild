#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace
from debian.debian_support import Version, version_compare
from dockerbuild.build import build
from functools import cmp_to_key
from github import Github
from pathlib import Path
from typing import Dict, List, Optional
import os
import requests
import semver
import shlex
import shutil
import sys

def namespace(**kwargs) -> Namespace:
    ns = Namespace()
    for k,v in kwargs.values():
        setattr(ns, k, v)
    return ns

def getopts() -> Namespace:
    ap = ArgumentParser()
    ap.add_argument("-o", "--output-dir", type=Path, default=Path(os.getcwd()))
    ap.add_argument("project_list", nargs='+', default=[])
    return ap.parse_args()

def getenv(ns: Namespace, *args) -> Namespace:
    for env in args:
        v = os.getenv(env, None)
        if v is None:
            raise ValueError(f'Missing environment variable: {env}')
        setattr(ns, env, v)
    return ns

def resolve_project_tags(github: Github, projects: Dict[str,str]) -> Dict[str,str]:
    def validate_tag(project: str, tag: str) -> Optional[str]:
        repo = github.get_repo(project)
        tags = repo.get_tags()
        if tags.totalCount == 0:
            raise ValueError(f'<{project}> has no tags')
        if tag == '?':
            versions = sorted(map(lambda t: Version(t.name), tags), key=cmp_to_key(version_compare))
            latest = str(versions[-1])
            return list(filter(lambda t: t.name == latest, tags))[0].tarball_url
        else:
            for t in tags:
                if tag == t.name:
                    return t.tarball_url
        raise KeyError(f'could not resolve or validate tag for project: {project}:{tag}')
    return { project: validate_tag(project, tag) for project, tag in projects.items() }

def main() -> int:
    opts = getopts()
    opts = getenv(opts, 'GITHUB_API_TOKEN')
    github = Github(opts.GITHUB_API_TOKEN)
    projects = {}

    print('Parsing project list...')
    for p in opts.project_list:
        if '=' in p:
            project, tag = p.split('=', 1)
        else:
            project = p
            tag = '?'
        projects[project] = tag

    print('Resolving project tags on github.com...')
    projects = resolve_project_tags(github, projects)

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

    return 0

if __name__ == "__main__":
    sys.exit(main())

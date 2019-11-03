from dataclasses import dataclass

@dataclass
class PackageSourceArchive:
    packagename: str
    version: str
    filename: str
    filedata: str

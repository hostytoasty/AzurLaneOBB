import json

from typing import TypedDict, List, Dict
from pathlib import Path
from argparse import ArgumentParser, BooleanOptionalAction
from dataclasses import asdict, dataclass

from lib.utility import ROOT
from lib.classes import HashRow, VersionControl, VersionType
from lib.extractor import extract_xapk
from lib.downloader import Downloader


class BuildVersion(TypedDict):
  version: str
  files: List[str]


@dataclass
class Build:
  server: str
  version: str
  filemap: Dict[str, HashRow]
  vtype: Dict[str, BuildVersion]


  def __init__(self, server: str, version: str) -> None:
    self.server = server
    self.version = version
    self.filemap = {}
    self.vtype = {}


  def save(self) -> None:
    with open('version.json', 'r+', encoding='utf-8') as file:
      try:
        data = json.load(file)
      except json.JSONDecodeError:
        data = {}

      data[self.server] = self.version
      file.seek(0)
      json.dump(data, file, indent=2)
      file.truncate()

    with open(f"{self.server}.json", 'w', encoding='utf-8') as file:
      json.dump(asdict(self), file, indent=2)


# still on prototype that heavily designed on EN server only
def main(direct: bool = False, build_only: bool = False):
  downloader = Downloader(execute=False)
  package = downloader.get_package()
  path = Path(ROOT, 'EN')

  if not build_only:
    xapk = downloader.download(package=package)
    path = extract_xapk(source=xapk, direct=direct)

  vctrl = VersionControl(client=path)
  build = Build(server='EN', version=package['version'])

  for version_type in VersionType:
    filemap = {}

    for hashrow in vctrl.get_hashes(version_type=version_type):
      filemap[hashrow.filepath] = asdict(hashrow)

    build.filemap.update(filemap)
    build.vtype[version_type.name] = BuildVersion(
      version=vctrl.get_version(version_type=version_type),
      files=list(filemap.keys())
    )

  build.save()


if __name__ == '__main__':
  parser = ArgumentParser(
    description='Download and extract latest Azur Lane Obb data.')
  parser.add_argument('--direct', type=bool, default=False, action=BooleanOptionalAction,
    help='Direct extract obb from xapk without extracting xapk.')
  parser.add_argument('--build-only', type=bool, default=False, action=BooleanOptionalAction,
    help='[DEBUG] Only building json file using local file without extract or download.')
  args = parser.parse_args()

  main(direct=args.direct, build_only=args.build_only)

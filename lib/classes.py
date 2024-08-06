from enum import Enum
from pathlib import Path
from typing import Generator, List, TypedDict
from dataclasses import dataclass


class Package(TypedDict):
  version: str
  download: str


# modified from nobbyfix repo
class VersionType(Enum):
  suffix: str
  """Suffix used on version and hash files."""

  AZL      = (1, "")
  CV       = (2, "cv")
  L2D      = (3, "live2d")
  PIC      = (4, "pic")
  BGM      = (5, "bgm")
  CIPHER   = (6, "cipher")
  MANGA    = (7, "manga")
  PAINTING = (8, "painting")
  DORM     = (9, "dorm")


  def __init__(self, _, suffix) -> None:
    # add attributes to enum objects
    self.suffix = suffix

  def __str__(self) -> str:
    return self.name

  @property
  def version_filename(self) -> str:
    """
    Full version filename using the suffix.
    """
    suffix = self.suffix
    if suffix: suffix = "-" + suffix
    return f"version{suffix}.txt"

  @property
  def hashes_filename(self) -> str:
    """
    Full hashes filename using the suffix.
    """
    suffix = self.suffix
    if suffix: suffix = "-" + suffix
    return f"hashes{suffix}.csv"


@dataclass
class HashRow:
  filepath: str
  size: int
  md5hash: str


class VersionControl:
  client: Path

  def __init__(self, client: Path) -> None:
    self.client = client


  def get_version(self, version_type: VersionType) -> str:
    filepath = Path(self.client, version_type.version_filename)

    if not filepath.exists():
      raise FileNotFoundError(f"ERROR: {filepath.as_posix()} not exists.")

    with open(filepath, 'r', encoding='utf-8') as file:
      return file.read()


  def get_hashes(self, version_type: VersionType) -> Generator[HashRow, None, None]:
    filepath = Path(self.client, version_type.hashes_filename)

    if not filepath.exists():
      raise FileNotFoundError(f"ERROR: {filepath.as_posix()} not exists.")

    with open(filepath, 'r', encoding='utf-8') as file:
      return self._parse_hashrows(hashes=file.read())


  @staticmethod
  def _iterate_hash_lines(hashes: str) -> Generator[List[str], None, None]:
    for asset in hashes.splitlines():
      if asset == '': continue
      yield asset.split(',')


  @staticmethod
  def _parse_hashrows(hashes: str) -> Generator[HashRow, None, None]:
    for path, size, md5hash in VersionControl._iterate_hash_lines(hashes):
      yield HashRow(path, int(size), md5hash)


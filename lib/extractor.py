import io
import json
import shutil

from tqdm import tqdm
from zipfile import ZipFile
from pathlib import Path

from lib.utility import BUFSIZE, ROOT


def unpack_obb(zipfile: ZipFile, target: Path) -> None:
  zfiles = [x for x in zipfile.infolist() if not x.is_dir()]
  length = len(zfiles)
  digits = len(str(length))

  print(f"Unpacking {length} files")

  for index, file in enumerate(zfiles, start=1):
    dest = Path(target, Path(file.filename).relative_to('assets'))
    dest.parent.mkdir(parents=True, exist_ok=True)

    # remove .ys suffix
    if dest.suffix == '.ys':
      dest = dest.with_suffix('')

    print(f"({index:0{digits}}/{length}): {dest.relative_to(ROOT)}")

    with zipfile.open(file, 'r') as zf, open(dest, 'wb') as f:
      shutil.copyfileobj(zf, f)


def extract_xapk(source: Path, direct: bool = True) -> Path:
  target = Path(ROOT, 'EN')
  expath = []

  if target.exists():
    print('Removing old obb data')
    shutil.rmtree(target)

  with ZipFile(source, 'r') as xapk:
    print('Reading manifest')
    with xapk.open('manifest.json', 'r') as manifestfile:
      manifest = json.loads(manifestfile.read().decode('utf-8'))

    for expansions in manifest['expansions']:
      with xapk.open(expansions['file'], 'r') as zf:
        # reduce memory usage if not direct extraction
        if not direct:
          obb_path = Path(ROOT, Path(expansions['file']).name)

          if obb_path.exists():
            obb_path.unlink()

          obb_size = xapk.getinfo(expansions['file']).file_size

          print('Extracting obb')
          # zf.extract not efficient at all it's load entire object and gonna cost tons of memory
          with tqdm.wrapattr(open(obb_path, 'wb'), 'write', miniters=1, total=obb_size) as f:
            while buf := zf.read(BUFSIZE):
              f.write(buf)

          expath.append(obb_path)
          continue

        print('Loading obb into memory')
        obb_bytes = io.BytesIO(zf.read())

        print('Unpacking obb')
        with ZipFile(obb_bytes, 'r') as obb:
          unpack_obb(obb, target)

  if not direct:
    for obb_path in expath:
      print('Unpacking obb')
      with ZipFile(obb_path, 'r') as obb:
        unpack_obb(obb, target)

      print(f"Removing {obb_path}")
      obb_path.unlink()

  print('Task completed')
  return target

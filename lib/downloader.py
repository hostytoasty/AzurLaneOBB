import cloudscraper

from bs4 import BeautifulSoup, Tag
from tqdm import tqdm
from pathlib import Path

from lib.utility import ROOT, BUFSIZE
from lib.classes import Package


class Downloader:
  api_url = 'https://apkpure.com/azur-lane-apk/com.YoStarEN.AzurLane'

  def __init__(self, execute: bool = True) -> None:
    self.scraper = cloudscraper.create_scraper()
    response = self.scraper.get(url=self.api_url)

    if response.status_code != 200:
      raise ValueError(f"ERROR: failed to load {self.api_url} ({response.status_code})")

    self.page = BeautifulSoup(response.text, 'html.parser')

    if execute:
      self.download(self.get_package())


  def get_package(self) -> Package:
    detail = self.page.find('div', class_='detail_banner')

    if not isinstance(detail, Tag):
      raise ValueError('ERROR: expected type for detail is Tag')

    sdk = detail.find('p', class_='details_sdk')

    if not isinstance(sdk, Tag):
      raise ValueError('ERROR: expected type for sdk is Tag')

    version = sdk.contents[1].get_text(strip=True)
    apkdata = detail.find('a', class_='download_apk_news')

    if not isinstance(apkdata, Tag):
      raise ValueError('ERROR: expected type for apkdata is Tag')

    package_name = apkdata.get('data-dt-package_name') or 'com.YoStarEN.AzurLane'
    version_code = apkdata.get('data-dt-version_code') or ''
    download = f"https://d.apkpure.com/b/XAPK/{package_name}?versionCode={version_code}"

    return Package(version=version, download=download)


  def download(self, package: Package, dest: Path = ROOT) -> Path:
    response = self.scraper.get(url=package['download'], stream=True, allow_redirects=True)

    if not response:
      raise ValueError(f"ERROR: no response for {package['download']}")

    length = int(response.headers.get('content-length') or 0)
    filename = f"AzurLane-{package['version']}.xapk"
    filepath = Path(dest, filename)
    print(f"Downloading: {filename} ({length})")

    with tqdm.wrapattr(open(filepath, 'wb'), 'write', miniters=1, total=length) as file:
      for chunk in response.iter_content(chunk_size=BUFSIZE):
        if chunk: file.write(chunk)

    print(f"Downloaded: {filepath}")
    return filepath          


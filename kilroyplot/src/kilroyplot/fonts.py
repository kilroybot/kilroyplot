import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.request import urlopen

from appdirs import user_cache_dir
from cachetools import cached

from kilroyplot.cache import DiskTTLCache
from kilroyplot.utils import list_files

ASSETS_SEARCH_URL = "https://api.github.com/repos/kilroybot/assets/git/trees/main?recursive=1"
ENCODING = "utf-8"
FORMAT = ".ttf"
CACHE_DIR = Path(user_cache_dir("kilroy"))
ASSETS_CACHE_DIR = CACHE_DIR / "assets"
FONT_CACHE_DIR = CACHE_DIR / "fonts"


@dataclass
class AssetData:
    path: str
    mode: str
    type: str
    sha: str
    url: str
    size: Optional[int] = None

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def basename(self) -> str:
        return Path(self.path).stem


@dataclass
class FileData:
    path: str
    sha: str

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def basename(self) -> str:
        return Path(self.path).stem


@dataclass
class BlobData:
    sha: str
    node_id: str
    size: int
    url: str
    content: str
    encoding: str


def get_response(
        url: str,
        encoding: str = ENCODING
) -> Dict[str, Any]:
    with urlopen(url) as url:
        return json.loads(url.read().decode(encoding=encoding))


@cached(DiskTTLCache(ASSETS_CACHE_DIR))
def search_assets(search_url: str = ASSETS_SEARCH_URL) -> Dict[str, Any]:
    return get_response(search_url)


def get_assets_data(
        *args,
        **kwargs
) -> List[AssetData]:
    data = search_assets(*args, *kwargs)
    return [AssetData(**asset) for asset in data["tree"]]


def get_available_fonts(
        *args,
        format: str = FORMAT,
        **kwargs
) -> List[AssetData]:
    assets = get_assets_data(*args, **kwargs)
    return [
        asset
        for asset in assets
        if asset.path.startswith("fonts/") and asset.path.endswith(format)
    ]


def github_sha_base(contents: bytes) -> bytes:
    return f"blob {len(contents)}\0".encode('utf-8') + contents


def sha256_file(
        path: Union[str, Path]
) -> str:
    with open(path, 'rb') as file:
        contents = file.read()
    return hashlib.sha1(github_sha_base(contents)).hexdigest()


def get_cached_files(
        cache_dir: Union[str, Path]
) -> List[FileData]:
    return [
        FileData(
            path=str(file),
            sha=sha256_file(file)
        )
        for file in list_files(cache_dir)
    ]


def get_blob(url: str) -> BlobData:
    return BlobData(**get_response(url))


def download_blob(
        url: str,
        to: Union[str, Path]
) -> str:
    blob = get_blob(url)
    content = base64.b64decode(blob.content)
    with open(to, 'wb') as file:
        file.write(content)
    return to


def download_fonts(
        *args,
        cache_dir: Union[str, Path] = FONT_CACHE_DIR,
        **kwargs
) -> List[str]:
    cache_dir = Path(str(cache_dir))
    cache_dir.mkdir(parents=True, exist_ok=True)
    fonts = get_available_fonts(*args, **kwargs)
    cached_fonts = get_cached_files(cache_dir)
    cached_shas = set(font.sha for font in cached_fonts)
    new_fonts = [font for font in fonts if font.sha not in cached_shas]
    new_fonts = [
        FileData(
            path=download_blob(font.url, cache_dir / font.filename),
            sha=font.sha
        )
        for font in new_fonts
    ]
    return [font.path for font in cached_fonts + new_fonts]


paths = download_fonts()

import time
from pathlib import Path

import pytest

from kilroyplot.cache import DiskTTLCache
from kilroyplot.utils import list_files


class TestDiskTTLCache:
    def test_cached_value(self, tmp_path: Path) -> None:
        cache = DiskTTLCache(tmp_path)
        cache["foo"] = "bar"
        assert cache["foo"] == "bar"

    def test_files_created(self, tmp_path: Path) -> None:
        assert len(list_files(tmp_path)) == 0
        cache = DiskTTLCache(tmp_path)
        cache["foo"] = "bar"
        assert len(list_files(tmp_path)) == 2

    def test_expired(self, tmp_path: Path) -> None:
        ttl = 1
        cache = DiskTTLCache(tmp_path, ttl=ttl)
        cache["foo"] = "bar"
        time.sleep(ttl + 1)
        with pytest.raises(KeyError):
            _ = cache["foo"]

    def test_length(self, tmp_path: Path) -> None:
        cache = DiskTTLCache(tmp_path)
        cache["foo"] = "bar"
        assert len(cache) == 1

    def test_delete(self, tmp_path: Path) -> None:
        cache = DiskTTLCache(tmp_path)
        cache["foo"] = "bar"
        del cache["foo"]
        assert len(cache) == 0

    def test_iter(self, tmp_path: Path) -> None:
        cache = DiskTTLCache(tmp_path)
        cache["foo"] = "bar"
        assert list(cache) == ["foo"]

    def test_metadata_suffix(self, tmp_path: Path) -> None:
        suffix = ".foo.json"
        cache = DiskTTLCache(tmp_path, metadata_suffix=suffix)
        cache["foo"] = "bar"
        assert any(
            file for file in list_files(tmp_path) if file.name.endswith(suffix)
        )

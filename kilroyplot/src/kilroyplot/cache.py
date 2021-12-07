import datetime
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import (
    Hashable,
    Iterator,
    MutableMapping,
    Set,
    TypeVar,
    Union
)

from appdirs import user_cache_dir

from kilroyplot.utils import deserialize, digest_args, iter_files, serialize

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class DiskTTLCache(MutableMapping[K, V]):
    DEFAULT_CACHE_DIR = CACHE_DIR = Path(user_cache_dir("kilroy"))
    DEFAULT_TTL = 86400
    DEFAULT_METADATA_SUFFIX = ".metadata.json"

    @dataclass
    class Metadata:
        save_time: str
        serialized_key: str

    def __init__(
            self,
            cache_dir: Union[str, Path] = DEFAULT_CACHE_DIR,
            ttl: int = DEFAULT_TTL,
            metadata_suffix: str = DEFAULT_METADATA_SUFFIX
    ) -> None:
        super().__init__()
        self._cache_dir = Path(str(cache_dir))
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl
        self._metadata_suffix = metadata_suffix

    def _time_to_str(self, time: datetime.datetime) -> str:
        return time.isoformat()

    def _str_to_time(self, x: str) -> datetime.datetime:
        return datetime.datetime.fromisoformat(x)

    def _key_to_str(self, k: K) -> str:
        return serialize(k).decode("utf-8", errors="replace")

    def _str_to_key(self, x: str) -> K:
        return deserialize(x.encode("utf-8", errors="replace"))

    def _key_to_digest(self, key: K) -> str:
        return digest_args(key)

    def _digest_to_key(self, digest: str) -> K:
        metadata = self._read_metadata(digest)
        return self._str_to_key(metadata.serialized_key)

    def _digest_to_dumpfile_name(self, digest: str) -> str:
        return digest

    def _dumpfile_name_to_digest(self, name: str) -> str:
        return name

    def _digest_to_metadata_name(self, digest: str) -> str:
        return f"{digest}{self._metadata_suffix}"

    def _metadata_name_to_digest(self, name: str) -> str:
        return name.removesuffix(self._metadata_suffix)

    def _is_metadata(self, name: str) -> bool:
        return name.endswith(self._metadata_suffix)

    def _saved_digests(self) -> Set[str]:
        return set(
            self._metadata_name_to_digest(file.name)
            for file in iter_files(self._cache_dir)
            if self._is_metadata(file.name)
        )

    def _full_path(self, name: str) -> Path:
        return self._cache_dir / name

    def _save_metadata(self, digest: str, metadata: Metadata) -> None:
        metadata_path = self._full_path(self._digest_to_metadata_name(digest))
        metadata_path.write_text(json.dumps(asdict(metadata)))

    def _read_metadata(self, digest: str) -> Metadata:
        metadata_path = self._full_path(self._digest_to_metadata_name(digest))
        return self.Metadata(**json.loads(metadata_path.read_bytes()))

    def _save_value(self, digest: str, value: V) -> None:
        dumpfile_path = self._full_path(self._digest_to_dumpfile_name(digest))
        dumpfile_path.write_bytes(serialize(value))

    def _read_value(self, digest: str) -> V:
        dumpfile_path = self._full_path(self._digest_to_dumpfile_name(digest))
        return deserialize(dumpfile_path.read_bytes())

    def _is_expired(self, digest: str) -> bool:
        metadata = self._read_metadata(digest)
        save_time = self._str_to_time(metadata.save_time)
        time_diff = datetime.datetime.utcnow() - save_time
        return time_diff.total_seconds() > self._ttl

    def __setitem__(self, key: K, value: V) -> None:
        digest = self._key_to_digest(key)
        metadata = self.Metadata(
            save_time=self._time_to_str(datetime.datetime.utcnow()),
            serialized_key=self._key_to_str(key)
        )
        self._save_value(digest, value)
        self._save_metadata(digest, metadata)

    def __delitem__(self, key: K) -> None:
        digest = self._key_to_digest(key)
        if digest not in self._saved_digests():
            raise KeyError
        dumpfile_name = self._digest_to_dumpfile_name(digest)
        metadata_name = self._digest_to_metadata_name(digest)
        self._full_path(dumpfile_name).unlink(missing_ok=True)
        self._full_path(metadata_name).unlink(missing_ok=True)

    def __getitem__(self, key: K) -> V:
        digest = self._key_to_digest(key)
        if digest not in self._saved_digests():
            raise KeyError
        try:
            if self._is_expired(digest):
                self.__delitem__(key)
                raise KeyError
            return self._read_value(digest)
        except FileNotFoundError as e:
            raise KeyError from e

    def __len__(self) -> int:
        return len(self._saved_digests())

    def __iter__(self) -> Iterator[K]:
        for digest in self._saved_digests():
            yield self._digest_to_key(digest)

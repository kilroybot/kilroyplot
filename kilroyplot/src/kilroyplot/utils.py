import hashlib
from pathlib import Path
from typing import Iterator, List, Union

import dill


def pathify(path: Union[str, Path]) -> Path:
    """Turns string or pathlib.Path into pathlib.Path."""
    return Path(str(path))


def iter_files(directory: Union[str, Path]) -> Iterator[Path]:
    return (p for p in Path(str(directory)).iterdir() if p.is_file())


def list_files(directory: Union[str, Path]) -> List[Path]:
    return list(iter_files(directory))


def serialize(obj) -> bytes:
    return dill.dumps(obj)


def deserialize(b: bytes):
    return dill.loads(b)


def digest_bytes(x: bytes) -> str:
    return hashlib.md5(x).hexdigest()


def digest_args(*args, **kwargs) -> str:
    args = (args, frozenset(kwargs.items()))
    return digest_bytes(serialize(args))

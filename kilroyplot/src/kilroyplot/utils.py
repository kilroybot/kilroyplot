import hashlib
from pathlib import Path
from typing import Iterator, List, Union

import dill


def pathify(path: Union[str, Path]) -> Path:
    """Turns string or pathlib.Path into pathlib.Path."""
    return Path(str(path))


def iter_files(directory: Union[str, Path]) -> Iterator[Path]:
    """Iterates over all files inside directory."""
    return (p for p in pathify(directory).iterdir() if p.is_file())


def list_files(directory: Union[str, Path]) -> List[Path]:
    """Returns a list with all files inside directory."""
    return list(iter_files(directory))


def serialize(obj) -> bytes:
    """Turns any object into bytes (if possible)."""
    return dill.dumps(obj)


def deserialize(b: bytes):
    """Turns serialized bytes into an object (if possible)."""
    return dill.loads(b)


def digest_bytes(x: bytes) -> str:
    """Returns hex digest of bytes."""
    return hashlib.md5(x).hexdigest()


def digest_args(*args, **kwargs) -> str:
    """Returns hex digest of any arguments."""
    args = (args, frozenset(kwargs.items()))
    return digest_bytes(serialize(args))

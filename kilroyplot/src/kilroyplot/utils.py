from pathlib import Path
from typing import Iterator, List, Union


def pathify(path: Union[str, Path]) -> Path:
    """Turns string or pathlib.Path into pathlib.Path."""
    return Path(str(path))


def iter_files(directory: Union[str, Path]) -> Iterator[Path]:
    """Iterates over all files inside directory."""
    return (p for p in pathify(directory).iterdir() if p.is_file())


def list_files(directory: Union[str, Path]) -> List[Path]:
    """Returns a list with all files inside directory."""
    return list(iter_files(directory))

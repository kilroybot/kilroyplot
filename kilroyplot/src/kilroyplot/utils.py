from pathlib import Path
from typing import Iterator, List, Union


def iter_files(directory: Union[str, Path]) -> Iterator[Path]:
    return (p for p in Path(str(directory)).iterdir() if p.is_file())


def list_files(directory: Union[str, Path]) -> List[Path]:
    return list(iter_files(directory))

from pathlib import Path
from typing import Iterator, List

from kilroyplot.utils import iter_files, list_files, pathify


def is_iterator_empty(it: Iterator) -> bool:
    return all(False for _ in it)


class TestPathify:
    def test_return_type_for_string(self) -> None:
        assert isinstance(pathify("."), Path)

    def test_return_type_for_path(self) -> None:
        assert isinstance(pathify(Path(".")), Path)


class TestIterFiles:
    def test_return_type(self, tmp_path: Path) -> None:
        assert isinstance(iter_files(tmp_path), Iterator)

    def test_return_value_for_empty_directory(self, tmp_path: Path) -> None:
        assert is_iterator_empty(iter_files(tmp_path))

    def test_directories_are_not_returned(self, tmp_path: Path) -> None:
        expected_file = tmp_path / "test"
        expected_file.mkdir()
        assert is_iterator_empty(iter_files(tmp_path))

    def test_returns_correct_files(self, tmp_path: Path) -> None:
        expected_file = tmp_path / "test"
        expected_file.touch()
        returned_files = iter_files(tmp_path)
        assert list(returned_files) == [expected_file]


class TestListFiles:
    def test_return_type(self, tmp_path: Path) -> None:
        assert isinstance(list_files(tmp_path), List)

    def test_return_value_for_empty_directory(self, tmp_path: Path) -> None:
        assert not list_files(tmp_path)

    def test_directories_are_not_returned(self, tmp_path: Path) -> None:
        expected_file = tmp_path / "test"
        expected_file.mkdir()
        assert not list_files(tmp_path)

    def test_returns_correct_files(self, tmp_path: Path) -> None:
        expected_file = tmp_path / "test"
        expected_file.touch()
        returned_files = list_files(tmp_path)
        assert returned_files == [expected_file]

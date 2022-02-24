from collections import Counter
from pathlib import Path
from typing import Iterator, List

from kilroyplot.utils import (
    deserialize,
    digest_args,
    digest_bytes,
    iter_files,
    list_files,
    pathify,
    serialize,
)


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


class TestSerialize:
    def test_return_type(self) -> None:
        assert isinstance(serialize(None), bytes)

    def test_works_on_integers(self) -> None:
        assert serialize(1)

    def test_works_on_strings(self) -> None:
        assert serialize("foo")

    def test_works_on_lists(self) -> None:
        assert serialize([1, 2, 3])

    def test_works_on_known_objects(self) -> None:
        assert serialize(Counter())

    def test_works_on_known_functions(self) -> None:
        assert serialize(serialize)


class TestDeserialize:
    def test_works_on_integers(self) -> None:
        assert deserialize(serialize(1)) == 1

    def test_works_on_strings(self) -> None:
        assert deserialize(serialize("foo")) == "foo"

    def test_works_on_lists(self) -> None:
        assert deserialize(serialize([1, 2, 3])) == [1, 2, 3]

    def test_works_on_known_objects(self) -> None:
        foo = Counter()
        assert deserialize(serialize(foo)) == foo

    def test_works_on_known_functions(self) -> None:
        assert deserialize(serialize(serialize)) == serialize


class TestDigestBytes:
    def test_return_type(self) -> None:
        assert isinstance(digest_bytes(b""), str)

    def test_length(self) -> None:
        assert len(digest_bytes(b"")) == 32

    def test_same_value(self) -> None:
        assert digest_bytes(b"") == digest_bytes(b"")

    def test_different_value(self) -> None:
        assert digest_bytes(b"foo") != digest_bytes(b"bar")


class TestDigestArgs:
    def test_return_type(self) -> None:
        assert isinstance(digest_args(), str)

    def test_works_with_positional_arguments(self) -> None:
        assert digest_args(1) == digest_args(1)

    def test_works_with_keyword_arguments(self) -> None:
        assert digest_args(x=1) == digest_args(x=1)

    def test_works_with_mixed_arguments(self) -> None:
        assert digest_args(1, x=1) == digest_args(1, x=1)

    def test_keyword_arguments_order(self) -> None:
        assert digest_args(x=1, y=2) == digest_args(y=2, x=1)

    def test_keyword_and_positional_differ(self) -> None:
        assert digest_args(1) != digest_args(x=1)

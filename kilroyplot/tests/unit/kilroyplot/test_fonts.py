from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError

import pytest
from _pytest.monkeypatch import MonkeyPatch

from kilroyplot import fonts
from kilroyplot.fonts import BlobData


class TestGetFonts:
    mocked_font_filename = "font.ttf"
    mocked_font_encoded_content = ""
    mocked_font_binary_content = b""
    mocked_font_sha = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    mocked_font_url = "http://foo.bar"

    @pytest.fixture
    def mock_search_assets(self, monkeypatch: MonkeyPatch) -> None:
        def mocked(*args, **kwargs) -> Dict[str, Any]:
            return {
                "tree": [
                    {
                        "path": f"fonts/{self.mocked_font_filename}",
                        "mode": "foo",
                        "type": "foo",
                        "sha": self.mocked_font_sha,
                        "url": self.mocked_font_url,
                    }
                ],
                "truncated": False,
            }

        monkeypatch.setattr(fonts, "search_assets", mocked)

    @pytest.fixture
    def mock_search_assets_error(self, monkeypatch: MonkeyPatch) -> None:
        def mocked(*args, **kwargs):
            raise URLError("foo")

        monkeypatch.setattr(fonts, "search_assets", mocked)

    @pytest.fixture
    def mock_get_blob(self, monkeypatch: MonkeyPatch) -> None:
        def mocked(*args, **kwargs) -> BlobData:
            return BlobData(
                sha=self.mocked_font_sha,
                node_id="foo",
                size=0,
                url=self.mocked_font_url,
                content=self.mocked_font_encoded_content,
                encoding="base64",
            )

        monkeypatch.setattr(fonts, "get_blob", mocked)

    @pytest.fixture
    def mock_get_blob_error(self, monkeypatch: MonkeyPatch) -> None:
        def mocked(*args, **kwargs):
            raise URLError("foo")

        monkeypatch.setattr(fonts, "get_blob", mocked)

    @pytest.fixture
    def mock_list_files_error(self, monkeypatch: MonkeyPatch) -> None:
        def mocked(*args, **kwargs):
            raise PermissionError

        monkeypatch.setattr(fonts, "list_files", mocked)

    def test_font_caching(
        self, mock_search_assets, mock_get_blob, tmp_path: Path
    ) -> None:
        result = fonts.get_fonts(cache_dir=tmp_path)
        expected = [str(tmp_path / self.mocked_font_filename)]
        assert result == expected

    def test_warning_on_asset_error(
        self, mock_search_assets_error, mock_get_blob, tmp_path: Path
    ) -> None:
        with pytest.warns(RuntimeWarning):
            fonts.get_fonts(cache_dir=tmp_path)

    def test_warning_on_blob_error(
        self, mock_search_assets, mock_get_blob_error, tmp_path: Path
    ) -> None:
        with pytest.warns(RuntimeWarning):
            fonts.get_fonts(cache_dir=tmp_path)

    def test_warning_on_file_error(
        self,
        mock_search_assets,
        mock_get_blob,
        mock_list_files_error,
        tmp_path: Path,
    ) -> None:
        with pytest.warns(RuntimeWarning):
            fonts.get_fonts(cache_dir=tmp_path)

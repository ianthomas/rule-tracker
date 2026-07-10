"""Fetch caching: existing raw.xml means zero network calls."""

import pytest

from src import config
from src.ingest import fetch as fetch_mod


def test_fetch_skips_download_when_raw_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CORPUS_DIR", tmp_path)

    doc = "2022-23873"
    ddir = tmp_path / doc
    ddir.mkdir()
    (ddir / "raw.xml").write_bytes(b"<RULE/>")

    def explode(*args, **kwargs):  # pragma: no cover
        raise AssertionError("network call attempted despite cached raw.xml")

    monkeypatch.setattr(fetch_mod.requests, "get", explode)

    result = fetch_mod.fetch(doc)
    assert result == ddir / "raw.xml"
    assert result.read_bytes() == b"<RULE/>"


def test_fetch_errors_when_no_xml_url(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CORPUS_DIR", tmp_path)

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"title": "no xml here"}

    monkeypatch.setattr(fetch_mod.requests, "get", lambda *a, **k: FakeResp())
    with pytest.raises(RuntimeError, match="full_text_xml_url"):
        fetch_mod.fetch("2022-23873")

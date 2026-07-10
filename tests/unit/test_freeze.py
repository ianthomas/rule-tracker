"""Freeze guard: frozen artifacts may never be silently rewritten (invariant 1)."""

import pytest

from src.ingest.sections import FrozenArtifactError, write_frozen


def test_first_write_succeeds(tmp_path):
    p = tmp_path / "text.txt"
    assert write_frozen(p, b"hello") is True
    assert p.read_bytes() == b"hello"


def test_identical_rewrite_is_noop(tmp_path):
    p = tmp_path / "text.txt"
    write_frozen(p, b"hello")
    assert write_frozen(p, b"hello") is False


def test_different_rewrite_raises(tmp_path):
    p = tmp_path / "text.txt"
    write_frozen(p, b"hello")
    with pytest.raises(FrozenArtifactError):
        write_frozen(p, b"changed")
    assert p.read_bytes() == b"hello"  # original preserved

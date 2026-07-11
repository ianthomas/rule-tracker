"""Normalization properties: NFC, whitespace collapse, idempotence."""

import unicodedata

from src.ingest.sections import normalize_text


def test_collapses_whitespace_runs():
    assert normalize_text("a  b\t c\n d") == "a b c d"


def test_strips_ends():
    assert normalize_text("  hello  ") == "hello"


def test_nfc_normalization():
    # e + combining acute accent (NFD) -> precomposed é (NFC)
    decomposed = "étude"
    out = normalize_text(decomposed)
    assert out == unicodedata.normalize("NFC", decomposed)
    assert out.startswith("é")


def test_nonbreaking_space_collapsed():
    assert normalize_text("42 U.S.C.") == "42 U.S.C."


def test_idempotent():
    s = "  § 425.20   Definitions.\n\n (c)  * * * "
    once = normalize_text(s)
    assert normalize_text(once) == once


def test_empty():
    assert normalize_text("   \n\t ") == ""

"""Automated integration tests for Phase 0 (run after `make ingest`).

These validate the REAL corpus artifacts — shapes, exit criteria, and
idempotence. They skip (not fail) if the corpus hasn't been ingested, so
`make test` stays green on a fresh clone before `make ingest`.
"""

import hashlib
import json

import pytest

from src import config
from src.ingest.sections import build_sections

DOC_IDS = list(config.DOCS)


def _artifacts(doc_id):
    ddir = config.CORPUS_DIR / doc_id
    text_p = ddir / "text.txt"
    manifest_p = ddir / "sections.json"
    if not (text_p.exists() and manifest_p.exists()):
        pytest.skip(f"corpus not ingested for {doc_id}; run `make ingest` first")
    return (
        text_p.read_text(encoding="utf-8"),
        json.loads(manifest_p.read_text(encoding="utf-8")),
    )


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_artifacts_exist_and_manifest_shape(doc_id):
    text, manifest = _artifacts(doc_id)
    assert manifest["doc_id"] == doc_id
    assert manifest["stage"] == config.DOCS[doc_id].stage
    assert manifest["sections"], "manifest has no sections"
    for e in manifest["sections"]:
        for key in ("section_id", "kind", "heading", "heading_path", "start", "end"):
            assert key in e, f"{doc_id} {e.get('section_id')} missing {key}"
        assert e["kind"] in ("preamble", "regtext")
        assert 0 <= e["start"] < e["end"] <= len(text)


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_text_hash_matches_manifest(doc_id):
    text, manifest = _artifacts(doc_id)
    assert (
        hashlib.sha256(text.encode("utf-8")).hexdigest() == manifest["text_sha256"]
    ), "text.txt does not match the hash recorded at ingestion — frozen artifact violated"


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_at_least_one_part_425_regtext(doc_id):
    """Exit criterion: manifest includes >=1 regtext block touching Part 425."""
    _, manifest = _artifacts(doc_id)
    regtext = [e for e in manifest["sections"] if e["kind"] == "regtext"]
    assert regtext, f"{doc_id}: no regtext sections captured"
    with_refs = [e for e in regtext if e.get("cfr_refs")]
    assert with_refs, f"{doc_id}: no regtext section carries a 425.x reference"


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_offsets_slice_to_heading(doc_id):
    """Exit criterion (smoke): every manifest range slices text.txt to a block
    whose first line equals the recorded heading."""
    text, manifest = _artifacts(doc_id)
    for e in manifest["sections"]:
        first_line = text[e["start"] : e["end"]].splitlines()[0]
        assert first_line == e["heading"], f"{doc_id} {e['section_id']}"


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_ingest_idempotent(doc_id):
    """Exit criterion: re-parsing raw.xml reproduces text.txt byte-identically."""
    text, _ = _artifacts(doc_id)
    raw = config.CORPUS_DIR / doc_id / "raw.xml"
    if not raw.exists():
        pytest.skip(f"raw.xml missing for {doc_id}")
    rebuilt, _ = build_sections(raw)
    assert rebuilt.encode("utf-8") == text.encode("utf-8")


@pytest.mark.parametrize("doc_id", DOC_IDS)
def test_no_xml_debris(doc_id):
    """Normalized text should carry no markup residue."""
    text, _ = _artifacts(doc_id)
    for marker in ("<P>", "</", "&amp;", "&#", "<E ", "<HD"):
        assert marker not in text, f"{doc_id}: XML debris {marker!r} in text.txt"

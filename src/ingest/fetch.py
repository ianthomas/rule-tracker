"""Fetch Federal Register documents: API JSON -> full-text XML.

XML only, never PDF (ADR-001). Downloads are cached: if corpus/{doc}/raw.xml
exists, no network request is made.
"""

import json
from pathlib import Path

import requests

from src import config


def doc_dir(fr_doc_no: str) -> Path:
    return config.CORPUS_DIR / fr_doc_no


def fetch(fr_doc_no: str, force: bool = False) -> Path:
    """Download the full-text XML for one FR document. Returns path to raw.xml.

    Skips the download entirely if raw.xml already exists (unless force=True).
    """
    ddir = doc_dir(fr_doc_no)
    ddir.mkdir(parents=True, exist_ok=True)
    raw_path = ddir / "raw.xml"
    if raw_path.exists() and not force:
        return raw_path

    meta_url = config.FR_API_DOC_URL.format(fr_doc_no=fr_doc_no)
    meta_resp = requests.get(meta_url, timeout=60)
    meta_resp.raise_for_status()
    meta = meta_resp.json()

    xml_url = meta.get("full_text_xml_url")
    if not xml_url:
        raise RuntimeError(f"FR API returned no full_text_xml_url for {fr_doc_no}")

    # Keep the API metadata alongside the raw XML for provenance.
    (ddir / "api.json").write_bytes(
        json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    )

    xml_resp = requests.get(xml_url, timeout=600)
    xml_resp.raise_for_status()
    raw_path.write_bytes(xml_resp.content)
    return raw_path

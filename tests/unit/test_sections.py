"""Section builder on synthetic FR XML fixtures covering BOTH layouts:

- RULE layout: <REGTEXT PART="425"> wrappers (baseline + final docs)
- PRORULE layout: flat PART/AMDPAR/SECTION runs after LSTSUB (proposed doc)
"""

from pathlib import Path

import pytest

from src.ingest.sections import build_sections

RULE_XML = """<RULE>
  <PREAMB><AGENCY>CMS</AGENCY></PREAMB>
  <SUPLINF>
    <HD SOURCE="HED">SUPPLEMENTARY INFORMATION:</HD>
    <HD SOURCE="HD1">I. Executive Summary</HD>
    <P>Intro text not about the program of interest.</P>
    <HD SOURCE="HD2">G. Medicare Shared Savings Program</HD>
    <P>First MSSP   preamble paragraph with  spaces.</P>
    <HD SOURCE="HD3">1. Background on the Shared Savings Program</HD>
    <P>Nested MSSP paragraph.</P>
    <HD SOURCE="HD2">H. Other Payment Topic</HD>
    <P>Out of scope paragraph.</P>
    <HD SOURCE="HD1">VII. Regulatory Impact Analysis</HD>
    <HD SOURCE="HD3">7. Medicare Shared Savings Program</HD>
    <HD SOURCE="HD3">a. General Impacts</HD>
    <P>RIA impact paragraph under a same-level lettered sub-heading.</P>
    <HD SOURCE="HD3">8. Other RIA Topic</HD>
    <P>Peer RIA paragraph, out of scope.</P>
    <REGTEXT TITLE="42" PART="414">
      <AMDPAR>1. Part 414 is amended.</AMDPAR>
    </REGTEXT>
    <REGTEXT TITLE="42" PART="425">
      <AMDPAR>2. Section 425.20 is amended by revising a definition.</AMDPAR>
      <SECTION>
        <SECTNO>&#xA7; 425.20</SECTNO>
        <SUBJECT>Definitions.</SUBJECT>
        <P>ACO participant means an entity identified by a TIN.</P>
      </SECTION>
    </REGTEXT>
  </SUPLINF>
</RULE>
"""

PRORULE_XML = """<PRORULE>
  <PREAMB><AGENCY>CMS</AGENCY></PREAMB>
  <SUPLINF>
    <HD SOURCE="HED">SUPPLEMENTARY INFORMATION:</HD>
    <HD SOURCE="HD2">G. Medicare Shared Savings Program</HD>
    <P>Proposed MSSP preamble paragraph.</P>
    <LSTSUB>List of Subjects 42 CFR Part 425</LSTSUB>
    <PART>PART 414&#8212;OTHER PART</PART>
    <AMDPAR>1. Part 414 amended.</AMDPAR>
    <PART>PART 425&#8212;MEDICARE SHARED SAVINGS PROGRAM</PART>
    <AMDPAR>2. Section 425.110 is amended by revising paragraph (a).</AMDPAR>
    <SECTION>
      <SECTNO>&#xA7; 425.110</SECTNO>
      <SUBJECT>Number of ACO professionals and beneficiaries.</SUBJECT>
      <STARS/>
      <P>(a) The ACO must have at least 5,000 assigned beneficiaries.</P>
    </SECTION>
    <SIG><NAME>Xavier Becerra</NAME></SIG>
  </SUPLINF>
</PRORULE>
"""


@pytest.fixture
def rule_path(tmp_path: Path) -> Path:
    p = tmp_path / "rule.xml"
    p.write_text(RULE_XML, encoding="utf-8")
    return p


@pytest.fixture
def prorule_path(tmp_path: Path) -> Path:
    p = tmp_path / "prorule.xml"
    p.write_text(PRORULE_XML, encoding="utf-8")
    return p


def test_rule_layout_kinds_and_scope(rule_path):
    text, entries = build_sections(rule_path)
    kinds = [e["kind"] for e in entries]
    assert kinds.count("preamble") == 2  # HD2 "G." block + RIA "7." block
    assert kinds.count("regtext") == 2  # amendatory group + § 425.20
    # out-of-scope content discarded at ingestion
    assert "Out of scope" not in text
    assert "Part 414" not in text
    assert "Peer RIA paragraph" not in text


def test_same_level_lettered_subheadings_do_not_end_block(rule_path):
    """Regression: FR XML tags 'a.' sub-headings at the SAME HD level as their
    numbered parent; the block must run to the next true peer ('8.')."""
    text, entries = build_sections(rule_path)
    ria = next(e for e in entries if e["heading"].startswith("7. Medicare"))
    body = text[ria["start"] : ria["end"]]
    assert "a. General Impacts" in body
    assert "RIA impact paragraph" in body
    assert "8. Other RIA Topic" not in body


def test_rule_layout_slices_match_headings(rule_path):
    text, entries = build_sections(rule_path)
    for e in entries:
        sliced = text[e["start"] : e["end"]]
        assert sliced.splitlines()[0] == e["heading"]


def test_rule_layout_preamble_content(rule_path):
    text, entries = build_sections(rule_path)
    pre = next(e for e in entries if e["kind"] == "preamble")
    body = text[pre["start"] : pre["end"]]
    assert pre["heading"] == "G. Medicare Shared Savings Program"
    assert "First MSSP preamble paragraph with spaces." in body  # collapsed
    assert "Nested MSSP paragraph." in body  # HD3 sub-block included in HD2 range


def test_rule_layout_cfr_refs(rule_path):
    _, entries = build_sections(rule_path)
    sec = next(e for e in entries if e["heading"].startswith("§ 425.20"))
    assert sec["cfr_refs"] == ["425.20"]


def test_prorule_flat_layout(prorule_path):
    text, entries = build_sections(prorule_path)
    kinds = [e["kind"] for e in entries]
    assert kinds.count("preamble") == 1
    assert kinds.count("regtext") == 2  # amendatory group + § 425.110
    assert "PART 414" not in text  # other parts discarded
    assert "Xavier Becerra" not in text  # SIG skipped
    sec = next(e for e in entries if e["heading"].startswith("§ 425.110"))
    body = text[sec["start"] : sec["end"]]
    assert "5,000 assigned beneficiaries" in body


def test_prorule_slices_match_headings(prorule_path):
    text, entries = build_sections(prorule_path)
    for e in entries:
        assert text[e["start"] : e["end"]].splitlines()[0] == e["heading"]


def test_determinism(rule_path):
    t1, e1 = build_sections(rule_path)
    t2, e2 = build_sections(rule_path)
    assert t1 == t2
    assert e1 == e2

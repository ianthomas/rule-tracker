"""Parse FR full-text XML into a frozen, normalized text artifact + section manifest.

Normalization happens ONCE here (CLAUDE.md invariant 1). After text.txt is
written it is immutable — write_frozen() refuses to overwrite with different
bytes. All downstream spans index into text.txt exactly as written.

Structure observed in the corpus — the XML vocabulary FORKS by document type
(a known risk from the phase doc; both paths share the same grouping logic):

  RULE (final rules, 2022-23873 / 2023-24184):
    root > SUPLINF (flat) > HD/P/... preamble flow, then <REGTEXT PART="425">
    blocks each containing AMDPAR instructions and SECTION elements.

  PRORULE (proposed rule, 2023-14624):
    no REGTEXT at all. Amendatory text sits flat under SUPLINF after a
    <LSTSUB> (List of Subjects): bare <PART> heading elements ("PART 425—...")
    followed by AMDPAR/AUTH/SECTION runs, until the next <PART>.
"""

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from src import config

# Elements with no extractable prose (page markers, graphics, doc plumbing,
# signatures). SIG is the officials' signature block — not regulation text.
SKIP_TAGS = {"PRTPAGE", "GPH", "GID", "BILCOD", "FRDOC", "CNTNTS", "EAR", "HRULE", "SIG"}

HD_LEVEL = {"HED": 0, "HD1": 1, "HD2": 2, "HD3": 3, "HD4": 4, "HD5": 5}

CFR_SECTION_RE = re.compile(r"425\.\d+[A-Za-z0-9-]*")


class FrozenArtifactError(RuntimeError):
    """Raised when code attempts to overwrite a frozen artifact with different bytes."""


def normalize_text(s: str) -> str:
    """NFC + collapse all whitespace runs to a single space + strip.

    Applied per paragraph, once, at ingestion. Idempotent.
    """
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def para_text(el: etree._Element) -> str:
    """One normalized paragraph from an element's full text content."""
    return normalize_text(" ".join(el.itertext()))


@dataclass
class Section:
    section_id: str
    kind: str  # "preamble" | "regtext"
    heading: str
    heading_path: list[str]
    paragraphs: list[str] = field(default_factory=list)
    cfr_refs: list[str] = field(default_factory=list)

    def render(self) -> str:
        return "\n\n".join([self.heading, *self.paragraphs])


def _hd_text(el: etree._Element) -> str:
    return para_text(el)


# FR XML flattens deep outline levels: sub-headings like "a. General Impacts"
# carry the SAME SOURCE level (e.g. HD3) as their parent "7. Medicare Shared
# Savings Program". The real hierarchy is encoded in the enumerator style, in
# this order (outermost first): I. > A. > 1. > a. > (1) > (a)/(i).
_ENUM_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"^[IVXLCDM]+\.\s"), 1),  # Roman capital: "VII. ..."
    (re.compile(r"^[A-Z]\.\s"), 2),  # Capital letter: "G. ..."
    (re.compile(r"^\d+\.\s"), 3),  # Number: "7. ..."
    (re.compile(r"^[a-z]\.\s"), 4),  # Lowercase letter: "a. ..."
    (re.compile(r"^\(\d+\)\s"), 5),  # Parenthesized number: "(1) ..."
    (re.compile(r"^\([a-z]+\)\s"), 6),  # Parenthesized letter/roman: "(a)", "(iv)"
]


def _enum_rank(heading: str) -> int:
    """Outline rank of a heading's enumerator; unenumerated headings rank
    deepest (9) so they never terminate an enumerated block."""
    for pattern, rank in _ENUM_PATTERNS:
        if pattern.match(heading):
            return rank
    return 9


def _preamble_ranges(children: list[etree._Element]) -> list[tuple[int, int]]:
    """Index ranges [start, end) of SUPLINF children covering MSSP preamble blocks.

    A block starts at a direct-child HD whose text contains the MSSP marker and
    runs until the next HD that is a true peer or ancestor — i.e. a lower HD
    SOURCE level, or the same level with an enumerator rank at or above the
    start's (see _enum_rank: same-level "a." sub-headings do NOT end a "7."
    block) — or the start of the regulation text (first REGTEXT, or LSTSUB in
    flat PRORULE layout). Ranges nested inside another matched range are dropped.
    """
    hds = [
        (i, HD_LEVEL.get(el.get("SOURCE", ""), 9), _hd_text(el))
        for i, el in enumerate(children)
        if el.tag == "HD"
    ]
    first_regtext = next(
        (i for i, el in enumerate(children) if el.tag in ("REGTEXT", "LSTSUB")),
        len(children),
    )
    ranges: list[tuple[int, int]] = []
    for i, level, text in hds:
        if config.MSSP_HEADING_MARKER not in text.lower():
            continue
        rank = _enum_rank(text)
        end = next(
            (
                j
                for j, l2, t2 in hds
                if j > i and (l2 < level or (l2 == level and _enum_rank(t2) <= rank))
            ),
            len(children),
        )
        ranges.append((i, min(end, first_regtext)))
    # Drop ranges fully contained in another matched range.
    return [
        r
        for r in ranges
        if not any(o != r and o[0] <= r[0] and o[1] >= r[1] for o in ranges)
    ]


def _heading_path_at(children: list[etree._Element], idx: int) -> list[str]:
    """Reconstruct the ancestor heading path for the HD at children[idx]."""
    level = HD_LEVEL.get(children[idx].get("SOURCE", ""), 9)
    path: list[str] = []
    want = level - 1
    for j in range(idx - 1, -1, -1):
        if want < 1:
            break
        el = children[j]
        if el.tag == "HD":
            lvl = HD_LEVEL.get(el.get("SOURCE", ""), 9)
            if lvl <= want:
                path.append(_hd_text(el))
                want = lvl - 1
    path.reverse()
    return path


def _preamble_section(
    children: list[etree._Element], start: int, end: int, sid: str
) -> Section:
    heading = _hd_text(children[start])
    sec = Section(
        section_id=sid,
        kind="preamble",
        heading=heading,
        heading_path=[*_heading_path_at(children, start), heading],
    )
    for el in children[start + 1 : end]:
        if el.tag in SKIP_TAGS or el.tag == "REGTEXT":
            continue
        p = para_text(el)
        if p:
            sec.paragraphs.append(p)
    return sec


def _regulation_sections(
    elements: list[etree._Element], part_label: str, make_id
) -> list[Section]:
    """Group a run of regulation-text elements into manifest sections.

    Works for both layouts: the children of a <REGTEXT PART="425"> block
    (RULE docs) or a flat run of SUPLINF children after a "PART 425" heading
    (PRORULE docs). Consecutive non-SECTION elements (AMDPAR instructions,
    authority citations, part headings) form 'amendatory' groups with a
    synthesized heading; each SECTION (§ 425.xxx) becomes its own section
    headed by '§ SECTNO SUBJECT'.
    """
    sections: list[Section] = []
    pending: list[str] = []

    def flush_pending() -> None:
        if not pending:
            return
        sec = Section(
            section_id=make_id(),
            kind="regtext",
            heading=f"{part_label} — amendatory instructions",
            heading_path=[part_label, "amendatory instructions"],
        )
        sec.paragraphs = list(pending)
        sec.cfr_refs = sorted(
            {m for p in pending for m in CFR_SECTION_RE.findall(p)}
        )
        sections.append(sec)
        pending.clear()

    for el in elements:
        if el.tag in SKIP_TAGS:
            continue
        if el.tag == "SECTION":
            flush_pending()
            sectno = el.find("SECTNO")
            subject = el.find("SUBJECT")
            sectno_t = para_text(sectno) if sectno is not None else ""
            subject_t = para_text(subject) if subject is not None else ""
            heading = normalize_text(f"{sectno_t} {subject_t}")
            sec = Section(
                section_id=make_id(),
                kind="regtext",
                heading=heading,
                heading_path=[part_label, heading],
                cfr_refs=CFR_SECTION_RE.findall(sectno_t),
            )
            for child in el:
                if child.tag in SKIP_TAGS or child.tag in ("SECTNO", "SUBJECT"):
                    continue
                p = para_text(child)
                if p:
                    sec.paragraphs.append(p)
            sections.append(sec)
        else:
            p = para_text(el)
            if p:
                pending.append(p)
    flush_pending()
    return sections


def build_sections(raw_xml_path: Path) -> tuple[str, list[dict]]:
    """Parse raw FR XML -> (normalized full text, section manifest entries).

    Deterministic: same input bytes always produce identical output.
    """
    tree = etree.parse(str(raw_xml_path))
    root = tree.getroot()
    sup = root.find("SUPLINF")
    if sup is None:
        raise RuntimeError(f"No SUPLINF element in {raw_xml_path} (root: {root.tag})")

    children = list(sup)
    ranges = _preamble_ranges(children)

    # PRORULE layout: no REGTEXT wrappers — find flat "PART 425" heading runs.
    has_regtext = any(c.tag == "REGTEXT" for c in children)
    flat_by_start: dict[int, int] = {}
    if not has_regtext:
        part_idxs = [i for i, el in enumerate(children) if el.tag == "PART"]
        for k, i in enumerate(part_idxs):
            label = para_text(children[i])
            if f"part {config.TARGET_CFR_PART}" in label.lower():
                end = part_idxs[k + 1] if k + 1 < len(part_idxs) else len(children)
                flat_by_start[i] = end

    counter = {"n": 0}

    def make_id() -> str:
        sid = f"s{counter['n']:04d}"
        counter["n"] += 1
        return sid

    # Walk SUPLINF children in document order, emitting sections as we go.
    sections: list[Section] = []
    range_by_start = {start: end for start, end in ranges}
    i = 0
    while i < len(children):
        el = children[i]
        if i in range_by_start:
            end = range_by_start[i]
            sections.append(_preamble_section(children, i, end, make_id()))
            i = end
            continue
        if i in flat_by_start:
            end = flat_by_start[i]
            part_label = para_text(el)  # e.g. "PART 425—MEDICARE SHARED SAVINGS PROGRAM"
            sections.extend(
                _regulation_sections(children[i + 1 : end], part_label, make_id)
            )
            i = end
            continue
        if el.tag == "REGTEXT" and el.get("PART") == config.TARGET_CFR_PART:
            part_label = (
                f"PART {el.get('PART', '?')} (Title {el.get('TITLE', '?')} CFR)"
            )
            sections.extend(_regulation_sections(list(el), part_label, make_id))
        i += 1

    # Assemble the frozen text and compute character offsets.
    parts: list[str] = []
    manifest: list[dict] = []
    offset = 0
    for sec in sections:
        rendered = sec.render()
        if parts:
            offset += 2  # the "\n\n" separator
        entry = {
            "section_id": sec.section_id,
            "kind": sec.kind,
            "heading": sec.heading,
            "heading_path": sec.heading_path,
            "start": offset,
            "end": offset + len(rendered),
        }
        if sec.cfr_refs:
            entry["cfr_refs"] = sec.cfr_refs
        manifest.append(entry)
        parts.append(rendered)
        offset += len(rendered)

    text = "\n\n".join(parts) + "\n"
    return text, manifest


def write_frozen(path: Path, data: bytes) -> bool:
    """Write bytes; refuse to change an existing frozen artifact.

    Returns True if written, False if identical content already exists.
    Raises FrozenArtifactError if the file exists with different bytes.
    """
    if path.exists():
        if path.read_bytes() == data:
            return False
        raise FrozenArtifactError(
            f"{path} is frozen; refusing to overwrite with different content. "
            f"Delete it explicitly if re-ingestion is intended."
        )
    path.write_bytes(data)
    return True


def ingest_doc(fr_doc_no: str) -> dict:
    """Build and write text.txt + sections.json for one already-fetched document."""
    spec = config.DOCS[fr_doc_no]
    ddir = config.CORPUS_DIR / fr_doc_no
    raw = ddir / "raw.xml"
    text, entries = build_sections(raw)

    text_bytes = text.encode("utf-8")
    manifest = {
        "doc_id": fr_doc_no,
        "stage": spec.stage,
        "citation": spec.citation,
        "docket": spec.docket,
        "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "text_sha256": hashlib.sha256(text_bytes).hexdigest(),
        "sections": entries,
    }
    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")

    wrote_text = write_frozen(ddir / "text.txt", text_bytes)
    # sections.json is derived deterministically from raw.xml; same freeze rule.
    wrote_manifest = write_frozen(ddir / "sections.json", manifest_bytes)

    kinds = [e["kind"] for e in entries]
    distinct_refs = sorted({r for e in entries for r in e.get("cfr_refs", [])})
    return {
        "doc_id": fr_doc_no,
        "stage": spec.stage,
        "sections": len(entries),
        "preamble": kinds.count("preamble"),
        "regtext": kinds.count("regtext"),
        "distinct_cfr_refs": len(distinct_refs),
        "chars": len(text),
        "wrote_text": wrote_text,
        "wrote_manifest": wrote_manifest,
    }

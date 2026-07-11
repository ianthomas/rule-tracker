"""Central configuration: corpus registry, model strings, spend caps.

Model strings live ONLY here (CLAUDE.md convention) — never hardcode them
elsewhere in src/.
"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"
CACHE_DIR = ROOT / "cache"
RUNS_DIR = ROOT / "runs"
GOLDEN_DIR = ROOT / "golden"


@dataclass(frozen=True)
class DocSpec:
    fr_doc_no: str
    stage: str  # BASELINE | PROPOSED | FINAL
    citation: str
    docket: str
    published: str


# The corpus is fixed — three FR documents, one rulemaking lineage (CLAUDE.md).
DOCS: dict[str, DocSpec] = {
    "2022-23873": DocSpec("2022-23873", "BASELINE", "87 FR 69404", "CMS-1770-F", "2022-11-18"),
    "2023-14624": DocSpec("2023-14624", "PROPOSED", "88 FR 52262", "CMS-1784-P", "2023-08-07"),
    "2023-24184": DocSpec("2023-24184", "FINAL", "88 FR 78818", "CMS-1784-F", "2023-11-16"),
}

FR_API_DOC_URL = "https://www.federalregister.gov/api/v1/documents/{fr_doc_no}.json"

# Extraction target: 42 CFR Part 425 (Medicare Shared Savings Program).
TARGET_CFR_PART = "425"
MSSP_HEADING_MARKER = "shared savings program"  # case-insensitive heading match

# Models (used from Phase 1 onward; declared here per convention).
DEFAULT_MODEL = "claude-haiku-4-5"  # $1.00 / $5.00 per MTok
COMPARISON_MODEL = "claude-sonnet-4-6"  # $3.00 / $15.00 per MTok
MODEL_PRICING_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
}

# Hard per-run spend cap (CLAUDE.md invariant 7).
MAX_RUN_SPEND_USD = 5.00

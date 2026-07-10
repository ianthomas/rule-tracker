# SPEC — MSSP Rule Lineage

> Capability-level view (what it does start-to-finish, for a reader): see
> docs/CAPABILITIES.md. This SPEC is the how; CAPABILITIES is the what.

## 1. Problem statement

Federal rulemaking encodes binding, conditional logic in dense prose, revised through a
baseline → proposed → final lifecycle. This project extracts that content into two typed
forms — declarative **knowledge objects** and executable **decision rules** — where every
atom carries a verified citation (character span) into the source text, then aligns
extractions across the three lifecycle stages to classify what changed and what survived
notice-and-comment.

Target corpus: MSSP provisions of the CY2023 final / CY2024 proposed / CY2024 final
Physician Fee Schedule rules (see CLAUDE.md for identifiers).

## 2. Pipeline

```
FR API (XML) ──► ingest ──► frozen text + section manifest
                              │
                              ▼
              pass 1: atom extraction (predicates, facts, spans)
                              │  span-verify atoms (exact / fuzzy≥95 / reject)
                              ▼
              pass 2: composition (boolean trees over verified atom IDs)
                              │  round-trip check + executable test cases
                              ▼
                     object store (JSONL per doc)
                              │
                              ▼
              lineage alignment across BASELINE / PROPOSED / FINAL
                              │
                              ▼
        eval harness (runs over everything above; produces runs/scorecard)
```

## 3. Ingestion

- Fetch document JSON from FR API; download `full_text_xml_url`.
- Parse XML structure; locate (a) the MSSP preamble section(s) — identified by heading
  match on "Medicare Shared Savings Program" — and (b) the Part 425 amendatory text in
  the regulation section (`<REGTEXT>` / part 425 headings).
- Emit per document:
  - `corpus/{doc_id}/sections.json` — manifest: section id, heading path, char range,
    kind (`preamble` | `regtext`).
  - `corpus/{doc_id}/text.txt` — normalized text (whitespace collapse, unicode NFC).
    **Frozen after write** (see CLAUDE.md invariant 1).
- Primary extraction target is `regtext` (clean normative language). Preamble is used
  only for lineage context in Phase 3 and is cuttable.

## 4. Schemas (pydantic v2, `src/schemas.py`)

```python
class Span(BaseModel):
    doc_id: str            # FR doc number
    start: int; end: int   # offsets into frozen text.txt
    quote: str             # denormalized copy for review UIs / golden labeling

class KnowledgeObject(BaseModel):
    obj_id: str
    obj_type: Literal["Requirement", "Definition", "Threshold"]
    section_id: str
    content: str           # model's normalized statement
    span: Span
    verification: Literal["exact", "fuzzy", "rejected"]

Operator = Literal["EQ", "NEQ", "IN_RANGE", "GTE", "LTE", "PRESENT", "ABSENT"]

class Predicate(BaseModel):
    atom_id: str
    attribute: str         # e.g. "aco_revenue_status", "prior_risk_experience"
    operator: Operator
    value: Any
    span: Span
    verification: Literal["exact", "fuzzy", "rejected"]

class ConditionNode(BaseModel):
    logic: Literal["AND", "OR", "NOT"]
    children: list["ConditionNode | PredicateRef"]   # refs by atom_id, not copies

class DecisionRule(BaseModel):
    rule_id: str
    title: str
    population: ConditionNode | None
    conditions: ConditionNode
    action: str                       # normalized outcome, e.g. "eligible_for_AIP"
    alternatives: list["AlternativeBranch"] = []
    source_spans: list[Span]          # section-level anchors
    doc_id: str
    stage: Literal["BASELINE", "PROPOSED", "FINAL"]

class RuleLineage(BaseModel):
    lineage_id: str
    members: dict[str, str | None]    # stage -> rule_id or None
    status: Literal[
        "unchanged", "proposed_new_finalized", "proposed_new_dropped",
        "modified_as_proposed", "modified_differently_than_proposed",
        "removed",
    ]
    change_notes: str
```

Closed operator vocabulary is deliberate: it is simultaneously the extraction target,
the storage format, and the executable form. Text that cannot be represented is logged
as a `representation_gap` record with its span — these are findings for the README.

## 5. Extraction (two passes)

- **Pass 1 (atoms):** per `regtext` section, prompt emits `KnowledgeObject`s and
  candidate `Predicate`s with spans. Structured output enforced by pydantic parse;
  parse failure → one retry with error feedback → reject.
- **Verify:** exact substring check at offsets; else rapidfuzz `partial_ratio ≥ 95`
  against a ±200-char window → mark `fuzzy`; else `rejected`.
- **Pass 2 (composition):** prompt receives section text + the verified atom list
  (IDs + content) and composes `DecisionRule` trees referencing atoms **by ID only**.
  The model assembles structure from verified parts; it cannot introduce new leaves.

## 6. Verification of logic (beyond spans)

1. **Round-trip check:** deterministic renderer (`src/rules/render.py`) converts a rule
   tree back to English; an LLM judge compares rendering vs. source span for logical
   equivalence (agree / disagree / unsure → disagree and unsure flagged for review).
2. **Executable test cases:** `src/rules/evaluate.py` (~50 lines) evaluates a rule
   against an entity dict. Golden set includes hand-written test cases per rule:
   `{"attrs": {...}, "expect": "eligible_for_AIP"}`. Logic-structure bugs surface as
   failing tests, not as vibes.

## 7. Eval harness

Golden set: 40–50 hand-labeled objects + 8–12 rules with 2–4 test cases each, drawn
from 2–3 Part 425 sections of the BASELINE doc (labeling more docs is cuttable).

Metrics per run (`runs/{timestamp}/scorecard.md` + `.json`):
- extraction precision / recall by `obj_type` (span-overlap ≥ 0.5 counts as match)
- groundedness rate: % objects `exact`, % `fuzzy`, % `rejected`
- rule test-case pass rate; round-trip agreement rate
- cost ($) and latency per document, per stage, per model

Golden-set provenance: the agent drafts candidate labels; the human adjudicates
(confirm/correct/reject) at the Phase 2 review gate before any metric is computed.
Scorecards report labels' provenance (`adjudicated: true`) — un-adjudicated metrics
are marked PRELIMINARY and never quoted in the README.

Run matrix: Haiku 4.5 vs Sonnet 4.6, same prompts. `make eval` runs everything and
writes the scorecard; the scorecard diff between models is the headline table.
Every scorecard is stamped with `{prompt_hash, model, corpus_hash, golden_hash}` so
any reported number is reproducible from the repo state alone.

### 7b. Call caching & spend control

`src/llm.py` caches every completion on `sha256(model + prompt_version + input)` in
`cache/` (JSON, gitignored). Cache hits cost nothing and log as `cached: true` in
`runs/calls.jsonl` (excluded from cost totals). A per-run spend cap
(`config.MAX_RUN_SPEND_USD`, default 5.00) aborts the run with a clear message and a
surfaced decision if projected cost exceeds it. Consequence: prompt/model changes are
the only things that re-pay corpus cost; code-only changes re-run free.

## 8. Lineage (Phase 3)

- Candidate matching: same CFR section number where available (regtext gives us
  § 425.xxx anchors — use them first), else embedding similarity over rule titles +
  atom sets.
- Classification into `RuleLineage.status` via deterministic comparison of the two
  trees (atom-set diff + structure diff), LLM judge only for `change_notes` prose.
- Demo query: "AIP eligibility as proposed vs. finalized, with cited spans from both."

## 9. Out of scope (do not build)

pgvector/retrieval layer; any frontend; preamble-wide extraction; comment-letter
analysis; more than three documents; agent frameworks; CI beyond `make eval`.
Each of these is a README "Roadmap" paragraph instead.
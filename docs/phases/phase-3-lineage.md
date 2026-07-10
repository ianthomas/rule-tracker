# Phase 3 — Lineage Across the Triplet (budget: 4h)

## Goal
Align rules across BASELINE → PROPOSED → FINAL and classify each lineage's fate,
producing the "what survived notice-and-comment" demo.

## Entry criteria
- Phase 2 complete; extractions exist for all three documents (run them now if
  deferred).

## Tasks
1. `src/lineage/align.py` — match rules across stages:
   a. First by CFR section anchor (§ 425.xxx) parsed from regtext headings.
   b. Unmatched remainder: cosine similarity over title + attribute set embeddings;
      accept above threshold, else leave unmatched.
2. `src/lineage/classify.py` — deterministic tree/atom diff between matched pairs →
   `RuleLineage.status` per SPEC §4. LLM writes `change_notes` prose only.
3. `make lineage` → `runs/lineage.md`: table of lineages with status, plus the
   flagship rendered example — AIP eligibility (or the best-extracted MSSP rule)
   as proposed vs. finalized, side by side, with cited spans from both documents.
4. Add 3–5 lineage assertions to the golden set if time allows (e.g. "this § was
   modified between proposed and final") and score alignment accuracy against them.

## Exit criteria
- [ ] `make lineage` produces the lineage table covering all extracted rules.
- [ ] At least one `modified_differently_than_proposed` or `proposed_new_finalized`
      lineage rendered as the side-by-side demo with verified spans.
- [ ] Unmatched rules reported explicitly (not dropped silently).

## Cuttable under time pressure
- Embedding fallback (CFR-anchor matching only; report the rest unmatched).
- Golden lineage assertions.
- If the whole phase is at risk: reduce to ONE hand-picked § followed through all
  three documents, fully rendered. One perfect lineage beats ten sloppy ones.

## Known risks
- Amendatory diff-format text (Phase 1 risk) bites hardest here: the PROPOSED doc
  may express changes as edit instructions rather than restated rules. The honest
  handling — and README paragraph — is that production systems resolve amendatory
  instructions against the CFR baseline (eCFR); this project notes the gap.

## Manual integration tests (design for the human — target ≤10 min total)
- **M1 — flagship lineage (5 min):** `make demo` prints the side-by-side
  proposed-vs-final rendering with spans; human verifies against the FR website that
  the change characterization is actually true. This is THE credibility check.
- **M2 — status distribution sanity (3 min):** lineage status counts; human judges
  plausibility (e.g. 90% `unchanged` across a major rulemaking would smell wrong).

## On completion (review gate)
1. Ensure unit tests + automated integration tests for this phase are green (`make test`).
2. Write `tests/integration/phase-N/MANUAL.md` (see manual tests below).
3. Write the retro, then the review package (`docs/review/phase-N-package.md`).
4. Update STATUS to `awaiting human review`; commit `phase-N: review package submitted`; STOP.
(Replace N with this phase's number.)

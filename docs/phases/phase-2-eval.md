# Phase 2 — Eval Harness (budget: 5h)

## Goal
A golden set and an automated scorecard that turns "does it work" into numbers, and
prices the Haiku-vs-Sonnet tradeoff. This phase is the interview centerpiece; do not
let it get squeezed.

## Entry criteria
- Phase 1 complete; pipeline runs end-to-end on BASELINE.

## Tasks
1. Golden set (`golden/`): the agent DRAFTS 40–50 candidate labels and 8–12 rules
   from 2–3 BASELINE Part 425 sections (same pydantic schemas,
   `source: "agent_draft"`), then builds `make adjudicate` — a terminal flow showing
   each draft label beside its source span for the human to confirm / correct /
   reject (keystroke-fast; corrections editable inline). Adjudication itself happens
   at THIS PHASE'S REVIEW GATE and flips labels to `source: "human_adjudicated"`.
   Metrics computed on un-adjudicated labels are marked PRELIMINARY. Agent timebox
   for drafting + tooling: 2h.
2. Rule test cases: 2–4 per golden rule (`golden/testcases.jsonl`), covering at least
   one boundary (range edge) and one negation branch each.
3. `src/eval/` — metrics from SPEC §7:
   - precision/recall by obj_type (span-overlap ≥0.5 = match)
   - groundedness: % exact / fuzzy / rejected (from logs)
   - rule test-case pass rate; round-trip agreement rate (wire the judge now if
     deferred from Phase 1)
   - cost + latency per doc per model (aggregate `runs/calls.jsonl`)
4. `make eval` → `runs/{ts}/scorecard.md` + `.json`. Markdown table format designed
   to be pasted directly into the README.
5. Run the matrix: Haiku 4.5 and Sonnet 4.6 on the golden sections. One prompt-tuning
   iteration afterward is allowed if a metric is embarrassing; re-run matrix after.

## Exit criteria
- [ ] `make eval` runs unattended and writes a scorecard.
- [ ] Scorecard contains the model-comparison table with cost per document.
- [ ] Every metric in SPEC §7 present (or explicitly marked n/a with reason).
- [ ] Golden set committed with a `golden/README.md` describing labeling rules
      (what counts as a Requirement vs Definition, span conventions) and provenance
      semantics (agent_draft vs human_adjudicated).
- [ ] `make adjudicate` works and is included as manual test M0.
- [ ] Scorecards stamped with prompt/model/corpus/golden hashes (SPEC §7).

## Cuttable under time pressure
- Round-trip judge metric (keep test-case pass rate — it's stronger anyway).
- Second model run on PROPOSED/FINAL (golden sections only is fine).

## Known risks
- Draft labeling always takes longer than expected. The 2h timebox is real: at 2h,
  stop and shrink the golden set to what exists.
- Adjudication UX matters: if confirm/correct/reject isn't keystroke-fast, the human
  gate blows its time budget. Test the flow on 5 labels before generating 50.

## Manual integration tests (design for the human — target ≤25 min total)
- **M0 — golden adjudication (10–15 min):** run `make adjudicate`; confirm/correct/
  reject every draft label. This is the gate's core task — final metrics only exist
  after it. (This replaces agent-side "hand-labeling"; your judgment IS the label.)
- **M1 — golden-set audit (5 min):** print 5 random golden labels with source; human
  confirms the labels themselves are right (garbage golden = garbage metrics).
- **M2 — scorecard credibility (5 min):** human reads the scorecard and checks each
  headline number against one drill-down example the package links (e.g. one false
  negative, one fuzzy match) — do the numbers mean what they claim?
- **M3 — disagreement review (3 min):** the 3 largest Haiku-vs-Sonnet disagreements,
  printed with sources; human notes which model was right (feeds the README).

## On completion (review gate)
1. Ensure unit tests + automated integration tests for this phase are green (`make test`).
2. Write `tests/integration/phase-N/MANUAL.md` (see manual tests below).
3. Write the retro, then the review package (`docs/review/phase-N-package.md`).
4. Update STATUS to `awaiting human review`; commit `phase-N: review package submitted`; STOP.
(Replace N with this phase's number.)

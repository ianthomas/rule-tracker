# Phase 1 — Extraction + Verification (budget: 6h)

## Goal
Two-pass extraction (atoms → composed rules) with code-enforced span verification,
working end-to-end on the BASELINE document first, then run on all three.

## Entry criteria
- Phase 0 complete (retro exists); frozen texts + manifests for all three docs.

## Tasks
1. `src/schemas.py` — all models from SPEC §4. Resist adding object types.
2. `src/extract/atoms.py` — pass 1 per regtext section: KnowledgeObjects + Predicates
   with spans. Structured output via pydantic parse; 1 retry with validation errors
   fed back; then reject.
3. `src/verify/spans.py` — exact match at offsets → `exact`; rapidfuzz partial_ratio
   ≥95 within ±200 chars → `fuzzy` (re-anchor offsets to best window); else `rejected`.
   Rejections logged to `runs/rejections.jsonl` with reason.
4. `src/extract/compose.py` — pass 2: DecisionRules referencing verified atoms by ID.
   Hard-fail any rule referencing an unknown atom_id.
5. `src/rules/render.py` + `src/rules/evaluate.py` — deterministic renderer and
   evaluator (SPEC §6). Unit-test the evaluator with hand-built trees BEFORE wiring
   the LLM round-trip judge.
6. LLM call metering AND caching in one place (`src/llm.py`): model, tokens, cost,
   latency → `runs/calls.jsonl`; cache on `hash(model+prompt_version+input)` per
   SPEC §7b; hard spend cap from config. Prompts live in `prompts/*.md` with version
   headers — no inline prompt strings (CLAUDE.md "Prompts are code").
7. Run full pipeline on BASELINE; skim outputs; fix the top 2–3 systematic errors via
   prompt edits (timeboxed: 45 min of prompt iteration max in this phase — the eval
   harness in Phase 2 is where tuning gets rigorous).
8. Run on PROPOSED and FINAL.

## Exit criteria
- [ ] `make extract` produces `objects.jsonl` + `rules.jsonl` per document.
- [ ] 0 objects in store with `rejected` status (rejected stays in logs only).
- [ ] Evaluator unit tests green, including a nested NOT(AND(...)) case.
- [ ] ≥5 DecisionRules extracted from BASELINE Part 425 text (sanity floor, not a target).
- [ ] `runs/calls.jsonl` populated with cost/latency for every call.
- [ ] Re-running `make extract` with no prompt/model change is a 100% cache hit
      (near-zero cost, verified in the log).
- [ ] All prompts in `prompts/` with version headers; extraction outputs stamped
      with prompt_hash.

## Cuttable under time pressure
- Round-trip LLM judge (defer wiring to Phase 2; renderer still required).
- PROPOSED/FINAL runs (defer to start of Phase 3).
- `Threshold` object type (fold into `Requirement`).

## Known risks
- Amendatory text is *diff-formatted* ("revise paragraph (a)(2) to read..."), so some
  regtext is instructions-about-text rather than rules. Handle: extract only from
  full restated provisions; log instruction-style blocks as `representation_gap`.
  This is a genuinely interesting finding — write it up in the retro.

## Manual integration tests (design for the human — target ≤15 min total)
- **M1 — citation faithfulness (5–8 min):** `make spotcheck N=8` prints 8 random
  objects: extracted content, quoted span, ±1 sentence of surrounding source. Human
  judges: is the span a faithful citation for the content? Pass = ≥7/8 faithful.
- **M2 — rule readability (5 min):** render 3 extracted DecisionRules to English
  side-by-side with their source spans. Human judges logical equivalence.
- **M3 — rejection triage (2 min):** print rejection-reason counts from
  `runs/rejections.jsonl`; human confirms no single systematic failure dominates.

## On completion (review gate)
1. Ensure unit tests + automated integration tests for this phase are green (`make test`).
2. Write `tests/integration/phase-N/MANUAL.md` (see manual tests below).
3. Write the retro, then the review package (`docs/review/phase-N-package.md`).
4. Update STATUS to `awaiting human review`; commit `phase-N: review package submitted`; STOP.
(Replace N with this phase's number.)

# Phase 4 — README, ADRs, Demo Polish (budget: 2h)

## Goal
The README *is* the product for a reviewer with 10 minutes. Write it as an
architecture decision record, not a tutorial.

## Entry criteria
- Phases 0–3 retros exist; scorecard and lineage outputs are current.

## Tasks
1. README structure:
   - What this is (3 sentences) + the one-sentence pitch.
   - The guaranteed-citation mechanism (span verification, leaf-level cites).
   - The rule schema and why it's constrained (extraction target = storage = executable).
   - Scorecard table (paste from runs/) — Haiku vs Sonnet cost/quality.
   - The lineage demo (side-by-side render, or screenshot of terminal output).
   - Honest limitations: representation gaps, amendatory-text problem, fuzzy-span rate.
   - Roadmap (design-only): eCFR baseline resolution, retrieval layer, preamble
     enrichment, comment-letter attribution, when a framework would earn its keep.
2. Sweep `docs/decisions/` — ensure ADRs exist for: XML-over-PDF, triplet corpus,
   constrained rule schema, no-framework, regtext-over-preamble. Fill gaps from
   retro notes (they're already half-written there).
3. `make demo` — single command that runs eval + lineage and prints the flagship
   example. Rehearse the 3-minute walkthrough once.
4. Final commit; tag `v0.1`.

## Exit criteria
- [ ] README complete with real numbers (no placeholders).
- [ ] Five ADRs present and honest.
- [ ] `make demo` works from a clean clone (given an API key).
- [ ] Final retrospective covers the whole project: what you'd say in the interview
      about what you'd do differently.

## Cuttable under time pressure
Nothing. If earlier phases ate the budget, cut THERE, not here — a polished README
over a partial build wins; a full build with a stub README loses.

## Manual integration tests (the human IS the test here — target ≤20 min)
- **M1 — cold-reader pass (10 min):** read the README start to finish as the
  interviewer would; every number must trace to a linked artifact; flag any claim
  you couldn't defend live.
- **M2 — clean-clone demo (5 min):** fresh clone, `make demo` with only an API key;
  it must work exactly as the README says.
- **M3 — interview rehearsal (5 min):** deliver the 3-minute walkthrough out loud
  once; note where you stumble — those spots need README or ADR reinforcement.

## On completion (review gate)
1. Ensure unit tests + automated integration tests for this phase are green (`make test`).
2. Write `tests/integration/phase-N/MANUAL.md` (see manual tests below).
3. Write the retro, then the review package (`docs/review/phase-N-package.md`).
4. Update STATUS to `awaiting human review`; commit `phase-N: review package submitted`; STOP.
(Replace N with this phase's number.)

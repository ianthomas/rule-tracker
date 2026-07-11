# Phase 0 Review Response

**Reviewer:** Ian · **Date:** 2026-07-11 · **Human time spent:** ~20 min (in-session, interactive)
**Verdict:** APPROVED — proceed to phase 1

---

## 1. Manual integration test results

| # | Result | Notes |
|---|--------|-------|
| M1 | ✅ | Ran `make inspect` on all three docs interactively. Presence: MSSP preamble chapter + § 425.x regtext in each doc. Purity: no other CFR parts / PFS topics. **The first M1 run caught a real capture bug** — the RIA preamble section (s0003, "7. Medicare Shared Savings Program") was heading-only because FR XML tags "a." sub-headings at the same HD level as their numbered parent. Fix authorized and applied (enumerator-rank boundaries, +66,243 chars recovered, corpus regenerated); see `docs/review/phase-0-package-addendum.md`. Re-ran inspect on all three docs post-fix: pass. Empty `§ 425.xxx [Amended]` stubs confirmed as correct FR structure. |
| M2 | ✅ | `make spotcheck` — 9/9 windows clean: no tag debris, no entities, intact words, correct paragraphing, `§` renders properly. The one anomaly ("provides that that the Secretary") was verified verbatim in the source XML — a genuine FR typo, faithfully reproduced. |

## 2. Decisions

- **D0.1:** (a) — keep coarse preamble blocks.
- **D0.2:** (a) — keep synthesized headings. Rationale: the more context baked into
  the artifact the better. The committed mitigation stands: Phase 1's span verifier
  rejects extraction spans overlapping a synthesized heading line (identifiable as
  the `heading` of manifest entries ending in `— amendatory instructions`).
- **D0.3:** (a) — accept the toolchain installs and repo config as done.
- Provisional decisions: all confirmed.

## 3. Rework items

None. (The one defect found in M1 was fixed and verified within this review cycle;
recorded in the addendum.)

## 4. Scope / plan adjustments

None.

## 5. Observations for the agent

- The M1 catch is the lesson to carry forward: the automated invariant
  ("first line == heading") passed while section *content* was missing. Structural
  checks don't prove completeness — keep the human eyeball step meaningful, and
  where cheap, add content-presence assertions (e.g. the new
  "no empty preamble sections" condition) to the automated suite.
- Synthesized amendatory-group headings differ cosmetically by layout
  ("PART 425 (Title 42 CFR) — …" in RULE docs vs "PART 425—MEDICARE SHARED SAVINGS
  PROGRAM — …" in PRORULE). Accepted as-is; both end in `— amendatory instructions`
  (the D0.2 marker). Note it at Phase 1 entry; do not thaw frozen artifacts for it.
- The proposed and final rules mirror each other's amendatory numbering (85–108)
  and § lineup almost 1:1 — use `cfr_refs` as the primary Phase 3 alignment key.

---

*On commit of this file, the agent is authorized to: convert architectural decisions
above into ADRs, apply rework items, and enter phase 1 per CLAUDE.md.*

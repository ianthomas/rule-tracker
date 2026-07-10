# ADR-002: One rulemaking lineage (baseline → proposed → final), MSSP slice only

**Status:** accepted · **Date:** project start · **Phase:** 0

## Context
20-hour budget. Candidate corpora: many CMS documents, coverage determinations,
multi-year MSSP finals. A proposed/final pair from the same docket plus the prior
final gives three semantically distinct diffs (proposal detection, comment effect,
net change) inside one consistent document family.

## Decision
Corpus is exactly: FR 2022-23873 (BASELINE), 2023-14624 (PROPOSED), 2023-24184
(FINAL); extraction scope is the MSSP preamble + 42 CFR Part 425 regtext only.

## Alternatives considered
- Two consecutive finals: simpler, but loses the notice-and-comment story.
- LCD/NCD coverage policies: richer clinical logic, but abandons the lineage angle
  and the MSSP domain knowledge already invested. Noted in roadmap.

## Consequences
Lineage becomes the flagship demo. Risk accepted: proposed-rule amendatory text may
express changes as edit instructions (see ADR-005 territory / Phase 3 risk note).

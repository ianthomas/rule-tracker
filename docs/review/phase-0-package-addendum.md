# Phase 0 Package — Addendum 1 (correction, 2026-07-11)

The submitted package (`phase-0-package.md`, tag `phase-0-pkg`) is unmodified per
the workflow; this addendum corrects it. Reviewed and authorized by Ian in-session
before the fix was applied.

## What was found

During the human's M1 dry run (`make inspect DOC=2022-23873`), preamble section
s0003 ("7. Medicare Shared Savings Program", the RIA impact analysis) was
discovered to contain **only its heading** — the body was missing from the frozen
corpus. Cause: FR XML tags sub-headings like "a. General Impacts" at the **same
HD SOURCE level** as their numbered parent, so the capture range ended at the
first sub-heading. The same truncation shortened other matched preamble blocks in
all three documents.

## What was fixed

- `_enum_rank()` in `src/ingest/sections.py`: heading enumerator styles are ranked
  (`I.` > `A.` > `1.` > `a.` > `(1)` > `(a)`); a capture range now ends only at a
  same-level heading whose rank is at or above the block start's rank.
- Regression test `test_same_level_lettered_subheadings_do_not_end_block` added
  (suite is now **37 passed**; `runs/phase-0/unit.txt` regenerated).
- Frozen artifacts were **deliberately deleted and regenerated** (authorized; the
  freeze guard requires explicit deletion). New `text_sha256` values are recorded
  in each `sections.json`.

## Numbers superseded (package §1–2 and retro)

| Metric | Was | Now |
|---|---|---|
| Total sections | 163 (19 preamble) | **162 (18 preamble)** — one FINAL-doc preamble block is now correctly contained inside an extended sibling range and merged |
| Frozen chars | ~3.0M (3,038,711) | **~3.1M (3,104,954)** — +66,243 chars of previously dropped MSSP preamble content |
| Unit tests | 36 passed | **37 passed** |
| BASELINE / PROPOSED / FINAL chars | 1,487,681 / 572,580 / 978,450 | 1,516,708 / 591,104 / 997,142 |

Regtext counts (57/44/43) and distinct § refs (36/26/26) are unchanged — the bug
affected preamble capture only. All exit criteria still pass on the regenerated
artifacts (idempotence re-verified: second `make ingest` logs `unchanged (frozen)`).

## Effect on your review

- M1/M2 should be run against the regenerated corpus (current working tree).
- Decision D0.1's size figure changes slightly (the baseline "G." chapter is
  unchanged; the RIA blocks grew). The decision itself and its default stand.
- No effect on D0.2 or D0.3.

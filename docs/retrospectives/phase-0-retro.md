# Phase 0 Retrospective — Scaffold + Ingestion

**Dates:** 2026-07-10 → 2026-07-10
**Budget:** 3h · **Actual:** ~2h · **Running total:** 2/20h

## What was built

A uv-managed Python skeleton (`pyproject.toml`, `Makefile`, `src/config.py` with the
doc registry, model strings, and the $5 spend cap) and the full ingestion pipeline:
`src/ingest/fetch.py` (FR API → cached `raw.xml`), `src/ingest/sections.py`
(XML → frozen `text.txt` + `sections.json`, with a freeze guard), and the
`inspect`/`spotcheck` CLIs backing the manual tests. All three corpus documents are
ingested and committed: 63 / 50 / 50 sections (57 / 44 / 43 regtext Part 425 blocks),
~3.0M chars of frozen text total. 36 unit + automated integration tests green
(`runs/phase-0/unit.txt`), ruff clean.

## Exit criteria review

| Criterion | Met? | Evidence |
|-----------|------|----------|
| `make ingest` produces raw.xml, text.txt, sections.json for all three docs | ✅ | `runs/phase-0/ingest.txt`; `corpus/*/` committed |
| Manifest for each doc includes ≥1 regtext block touching Part 425 | ✅ | `test_at_least_one_part_425_regtext`; counts printed in `runs/phase-0/ingest.txt` (57/44/43 blocks, 36/26/26 distinct § refs) |
| Smoke test green (offsets slice to heading) | ✅ | `test_offsets_slice_to_heading` — 0 violations across 163 sections |
| text.txt byte-identical across two consecutive `make ingest` runs | ✅ | second run printed `unchanged (frozen)` for all docs; `test_ingest_idempotent` re-parses raw.xml and compares bytes |

## What was harder than planned

- **The proposed rule has no `<REGTEXT>` elements at all.** The phase doc predicted
  tag-vocabulary differences; the reality was structural: `PRORULE` documents put
  amendatory text flat under `SUPLINF` (`<PART>` heading elements followed by
  AMDPAR/AUTH/SECTION runs), while `RULE` documents wrap it in
  `<REGTEXT PART="425">`. First ingest of 2023-14624 captured **0 regtext sections**.
  Fixed by detecting the layout and routing both through one shared grouping
  function (`_regulation_sections`); documented in the module docstring. Cost ~30 min.
- **Windows environment setup.** `uv`, `make`, and Python ≥3.11 were all absent from
  the machine at session start (Phase 0 entry criteria assumed a uv env existed).
  Installed uv via the official installer and GNU make 4.4.1 from ezwinports into
  `~/.local/bin`. Cost ~20 min. Also added `.gitattributes` (`corpus/** -text`)
  because git's Windows CRLF conversion would silently rewrite frozen artifacts and
  shift every span offset.

## What was cut, and why

- Nothing from the phase's cuttable list. Both preamble capture and the inspect
  command shipped.

## Surprises / findings

- **Amendatory text is fragmentary by design.** Sections revised by a rule appear as
  partial text with `* * *` (STARS) placeholders for unchanged paragraphs — e.g.
  § 425.106 in the proposed rule is 343 chars: only paragraph (c)(5). Extraction in
  Phase 1 must not assume a section slice is the complete regulation; the lineage
  logic in Phase 3 must not read "absent from the proposed rule" as "removed".
- **The heading is the span anchor.** Making "manifest heading == first line of the
  slice" an invariant gave every phase a free structural integrity check (it's both a
  unit test on synthetic XML and an integration test on the real corpus).
- Tables (`GPOTABLE`) are flattened to run-on paragraph text. Only 2 occur in the
  baseline doc's captured range; acceptable for now, noted for the M2 reviewer.

## Prompt/model observations

No LLM calls this phase (ingestion is deterministic code). The Phase 1 extraction
prompts will consume per-section slices; the fragmentary-amendment finding above
should be reflected in the extraction prompt's framing.

## Talking points harvested (REQUIRED — appended to docs/TALKING-POINTS.md)

- See docs/TALKING-POINTS.md (Phase 0 section): dual-layout fork, CRLF-vs-spans,
  the freeze-guard invariant, and fragmentary amendatory text.

## Instructions for the next phase

- Start Phase 1 by reading `sections.json` — extraction operates on `regtext`
  sections only; use `cfr_refs` as the section anchor for later lineage.
- Amendatory-instruction groups (`… — amendatory instructions` headings) carry
  context ("Section X is amended by revising (c)(5)") that the extractor should see
  alongside the following § section — consider pairing them in the prompt input.
- Do NOT re-normalize text anywhere downstream. Spans index into `text.txt` as
  committed; `sections.json.text_sha256` is the guard.
- The environment is now set up (uv, make on PATH for new sessions). `make test`
  runs everything; integration tests skip gracefully without the corpus.

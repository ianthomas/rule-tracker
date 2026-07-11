# Phase 0 — Scaffold + Ingestion (budget: 3h)

## Goal
Three frozen, span-stable MSSP/Part 425 text artifacts with section manifests, plus a
working project skeleton. Nothing clever; everything reproducible with `make ingest`.

## Entry criteria
- Repo initialized, `uv` env created, CLAUDE.md and docs/ in place.

## Tasks
1. `src/config.py` — doc registry (three FR doc numbers + stages), model strings.
2. `src/ingest/fetch.py` — FR API JSON → download `full_text_xml_url` to
   `corpus/{doc_id}/raw.xml`. Cache: skip download if file exists.
3. `src/ingest/sections.py` — parse XML; build heading tree; select MSSP preamble
   sections (heading contains "Shared Savings Program") and Part 425 regtext blocks;
   emit `sections.json` + frozen `text.txt` (normalize ONCE: NFC, collapse runs of
   whitespace inside lines, preserve paragraph breaks).
4. Spot-check notebook or `make inspect DOC=2022-23873` printing section headings and
   first 200 chars of each — eyeball that MSSP content is actually captured.
5. `pytest` smoke test: offsets in `sections.json` slice `text.txt` to text whose first
   line matches the recorded heading.

## Exit criteria (check off with evidence in this file)
- [x] `make ingest` produces `corpus/{doc}/raw.xml`, `text.txt`, `sections.json` for all
      three documents. — Evidence: `runs/phase-0/ingest.txt`; artifacts committed under `corpus/`.
- [x] Section manifest for each doc includes ≥1 `regtext` block touching Part 425.
      — Evidence: 57/44/43 regtext sections; `test_at_least_one_part_425_regtext` green.
- [x] Smoke test green. — Evidence: `test_offsets_slice_to_heading`, 0 violations
      across 163 sections (`runs/phase-0/unit.txt`).
- [x] `text.txt` files are byte-identical across two consecutive `make ingest` runs
      (idempotence — protects span integrity). — Evidence: second run logged
      `unchanged (frozen)` for all three docs; `test_ingest_idempotent` green.

## Cuttable under time pressure
- Preamble section capture (keep regtext only; lineage loses some context, survivable).
- The inspect command (fall back to manual grep).

## Known risks
- XML tag vocabulary may differ between proposed and final rule documents; if section
  selection logic forks per doc type, note it in an ADR-worthy comment, not a hack.
- The proposed rule is "Book 2 of 2" — confirm the API's XML covers the full document.

## Manual integration tests (design for the human — target ≤10 min total)
- **M1 — MSSP capture sanity (5 min):** `make inspect DOC=<each>` for all three docs;
  human confirms the section headings are actually MSSP/Part 425 material and that
  nothing obviously MSSP-related is missing (compare against the FR website TOC).
- **M2 — text quality spot-check (3 min):** print 3 random 500-char windows per doc;
  human confirms no XML tag debris, no mid-word breaks, sane paragraphing.

## On completion (review gate)
1. Ensure unit tests + automated integration tests for this phase are green (`make test`).
2. Write `tests/integration/phase-N/MANUAL.md` (see manual tests below).
3. Write the retro, then the review package (`docs/review/phase-N-package.md`).
4. Update STATUS to `awaiting human review`; commit `phase-N: review package submitted`; STOP.
(Replace N with this phase's number.)

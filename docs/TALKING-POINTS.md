# Talking Points — interview-ready material, harvested per phase

Append-only. Every retro adds 2–4 bullets (see retro template). Phase 4 polishes
this file into the walkthrough script; it does not create it from scratch.

Format per bullet: **[phase-N]** claim, with the number or artifact that backs it.

Seed points (from project design, before any code):
- **[design]** Citations are enforced by code, not trusted from the model: every
  extracted atom carries character-span offsets verified against frozen source text;
  spans that fail exact-or-fuzzy(≥95) verification are rejected, so an uncited claim
  structurally cannot enter the store.
- **[design]** The rule schema's closed operator vocabulary does three jobs at once —
  extraction target, storage format, executable form — which is what makes leaf-level
  citation and executable test cases possible at all.
- **[design]** Chose one rulemaking lineage (baseline → proposed → final) over more
  documents: three semantically distinct diffs (proposal detection, comment effect,
  net change) beat breadth for demonstrating regulatory intelligence.
- **[design]** Deliberately no LangChain/ADK: a fixed two-pass DAG doesn't earn a
  framework; the stronger answer is articulating the adoption threshold (dynamic tool
  routing, multi-agent state, org-scale provider abstraction).

Phase 0:
- **[phase-0]** The FR XML vocabulary forks by document type: final rules wrap
  amendatory text in `<REGTEXT PART="425">`, but the proposed rule has zero REGTEXT
  elements — its regulation text sits flat under SUPLINF. First ingest captured 0 of
  44 regtext sections for the proposed rule; one shared grouping function now handles
  both layouts. Lesson: validate ingestion per document *type*, not per pipeline.
- **[phase-0]** Span integrity nearly died before extraction even started: on Windows,
  git's autocrlf would rewrite the frozen text.txt line endings on checkout, silently
  shifting every character offset. Fixed with `.gitattributes: corpus/** -text` —
  a one-line file protecting the project's core invariant.
- **[phase-0]** The freeze guard is code, not convention: `write_frozen()` refuses to
  overwrite an artifact with different bytes, and an integration test re-hashes
  text.txt against the sha256 recorded at ingestion. Re-running `make ingest` is a
  verified no-op (byte-identical across runs).
- **[phase-0]** Amendatory text is fragmentary by design — a revised section appears
  as just the changed paragraphs with `* * *` placeholders (§ 425.106 in the proposed
  rule is 343 chars: only (c)(5)). This constrains Phases 1 and 3: a section slice is
  not the whole regulation, and "absent from the proposed rule" ≠ "removed".

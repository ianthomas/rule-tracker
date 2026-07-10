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

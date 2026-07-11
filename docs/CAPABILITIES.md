# Capabilities

What the system does, start to finish. This document is the capability contract;
Phase 4 fills the `{{...}}` placeholders with real numbers from `runs/` and links to
concrete output artifacts. Until then, unfilled placeholders mean "not yet measured."

The one-sentence version:

> Point it at a policy rulemaking, and it gives you a queryable knowledge base where
> every answer is cited, every rule is executable against a scenario, and every change
> across the proposed-to-final lifecycle is traced — with an eval harness that says how
> often it's right and what it cost.

---

## Input

Three Federal Register document numbers — the CY2023 PFS final (baseline), the CY2024
PFS proposed, and the CY2024 PFS final. That is the entire input. `make ingest` pulls
the official XML, isolates the MSSP + 42 CFR Part 425 sections out of ~2,200 pages of
omnibus rule, and writes three frozen, span-stable text corpora with section manifests.

Capability: turn a ~1,000-page regulatory document into a clean, addressable slice of
exactly the policy area in scope, reproducibly (`make ingest` is idempotent).

## The knowledge layer (built by `make extract`)

Per document, two artifacts:

- **Knowledge objects** — every Requirement, Definition, and Threshold in the
  regulation text as a typed record, each with character-span offsets code-verified
  against the frozen source. Guarantee: nothing enters the store without a citation
  that verifies. Objects whose spans fail exact-or-fuzzy(≥95) verification are rejected.
- **Decision rules** — conditional eligibility/obligation logic as executable boolean
  trees over a closed operator vocabulary, every leaf predicate carrying its own
  verified span. Policy logic that is both cited and runnable.

Corpus counts (filled in Phase 4): {{n_objects_by_type}}, {{n_rules}},
{{n_representation_gaps}}.

## The four things you can do

### 1. Cited question answering
Query the knowledge objects; answers are composed only from stored objects, return the
source text + citation with every claim, and abstain when no supporting object exists
rather than drawing on model priors.
- Example query + output: {{qa_example_link}}
- Abstention example (out-of-corpus question): {{qa_abstain_example_link}}

### 2. Rule execution against a scenario  ← differentiator
Hand it an entity profile; the evaluator fires the extracted logic and returns the
outcome plus the cited span for every predicate that fired.
```
input:  { "revenue_status": "low", "prior_risk_experience": false, ... }
output: eligible_for_advance_investment_payment: true
          ✓ revenue_status == "low"        → § 425.xxx  "<verified span>"
          ✓ prior_risk_experience == false → § 425.xxx  "<verified span>"
```
Flipping one attribute changes the determination and shows which predicate failed.
- Worked example: {{rule_exec_example_link}}

### 3. Lifecycle lineage (built by `make lineage`)
Aligns a rule across baseline → proposed → final and classifies its fate
(`unchanged`, `modified_as_proposed`, `modified_differently_than_proposed`,
`proposed_new_finalized`, `proposed_new_dropped`, `removed`). "What did CMS propose,
and what survived notice-and-comment" — computed as a deterministic tree/atom diff,
with cited spans from each stage. LLM writes only the change-note prose.
- Flagship side-by-side (proposed vs finalized): {{lineage_flagship_link}}
- Full lineage table: {{lineage_table_link}}

### 4. Measurement (built by `make eval`)
Stamped scorecard: extraction precision/recall by type, groundedness rate, rule
test-case pass rate, cost and latency — as a Haiku-vs-Sonnet matrix.
- Scorecard: {{scorecard_link}} · Model comparison headline: {{model_comparison_row}}

## The demo, as one motion (`make demo`)
Point at the extracted store → ask a knowledge question, get a cited answer → run an
ACO profile through a rule, get a cited determination → flip one attribute, watch it
change → pull that rule's proposed-vs-final lineage → show the scorecard.

## What it deliberately does not do
- Not a chatbot over all of Medicare law — three documents, MSSP slice. Scope is a feature.
- Does not resolve amendatory instructions ("revise paragraph (a)(2) to read...")
  against the live eCFR baseline; edit-instruction text is logged as a
  `representation_gap`, not silently applied. Production systems (Lexis included)
  resolve against the codified baseline; this one names the gap.
- Logic outside the closed operator vocabulary is logged as a representation gap, not
  forced into a wrong shape. Gaps are a reported finding, not a hidden failure.
- No open-web retrieval, no un-ingested documents, no UI. The surface is a CLI, by choice.

## Maturity (honest, updated each phase)
- Cited Q&A / rule execution / eval: core, expected solid on extracted sections.
- Lineage: highest schedule risk; fallback is one fully-worked lineage over
  comprehensive coverage ("one perfect lineage beats ten sloppy ones").
- Rule extraction: robust on well-structured eligibility sections, thinner on
  amendatory text — which is exactly what representation-gap logging surfaces.
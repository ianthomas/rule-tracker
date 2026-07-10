# mssp-rule-lineage

Point it at a policy rulemaking, and it gives you a queryable knowledge base where
every answer is cited, every rule is executable against a scenario, and every change
across the proposed-to-final lifecycle is traced — with an eval harness that says how
often it's right and what it cost.

The corpus is the Medicare Shared Savings Program provisions of three CMS Physician
Fee Schedule rules — CY2023 final (baseline), CY2024 proposed, CY2024 final — one
rulemaking followed through the notice-and-comment lifecycle.

> **Note:** this README is finalized in Phase 4 with real numbers. Sections marked
> `{{...}}` are placeholders until then. Design intent is authoritative now; the
> metrics are not yet measured.

## Why this exists

In legal and regulatory text, a fabricated citation is a fireable offense. The design
premise here is that **citations are enforced by code, not trusted from the model**:
every extracted atom carries character-span offsets into a frozen source text, and a
verification layer checks each span exists before the object is allowed into the store.
An uncited claim structurally cannot enter. That is the same bet the domain's leading
products make — grounded answers whose every clause traces to real source.

## What it does

1. **Cited question answering** — answers composed only from stored objects, each with
   its source span; abstains when no supporting object exists.
2. **Rule execution** — extracted eligibility/obligation logic runs against a scenario
   and returns a determination with a cited span for every predicate that fired.
3. **Lifecycle lineage** — the same rule aligned across baseline → proposed → final,
   classified by what survived notice-and-comment, with cited spans from each stage.
4. **Measurement** — a stamped scorecard of accuracy, groundedness, and cost/latency,
   run as a model-comparison matrix.

Full capability contract: [`docs/CAPABILITIES.md`](docs/CAPABILITIES.md).

## Architecture in one paragraph

Federal Register XML → ingestion (isolate MSSP/Part 425, freeze normalized text) →
two-pass extraction (atoms with spans, then boolean-tree composition over verified
atoms by ID) → two verification gates (span existence, then logic correctness via
round-trip check + executable test cases) → JSONL object store → lineage alignment
across the three documents. Every model call routes through one metered, cached
wrapper; every scorecard is stamped with prompt/model/corpus/golden hashes for
reproducibility. Design and schemas: [`docs/SPEC.md`](docs/SPEC.md); decisions:
[`docs/decisions/`](docs/decisions/).

## Quickstart

```bash
uv sync
cp .env.example .env   # add ANTHROPIC_API_KEY
make ingest            # pull XML, freeze the three corpora
make extract           # objects + rules per document
make eval              # scorecard → runs/
make lineage           # rule lineage across the triplet
make demo              # the 3-minute walkthrough
```

## Results  {{filled in Phase 4}}

- Extraction precision/recall by type: {{table}}
- Groundedness (exact / fuzzy / rejected): {{rates}}
- Rule test-case pass rate: {{rate}}
- Haiku vs Sonnet — cost per document at equal quality: {{comparison}}

## Limitations

Honest edges (expanded in `docs/CAPABILITIES.md`): three-document MSSP slice, not all
of Medicare law; amendatory edit-instructions are logged as representation gaps rather
than resolved against the live eCFR baseline; logic outside the closed operator
vocabulary is logged, not forced; CLI only.

## Roadmap (designed, not built)

eCFR baseline resolution for amendatory text; hybrid retrieval at scale via pgvector
colocated with the relational rule/lineage data; a graph layer over lineage edges
(the architectural bet behind knowledge-graph-augmented legal RAG); preamble
enrichment; comment-letter attribution. Rationale for each in the ADRs.
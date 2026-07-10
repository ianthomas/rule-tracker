# CLAUDE.md — mssp-rule-lineage

Portfolio project: extract citation-verified knowledge objects and **computable decision
rules** from CMS Medicare Shared Savings Program (MSSP) rulemaking, and track each rule
through the regulatory lifecycle (existing rule → proposed rule → final rule).

Built by one person in ~20 focused hours. Scope discipline is a feature, not a constraint.

## The corpus (fixed — do not expand)

Three Federal Register documents, one rulemaking lineage:

| Stage    | FR Doc No.  | Published  | Citation           | Docket     |
|----------|-------------|------------|--------------------|------------|
| BASELINE | 2022-23873  | 2022-11-18 | 87 FR 69404–70700  | CMS-1770-F |
| PROPOSED | 2023-14624  | 2023-08-07 | 88 FR 52262–53197  | CMS-1784-P |
| FINAL    | 2023-24184  | 2023-11-16 | 88 FR 78818–       | CMS-1784-F |

Acquire via the Federal Register API, **XML only, never PDF**:
`https://www.federalregister.gov/api/v1/documents/{fr_doc_no}.json` → `full_text_xml_url`

Extraction scope: the MSSP preamble sections + the 42 CFR Part 425 amendatory/regulation
text ONLY. These are ~1,000-page omnibus rules; everything not MSSP/Part 425 is out of
scope and must be discarded at ingestion.

## Non-negotiable invariants

1. **Span integrity.** Every extracted object carries character-span offsets into a
   frozen, normalized source text. Normalization happens ONCE at ingestion; after a
   document's `.txt` artifact is written, it is immutable. Any code that re-normalizes,
   strips, or re-wraps text downstream of ingestion is a bug.
2. **Verification is code, not prompting.** No object enters the store unless its span
   verifies against the source (exact match, or rapidfuzz ≥ 95 → flagged `fuzzy`).
   Failures are rejected and logged, never silently repaired.
3. **Constrained rule schema.** The LLM never emits free-form logic. Rules are composed
   only from the closed operator vocabulary in `src/schemas.py`. If real text can't be
   represented, log it as a `representation_gap` — that's a finding, not a failure.
4. **Every LLM call is metered.** Model, tokens, cost, latency logged per call to
   `runs/`. The cost/quality tradeoff table is a first-class deliverable.
5. **No orchestration frameworks.** Plain Python. `docs/decisions/ADR-004` explains why;
   do not add LangChain/ADK/etc. without a superseding ADR.
6. **The golden set is human-adjudicated.** The agent may DRAFT candidate labels, but
   every golden label and rule test case is confirmed or corrected by the human before
   it counts. A model grading its own homework is not an eval. Adjudication happens at
   the Phase 2 review gate.
7. **LLM calls are cached and capped.** Extraction/judge calls are cached on
   `hash(model + prompt_version + input_text)` in `cache/` — re-runs after code-only
   changes must be free. A hard per-run spend cap lives in `src/config.py`
   (default $5); the agent stops and surfaces a decision if a run would exceed it.

## Workflow: agent execution + human review gates

This project runs as an **agent-work / human-review loop**. The agent (Claude Code)
does the maximum possible work autonomously within a phase; the human's time is spent
only on (a) manual integration tests requiring judgment, and (b) decisions. The unit
of handoff is the **review package**. Current state lives in `docs/STATUS.md`.

### Phase lifecycle

1. **Entry.** Read the phase doc, the previous phase's review response
   (`docs/review/phase-{N-1}-response.md`), and the previous retro. Confirm entry
   criteria. Set STATUS to `in progress`.
2. **Execute.** Build the phase's tasks. Alongside implementation, the agent MUST:
   - Write **unit tests** for all deterministic logic (parsers, verifiers, evaluator,
     renderers, diff/classification code) and run them (`make test`).
   - Define **integration tests**, split explicitly into:
     - `automated/` — runnable without human judgment (pipeline produces expected
       artifact shapes, idempotence checks, golden-set metrics above floors). Agent
       runs these and records results.
     - `manual/` — checks requiring human judgment (extraction quality eyeballing,
       span spot-checks against source text, demo output sanity). Agent does NOT run
       these; it scripts them so each takes ≤5 minutes: exact command, what to look
       at, what "pass" looks like.
   Integration test definitions live in `tests/integration/phase-N/` with a
   `MANUAL.md` per phase.
3. **Retrospective.** Write `docs/retrospectives/phase-N-retro.md` from the template.
4. **Review package.** Write `docs/review/phase-N-package.md` from
   `docs/review/PACKAGE-TEMPLATE.md`. This is the ONLY document the human is required
   to read; it must be self-sufficient and honest. It links (not duplicates) the retro,
   test outputs, and artifacts, and it enumerates **decisions needed** — each with
   options, the agent's recommendation, and a default that applies if the human just
   writes "defaults."
4b. **Fresh-context self-review.** Before submitting, the package is reviewed in a
   CLEARED context (`/clear`, or a subagent given only the package + linked artifacts)
   playing skeptical reviewer: unclear claims, numbers without evidence links, manual
   tests that would take longer than estimated, decisions missing defaults. Fix what
   it finds, note in the package footer that self-review ran.
5. **Stop.** Set STATUS to `awaiting human review`. Commit
   (`phase-N: review package submitted`). Do not write code for phase N+1. Do not
   modify the submitted package afterward — corrections go in an addendum file.
6. **Human review (Ian).** Runs `MANUAL.md`, reads the package, writes
   `docs/review/phase-N-response.md` from `docs/review/RESPONSE-TEMPLATE.md`:
   manual test results, decisions, scope adjustments, approval or rework request.
   Commits it. This document is the sole authorization to proceed.
7. **Next phase entry** begins by parsing that response: decisions become config/ADRs,
   rework items become the first tasks, then proceed per step 1.

### Rules

- **Rework loop:** if the response requests rework, the agent fixes, re-runs affected
  tests, and submits `phase-N-package-v2.md` (previous package untouched). STATUS
  returns to `awaiting human review`.
- **Blocked mid-phase:** if a genuine decision blocker arises mid-phase, don't stall —
  take the most reversible option, record it as a `provisional decision` in the review
  package's decisions table, and continue. The human confirms or reverses at the gate.
- **Scope pressure:** cut inside the phase using its "cuttable" list rather than
  borrowing hours; record cuts in the retro AND surface them in the package under
  "what changed vs. plan."
- **Decisions:** anything you'd have to explain in an interview gets an ADR in
  `docs/decisions/`. Human decisions from review responses that are architectural get
  turned into ADRs by the agent at next-phase entry, citing the response doc.
- **Budget accounting:** agent hours and human review time tracked separately in
  STATUS. The design goal is human time ≤ 30 min per gate; if a package would need
  more, the package (not the human) is wrong — tighten it.
- **Branch per phase, tag per package.** Work happens on `phase-N`; submitting a
  package tags `phase-N-pkg` (rework: `phase-N-pkg-v2`). The human's APPROVED
  response is what merges `phase-N` → `main`. Never commit phase work directly to
  main.
- **One session per phase.** Each phase starts in a fresh Claude Code session; the
  docs (previous retro + response) are the memory, not the context window. Do not
  carry a session across a review gate.
- **Harvest talking points continuously.** At every retro, append 2–4 bullets to
  `docs/TALKING-POINTS.md`: the surprising finding, a tradeoff with numbers, a
  failure and its fix. This file is the interview-prep deliverable; Phase 4 polishes
  it rather than creating it.

## Conventions

- Python ≥3.11, `uv` for env/deps, `pydantic` v2 for all schemas, `pytest`, `ruff`.
- Anthropic API direct (`anthropic` SDK). Default model: Haiku 4.5. Comparison model
  for the eval matrix: Sonnet 4.6. Never hardcode model strings outside `src/config.py`.
- **Prompts are code.** Every prompt lives in `prompts/*.md` with a version header;
  no inline prompt strings in `src/`. Every scorecard and extraction run records
  `prompt_hash + model + corpus_hash` so any number is reproducible. Prompt edits
  get a one-line changelog entry at the top of the prompt file.
- Layout:
  ```
  src/            ingestion, extraction, verification, rules, lineage, eval
  corpus/         raw XML + frozen normalized .txt + section manifests (gitignored raw)
  golden/         hand-labeled golden set + rule test cases (committed)
  runs/           eval scorecards, cost logs, test outputs (committed, small JSON/MD)
  tests/          unit/ + integration/phase-N/{automated tests, MANUAL.md}
  prompts/        versioned prompt files (see "Prompts are code")
  cache/          LLM call cache, keyed on model+prompt_version+input (gitignored)
  docs/           SPEC, phases, retrospectives, decisions, review, STATUS,
                  TALKING-POINTS.md (see below)
  ```
- CLI over UI. `make ingest`, `make extract`, `make eval`, `make lineage` are the
  demo surface. No frontend.
- Commit style: small, phase-prefixed (`phase-2: add groundedness metric`).

## What this project is optimizing for

An interview narrative: "citations verified by code, not trusted from the model; logic
extracted into an executable schema with leaf-level citations; an eval harness that
prices the cost/quality tradeoff; rule lineage across the notice-and-comment lifecycle."
When in doubt, prefer the choice that strengthens that narrative over the choice that
adds features. The README and `runs/` scorecard are the product; the code is evidence.

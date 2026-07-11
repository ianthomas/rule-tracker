# STATUS

Total agent budget: 20 focused hours. Human review target: ≤30 min per gate.
Update at every state transition.

| Phase | Name                        | Agent budget | Agent actual | Human review | State       |
|-------|-----------------------------|--------------|--------------|--------------|-------------|
| 0     | Scaffold + ingestion        | 3h           | ~3h          | ~20 min      | approved    |
| 1     | Extraction + verification   | 6h           | –            | –            | not started |
| 2     | Eval harness                | 5h           | –            | –            | not started |
| 3     | Lineage across the triplet  | 4h           | –            | –            | not started |
| 4     | README, ADRs, demo polish   | 2h           | –            | –            | not started |

Valid states: `not started` → `in progress` → `awaiting human review`
→ (`rework` → `awaiting human review`)* → `approved`

Current phase: 0 approved (merged to main); phase 1 not started
Last package submitted: docs/review/phase-0-package.md (2026-07-10, tag phase-0-pkg; addendum 1 on 2026-07-11)
Last response received: docs/review/phase-0-response.md (2026-07-11, APPROVED)

Gate rule: a phase is `approved` only when docs/review/phase-N-response.md exists
with an APPROVED verdict. The agent may not enter phase N+1 before that. See
CLAUDE.md → Workflow.

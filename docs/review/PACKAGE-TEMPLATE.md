# Phase {N} Review Package — {phase name}

**Submitted:** {date} · **Agent hours:** {X} of {budget} · **STATUS:** awaiting human review
**Estimated human review time:** {≤30 min target — state actual estimate}

---

## 1. Headline (read this even if you read nothing else)

3–5 sentences: what was built, whether it works, the one number that matters this
phase, and the single most important thing needing your judgment.

## 2. Test results

### Unit tests
`make test` → {N passed / N failed / coverage note}. Full output: `runs/phase-{N}/unit.txt`

### Automated integration tests
| Test | Result | Evidence |
|------|--------|----------|
| {name — one line on what it proves} | ✅/❌ | path |

Failures, if any, each get one paragraph: why it fails, whether it blocks, agent's plan.

## 3. Manual integration tests — YOUR ACTION (est. {X} min total)

Run `tests/integration/phase-{N}/MANUAL.md`. Summary of what's there:

| # | Check | Command | You're judging | Est. |
|---|-------|---------|----------------|------|
| M1 | {e.g. span spot-check} | `make spotcheck N=5` | do the 5 quoted spans read as faithful citations of the source? | 5 min |

Record results in your response doc. Every manual test states what "pass" looks like.

## 4. Decisions needed — YOUR ACTION

Each decision: options, recommendation, and a **default**. Reply "defaults" to accept
all recommendations; otherwise answer by ID.

### D{N}.1 — {short title}
- **Question:** ...
- **Options:** (a) ... (b) ... (c) ...
- **Agent recommends:** (b), because ...
- **Default if unaddressed:** (b)
- **Reversibility:** cheap / moderate / expensive to change later

*(Provisional decisions already taken mid-phase appear here marked `provisional`,
with what it would cost to reverse.)*

## 5. What changed vs. plan

Scope cuts, budget deltas, surprises — one line each, linking the retro
(`docs/retrospectives/phase-{N}-retro.md`) for detail. No surprises hidden here;
this section being empty and wrong is the worst failure mode of the package.

## 6. Artifacts for optional deeper review

- Retro: `docs/retrospectives/phase-{N}-retro.md`
- Key outputs: {paths — scorecard, extracted objects sample, lineage table...}
- Notable code (only if worth human eyes): {path + why}

## 7. Next phase preview

2–3 sentences: what phase {N+1} does with this, and how today's decisions shape it.

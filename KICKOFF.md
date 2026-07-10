# Kickoff — agent/human review loop

## Zero-time setup (once, ~10 min, before session 1)

1. **Permissions:** `.claude/settings.json` pre-authorizes test/build/git/FR-API
   commands and denies `git push` / `rm -rf`. Review it once so the agent never
   stalls on confirmation prompts mid-phase. Adjust to taste.
2. **Spend cap:** set `ANTHROPIC_API_KEY` in `.env`; the per-run cap defaults to $5
   in `src/config.py` (agent creates it in Phase 0).
3. **Git:** `git init && git add -A && git commit -m "scaffold"` on `main`.

## Session 1 — start Phase 0 (paste into Claude Code from repo root)

---

Read CLAUDE.md, docs/SPEC.md, docs/STATUS.md, docs/phases/phase-0-ingestion.md, and
docs/review/PACKAGE-TEMPLATE.md in full before writing any code.

Create branch `phase-0` and execute Phase 0 under the workflow in CLAUDE.md ("agent
execution + human review gates"): build the phase tasks, write and run unit tests,
implement and run the automated integration tests, script the manual integration
tests into tests/integration/phase-0/MANUAL.md exactly as specified in the phase
doc, write the retrospective (including the talking-points harvest), then assemble
docs/review/phase-0-package.md.

Before submitting: run the fresh-context self-review from CLAUDE.md step 4b — clear
context or spawn a subagent that sees only the package and its linked artifacts, and
have it attack the package as a skeptical reviewer. Fix findings. Then tag
`phase-0-pkg`, set STATUS to awaiting human review, commit, and STOP. Do not begin
Phase 1 work in any form.

Budget pressure → apply the phase's "cuttable" list and surface cuts in the package.
Decision blockers → take the most reversible option, mark it `provisional`, keep
moving. The review package is the only document I'm guaranteed to read — make it
self-sufficient, honest, and reviewable in under 30 minutes including manual tests.

---

## Your review turn (each gate)

1. Read `docs/review/phase-N-package.md` (headline → tests → decisions).
2. Run `tests/integration/phase-N/MANUAL.md`. (Phase 2 note: M0 `make adjudicate`
   is the golden-set adjudication — final metrics only exist after you do it.)
3. Copy `docs/review/RESPONSE-TEMPLATE.md` → `docs/review/phase-N-response.md`,
   fill it ("defaults" is a valid decisions answer), set verdict, commit.
4. On APPROVED: merge `phase-N` → `main`.

## Session N+1 — after your approval (fresh Claude Code session)

---

Read docs/review/phase-{N}-response.md, docs/retrospectives/phase-{N}-retro.md,
docs/STATUS.md, and docs/phases/phase-{N+1}-*.md.

First apply my response: convert architectural decisions into ADRs citing the
response doc, and execute rework items before new work. Then create branch
phase-{N+1} and execute the phase under the same workflow — tests, MANUAL.md, retro
with talking-points harvest, package, fresh-context self-review, tag, STOP.

---

## Rework (verdict was REWORK REQUIRED)

---

Read docs/review/phase-{N}-response.md. On branch phase-{N}, execute the rework
items only, re-run affected tests, and submit docs/review/phase-{N}-package-v2.md
(original package untouched). Tag phase-{N}-pkg-v2. STOP.

---

## Why one session per phase

The docs are the memory: each session starts from the previous retro + your
response, not from a stale context window. Never carry a session across a gate.

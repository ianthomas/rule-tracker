# Phase 0 Review Package — Scaffold + Ingestion

**Submitted:** 2026-07-10 · **Agent hours:** ~2 of 3 · **STATUS:** awaiting human review
**Estimated human review time:** ~15 min total (8 min manual tests + 7 min reading)

---

## 1. Headline (read this even if you read nothing else)

The project skeleton and ingestion pipeline are built, and all three FR documents are
ingested into frozen, span-stable artifacts: **163 sections captured (19 preamble,
144 regtext Part 425), ~3.0M chars, 0 heading-slice violations, byte-identical on
re-ingest**. The one number that matters: the proposed rule initially yielded **0**
regtext sections because `PRORULE` XML has no `<REGTEXT>` wrapper at all — the parser
now handles both layouts through one shared grouping path, and the fix is covered by
synthetic-XML unit tests for each layout. Your judgment is needed on the two scripted
manual eyeball checks and three decisions (all with defaults) — two are low-stakes;
**D0.2 is a corpus-integrity call** (synthesized heading lines injected into the
frozen text) and deserves the extra minute.

## 2. Test results

### Unit tests
`make test` → **36 passed, 0 failed** (unit + automated integration together).
Full output: `runs/phase-0/unit.txt`. `make lint` (ruff) clean: `runs/phase-0/lint.txt`.

### Automated integration tests
| Test | Result | Evidence |
|------|--------|----------|
| Artifacts exist + manifest shape valid for all 3 docs | ✅ | `tests/integration/phase-0/test_corpus_artifacts.py` |
| text.txt sha256 matches hash recorded at ingestion (freeze intact) | ✅ | `test_text_hash_matches_manifest` |
| ≥1 Part 425 regtext block per doc (exit criterion) | ✅ | `test_at_least_one_part_425_regtext`; counts (57/44/43 blocks, 36/26/26 distinct § refs) printed in `runs/phase-0/ingest.txt` |
| Every manifest range slices to a block whose first line == heading | ✅ | 0 violations / 163 sections |
| Re-parsing raw.xml reproduces text.txt byte-identically (idempotence) | ✅ | `test_ingest_idempotent` |
| No XML debris in normalized text | ✅ | `test_no_xml_debris` |

No failures.

## 3. Manual integration tests — YOUR ACTION (est. 8 min total)

Run `tests/integration/phase-0/MANUAL.md`. Summary:

| # | Check | Command | You're judging | Est. |
|---|-------|---------|----------------|------|
| M1 | MSSP capture sanity | `make inspect DOC=<each of 3>` | presence (MSSP preamble chapter + § 425.x sections per doc) and purity (no other CFR parts / PFS topics). A deeper FR-site TOC audit is optional and separately estimated in MANUAL.md | 5 min |
| M2 | Text quality | `make spotcheck` | 3 seeded 500-char windows per doc: no tag debris, no mid-word breaks, sane paragraphing | 3 min |

MANUAL.md states exactly what pass and fail look like for each. Record results in
your response doc.

## 4. Decisions needed — YOUR ACTION

Reply "defaults" to accept all recommendations; otherwise answer by ID.

### D0.1 — Preamble capture granularity `provisional`
- **Question:** MSSP preamble is captured as a few large blocks rather than one
  entry per HD3 subsection — the baseline's "G. Medicare Shared Savings Program"
  chapter is a single 1.36M-char section (of the doc's 1.49M chars total). Fine
  for Phase 3 lineage context, or split finer now?
- **Options:** (a) keep coarse blocks; (b) split preamble per HD3 subsection.
- **Agent recommends:** (a) — preamble is context-only (SPEC §3); extraction targets
  regtext. Splitting later is cheap: re-run ingestion with a flag, since raw.xml is
  cached and text.txt would be regenerated deliberately at a phase boundary.
- **Default if unaddressed:** (a)
- **Reversibility:** cheap (re-ingest before Phase 1 extraction begins; expensive
  after spans exist).

### D0.2 — Synthesized headings for amendatory-instruction groups `provisional`
- **Question:** AMDPAR instruction runs ("87. Section 425.106 is amended by…") get a
  synthesized heading line (`PART 425… — amendatory instructions`) injected into the
  frozen text so the heading==first-line invariant holds. OK?
- **Options:** (a) keep synthesized headings; (b) leave AMDPAR runs headerless and
  drop the invariant for them.
- **Agent recommends:** (a) — one uniform invariant beats special cases; the injected
  line is clearly a label, and spans still verify against the frozen text.
- **Corpus-integrity note (be aware before deciding):** these lines are text CMS
  never published, sitting inside the artifact that citations verify against.
  Nothing currently *prevents* a Phase 1 span from landing on one. Mitigation
  committed to under default (a): synthesized lines are exactly identifiable —
  they are the `heading` of manifest entries whose heading ends in
  `— amendatory instructions` — and Phase 1's span verifier will reject
  extraction spans that overlap a synthesized heading line.
- **Default if unaddressed:** (a) with the mitigation above
- **Reversibility:** moderate (changes frozen bytes → requires deliberate re-ingest).

### D0.3 — Toolchain installs on this machine `provisional` (already done)
- **What happened:** the machine had no uv, no make, no Python ≥3.11 on PATH.
  Installed uv 0.11.28 (official installer) and GNU make 4.4.1 (ezwinports) into
  `C:\Users\VR\.local\bin`; created `~/.bashrc`/`~/.bash_profile` exporting it.
  Also set repo-local git identity and added `.gitattributes` (`corpus/** -text`)
  to stop Windows CRLF conversion from silently corrupting span offsets.
- **Options:** (a) accept; (b) tell me what to change.
- **Default if unaddressed:** (a)
- **Reversibility:** cheap (delete two binaries + dotfiles).

## 5. What changed vs. plan

- **PRORULE layout fork** (~30 min): proposed rule has no REGTEXT; parser now
  handles RULE and PRORULE layouts via one shared grouping function. Detail in
  `docs/retrospectives/phase-0-retro.md`.
- **Environment setup** (~20 min, unplanned): entry criteria assumed a uv env
  existed; see D0.3.
- **No scope cuts** — preamble capture and the inspect command both shipped.
- Finding worth knowing for later phases: **amendatory text is fragmentary** —
  a revised section appears as only its changed paragraphs plus `* * *`
  placeholders. Phase 1 extraction and Phase 3 lineage must not treat a section
  slice as the complete regulation.

## 6. Artifacts for optional deeper review

- Retro: `docs/retrospectives/phase-0-retro.md`
- Frozen corpus: `corpus/{2022-23873,2023-14624,2023-24184}/{text.txt,sections.json}`
- Test evidence: `runs/phase-0/unit.txt`, `runs/phase-0/ingest.txt`
- Notable code: `src/ingest/sections.py` — the dual-layout fork + freeze guard
  (the module docstring documents the two XML layouts; ADR-worthy comment per the
  phase doc's instruction)

## 7. Next phase preview

Phase 1 (extraction + verification, 6h) prompts over the 144 regtext sections using
`sections.json` offsets as anchors, emitting knowledge objects and predicates whose
spans are verified by code against these frozen artifacts. D0.1/D0.2 shape the
section inputs the extractor sees; approving the defaults means Phase 1 starts
directly on the committed corpus with no re-ingestion.

---

*Footer: fresh-context self-review ran before submission (step 4b) — a subagent
given only this package + linked artifacts returned 7 findings (0 blockers,
4 should-fix, 3 nits: unverifiable §-ref evidence, M1 estimate vs. scope,
a mojibake false-failure hazard in M2, D0.2 framing, and wording/evidence nits).
All were fixed in place before this submission.*

# Phase 0 — Manual Integration Tests

Total estimated time: **≤ 8 minutes**. Run from the repo root. Record results
in `docs/review/phase-0-response.md`.

> Prerequisite: `make ingest` has been run (the agent already ran it; artifacts
> are committed under `corpus/`).

---

## M1 — MSSP capture sanity (~5 min)

**Command (run one at a time):**

```
make inspect DOC=2022-23873
make inspect DOC=2023-14624
make inspect DOC=2023-24184
```

**What to look at:** the listing of section headings (preamble first, then
regtext). Compare against the document's table of contents on the FR website:

- BASELINE: https://www.federalregister.gov/documents/2022/11/18/2022-23873
- PROPOSED: https://www.federalregister.gov/documents/2023/08/07/2023-14624
- FINAL:    https://www.federalregister.gov/documents/2023/11/16/2023-24184

**Pass looks like:**

- Preamble headings are MSSP material: a "Medicare Shared Savings Program"
  main section plus small MSSP subsections from the ICR/RIA parts.
- Regtext headings are `§ 425.xxx ...` sections and
  `PART 425 ... amendatory instructions` groups — nothing from other CFR parts
  (no § 414.x, § 410.x, etc.).
- Nothing obviously MSSP-related in the FR site's TOC is missing from the
  preamble list. (Judgment call: minor sub-headings are inside their parent
  section's text, not separate manifest entries — that's expected.)

**Fail looks like:** headings about drug pricing / telehealth / other PFS
topics appearing as sections; or an MSSP chapter visible on the FR site with
no corresponding captured section.

---

## M2 — Text quality spot-check (~3 min)

**Command:**

```
make spotcheck
```

(Prints 3 deterministic pseudo-random 500-char windows per document; re-runs
show the same windows.)

**Pass looks like:**

- Prose reads cleanly: no XML tags, no `&amp;`-style entities, no mid-word
  breaks or run-together words.
- Paragraphs separated by blank lines; regulatory text markers like
  `(c) * * *` and `§ 425.xxx` render correctly.

**Fail looks like:** tag debris (`<P>`, `</E>`), words jammed together
(`beneficiaryassignment`), garbled characters (`Â§`, `â€”`), or windows that
are mostly table-cell soup (a single messy table window is tolerable — flag
it in the response rather than failing outright).

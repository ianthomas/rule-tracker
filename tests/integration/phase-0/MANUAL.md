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
regtext). This is a **presence + purity** check, scoped to 5 minutes:

**Pass looks like:**

1. **Presence:** each doc has a "Medicare Shared Savings Program" preamble
   section (the main chapter) and a list of `§ 425.xxx ...` regtext sections.
2. **Purity:** nothing from other CFR parts or other PFS topics — no § 414.x /
   § 410.x headings, no drug pricing / telehealth sections.
3. (Judgment call: MSSP sub-headings live inside their parent section's text,
   not as separate manifest entries — that's expected.)

**Fail looks like:** headings about other PFS topics appearing as sections, or
a doc with no MSSP preamble section / no § 425.x regtext sections at all.

*Optional deeper audit (NOT in the 5-min estimate):* compare the preamble list
against the MSSP portions of the documents' TOCs on the FR website —
2022-23873 / 2023-14624 / 2023-24184 at federalregister.gov/documents/. Doing
this honestly for three ~1,000-page omnibus rules takes 10–15 extra minutes;
skip it or sample one document unless something in the 5-min check looks off.

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

> Encoding caveat: the CLIs force UTF-8 output. If your *terminal* still shows
> `Â§` where `§` should be, that's the terminal's codepage, not the data —
> confirm by opening `corpus/<doc>/text.txt` in an editor (it is UTF-8) before
> recording a failure.

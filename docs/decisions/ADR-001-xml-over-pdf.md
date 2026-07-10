# ADR-001: Ingest Federal Register XML, not PDF

**Status:** accepted · **Date:** project start · **Phase:** 0

## Context
The three corpus documents are 900–1,300 page two-column PDFs (one exceeds 20MB).
The whole architecture depends on stable character-span offsets; PDF text extraction
introduces page-break artifacts, column-order errors, and hyphenation noise that
would silently corrupt spans and poison the verification layer.

## Decision
Acquire official full-text XML via the Federal Register API
(`/api/v1/documents/{doc}.json` → `full_text_xml_url`) and never touch the PDFs.

## Alternatives considered
- PDF + pdfplumber/pypdf: hours of cleanup, fragile offsets. Rejected.
- GovInfo bulk-issue XML: works, but per-document API is simpler and self-documenting.

## Consequences
Free structural segmentation (headings, regtext markup); reproducible ingestion;
dependence on FR API availability (mitigated by caching raw XML in the repo's
gitignored corpus dir). Content-acquisition judgment worth stating in the README.

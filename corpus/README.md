# Corpus

Raw XML and frozen normalized text live here, produced by `make ingest`.
`raw.xml` files are gitignored (large); `text.txt` + `sections.json` are committed
because span offsets in the golden set depend on these exact bytes.

| Stage    | FR Doc No. | API                                                              |
|----------|------------|------------------------------------------------------------------|
| BASELINE | 2022-23873 | https://www.federalregister.gov/api/v1/documents/2022-23873.json |
| PROPOSED | 2023-14624 | https://www.federalregister.gov/api/v1/documents/2023-14624.json |
| FINAL    | 2023-24184 | https://www.federalregister.gov/api/v1/documents/2023-24184.json |

NEVER regenerate text.txt after golden labeling has begun without re-verifying
every golden span. See CLAUDE.md invariant 1.

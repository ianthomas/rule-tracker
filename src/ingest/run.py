"""`make ingest` entry point: fetch + parse + freeze all three corpus documents."""

import sys

from src import config
from src.ingest.fetch import fetch
from src.ingest.sections import ingest_doc

# Force UTF-8 output so redirected logs (runs/) don't render § as mojibake.
sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    for fr_doc_no, spec in config.DOCS.items():
        print(f"[{spec.stage}] {fr_doc_no} ({spec.citation}, {spec.docket})")
        raw = fetch(fr_doc_no)
        print(f"  raw.xml: {raw.stat().st_size:,} bytes")
        summary = ingest_doc(fr_doc_no)
        frozen = "written" if summary["wrote_text"] else "unchanged (frozen)"
        print(
            f"  sections: {summary['sections']} "
            f"({summary['preamble']} preamble, {summary['regtext']} regtext, "
            f"{summary['distinct_cfr_refs']} distinct § 425.x refs), "
            f"text.txt: {summary['chars']:,} chars [{frozen}]"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

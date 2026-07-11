"""`make spotcheck [DOC=...]`: print 3 seeded-random 500-char windows per doc.

Human eyeball check for text quality (manual test M2): no XML tag debris,
no mid-word breaks, sane paragraphing. Windows are seeded on the doc id so
re-runs show the same excerpts.
"""

import random
import sys

from src import config

# The corpus is UTF-8 (§, —). Force UTF-8 output so redirected/piped runs on
# Windows don't render mojibake that looks like a data problem (manual test M2).
sys.stdout.reconfigure(encoding="utf-8")

WINDOWS = 3
WINDOW_CHARS = 500


def spotcheck(fr_doc_no: str) -> None:
    text = (config.CORPUS_DIR / fr_doc_no / "text.txt").read_text(encoding="utf-8")
    rng = random.Random(fr_doc_no)  # deterministic per doc
    print(f"=== {fr_doc_no} ({config.DOCS[fr_doc_no].stage}) — {len(text):,} chars ===")
    for i in range(WINDOWS):
        start = rng.randrange(0, max(1, len(text) - WINDOW_CHARS))
        window = text[start : start + WINDOW_CHARS]
        print(f"\n--- window {i + 1} @ chars {start}..{start + WINDOW_CHARS} ---")
        print(window)
    print()


def main() -> int:
    args = sys.argv[1:]
    docs = args if args else list(config.DOCS)
    for d in docs:
        spotcheck(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())

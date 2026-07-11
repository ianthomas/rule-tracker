"""`make inspect DOC=<fr_doc_no>`: print section headings + first 200 chars of each.

Human eyeball check that MSSP content is actually captured (manual test M1).
"""

import json
import sys

from src import config

# The corpus is UTF-8 (§, —). Force UTF-8 output so redirected/piped runs on
# Windows don't render mojibake that looks like a data problem (manual test M2).
sys.stdout.reconfigure(encoding="utf-8")


def inspect(fr_doc_no: str) -> None:
    ddir = config.CORPUS_DIR / fr_doc_no
    manifest = json.loads((ddir / "sections.json").read_text(encoding="utf-8"))
    text = (ddir / "text.txt").read_text(encoding="utf-8")

    spec = config.DOCS[fr_doc_no]
    print(f"=== {fr_doc_no} [{spec.stage}] {spec.citation} ({spec.docket}) ===")
    print(f"{len(manifest['sections'])} sections, {len(text):,} chars\n")
    for e in manifest["sections"]:
        body = text[e["start"] : e["end"]]
        preview = body[len(e["heading"]) :].strip().replace("\n", " ")[:200]
        refs = f"  [{', '.join(e['cfr_refs'])}]" if e.get("cfr_refs") else ""
        print(f"--- {e['section_id']} ({e['kind']}) {e['heading'][:100]}{refs}")
        print(f"    {preview}\n")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: make inspect DOC=<fr_doc_no>", file=sys.stderr)
        print(f"known docs: {', '.join(config.DOCS)}", file=sys.stderr)
        return 2
    inspect(args[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())

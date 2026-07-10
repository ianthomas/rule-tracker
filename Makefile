# Demo surface (see CLAUDE.md): make ingest / extract / eval / lineage
# Phase 0 provides: ingest, inspect, spotcheck, test, lint

.PHONY: ingest inspect spotcheck test lint

ingest:
	uv run python -m src.ingest.run

# Usage: make inspect DOC=2022-23873
inspect:
	uv run python -m src.ingest.inspect $(DOC)

# Usage: make spotcheck DOC=2022-23873  (or omit DOC for all three)
spotcheck:
	uv run python -m src.ingest.spotcheck $(DOC)

test:
	uv run pytest -q

lint:
	uv run ruff check src tests

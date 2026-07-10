# ADR-003: Closed-vocabulary rule schema; LLM never emits free-form logic

**Status:** accepted · **Date:** project start · **Phase:** 1

## Context
The project's thesis is verification-by-code. Free-form logic output (Python
snippets, pseudo-code, arbitrary JSON Logic) cannot be span-verified, executed
safely, or diffed deterministically.

## Decision
Rules are boolean trees over typed Predicates with a 7-operator closed vocabulary
(EQ, NEQ, IN_RANGE, GTE, LTE, PRESENT, ABSENT). Pass 2 composes trees referencing
verified atoms by ID only. Unrepresentable text is logged as a representation_gap.

## Alternatives considered
- JSON Logic / OPA-Rego: heavier than needed; obscures the leaf-level citation story.
- Direct text→code generation: unverifiable; rejected on thesis grounds.

## Consequences
One schema serves as extraction target, storage format, and executable form.
Representation gaps become a reportable finding rather than silent failure.
Vocabulary growth requires a superseding ADR (guards against schema sprawl).

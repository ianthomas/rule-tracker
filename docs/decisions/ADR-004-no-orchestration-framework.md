# ADR-004: Plain Python; no LangChain/ADK/agent framework

**Status:** accepted · **Date:** project start · **Phase:** 1

## Context
The JD this project targets name-drops Google ADK and LangChain. The pipeline is a
fixed two-pass DAG over ~150 pages of text with one retry policy — there is no
dynamic tool selection, no branching agent behavior, no multi-turn state.

## Decision
Direct Anthropic SDK calls behind one metered wrapper (src/llm.py). No framework.

## Alternatives considered
- Adopting LangChain "for the resume": adds dependency surface and debugging
  indirection while demonstrating nothing the JD actually tests. The stronger
  interview answer is articulating WHEN a framework earns its complexity
  (dynamic tool routing, multi-agent state, provider abstraction at org scale).

## Consequences
Every LLM interaction visible and metered in one file; cost/latency accounting
trivial. README roadmap includes the framework-adoption threshold explicitly.

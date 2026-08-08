# AI Agent Memory Strategies: A Decision-Tree Approach

Summary of "Choosing the Right AI Agent Memory Strategy: A Decision Tree Approach" (machinelearningmastery.com, 2026).
Source: https://machinelearningmastery.com/choosing-the-right-ai-agent-memory-strategy-a-decision-tree-approach/

## Core thesis

Effective agent memory design means categorizing information, not picking one storage system for everything. The choice of memory tooling matters less than deciding where each category of information should live. Balance persistence, retrieval cost, and stability across four memory layers.

## The decision tree

1. Does this information need to persist beyond the current turn?
   - No: keep it in the context window only.
   - Yes: continue.
2. Does it need to survive beyond a single session?
   - Within-session only: working memory.
   - Beyond the session: continue.
3. Is it a stable fact or an evolving event?
   - Stable fact: semantic memory.
   - Evolving event: episodic memory.
4. How will it be retrieved?
   - Small bounded store: full read at session start.
   - Large searchable store: semantic or similarity search.
5. Does the agent need reusable procedures?
   - Recurring task patterns: add a procedural memory layer.
   - One-off tasks: skip.

## The four memory types

| Type | What it holds | When to use |
|---|---|---|
| Working | Current-session information within the token budget | Everything relevant lives inside the active conversation |
| Semantic | Stable facts and domain knowledge | User preferences, business rules, project constraints |
| Episodic | History of past events and decisions | Agent needs context from past interactions |
| Procedural | Distilled, reusable routines | Recurring tasks the agent should get better at |

## Mapping to a Claude Code workflow

| Memory type | Concrete implementation |
|---|---|
| Working | Context-window hygiene: filtered tool output (rtk), progressive-disclosure search (qmd, codegraph), subagent delegation |
| Semantic | CLAUDE.md, AGENTS.md, BMAD artifacts (PRDs, architecture docs, stories), indexed for cheap retrieval |
| Episodic | Session handoff notes in the repo, or an automatic capture tool (claude-mem) |
| Procedural | Skills (SKILL.md): instructions loaded on demand instead of sitting in every prompt |

Key implication: BMAD already produces the semantic layer as a byproduct of normal work. The open design decisions are usually episodic (notes vs automatic capture) and retrieval (grep vs indexed search), not storage format.

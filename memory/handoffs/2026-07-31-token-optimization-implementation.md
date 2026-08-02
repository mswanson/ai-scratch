---
date: 2026-07-31
topic: Token Optimization framework, implementation phase
repos: [ai-scratch]
status: resolved
---

# Handoff: Token Optimization Implementation Phase

## Authoritative context (read first, do not re-derive)

- `docs/2026-07-31-token-optimization-framework-design.md`: the approved design. §9 is the implementation sequence this session executes. Supersedes the June master plan.
- `~/.claude/backups/2026-07-30-pre-cleanup/`: baseline.md and after-state.md (before/after harness state, Step 8 fresh-session verification checklist).
- `docs/templates/hub-CLAUDE.md`: hub template, ownership section verified against a real `_bmad` tree.
- `docs/claude_setup/`: work-computer configs and skills (uncommitted by choice; contains work material). Includes consolidate-memory and write-like-me skills.
- Key commits: d233973 (snapshot), d9f1e52 (cleanup/dedupe), 2bb83b8 + 869704f + 80e4bfd (design docs).

## State

- Cleanup Steps 1-7 done: new global CLAUDE.md live, plugins rescoped (6 global), skills deduped via symlinks (.agents/skills canonical), rtk excludes grep/rg (`~/Library/Application Support/rtk/config.toml`).
- Step 8 pending: user runs the fresh-session checklist in after-state.md; collect results before heavy work.
- Nothing from design §9 implementation has started.

## Next work (design §9 order)

1. Step 8 verification results from user.
2. qmd: install, collections for active hubs (ai-scratch now; lyceum-planning, marshal-planning when confirmed), `qmd context add` hierarchy, `--http --daemon` mode, register MCP. Embedder choice is a one-way door.
3. `codegraph init` on active spokes (ask user which; never init unprompted per CLAUDE.md).
4. Author `bmad-hub-setup` (instantiates the hub template; repairs bmad-* symlinks only, never project-owned skills; drift check) and `bmad-handoff` (destination memory/handoffs/, frontmatter, multi-repo state block). Extend consolidate-memory (handoff lifecycle, _bmad/_memory slice, staleness marker, MEMORY.md cap, date absolutization). All against /writing-great-skills.
5. Writing stack: concise-writing + edit-pass skills; review write-like-me for user-level install.
6. Work-skill placement decisions (auth0-*, todoist, review-file, dev-workflow) still owed by user.

## Constraints to honor

- BMAD files are installer-owned; module changes only via `npx bmad-method install`. `_bmad/custom/` and `config.user.toml` are the editable surface; `_bmad/_memory/` is read-only agent data.
- Suggest-table rows in global CLAUDE.md are added only when a skill is actually installed.
- BMAD Precedence: do not route this work through superpowers lifecycle skills; design is approved, go straight to implementation.
- Deferred ledger (design §11) is settled; do not re-open claude-mem, context-mode, headroom, caveman, etc.

## Open user inputs

Step 8 results; which spokes get codegraph; lyceum discord-repo confirmation (guessed lyceum/lyceum); dead-project purge list for ~/.claude.json; read-only allowlist decision (/fewer-permission-prompts available).

## Suggested skills

- /writing-great-skills before authoring bmad-hub-setup, bmad-handoff, or the consolidate-memory extension.
- /fewer-permission-prompts if the user wants the allowlist.
- superpowers:verification-before-completion at each implementation milestone.

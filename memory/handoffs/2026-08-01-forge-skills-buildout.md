---
date: 2026-08-01
topic: forge-skills buildout — remaining authoring, audit, and teardown
repos: [ai-scratch, forge-skills, dotfiles]
status: open
---

# Handoff: forge-skills buildout continuation

## Authoritative context

- `docs/2026-07-31-token-optimization-framework-design.md` — the framework design; §6 carries the narrowed namespace rule (forge-* = framework tooling only; personal skills natural names; never bmad-*) and the ownership layout rule; §8 the skill specs and completion records. Do not re-derive anything §11's deferred/retired ledger settles. Note its header: history was rewritten 2026-08-01, so shas cited in the doc may not resolve.
- `/Users/michaelswanson/Code/forge-skills` — canonical skills repo (remote: github.com/forge512/agent-skills, private). README carries the namespace rule, layout, test commands. CI: macOS-only runners (deliberate — BSD sed/bash 3.2 production fidelity), Claude PR reviewer authenticated via CLAUDE_CODE_OAUTH_TOKEN secret.
- `memory/handoffs/2026-07-31-token-optimization-implementation.md` — prior handoff (status open; its next-work items largely done — flip to resolved when consolidation lands).
- Session task list (harness): #6 forge-consolidate-memory, #7 forge-review-file, #9 dev-workflow audit, #10 teardown.
- `~/.claude/backups/2026-08-01-claude-setup-purge/` — pre-purge bundle + working-copy backup of docs/claude_setup.

## State

- ai-scratch: branch `bmad-loop-dev`, clean, pushed to mswanson/ai-scratch after a `git filter-repo` purge of `docs/claude_setup/` (work material committed by accident via a `git add -A` sweep; now gitignored on disk, restored from backup). `main` unchanged (e56820e).
- forge-skills: `main` clean and pushed. Live skills: forge-loop, forge-hub, forge-handoff, todoist, write-like-me (all wired through `~/.agents/skills` → `~/.claude/skills` chains); forge-review-file in repo but deliberately NOT wired (WIP). All test suites green (10+10+8 fixture scenarios + plugin tests).
- dotfiles (~/Code/dotfiles): statusline.sh checked in (c31cb7f); repo otherwise has pre-existing uncommitted changes not from this work; fork-handling overhaul deferred (design §11).
- qmd: collections ai-scratch-docs/-memory/-output + forge-skills; launchd daemon serving MCP user-scope.

## Next work

1. Task #6 — author `forge-consolidate-memory`: source `docs/claude_setup/consolidate-memory/SKILL.md`, fold `docs/claude_setup/memory-scout.md` in as the inventory-subagent reference, extend per design §8.3 (handoff lifecycle + `_archive/`, `_bmad/_memory` read-only slice, staleness marker cadence, MEMORY.md cap, date absolutization). Tests + evals per repo pattern; wire symlinks; update repo README.
2. Task #7 — refine `forge-review-file` into a real skill (SKILL.md, wire review.py flow, tests/evals), then wire symlinks and drop the WIP marker.
3. Task #9 — audit `docs/claude_setup/dev-workflow/` + ai-review-workflow.md + code-review-workflow.md + detect-ai-reviewers.sh + fetch-ai-review-comments.sh + metrics.js; design a generic forge-* dev-workflow (strip Jira/metrics.js work wiring).
4. Task #10 — teardown `docs/claude_setup/`: everything mined or adopted gets trashed (CLAUDE.md, CLAUDE 2.md, RTK.md, settings.json, session guides, todoist-workspace, statusline.sh, auto_allow_web_tools.py, memory-scout.md once folded, auth0-* — verified upstream in github.com/auth0/agent-skills as feature-branding/feature-custom-domains references). Keep dev-workflow set until #9 completes. workflow-writing-guide.md pending user verdict.
5. First real forge-hub Setup run on ai-scratch (CLAUDE.md instantiation with the forge-skills spoke row) — good capstone after #6/#7.

## Constraints to honor

- Namespace: forge-* only for framework tooling; personal skills natural names; never bmad-*; no bmad infix. Repo boundary = family identity.
- docs/claude_setup/ is gitignored — never re-commit it; history was purged to remove it.
- forge-review-file stays unwired until refined.
- bmad-loop pins: tool at tag v0.9.0; policy.toml is per-machine/gitignored; skill layout ownership rule per design §6.
- CI stays macos-latest (production fidelity); the Claude reviewer uses the subscription OAuth token.
- Commit/push forge-skills freely; ai-scratch pushes may hit the auto-mode classifier — hand to the user via `!` prefix when blocked.

## Open user inputs

- workflow-writing-guide.md keep/park verdict (file was sent for review 2026-08-01).
- Generic Pocock `handoff` skill: deactivate its symlink in favor of forge-handoff, or keep both (design §8.2 records the tradeoff).
- qmd collections for lyceum-planning / marshal-planning; codegraph init on which spokes.
- github plugin MCP auth (still failing; `/mcp` → authenticate, or drop at the §10 checkpoint).
- /fewer-permission-prompts run (Todoist reminder due 2026-08-02).

## Suggested skills

- superpowers:writing-skills before authoring forge-consolidate-memory (#6) and refining forge-review-file (#7).
- superpowers:verification-before-completion at each task's completion claim.
- forge-handoff again at the next boundary; flip this handoff to `resolved` when #6-#10 land.

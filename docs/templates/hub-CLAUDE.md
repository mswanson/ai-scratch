<!--
Template: BMAD planning-hub CLAUDE.md
Instantiated by /forge-hub. Replace every {{placeholder}}; delete any
section that does not apply. Do not duplicate global CLAUDE.md content here
(style, subagent models, search discipline, BMAD precedence, memory rules,
handoff behavior are all global). This file holds only what is specific to
this hub.
-->

# {{PROJECT_NAME}} Planning Hub

{{ONE_SENTENCE_DESCRIPTION}}. This repo is the BMAD planning hub: it owns planning artifacts, stories, and cross-repo knowledge. Code lives in the spoke repos below.

## Keeping This File Lean

Every line here costs tokens in every session. Configuration tables, conventions, and pointers only; detailed procedures live in `docs/` and are referenced from the Custom Workflows table. Before adding content here, check whether it belongs in a `docs/` file instead.

## Spoke Repositories

Symlinks in this repo point at code repos. Searches do not follow symlinks: always use the real path when searching, delegating, or spawning agents into spoke code. bmad-loop dev sessions run in worktrees on these repos.

| Symlink | Real path | What it is |
|---|---|---|
| {{SYMLINK_NAME}} | {{REAL_PATH}} | {{DESCRIPTION}} |

## Key Artifacts

| What | Where |
|---|---|
| PRD, architecture, epics | `_bmad-output/planning-artifacts/` |
| Stories and sprint status | `_bmad-output/{{STORIES_PATH}}` |
| Handoff notes | `memory/handoffs/` (hub-level, including for spoke work) |
| Project memory index | `memory/MEMORY.md` |

## Archived Content — Not Current

Files inside any `_archive/` or `archive/` folder are historical record only. Never cite them as current state, never use them to answer "what is the current X", and skip those paths when searching. If a live doc conflicts with an archived one, the live doc wins; the archived version was superseded for a reason.

## BMAD Framework Files — Do Not Modify

Installer-generated and replaced on install or upgrade; never edit directly: `bmad-*` skills (on repos running bmad-loop: real directories in every registered CLI tree — `.claude/skills`, `.agents/skills`, `.agent`; elsewhere they may be canonical in `.agents/skills` with `.claude/skills` symlinks), the module trees under `_bmad/` (`core/`, `bmm/`, etc.), `_bmad/scripts/`, `_bmad/_config/`, `_bmad/config.toml`, and every module `config.yaml` (all generated from installer answers).

Yours to edit: `_bmad/custom/` overrides (the customization surface below) and `_bmad/config.user.toml` for pinning config values. To change an install answer durably, re-run the installer; it remembers prior answers. Custom module trees (bmb-built, e.g. a project-specific module) are owned by their module source. Non-bmad skills in either skills tree are project-owned.

Runtime data, neither of the above: `_bmad/_memory/` is agent sidecar memory written by BMAD agents. Treat it as read-only in consolidation and cleanup passes; inventory it, never rewrite it.

Customization goes in `_bmad/custom/`:
- `_bmad/custom/<skill-name>.toml`: team overrides, committed
- `_bmad/custom/<skill-name>.user.toml`: personal overrides, gitignored
- Overrides are sparse: arrays append, scalars win. Author with the `bmad-customize` skill; verify with `python3 _bmad/scripts/resolve_customization.py --skill .claude/skills/<skill> --key workflow`.

**Active overrides in this hub** (document every one here):

| Override file | What it changes |
|---|---|
| {{OVERRIDE_FILE}} | {{OVERRIDE_SUMMARY}} |

## Agent Routing

- "implement / dev / build story X": invoke `{{DEV_ENTRYPOINT}}` <!-- bmad-agent-dev, or the bmad-loop run flow -->
- {{OTHER_PROJECT_ROUTING_RULES}}

## Custom Workflows

Project-specific workflow docs are authoritative and take precedence over generic BMAD skill behavior. Read the relevant file before performing any operation it covers.

| File | Purpose |
|---|---|
| {{DOC_PATH}} | {{DOC_PURPOSE}} |

## Permissions

Run `/fewer-permission-prompts` after the first few sessions in this hub, and again when tool patterns change; it keeps the project allowlist current so read-only commands stop prompting.

## Modules Installed

<!-- Keep in sync with _bmad/_config/manifest.yaml; module changes go through `npx bmad-method install` (Modify Install), never manual edits. -->
{{MODULE_LIST}} <!-- e.g. core, bmm, bmad-loop (stable channel) -->

# ai-scratch Planning Hub

Sandbox and authoring hub for the BMAD tooling and the token-optimization framework; planning happens here, implementation lands in the spokes. This repo is the BMAD planning hub: it owns planning artifacts, stories, and cross-repo knowledge. Code lives in the spoke repos below.

## Keeping This File Lean

Every line here costs tokens in every session. Configuration tables, conventions, and pointers only; detailed procedures live in `docs/` and are referenced from the Custom Workflows table. Before adding content here, check whether it belongs in a `docs/` file instead.

## Spoke Repositories

Symlinks in this repo point at code repos. Searches do not follow symlinks: always use the real path when searching, delegating, or spawning agents into spoke code. bmad-loop dev sessions run in worktrees on these repos.

| Symlink | Real path | What it is |
|---|---|---|
| dotfiles | /Users/michaelswanson/Code/dotfiles | macOS dotfiles (dotbot-managed); canonical home of `~/.claude` global config via dotbot symlinks |
| forge-skills | /Users/michaelswanson/Code/forge-skills | Personal skill library (verb-named user skills: implement-story, manage-planning-repos, …) |

Each spoke's implementation rules live in its own `docs/project-context.md` (generated, versioned with the code); read it before writing code in that spoke.

## Key Artifacts

| What | Where |
|---|---|
| PRD, architecture, epics | `_bmad-output/planning-artifacts/` |
| Stories and sprint status | `_bmad-output/implementation-artifacts/` |
| Handoff notes | `memory/handoffs/` (hub-level, including for spoke work) |
| Project memory index | `memory/MEMORY.md` |

## Archived Content — Not Current

Files inside any `_archive/` or `archive/` folder are historical record only. Never cite them as current state, never use them to answer "what is the current X", and skip those paths when searching. If a live doc conflicts with an archived one, the live doc wins; the archived version was superseded for a reason.

Archive to the repo-root `_archive/`, mirroring the original subpath (`_bmad-output/planning-artifacts/foo.md` → `_archive/planning-artifacts/foo.md`), never to an `_archive/` inside a qmd-indexed dir: qmd has no path exclusions, so anything archived inside a collection root stays in the search index forever. The repo-root `_archive/` sits outside every collection, and the next `qmd update` prunes moved files from the index — run `qmd update` as the final step of any archival. Until that reindex (or for `.RETIRED` markers kept in place), discount any qmd hit whose path contains `_archive/` or `.RETIRED`.

## BMAD Framework Files — Do Not Modify

Installer-generated and replaced on install or upgrade; never edit directly: `bmad-*` skills (on repos running bmad-loop: real directories in every registered CLI tree — `.claude/skills`, `.agents/skills`, `.agent`; elsewhere they may be canonical in `.agents/skills` with `.claude/skills` symlinks), the module trees under `_bmad/` (`core/`, `bmm/`, etc.), `_bmad/scripts/`, `_bmad/_config/`, `_bmad/config.toml`, and every module `config.yaml` (all generated from installer answers).

Yours to edit: `_bmad/custom/` overrides (the customization surface below) and `_bmad/config.user.toml` for pinning config values. To change an install answer durably, re-run the installer; it remembers prior answers. Custom module trees (bmb-built, e.g. a project-specific module) are owned by their module source. Non-bmad skills in either skills tree are project-owned.

Runtime data, neither of the above: `_bmad/_memory/` is agent sidecar memory written by BMAD agents. Treat it as read-only in consolidation and cleanup passes; inventory it, never rewrite it.

Customization goes in `_bmad/custom/`:

- `_bmad/custom/<skill-name>.toml`: team overrides, committed
- `_bmad/custom/<skill-name>.user.toml`: personal overrides, gitignored
- Overrides are sparse: arrays append, scalars win. Author with the `bmad-customize` skill; verify with `python3 _bmad/scripts/resolve_customization.py --skill .claude/skills/<skill> --key workflow`.
- Beyond overrides, a fully custom module is possible: a project-owned module tree with its own skills and workflows, built with bmb (`bmad-bmb-setup`). It installs alongside the stock modules and is owned by its module source, not the installer.

There are no active overrides in this hub; document every new override file here when one lands.

## Agent Routing

- "implement / dev / build story X": the bmad-loop run flow — invoke `operate-bmad-loop` (tool pinned at v0.9.1; see `memory/bmad-loop-pins.md`)

## Permissions

Run `/fewer-permission-prompts` after the first few sessions in this hub, and again when tool patterns change; it keeps the project allowlist current so read-only commands stop prompting.

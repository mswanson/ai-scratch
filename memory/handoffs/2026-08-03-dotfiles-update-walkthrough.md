---
date: 2026-08-03
topic: dotfiles update plan walkthrough
repos:
  - ai-scratch
  - dotfiles
status: open
---

# Dotfiles update plan walkthrough

## Authoritative context

Read these first; do not re-derive what they settle.

- `docs/2026-08-02-dotfiles-update-plan.md` — the working punch-list for the dotfiles spoke. Six sections; the walkthrough executes it top to bottom. This handoff only carries session state on top of it.
- `docs/2026-07-31-token-optimization-framework-design.md` §3, §5, §6 — authoritative for plan §4 (bootstrap of rtk/qmd/codegraph/MCP/skills chain).
- `memory/MEMORY.md` + the dotfiles-spoke context line — hub-and-spoke wiring, real-path rule, what `~/.claude` symlinks exist.
- dotfiles repo `main` at `9f17f74` (pushed, in sync with origin) — the 2026-08-01/02 cleanup commits; `git log` there is the record of what was already removed.

## State

- **dotfiles** (`/Users/michaelswanson/Code/dotfiles`): branch `main` at `9f17f74`, clean, pushed. Cleanup phase done (Okta removal, `_bmad` trashed, single tool-versions source, Claude config tracked + dotbot-linked, modernization guide archived). One old stash deliberately left; fate undecided.
- **ai-scratch** (hub): uncommitted changes — `dotfiles` spoke symlink at repo root, `memory/MEMORY.md` updates, `docs/2026-08-02-dotfiles-update-plan.md`, and this handoff.
- **Walkthrough position**: plan §1, decision 1 of 3 (Go: in or out) was presented with a recommendation of "out"; the user has not answered. No §1 decision has been made or executed. Sections 2–6 untouched.
- An earlier AskUserQuestion presenting all three §1 decisions was rejected by the user; walk through them conversationally instead.

## Next work

1. Get the user's call on plan §1 decision 1: Go in or out (recommendation: out; strip README + `make install-languages` claims).
2. Then §1 decisions 2 and 3: `config/git/work.gitconfig` fill-or-delete; `symlinked/gemrc.sh` keep-or-drop (recommendation: drop).
3. Execute each decision as a small direct commit to dotfiles `main`, checking items off in the plan doc.
4. Continue to plan §2 (config surface review) and onward as the user directs; §5 (docs reconcile) is gated on §1.
5. User signaled more plan items to come ("there's more but this is a start") — add them to §6 parking lot when they arrive.

## Constraints to honor

- The plan doc is the single punch-list; check items off there, don't fork a second list.
- Work lands as small, single-purpose commits directly to dotfiles `main` (user-approved pattern from the cleanup phase).
- `rm` is disabled on this machine; use `trash`, `git rm`, or `nuke` (explicit permanent only).
- Searches and delegation into the dotfiles spoke use the real path `/Users/michaelswanson/Code/dotfiles`, never the hub symlink.
- Two credential-shaped values exist in dotfiles git history (names: LITELLM_KEY, TX_TOKEN; repo is private). Treated as burned; lines already deleted from HEAD. Never quote the values; rotation is the user's job, and per the Cloudflare-token memory, don't nag about it.
- qmd MCP timed out on 2026-08-02; check service health via `launchctl print gui/$UID/local.qmd-mcp`, not `qmd status` (design doc §5 gotcha). Supports the planned doctor.sh check in plan §4.

## Open user inputs

- Plan §1 decisions: Go in/out; work.gitconfig fill/delete/keep; gemrc.sh keep/drop.
- Rotate or confirm-dead LITELLM_KEY and TX_TOKEN.
- Keep or drop the old dotfiles stash.
- Commit the ai-scratch hub changes (spoke symlink, MEMORY.md, plan doc, this handoff).
- The additional plan items the user said were coming.

## Suggested skills

- `manage-planning-repos` — if spoke wiring drifts or the dotfiles spoke needs a qmd collection / repo CLAUDE.md pass (its redline comment c12 already feeds plan §4: qmd install/wiring in machine setup).
- `redline-file` — if the user wants to mark up the plan doc before executing more of it.

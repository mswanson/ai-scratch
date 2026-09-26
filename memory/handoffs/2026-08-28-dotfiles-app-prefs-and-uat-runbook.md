---
date: 2026-08-28
topic: "dotfiles-app-prefs-and-uat-runbook"
repos:
  - "/Users/michaelswanson/Code/ai-scratch"
  - "/Users/michaelswanson/Code/dotfiles"
status: open
---

## Authoritative context

Read these first; they settle things this handoff does not repeat.

- dotfiles `docs/uat.md` — **the live document, and the next action.** The
  acceptance-test runbook: account creation, a table of what each of the 16
  bootstrap steps should do, what legitimately fails on a shared machine, and
  the teardown. Written 2026-08-28, never executed.
- `_bmad-output/planning-artifacts/2026-08-26-bootstrap-gap-audit.md` — the six
  gaps. **1, 2, 3 and 5 are now closed**; 4 (VS Code) and 6 (Dock) are not, and
  3 (Chrome apps) stays blocked on account logins by its own nature. Two
  corrections to it are recorded below rather than edited into it.
- `memory/handoffs/2026-08-26-dotfiles-bootstrap-uat.md` — the previous
  handoff, now `status: resolved`. Its constraints still bind; its Next Work
  items are either done or carried forward here.
- dotfiles `CLAUDE.md` §"Acceptance testing" — the rule and the eleven-bug
  evidence. Its "how" now points at `docs/uat.md`.
- dotfiles `git log 5897393..961c276` — 10 commits, each explaining its own
  reasoning. Do not re-explain what a commit message covers.

## State

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | this handoff + the 2026-08-26 one (untracked) | `4a73321` planning: bootstrap gap audit |
| dotfiles | main | clean, pushed | `961c276` docs: a UAT runbook, not a one-line instruction |

dotfiles is pushed; ai-scratch `memory/` is not committed.

**Done: audit gaps 1, 2, 3, 5.** `make bootstrap` is 16 steps. iTerm2 and Alfred
preferences are tracked in `config/iterm/` and `config/alfred/`, the Claude Code
CLI installs (`install-claude-code.sh`), and `setup-iterm.sh` /
`set-default-shell.sh` are finally called by something. `make doctor` passes.

**iTerm2 is live on the repo copy and verified** — `PrefsCustomFolder` resolves
to `~/.dotfiles/config/iterm` and the plists were byte-identical before
`~/Documents/App Settings/iTerm2` was trashed.

**Alfred is NOT live.** `make alfred` set `syncfolder`, and a running Alfred had
reverted it minutes later; Alfred holds the value in memory and rewrites its
whole domain. `~/Documents/App Settings/Alfred` is therefore still the live
location and still on disk. This does not affect bootstrap, where Alfred has
never launched — only the retrofit. See `scripts/setup-alfred.sh`'s header.

**Two corrections to the gap audit, which is otherwise still accurate:**

- Rectangle Pro does not "find" `RectangleProConfig.json` anywhere. That file is
  a manual File → Export dated 2024-11-28; the live config is the
  `com.knollsoft.Hookshot` defaults domain, written continuously, and the app
  has no CLI import. **Decision: iCloud sync**, which was already on. Nothing
  is tracked in the repo and the stale export has been trashed.
- The dead starship module blocks numbered **54**, not 56. The other two
  `disabled = true` were `[git_status]` (now enabled) and `[package]` (kept —
  its comment records a real decision).

**Prompt regressions, found by the owner mid-session and fixed.** `b590b55`
(269→140 lines) had bundled a cleanup with a behaviour change: dropping
`[username]`/`[hostname]` left the directory module's `"in "` prefix dangling,
so every prompt opened `in ~/Code`. Reverted wholesale at `dfedfaf`, then the
four changes were re-applied one at a time and separately agreed (`4e1b6a3`):
git_metrics conditional halves, `[hostname]` removed *with* a compensating
trailing space on `[username]`, `git_status` enabled with Nerd Font glyphs, and
the 54 dead blocks removed with a mechanical check first.

**`reload` was broken** and is fixed at `e890e86`. `typeset -U fpath` inside a
function localises *and empties* fpath, so compinit ran blind. Two more bugs in
the same function: it wrote a dumpfile name (`zcomp-$HOST`) no shell ever read,
and `$ZSH_CACHE_DIR` had no fallback.

**Never acceptance-tested, and this is the point of the next session:**
`setup-ssh-keys.sh` (added 2026-08-26, after the last UAT),
`install-claude-code.sh` (its install path cannot run on a machine that has the
CLI), and the MCP step it gates.

## Next work

1. **Run the UAT.** `docs/uat.md`, start to finish. `mktestuser` must be run by
   the owner in a real terminal — sudo cannot prompt from an agent shell,
   including via `!`. `dftest` and `/Users/Shared/dotfiles.bundle` from the
   previous run are already gone, so this starts clean. Log which steps failed,
   which *skipped* (a skip means a gate found a tool missing, which on a fresh
   machine is usually the real bug), and anything worked around by hand.
2. **Finish Alfred.** Quit Alfred, `make alfred`, relaunch, confirm with
   `defaults read com.runningwithcrayons.Alfred-Preferences syncfolder`. If it
   reverts again use Alfred > Preferences > Advanced > Syncing > "Set
   preferences folder…", which migrates the bundle rather than just repointing.
   Only then trash `~/Documents/App Settings/Alfred`.
3. **Alfred's two known weaknesses**, both documented in the script header and
   neither fixed: `workflows/alfred-bear` is a symlink into
   `.asdf/installs/nodejs/26.7.0/...` while `.tool-versions` pins `24.19.0`, so
   it is already dead on any machine built from this repo; and
   `preferences/local/<machine-hash>/` holds hotkey and keyboard settings keyed
   to one machine.
4. **Gap 4, VS Code:** track `settings.json` and the 53 extensions, or adopt
   Settings Sync. Either; still undecided.
5. **Phased Homebrew upgrade**, its own session. Three passes: security and
   network formulae, then leaf tools, then `zsh` and `asdf` separately with a
   shell restart and `make doctor` between each.
6. **`make macos` has still never been applied.** Written and verified, prompts,
   never run.

## Constraints to honor

- **Propose removals; the owner confirms.** Binds every pass.
- **Do not bundle a cleanup with a behaviour change.** This session's one real
  mistake, and the reason a whole commit had to be reverted. If a change alters
  what the owner sees, it is its own commit with its own decision — line count
  is never the justification.
- **Test script changes on a clean `$HOME` before calling them done.** Rule and
  evidence in dotfiles `CLAUDE.md`; procedure in `docs/uat.md`.
- **`git config --global` edits a tracked file** here, because `~/.gitconfig` is
  a symlink into the repo. Edit `symlinked/gitconfig.sh`. Same trap as
  `.claude/settings.json`, which IS the live `~/.claude/settings.json`.
- **No `set -e` over a sequence of independent operations.** Four scripts so far.
- **`typeset` on a zsh SPECIAL parameter inside a function localises AND empties
  it.** Use `-g`. This is what broke `reload`.
- **A running app wins over `defaults write`.** True of Alfred, and the reason
  iTerm2 and Alfred both get a "quit it first" warning.
- **`rm` is shadowed** by a function in `exports/functions.sh`. Use `trash`,
  `nuke`, or `command rm`.
- **`sudo` cannot prompt from a Claude Code shell**, including via `!`.
- The repo targets Apple Silicon only. Small single-purpose commits on `main`.
- Searches into spoke code use the real path, never the hub symlink.

## Open user inputs

- **Gap 4:** VS Code settings + 53 extensions tracked in the repo, or Settings
  Sync.
- **`git_status`'s trailing space** inside the brackets (`[1 󰜷8 ]`). Dropping
  the brackets from the format removes it; the bracketed format was the owner's
  own, previously commented out, so it was left alone.
- **1Password SSH agent migration** — still blocked on whether unattended
  bmad-loop sessions can commit, since they cannot answer a Touch ID prompt.
  Partly superseded: bootstrap now generates an on-disk key, so that plan
  changes where the key lives, not whether one is created.
- Whether the saved-reading agent, recipe corpus and PKM stubs are three
  projects or one.

## Suggested skills

- `write-handoff` — after the UAT run; its findings are a session-sized unit.
- `redline-file` — for reviewing a plan doc in place rather than deciding
  section by section in chat. Both rounds of it changed real decisions.
- `manage-planning-repos` — if spoke wiring drifts or the dotfiles spoke needs a
  qmd collection pass.
- Not `implement-story` / `operate-bmad-loop`: this work is direct commits to
  `main`, not story-driven.

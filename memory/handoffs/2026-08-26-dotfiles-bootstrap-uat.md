---
date: 2026-08-26
topic: "dotfiles-bootstrap-uat"
repos:
  - "/Users/michaelswanson/Code/ai-scratch"
  - "/Users/michaelswanson/Code/dotfiles"
status: resolved
---

## Authoritative context

Read these first; they settle things this handoff does not repeat.

- `_bmad-output/planning-artifacts/2026-08-26-bootstrap-gap-audit.md` — **the
  live document.** Six gaps between what `make bootstrap` does and the owner's
  bar ("Xcode, clone, bootstrap, log into accounts, work"). Ordered, with the
  reasoning for each. This is where the next session starts.
- `_bmad-output/planning-artifacts/2026-08-25-dotfiles-remaining-surfaces-plan.md`
  — the cleanup plan, EXECUTED. Carries a *What did not run* section and a
  *Notes from execution* section; both are current.
- `_bmad-output/planning-artifacts/2026-08-25-dotfiles-bootstrap-reproducibility-plan.md`
  — EXECUTED. Its "What is verified, and what is not" section is the honest
  record of test coverage.
- `_bmad-output/planning-artifacts/2026-08-22-1password-ssh-agent-plan.md` —
  written, not started, and now **partly superseded**: bootstrap generates an
  on-disk key. That plan changes where the key lives, not whether bootstrap
  creates one. Its unattended-commit blocker is still unresolved.
- dotfiles `CLAUDE.md` — rewritten this session. The acceptance-testing rule and
  the two symlink traps (`.claude/settings.json`, `git config --global`) are
  there, not here.
- dotfiles `git log` — 30+ commits across 2026-08-25/26, each explaining its own
  reasoning. Do not re-explain what a commit message covers.

## State

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | clean | `4a73321` planning: bootstrap gap audit |
| dotfiles | main | clean | `5897393` docs: git config --global writes into the repo |

Both pushed. `make doctor` passes all checks including the new SSH & Commit
Signing and Agent Toolchain sections.

**Done.** The cleanup plan (stages 0-8) and the bootstrap reproducibility plan
(all 7 gaps) both landed. `make bootstrap` is 13 steps and now includes SSH key
generation with GitHub registration for both authentication and signing.

**The method that produced most of the value:** a throwaway admin account
(`mktestuser` / `rmtestuser`, in `exports/functions.sh`) running `make bootstrap`
against a clean `$HOME`. It found **eleven** bugs on a repo where `make doctor`
was green, four of which made a fresh install impossible. Three were regressions
introduced earlier the same session. This machine only ever exercises the
idempotent path; the install path is invisible from here. That rule is now in
`CLAUDE.md`.

**Not run, deliberately:** the phased Homebrew upgrade (53 packages, moves `zsh`
and `asdf`, wants its own session), and `make macos` (written and verified,
prompts, never applied).

## Next work

1. **Move `~/Documents/App Settings/` into the repo.** Gap 1 in the audit, and
   the largest. iTerm2, Alfred and Rectangle Pro all load their real config from
   there and none of it is tracked. This is what the owner half-remembered as
   "a specific local file for the iTerm theme" — `PrefsCustomFolder` +
   `LoadPrefsFromCustomFolder`, which is also why `setup-iterm.sh` has been
   editing a plist the app ignores. Check Rectangle Pro's `iCloudSync = 1`
   (last sync 2023) before repointing it.
2. **Add `set-default-shell.sh` and `setup-iterm.sh` to bootstrap.** Both exist
   as make targets and neither runs. Without the first, a fresh machine keeps
   `/bin/zsh`. `set-default-shell.sh` needs sudo, so it goes last with a prompt.
3. **Install the Claude Code CLI in bootstrap.** Nothing does. It gates
   `setup-mcp-servers.sh`, which is why step 12 skipped on the test account.
   `cask "claude"` is the desktop app, not the CLI.
4. **VS Code:** track `settings.json` and the 53 extensions, or adopt Settings
   Sync. Either; neither is happening now.
5. **Chrome apps** (gap 3) — six of them, per-profile, so genuinely blocked on
   the account-login step. Scriptable only afterwards.
6. **Phased Homebrew upgrade**, in its own session. Three passes: security and
   network formulae, then leaf tools, then `zsh` and `asdf` separately with a
   shell restart and `make doctor` between each.

## Constraints to honor

- **Propose removals; the owner confirms.** Set after an over-eager pass deleted
  a curated wishlist. Binds every pass.
- **Commented Brewfile entries are deliberate records**, not cruft.
  Declared-but-not-installed is legitimate: the lists are rebuild manifests.
- **Test script changes on a clean `$HOME` before calling them done.** The rule,
  the evidence and the proportionality caveat are in dotfiles `CLAUDE.md`.
- **`git config --global` edits a tracked file** here, because `~/.gitconfig` is
  a symlink into the repo. Edit `symlinked/gitconfig.sh` instead. Same trap as
  `.claude/settings.json`, which IS the live `~/.claude/settings.json`.
- **No `set -e` over a sequence of independent operations.** This bit three
  scripts this session (`doctor.sh`, the old macOS-defaults wrapper,
  `bootstrap.sh`) and cost the most in `bootstrap.sh`.
- **`rm` is shadowed** by a function in `exports/functions.sh`. Use `trash`,
  `nuke`, or `command rm`.
- **The repo targets Apple Silicon only.** Scripts call `require_apple_silicon`.
- **`sudo` cannot prompt from a Claude Code shell**, including via `!`. Those
  commands go to the owner.
- Small single-purpose commits directly on dotfiles `main`.
- Searches into spoke code use the real path, never the hub symlink.

## Open user inputs

- **Which of audit gaps 1-3 to start with.** The question was asked and not
  answered; the session ended there.
- **Rectangle Pro's iCloud sync vs a repo-tracked config** — which wins.
- **1Password SSH agent migration:** still blocked on whether unattended
  bmad-loop sessions can commit, since they cannot answer a Touch ID prompt.
  The plan names the middle option (passphrase in the keychain).
- **Test-account teardown:** `dftest` (1.1 GB) and `/Users/Shared/dotfiles.bundle`
  were still present at session end. `rmtestuser` removes the first.
- Whether the saved-reading agent, recipe corpus and PKM stubs are three
  projects or one; they share a capture-into-structured-corpus shape.

## Suggested skills

- `redline-file` — for reviewing the gap audit or any plan doc in place rather
  than deciding section by section in chat. Used twice this session and both
  rounds changed real decisions.
- `write-handoff` — again at the next boundary; gaps 1-3 are a session-sized
  unit.
- `manage-planning-repos` — if spoke wiring drifts or the dotfiles spoke needs a
  qmd collection pass.
- Not `implement-story` / `operate-bmad-loop`: this work is direct commits to
  `main`, not story-driven.

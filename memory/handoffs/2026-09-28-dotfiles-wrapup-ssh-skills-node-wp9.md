---
date: 2026-09-28
topic: "dotfiles-wrapup-ssh-skills-node-wp9"
repos:
  - "ai-scratch"
  - "dotfiles"
  - "forge-skills"
status: open
---

## Authoritative context

Read these first; they settle things this handoff does not repeat.

- `_bmad-output/implementation-artifacts/spec-wp9-hub-registry.md` — the
  story this session produced: manage-planning-repos hub registry +
  `hubs.sh` fan-out. Frozen intent, I/O matrix, code map, ACs, eval
  scenarios. Baseline forge-skills `c46e2d6`. Owner review of 2026-09-28
  is folded in (roots are asked, never assumed; fan-out is
  manage-planning-repos Verify only).
- `_bmad-output/planning-artifacts/2026-08-22-1password-ssh-agent-plan.md`
  — carries the full test record and the two reversals (2026-09-25 split,
  2026-09-27 revert). Final SSH state is in its last section; do not
  re-argue 1Password for git.
- dotfiles `git log 5e6f4a4..687dded` (2026-09-25 to 2026-09-27) — nine
  commits, each explaining its own reasoning: SSH split and revert, Alfred
  prefs.json, `make node`, README fresh-machine path, `make skills`, the
  skills clone-slug fix, the mattpocock removals.
- dotfiles `docs/uat.md` — the fresh-machine runbook; still never executed.
- dotfiles `scripts/README.md` — the script table, now including
  `update-skills.sh`, `upgrade-node.sh`, `link-alfred-node-workflows.sh`,
  `setup-alfred.sh`, `setup-ssh-keys.sh`.
- `memory/handoffs/2026-09-25-migration-prep-skills-dotfiles-agents-md.md`
  — still `status: open`; its "Update" sections record the day-by-day
  decisions this handoff summarizes. Its forge-skills items (pin PR,
  `check_freshness.sh` bug, hub BMAD 6.12 rerun, AGENTS.md decision) are
  untouched and carry forward.

## State

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | `CLAUDE.md`, `memory/MEMORY.md`, `memory/bmad-loop-pins.md` (NOT this session's; a parallel session's pin/base-branch edits) + this handoff | `a7fde6a` planning: WP9 asks for scan roots |
| dotfiles | main | clean, pushed | `687dded` skills: drop the eight mattpocock skills deleted upstream |
| forge-skills | `operate-bmad-loop/base-branch` (off unmerged `5b81803` pin-v0.12.0) | 14 modified + `scripts/read_target_branch.py` untracked, all from a parallel session | `5b81803` chore(operate-bmad-loop): pin bmad-loop tool at v0.12.0 |

**Done in dotfiles, all pushed, `make doctor` green:**

- SSH: one on-disk key for GitHub auth and signing, passphrase in the
  keychain, loaded by zshrc; the managed github.com block pins
  `IdentityAgent SSH_AUTH_SOCK`; the `Host *` 1Password line is gone from
  `~/.ssh/config`; GitHub holds the key twice (`Michael's MBP`,
  `Personal MBP (signing)`), the "1Password GitHub" key is deleted, the
  owner deleted the 1Password item. Verified from detached tmux and with
  1Password locked. `setup-ssh-keys.sh` runs `gh auth login` in-step when
  needed and flips a token/bundle clone's origin to SSH.
- Alfred live from the repo (`prefs.json`, not the defaults key);
  `~/Documents/App Settings` trashed; Bear workflow relinked through
  `~/.local/share/alfred-node-workflows/` (was pointing at nodejs 26.7.0,
  not installed).
- `make node VERSION=x|latest` (`upgrade-node.sh`), `make skills`
  (`update-skills.sh`, also in `make update` and the end of
  `setup-skills.sh`). Claude and Codex both see all 39 store skills; 17
  third-party skills upgraded; 8 upstream-deleted mattpocock skills removed
  and their two rows dropped from the global CLAUDE.md suggest table.
- README: fresh-machine path assuming no gh/Homebrew/SSH (Xcode CLT →
  fine-grained token → HTTPS clone → bootstrap → revoke token; bundle over
  AirDrop as the tokenless alternative).
- `setup-skills.sh` cloned a nonexistent repo (`mswanson/forge-skills`);
  now `forge512/agent-skills`.
- Slack CLI is the Homebrew cask; curl binaries trashed, `~/.slack`
  credentials kept. `docs/linear-workspace-blueprint.md` trashed
  (superseded by rev 3.2 in the Orderly planning repo).

**Pending:** the fresh-machine UAT (owner: hold), the phased Homebrew
upgrade (owner: hold, after the UAT), and the new-machine-only items.

## Next work

1. **Implement WP9** in forge-skills via `implement-story` once the
   checkout is back on `main` with the parallel session's work landed
   (commit or PR the `base-branch` branch first; the pin commit `5b81803`
   is also not on main). Story file above; baseline `c46e2d6`.
2. **dotfiles follow-up after WP9 lands:** dotbot-link
   `~/.config/planning-repos/registry.json` into the repo
   (`install.conf.yaml`, one line), same pattern as the skill lockfile.
3. **Fresh-machine UAT** (`docs/uat.md`) when the owner says go. Never
   exercised on a clean account: the rewritten SSH step (passphrase prompt,
   keychain load, in-step `gh auth login`, origin flip),
   `install-claude-code.sh` + the MCP step, Alfred first launch with no
   `prefs.json`, the workflow relink, the skills mirror.
4. **Phased Homebrew upgrade**, after the UAT: security/network formulae,
   then leaf tools, then `zsh` and `asdf` separately with `make doctor`
   between passes.
5. Carry forward from the 2026-09-25 handoff, unchanged: forge-skills
   `check_freshness.sh` fix, BMAD installer rerun in this hub to 6.12.0,
   AGENTS.md decision + manage-planning-repos Step 3 change, forge-skills
   worktree cleanup (2 worktrees + 3 branches with gone remotes), the
   deferred-work ledger.
6. New-machine day, no prep needed: `make macos`, Alfred hotkeys, Chrome
   apps (check `chrome://apps` after profile sign-in before scripting),
   VS Code Settings Sync sign-in, Dock, `slack login`.

## Constraints to honor

- **1Password stays out of the git path.** Decided twice, tested eight
  ways; the plan doc has the table. The keychain-passphrased disk key is
  the end state, not a fallback.
- **`make skills` will not pull forge-skills** while it is off `main` or
  dirty; that is by design. Do not "fix" it by pulling anyway.
- **The hub's dirty `CLAUDE.md`, `MEMORY.md`, `bmad-loop-pins.md` belong to
  another session.** Do not commit, revert, or fold them.
- **Propose removals; the owner confirms.** Binds every dotfiles pass.
- **Do not bundle a cleanup with a behaviour change.**
- **Test script changes on a clean `$HOME` before calling them done**
  (dotfiles `CLAUDE.md`; procedure in `docs/uat.md`).
- **Edit tracked files through the repo path, never through the `~`
  symlink**: `~/.tool-versions`, `~/.gitconfig`, `~/.claude/settings.json`,
  `~/.agents/.skill-lock.json` are dotbot links; BSD `sed -i` on the link
  detaches it. `upgrade-node.sh` documents the trap.
- **No `set -e` over independent operations**; no GNU tools (`timeout`
  does not exist on macOS, which broke one test harness this session).
- `rm` is disabled: `trash`, `git rm`, `command rm` inside scripts only
  for dead symlinks. `sudo` cannot prompt from an agent shell.
- forge-skills: bash 3.2 + BSD, Python stdlib, hermetic tests, markdownlint
  clean; merges belong to the owner; merge commits, never squash/rebase.
- Hub: never squash or rebase hub PRs.

## Open user inputs

- When to run the fresh-machine UAT (owner said hold).
- Whether to turn off the 1Password SSH agent entirely (Settings →
  Developer); nothing uses it now.
- Carried: AGENTS.md flip per repo; whether saved-reading, recipe corpus
  and PKM are one project or three.

## Suggested skills

- `implement-story` — for WP9, from this hub, once forge-skills is on
  `main`.
- `operate-bmad-loop` (Upgrade) — after the hub's BMAD installer rerun.
- `manage-planning-repos` — WP9 changes it; run Verify on this hub after
  the story lands to see the marker GAP and stamp it.
- `consolidate-memory` — the 2026-08-25, 08-26, 08-28 and 09-25 handoffs
  are ready to fold once the UAT runs; this one joins them after WP9.
- `write-handoff` — at the next boundary.

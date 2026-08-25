---
date: 2026-08-25
topic: "dotfiles-brewfile-apps-audit"
repos:
  - "/Users/michaelswanson/Code/ai-scratch"
  - "/Users/michaelswanson/Code/dotfiles"
status: open
---

## Authoritative context

Read these first; do not re-derive what they settle.

- `_bmad-output/planning-artifacts/2026-08-02-dotfiles-update-plan.md` — the working punch-list and the record of every decision. §1 closed, §2 partly done with per-directory findings written in, §3–§6 open. The §2 `scripts/` entry carries four findings from this session that are worth reading before touching that directory.
- `_bmad-output/planning-artifacts/2026-08-22-1password-ssh-agent-plan.md` — three-stage SSH key migration, written and not started.
- Four project stubs written this session, all indexed in `memory/MEMORY.md`: `2026-08-25-local-rag-and-tuning-scope.md`, `2026-08-25-recipe-corpus-project.md`, `2026-08-25-saved-reading-agent-idea.md`, plus the Alfred / Chrome-profile / PKM items in the plan's §6 parking lot.
- dotfiles `main` at `0186d0c` — 37 commits this session, each explaining its own reasoning. `git log` there is the record; don't re-explain what a commit message already covers.

**Method that made this work, and should carry forward:** file-first, not topic-first. For each file ask what consumes it and whether the tool it configures is actually installed, then remove whole — file, dotbot entry, script reference, doctor check, README claim, live symlink. Topic-grep misses things; that is how the 2025-12 Go removal left the plugin install, prompt module and doctor check behind.

## State

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | this handoff (untracked) | `073f94a` planning: recipe corpus project stub |
| dotfiles | main | `.claude/settings.json`, `brew/brewfiles/Brewfile.apps` | `0186d0c` brew: fold the Quick Look list into Brewfile.apps, note Overcast |

**The dotfiles working-tree change is the user's, not the session's:** `Brewfile.apps` has `mas "Okta Verify"` commented out by hand after the session declared it. Leave that decision alone. `.claude/settings.json` is accepted model/effort churn per `memory/claude-settings-scopes.md`.

**Done this session.** `Brewfile.apps` audited app by app across 13 functional sections and reorganised by purpose, with a note on every entry whose reason is not self-evident. Brewfiles reduced from four lists to three (`cli`, `apps`, `fonts`) — `Brewfile.quicklook` folded in once all its entries were casks. `brew bundle` now runs at all, which it never did before this session.

Removed from the machine: Airmail, Spark, Dropbox, SourceTree, Local, NameChanger, Sequel Ace, gpg-suite, hub, ruby, Homebrew's node, Pop, and a python.org Python 3.13 framework. Roughly 8 GB trashed plus 290 MB from Python. Adopted as declarations: nine apps that were installed by hand and declared nowhere, which was the real gap the audit existed to find.

**Pending, in the order the user set it:** formula audit on `Brewfile.cli` (~95 formulae, same section-by-section walkthrough), then the phased upgrade of the outdated packages, then the remaining §2 directories, then §3.

## Next work

1. **Formula audit on `Brewfile.cli`.** Same format as the apps audit: group by function, present installed/declared/evidence per entry, let the user decide each section. Known entries already flagged: `lua` (its only annotation said "Used with Hammerspoon", and Hammerspoon was cut this session, so its reason is now unknown), a commented `redis-stack` duplicating what `Brewfile.apps` declares properly, a commented `pgcli` among the last Postgres traces, and `coreutils` — commented out, but `greadlink` from it is what broke two scripts.
2. **Phased Homebrew upgrade**, only after the audit. Three passes, verifiable separately, not one blanket `brew upgrade`: security and network formulae (`openssl@3`, `curl`, `gnupg`, `ca-certificates`) first, then leaf CLI tools, then `zsh` and `asdf` deliberately with a shell restart and `make doctor` after each. `zsh` is the login shell and `zshenv.sh` documents the stale-`FPATH` hazard an upgrade triggers.
3. **§2 remaining directories:** `aliases/` (5 files), `scripts/` (20), `config/` (13), `starship/` (2). Start with `scripts/` — the plan's findings there are already written up.
4. **§3 submodule removal** — `lib/iTerm2-Color-Schemes` is now unreferenced and 92 MB. The plan carries the full deinit/rm/.gitmodules/.git-modules sequence.
5. **§4 bootstrap reproducibility** — the largest remaining chunk and arguably the highest value: qmd, codegraph, MCP registrations, the skills chain and the LiteLLM stack are all hand-installed as of 2026-08-25.

## Constraints to honor

- **Propose removals; the user confirms.** Set explicitly after an over-eager pass deleted a curated wishlist. Explain why something is not needed and let them decide. This binds every future pass.
- **Commented Brewfile entries are deliberate records**, not cruft. They hold considered-and-passed decisions and App Store ids that are tedious to re-look-up. Never bulk-delete them.
- **Declared-but-not-installed is legitimate** in `Brewfile.apps`: the list is a new-machine install manifest, so an entry the user wants on a rebuild is correct even if it is not installed at the time.
- Work lands as small single-purpose commits directly on dotfiles `main`.
- `rm` is disabled (a zsh function in `exports/functions.sh`); use `trash`, `git rm`, or `nuke`. `sudo` bypasses the function.
- **Two hard environment limits, both hit repeatedly this session.** `sudo` cannot prompt from a Claude Code shell *or* from the `!` prefix — those commands must be run in a real terminal window. And `~/Library/Containers` is TCC-protected: creating there works, deleting does not, so container removal needs Finder or Full Disk Access for the responsible app (VS Code hosts this terminal).
- Searches and delegation into the dotfiles spoke use the real path, never the hub symlink.

## Open user inputs

- **The Finder pass**, blocked by root ownership or TCC: `/Applications/Termius.app` (556 MB), `OneDrive.app`, `Adobe Acrobat Reader.app`, `Microsoft Teams classic.app`, `GPG Keychain.app` (left by the gpg-suite uninstall), and six folders under `~/Library/Containers` (four `it.bloop.airmail2*`, `com.readdle.smartemail-Mac`, `com.sequel-ace.sequel-ace`).
- **`~/Local Sites/txapa`** — 1.67 GB WordPress site from 2023-08, left in place pending a keep-or-export decision.
- **Creative Cloud → Preferences → Syncing.** Core Sync has 63 minutes of CPU since 2026-07-12 syncing a Creative Cloud Files folder that does not exist. `launchctl` cannot hold it down because the CC app launches it.
- **Emptying the Trash** is what actually reclaims the ~8 GB.
- Whether the saved-reading agent, recipe corpus and PKM stubs are three projects or one — they share a capture-into-structured-corpus shape.
- 1Password SSH plan: whether unattended bmad-loop sessions create signed commits (they cannot answer a Touch ID prompt), and whether anything besides GitHub uses that key.

## Suggested skills

- `implement-story` / `operate-bmad-loop` — not for this work; the dotfiles passes are direct commits to `main`, not story-driven.
- `redline-file` — if the user wants to mark up the plan doc before executing more of it, rather than deciding section by section in chat.
- `manage-planning-repos` — if spoke wiring drifts, or if the dotfiles spoke needs a qmd collection pass.
- `write-handoff` — again at the next natural boundary; the formula audit plus the phased upgrade is a session-sized unit.

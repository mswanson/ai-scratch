# Dotfiles Update Plan

Working plan for the `dotfiles` spoke (`/Users/michaelswanson/Code/dotfiles`). The 2026-08-01/02 cleanup is done: Claude config tracked and symlinked via dotbot, Okta era removed, dead weight deleted, `_bmad` removed, single tool-versions source, modernization guide archived and closed out. This plan covers what's next. Work lands as small direct commits to `main`; check items off here.

## 1. Open decisions — CLOSED 2026-08-16

All three decided "out" and executed as small commits on dotfiles `main`.

- [x] **Go: out.** `4824c8d` + `e31dd1e`. Traced to `c87ed97`, the commit that executed the archived 2025-12 modernization guide; that guide's mission line names Go, no commit or project ever used it. Was half-removed already: `ad102d1` dropped it from `tool-versions.sh` but left the automation, so `make setup-asdf` still installed the golang plugin on fresh machines, starship configured a prompt module, doctor reported the version. Eleven references stripped.
- [x] **Work identity: deleted.** `904ae19`. The machinery was never connected: neither `~/code/work` nor `~/Code/work` has ever existed, `work.gitconfig` was the raw template, and the `github.com-work` SSH host alias it rewrites URLs to is absent from `~/.ssh/config` and from the repo. Commit signing has landed since, so a real second identity also needs its own signing key and `allowed_signers` entry — rebuilding against a real account beats resurrecting a guess. Dropped `work.gitconfig`, `personal.gitconfig` (unfilled, included by nothing), both `includeIf` blocks, and `verify-git-identity.sh` (doctor.sh already covers git identity), plus the make target, bootstrap step, and README claims.
- [x] **Ruby: dropped.** `39c930f`. `gemrc.sh` (`--no-ri --no-rdoc`, deprecated a decade), its dotbot link, `~/.gemrc` unlinked, and the stale CLAUDE.md claim that `dev-utils.sh` holds Rails aliases (it holds none).

### Bug found while verifying

- [x] **`doctor.sh` aborted at the first failed check.** `1e782bd`. `set -e` plus check functions that `return 1` killed the run on the first missing tool — `error_msg` is even commented "don't exit". On this machine doctor had been dying at the Go check, so symlinks, git identity, language versions and CLI tools were never checked. Removed `set -e`; the script now tallies ISSUES and reports at the end as designed.

### Findings the fixed doctor surfaced (feed §2)

- [ ] **ripgrep not installed.** `rg` is not on PATH; doctor expects it. Install or drop the check.
- [ ] **Node is not the pinned version.** `~/.tool-versions` pins `nodejs 22.12.0`; the running node is `/opt/homebrew/bin/node` v26.4.0 — Homebrew's node shadows the asdf shim. Python resolves correctly through asdf. Decide which manager owns node, then make PATH match.

## 2. Config surface review

Line-by-line pass over each config surface, verifying every entry against tools actually installed and workflows actually used. Kill on sight; nothing is precious.

73 files across seven directories: `symlinked/` (22), `scripts/` (20), `config/` (13), `exports/` (6), `aliases/` (5), `brew/` (5), `starship/` (2).

**Method — file-first, not topic-first.** The Go removal proved topic-grep misses things: the 2025-12 cleanup grepped for `golang`, removed it from `.tool-versions`, and left the plugin install, the prompt module, and the doctor check behind. So for each file ask: *what consumes this, and is the tool it configures actually installed?* Then remove whole — file, dotbot entry, script reference, doctor check, README claim, live symlink in `$HOME` — never partially. Start with `symlinked/` (biggest, most likely stale).

### `symlinked/` — DONE 2026-08-21 (21 files → 15)

Owner decisions taken during the pass: bash is used interactively only (remote sessions, laptop setup); wget is installed solely so other tools can call it; vimrc to be cleaned up rather than dropped; asdf owns node and `.tool-versions` stays current.

- [x] **Six dropped** (`4351630`). `curlrc.sh` and `wgetrc.sh` both spoofed the user agent as IE on Windows 7 — curl's applied to every call on the machine, and wget's callers should get stock behaviour, not `robots=off` plus verbose `server_response`. `wget-hsts.sh` and `stCommitMsg.sh` are mutable state, not config: wget's HSTS cache (its one entry expired 2023) and the scratch file SourceTree writes commit messages into — tracking them means those tools write into the repo. `psqlrc.sh` configured an uninstalled psql. `bashenv.sh` existed so `#!/bin/bash` scripts would inherit aliases, but `BASH_ENV` was exported from `bashrc.sh`, which only interactive bash reads, while `BASH_ENV` is only consulted by non-interactive shells — the login shell is zsh, so it never fired.
- [x] **`gitignore_global.sh` opened with `syntax: glob`** (`89d3d4e`) — Mercurial syntax; git read it as a literal pattern. Rewritten with macOS, editor and secrets patterns.
- [x] **`zshrc.sh` sourced a gcloud SDK on the Desktop** (`89d3d4e`) that does not exist; gcloud is not installed. Four dead lines plus a commented template TODO block.
- [x] **`bashrc.sh` history was non-functional** (`81c11b6`): `SAVEHIST` is zsh-only and `BASH_HISTFILE` is not a bash variable, so history ran on defaults. Now `HISTSIZE`/`HISTFILESIZE`/`HISTFILE`. Also dropped `GREP_OPTIONS`, removed from GNU grep in 2014 and ignored by the ugrep now installed as grep.
- [x] **`vimrc.sh` rewritten** (`0ab049b`). Was mostly commented-out Vundle scaffolding for a plugin manager never installed. Now built-in settings only, so it works on a bare machine: indentation matches editorconfig at 2 spaces, persistent undo, swap/backup out of the working directory, gitcommit wraps at 72 with spell-check. `nohlsearch` moved off `<CR>`, which shadowed Enter in quickfix.
- [x] **`gitconfig.sh` cleaned** (`c1b1240`). The `git://` shorthands mapped `github:` and `gist:` onto a protocol GitHub disabled in January 2022. The `[filter "lfs"]` block declared `required = true` while git-lfs is not installed, which makes any repo with LFS pointers fail hard. Dropped the inert `gpg program` line (signing is `format = ssh`) and the placeholder comments.
- [x] **Colorize plugin dropped** (`9185502`). Its `ccat`/`cless` need pygmentize, not installed. `exports/colorize-config.sh` was orphaned — nothing sourced it, and it pointed at `lib/tasks/install-pygments.sh`, removed in an earlier cleanup. `bat` covers it.
- [x] **Node: asdf now owns it** (`928bbd8`). Three versions disagreed — `.tool-versions` pinned 22.12.0, asdf had 24.8.0 selected, Homebrew's v26.4.0 actually ran, because the oh-my-zsh asdf plugin adds shims during antidote load and `exports/paths.sh` then prepended `/opt/homebrew/bin` ahead of them. paths.sh now puts shims first explicitly; `.tool-versions` pinned to 24.8.0. Also removed a stray untracked `~/Code/.tool-versions` that silently overrode the home file for every repo under `~/Code`.

Kept and verified clean: `asdfrc.sh`, `bash_profile.sh`, `bashrc.sh`, `default-npm-packages.sh`, `default-python-packages.sh`, `editorconfig.sh`, `hushlogin.sh`, `inputrc.sh`, `tool-versions.sh`, `zsh_plugins.txt`, `zshenv.sh` (the fpath hardening is deliberate), `zshrc.sh`.

### Open items carried out of the `symlinked/` pass

- [ ] **npm global prefix still points at Homebrew.** `npm config get prefix` returns `/opt/homebrew`, set by the builtin npmrc inside Homebrew's npm, so `npm -g` installs land outside asdf even though `node` and `npm` now resolve through the shims. Decide whether Homebrew's node can go (only `todoist-cli` depends on it) or whether to override the prefix.
- [ ] **asdf nodejs 22.12.0 is still installed** and now unreferenced; `asdf uninstall nodejs 22.12.0` when convenient.
- [ ] **ripgrep is not installed** but doctor expects it and `aliases/` may reference it. Install or drop the check. Now the only issue doctor reports.

### Remaining directories

- [ ] `aliases/` (5 files): dead tool references (antigenrc comment in dev-utils), open TODOs (bat/exa in cli-utils), aliases for uninstalled tools.
- [ ] `exports/` (4 remaining files): config.sh, functions.sh, paths.sh, colorize-config.sh; also `claude_update.sh` sourcing.
- [ ] `brew/brewfiles/*`: diff against `brew list` / `brew bundle cleanup --dry-run`; remove uninstalled, add unmanaged (qmd and codegraph live in `/opt/homebrew/bin` but only rtk is a brew formula; see §4).
- [ ] `config/`: `hammerspoon.lua` is orphaned (tool not installed, not linked); delete or install hammerspoon deliberately.
- [ ] `scripts/`: leftover antigen references in `update.sh` and `rollback-dotfiles.sh`; verify `doctor.sh` checks match the post-cleanup file set.
- [ ] `starship/`, `symlinked/` misc (curlrc, wgetrc, editorconfig, inputrc, psqlrc, hushlogin, stCommitMsg): still wanted?

## 3. Get rid of submodules

Goal: zero submodules; plain files or brew-managed.

- [ ] `lib/iTerm2-Color-Schemes` (huge upstream repo for what is probably one used scheme): identify the scheme(s) actually loaded by `make iterm` / `scripts/setup-iterm*`, vendor just those files, drop the submodule.
- [ ] `lib/bear-templates` (own repo): vendor the templates into `lib/` or keep as separate repo cloned on demand; drop the submodule either way.
- [ ] `lib/macOS-defaults` is a plain vendored dir (not a submodule); leave as is or refresh while in there.
- [ ] Update CLAUDE.md submodule docs and `scripts/update.sh` submodule handling once gone.

## 4. Token-optimization stack in bootstrap

Make `make bootstrap` on a fresh machine reproduce the framework machine setup (design: `_bmad-output/planning-artifacts/2026-07-31-token-optimization-framework-design.md` §3, §5, §6). Today most of it is hand-installed and unreproducible.

- [ ] **Binaries**: pin install method for the stack: rtk (brew formula, done), qmd and codegraph (in `/opt/homebrew/bin` but not brew-tracked; add tap/formula or an install script step).
- [ ] **rtk config**: locate the tuned config (`hooks.exclude_commands` for grep/rg per design §3) and track it in dotfiles + dotbot link.
- [ ] **qmd service**: track `~/Library/LaunchAgents/local.qmd-mcp.plist` in dotfiles, dotbot-link it, add a bootstrap step (`launchctl bootstrap`) and a doctor check (launchd + MCP health, not `qmd status`; design §5 gotcha).
- [ ] **MCP registrations**: user-scope MCPs (qmd HTTP, codegraph, todoist) live in `~/.claude.json`, which stays untracked; add an idempotent script (`scripts/setup-claude-mcp.sh` or similar) with the `claude mcp add --scope user ...` commands.
- [ ] **Claude plugin set**: global plugins are already reproducible via tracked `settings.json` `enabledPlugins`; verify a fresh-machine run actually installs them.
- [ ] **Skills chain**: bootstrap step that clones `~/Code/forge-skills` and runs its `install.sh` (the `~/.claude/skills → ~/.agents/skills → repo` chain), then restores third-party skills from the tracked `.agents/skill-lock.json` manifest.
- [ ] **doctor.sh coverage**: checks for the whole chain: rtk hook firing, qmd MCP answering, codegraph on PATH, `~/.claude/*` symlinks intact.
- [ ] **LiteLLM stack install script.** The stack itself landed 2026-08-06 in `config/litellm-stack/` (dotbot-linked to `~/litellm-stack`, plist linked into `~/Library/LaunchAgents/`), but bringing it up on a fresh machine is still the hand-run sequence in that directory's README: brew Ollama + `ollama pull`, brew LM Studio cask + manual onboarding + three `lms get` pulls (~74 GB), `~/.config/litellm/.env` creation with a generated master key, `docker compose up -d`. Write `scripts/setup-litellm.sh` to do the scriptable parts idempotently and prompt for what it can't (LM Studio's GUI onboarding, the two API keys), then wire it into `make bootstrap` and add a doctor check (proxy answering on :4000, both native backends reachable, LaunchAgent loaded).

## 5. Docs reconcile (after §1 decisions land)

- [ ] CLAUDE.md: dotbot-as-submodule sections (install flow, "Updating Submodules"); document `.claude/` and `.agents/` dirs; re-verify shell loading order matches post-cleanup zshrc.
- [ ] README: Go claim per §1, identity-switching claim per §1, stale "Last Updated", merge the old 7-item TODO section into this plan and delete it.
- [ ] Delete or annotate `archive/2025-12-modernization-guide.md` cross-references once §1 closes the last open phases.

## 6. Parking lot

(Owner: more items to come.)

- [ ] Note from the 2026-08-02 manage-planning-repos redline (c12): machine-level qmd setup (binary + launchd + MCP registration) is dotfiles' job — §4 items above cover it; per-repo qmd COLLECTIONS stay out of dotfiles, they're created by manage-planning-repos Setup per repo.

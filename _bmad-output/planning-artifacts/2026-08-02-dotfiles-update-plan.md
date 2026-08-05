# Dotfiles Update Plan

Working plan for the `dotfiles` spoke (`/Users/michaelswanson/Code/dotfiles`). The 2026-08-01/02 cleanup is done: Claude config tracked and symlinked via dotbot, Okta era removed, dead weight deleted, `_bmad` removed, single tool-versions source, modernization guide archived and closed out. This plan covers what's next. Work lands as small direct commits to `main`; check items off here.

## 1. Open decisions (small, unblock the docs pass)

- [ ] **Go: in or out.** Go isn't installed anywhere (no asdf plugin, no Brewfile entry) but README claims Go development support. Either add it (asdf plugin + `golang` in `symlinked/tool-versions.sh`) or strip the Go claims from README and `make install-languages`. Leaning out unless Go work is actually planned.
- [ ] **`config/git/work.gitconfig`: fill or delete.** The `includeIf` wiring in `symlinked/gitconfig.sh` works, but the target is an unfilled template (`YOURCOMPANY.com`). Fill with forge512 identity, or delete the template and the README "smart identity switching" claim until there's a second identity to switch to.
- [ ] **`symlinked/gemrc.sh`: keep or drop.** Last Ruby remnant, still linked to `~/.gemrc`. Harmless with Homebrew ruby; contradicts the no-Ruby-tooling goal.

## 2. Config surface review

Line-by-line pass over each config surface, verifying every entry against tools actually installed and workflows actually used. Kill on sight; nothing is precious.

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

## 5. Docs reconcile (after §1 decisions land)

- [ ] CLAUDE.md: dotbot-as-submodule sections (install flow, "Updating Submodules"); document `.claude/` and `.agents/` dirs; re-verify shell loading order matches post-cleanup zshrc.
- [ ] README: Go claim per §1, identity-switching claim per §1, stale "Last Updated", merge the old 7-item TODO section into this plan and delete it.
- [ ] Delete or annotate `archive/2025-12-modernization-guide.md` cross-references once §1 closes the last open phases.

## 6. Parking lot

(Owner: more items to come.)

- [ ] Note from the 2026-08-02 manage-planning-repos redline (c12): machine-level qmd setup (binary + launchd + MCP registration) is dotfiles' job — §4 items above cover it; per-repo qmd COLLECTIONS stay out of dotfiles, they're created by manage-planning-repos Setup per repo.

# Dotfiles: Remaining Surfaces — Staged Plan

Audit of everything not yet reviewed, staged for sequential execution. Nothing here is changed yet. Each stage lists what I propose to do and what I need from you first.

Written 2026-08-25, after `symlinked/`, `exports/` (partial), the Brewfile app audit, and Quick Look were closed.

## What is left, by size and defect density

| Surface | Files | Lines | State |
|---|---|---|---|
| `scripts/` | 17 | 1,242 | Highest defect density. Two scripts cannot run at all. |
| `starship/` | 2 | 277 | 66 module blocks, 56 disabled, only 16 reachable. |
| `aliases/` | 5 | 246 | 13 of 41 aliased commands are not on PATH. |
| `exports/` | 4 | 299 | `config.sh` and `functions.sh` cleaned; `paths.sh` and `litellm.sh` unreviewed. |
| `brew/brewfiles/Brewfile.cli` | 1 | ~95 entries | The formula audit, already queued. |
| `lib/` | — | 93 MB | Two submodules; the 92 MB one is now unreferenced. |
| `config/` | 12 | — | Mostly current. `litellm-stack/` is its own subsystem. |
| Root docs + `install.conf.yaml` | 5 | — | CLAUDE.md carries stale submodule claims. |

**Three things are already healthy**, and worth stating so no one re-checks them: every script in `scripts/` is referenced by `bootstrap.sh`, the `Makefile`, or `update.sh` — there are no orphans. Every `install.conf.yaml` link source exists. And no symlink in `$HOME` points into dotfiles without dotbot managing it.

---

## Stage 1 — `scripts/` (highest value, most broken)

Two scripts are dead, and they fail the same way the two already fixed this session did.

**`set-default-shell.sh` and `rollback-dotfiles.sh` both call `greadlink`**, from coreutils, which is not installed. That is the third and fourth instance of this bug — `setup-iterm.sh` and `patch-quicklook-plugins.sh` were the first two. Neither script can run today.

Those same two are also **the only remaining consumers of the legacy `scripts/functions.sh`**. The other fifteen scripts use `scripts/lib/common.sh`, which has a fuller helper set (`warn`, `print_header`, `require_command`, `require_macos`, `is_apple_silicon`). `functions.sh` lacks `warn`, so a script written to the common idiom calls an undefined function, and its own first line sources `./config/exports/functions.sh` — a path that has not existed since the cleanup.

**Antigen leftovers**, from a plugin manager replaced by antidote: `update.sh` lines 90–92 clean a `~/.config/antigen` cache directory, and `rollback-dotfiles.sh` lines 24–25 remove `.config/antigen` and `.antigenrc.zwc`.

**Proposed changes**

1. Fix the `greadlink` calls in both scripts — use zsh's `${0:A:h}`, the same fix applied to `setup-iterm.sh`.
2. Migrate both to `lib/common.sh`, then delete `scripts/functions.sh`.
3. Remove the antigen blocks from `update.sh` and `rollback-dotfiles.sh`.
4. Read `setup-macos-defaults.sh` closely. It is the same class of script as `setup-iterm.sh`, which turned out to be writing a font that was not installed and a path under the wrong username. Assume nothing in it is verified.
5. Re-run `make doctor` and a dry pass over each touched script.

**Questions for you**

- **`rollback-dotfiles.sh` is destructive by design** — it removes every dotfile symlink. Do you want it kept and fixed, or is it scaffolding you would never actually run? Fixing it means testing it, which means finding a safe way to exercise a script whose job is to tear down your environment.
- **`set-default-shell.sh`** sets zsh as the login shell. Your shell is already `/opt/homebrew/bin/zsh`. Keep for fresh-machine setup, or drop?

---

## Stage 2 — `starship/`

`starship.toml` is 269 lines defining **66 module blocks. 56 are explicitly `disabled = true`.** And the `format` string at the top only ever renders 16 modules, so those 56 are dead twice over — not in the format, and disabled anyway. They cover languages you do not use: cobol, crystal, elm, erlang, haskell, julia, nim, ocaml, perl, purescript, red, scala, vlang, zig, and more.

Starship only renders what the `format` string names. Everything else is inert configuration.

**Proposed change**

Cut the file to the modules the format actually uses — username, hostname, directory, the git set, package, nodejs, python, env_var, custom, cmd_duration, character — plus a short comment explaining that adding a module means adding it to `format`, not just defining a block. Roughly 269 lines to about 80.

**Question for you**

- Any of those 56 you want kept as commented notes, the way we kept the Brewfile wishlist? My instinct is no — a starship block is trivially re-added from their docs, unlike an App Store id. But the same argument applied to the Brewfiles and you wanted those kept, so I am asking rather than assuming.

---

## Stage 3 — `aliases/`

41 distinct commands are aliased; **13 are not on PATH.** Some of those are false alarms worth discounting up front: `PlistBuddy` lives at `/usr/libexec`, `emulate` is a zsh builtin, and one match was an env-var prefix rather than a command.

The real absences: `bubo`, `color-ls`, `diskspace_report`, `g`, `lsregister`, `nuke`, `pg_ctl`, `redis-cli`, `redis-server`, `ScreenSaverEngine`.

Two need your judgment specifically. **`nuke`** is the permanent-delete command referenced in your global CLAUDE.md as the counterpart to `trash` — if it is not on PATH, that instruction points at something that does not exist. And **`redis-cli`/`redis-server`** are absent even though you kept `redis-stack-server`; that cask may not put those on PATH.

`dev-utils.sh` line 3 also credits aliases to "OMZ plugins (see antigenrc)" — antigen is gone.

**Proposed change**

Go file by file, list every alias with whether its command resolves, and let you keep or cut each group. No bulk removal.

**Questions for you**

- What is `nuke`, and where should it come from? It is load-bearing in your global instructions.
- `bubo` and `diskspace_report` — yours, or inherited from a template?

---

## Stage 4 — `Brewfile.cli` formula audit

The one already queued. ~95 formulae, same section-by-section walkthrough as the apps audit. Known items going in: `lua` (its only annotation said "used with Hammerspoon", and Hammerspoon was cut, so its reason is now unknown), a commented `redis-stack` duplicating what `Brewfile.apps` declares properly, a commented `pgcli` among the last Postgres traces, and `coreutils` — commented out, while `greadlink` from it is what broke four scripts.

That last one is a real decision rather than a cleanup: **install coreutils, or purge every `g`-prefixed GNU tool assumption from the scripts.** I lean toward purging, since the scripts should not depend on optional tooling, but installing it is defensible.

---

## Stage 5 — `lib/` submodules

`lib/iTerm2-Color-Schemes` is **92 MB and now unreferenced** — the two schemes you use were vendored to `config/iterm/themes` (16 KB) this session. Removal is the full sequence, not a delete: `git submodule deinit`, `git rm`, strip the `.gitmodules` stanza, clear `.git/modules/`.

`lib/bear-templates` (92 KB) is your own repo, dotbot-linked to `~/.config/bear/templates`, and still live. `lib/macOS-defaults` (72 KB) is a plain vendored directory read by `setup-macos-defaults.sh`.

**Question for you**

- `bear-templates` is a submodule pointing at a repo you own. Keep it as a submodule, or vendor the templates in and drop submodules from this repo entirely? Zero submodules was the stated §3 goal.

---

## Stage 6 — Docs reconcile

`CLAUDE.md` still describes **dotbot as a submodule** with an "Updating Submodules" section. Dotbot is a Homebrew formula, declared in `Brewfile.cli`. The `lib/` section lists three submodules; one is about to go and one never was a submodule.

`install.conf.yaml:44` carries a commented TODO about linking `~/Dropbox/Code/ssh` to `~/.ssh`. Dropbox is uninstalled, and that line is also evidence SSH keys once lived in Dropbox — worth carrying into the 1Password plan as motivation rather than just deleting.

`README.md` has a seven-item TODO list at the top that predates this plan.

**Proposed change**

Reconcile both files against reality once stages 1–5 land, and fold the README TODOs into this plan so there is one list rather than two.

---

## Sequence and why

Stages 1 and 2 first: `scripts/` because broken automation is the only category here that actively costs you something, and `starship/` because it is the largest single reduction for the least risk. Then `aliases/` and the formula audit, which both need your input per item. Then `lib/`, which is mechanical. Docs last, since they describe everything above.

The phased Homebrew upgrade sits outside this sequence and can happen whenever — it is independent of every stage here.

## Open questions, collected

1. `rollback-dotfiles.sh` — keep and fix, or drop?
2. `set-default-shell.sh` — keep for fresh machines, or drop?
3. Starship: cut the 56 dead blocks entirely, or keep as commented notes?
4. `nuke` — what provides it? Your global CLAUDE.md depends on it.
5. `bubo`, `diskspace_report` — yours or inherited?
6. `coreutils` — install it, or purge the `g`-prefixed assumptions?
7. `bear-templates` — keep as a submodule, or vendor and reach zero submodules?

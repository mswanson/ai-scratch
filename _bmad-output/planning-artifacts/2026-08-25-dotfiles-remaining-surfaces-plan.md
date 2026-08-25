# Dotfiles: Remaining Surfaces — Full Audit and Execution Plan

**Status: reviewed 2026-08-25, decisions folded in.** Every file outside `lib/`
has been read. Every proposed change is named by file and line, every removal
carries its reason, and every question you raised in review is answered below or
listed as still-open with a default.

Two things grew out of the review and are now their own stages: a full
alias-by-alias audit (Stage 2) and a full starship module-by-module audit
(Stage 3). Two more spawned separate plans, noted at the end.

Baseline: dotfiles `main` at `84b7294`, `make doctor` passing all 30 checks.

---

## What the review changed

| Your comment | Where | Decision now in the plan |
|---|---|---|
| "assume apple silicon, I don't have any Intel hardware" | Stage 1.1 | Hardcode `/opt/homebrew`. Drops the dual-arch branch here and simplifies `get_brew_prefix`. |
| "option 1 to see what's viable, then option 2 and pick" | Q1, `.macos` | Adopted. Stage 1.5 is now a two-phase probe-then-select. Upstream research answered below. |
| "are node and python the only languages I need?" | Stage 1.6 | Answered below. Recommendation: yes. Left open for your call. |
| "update ifactive to the modern equivalent" | Stage 2 | Fix, not delete. |
| "update undopush to use the current branch" | Stage 2 | Fix, not delete. |
| "AWS aliases, I don't know what these are for, kill them" | Stage 2 | Commented block deleted. The four live ones are in the Stage 2 table for a separate call. |
| "audit the remaining working aliases, likely cruft copy/pasted" | Stage 2.4 | Stage 2 is now a full audit of all 62 aliases, not just the broken ones. |
| "audit the full starship list, I don't use deno or dart but I do use docker" | Stage 3 | Stage 3 is now a module-by-module audit against installed tooling. |
| "let's fix the icons" | `[git_status]` | Concrete Nerd Font block proposed in Stage 3.3. |
| "not sure what this even does" | `[package]` | Explained below. |
| "just delete this, I don't use it" | `cc` alias | Deleted, not repaired. |
| "remove lua" / "remove them" | `Brewfile.cli` | `lua`, `unbound`, `rtmpdump` all removed. |
| "not sure I've ever used this" | `emptytrash()` | Proposing full deletion. |
| "I don't use sed, find, xargs often if at all" | Q4, coreutils | Settles it: purge, don't install. |
| "do I need any fonts at all" | Q5, fonts | Answered below: exactly one, and you already have it. |
| "add my ~/.claude setup to dotfiles" | Stage 6 | It is already there. Correction and the real gap below. |
| "give me the commands to run" | Manual steps | Copy-paste block at the end. |
| "add a plan for this" | Bootstrap reproducibility | Separate plan, written as a companion. |
| "should dotfiles be a monorepo?" | Stage 6 | Open question, framed below. |

---

## Answers to what you asked in review

### Are node and python the only languages asdf needs?

**Recommendation: yes, and it already is.** `asdf plugin list` returns exactly
`nodejs` and `python`, so nothing is being missed today.

Scanning `~/Code` for source files by extension, the only other languages present
are Ruby (87 files, all under `swimtopia/swimtopia-classic` and
`swimtopia-bravo`) and PHP (15 files, all under `clients/bluegriffin`). No Go,
Rust, Java, Elixir, Swift or Dart anywhere. TypeScript dominates at 314 files.

So the real question is narrower than "which languages": **do you still open the
swimtopia Ruby repos or the bluegriffin PHP client work?** If yes, those want
plugins so the versions are pinned rather than falling through to system `ruby`
(which macOS 26 still ships, deprecated) and a PHP you do not have installed at
all. If no, the current two-plugin setup is correct and complete.

One cleanup either way: `asdf list` shows stale installs. `nodejs 26.7.0` and
`python 3.10.2` are both installed and neither is in `.tool-versions`. Node 26.7
is what Homebrew's node pulled in before it was removed, and it is the ABI that
broke `qmd`. Proposing `asdf uninstall nodejs 26.7.0` and `asdf uninstall python
3.10.2`, which reclaims roughly 400 MB and removes the version that caused the
native-module crash.

### What does the starship `[package]` module do?

It reads the version number out of whatever package manifest is in the current
directory and shows it in the prompt. In a Node repo it reads `version` from
`package.json`; it also understands `Cargo.toml`, `pyproject.toml`,
`composer.json`, `*.gemspec` and about a dozen others.

So in `~/Code/dotfiles` it shows nothing (no manifest), and in a Node project it
would render something like `is v2.8.3`.

The note in the file, "Unnecessary for most of my projects (but not all of them)",
reads as someone deciding the version number is rarely what they need to know at a
glance. That is a reasonable call: the module cannot be conditional on the repo,
so it is all-or-nothing. **My recommendation is to leave it disabled.** You get
the same information from `cat package.json` when you actually want it, and the
prompt is already carrying eight segments.

### Do you need any fonts at all?

**One, and it is the one you already have.** `font-jetbrains-mono-nerd-font` is
not a typeface preference, it is load-bearing:

- iTerm's Normal Font is set to `JetBrainsMonoNFM-Regular 14`, which
  `setup-iterm.sh` configures.
- `color-ls` runs `eza --icons`, which renders file-type glyphs from the Nerd Font
  private-use range.
- Your starship prompt uses three Nerd Font glyphs today: `` (git branch), ``
  (nodejs), `` (python). Without the font those render as tofu boxes.

That is the "IIRC one of those fonts is for icons in the terminal" you were
remembering. It is not a separate icon font; Nerd Font *is* the patched version
that adds the icons to JetBrains Mono.

The other 63 in `Brewfile.fonts` are Google Fonts casks (abeezee, advent-pro,
amiri, barlow and its variants, and so on). None are installed, and with
Workspace serving fonts from the web there is nothing to install them for. See
Stage 5.2 for the proposal.

### Is there a maintained successor to `.macos`?

**No, and that is the finding.** I checked the two obvious candidates:

- **`mathiasbynens/dotfiles`** — the file you vendored. Last commit touching
  `.macos` was **2020-10-12**, nearly six years ago. macOS 11 Big Sur shipped a
  month later, so the script has never seen Big Sur, Monterey, Ventura, Sonoma,
  Sequoia, or 26. The repo itself is alive (2024 commits) but `.macos` is not
  being maintained.
- **`kevinSuttle/macOS-Defaults`**, which explicitly exists as "a centralized
  place for the awesome work started by @mathiasbynens on .macos" — last commit
  **2020-03-07**. Also dead.

The living resource is **[macos-defaults.com](https://macos-defaults.com/)**, last
updated December 2024. It is a per-command reference with animated demos and
version annotations rather than a script, which suits option 2 well: it is the
place to look up each setting you decide you want.

Conclusion: there is nothing newer to vendor. After the probe-and-select in
Stage 1.5, the vendored file has no further use and should go.

### Your Claude setup in the dotfiles repo

**It is already there, and has been.** Five things under `~/.claude` are tracked
in this repo and dotbot-linked:

| `~/.claude/...` | Tracked at |
|---|---|
| `CLAUDE.md` | `.claude/CLAUDE.md` (97 lines) |
| `RTK.md` | `.claude/RTK.md` (29 lines) |
| `settings.json` | `.claude/settings.json` (91 lines) |
| `statusline.sh` | `.claude/statusline.sh` (106 lines) |
| `hooks/` | `.claude/hooks/` (2 Python hooks, 167 lines) |

`install.conf.yaml:16-20` links all five. So the two files you named specifically,
the user-level CLAUDE.md and the statusline, are already versioned and travel with
the repo.

**What is genuinely not covered**, and what the question should be about:

- `~/.claude/skills/` is 26 symlinks into `~/.agents/skills`, which is the
  `forge-skills` repo. That repo is a spoke, versioned separately. The wiring
  between them is not reproducible from this repo; on a fresh machine nothing
  creates those 26 symlinks.
- `~/.claude/plugins/` is 239 MB of installed plugins. The *list* is declarative
  (`enabledPlugins` in `settings.json`, already tracked) but the install is not.
- `~/.claude/.claude.json` and `config.json` hold session state and credentials.
  These should **never** be tracked.
- Two untracked leftovers to delete: `~/.claude/statusline_BAK.sh` and
  `~/.claude/settings.json.bak`.

The skills-symlink wiring is the real gap, and it belongs in the bootstrap
reproducibility plan rather than here, since it is the same shape as the qmd and
codegraph problem.

---

## Corrections to the pre-review draft

Two claims in the first version were wrong. Keeping the record.

**"13 of 41 aliased commands are not on PATH" was a bad measurement.** It tested
PATH only, so it counted aliases and shell functions defined in this same repo as
missing. `nuke`, `bubo`, `diskspace_report` are aliases; `color-ls` is a function
in `exports/functions.sh:5`; `g` comes from the oh-my-zsh git plugin. Re-measured
with `whence -w` in a login shell, the genuinely-unresolvable list is five:
`pg_ctl`, `redis-cli`, `redis-server`, `pcregrep`, `greadlink`. Since the review,
`ngrep` joins them, found while auditing the network aliases.

**`scripts/` is 18 files and 1,693 lines, not 17 and 1,242.** The earlier count
omitted `scripts/README.md`, at 451 lines the largest file in the directory.

---

## Working tree

Two uncommitted changes exist and are **not** this plan's to touch:
`Brewfile.apps` has `mas "Okta Verify"` commented out by hand, and
`.claude/settings.json` carries accepted model/effort churn.

---

## Stage 0 — Safety net

1. `git tag pre-cleanup-2026-08-25` — one name to revert to.
2. `make doctor > /tmp/doctor-before.txt` — every stage diffs against this.
3. Confirm the two working-tree edits above are still the only dirt.

---

## Stage 1 — `scripts/`

### 1.1 `set-default-shell.sh` (28 lines) — rewrite, Apple Silicon only

The most dangerous file in the repo, broken three ways:

- **Line 9** calls `greadlink` (coreutils, not installed), so the script aborts
  before doing anything. That abort is the only thing currently protecting you
  from the next two bugs.
- **Lines 17 and 20 disagree.** It greps `/etc/shells` for
  `/opt/homebrew/bin/zsh` and, when that is missing, appends
  `/usr/local/bin/zsh`. On this machine the grep succeeds so the append is
  skipped and the bug hides. On a fresh machine it writes a path to a binary that
  does not exist.
- **Line 26** then runs `chsh -s /usr/local/bin/zsh` unconditionally, setting the
  login shell to that nonexistent binary. Recovery means Directory Utility or a
  rescue shell.

**Per your review, the rewrite assumes Apple Silicon.** `/opt/homebrew/bin/zsh` is
hardcoded, the same path in the grep and the append, with an existence check
before `/etc/shells` is touched and a skip when the login shell already matches.
Migrates to `lib/common.sh`.

That decision has one knock-on: `get_brew_prefix()` in `lib/common.sh:68-74`
exists only to branch between `/opt/homebrew` and `/usr/local`. Its sole caller is
`install-homebrew.sh:43`. Proposing it be simplified to return `/opt/homebrew`,
with `is_apple_silicon()` kept as a guard that errors on Intel rather than
silently doing the wrong thing. Cleaner than deleting the concept outright, and it
makes the assumption explicit rather than implicit.

**Testing limit:** the `chsh` line cannot be exercised here, since your login shell
is already correct, and `sudo` cannot prompt from this session. I will test path
derivation and the `/etc/shells` logic with the destructive lines stubbed, and
write that limitation into the script header.

### 1.2 `rollback-dotfiles.sh` (33 lines) — fix and keep

Same `greadlink` break at line 9. The intent is sound: find symlinks in `$HOME`
targeting the repo, unlink them, then trash generated files.

- Line 9: `BASH_SOURCE` idiom instead of `greadlink -f`.
- Line 13: source `lib/common.sh` instead of `functions.sh`.
- **Lines 24-25 deleted.** `.config/antigen` and `.antigenrc.zwc` are antigen
  artifacts; antidote replaced it and neither path is created any more.
- **Add** `.config/starship`, `.config/qmd`, `.cache/zsh` and
  `~/Library/LaunchAgents/com.litellm.versioncheck.plist`. All four are created by
  the current setup and none are cleaned up today.
- Add a `confirm()` prompt. A `make rollback` typo currently tears down the
  environment silently.

**Testing:** run against a throwaway `HOME=/tmp/rollback-test` with planted fake
symlinks, so the teardown logic is exercised without touching your real home
directory.

### 1.3 `scripts/functions.sh` (104 lines) — delete

After 1.1 and 1.2, nothing sources it. It is a near-duplicate of `lib/common.sh`
with divergent behaviour, which is a live trap: `error()` exits in one and does
not in the other, and `warn()` exists only in `lib/common.sh`, so a snippet moved
between scripts silently changes meaning. Its own line 2 sources
`./config/exports/functions.sh`, a path deleted in the reorganisation. Its
`clone_repo` and `asdf_plugin_update` helpers have no callers. Nothing in it is
worth carrying over.

### 1.4 `update.sh` (128 lines) — three edits

- **Lines 87-95 deleted.** Antigen cache block; the directory no longer exists.
- **Line 30, `brew upgrade`: gate behind `--upgrade`.** A blanket upgrade of all
  53 outdated packages is exactly what the phased plan exists to avoid. Default
  `make update` becomes `brew update` plus `brew bundle`; the upgrade moves behind
  a flag, with the reasoning in a comment.
- **Line 66, `npm update -g`: add a rebuild guard.** This is what broke `qmd`
  twice this session. Global npm packages with native modules compile against one
  `NODE_MODULE_VERSION` and crash silently when node moves. Stamp the node version
  to a file, compare after the update, and run `npm rebuild -g` when it changed.

### 1.5 `setup-macos-defaults.sh` + `lib/macOS-defaults/.macos` — probe, then select

Adopting your two-phase answer. The wrapper is fine; what it runs is not.

`.macos` is 1,044 lines written for OS X Yosemite: three references to "System
Preferences" (renamed in macOS 13), two `com.apple.dashboard` writes (Dashboard
removed in 10.15), two DiskUtility debug-menu writes, and a comment reading
"Disable transparency in the menu bar and elsewhere on Yosemite".

Two structural problems compound it. **Line 48 of the wrapper `source`s the file**,
so `set -e` applies to all 1,044 lines and the first failing `defaults write`
aborts the rest silently — the same failure shape as the `doctor.sh` bug fixed
earlier this session, which is why this script has almost certainly never
completed a run. And **lines 13-15 of `.macos`** start a `while true; do sudo -n
true; ... kill -0 "$$"; done &` sudo keepalive whose exit condition watches the
wrong process, because sourcing means `$$` is the parent shell.

**Phase A, the probe.** A throwaway script reads every `defaults write` out of
`.macos`, and for each one records the domain, the key, the current value, and
whether the domain still exists on macOS 26. Read-only; it writes nothing. Output
is a table: which settings still apply, which target dead domains, and which you
have already set differently by hand.

**Phase B, the selection.** You read that table and name the ones worth keeping. I
write those fresh into `scripts/setup-macos-defaults.sh` as a direct, executed
(not sourced) script with no `set -e` over the settings block, a per-setting
comment, and no sudo keepalive. `macos-defaults.com` is the reference for anything
you want that is not already in the list.

**Phase C.** `lib/macOS-defaults/` is deleted. Nothing else reads it, no upstream
is maintaining it, and its content will have been superseded by whatever survives
Phase B.

### 1.6 `install-asdf-languages.sh:34` — one line

`info "Node.js and Python take the longest. Go is usually faster."` Go was removed
in 2025-12; this is the fifth remnant found this session and the last I can
locate. Rewrite to name only the runtimes `.tool-versions` declares.

### 1.7 `Makefile:26-38` — `make help` hides three targets

The help output is built from three greps matching
`bootstrap|sync|update|doctor|clean`, `install-|setup-|verify-` and `macos|test`.
The `iterm`, `shell` and `rollback` targets match none of them, so all three have
`##` documentation that never prints. Add a fourth group, and label `rollback`
destructive in the help text rather than only in the target body.

### 1.8 `scripts/README.md` (451 lines) — rewrite to about 120

It documents 14 scripts; there are 17. Missing: `setup-iterm.sh`,
`set-default-shell.sh`, `rollback-dotfiles.sh`. It documents `functions.sh`
helpers that 1.3 deletes. Roughly 200 lines are generic shell-scripting advice
that is not specific to this repo.

Cut to a table of every script with purpose, entry point, and idempotency; keep
the `lib/common.sh` function reference; drop the tutorial sections and the emoji
headers.

---

## Stage 2 — `aliases/`: full audit

Rebuilt as a complete audit per your review. All 62 aliases across five files,
each with whether it works and a recommendation. **Nothing is cut without your
sign-off on this table**; strike any row you want kept.

Five categories: **FIX** (broken, worth repairing), **CUT** (broken or superseded),
**KEEP** (works, earns its place), and **?** (works, but I cannot tell if you use
it — these are the ones your "copy/pasted cruft" instinct is about).

### 2.1 Broken today

| # | Alias | File:line | What is wrong | Action |
|---|---|---|---|---|
| 1 | `ps` | `cli-utils.sh:59` | `alias ps="ps aux"` breaks every flag form. `ps -ef` returns `ps: illegal option -- f`. Verified. | **FIX** — rename to `psa`, leave `ps` alone |
| 2 | `urlencode` | `cli-utils.sh:62` | Python 2 syntax. Raises `SyntaxError` on any Python 3. Verified. | **FIX** — `urllib.parse.quote_plus` |
| 3 | `sshkey` | `dev-utils.sh:5` | Cats `~/.ssh/id_rsa.pub`, which does not exist. Your key is `id_ed25519.pub`. | **FIX** — and again in the 1Password migration |
| 4 | `netstat` | `network-utils.sh:31` | Missing the `alias` keyword, so it is a variable. `-p` also takes a protocol arg on BSD. | **CUT** |
| 5 | `clean_ds_store` | `cli-utils.sh:84` and `:91` | Defined twice, identically. | **FIX** — delete the second |
| 6 | `ifactive` | `network-utils.sh:11` | Needs `pcregrep`, not installed. | **FIX** per your review — `ifconfig \| grep -B4 "status: active"` |
| 7 | `undopush` | `dev-utils.sh:6` | Force-pushes to `master`; every repo here uses `main`. | **FIX** per your review — default to current branch, accept an optional branch arg |
| 8 | `nombom` | `dev-utils.sh:18` | Calls `rm -rf`, which hits your own `rm()` guard and prompts. Verified: `whence -w rm` returns `function`. | **FIX** — `command rm -rf` |
| 9 | `sniff` | `network-utils.sh:23` | Needs `ngrep`, not installed. Found during this audit. | **CUT** |
| 10 | `httpdump` | `network-utils.sh:24` | Hardcodes `en1`; your primary interface is `en0`. Verified. | **CUT** — see note below |
| 11 | `redis`, `rdserver` | `dev-utils.sh:25-26` | `redis-cli`/`redis-server` not on PATH. The `redis-stack-server` cask installs to `/Applications` and adds neither. Never worked here. | **CUT** |
| 12 | `pgreload`, `pgst` | `dev-utils.sh:28-29` | `pg_ctl` not installed; every Postgres CLI was removed this session. | **CUT** |
| 13 | `cc` | `dev-utils.sh:34` | Hardcoded `/Users/michaelswanson/...` path. | **CUT** per your review |

On #9 and #10: both are packet-capture tools for watching plaintext HTTP, which
barely exists now. If you want the capability back, `tcpdump` is installed and one
correct invocation beats two broken aliases.

### 2.2 Works, but likely cruft — your call on each

These are what your "copy/pasted from other places" instinct was pointing at.

| # | Alias(es) | File | What it does | Recommendation |
|---|---|---|---|---|
| 14 | `diskspace_report`, `free_diskspace_report` | macOS-utils | `df -P -kHl`, and an alias to the alias | **CUT both.** You named this one. `df -h` is shorter and you already know it |
| 15 | `bubo`, `bubc`, `bubu` | cli-utils | update+outdated, upgrade+cleanup, both | **CUT.** You named `bubo`. The phased-upgrade plan exists precisely because blanket `brew upgrade` is not what you want |
| 16 | `brewi`, `brewui`, `brewri`, `brewf`, `brewq`, `brewd` | cli-utils | 6 aliases saving 2-4 characters each on `brew install/uninstall/reinstall/info/search/doctor` | **CUT all 6.** They save less than they cost to remember, and `brew` has completion |
| 17 | `brews`, `casks`, `brservices`, `brtidy`, `bruse`, `brdeps` | cli-utils | list formulae/casks with versions, services, autoremove+cleanup, uses, deps | **KEEP.** These wrap flag combinations worth not retyping. Different class from #16 |
| 18 | `rsync-copy`, `rsync-move`, `rsync-update`, `rsync-sync` | cli-utils | 4 rsync flag sets | **?** Dropbox is gone and Google Drive syncs itself. If you have not run rsync this year, cut all four |
| 19 | `GET`/`HEAD`/`POST`/`PUT`/`DELETE`/`OPTIONS` | network-utils | 6 uppercase aliases wrapping `lwp-request` | **CUT.** They do resolve (Perl's libwww ships with macOS), but `httpie` is declared for this job and six single-word uppercase aliases is a lot of global namespace |
| 20 | `chromekill` | app-utils | Kills Chrome renderer processes | **CUT.** Chrome's own task manager (Window → Task Manager) does this with a UI |
| 21 | `fs` | cli-utils | `stat -f "%z bytes"` | **?** `ls -lh` covers it |
| 22 | `ismember` | cli-utils | `dseditgroup -o checkmember -m` | **CUT.** Directory-services group check; niche even for admin work |
| 23 | `setopt-list`, `setopt-reset` | cli-utils | zsh option introspection | **?** Useful when debugging shell config, invisible otherwise |
| 24 | `dockspace` | macOS-utils | Adds a Dock spacer tile | **?** Run once per machine, if ever |
| 25 | `hidedesktop`, `showdesktop` | macOS-utils | Toggle desktop icons for presenting | **KEEP** if you present from this machine, else cut the pair |
| 26 | `c` | cli-utils | `tr -d '\n' \| pbcopy` | **?** Single-letter alias for a pipe target |
| 27 | `map` | cli-utils | `xargs -n1` | **?** |
| 28 | `gurl` | network-utils | `curl --compressed` | **CUT.** curl negotiates compression by default for most servers now |
| 29 | `awswho`, `awslogin`, `awsprofiles`, `awsregion` | dev-utils | identity, SSO login, profile list, region | **?** Your review said "kill them" about the *commented* profile-switchers, which are gone. These four are live and `awscli` is installed. Confirm whether AWS is still in play at all |

### 2.3 Keeping, no action

`ls`, `l`, `cat`, `catp`, `nuke`, `sudo`, `path`, `finder`, `afk`, `plistbuddy`,
`zcompcleanup`, `clean_ds_store` (one copy), `gcm`, `codex`, `ip`, `localip`,
`ips`, `whois`, `flush`, `lscleanup`, `onport`.

All verified working. `ip`, `localip`, `ips` and `fs` were run and return correct
output. `afk`, `lscleanup` and `plistbuddy` reference absolute macOS paths that all
still exist on macOS 26.

### 2.4 Comment corrections

`dev-utils.sh` lines 3, 15 and 22 credit aliases to "OMZ plugins (see antigenrc)".
Antigen is gone; the file is `~/.zsh_plugins.txt`, tracked at
`symlinked/zsh_plugins.txt`, loaded by antidote. Three one-line fixes.

### 2.5 Net effect

If every CUT lands and the `?` rows go too: 62 aliases to roughly 30, with five
repairs. If only the CUTs land: 62 to about 38.

---

## Stage 3 — `starship/`: full module audit

Rebuilt as an audit per your review, rather than a bulk cut.

`starship.toml` is 269 lines defining **66 module blocks, 56 disabled.** The
`format` string names 16 modules, two of which (`$git_status`, `$package`) point
at disabled blocks. **Net: 10 of 66 affect the prompt.** A module not named in
`format` is inert regardless of its `disabled` value, so the 56 are dead twice
over. Lines 105-140 then repeat all 56 names again as commented format fragments.

### 3.1 Disabled modules that should be enabled

Checked every disabled module against what is actually installed.

| Module | Tool present? | Recommendation |
|---|---|---|
| `docker_context` | `docker` **yes** | **ENABLE.** You named this. Shows the active Docker context, which matters once you are running local model containers |
| `aws` | `aws` **yes** | **ENABLE if AWS is still live** (ties to alias row 29). Shows profile and region, which is the thing SSO sessions make easy to lose track of |
| `kubernetes` | `kubectl` **yes** | **?** `kubectl` is installed but nothing else here suggests active cluster work. Enabling it is cheap and it renders only inside a kube context |
| `sudo` | n/a | **?** Renders a marker while sudo credentials are cached. Genuinely useful, unrelated to any toolchain |
| `status` | n/a | **?** Shows the exit code of the last command. Many people consider this the single most useful non-default module |
| `jobs` | n/a | **?** Count of backgrounded jobs. Useful if you use `bg`/`fg` |
| `deno` | `deno` yes | **LEAVE DISABLED.** You said you do not use it; it is present only as a dependency |
| `java` | `java` yes | **LEAVE DISABLED.** System JDK, not your work |
| `rust`, `dart`, `php`, `elixir`, `terraform`, `helm`, `pulumi`, `gcloud`, `azure`, `conda`, `nix_shell`, `vagrant`, and 30+ others | **no** | **CUT.** Tool not installed and language not present in `~/Code` |

The full cut list is every module whose language or tool is absent: buf, c, cmake,
cobol, container, crystal, dart, dotnet, elixir, elm, erlang, haskell, helm,
hg_branch, julia, kotlin, lua, memory_usage, nim, nix_shell, ocaml, openstack,
perl, php, pulumi, purescript, red, rlang, rust, scala, singularity, spack, swift,
terraform, vagrant, vcsh, vlang, zig, azure, battery, conda, gcloud, localip,
shell, shlvl, time.

Two of those deserve a note rather than a silent cut: **`battery`** and
**`time`** are not toolchain-dependent and some people want them. Neither is in
your format string and both are disabled, so they have never rendered. Say the
word if either should come back instead.

### 3.2 Enabled modules that may be cruft

| Module | Currently | Note |
|---|---|---|
| `username` | enabled, `show_always = true` | Renders your username on every prompt, on a single-user laptop. **Recommend disabling** unless you like it |
| `hostname` | enabled, `ssh_only = false` | Same: renders on every local prompt. `trim_at = ".companyname.com"` is a placeholder that was never customised. **Recommend `ssh_only = true`**, so it appears when it actually tells you something |
| `git_commit` | enabled, `only_detached = true` | Correct as configured; shows the hash only in detached HEAD |
| `git_metrics` | enabled | `+added/-deleted` line counts on every prompt in a repo. **?** Some find this noise |
| `directory` | `truncation_length = 100` | Effectively no truncation. Fine, but deep paths will wrap |
| `nodejs`, `python`, `git_branch`, `git_state`, `cmd_duration` | enabled | **KEEP** all five |

### 3.3 `[git_status]` — the icons

You asked to fix these rather than leave the module parked. The block is disabled
today with the comment "disabled until I figure out a better set of icons",
and its format line is commented out.

Proposed, using Nerd Font glyphs consistent with the `` / `` / `` already in
your prompt:

```toml
[git_status]
disabled = false
format = '([$all_status$ahead_behind]($style) )'
conflicted = " ${count} "     # merge conflict
ahead      = "󰜷${count} "      # commits to push
behind     = "󰜮${count} "      # commits to pull
diverged   = "󰦎${ahead_count}/${behind_count} "
untracked  = " ${count} "     # new, unstaged
modified   = " ${count} "     # tracked, changed
staged     = " ${count} "     # in the index
renamed    = " ${count} "
deleted    = " ${count} "
stashed    = " ${count} "
up_to_date = ""
```

Two caveats worth stating rather than discovering: **glyph coverage varies**, so
this needs a visual check in your terminal before it lands, and I will render each
one to confirm before committing. And this makes the prompt noticeably busier in a
dirty repo, which is the whole point but is also the reason it was disabled.
Proposal: land it, live with it for a few days, and tune the count thresholds if
it is too loud.

### 3.4 Net effect

269 lines to roughly 95: the ten live modules, plus `docker_context`, plus a
configured `git_status`, plus whatever you enable from the `?` rows. Both dead
lists are replaced with a three-line comment stating the rule (a module renders
only if `format` names it) and pointing at `starship.rs/config`.

---

## Stage 4 — `exports/` and `symlinked/`

### 4.1 `exports/functions.sh:65-82`, `emptytrash()` — delete

You said "not sure I've ever used this", which settles what I was going to ask.
**Proposing deletion of the whole function**, not just the log branches.

For the record, the reasons it should go regardless: it runs `sudo /bin/rm -rvf
/var/log/*`, which on macOS 26 deletes files `newsyslog` and the unified logging
system own; its "clear Apple's System Logs to improve shell startup speed" comment
describes a macOS 10.11 problem; and it bypasses the `rm()` guard by calling
`/bin/rm` directly, so the repo ships both a safety rail and a documented way
around it.

Emptying the Trash is `Finder → Empty Trash` or `open ~/.Trash`. Nothing is lost.

### 4.2 `symlinked/zshenv.sh:3` — one line

Header says it loads from `~/.dotfiles/config/exports`. The path is
`~/.dotfiles/exports`.

### 4.3 Hardcoded home paths

Three `/Users/michaelswanson/` references in files meant to bootstrap a machine:

- `aliases/dev-utils.sh:34` (`cc`) — **deleted** per your review, so this resolves
  itself.
- `symlinked/gitconfig.sh:12` (`signingkey`) and `:68` (`allowedSignersFile`) —
  replace with `~/.ssh/...`; git expands `~` in both. The 1Password migration
  rewrites both again.

`config/litellm-stack/com.litellm.versioncheck.plist` hardcodes the path three
times, but launchd does not expand `$HOME` in plists. Platform constraint, not a
defect. Adding a comment saying so.

### 4.4 `config/git/common.gitconfig:69` — one word

`conflictstyle = diff3` → `zdiff3`. Same three-way view with common lines hoisted
out of the conflict hunks. Git 2.35+; you are on 2.54.

### 4.5 asdf: two stale runtime installs

`asdf list` shows `nodejs 26.7.0` and `python 3.10.2` installed and neither in
`.tool-versions`. Node 26.7 is the Homebrew-era version whose ABI broke `qmd`.
Proposing `asdf uninstall` for both. About 400 MB.

---

## Stage 5 — `brew/`

### 5.1 `Brewfile.cli` (103 lines)

**Reconciled against reality before the walkthrough**, so this starts from facts.

**Declared but not installed (4):** `aws-sam-cli`, `fd`, `httpie`, `tesseract`.
Legitimate manifest entries if you want them on a rebuild, which is the standing
rule. Worth a yes/no each. Note `fd` and `httpie` are both referenced by other
parts of this plan (`httpie` as the replacement for the uppercase HTTP aliases),
so declaring-and-installing them is the coherent choice if you keep those.

**Declared, satisfied by something else (3):** `jq` resolves to `/usr/bin/jq`,
macOS's own copy. `delta` and `openssl` are Homebrew *aliases* for `git-delta` and
`openssl@3`, both installed.

**That makes the "Name corrections" block at lines 94-103 wrong.** It declares
`git-delta`, `openssl@3` and `docker-desktop` as replacements while leaving the
originals above, but all three originals resolve: two are aliases and `cask
"docker"` still installs `docker-desktop` with a rename warning. So it is not a
fix, it is three packages declared twice. **Delete lines 94-103 and rename the
three entries in place**, keeping the comments.

**Removals confirmed in review:**

- `lua` (line 80) — annotated "used with Hammerspoon", which was cut this session.
  Verified: `brew uses --installed lua` returns nothing and it is a `brew leaves`
  entry, so nothing depends on it.
- `unbound` (line 81) — recursive DNS resolver, leaf, no dependents, no
  annotation, no reference anywhere in the repo.
- `rtmpdump` (line 82) — Flash streaming; the protocol is dead. Leaf. Almost
  certainly a `yt-dlp` dependency from before `yt-dlp` was declared on its own.

**`coreutils` (line 19, commented) — settled: do not install.** Your review said
you do not use `sed`, `find` or `xargs` often if at all, which removes the only
argument for it. After Stage 1 there are zero `g`-prefixed calls left, so
installing it would fix nothing still broken; it would only make it possible to
reintroduce the dependency without noticing. Deleting the commented line so the
question does not come back.

**The appended block, lines 67-92**, is the 22-entry "installed but never
declared" batch from 2026-08-22, parked so the audit could see it. The walkthrough
sorts the survivors into the functional sections above, the same treatment
`Brewfile.apps` got.

**Everything installed at top level is declared.** `brew leaves` against the
Brewfile came back clean once tap-qualified names were normalised. The manifest is
not missing anything you rely on.

### 5.2 `Brewfile.fonts` — cut 64 to 1

Per the font answer above: `font-jetbrains-mono-nerd-font` is load-bearing (iTerm's
configured font, `eza --icons`, and three starship glyphs), and it is the only one
installed. The other 63 are Google Fonts casks with nothing depending on them.

**Proposal: delete `Brewfile.fonts` and move the one entry into `Brewfile.cli`**,
next to the tools that need it, with a comment saying why it is not optional.

That also removes a wart: `Brewfile.fonts` is deliberately excluded from the
aggregator (`Brewfile.sh:34-35` says run it by hand), which means the one font
your terminal actually needs is not installed by `make bootstrap`. Folding it in
fixes a real fresh-machine gap.

If you would rather keep the 63 as a record, say so and they stay as a commented
block under the same rule as the Brewfile wishlists.

### 5.3 The phased upgrade — 53 outdated packages

Independent of every stage here. Three passes, verified separately:

1. Security and network: `openssl@3`, `ca-certificates`, `curl`, `gnupg`,
   `libnghttp2`, `libssh2`, `p11-kit`, `pinentry`.
2. Leaf CLI tools: everything else except the two below.
3. `zsh` and `asdf`, deliberately and separately, with a shell restart and `make
   doctor` between each. `zsh` is your login shell and `symlinked/zshenv.sh:11-24`
   documents the stale-FPATH hazard a `zsh` upgrade triggers.

`python@3.14` is in the outdated list. It is a Homebrew dependency, not your
runtime (asdf owns 3.12.7), so upgrading is safe, but worth confirming nothing
shifted afterward given the rogue-Python removal earlier this session.

---

## Stage 6 — `lib/` and repo weight

`.git` is **221 MB against a 977 KB packfile.** Effectively all of it is
`.git/modules/iTerm2-Color-Schemes`.

**`lib/iTerm2-Color-Schemes`** is 92 MB and now unreferenced: the two schemes you
use were vendored to `config/iterm/themes/` (16 KB) this session and
`setup-iterm.sh` reads them from there. Removal is the full sequence:

```
git submodule deinit -f lib/iTerm2-Color-Schemes
git rm -f lib/iTerm2-Color-Schemes
trash .git/modules/iTerm2-Color-Schemes
# strip the stanza from .gitmodules
```

Net reclaim: about 312 MB across working tree and `.git`.

**`lib/bear-templates`** (92 KB, your own repo, dotbot-linked to
`~/.config/bear/templates`) — vendoring it reaches zero submodules, which was the
stated §3 goal, and removes the "did you run `git submodule update`?" failure mode
from a fresh clone. The cost is that edits no longer flow back to the standalone
repo. Default: vendor.

**`lib/macOS-defaults`** — deleted in Stage 1.5 Phase C.

**Your monorepo question.** You raised it here and it is the right place to raise
it, but it is a bigger question than this plan should answer inline. Framing it so
it does not get lost:

The repo already behaves like a small monorepo. It carries shell config, Homebrew
manifests, Claude Code config, a LiteLLM Docker stack, iTerm themes, a qmd
collection registry, and vendored Bear templates. Those have genuinely different
lifecycles: `symlinked/` changes yearly, `.claude/settings.json` changes weekly,
`config/litellm-stack/` is a deployable subsystem with its own README.

The real questions are whether `forge-skills` and `bear-templates` should live
here rather than as separate repos, and whether `config/litellm-stack/` should be
extracted into one. **That is a structural decision with real consequences for
your BMAD hub-and-spoke setup**, and it deserves its own conversation rather than a
paragraph. Flagging it as the next planning topic after this cleanup lands.

---

## Stage 7 — Docs

Last, because they describe everything above.

### 7.1 `CLAUDE.md` (126 lines)

- **Line 17** claims `install.sh` "initializes and updates the Dotbot submodule".
  Dotbot is a Homebrew formula (`Brewfile.cli:11`); `install.sh` checks PATH.
  There is no dotbot submodule and never was.
- **Lines 21-28**, the whole "Updating Submodules" section, rests on that false
  premise.
- **Lines 58-61** list three submodules under `lib/`. After this plan there are
  zero, and `macOS-defaults` never was one.
- **Lines 40-43** omit `exports/litellm.sh`. The shell loading order at lines
  65-71 omits `~/.zshenv` → `exports/config.sh` (which runs *first*), the Homebrew
  command-not-found block, `z`, and the litellm toggle.
- **Line 38** lists `default-npm-packages.sh` but not `default-python-packages.sh`
  or `tool-versions.sh`.
- No mention of `config/litellm-stack/`, `config/qmd/`, or `config/iterm/themes/`.
- Nothing documents that `.claude/` is tracked here and linked into `~/.claude`,
  which is the single most surprising thing about this repo to a new reader, and
  which you had forgotten yourself.

### 7.2 `README.md` (230 lines)

- **Lines 5-22**, a seven-item TODO list, predates this plan. Two items are done
  (ARCHFLAGS and Apple Silicon paths). The rest are superseded by this document.
  Fold in and delete the section.
- **Line 26** says "Node 22 LTS". It is 24.19.0, which line 67 gets right.
- **Line 92** claims Python SDKs (anthropic, openai) are installed. Both are
  commented out in `symlinked/default-python-packages.sh:6-7`.
- **Line 98** lists Sourcetree, removed this session.
- **Line 230** says "macOS Sequoia+". You are on macOS 26.
- **Lines 126-146**, the structure block, omits `lib/`, `archive/`, `.claude/`
  and `.agents/`.

### 7.3 `install.conf.yaml:42-43`

A commented TODO about linking `~/Dropbox/Code/ssh` to `~/.ssh`. Dropbox is
uninstalled. The line is also evidence that SSH keys once lived in Dropbox, which
is real motivation for the 1Password migration, so it moves into that plan's
rationale rather than being deleted outright.

---

## Stage 8 — Verification

After each stage, not just at the end:

1. `make doctor`, diffed against `/tmp/doctor-before.txt`. Any new failure blocks
   the commit.
2. `zsh -lic 'exit'` clean, and `time zsh -lic exit` against the current baseline
   so no stage silently costs startup time.
3. `brew bundle check --file=~/.config/brew/Brewfile` after Stage 5.
4. `dotbot -d . -c install.conf.yaml` after any `install.conf.yaml` change, then
   confirm no `$HOME` symlink went dead.
5. `git status` clean except the two known user edits.

Commits: one per numbered item, on `main`, message explaining reasoning rather
than restating the diff.

---

## Still open

Four, each with a default so approval alone is enough to proceed.

**Q1. asdf plugins: do you still work in the swimtopia Ruby repos or the
bluegriffin PHP client work?** *Default: no, keep the two-plugin setup as is.*
Either way I will uninstall the two stale runtime versions.

**Q2. Are the four live AWS aliases still in play?** Your "kill them" was against
the commented profile-switchers, now gone. `awscli` and `aws-sam-cli` are declared
and the `[aws]` starship module hangs off the same answer. *Default: keep the four
aliases, enable the starship module.*

**Q3. Alias table `?` rows** (18, 21, 23, 24, 26, 27 in Stage 2.2). Six judgment
calls I cannot make for you: the rsync set, `fs`, the setopt pair, `dockspace`,
`c`, `map`. *Default: cut the rsync set, keep the rest.* Rsync had a clear purpose
under Dropbox and none now; the others are cheap.

**Q4. Starship `?` rows** (`kubernetes`, `sudo`, `status`, `jobs`, plus whether
`username`/`hostname`/`git_metrics` stay on). *Default: enable `status` and
`sudo`, leave `kubernetes` and `jobs` off, set `hostname` to `ssh_only = true`,
and disable `username`.* That trims two always-on segments and adds two that only
appear when they have something to say.

---

## Commands for you to run

You asked for these rather than a description. Copy-paste, in a real terminal
(`sudo` cannot prompt from a Claude Code session).

**The Finder pass** — root-owned or TCC-protected, so `trash` from a script fails:

```bash
# App Store apps are root:wheel; these need Finder, or sudo in a real terminal
sudo trash /Applications/Termius.app                 # 556 MB
sudo trash /Applications/OneDrive.app
sudo trash "/Applications/Adobe Acrobat Reader.app"
sudo trash "/Applications/Microsoft Teams classic.app"
sudo trash "/Applications/GPG Keychain.app"          # left by the gpg-suite uninstall
```

**The container folders** — `~/Library/Containers` is TCC-protected and refuses
deletion even with `sudo`. These have to go through Finder: open
`~/Library/Containers` in Finder (Cmd-Shift-G, paste the path) and delete:

```
it.bloop.airmail2                     (and the three other it.bloop.airmail2* folders)
com.readdle.smartemail-Mac
com.sequel-ace.sequel-ace
```

**Creative Cloud sync** — Core Sync has 63 minutes of CPU since 2026-07-12 syncing
a folder that does not exist, and `launchctl` cannot hold it down because the CC
app relaunches it. Creative Cloud → account menu → Preferences → Syncing → turn
off.

**Reclaim the space** — nothing above actually frees disk until this runs:

```bash
open ~/.Trash        # look before you empty
# then: Finder → Empty Trash    (~8 GB from this session)
```

**Stale asdf runtimes** — safe from any terminal, no sudo:

```bash
asdf uninstall nodejs 26.7.0     # the ABI that broke qmd
asdf uninstall python 3.10.2
```

**Untracked Claude leftovers**:

```bash
trash ~/.claude/statusline_BAK.sh ~/.claude/settings.json.bak
```

**Still needing a decision, not a command:** `~/Local Sites/txapa`, a 1.67 GB
WordPress site from 2023-08. Keep, export, or delete.

---

## Companion plans

- **Bootstrap reproducibility** — you asked for a plan; written as
  `2026-08-25-dotfiles-bootstrap-reproducibility-plan.md`. It covers qmd,
  codegraph, MCP registrations, the `~/.claude/skills` → `forge-skills` symlink
  wiring, LM Studio's model pulls, and the LiteLLM stack, none of which survive a
  fresh machine today.
- **Monorepo structure** — framed in Stage 6, deferred to its own conversation.
- **1Password SSH migration** — `2026-08-22-1password-ssh-agent-plan.md`, written
  and not started. Stage 4.3 touches the same two `gitconfig.sh` lines, so
  whichever runs second inherits the other's edit.

---

## Deliberately out of scope

- `.claude/` and `.agents/` content (805 lines). Live config that changes
  constantly. The *wiring* is in the bootstrap plan; the content is not cleanup
  territory.
- `archive/2025-12-modernization-guide.md` (1,977 lines). Correctly quarantined
  historical record, and the source of the Go decisions this session kept
  unwinding. Stays readable.
- `config/litellm-stack/` (7 files). A working subsystem with its own 332-line
  README and a loaded LaunchAgent (`com.litellm.versioncheck`, last exit 0).
- `config/qmd/index.yml`. Current; matches the ten collections qmd reports.

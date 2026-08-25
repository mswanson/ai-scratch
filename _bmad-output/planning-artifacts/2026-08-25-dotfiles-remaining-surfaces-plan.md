# Dotfiles: Remaining Surfaces — Full Audit and Execution Plan

**Status: EXECUTED 2026-08-25.** Stages 0-8 landed in ten commits on dotfiles
`main`, `15a3dcd..cddb948`, tagged `pre-cleanup-2026-08-25` beforehand. `make
doctor` passes identically to the baseline and shell startup is unchanged at
0.21s. Three things are deliberately outstanding and listed at the very bottom
under *What did not run*. Every file outside `lib/`
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

### Round two

| Your comment | Decision |
|---|---|
| "Cut nombom" | Cut, not fixed. Row 8. |
| "for redis and postgres do we need to install them to run locally? the CLIs are critical for agents" | Reverses rows 11-12. Answered below; both aliases stay and the CLIs get installed. |
| "keep brewi, brewui, brewf, kill the other 3" | Row 16 split. |
| "keep setopt-list setopt-reset" / "kill dockspace" / "kill `c`, `map`" | Rows 23, 24, 26, 27 settled. |
| "awscli is still in use but I don't need the alias, an agent runs the commands" | Row 29 cut. Starship `[aws]` still enabled; see below. |
| "keep the sudo, keep status" | Both enabled. |
| "hostname can go" | Removed from the block set and from `format`. |
| "use a sensible default for directory truncation" | `truncation_length = 3`. |
| "we should audit the installed packages" | New Stage 5.3, groundwork already done. |
| "no I don't" (swimtopia Ruby / bluegriffin PHP) | Q1 closed. asdf stays at two plugins. |
| "what is the difference between awscli and aws-sam-cli?" | Answered below. `aws-sam-cli` comes off the manifest. |

### Round three

| Your question | Answer |
|---|---|
| "how does `brew install redis` move the CLIs from stack server?" | It does not. Corrected below, and it turned up that Redis Stack is EOL and Redis 8 already contains the modules. Changes the recommendation. |
| "does postgres get installed with Beekeeper?" | No. Confirmed by searching the app bundle. `libpq` vs `postgresql@18` laid out below. |
| "agreed drop aws-sam-cli" | Done. Removed from the manifest in 5.1. |
| "what does tesseract do?" | OCR. Explained in 5.1, with the one reason to keep it. |
| "what are the gws-* skills?" | Google's official Workspace CLI skills. Answered in the bootstrap plan, whose Q1 this closes. |

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

### awscli vs aws-sam-cli, and do you need both?

Different scopes, and only one of them is yours.

**`awscli`** is the general-purpose AWS CLI v2. Every service, every API:
`aws s3 cp`, `aws sts get-caller-identity`, `aws sso login`. It is installed, it
is 200 MB, and `aws configure list-profiles` returns two real profiles
(`mswanson`, `1524-devops`), so it is genuinely in use.

**`aws-sam-cli`** is a narrow tool for one thing: the Serverless Application
Model. It builds Lambda functions, runs them locally in Docker (`sam local
invoke`), and deploys the CloudFormation stack behind them. It only does anything
in a directory containing a `template.yaml` and a `samconfig.toml`.

**You have no SAM projects.** I searched `~/Code` for `template.yaml`,
`template.yml` and `samconfig.toml` and found none, and no `package.json`
anywhere references `aws-lambda` or `serverless`. It is also declared but not
installed, so nothing has ever run it here.

**Recommendation: drop `aws-sam-cli` from `Brewfile.cli`.** It is a 
serverless-specific tool with no serverless work to do. Keep `awscli`. If Lambda
work starts later, one `brew install` restores it.

### Do redis and postgres need to be installed to run locally?

You framed this right: the GUIs are for you, the CLIs are for agents. The answers
differ, and the redis one turned out bigger than a PATH fix.

#### Redis: `brew install redis` does not move anything

Correcting the earlier wording, which was wrong. Homebrew formulae and casks are
separate installs; nothing gets relocated. What actually happens:

- The cask keeps its binaries in
  `/opt/homebrew/Caskroom/redis-stack-server/7.2.0-v3/bin/`. It links exactly one
  of them, `redis-stack-server`, into `/opt/homebrew/bin`. `redis-cli` and
  `redis-server` are deliberately left unlinked, which is why the aliases fail.
- `brew install redis` installs a **second, independent copy** and links *its*
  `redis-cli`, `redis-server`, `redis-benchmark` and `redis-sentinel` into
  `/opt/homebrew/bin`. The cask's copies stay where they are, unused.

So the honest description is "installs a current redis alongside the old one",
not "moves the CLIs".

**Which raises the better question, and it has a clean answer.** The formula is at
**redis 8.10.1**; the cask is **7.2.0-v3 from October 2023**. Two facts settle
what to do:

- **Redis 8 folded the Stack modules into core.** Search, JSON, TimeSeries, Bloom,
  cuckoo filter, top-k, count-min sketch and t-digest all ship in Redis Open
  Source 8. The standalone RediSearch / RedisJSON / RedisTimeSeries / RedisBloom
  modules are no longer separate things.
- **Redis Stack is end-of-life.** Maintenance releases for Stack 6.2, 7.2 and 7.4
  stopped in **December 2025**. Your 7.2.0-v3 is on a branch that stopped getting
  fixes eight months ago.

**Recommendation: `brew install redis`, then drop the `redis-stack-server` cask.**
One current, maintained package replaces a dead 2023 one and gives you strictly
more: the same modules, plus `redis-cli` and `redis-server` on PATH, plus `brew
services` to start and stop it. `redis-stack-redisinsight` (the GUI) is unaffected;
it talks to any Redis over the wire.

One thing to check before running it: the formula **conflicts with `valkey`**,
which is not installed here, so there is nothing in the way.

#### Postgres: nothing is installed, and Beekeeper does not help

Confirmed by searching inside the app bundle: **Beekeeper Studio ships no `psql`
and no `libpq`.** It is an Electron app using a JavaScript Postgres driver, so it
speaks the wire protocol itself and exposes no command-line tool. Nothing else on
the machine provides `psql`, `pg_ctl` or `pg_dump` either.

So this genuinely needs an install, and there are two shapes. Both are keg-only,
so both need linking or a PATH entry.

| | `libpq` 18.6 | `postgresql@18` 18.6 |
|---|---|---|
| Gives you | `psql`, `pg_dump`, `pg_restore`, `pg_isready` | all of that **plus** the server |
| Runs a database locally | no | yes, with a data directory and a `brew services` entry |
| Disk | small | larger, plus whatever the data directory grows to |
| Maintenance | none | initdb, version upgrades, a service to remember |

**Decided 2026-08-25: `libpq`.** It is the client set, which is exactly what "agents
need to interact with a database" means. Nothing in `~/Code` currently runs a
local Postgres: no `docker-compose.yml` references one, and the marshal project
uses Supabase, which is hosted. Installing the full server would add a service to
manage for a database that does not exist yet.

A comment goes in `Brewfile.cli` next to the entry recording the upgrade path, so
the next reader does not have to re-derive it: if a local server is ever needed,
`brew install postgresql@18` supersedes this and brings its own `psql`.

Either way **`pgreload` and `pgst` still go**: both call `pg_ctl`, which is a
*server* control command and is not in `libpq`. What you get back is `psql`, which
is the one you would actually use.

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
| 8 | `nombom` | `dev-utils.sh:18` | Calls `rm -rf`, which hits your own `rm()` guard and prompts. Verified: `whence -w rm` returns `function`. | **CUT** per round two |
| 9 | `sniff` | `network-utils.sh:23` | Needs `ngrep`, not installed. Found during this audit. | **CUT** |
| 10 | `httpdump` | `network-utils.sh:24` | Hardcodes `en1`; your primary interface is `en0`. Verified. | **CUT** — see note below |
| 11 | `redis`, `rdserver` | `dev-utils.sh:25-26` | `redis-cli`/`redis-server` are not on PATH. Corrected in round two: the cask **does** ship them, at `/opt/homebrew/Caskroom/redis-stack-server/7.2.0-v3/bin/`, which is not a PATH directory. | **KEEP** — `brew install redis` puts both in `/opt/homebrew/bin`. See the answer above |
| 12 | `pgreload`, `pgst` | `dev-utils.sh:28-29` | `pg_ctl` not installed, and it is a *server* control command that `libpq` does not carry. | **CUT** — but `brew install libpq` gets you `psql`, which is what agents actually need. See the answer above |
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
| 16 | `brewi`, `brewui`, `brewf` | cli-utils | `brew install`, `brew uninstall`, `brew info` | **KEEP** per round two — you use these |
| 16b | `brewri`, `brewq`, `brewd` | cli-utils | `brew reinstall`, `brew search`, `brew doctor` | **CUT** per round two |
| 17 | `brews`, `casks`, `brservices`, `brtidy`, `bruse`, `brdeps` | cli-utils | list formulae/casks with versions, services, autoremove+cleanup, uses, deps | **KEEP.** These wrap flag combinations worth not retyping. Different class from #16 |
| 18 | `rsync-copy`, `rsync-move`, `rsync-update`, `rsync-sync` | cli-utils | 4 rsync flag sets | **CUT all 4** (default, unchallenged in round two). Dropbox is gone and Google Drive syncs itself |
| 19 | `GET`/`HEAD`/`POST`/`PUT`/`DELETE`/`OPTIONS` | network-utils | 6 uppercase aliases wrapping `lwp-request` | **CUT.** They do resolve (Perl's libwww ships with macOS), but `httpie` is declared for this job and six single-word uppercase aliases is a lot of global namespace |
| 20 | `chromekill` | app-utils | Kills Chrome renderer processes | **CUT.** Chrome's own task manager (Window → Task Manager) does this with a UI |
| 21 | `fs` | cli-utils | `stat -f "%z bytes"` | **KEEP** (default, unchallenged in round two) |
| 22 | `ismember` | cli-utils | `dseditgroup -o checkmember -m` | **CUT.** Directory-services group check; niche even for admin work |
| 23 | `setopt-list`, `setopt-reset` | cli-utils | zsh option introspection | **KEEP** per round two |
| 24 | `dockspace` | macOS-utils | Adds a Dock spacer tile | **CUT** per round two |
| 25 | `hidedesktop`, `showdesktop` | macOS-utils | Toggle desktop icons for presenting | **KEEP** if you present from this machine, else cut the pair |
| 26 | `c` | cli-utils | `tr -d '\n' \| pbcopy` | **CUT** per round two |
| 27 | `map` | cli-utils | `xargs -n1` | **CUT** per round two |
| 28 | `gurl` | network-utils | `curl --compressed` | **CUT.** curl negotiates compression by default for most servers now |
| 29 | `awswho`, `awslogin`, `awsprofiles`, `awsregion` | dev-utils | identity, SSO login, profile list, region | **CUT all 4** per round two. AWS is still in use (two configured profiles), but an agent runs the commands and does not read your aliases |

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

Every row is now decided. **62 aliases down to 31**, with five repairs
(`ps`→`psa`, `urlencode`, `sshkey`, `clean_ds_store`, `ifactive`, `undopush`) and
two new brew installs (`redis`, `libpq`) that make rows 11 and 12 mean something
for the first time.

No `?` rows remain, so Stage 2 needs no further input.

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
| `aws` | `aws` **yes** | **ENABLE.** AWS is confirmed live: two configured profiles. You cut the aliases because an agent runs the commands, but the prompt segment is for you, and profile/region drift is exactly what SSO sessions make easy to lose track of |
| `sudo` | n/a | **ENABLE** per round two. Renders a marker while sudo credentials are cached |
| `status` | n/a | **ENABLE** per round two. Shows the exit code of the last command |
| `kubernetes` | `kubectl` **yes** | **LEAVE DISABLED** (default, unchallenged). `kubectl` is installed but nothing here suggests active cluster work |
| `jobs` | n/a | **LEAVE DISABLED** (default, unchallenged) |
| `deno` | `deno` yes | **LEAVE DISABLED.** Confirmed: `brew uses --installed deno` shows it is a **dependency of `yt-dlp`**, not something you chose |
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
| `hostname` | enabled, `ssh_only = false` | **REMOVE** per round two ("hostname can go"). Block deleted and `$hostname` dropped from `format`. That also retires the `trim_at = ".companyname.com"` placeholder nobody ever customised |
| `username` | enabled, `show_always = true` | **DISABLE** (default, unchallenged). Renders your username on every prompt of a single-user laptop |
| `directory` | `truncation_length = 100` | **CHANGE to 3** per round two. That is starship's own default and the sensible one: the last three path components, with the existing `truncation_symbol = "…/"` marking the elision. At 100 there is effectively no truncation, so a deep monorepo path pushes the rest of the prompt off-screen |
| `git_commit` | enabled, `only_detached = true` | **KEEP.** Correct as configured; hash only in detached HEAD |
| `git_metrics` | enabled | `+added/-deleted` counts on every prompt in a repo. **KEEP** (default, unchallenged) |
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

**269 lines to roughly 90.** The prompt ends up with these segments:
`directory`, the five git modules (`branch`, `commit`, `state`, `metrics`, and a
newly-configured `status`), `nodejs`, `python`, `docker_context`, `aws`, `sudo`,
`status`, `cmd_duration`, `character`.

Gone from the prompt: `username` (disabled) and `hostname` (deleted outright).
`package` stays disabled per the explanation above.

Both dead lists are replaced with a three-line comment stating the rule (a module
renders only if `format` names it) and pointing at `starship.rs/config`.

**One thing to watch.** That is five segments added against two removed, so the
prompt gets busier rather than simpler. Four of the five render only when they
have something to say, so a plain directory should be shorter than today; a dirty
repo on an AWS profile inside a Docker context will be noticeably longer. Worth
living with for a few days before tuning.

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

- **`aws-sam-cli` — remove from the manifest. Confirmed in round three.** No SAM
  projects exist and none ever have.
- **`fd` and `httpie` — install them.** Both are referenced by other parts of this
  plan (`httpie` is what replaces the six uppercase HTTP aliases in row 19), so
  declaring them and leaving them uninstalled is the incoherent state.
- **`tesseract` — needs a yes/no.** It is Google's open-source **OCR engine**:
  point it at an image or a scanned PDF and it returns the text. `tesseract
  receipt.jpg out` writes `out.txt`. It is the standard free alternative to
  commercial OCR, and it is what most "extract text from a photo" pipelines call
  underneath.

  Nothing in the repo or in `~/Code` references it, and it is declared but never
  installed, so it has done nothing here. It was probably declared for a
  document-scanning idea that did not happen. *Default: drop it.*

  **Decided 2026-08-25: drop it,** with this note carried into the recipe-corpus
  stub, because the choice is not obvious when that project starts.

  **Tesseract vs an LLM for OCR.** They fail differently, and the difference
  matters for recipes. Tesseract is deterministic pattern recognition: fast, free,
  offline, and it degrades *visibly* — bad input yields garbled text you can see
  is garbled. It is weak on handwriting, curved or skewed pages, columns, and
  anything with a decorative layout, which describes most recipe cards and
  cookbook scans. A vision LLM reads all of those far better, understands
  structure (this is the ingredient list, that is the method), and can emit
  Cooklang directly instead of raw text needing a second parsing pass.

  The catch is the failure mode: an LLM degrades *invisibly*. It will confidently
  produce a plausible quantity where the page was smudged, and "2 tsp" silently
  becoming "2 tbsp" is worse than no recipe at all. Any LLM OCR path needs a
  review queue; Tesseract's does not, because you can see it failed.

  Practical read for the recipe corpus: **use a vision LLM, with review.** The
  corpus is small enough that a human check per recipe is affordable, the sources
  are exactly what Tesseract is worst at, and going straight to Cooklang skips a
  whole conversion stage. Tesseract earns its place on clean typeset PDFs at
  volume, which is not the shape of this backlog. Reinstall is one command if that
  changes.

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

### 5.3 Audit what is actually installed

New, from round two: "we should audit the installed packages to see if I actually
need all of them." Stage 5.1 audits what is *declared*; this audits what is
*installed*, which is the different and better question.

Scope: the **45 `brew leaves`** entries, meaning top-level installs you asked for
rather than dependencies pulled in behind them. Same section-by-section
walkthrough as the apps audit.

Groundwork is done, so the walkthrough starts from evidence rather than guesses:

**Justified, no discussion needed.** The three largest unexplained entries turned
out to be one project's toolchain: `supabase` (155 MB), `auth0` (58 MB), and
`openfga` + `fga` (85 MB) are all referenced by `marshal/cool-story`, in its
`package.json` and its `deploy/local/*.env.example`. That is 298 MB with a clear
owner. Same for `awscli` (200 MB, two live profiles) and `ollama` (47 MB, behind
the LiteLLM stack).

**Already marked for removal in 5.1:** `lua`, `unbound`, `rtmpdump`.

**New candidates found while gathering this:**

- **`grc` (436 KB)** — a command-output colorizer that does nothing until you wrap
  commands in it. Grepped the entire repo: **no alias, function, or config
  references it.** It has never been wired up. This is the one you asked about
  early in the session; the answer is that it is inert.
- **`jid` (3.6 MB)** — interactive JSON digger. You have `jq` and `fzf`, which
  cover the same ground together. Worth a look.
- **`tmux` (1.4 MB)** and **`htop` (432 KB)** — both small, both classic, neither
  referenced anywhere in the repo. Cheap to keep, worth confirming you use them.
- **`bun` (60 MB)** — a leaf, so deliberately installed, but nothing in `~/Code`
  or the repo references it and node owns the runtime story here.
- **`redis-stack-server`** — not a formula, and no longer a question. Round three
  settled it: the installed cask is **7.2.0-v3 from October 2023**, Redis Stack
  maintenance ended **December 2025**, and Redis 8 ships all the Stack modules in
  core. **Replace it with `brew install redis`** and drop the cask. See the redis
  answer above.

**Confirmed-good, mentioned so they are not re-litigated:** `deno` is not a leaf;
it is a dependency of `yt-dlp`, which is why it appeared installed despite you
saying you do not use it.

### 5.4 The phased upgrade — 53 outdated packages

Runs after 5.3, so nothing gets upgraded that is about to be removed. Three
passes, verified separately:

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

**Round two closed all four.** Q1 answered "no I don't" (no swimtopia Ruby, no
bluegriffin PHP), so asdf stays at two plugins. Q2 answered: AWS is live but the
aliases go and the prompt module stays. Q3 and Q4 were answered row by row, and
every `?` in Stages 2 and 3 now has a decision.

Three things still need you, none of them blocking:

**A. `tesseract`** — OCR engine; declared, never installed, referenced nowhere.
*Default: drop it.* The only reason to hesitate is the recipe-corpus project,
which needs OCR as the first step of converting recipe photos and PDFs to
Cooklang. Close project: keep. Someday project: drop, and reinstall in one
command.

**A2. Postgres shape** — `libpq` (client only) or `postgresql@18` (client plus a
local server). *Default: `libpq`,* since nothing here runs a local Postgres today
and the marshal project uses hosted Supabase.

**B. Stage 5.3's new candidates.** `grc` (proven unwired), `jid`, `tmux`, `htop`,
`bun`, and the three-year-old `redis-stack-server`. That is a walkthrough, not a
question, and it happens when Stage 5 runs. Nothing needed from you first.

**C. Monorepo structure**, raised in your first review and framed in Stage 6.
Deferred to its own conversation, deliberately.

Everything else in this plan can run unattended.

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


---

## What did not run

Everything in Stages 0-8 landed except these, each for a stated reason.

**5.4, the phased Homebrew upgrade.** 53 packages are still outdated. This was
always independent of the cleanup, and it moves `zsh` (the login shell) and
`asdf` (which owns every runtime), so it wants its own session with a shell
restart and a `make doctor` between passes. `make upgrade` now exists for it.

**5.3's remaining candidates.** `lua`, `unbound` and `rtmpdump` were removed as
decided. Still installed and still unexplained: `grc` (proven to be referenced
by nothing in the repo), `jid`, `tmux`, `htop`, `bun`. All are small; none is
urgent. They need a yes/no each rather than analysis.

**`make macos` was not applied.** The new 85-setting script is written, tested
for syntax, and every domain verified live, but running it changes system
preferences. It prompts and defaults to No. Run it when you want the settings.

## Notes from execution

Three things came up while doing the work that the plan did not predict.

**The rollback script had a worse bug than `greadlink`.** It used `find $HOME
-maxdepth 1`, so it only ever saw links directly in `$HOME`. Today most are
deeper: `~/.claude/settings.json` at depth 2, `~/.config/starship/starship.toml`
and the litellm LaunchAgent at depth 3. A "rollback" would have left 8 of 10
links in place. Testing it against a throwaway `$HOME` is what found this, and
that same test proved `launchctl bootout` ignores `$HOME` and unloaded the live
litellm agent, which was bootstrapped straight back.

**The `cc` alias was shadowing the C compiler.** `alias
cc="/Users/michaelswanson/.asdf/shims/claude"` sat in front of `/usr/bin/cc`, so
any `cc foo.c` in an interactive shell launched Claude. It was slated for
removal as a hardcoded path; the shadowing was not noticed until the aliases
were verified in a live shell afterwards.

**Redis Stack could not uninstall itself.** `brew uninstall --cask
redis-stack-server` fails with `undefined method 'exists?' for class File`: the
October 2023 cask definition calls `File.exists?`, removed in Ruby 3, and the
error happens while *loading* the cask, so `--force` does not help either. The
Caskroom directory and its wrapper symlink went to the Trash instead, which is
what the uninstaller would have done. Redis 8 was smoke-tested
(start / ping / shutdown) afterwards.

# Dotfiles: Remaining Surfaces — Full Audit and Execution Plan

Every file in the repo outside `lib/` has now been read. This replaces the first
draft of this document, which was written from directory-level sampling and got
two things materially wrong (see *Corrections* below).

The plan is built to be executed autonomously: every proposed change is named
with its file and line, every removal carries its reason, and every open
question carries a **default** so a bare "approved" is enough to proceed. Nothing
has been changed yet.

Written 2026-08-25. Baseline: dotfiles `main` at `0186d0c`, `make doctor` passing
all checks, working tree carrying two user edits (see *Working tree*).

---

## Corrections to the first draft

Two claims in the earlier version were wrong, and one number was understated.
Correcting them here because both changed what the work looks like.

**"13 of 41 aliased commands are not on PATH" was a bad measurement.** It tested
PATH only, so it counted shell functions and aliases defined in this very repo as
missing. `nuke` is an alias in `aliases/cli-utils.sh:56`; `bubo` is one at line
20; `diskspace_report` is one in `macOS-utils.sh:16`; `color-ls` is a function in
`exports/functions.sh:5`; `g` comes from the oh-my-zsh git plugin loaded through
antidote. `ScreenSaverEngine`, `lsregister` and `PlistBuddy` are referenced by
absolute path and all three exist on macOS 26. Re-run in a real login shell with
`whence -w`, the genuinely-unresolvable list is five entries, not thirteen:
`pg_ctl`, `redis-cli`, `redis-server`, `pcregrep`, `greadlink`.

That kills questions 4 and 5 from the first draft. `nuke` is not missing, so the
global CLAUDE.md instruction that depends on it is sound.

**The real alias defects are different, and worse.** Reading the files instead of
probing PATH turned up five that actually misbehave today, including one that
silently breaks a command you would reach for by reflex. They are listed in
Stage 2.

**`scripts/` is 18 files and 1,693 lines, not 17 and 1,242.** The earlier count
omitted `scripts/README.md`, which at 451 lines is the largest file in the
directory and documents four scripts that no longer match reality.

---

## Working tree

Two uncommitted changes exist and are **not** this plan's to touch:

- `brew/brewfiles/Brewfile.apps` — `mas "Okta Verify"` commented out by hand
  after the session declared it. Owner's decision; leave it.
- `.claude/settings.json` — model and effort churn, accepted per
  `memory/claude-settings-scopes.md`.

Everything below assumes both stay as they are.

---

## Inventory

| Surface | Files | Lines | Verdict |
|---|---|---|---|
| `scripts/` | 18 | 1,693 | Highest defect density. Two scripts cannot run; one would break a shell if it could. |
| `aliases/` | 5 | 246 | Five live defects, one of them breaking `ps` for every flag form. |
| `starship/` | 2 | 277 | 66 module blocks, 56 disabled, 10 reachable. |
| `exports/` | 4 | 299 | Healthy. One stale path reference, one destructive function to review. |
| `symlinked/` | 15 | 433 | Healthy. Cleaned earlier this session; two portability items remain. |
| `brew/` | 4 | 330 | Aggregator fixed. `Brewfile.cli` never audited; `Brewfile.fonts` is 64 declared, 1 installed. |
| `config/` | 12 | — | Healthy. `litellm-stack/` is a working subsystem, not cruft. |
| `lib/` | — | 93 MB | One 92 MB submodule now unreferenced; `.git` is 221 MB against a 977 KB packfile. |
| Root docs | 6 | 560 | `CLAUDE.md` and `README.md` both describe a repo that no longer exists. |
| `archive/` | 1 | 1,977 | The 2025-12 modernization guide. Historical, correctly quarantined. |
| `.claude/`, `.agents/` | 7 | 805 | Live config, symlinked into `~/.claude`. Out of scope. |

**Verified healthy, so nobody re-checks:** every script in `scripts/` is reachable
from `bootstrap.sh`, the `Makefile`, or `update.sh`; every `install.conf.yaml`
link source exists on disk; every symlink in `$HOME` pointing into this repo is
dotbot-managed; `make doctor` passes all 30 checks; `config/git/common.gitconfig`
is wired in through `[include]` in `symlinked/gitconfig.sh` even though it is not
itself a dotbot link; and the `todoist` / `todoist-app` pair in the Caskroom is a
rename symlink, not a duplicate install.

---

## Stage 0 — Safety net

Before touching anything.

1. Tag the current state: `git tag pre-cleanup-2026-08-25`. Free, and gives one
   name to revert to rather than a sha to look up.
2. Capture the baseline: `make doctor > /tmp/doctor-before.txt`. Every stage ends
   by diffing against this.
3. Confirm the two working-tree edits above are still the only dirt.

---

## Stage 1 — `scripts/`

### 1.1 `set-default-shell.sh` (28 lines) — **rewrite**

This is the most dangerous file in the repo and the reason this stage goes first.

It is broken three separate ways:

- **Line 9** calls `greadlink`, from coreutils, which is not installed. The script
  aborts before doing anything. This is the only thing currently protecting you
  from the next two bugs.
- **Lines 17 and 20 disagree with each other.** It greps `/etc/shells` for
  `/opt/homebrew/bin/zsh` (the Apple Silicon path) and, when that is missing,
  appends `/usr/local/bin/zsh` (the Intel path). On this machine the grep
  succeeds, so the append is skipped, and the bug stays hidden. On a fresh Apple
  Silicon machine the grep fails and it writes a path to a binary that does not
  exist.
- **Line 26** then runs `chsh -s /usr/local/bin/zsh` unconditionally. On a fresh
  machine that sets the login shell to a nonexistent binary. Recovering means
  Directory Utility or a rescue shell.

Proposed rewrite: derive the shell path from `get_brew_prefix` in `lib/common.sh`
rather than hardcoding either architecture, verify the binary exists before
touching `/etc/shells`, use the same path in the grep and the append, and skip
`chsh` when the login shell already matches. Migrate to `lib/common.sh` and drop
`${0:A:h}` in favour of the `BASH_SOURCE` idiom the other fifteen scripts use.

**Testing note:** the `chsh` line cannot be exercised safely here, since your
login shell is already correct. I will test the path-derivation and the
`/etc/shells` logic with the destructive lines stubbed, and leave the real run
for a fresh machine. That limitation gets written into the script's header
comment so the next reader knows it is untested against the failure path.

### 1.2 `rollback-dotfiles.sh` (33 lines) — **fix and keep**

Same `greadlink` break at line 9. Beyond that it is sound in intent: it finds
symlinks in `$HOME` whose target is inside the repo and unlinks them, then trashes
a short list of generated files.

Changes:

- Line 9: replace `greadlink -f` with the `BASH_SOURCE` idiom.
- Line 13: source `lib/common.sh` instead of `functions.sh`.
- **Lines 24-25: delete.** `.config/antigen` and `.antigenrc.zwc` are antigen
  artifacts. Antigen was replaced by antidote and neither path is created any
  more.
- **Add** `.config/starship`, `.config/qmd`, `.cache/zsh` and
  `~/Library/LaunchAgents/com.litellm.versioncheck.plist` to the generated-files
  list. All four are created by the current setup and none are cleaned up today,
  so a rollback leaves them behind.
- Add a confirmation prompt using `confirm()` from `lib/common.sh`. A `make
  rollback` typo currently tears down the environment with no prompt.

**Testing:** run it against a throwaway `$HOME` (`HOME=/tmp/rollback-test`) with
a few fake symlinks planted, so the teardown logic is exercised without touching
the real home directory. That is the safe way to test a destructive script, and
it answers the first draft's open question about whether this is testable at all.

### 1.3 `scripts/functions.sh` (104 lines) — **delete**

Once 1.1 and 1.2 are done, nothing sources it. Deleting it removes a real trap:
it is a near-duplicate of `lib/common.sh` with subtly different behaviour, so
copying a snippet from one script into another silently changes what `error()`
does (`lib/common.sh` exits, `functions.sh` does not) and calls to `warn()`, which
only `lib/common.sh` defines, fail outright. Its own line 2 sources
`./config/exports/functions.sh`, a path that has not existed since the
reorganisation, and its `clone_repo` and `asdf_plugin_update` helpers have no
callers anywhere in the repo.

Nothing in it is worth carrying over. `confirm`, `is_installed`, `info`,
`success`, `error` all exist in `lib/common.sh`; `question` and `condition` have
no callers.

### 1.4 `update.sh` (128 lines) — **three edits**

- **Lines 87-95: delete the antigen cache block.** `~/.config/antigen` no longer
  exists; the block never fires.
- **Line 30, `brew upgrade`: gate behind a flag.** This is a blanket upgrade of
  all 53 outdated packages in one shot, which is exactly what the phased-upgrade
  plan exists to avoid. Proposal: default `make update` to `brew update` plus
  `brew bundle` (install what is declared and missing) and move the upgrade
  behind `./scripts/update.sh --upgrade`, with the reasoning in a comment.
- **Line 66, `npm update -g`: add a rebuild guard.** This is what broke `qmd`
  earlier in the session, twice over. Global npm packages with native modules
  (`better-sqlite3` inside qmd) are compiled against one `NODE_MODULE_VERSION`
  and silently crash when node changes underneath them. Proposal: follow the
  update with a `node --version` comparison against a stamp file, and run `npm
  rebuild -g` when it changed. Cheap, and it turns a confusing crash into a
  no-op.

### 1.5 `setup-macos-defaults.sh` (51 lines) + `lib/macOS-defaults/.macos` (1,044 lines) — **needs a decision, see Q1**

The wrapper is fine. What it runs is not.

`lib/macOS-defaults/.macos` is Mathias Bynens' well-known `~/.macos`, vendored.
It is a 1,044-line unconditional stream of `defaults write` commands written for
OS X Yosemite. Concrete evidence of age: three references to "System Preferences"
(renamed System Settings in macOS 13), two `com.apple.dashboard` writes (Dashboard
was removed in macOS 10.15), two `com.apple.DiskUtility` debug-menu writes, a
comment that literally reads "Disable transparency in the menu bar and elsewhere
on Yosemite", and a `com.apple.systempreferences` write against the retired app.

Two structural problems compound it:

- **Line 48 of the wrapper `source`s the file**, so `set -e` from the wrapper
  applies to all 1,044 lines. The first `defaults write` that fails against a
  domain macOS 26 no longer has aborts the run and the remaining settings never
  apply, silently. Same failure shape as the `doctor.sh` bug fixed earlier this
  session, and for the same reason.
- **Lines 13-15 of `.macos`** start an unkillable `while true; do sudo -n true;
  sleep 60; kill -0 "$$" || exit; done &` sudo keepalive. Because the file is
  sourced rather than executed, `$$` is the *parent* shell, so the loop's exit
  condition watches the wrong process.

I am not proposing to fix 1,044 lines of someone else's 2014 script. See Q1 for
the three real options.

### 1.6 `install-asdf-languages.sh` (49 lines) — **one line**

**Line 34**: `info "Node.js and Python take the longest. Go is usually faster."`
Go was removed from this repo in 2025-12. This is the fifth Go remnant found this
session and the last one I can locate. Change the line to name only the two
runtimes `.tool-versions` actually declares.

### 1.7 `Makefile` (117 lines) — **one fix**

The `help` target builds its output from three greps (lines 28, 33, 38) that
between them match `bootstrap|sync|update|doctor|clean`, `install-|setup-|verify-`
and `macos|test`. The `iterm`, `shell` and `rollback` targets match none of them,
so all three have `##` documentation that `make help` never prints. Add a fourth
group, "Optional", covering them. Note that `rollback` is destructive and should
be labelled as such in the help output, not just in the target body.

### 1.8 `scripts/README.md` (451 lines) — **rewrite to about 120**

It documents 14 scripts and there are 17. Missing entirely: `setup-iterm.sh`,
`set-default-shell.sh`, `rollback-dotfiles.sh`. It documents `functions.sh`
helpers that 1.3 deletes. Roughly 200 lines are generic shell-scripting advice
("Test Idempotency", "Adding a New Script", "Best Practices") that is not specific
to this repo and will not be read.

Proposal: cut to a table of every script with its purpose, its entry point (make
target or bootstrap step), and whether it is idempotent; keep the `lib/common.sh`
function reference, which is genuinely useful; drop the tutorial sections and the
emoji headers.

---

## Stage 2 — `aliases/`

Five live defects, then a set of judgment calls.

### 2.1 Defects to fix

| # | File:line | Defect | Fix |
|---|---|---|---|
| 1 | `cli-utils.sh:59` | `alias ps="ps aux"` breaks every other form. `ps -ef` becomes `ps aux -ef` and errors with `ps: illegal option -- f`. Verified. | Rename to `psa`. Leave `ps` alone. |
| 2 | `cli-utils.sh:62` | `urlencode` is Python 2 (`print ul.quote_plus(...)`, `import urllib as ul`). Raises `SyntaxError` on any Python 3. Verified. | Rewrite for `urllib.parse.quote_plus`. |
| 3 | `dev-utils.sh:5` | `sshkey` cats `~/.ssh/id_rsa.pub`. That file does not exist; your key is `id_ed25519.pub`. | Point at `id_ed25519.pub`. Flagged for the 1Password SSH plan, which changes this again. |
| 4 | `network-utils.sh:31` | `netstat="netstat -anp"` is missing the `alias` keyword, so it defines a shell variable, not an alias. Also `-p` on macOS `netstat` takes a protocol argument, so the intended command would fail anyway. | Delete. BSD `netstat` does not have the flag set this was written for. |
| 5 | `cli-utils.sh:84` and `:91` | `clean_ds_store` defined twice, identically. Verified as the only duplicated alias in the directory. | Delete the second. |

### 2.2 Removals proposed, with reasons

Each of these is a suggestion, per the standing rule. Confirming the plan
confirms the list; strike any line you want kept.

| # | Alias | File:line | Why it can go |
|---|---|---|---|
| 6 | `redis`, `rdserver` | `dev-utils.sh:25-26` | `redis-cli` and `redis-server` are not on PATH. You kept `redis-stack-server` as a cask, which installs into `/Applications` and does not put these on PATH. The aliases have never worked on this machine. |
| 7 | `pgreload`, `pgst` | `dev-utils.sh:28-29` | `pg_ctl` is not installed. Every Postgres GUI and CLI was removed this session except Beekeeper Studio, which does not provide it. |
| 8 | `ifactive` | `network-utils.sh:11` | Depends on `pcregrep`, not installed. Modern equivalent is `ifconfig | grep -B4 "status: active"`, which I would substitute rather than delete if you want the command. |
| 9 | `undopush` | `dev-utils.sh:6` | Force-pushes to `master`. Your `init.defaultBranch` is `main` and every repo here uses it, so this force-pushes to a branch that does not exist, or worse, to a stale one that does. |
| 10 | `GET`/`HEAD`/`POST`/`PUT`/`DELETE`/`OPTIONS` loop | `network-utils.sh:34-36` | Six uppercase aliases wrapping `lwp-request`. It does resolve (Perl's libwww ships with macOS), so these are not broken. But `httpie` is declared for exactly this job and six single-word uppercase aliases in the global namespace is a lot of surface for a tool you have not mentioned using. |
| 11 | `nombom` | `dev-utils.sh:18` | Runs `rm -rf`, which hits the `rm()` guard function in `exports/functions.sh` and prompts interactively. Verified: `whence -w rm` returns `function`. So the alias asks you to confirm a deletion it was written to make automatic. Fix by calling `command rm -rf` explicitly, or drop it. |
| 12 | Commented Python aliases | `dev-utils.sh:49-52` | Four commented lines pointing at `/usr/local/bin` Intel paths and a system Python 2. Dead on two counts. Unlike the Brewfile comments these record nothing worth keeping. |
| 13 | `sudo` in the AWS block | `dev-utils.sh:44-47` | Three commented `awsprod`/`awsdev`/`awspersonal` profile aliases. Keep or cut is your call; they are a template's suggestion, not a decision you made. |

### 2.3 Comment corrections

`dev-utils.sh` lines 3, 15 and 22 all credit aliases to "OMZ plugins (see
antigenrc)". Antigen is gone; the file is `~/.zsh_plugins.txt`, tracked at
`symlinked/zsh_plugins.txt`, loaded by antidote. Three one-line fixes.

### 2.4 Keeping, explicitly

`nuke`, `bubo`, `diskspace_report`, `color-ls`, `afk`, `lscleanup`, `plistbuddy`
and the whole rsync and Homebrew groups all resolve and work. The first draft
implied otherwise. No action.

---

## Stage 3 — `starship/`

`starship.toml` is 269 lines defining **66 module blocks. 56 carry `disabled =
true`.** The `format` string at lines 16-31 names 16 modules, and two of those
(`$git_status`, `$package`) point at blocks that are disabled, so they render
nothing. Net: **10 of 66 blocks affect the prompt.**

Starship renders only what `format` names. A module block that is not in the
format string is inert regardless of its `disabled` value, so the 56 are dead
twice over. They cover cobol, crystal, elm, erlang, haskell, julia, nim, ocaml,
perl, purescript, red, scala, vlang, zig, and about forty more.

The file also carries a second copy of the same list: lines 105-140 are a
commented "Disabled Modules" block repeating every one of those names as a
`# $modulename\` format fragment.

**Proposed change:** cut to the ten live blocks plus the format string, and
replace both dead lists with a three-line comment stating the rule (a module
appears only if it is in `format`, and the full list is at
`starship.rs/config`). 269 lines to roughly 80.

Two blocks need a decision rather than a cut, because they are in `format` but
disabled, which means someone turned them off deliberately:

- `[git_status]` carries the comment "disabled until I figure out a better set of
  icons". That is a parked intent, not cruft. Proposal: leave it disabled with the
  comment intact.
- `[package]` carries "Unnecessary for most of my projects (but not all of them)".
  Same reading. Leave it.

See Q2 for whether the 56 come back as comments.

---

## Stage 4 — `exports/` and `symlinked/`

Both directories were cleaned earlier this session and are in good shape. Four
items remain.

### 4.1 `exports/functions.sh:65-82`, `emptytrash()` — **review, see Q3**

It runs `sudo /bin/rm -rvf` against `/var/log/*`, `/Library/Logs/*`,
`$HOME/Library/Logs/*`, `/Volumes/*/.Trashes` and `/private/var/log/asl/*.asl`.
Three concerns, in order of seriousness:

- `sudo /bin/rm -rvf /var/log/*` on macOS 26 deletes system log files that
  `newsyslog` and the unified logging system expect to own. It predates the
  unified log (macOS 10.12) and the "clear Apple's System Logs to improve shell
  startup speed" comment describes a problem that no longer exists.
- It bypasses the `rm()` guard by calling `/bin/rm` directly, which is correct for
  its purpose but means the repo contains both a safety rail and a documented way
  around it.
- The no-argument path (`/bin/rm -rfv $HOME/.Trash/*`) is the useful one and is
  the only part I would keep.

### 4.2 `symlinked/zshenv.sh:3` — **one line**

The header says it loads from `~/.dotfiles/config/exports`. The path is
`~/.dotfiles/exports`. Same stale path as the one in `scripts/functions.sh`, from
the same reorganisation.

### 4.3 `aliases/dev-utils.sh:34` and `symlinked/gitconfig.sh:12,68` — **portability**

Three hardcoded `/Users/michaelswanson/` paths in files that are meant to
bootstrap a new machine:

- `alias cc="/Users/michaelswanson/.asdf/shims/claude"` — replace with
  `claude`, which the asdf shims directory already puts on PATH (`exports/paths.sh:26`).
- `gitconfig.sh:12` `signingkey` and `:68` `allowedSignersFile` — replace with
  `~/.ssh/...`. Git expands `~` in both. This also matters for the 1Password SSH
  migration, which rewrites both lines again.

`config/litellm-stack/com.litellm.versioncheck.plist` also hardcodes the path
three times, but launchd does not expand `$HOME` in plists, so that one is a
platform constraint rather than a defect. Leaving it, with a comment saying why.

### 4.4 `config/git/common.gitconfig:69` — **one line**

`conflictstyle = diff3`. Git 2.35 added `zdiff3`, which is the same three-way
view with the common lines hoisted out of the conflict hunks. Strictly better, one
word.

---

## Stage 5 — `brew/`

### 5.1 `Brewfile.cli` — the audit, with the reconciliation already done

Ran `brew bundle list` against `brew list` to get the real diff before the
walkthrough, so the audit starts from facts rather than guesses.

**Declared but not installed (4):** `aws-sam-cli`, `fd`, `httpie`, `tesseract`.
All four are legitimate manifest entries if you want them on a rebuild; that is
the standing rule for `Brewfile.apps` and applies here too. Worth a yes/no each.

**Declared, satisfied by something else (3):** `jq` resolves to `/usr/bin/jq`,
macOS's own copy, so Homebrew's is not installed. `delta` and `openssl` are
Homebrew *aliases* for `git-delta` and `openssl@3`, both installed.

**That last point makes the "Name corrections" block at lines 94-103 wrong.** It
declares `git-delta`, `openssl@3` and `docker-desktop` as replacements for
`delta`, `openssl` and `docker` while leaving the originals in place above. But
all three originals resolve: two are aliases, and `cask "docker"` still installs
`docker-desktop` with a rename warning. So the block is not a fix, it is a
duplicate declaration of three packages. Proposal: delete lines 94-103 and rename
the three entries in place, in their sections, keeping the comments.

**The appended block at lines 67-92** is the "installed but never declared" batch
from 2026-08-22, parked there so the audit could see it. Twenty-two entries. The
walkthrough sorts them into the functional sections above, the same treatment
`Brewfile.apps` got.

**Three entries need your call specifically:**

- `lua` (line 80). Its only annotation said "used with Hammerspoon", and
  Hammerspoon was cut this session. Checked: `brew uses --installed lua` returns
  nothing and it is a `brew leaves` entry, so nothing on this machine depends on
  it and nothing in the repo references it. Its reason for being here is gone.
- `unbound` and `rtmpdump` (lines 81-82). Both landed in the appended
  never-declared block on 2026-08-22 without annotations. Both are leaves with no
  dependents. `unbound` is a recursive DNS resolver, `rtmpdump` a Flash streaming
  tool whose protocol is dead; `rtmpdump` is most likely a leftover `yt-dlp`
  dependency from before it was declared on its own. Neither has an obvious
  reason to be installed.
- `coreutils` (line 19, commented). This is the `greadlink` decision. See Q4.

**Everything installed at top level is declared.** `brew leaves` against the
Brewfile came back clean once tap-qualified names were normalised. That is a good
result and worth stating: the manifest is not missing anything you rely on.

### 5.2 `Brewfile.fonts` — 64 declared, 1 installed

Only `font-jetbrains-mono-nerd-font` is installed, and it is the one
`setup-iterm.sh` configures iTerm to use. The other 63 are Google Fonts casks:
abeezee, advent-pro, amiri, barlow and its two width variants, and so on.

The file is deliberately excluded from the `brew bundle` aggregator
(`Brewfile.sh:34-35` says to run it by hand). So it costs nothing today. But as a
new-machine manifest it would install 63 fonts you have not used on this machine.

See Q5.

### 5.3 The phased upgrade — 53 outdated packages

Independent of every stage here and unchanged from the earlier plan: security and
network formulae first (`openssl@3`, `ca-certificates`, `curl`, `gnupg`,
`libnghttp2`, `libssh2`, `p11-kit`, `pinentry`), then leaf CLI tools, then `zsh`
and `asdf` deliberately with a shell restart and `make doctor` between each.

`zsh` is your login shell and `symlinked/zshenv.sh:11-24` documents the stale-FPATH
hazard that a `zsh` upgrade triggers, which is exactly why it goes last and alone.

One addition since the earlier plan: `python@3.14` is in the outdated list. It is
a Homebrew dependency, not your runtime (asdf owns 3.12.7), so upgrading it is
safe, but it is worth confirming nothing shifted after it lands, given the
rogue-Python-3.13 removal earlier this session.

---

## Stage 6 — `lib/` and repo weight

`.git` is **221 MB against a 977 KB packfile.** Effectively all of it is
`.git/modules/iTerm2-Color-Schemes`.

`lib/iTerm2-Color-Schemes` is 92 MB on disk and **now unreferenced**: the two
schemes you use were vendored to `config/iterm/themes/` (16 KB total) earlier this
session and `setup-iterm.sh` reads them from there. Removal is the full sequence,
not a `git rm`:

```
git submodule deinit -f lib/iTerm2-Color-Schemes
git rm -f lib/iTerm2-Color-Schemes
trash .git/modules/iTerm2-Color-Schemes
# then strip the stanza from .gitmodules
```

Net reclaim: about 312 MB across the working tree and `.git`.

`lib/bear-templates` (92 KB) is your own repo, dotbot-linked to
`~/.config/bear/templates`, and live. See Q6.

`lib/macOS-defaults` (72 KB) is a plain vendored directory, not a submodule
despite what `CLAUDE.md` claims. Its fate follows Q1.

---

## Stage 7 — Docs

Both root docs describe a repo that does not exist. They go last because they
document everything above.

### 7.1 `CLAUDE.md` (126 lines)

- **Line 17** claims `install.sh` "initializes and updates the Dotbot submodule".
  Dotbot is a Homebrew formula (`Brewfile.cli:11`) and `install.sh` checks for it
  on PATH. There is no dotbot submodule and has not been one.
- **Lines 21-28**, the entire "Updating Submodules" section, is built on that
  false premise.
- **Lines 58-61** list three submodules under `lib/`. One is going away, one
  (`macOS-defaults`) never was a submodule.
- **Lines 40-43** omit `exports/litellm.sh`, and the shell loading order at lines
  65-71 omits `~/.zshenv` → `exports/config.sh` (which runs *first*), the
  Homebrew command-not-found block, `z`, and the litellm toggle.
- **Line 38** lists `default-npm-packages.sh` but not `default-python-packages.sh`
  or `tool-versions.sh`.
- No mention of `config/litellm-stack/`, `config/qmd/`, or `config/iterm/themes/`.

### 7.2 `README.md` (230 lines)

- **Lines 5-22**, a seven-item TODO list, predates this plan. Two items are done
  (ARCHFLAGS and the Apple Silicon paths, both correct since this session); the
  rest are either superseded by this plan or belong in it. Proposal: fold into
  this document and delete the section.
- **Line 26** says "Node 22 LTS". It is 24.19.0, which line 67 gets right.
- **Line 92** claims "Python SDKs (anthropic, openai)" are installed. Both are
  commented out in `symlinked/default-python-packages.sh:6-7`.
- **Line 98** lists Sourcetree, removed this session.
- **Line 230** says "macOS Sequoia+". You are on macOS 26.
- **Lines 126-146**, the structure block, omits `lib/`, `archive/`, `.claude/`
  and `.agents/`.

### 7.3 `install.conf.yaml:42-43`

A commented TODO about linking `~/Dropbox/Code/ssh` to `~/.ssh`. Dropbox is
uninstalled. The line is also evidence that SSH keys once lived in Dropbox, which
is real motivation for the 1Password migration, so it moves into that plan's
rationale rather than just being deleted.

---

## Stage 8 — Verification

After each stage, not just at the end:

1. `make doctor`, diffed against `/tmp/doctor-before.txt`. Any new failure blocks
   the commit.
2. `zsh -lic 'exit'` clean, and `time zsh -lic exit` compared against the current
   baseline so a stage does not silently cost startup time.
3. `brew bundle check --file=~/.config/brew/Brewfile` after Stage 5.
4. `dotbot -d . -c install.conf.yaml` after any `install.conf.yaml` change, then
   confirm no symlink in `$HOME` went dead.
5. `git status` clean except the two known user edits.

Commits: one per numbered item, on `main`, message explaining the reasoning rather
than restating the diff. That is the pattern the 37 commits from this session
already follow.

---

## Open questions

Six. Each has a default, so approving the plan without answering any of them is
enough for me to proceed.

**Q1. `lib/macOS-defaults/.macos` — what happens to 1,044 lines of Yosemite-era
`defaults write`?**

Three options:

1. **Prune to what still works.** I test each `defaults` domain against macOS 26
   and keep the ones that apply. Real work, maybe 200 surviving lines, and it
   gives you a macOS setup step that actually functions.
2. **Cut to a short list you actually care about.** You tell me the ten or fifteen
   settings worth automating; I write those fresh. Smaller and more honest than
   pruning someone else's list.
3. **Delete the whole thing**, along with `setup-macos-defaults.sh` and the `make
   macos` target. macOS settings get configured by hand once per machine.

*Default if you say nothing: option 3.* The script has never run successfully on
this machine (the `set -e` bug guarantees it would abort partway), so deleting it
removes something that does not work rather than something you would miss. Option
1 is a lot of testing for a script run once every few years.

**Q2. Starship: do the 56 dead module blocks come back as comments?**

*Default: no, cut them.* A starship block is three lines regenerated from
`starship.rs/config` in seconds, unlike an App Store id. The commented
"Disabled Modules" list at lines 105-140 already serves as the record of what was
considered, and I would keep a trimmed version of that as the single note.

**Q3. `emptytrash()` — what stays?**

*Default: keep the trash-emptying, drop the log deletion.* That is `/bin/rm -rfv
$HOME/.Trash/*` and its dotfile twin, and nothing else. The `all` and `user`
branches delete system and user logs, which on macOS 26 is at best useless (the
unified log is not in those files) and at worst breaks `newsyslog`. If you use
`emptytrash -a` regularly, say so and I will keep it with the `/var/log` line
removed.

**Q4. `coreutils` — install it, or purge the `g`-prefixed assumptions?**

*Default: purge.* Four scripts have broken on missing `greadlink` this session.
After Stage 1 there are zero `g`-prefixed calls left, so installing coreutils
would fix nothing that is still broken; it would just make it possible to
reintroduce the dependency without noticing. A bootstrap script should not depend
on optional tooling. Installing it is defensible if you want GNU `sed`, `find` and
`xargs` interactively, but note you already have `gnu-sed` and `grep` declared
separately.

**Q5. `Brewfile.fonts` — 64 fonts, 1 installed. What is it for?**

Three readings, and I cannot tell which is right: an aspirational wishlist, a
snapshot of a machine you no longer have, or a genuine "install all of these on a
rebuild" manifest.

*Default: keep the file, keep it out of the aggregator, and add a header saying
it is a wishlist rather than a manifest.* That is a comment-only change and
preserves everything. But if you want it to be a real manifest I would cut it to
the fonts you use, which appears to be one.

**Q6. `lib/bear-templates` — submodule or vendor?**

92 KB, your own repo, dotbot-linked and live. Vendoring it reaches zero submodules
in this repo, which was the stated §3 goal, and removes the "did you `git
submodule update`?" failure mode from a fresh clone. The cost is that edits no
longer flow back to the standalone repo.

*Default: vendor it,* on the grounds that zero submodules was the goal and the
templates are small and stable. Say the word if that standalone repo is still
somewhere you edit from.

---

## Sequence

Stage 0, then 1, 2, 3, 4, 5, 6, 7, verifying after each.

Stage 1 first because broken automation is the only thing here that actively costs
you something, and `set-default-shell.sh` is the one file in the repo that could
lock you out of a machine. Stage 2 next because two of its defects (`ps`,
`urlencode`) affect commands you would type today. Stage 3 is the largest
reduction for the least risk. Stages 4-6 are mechanical. Docs last, since they
describe all of it.

The phased Homebrew upgrade (5.3) is independent and can happen at any point.

---

## What cannot be done autonomously

Flagging these up front so approval is not mistaken for "this all completes
unattended":

- **Anything requiring `sudo`.** It cannot prompt from a Claude Code shell or from
  the `!` prefix. This affects testing `set-default-shell.sh` end to end, and any
  Q1 option other than deletion.
- **`chsh`.** Same reason, plus it should not be exercised on a working machine.
- **The `make rollback` real-world path.** I will test it against a throwaway
  `$HOME`; running it against your actual home directory is not something I will
  do.
- **The Finder pass** carried over from the last session (Termius at 556 MB,
  OneDrive, Adobe Acrobat Reader, Microsoft Teams classic, GPG Keychain, six
  `~/Library/Containers` folders). TCC-protected; needs Finder or Full Disk Access
  for VS Code.
- **Emptying the Trash**, which is what actually reclaims the ~8 GB from this
  session plus the ~312 MB from Stage 6.

---

## Deliberately out of scope

- `.claude/` and `.agents/` (805 lines). Live config, symlinked into `~/.claude`,
  changing constantly. Not cleanup territory.
- `archive/2025-12-modernization-guide.md` (1,977 lines). Correctly quarantined
  historical record. It is the source of the Go decisions this session kept
  unwinding, so it stays readable.
- `config/litellm-stack/` (7 files). A working subsystem with its own 332-line
  README and a loaded LaunchAgent (`com.litellm.versioncheck`, last exit 0).
  Nothing to clean.
- `config/qmd/index.yml`. Current, and the collection list matches the ten
  collections qmd reports.
- **§4 bootstrap reproducibility**, still the largest unaddressed gap in this
  repo: qmd, codegraph, MCP registrations, the skills chain and the LiteLLM stack
  are all hand-installed and none are in `make bootstrap`. That is a project, not
  a cleanup pass, and it deserves its own plan rather than being smuggled into
  this one.

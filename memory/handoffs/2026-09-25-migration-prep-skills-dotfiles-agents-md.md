---
date: 2026-09-25
topic: "migration-prep-skills-dotfiles-agents-md"
repos:
  - "ai-scratch"
  - "forge-skills"
  - "dotfiles"
status: open
---

## Authoritative context

Read these first; they settle things this handoff does not repeat.

- `memory/handoffs/2026-08-28-dotfiles-app-prefs-and-uat-runbook.md` — still
  `status: open` and still the dotfiles baseline: the UAT runbook in dotfiles
  `docs/uat.md` has never been executed, Alfred is not live from the repo, VS
  Code (gap 4) is undecided, the phased Homebrew upgrade and `make macos` have
  not run. This handoff adds to it; it does not replace it.
- `memory/handoffs/2026-08-25-forge-skills-pr-wrapup.md` — `status: open`. PR #4
  has since merged, but its post-merge sweep, worktree cleanup and the 82-entry
  ledger in `_bmad-output/implementation-artifacts/deferred-work.md` are still
  pending. The 8 worktrees under `~/Code/forge-skills-worktrees/` plus
  `~/Code/forge-skills-opus` (PR #12, merged) are all still on disk.
- forge-skills `skills/operate-bmad-loop/references/pins.md` (working tree on
  branch `operate-bmad-loop/pin-v0.12.0`) — the pin table, the freshness-check
  procedure, and the new "v0.12.0 behavior notes" section. Everything about
  what v0.12.0 changed lives there, not here.
- dotfiles `scripts/install-claude-code.sh` header — the recorded reasoning for
  the native installer over npm; this session extended the same reasoning to
  "over Homebrew" (below) and the opposite call for the Slack CLI.
- Claude Code AGENTS.md support: `https://code.claude.com/docs/en/memory` and
  the 2.1.277 changelog entry. Facts used: shipped 2.1.277 (2026-09-18); setting
  `instructionFiles` in user or managed settings, default
  `claude-md-or-agents-md` (a project with any CLAUDE.md of its own ignores
  AGENTS.md entirely), alternative `claude-md-and-agents-md` loads both;
  AGENTS.md walks the same tree as CLAUDE.md including `~/AGENTS.md` and
  `.claude/AGENTS.md`; imports work; no official migration guidance. Codex reads
  `~/.codex/AGENTS.md` plus every AGENTS.md from git root down and has no
  CLAUDE.md fallback.

## State

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | this handoff + the two 2026-08 handoffs + `docs/linear-workspace-blueprint.md`, all untracked | `4a73321` planning: bootstrap gap audit |
| forge-skills | `operate-bmad-loop/pin-v0.12.0` (off main `d969789`) | `SKILL.md`, `references/pins.md` uncommitted | `d969789` merge of PR #12 |
| dotfiles | main, 1 commit ahead of origin | 7 files uncommitted (see below) | `d5963f7` Codex delegation rule |

Nothing from this session is committed or pushed anywhere.

**forge-skills pulled** 2026-09-20: main fast-forwarded to `d969789` (PR #12,
operate-bmad-loop defaults sessions to Opus 5 at xhigh effort). PR #13
(teammate, manage-planning-repos spoke-symlink verification) is open; not
touched.

**operate-bmad-loop pin bump, done, uncommitted.** bmad-loop v0.12.0 released
2026-09-20 and is the only release after the skill's v0.11.1 pin; BMAD-METHOD
is unchanged at 6.12.0. The bump touched only `pins.md` and one delegation
string in `SKILL.md`; no script depends on the changed behavior (nothing in the
skill parses `diagnose --json`, reads `verification_sequence`, or hooks
`post_dev_verify`; rich-commit registers `on_pre_commit`). All 12 suites pass
when run by their Makefile invocations, `markdownlint-cli2` 0 issues,
`check_pin.sh` reports `rev=v0.12.0` against the live install. Two deliberate
non-changes: the `test_ol_scripts.sh` fixture manifest stays at `v0.11.1`
because it records the BMAD-installed MODULE version, not the tool pin; and
the pins table no longer claims tool and module versions always agree.

**Bug found, not fixed:** `scripts/check_freshness.sh` reports
`latest_tag: codexr3g-s5, compare_status: diverged` on a current pin. The
bmad-loop repo has dozens of non-release tags (`codexr3g-s5`, `codexr3f-s4`,
…); the semver-max key reads the first digit run, so `3` outranks `0.12.0`.
Setup step 1 and Upgrade step 1 both run this check. Fix is its own branch:
restrict candidates to release-shaped tags and add fixtures to
`tests/test_ol_scripts.sh`.

**This hub is behind.** `_bmad/_config/manifest.yaml` records BMAD 6.10.0 with
the bundled bmad-loop module at v0.9.0, while the uv tool is v0.12.0. The
skill's own Setup would not pass here until `npx bmad-method install` is rerun
to 6.12.0. `tests/verify_setup.sh` against the hub: 20 passed, 1 failed (dirty
tree), 1 content gap (sprint plan), both pre-existing.

**dotfiles, uncommitted, two groups.** Pre-existing from earlier sessions:
`.claude/CLAUDE.md` (the model-selection rewrite with the Claude/OpenAI tier
table), `.claude/settings.json` (+64 lines), `config/qmd/index.yml` (orderly
hub collections). This session: `brew/brewfiles/Brewfile.cli` adds
`cask "slack-cli"` (with the brew-over-installer reasoning in a comment),
`brew "mlx"`, `brew "mlx-c"`, `brew "deno"`; `Brewfile.apps` renames the
retired `redis-stack-redisinsight` cask to `redis-insight` (404 on
formulae.brew.sh; `make bootstrap` would have failed on it);
`symlinked/default-uv-tools.sh` moves the bmad-loop pin v0.9.1 → v0.12.0;
`scripts/doctor.sh` gains a `slack` check. Both Brewfiles pass `ruby -c`.
`brew bundle check` could NOT be run: Homebrew is blocked on the Xcode license
on this machine.

**Install-source decisions made, recorded in Brewfile comments:**

- Slack CLI → Homebrew cask. Cask and curl installer ship the same 4.8.0,
  neither self-updates, so the cask wins on manifest simplicity. Update with
  brew, never `slack upgrade`. On THIS machine the curl install
  (`~/.slack/bin`, `~/.local/bin/slack`) still exists and will be shadowed by
  `/opt/homebrew/bin/slack` once the cask installs; trash the old one then.
- Claude Code → stays native installer. The `claude-code` cask tracked 2.1.267
  while native was 2.1.278; the cask disables auto-update; Anthropic names
  native as recommended. Codex CLI is already the `codex` cask (0.154.0).
- Claude desktop = `cask "claude"` (Homebrew). ChatGPT desktop is declared as
  `cask "chatgpt"` but this machine's copy was hand-installed 2026-09-17; the
  new machine gets the cask. Same shape for Granola, Linear, Roam, Spotify,
  Superwhisper, Office, Zoom, Readwise-iBooks: declared, present, not via
  brew. Fine for a clean install.
- Ignored by owner decision: Studio by Spotify Labs, the five Apple apps
  (Pages, Numbers, Keynote, iMovie, GarageBand). Microsoft Teams and Zotero are
  declared and not installed anywhere; left declared per the rebuild-manifest
  rule.

**AGENTS.md: researched, discussed, no decision.** Recommendation on the table:
keep the default `instructionFiles` mode; in repos where Codex is a real second
reader, rename `CLAUDE.md` → `AGENTS.md` and drop manage-planning-repos'
thin pointer file (Claude falls back to it, Codex reads it natively, no
symlink); global config stays split (`~/.claude/CLAUDE.md` vs
`~/.codex/AGENTS.md`, never a `~/AGENTS.md` that both would read); update
manage-planning-repos Step 3 to make canonical AGENTS.md the default for new
repos and treat CLAUDE.md-plus-pointer as legacy-valid. Before flipping any
repo, check what greps for `CLAUDE.md` by name (the `@RTK.md` import, qmd
collections). Only `corex-webapp` had an AGENTS.md as of 2026-09-20.

## Next work

1. **Commit and push dotfiles**, two commits: the pre-existing trio
   (CLAUDE.md, settings.json, qmd index), then this session's manifest edits.
   Then push `d5963f7` with them. This is the migration blocker: these are the
   live global config and do not reach the new machine until pushed.
2. **Owner runs `sudo xcodebuild -license accept`** in a real terminal, then
   `brew bundle check --file=brew/brewfiles/Brewfile.cli` (and `.apps`) to prove
   the manifests resolve, and `make doctor`.
3. **Commit the forge-skills branch and open a PR** (`operate-bmad-loop/pin-v0.12.0`,
   2 files). Every push is bot-reviewed; merge is the owner's.
4. **Fix `check_freshness.sh`** on its own branch: release-shaped tags only,
   fixtures in `test_ol_scripts.sh`, and correct the pins.md paragraph that
   still calls `latest_tag` a reliable semver max.
5. **Rerun the BMAD installer in this hub** to 6.12.0 so the hub matches the
   skill it authors (`npx bmad-method install`; the 2026-08-21 upgrade-plan
   handoff and `references/pins.md` cover the 6.12 shims and `--shims` flag).
6. **AGENTS.md decision**, then the manage-planning-repos Step 3 change.
7. Carry forward, unchanged, from the 2026-08-28 handoff: run the UAT, finish
   Alfred, decide VS Code, phased brew upgrade, `make macos`.
8. Carry forward from 2026-08-25: forge-skills worktree + remote-branch
   cleanup (9 worktrees now), the EOF-registration sweep, the ledger.

## Constraints to honor

- **Nothing committed this session; do not assume otherwise.** Both branches
  hold uncommitted work described above.
- **Propose removals; the owner confirms.** Binds every dotfiles pass.
- **Do not bundle a cleanup with a behaviour change** (2026-08-28 lesson).
- **Declared-but-not-installed casks are rebuild manifests**, and
  installed-not-via-Homebrew is not drift. Compare against `/Applications`,
  not only the Caskroom — this session got that wrong once.
- **Homebrew vs vendor installer rule** (this session): Homebrew when the
  cask tracks the vendor's current release and the tool does not self-update;
  vendor installer when the tool self-updates and the cask lags a channel.
- forge-skills: merges belong to the owner; agents never merge, rebase,
  squash or force-push. Merge commits are the repo style. Script constraints:
  macOS bash 3.2 + BSD userland, Python stdlib only, hermetic tests,
  markdownlint clean. Do not touch PR #13.
- `.claude/settings.json` and `.claude/CLAUDE.md` in dotfiles ARE the live
  `~/.claude/` files (dotbot symlinks). `git config --global` writes into the
  repo.
- `rm` is disabled: `trash`, `git rm`, `git worktree remove`.
- `sudo` cannot prompt from a Claude Code shell, including via `!`.
- Searches into spoke code use the real path, never the hub symlink.
- Hub: never squash or rebase hub PRs (memory cites SHAs).

## Open user inputs

- AGENTS.md: which repos flip to canonical AGENTS.md, if any, and whether
  manage-planning-repos should default new repos to it.
- Gap 4, VS Code: track settings + 47 extensions in the repo, or Settings Sync.
- Whether `deno` is still wanted (added because installed 2026-06-28; nothing
  in the repo references it).
- Whether to clean the curl-installed Slack CLI on this machine now or leave
  it until the migration.
- Carried from 2026-08-28: `git_status` trailing space; 1Password SSH agent
  migration blocker; whether saved-reading, recipe corpus and PKM are one
  project or three.

## Suggested skills

- `operate-bmad-loop` (Upgrade action) — after step 5, to bring this hub onto
  the v0.12.0 pin the skill now documents.
- `manage-planning-repos` — for the AGENTS.md Step 3 change and a drift report
  after the BMAD installer rerun.
- `bmad-code-review` — before opening the forge-skills PR; the bots re-review
  regardless.
- `superpowers:using-git-worktrees` — for the `check_freshness.sh` fix branch.
- `consolidate-memory` — three handoffs (2026-08-25, 2026-08-26, 2026-08-28)
  are ready to fold once steps 1-3 land.
- `write-handoff` — at the next boundary.
- Not `implement-story`: dotfiles is direct commits to `main`, not story-driven.

## Update, 2026-09-25 evening

- dotfiles next-work step 1 DONE and pushed: `e5755cd` (live config trio),
  `f8a9126` (manifests), `80f8b03` (starship git_status brackets dropped, which
  removes the trailing space). Step 2 done by owner (Xcode license).
- Decisions: deno stays (Supabase edge functions; Brewfile comment updated).
  Slack CLI cask installed (4.8.0); curl binaries `~/.local/bin/slack` and
  `~/.slack/bin` trashed; `~/.slack/credentials.json` kept.
- VS Code gap 4: Settings Sync is ON here (GitHub account, last settings sync
  2026-09-15). Decision: rely on Sync, do not track in repo.
- `make alfred` "No rule" error: the target exists in the Makefile; the owner
  ran make outside `~/.dotfiles`. Alfred still not live from the repo.
- Owner runs the UAT next, then the phased brew upgrade.
- 1Password SSH agent: owner wants to test it against bmad-loop. Commit signing
  is global (`commit.gpgsign true`, ssh format), so every loop commit signs.
  The 1Password agent socket does not exist yet (agent not enabled).
- Alfred now LIVE from the repo (`5e6f4a4`). Root cause of every revert:
  Alfred 5 reads `~/Library/Application Support/Alfred/prefs.json`, and the
  `syncfolder` defaults key is only a mirror. The script now edits prefs.json.
  Fresh-machine path (no prefs.json yet) is untested; the UAT covers it.
  `~/Documents/App Settings/Alfred` is still on disk pending owner OK to trash.
- `~/Documents/App Settings/Alfred` trashed (owner OK).
- 1Password SSH agent tested against bmad-loop's launch shape; result table and
  recommendation appended to the 2026-08-22 1Password plan. Short version:
  approval does not survive a lock, so unattended signing fails. Recommended
  split: 1Password for auth, keychain-passphrased on-disk key for signing.
  Awaiting owner decision.
- SSH split DONE and pushed (dotfiles, commit after `5e6f4a4`): 1Password
  "Github" item = GitHub auth; `~/.ssh/id_ed25519` passphrased, keychain,
  signing only. GitHub "Personal MBP" auth key deleted. Okta MBP keys untouched
  (other machines). Fresh-machine path of the new setup-ssh-keys.sh is untested;
  the UAT covers it (step 5 now prompts for a passphrase and pauses for
  1Password; `s` skips).

## Update, 2026-09-27

- SSH split REVERTED (dotfiles commit after `0026663`). Phone-driven remote
  sessions could not push with 1Password locked. Final state: one on-disk key,
  keychain passphrase, agent-loaded by zshrc, both GitHub registrations;
  github.com block pins `IdentityAgent SSH_AUTH_SOCK`. "1Password GitHub"
  deleted from GitHub; owner deletes the 1Password item. Details in the
  1Password plan doc. Fresh-machine path still untested; UAT step 5 now has
  no 1Password pause.
- `docs/linear-workspace-blueprint.md` trashed: superseded by rev 3.2 in the
  Orderly planning repo (`docs/linear-setup/`).
- Story written: `_bmad-output/implementation-artifacts/spec-wp9-hub-registry.md`
  (manage-planning-repos hub registry + `hubs.sh` fan-out; registry built by
  the skill from repo markers, never from dotfiles; JSON at
  `~/.config/planning-repos/registry.json`). Baseline forge-skills `c46e2d6`.
  Dotfiles follow-up once it lands: dotbot-link the registry into the repo.
- dotfiles tonight: `make skills` (update-skills.sh; Claude/Codex now see all
  skills; 17 third-party upgraded; 8 upstream-deleted mattpocock skills
  removed), `make node VERSION=x` (upgrade-node.sh + stable Alfred workflow
  links), README fresh-machine path without gh, setup-skills clone slug fix.
- forge-skills is on branch `operate-bmad-loop/base-branch` (off the
  unmerged pin-v0.12.0 commit 5b81803) with uncommitted implement-story and
  operate-bmad-loop edits from a parallel session; `make skills` will not
  pull until that lands.

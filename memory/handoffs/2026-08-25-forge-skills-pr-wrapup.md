---
date: 2026-08-25
topic: "forge-skills script-conversion PRs — wrap-up: merge #4, post-merge sweep, worktree cleanup, follow-up backlog"
repos:
  - "ai-scratch"
  - "forge-skills"
status: open
---

## Authoritative context

Read these first; do not re-derive what they settle.

- `_bmad-output/implementation-artifacts/deferred-work.md` (hub, commit `dfff397`, 82 entries): the single tracker for every post-merge follow-up from PRs #1–#8, grouped by PR, plus an "Owner-requested follow-ups" section (redline-file reply bug + wider container, 2026-08-24) and a "GNU/Linux portability cluster" decision section. Add follow-ups here, never in a new doc.
- `memory/handoffs/2026-08-21-forge-skills-pr-closeout.md` (now `status: resolved`): the history of the five review rounds, the merge-time bar, and the agent-orchestration lessons (75s mutation spacing, per-PR scratch namespacing). Superseded by this file for next work.
- `_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md` and `_bmad-output/implementation-artifacts/spec-wp1…wp8-*.md` (all `status: done`): what was built and why.
- GitHub `forge512/agent-skills` PRs #2–#8, each carrying a "Merge-time closeout" comment: the per-PR fixed/deferred record. #1 and #3 have "Final round" comments instead.
- `memory/handoffs/2026-08-21-bmad-6-11-upgrade-plan.md` (another session's, untracked in the hub at handoff time): its skill work is explicitly queued behind these merges and unblocks once #4 lands.

## State

**forge-skills** (github `forge512/agent-skills`, real path `/Users/michaelswanson/Code/forge-skills`)

- Merged with merge commits, all on 2026-08-22: #1 write-handoff, #2 redline-file, #3 implement-story, #5 manage-todoist, #6 consolidate-memory, #7 operate-bmad-loop, #8 manage-planning-repos. `origin/main` = `5b4ffd8` (merge of #6).
- **#4 write-like-me: OPEN, MERGEABLE, 0 unresolved threads** at `a035a56`. Final commits: `82edeba` main merge (keep-both EOF registrations), `413f70b` style-profile.json scrub (owner-directed: employer, customer tenant, team handle, feature-flag and feature names replaced with synthetic equivalents; sign-off recorded on the resolved escalation thread), `a035a56` `--plain` documented-command fix. Pre-scrub content still exists in the branch's earlier commits; squash-merge + branch delete is the owner's option to keep it out of main history.
- #9 `operate-bmad-loop/rich-commit-content-select` is a peer session's open PR; the main checkout `/Users/michaelswanson/Code/forge-skills` is on that branch. Leave both alone.
- Worktrees still present (8): `/Users/michaelswanson/Code/forge-skills-worktrees/{consolidate-memory,implement-story,manage-planning-repos,manage-todoist,operate-bmad-loop,redline-file,write-handoff,write-like-me}` on branches `scripts/<skill>`, all clean and pushed.
- Remote branches still present: `scripts/write-like-me` (open PR), `scripts/consolidate-memory` and `scripts/manage-todoist` (merged, not yet deleted). The other five were deleted at merge.
- Suite state at last run (write-like-me worktree, post-main-merge): `make test` exit 0 across all registered suites, `make lint-docs` 0 issues.
- Root README Tests list and Layout bullet do not yet mention the new `scripts/` dirs or suites; Makefile and `.github/workflows/tests.yml` carry three EOF tails (`test-is-scripts`, `test-mt-scripts`, `test-wlm-scripts`) behind "EOF registration" comments instead of the canonical `test:` list.

**ai-scratch** (hub, github `mswanson/ai-scratch`, main at `0d2c432`)

- Ledger commits this session: `48bac84` (79 entries), `cbbc80a` (+1), `dfff397` (+2 owner-requested). All pushed.
- Uncommitted at handoff time, NOT this session's: `memory/MEMORY.md` gains one line (BMAD 6.11 handoff link) and `memory/handoffs/2026-08-21-bmad-6-11-upgrade-plan.md` is untracked. Belongs to a peer session; commit separately or leave for it.
- `qmd update` is broken on this machine: better-sqlite3 native binding fails under Node v24.19.0 (`ERR_DLOPEN_FAILED`). Ledger and handoffs are not qmd-searchable until fixed.

## Next work

1. **Merge #4** (owner action, or on owner instruction): `gh pr merge 4 --merge` to match the others, or `--squash --delete-branch` if the pre-scrub profile should leave main's history. Any codex wave after `a035a56` is post-merge backlog per the PR's closeout comment; triage only if the owner asks.
2. **Post-merge sweep** on forge-skills, one commit (branch + small PR is the safe default since every push gets bot-reviewed; direct-to-main only if the owner says so): fold the three EOF registrations into the canonical `test:` prerequisite list in `Makefile` and the step list in `.github/workflows/tests.yml`, dropping the "EOF registration" comments; add the new suites to the root `README.md` Tests list and a `scripts/` line to its Layout bullet. Verify with `make test` and `make lint-docs`.
3. **Cleanup**: from `/Users/michaelswanson/Code/forge-skills`, `git worktree remove` each of the 8 worktrees (they are clean; `--force` should not be needed), then `git worktree prune`; delete remote branches `scripts/consolidate-memory`, `scripts/manage-todoist`, and `scripts/write-like-me` once #4 is merged (`git push origin --delete <branch>`); `git branch -d` the local ones. Never `rm -rf` the worktree dirs.
4. **Fix qmd**: `npm rebuild better-sqlite3` inside the global install (`~/.bun/install/global/node_modules/`), or reinstall `@tobilu/qmd`; then `qmd update` from the hub.
5. **Owner-requested redline-file tweaks** (ledger, top section): reproduce the reply-to-comment bug in `skills/redline-file/scripts/review.py reply` / the review page, then widen the page container. Small PR each or together.
6. **Ledger P1s**: `archive-handoffs.sh` in-repo symlinked source parent (top of PR #6 section; git records a deletion instead of a rename) and `install_assets.sh` predictable temp path (PR #7). Then work the rest of the ledger by section as capacity allows.
7. Unblocked after step 1: the BMAD 6.11 upgrade skill work (its own handoff).

## Constraints to honor

- Merges belong to the owner unless explicitly delegated; agents never merge, rebase, squash, or force-push PR branches. Merge commits are the repo's established style.
- GitHub write mutations (replies, resolves, comments) at 75s spacing, one clock across all agents; check every GraphQL response is non-null (rate-limit blocks return null silently). codex re-reviews every push; a post-closeout wave is post-merge backlog, not a reason to loop.
- Parallel agents get namespaced scratch dirs; shared filenames collided in an earlier round.
- `rm` is disabled: `trash`, `git rm`, `git worktree remove`. `nuke` only on explicit instruction.
- The style-profile.json values introduced in `413f70b` are deliberately synthetic (fabricated Slack ID and handle, `acme-*` placeholders); do not "correct" them, and never reintroduce employer, customer, tenant, team, or feature identifiers into any repo. The same rule was applied only to #4; main still carries Auth0/ACUL references in manage-todoist (owner decision pending, below).
- Script constraints for any fix: macOS bash 3.2 + BSD userland, Python stdlib only with `allow_abbrev=False`, hermetic tests (shims, never real qmd/gh/tailscale), markdownlint-cli2 clean, Makefile/CI registration via the canonical list once the sweep lands.
- Follow-ups go into the ledger; do not create parallel trackers.
- Hub: never squash or rebase hub PRs (memory cites SHAs). Do not commit the peer session's uncommitted hub files as part of unrelated work.
- Do not touch PR #9 or the `operate-bmad-loop/rich-commit-content-select` branch.

## Open user inputs

- Merge #4 as a merge commit (consistent) or squash + delete branch (keeps pre-scrub profile out of main history)?
- manage-todoist on main references `PROJECTS: Auth0`, `area: auth0`, `feature: acul` and internal workstream names; they mirror real Todoist labels the skill routes by. Leave as-is (private repo, no customer data), or rename in Todoist first and scrub the skill to match?
- GNU/Linux portability cluster (ledger section): adopt Linux support as a work item, or accept that codex re-reports these on every wave?
- Post-merge sweep: direct commit to main, or branch + PR?
- Redline reply bug: what did it do, and on which comment or file? Needed to reproduce.

## Suggested skills

- `bmad-quick-dev` for the sweep, the redline tweaks, and ledger P1 fixes in the forge-skills spoke (the WP1–WP8 pattern; hub-driven, worktree per change).
- `redline-file` to reproduce the reply bug against a real file before touching code.
- `bmad-code-review` (Blind Hunter + Edge Case Hunter) before opening any new forge-skills PR; the GitHub bots re-review on every push regardless.
- `superpowers:using-git-worktrees` if a new worktree is needed for the sweep; cleanup itself is plain `git worktree remove`.
- `consolidate-memory` once #4 is merged and the sweep lands: three forge-skills handoffs are then resolved and ready to fold into durable memory.
- `write-handoff` at the next boundary.

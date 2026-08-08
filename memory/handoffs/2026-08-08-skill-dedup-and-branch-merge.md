---
date: 2026-08-08
topic: handoff skill deduplicated in favor of write-handoff; ai-scratch and dotfiles branches merged and cleaned
repos: [ai-scratch, dotfiles]
status: open
---

# Skill dedup and branch merge

Short maintenance session, closed cleanly. Nothing is mid-flight. The value
here is the two rules it established: how skills get removed on this machine,
and why hub PRs must never be squashed.

## Authoritative context

- `dotfiles/.claude/CLAUDE.md` §Session Handoffs and §Suggest These Skills —
  amended this session; the handoff policy it states is now the one
  `write-handoff` actually implements. Do not reopen the naming.
- `dotfiles/.agents/skill-lock.json` (dotbot-symlinked to
  `~/.agents/.skill-lock.json`) — the authoritative inventory of which agent
  skills are installed globally and where each came from. 31 skills, 25 from
  `mattpocock/skills`.
- `memory/claude-settings-scopes.md` — settles that `settings.json`
  model/effortLevel churn is expected and uncommitted by design.
- ai-scratch `0341473` — the PR #1 merge commit; `main` now carries all
  three weeks of hub work.

## State

Done:

- Established that `write-handoff` and `handoff` were independent skills with
  no shared code, and that `write-handoff` is a strict superset. `handoff`
  wrote to the OS temp dir; `write-handoff` implements the `memory/handoffs/`
  hub-and-spoke policy, frontmatter, per-repo state block, delta-scoping, and
  a self-check.
- Removed the `handoff` skill:
  `npx skills@latest remove --global --skill handoff -y`. Clean — skill dir,
  `~/.claude/skills` symlink, and lock entry all gone (32 → 31 skills), no
  dangling links. `/handoff` no longer resolves.
- Amended `dotfiles/.claude/CLAUDE.md`: §Session Handoffs names
  `write-handoff` and notes it is model-invocable; dropped the `/handoff` row
  from the Suggest These Skills table (that table is user-typed-only skills).
- Merged ai-scratch PR #1 (`bmad-loop-dev` → `main`, 59 commits) as merge
  commit `0341473`. Deleted the branch local and remote, pruned the stale ref,
  and deleted the fully-merged `memory-consolidation-2026-08-04`.

Pending: nothing from this session.

Per-repo:

| Repo | Branch | Tip | Sync | Uncommitted |
|---|---|---|---|---|
| ai-scratch | `main` | `0341473` | in sync with `origin/main` | none |
| dotfiles | `main` | `088fb0d` | in sync with `origin/main` | `.claude/settings.json` (model + effortLevel toggle, intentional) |
| forge-skills | untouched | — | — | — |

`main` is the only branch in ai-scratch, local and remote. Hub work now
starts from `main` rather than a long-lived `bmad-loop-dev`.

## Next work

No focus was named for the next session. The threads that remain open are
older than this session:

1. **LiteLLM adapter usability trial** — built and protocol-verified, never
   used for real work. That trial is the only thing that decides whether it
   stays. See `memory/handoffs/2026-08-08-litellm-local-adapter.md`.
2. **Dotfiles punch-list** — `_bmad-output/planning-artifacts/2026-08-02-dotfiles-update-plan.md`,
   post-cleanup phase, including the deferred Go decision and the LiteLLM
   install script in §4.
3. **Prune the remaining mattpocock skills.** 25 are still installed; several
   overlap the forge-skills family the same way `handoff` did (`grill-me` vs
   `grilling`, `review`, `qa`, `request-refactor-plan`, `teach`,
   `scaffold-exercises`, `design-an-interface`). Nobody has audited which are
   actually used. Same removal command, one `--skill` at a time.
4. **Extract the skill-removal mechanics into `memory/`.** Where the lockfile
   lives and the `npx skills remove` invocation are durable facts that this
   handoff should not be the only record of.

Four other handoffs are still `status: open` and predate this session:
skill-review-and-rename (2026-08-01), cloudflare-migration (2026-08-02),
dotfiles-update-walkthrough (2026-08-03), skill-redline-review (2026-08-03).
Worth a lifecycle pass to flip the finished ones to `resolved`.

## Constraints to honor

- **Never squash or rebase-merge an ai-scratch PR.** Files under `memory/`
  and `memory/handoffs/` cite commit SHAs; squash collapses them and rebase
  rewrites them, orphaning every reference. Merge commits only. This is why
  PR #1 was merged rather than fast-forwarded.
- **Global agent skills are managed by the `npx skills` CLI**, not by hand and
  not by the Claude Code plugin system. Removing one means
  `npx skills@latest remove --global --skill <name>`, then committing the
  lockfile change in dotfiles. Deleting a skill directory directly leaves the
  lockfile lying.
- **Do not reinstall `handoff`.** It was removed deliberately, not by
  accident. `write-handoff` supersedes it.
- `.claude/settings.json` model/effortLevel drift stays uncommitted. Already
  settled in `memory/claude-settings-scopes.md`; do not re-raise.
- Commit and push only on request. Both repos were pushed this session only
  because the user asked each time.

## Open user inputs

- Which of the 25 remaining `mattpocock/skills` are worth keeping? Needs the
  user's judgment about what they actually reach for, not an inventory.
- Should hub work continue directly on `main`, or does the next multi-commit
  effort get its own branch and PR? `bmad-loop-dev` ran three weeks before
  merging; unclear whether that cadence was intended.

## Suggested skills

- `write-handoff` — at the next natural boundary. Now the only handoff skill.
- `consolidate-memory` — for the lifecycle pass over the five open handoffs,
  and to extract item 4 above into a `memory/` file.
- `manage-planning-repos` — if the skill pruning turns into a broader drift
  check across hub and spokes.

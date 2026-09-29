---
date: 2026-09-28
topic: "base-branch-wp9-registry-retirement"
repos:
  - "ai-scratch"
  - "forge-skills"
  - "dotfiles"
  - "lyceum-planning"
  - "marshal-planning"
  - "product_planning"
status: open
story: "wp9-hub-registry"
---

## Authoritative context

Read these first; they settle things this handoff does not repeat.

- `_bmad-output/implementation-artifacts/spec-wp9-hub-registry.md` — the WP9
  story, status `done`, merged as forge-skills PR #18 (`1de7beb`,
  2026-09-28). Frozen intent with the two owner amendments of 2026-09-28
  (third marker kind `standalone`; a `.git` file alone is not a worktree),
  Dev Agent Record, `### Review Findings`, metrics, merge line.
- `_bmad-output/implementation-artifacts/wp9-hub-registry-code-review-report.md`
  — every finding from six Codex rounds, the three bmad-code-review layers
  and the two PR bots, with bucket and outcome. Do not re-litigate.
- `_bmad-output/implementation-artifacts/wp9-hub-registry-session-state.yaml`
  — the implement-story metrics record for WP9 (`hil_review: merged`). The
  skill that wrote it is retired; the file stays as the story's record.
- `_bmad-output/implementation-artifacts/deferred-work.md`, section
  "Deferred from: code review of spec-wp9-hub-registry (2026-09-28)" — the
  four WP9 deferrals.
- `memory/forge-skills-spoke.md` — the spoke's AI review infrastructure
  (`claude[bot]` via `claude-review.yml`; the Codex GitHub app as
  `chatgpt-codex-connector[bot]`) and three owner-approved learnings
  (isolated read-only `claude -p`; reject relative config paths; one live
  smoke per story).
- `memory/bmad-loop-pins.md` — tool at v0.12.0; phase branch
  `bmad-loop-dev` exists in this hub with base `main` recorded as git
  config `branch.bmad-loop-dev.bmad-loop-base`; implement-story retired.
- forge-skills `skills/operate-bmad-loop/SKILL.md` (Setup step 5/9, Action
  3) and `references/phase-branch-workflow.md` — the base-branch feature
  (PR #16) and, since PR #17, the Codex review step that used to be
  implement-story phase 2.3.
- forge-skills `skills/manage-planning-repos/SKILL.md` §4 "Registry and
  fan-out" and `references/board-sync.md` — the registry/fan-out contract
  (PR #18) and the status board's new home (PR #20).
- `memory/handoffs/2026-09-28-dotfiles-wrapup-ssh-skills-node-wp9.md` —
  the previous handoff; its Next work items 1 and 2 are done here, 3–6
  carry forward unchanged.

## State

Per-repo (2026-09-28, end of session):

| Repo | Branch | Last commit | Dirty | Note |
|---|---|---|---|---|
| ai-scratch | main = origin | `279462b` memory: implement-story retired | this handoff only | hub marker stamped (`6cefccc`); phase branch `bmad-loop-dev` at main with base recorded |
| forge-skills | main = origin `61bee4f` (merge of PR #20) | — | clean | no worktrees, no local or remote branches besides main |
| dotfiles | main = origin `2220154` | — | clean | `config/planning-repos/registry.json` tracked and dotbot-linked from `~/.config/planning-repos/registry.json` |
| lyceum-planning | main = origin `2c685cd` (#79) | — | 2 handoff files, another session's | marker (#78) and `board-config.yaml` (#79) merged by the owner; direct pushes to main are hook-blocked |
| marshal-planning | main = origin `51c06c9` | — | 3 files, another session's | marker stamped `hub` (no spoke table; registry lists it with 0 spokes) |
| product_planning | `michael/stability-stories` = origin `b75d78d` | — | clean | marker (`b2056b1`) and `board-config.yaml` ride on that feature branch |

Done this session (2026-09-27 → 2026-09-28), all merged:

- forge-skills PR #15 (bmad-loop tool pin v0.12.0), PR #16 (operate-bmad-loop
  base branch: `install_assets.sh --branch-only --base-branch`, git config
  `branch.<phase>.bmad-loop-base`, Verify checks; implement-story `pr_base`),
  PR #18 (WP9: `stamp_marker.sh`, `registry.py`, `hubs.sh`, marker GAP/drift in
  `verify_hub.sh`; test chain 404 at merge), PR #19 (Opus 5.5 pin for loop
  stages), PR #17 (retire implement-story; authored by a concurrent session,
  owner-directed merge), PR #20 (manage-planning-repos owns the status board:
  `compute-board-state.py`, `board-config.yaml`, `board-sync.md`; chain 443).
- Hub setup: `bmad-loop-dev` created at main with base `main`;
  operate-bmad-loop Verify 23/23 (content gap: no sprint plan).
- Registry on this machine: 4 hubs (ai-scratch, lyceum-planning,
  marshal-planning, product_planning, all `marker:yes`), 1 standalone
  (auth0-bmad-poc), 11 excluded; roots `~/Code`, depth 4. Live
  `hubs.sh verify --jobs 2` on two hubs returned real reports.
- forge-skills cleanup: nine merged `scripts/*` worktrees, `forge-skills-opus`,
  both `forge-skills-wt/*` worktrees, and the superseded branches
  `rich-commit-content-select` and `autonomous-provisioning` removed; three
  merged remote branches deleted.
- Skill links: `make skills` pruned the dead implement-story links (Claude,
  Codex, agents); 38 skills in the store.
- Process note, recorded honestly: PRs #19 and #17 were merged before their
  CI finished (my wait loop read an empty check list as done). Verification
  came after: PR checks, main CI on both merge commits, and the local full
  suite all passed. PR #20 used the corrected wait.

Pending: nothing in flight. See Next work.

## Next work

1. **BMAD installer rerun in this hub to 6.12.0** (carried since 2026-09-25).
   The hub manifest says 6.10.0; product_planning is on 6.12.0. Then
   operate-bmad-loop Upgrade. On BMAD ≥ 6.12 Setup step 3 (bmm skills sync)
   is a SKIP.
2. **Next hub stories.** No sprint plan and no `ready-for-dev` story remain.
   Sources: the deferred-work ledger (37 KB, including WP9's four
   deferrals), and the retirement's own follow-up already done in PR #20.
   Without implement-story, manual stories go through `bmad-dev-story`
   with the phase-branch workflow's Codex step; loop stories through
   operate-bmad-loop.
3. **Registry follow-ups (small):** `lyceum/lyceum` is excluded as `no hub
   evidence` rather than `spoke of lyceum-planning` because the spoke pass
   relabels only standalone and legacy-hub candidates; consider extending
   it. `make sync` in dotfiles exits 1 because `~/.claude/settings.json` is
   a regular file, not the dotbot link — pre-existing and accepted, but it
   masks other dotbot failures.
4. **Fresh-machine UAT** (`docs/uat.md`) when the owner says go; the
   registry link and `make skills` pruning are now part of what it covers.
5. **Phased Homebrew upgrade** after the UAT.
6. Carried: forge-skills `check_freshness.sh` fix; AGENTS.md decision +
   manage-planning-repos Step 3 change; `.claude/settings.json` link drift.

## Constraints to honor

- **Spec amendments are owner rulings, not drift:** `standalone` is a valid
  marker kind; templates unchanged; Step 3 re-stamps a hub-template
  instantiation with `stamp_marker.sh <CLAUDE.md> standalone --replace`.
  A checkout is a worktree only when `git rev-parse --git-dir` differs from
  `--git-common-dir`.
- **Registry roots are always asked, never assumed.** `registry.py` has no
  default root; a rebuild reuses recorded roots and depth only after the
  user says keep.
- **Read-only fan-out is isolated:** `--restricted --setting-sources ""
  --strict-mcp-config --tools Bash,Read,Glob,Grep`, deny list, one exact
  path-anchored grant, no `*`. Do not loosen it to make a prompt work; use
  `--apply`.
- **Hand-edited registry paths must be absolute or `~/`;** relative is
  refused, never resolved.
- **Merge policy:** forge-skills PRs merge with merge commits, never squash
  or rebase; wait for checks to exist and pass before merging (see State).
  lyceum-planning blocks direct pushes to main; use a branch + PR there.
- **Other sessions' checkouts:** lyceum-planning and marshal-planning carry
  another session's dirty files; commit only the file you changed
  (`git commit -o <file>`), never stash or reset there.
- **rm is disabled; `trash` only.** `make skills` will not pull forge-skills
  while it is off main or dirty; that is by design.
- Board config: readers check `board-config.yaml` first, then the legacy
  `implement-story.config.yaml`; both live hubs are migrated, legacy files
  untouched.
- Never squash or rebase hub PRs; memory cites SHAs.

## Open user inputs

- When to run the fresh-machine UAT (owner said hold).
- Whether `~/.claude/settings.json` should become the dotbot link again
  (currently a regular file; `make sync` reports it every run).
- Carried: AGENTS.md flip per repo; whether saved-reading, recipe corpus
  and PKM are one project or three.

## Suggested skills

- `operate-bmad-loop` (Verify first, then Upgrade) — after the BMAD 6.12.0
  installer rerun in this hub.
- `manage-planning-repos` (Verify) — on any hub after skill changes; §4
  `hubs.sh verify` runs it across all four hubs at once.
- `bmad-dev-story` — manual stories in this hub now that implement-story
  is retired; `bmad-code-review` after.
- `consolidate-memory` — the 2026-08-25, 08-26, 08-28, 09-25 and 09-28
  handoffs are ready to fold; this one joins them once items 1–2 land.

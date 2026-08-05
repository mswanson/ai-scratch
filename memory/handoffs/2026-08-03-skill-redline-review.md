---
date: 2026-08-03
topic: skill redline review — phase references pending; redline-file tool matured
repos: [ai-scratch, forge-skills]
status: open
---

# Handoff: skill redline review continuation

## Authoritative context

- `memory/handoffs/2026-08-01-skill-review-and-rename.md` (still open) —
  batch-4 punch list, capstone ordering, older constraints. This handoff
  layers the redline-review pass on top; that one stays authoritative for
  batch 4 / capstones / dry-run sequencing.
- `_bmad-output/planning-artifacts/2026-07-31-token-optimization-framework-design.md`
  (moved from `docs/` 2026-08-04) — framework design; §6 naming (settled, do not reopen), §8.5 implement-story design.
  New "Later" item 2026-08-03: extend loop init beyond `--cli claude` to
  codex.
- `~/Code/forge-skills` main @ `4cdd9b8`, clean, pushed — every change of
  this session is committed there; `git log --oneline fd0f584..4cdd9b8`
  is the session's change record with rationale per commit.
- Task #12 (harness task list) — dry-run watch list; UPDATED 2026-08-03:
  Linear must be wired into implement-story phase 0.1/3.4 before/with
  the dry runs so they exercise the full flow (user requirement from
  redline c4).

## State

- forge-skills: main @ `4cdd9b8`, clean, pushed. `make test` = 8 suites
  green (redline server suite now 52 scenarios); CI additionally gates
  `make lint-docs` (markdownlint, 0 issues across 38 files).
- Redline reviews COMPLETED and resolved (comments processed, markup
  stripped, committed): manage-planning-repos SKILL.md (12 comments →
  hub/spoke redesign, BMAD optional, unified bmad-* layout rule,
  Setup/Repair rename), hub-CLAUDE.md + spoke-CLAUDE.md templates
  (spoke template NEW; multi-hub spokes table; Modules Installed section
  dropped), operate-bmad-loop SKILL.md (1 comment → codex noted),
  implement-story SKILL.md (5 comments → security rule promoted to top
  with workflow-stopping weight, user-directed merge exception in
  SKILL.md + phase-5-close.md, resume protocol inlined).
- **phase-0-pregate.md: NOT REVIEWED** — a session was launched twice but
  the user closed it without commenting. It lints clean; content
  unchanged this session.
- redline-file tool grew substantially (all committed with tests):
  margin comment cards with edit/delete/REPLY threads, comment metadata
  (`{#cN by= at=}`, `--author` flag), selection anchoring by occurrence
  index, list-aware + fence-aware block splitting, block comments append
  at block END (placement fix), frontmatter document-record card, drafts
  survive click-away, dark mode + blue accent, mobile layout + marker
  bottom-sheet, remote review via `--allow-host` + tailscale serve,
  SIGTERM exits 0, 30s auto-close after Done.
- Tool-replacement research done: Roughdraft (Lex-Inc) is the nearest
  substitute and the tool ours consciously replaced; decision = keep
  ours, revisit only if requirements change shape (multi-reviewer,
  non-markdown).
- ai-scratch: bmad-loop-dev, design-doc commit pushed. Untracked strays
  (`.claude/settings.local.json`, `docs/2026-08-02-dotfiles-update-plan.md`,
  `dotfiles` symlink) predate/parallel this session — left alone.
- Memory: `dotfiles-spoke.md` gained the qmd-in-dotfiles-setup follow-up
  (redline c12, 2026-08-02).

## Next work

1. Resume the agreed review queue, each via redline-file (launch recipe
   in Constraints): **phase-0-pregate.md first (unreviewed)**, then
   `phase-2-validate.md`, `phase-4-review.md`, `phase-5-close.md`,
   `references/session-state.md`, `assets/implementation-principles.md`
   (all under `skills/implement-story/`). Process each: resolve
   comments, strip markup, test delta if behavior changed, commit.
2. Then SKILL.md-only redlines: write-handoff, consolidate-memory,
   redline-file, manage-todoist, write-like-me (agreed scope: skip
   their tests/scripts/references).
3. Then the 2026-08-01 handoff's remaining work in its order: batch-4
   leftovers (description voice/length, single-sourcing implement-story
   duplicated rules, story-key examples, engineer_reported →
   user_reported, operate-bmad-loop step-3 dedup), manage-planning-repos
   Setup capstone (ai-scratch → lyceum-planning + marshal-planning),
   task #12 dry runs — now including Linear wiring first (phase
   0.1/3.4 + per-hub config).

## Constraints to honor

- Redline launch recipe: run `scripts/review.py` via run_in_background
  with `--allow-host mbp.tailad3283.ts.net --author michael`, then
  `tailscale serve --bg <port>` and verify the tailnet URL returns 200;
  give the user both URLs. Stop serve when winding down
  (`tailscale serve --https=443 off`). Sessions are token-gated; killed
  sessions exit 0 (not failures). Comments live in the file — restarts
  lose nothing.
- Review-processing protocol (redline-file SKILL.md "After it returns"):
  act only on `{#cN}`-tagged + self-seeded markup; whole threads strip
  together; agent may answer in-thread (`{#cN.M by=agent}`) instead of
  resolving.
- Lint the target file (`make lint-docs-fix` scope-limited) BEFORE
  launching a session, never mid-session.
- `make test` green + `make lint-docs` clean = merge gate; every
  behavior change carries its test delta.
- Batch 1-3 fixes, naming (§6 second revision), sprint-status semantics
  (2026-08-01), HIL gate model: settled, do not reopen. New settled
  items this session: security rule sits at top of implement-story hard
  rules; user-directed merge is the ONE merge exception; spokes may
  serve multiple hubs (repo assets stay hub-neutral); codegraph/qmd
  wiring is setup-owned in manage-planning-repos (no extra ask);
  project-context lives in the SPOKE at docs/project-context.md.
- rm disabled (trash/nuke/git rm); BSD/bash 3.2; macOS CI; ai-scratch
  pushes may hit the classifier (hand to user via `!` if blocked).
- Commit memory/ only with user confirmation.

## Open user inputs

- write-like-me provenance (license: Proprietary, author Christian
  Tamnou) — unresolved from 2026-08-01; surfaces again at its SKILL.md
  redline (Next work 2).
- Which hub first for the Setup capstone, and which stories for the
  task #12 dry runs.
- Older threads unchanged (2026-08-01 handoff): generic Pocock handoff
  skill deactivation, qmd collections for lyceum/marshal-planning,
  github plugin MCP auth, /fewer-permission-prompts (Todoist reminder
  was due 2026-08-02).

## Suggested skills

- redline-file for every doc in Next work 1-2 (it self-documents the
  launch recipe; honor the run_in_background rule).
- superpowers:verification-before-completion at each review's
  resolution claim.
- manage-planning-repos (Setup) and implement-story for Next work 3,
  per the 2026-08-01 handoff.
- write-handoff at the next boundary; flip THIS handoff to resolved
  when the review queue (Next work 1-2) completes; the 2026-08-01
  handoff resolves only when batch 4 + capstones land.

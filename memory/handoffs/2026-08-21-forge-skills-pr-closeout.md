---
date: 2026-08-21
topic: forge-skills script-conversion PRs — finish closeout and merge
repos: [ai-scratch, forge-skills]
status: open
---

## Authoritative context

- `_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md` — the eight-work-package plan (one PR per skill); execution contract and open-decision log. Settled; do not re-derive.
- `_bmad-output/implementation-artifacts/spec-wp1-*.md` … `spec-wp8-*.md` — per-package specs with review change logs. All `status: done`.
- `_bmad-output/implementation-artifacts/deferred-work.md` — DW ledger (currently one entry: repo-wide /bin/bash pinning).
- forge-skills PRs #1–#8 (github.com/forge512/agent-skills) — each carries round-1/round-2/final/closeout summary comments recording every finding disposition. The PR comment history IS the review record; read it before touching a branch.
- All owner decisions to date are recorded in the spec change logs and PR comments: `--planning` and `--update` flags (#5), deferred baseline commit (#8), `--branch-only` (#7), phase-0-2 prefix metrics (#3), scoped staleness marker (#6), seeds-skip-code (#2), README sweep post-merge (all).

## State

Five review rounds complete (2 initial + owner-decisions + final + merge-time closeout). ~160 findings fixed with regression tests across the eight branches; every suite green; all branches MERGEABLE, CI `test` pass everywhere.

| PR | Skill | Tip | Open threads | Note |
|---|---|---|---|---|
| #1 | write-handoff | ce359b7 | 0 | closed out |
| #2 | redline-file | 42dd814 | 0 | closed out |
| #3 | implement-story | 1731a43 | 0 | closed out |
| #4 | write-like-me | c891847 | 1 | owner-only thread: style-profile.json workplace snippets |
| #5 | manage-todoist | 2e52db6 | 5 | closeout agent died in rate-limit cool-off AFTER pushing + posting final comment; the 2026-08-19 04:57–04:59 re-review threads (1×P1 sync_bundle.sh + 3×P2 + 1 claude checklist note) never replied/resolved |
| #6 | consolidate-memory | e8afe4c | 7 | never had a closeout pass; 2026-08-19 04:44/04:47 re-review threads (1×P1 archive-handoffs.sh + 6 more) undispositioned |
| #7 | operate-bmad-loop | 9344eb0 | 0 | closed out; one deferred P1 recorded on-thread (predictable temp path in install_assets.sh — mkstemp fix, same class as merge_policy's) |
| #8 | manage-planning-repos | 729d04f | 0 | closed out |

Repos: ai-scratch on main @ 4df4598 (clean; note unrelated dotfiles-plan commit from another session). forge-skills main @ e3c757e; eight worktrees under `~/Code/forge-skills-worktrees/` (one per branch, all clean, all pushed). Hub planning artifacts committed (d5ce080, 36b9b72).

## Next work

1. Finish the closeout on #5 and #6: triage the listed open threads at the merge-time bar (FIX only reproducible P1 data-loss/wrong-result — the sync_bundle.sh P1 on #5 and archive-handoffs.sh P1 on #6 need real evaluation; everything else reply "deferred to post-merge follow-up" + resolve). Pattern and bar: `scratchpad` closeout briefs are gone, but the PR #2/#7/#8 "Merge-time closeout" comments show the exact format. Space replies ~75s (GitHub secondary rate limit; see Constraints).
2. Owner merges the PRs (any order; only seam: #8's board path exit-3 fallback until #3 merges).
3. Post-merge sweep, one commit on forge-skills main: sync root README Tests list + Layout bullet (`scripts/`), fold the EOF Makefile/CI registrations into the canonical `test:` list.
4. Remove the eight worktrees (`git worktree remove`) and delete merged branches.
5. Work the deferred backlog: the on-thread deferred lists in each PR's closeout comment (~40 items), the #7 install_assets temp-path P1, and the DW-ledger /bin/bash pinning item.

## Constraints to honor

- Merge-time bar for any further automated-review findings: fix only reproducible P1 data loss / wrong result; everything else reply + resolve as deferred. Codex re-reviews EVERY push — do not restart the loop.
- No merge/rebase/squash/force-push on the PR branches; one commit per intervention.
- GitHub secondary rate limit trips after ~6 rapid review-thread replies and takes ~30 min of full quiet to clear; space replies 75s from the start.
- Parallel agents must namespace scratch files (`scratchpad/pr<N>/…`); the shared root caused three collisions, including a wrong-PR comment (caught and patched).
- Hard rules for any code touched: bash 3.2 + BSD; stdlib-only Python, allow_abbrev=False, no tracebacks; failures non-zero + stderr, stdout machine-readable; shims only in tests; markdownlint clean; scope per-skill.
- Do not resolve #4's style-profile thread — owner-only.
- bmad-loop pins and hub conventions per `memory/bmad-loop-pins.md` and hub CLAUDE.md are unchanged by all of this.

## Open user inputs

- style-profile.json: scrub the verbatim workplace Slack snippets (tenant names, subteam handle), replace with synthetic, or accept as-is? (Private repo; scrubbing is test-safe.)
- Merge timing/order, and whether the post-merge sweep + worktree cleanup should run unattended once merges land.

## Suggested skills

- `operate-bmad-loop` / `manage-planning-repos` — NOT needed next session; this is PR-closeout work, not story work.
- `consolidate-memory` — after merge + sweep, a pass would fold this saga's durable lessons (rate-limit pacing, scratchpad namespacing, reviewer-loop policy) into memory.
- dispatching parallel Opus agents per PR worked well; reuse the closeout-brief pattern from the PR #2/#7/#8 comments if #5/#6 are done by agent rather than by hand.

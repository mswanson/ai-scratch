---
title: 'WP3: implement-story bookkeeping scripts'
type: 'feature'
created: '2026-08-10'
status: 'done'
review_loop_iteration: 0
baseline_commit: '3ee1ea3'
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** implement-story's highest-volume mechanical work is hand-executed: YAML step logging with UTC timestamps dozens of times per story, metrics arithmetic the checker already knows how to recompute (but only to validate, never to produce), story-file gate extraction at three sites, board mechanical state the prose itself labels "mechanical", and thrice-restated command/environment/label procedures.

**Approach:** A shared Python module holds the checker's parsing + metrics math; `session-state.py` writes state, `check_story_state.py --emit` produces the metrics block, `inspect-story.py` and `compute-board-state.py` extract story/board facts; three bash scripts cover command detection, environment checks, and PR labels. Prose swaps at every replaced site. One PR on branch `scripts/implement-story`.

## Boundaries & Constraints

**Always:** state files written by `session-state.py` and blocks printed by `--emit` pass `check_story_state.py` unchanged-in-judgment (same fields, same tolerances); `metrics.code_review.totals` stays a single-line flow mapping, unset numerics are literal `null` (checker requirement); Python stdlib-only; shell is macOS bash 3.2 + BSD; Makefile/CI registration is purely additive at file ends (separate `.PHONY` line, `test: <target>` union line, CI steps appended last) so the open WP1 PR cannot conflict; judgment stays prose (CLAUDE.md command authority, triage, go/no-go, curated board prose); universal script contract (terminate on every argv; usage → stderr + exit 1; failures non-zero + stderr, no success output; machine-readable stdout).

**Ask First:** any new REQUIRED key in the checker (template additions that stay unvalidated are fine); any change to existing checker failure semantics.

**Never:** parse legacy freeform deferred-work.md mechanically (three incompatible shapes exist; DW-format only, flag legacy); auto-write board HTML (script emits data; LLM writes prose); touch other skills' files.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| session-state start/complete | `start-step 2.1 "lint"` then `complete-step 2.1` | Entry appended with both UTC ISO timestamps, `current_step` bumped, checker-exact indentation | unknown step id on complete → exit 1 |
| session-state set/append/note | `set hil_review pending`, `append pr_urls <url>`, `note "board_sync: failed — x"` | Scalar set; list-key append; freeform note attached to current step | unknown scalar key → exit 1 naming it |
| --emit | State with completed_steps + cycles | Metrics block (implementation + code_review.totals) printed in checker-exact format; numbers match the checker's own recomputation | malformed state → non-zero + reason |
| inspect-story | Story with ticket header, active + struck `⚠️ OPEN`, `- Repo:` lines, `## Tasks / Subtasks` boxes | JSON: ticket{id,link,matches_prefix}, open_flags (active only) + resolved_flags (struck/annotated), repos, tasks{total,checked,unchecked[]} | zero matches in a section → `"none_found"` marker, never silence |
| compute-board-state | sprint-status.yaml + DW-format ledger | JSON: updated stamp, merged count, progress pct, by-state tiles, story pills, epic fractions + eyebrows, gate chain, open DW entries | legacy ledger → `deferred_format:"legacy"`, no entries; missing file → error |
| detect-command | repo with package.json scripts / Makefile targets | JSON candidates per kind (test/lint/typecheck) + `claude_md_present` flag; never claims final authority | no candidates → empty list, exit 0 |
| check-environment | repos + symlink roots | Per repo: symlink resolves, clean tree, default branch (origin HEAD) | degraded fields, per-repo error objects |
| ensure-pr-labels | repo + `label:color` pairs | created/existing report; idempotent | permission-denied → distinct status + non-zero |

</frozen-after-approval>

## Code Map

- `tests/check_story_state.py` -- pure parse helpers at 34-93; metrics math INLINE in main() (161-165, 184-204) — must be factored out first; totals parsed from one physical line; required keys :124-129
- `assets/session-state-template.yaml` -- 30-line schema; gains `pr_urls: []` (prose at phase-3-ship.md:39 instructs it; no key exists — contract-sheet delta)
- `references/` -- swap sites: phase-0-pregate.md:6-19,22-23,28-36,43-46; phase-1-implement.md:3,40; phase-2-validate.md:10-18,38,53-56; phase-3-ship.md:9-10,23-26,39; phase-4-review.md:32-33,76-78 (copy its existing `bash "{skill-root}/scripts/…"` invocation pattern); phase-5-close.md:43-45,54,72; board-sync.md:32-41,53-55; SKILL.md:75-78
- `scripts/` -- new: `story_state_lib.py` (shared module), `session-state.py`, `inspect-story.py`, `compute-board-state.py`, `detect-command.sh`, `check-environment.sh`, `ensure-pr-labels.sh`
- `tests/` -- extend `test_check_story_state.py` (Python scripts, zero new registration); new `test_is_scripts.sh` (shell trio, gh/git shims per `test_fetch_script.sh` pattern); README renumber duplicate "9."
- `assets/implement-story-config.yaml` -- `pr.labels` + colors 1D76DB/B60205 (phase-3-ship.md:23-26) feed ensure-pr-labels

## Tasks & Acceptance

**Execution:**
- [x] `scripts/story_state_lib.py` -- move the checker's parse helpers + factor its inline metrics math into `compute_step_metrics(steps)` / `compute_cycle_totals(cycles)`; writer functions produce checker-exact indentation (totals single-line, `null` literals)
- [x] `tests/check_story_state.py` -- import the lib (path-relative), behavior-identical validation, plus `--emit` printing the computed metrics block
- [x] `scripts/session-state.py` -- verbs `start-step <id> <name>`, `complete-step <id>`, `set <key> <value>` (template scalar keys only), `append <list-key> <value>`, `note <text>`; auto UTC ISO timestamps; add `pr_urls: []` to the template
- [x] `scripts/inspect-story.py` -- ticket per `{tracker.ticket_prefix}-<number>`; `⚠️ OPEN` active vs resolved (exclude `~~…~~` struck and same-line resolved annotations — qualifier from the sibling dev-workflow doc, missing from phase-0-pregate.md: add it to the prose); repos from `## Dev Notes` `- Repo:` bullets; `## Tasks / Subtasks` checkbox census
- [x] `scripts/compute-board-state.py` -- sprint-status.yaml (flat `development_status` map, `epic-N`/`N-M-slug`/`epic-N-retrospective` keys) → board mechanical JSON; DW-format ledger (`### DW-<n>:` + `status:`) → open entries; legacy → flagged, skipped
- [x] `scripts/detect-command.sh` / `check-environment.sh` / `ensure-pr-labels.sh` -- per matrix; label colors parameterized with 1D76DB/B60205 defaults
- [x] Prose swaps at every Code Map site: script invocation + interpret, keeping CLAUDE.md authority, halt/ask branches, and judgment text; board-sync deferred panel stays curated prose fed by the script's DW data; README duplicate "9." renumbered
- [x] `tests/` -- extend test_check_story_state.py (lib equivalence: emit-then-check round-trip must pass; session-state sequences; inspect fixtures incl. struck OPEN; board fixtures DW + legacy); new `test_is_scripts.sh` with shims; Makefile/CI additive-at-end registration

**Acceptance Criteria:**
- Given a state file built purely by `session-state.py` verbs then `--emit`, when the checker runs, then zero FAILs (round-trip proof).
- Given the 14 existing checker scenarios, when the refactored checker runs, then identical pass/fail results and messages.
- Given the prose after swaps, when read end-to-end, then no site instructs hand-editing state YAML, hand-computing metrics, eyeballing gates, or hand-tabulating board state; every invocation uses the phase-4 pattern.
- Given `git merge` of this branch onto a tree containing WP1's Makefile/CI changes, when merged, then no conflicts (additive-at-end verified by test-merging locally against `scripts/write-handoff`).

## Spec Change Log

## Design Notes

Contract-sheet deltas folded in: schema gap (`pr_urls`, freeform notes), OPEN-resolution qualifier, no-corpus defensive regexes (fixtures encode the spec), deferred-work format fork (DW-only mechanical), inline-math extraction prerequisite, totals single-line constraint, README duplicate numbering. Python tests ride the already-registered `test-check-story-state` target; only the shell suite adds registration.

## Verification

**Commands:**
- `python3 -m py_compile` all Python; `bash -n` all shell -- clean
- `make test-check-story-state` -- 14 legacy + new, 0 failed
- `bash tests/test_is_scripts.sh` then `make test` -- exit 0
- `git merge --no-commit --no-ff scripts/write-handoff` (throwaway worktree) -- no conflicts, then aborted
- `make lint-docs` -- 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat` shows only `skills/implement-story/**` + additive Makefile/CI tails.

## Suggested Review Order

**Shared library (everything else stands on this)**

- Metrics math factored from the checker's inline main()
  [`story_state_lib.py:112`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/story_state_lib.py#L112)
- Newline-rejecting scalar formatting (state-file injection guard)
  [`story_state_lib.py:214`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/story_state_lib.py#L214)
- Quote-aware flow-list scanner (comma-corruption fix)
  [`story_state_lib.py:352`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/story_state_lib.py#L352)

**State verbs**

- abort-step crash recovery; add-cycle closes the last hand-edited section
  [`session-state.py:149`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/session-state.py#L149)

**Gate extraction**

- Fence-aware single-pass scan; resolved-annotation tightening
  [`inspect-story.py:141`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/inspect-story.py#L141)
- empty_sections marker replaces the none_found sentinel
  [`inspect-story.py:54`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/inspect-story.py#L54)

**Board + shell trio**

- Tolerant sprint-status parsing, duplicate-key hard error, orphan-epic synthesis
  [`compute-board-state.py:1`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/compute-board-state.py#L1)
- Candidates-only command detection; env facts; idempotent labels with rate-limit vs permission split
  [`detect-command.sh:1`](../../../forge-skills-worktrees/implement-story/skills/implement-story/scripts/detect-command.sh#L1)

**Prose + peripherals**

- Gate wording: tasks.total > 0 AND unchecked == []
  [`phase-2-validate.md:1`](../../../forge-skills-worktrees/implement-story/skills/implement-story/references/phase-2-validate.md#L1)
- Verb reference incl. pending-marker semantics
  [`session-state.md:1`](../../../forge-skills-worktrees/implement-story/skills/implement-story/references/session-state.md#L1)
- 156-check Python suite + 48-check shell suite; additive-at-end registration
  [`test_check_story_state.py:1`](../../../forge-skills-worktrees/implement-story/skills/implement-story/tests/test_check_story_state.py#L1)

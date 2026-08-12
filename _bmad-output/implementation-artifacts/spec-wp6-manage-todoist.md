---
title: 'WP6: manage-todoist validator + pomodoro math'
type: 'feature'
created: '2026-08-11'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'e3c757e' # corrected: main moved (getfqdn CI hotfix) before worktree creation
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
---

<frozen-after-approval reason="human-owned intent — pre-approved by user instruction 2026-08-11 (run WP4-WP8 continuously)">

## Intent

**Problem:** manage-todoist's Common-mistakes checklist (~6 simultaneous rules: P1-needs-date, priority-as-string, duration format, label-namespace-by-project, mode-on-active, Habits/AREAS sections) is re-derived from prose on every write, and its own eval history (evals 2/5/6/7) documents exactly these misses. Plan-today sums mixed-format durations by eye. The bundle graduation/sync steps are freehand file ops.

**Approach:** `validate_task.py` (draft-task JSON in → violations out, run before every MCP write), `pomodoro_sum.py` (find-tasks JSON in → totals + overcommit), `sync_bundle.sh` (local copy/graduate). MCP calls, Eisenhower classification, mode selection, and label-value choice stay LLM. One PR on branch `scripts/manage-todoist`.

## Boundaries & Constraints

**Always:** Python stdlib-only, bash 3.2 + BSD, universal contract; validator enforces namespace SCOPE rules only, never the volatile label inventory (reference_todoist_system.md stays the LLM's lookup); duration format validated strictly but mode-range advisory-only (never a hard reject — the skill says real time wins); focused-work inclusion for the 150m budget is parameterized `--exclude-modes` with default `moving,adulting` (the only fillers SKILL.md names — default flagged to user in the PR, adjustable without code); registration additive-at-end (trivial keep-both conflict with open PRs accepted, noted in PR body).

**Ask First:** any rule NOT derivable from SKILL.md's text; changing the 150m threshold or the default exclusion list beyond the documented reading.

**Never:** call the Todoist API or MCP from scripts; validate specific label values against the inventory doc; auto-fix a draft (report violations; the LLM corrects); cross-machine sync or claude.ai upload in sync_bundle.sh (stays manual, documented).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| validate clean | p2 task, dueString, mode label, work project, valid duration | `{"violations": [], "ok": true}` | N/A |
| validate violations | int priority, P1 no date, `feature:*` on non-Auth0 project, p2 without `mode:*`, Habits without sectionId, `duration: "0m"`/`"25h"` | one violation per rule with rule id + message (numeric-priority coercion suggestion REMOVED 2026-08-11: UI vs REST semantics invert) | exit 0 (violations are data); malformed JSON → exit 1 stderr |
| CORRECTED 2026-08-11 (review, one-possible-reading): P1-date satisfied by `dueString` or `deadlineDate` (the real MCP fields); `dueDate` is not an API parameter and is itself flagged; `projectTopLevelName` is a documented LLM-injected field — absent → scope/section checks skip with a `project-unknown` advisory | | | |
| validate suggest | `--suggest` with mode label | default duration + range from the mode table | N/A |
| pomodoro sum | find-tasks JSON, mixed `25m`/`1h30m`/`1.5h`/`{amount,unit}` durations | total minutes, per-task breakdown, focused-total (excluding excluded modes), `overcommit` vs 150m | unparseable duration → listed in `unparsed[]`, excluded from total, exit 0 |
| pomodoro empty | no tasks with durations | totals 0, overcommit false | N/A |
| sync bundle | `<dest>` (+`--from <src>` graduate) | full copy incl. resources/, stale source removed only with --from; report | dest inside source → exit 1; missing source → exit 1 |

</frozen-after-approval>

## Code Map

- `skills/manage-todoist/SKILL.md` -- rules at :23-30 (priorities, P1-date, day-fits), :31-42 (mode table), :44 + :50 (duration string, priority string), :54-68 (label namespaces), :70-86 (modes), :123-131 (Application bar), :156-168 (Common mistakes checklist → becomes "run validate_task.py before every write"); plan-today workflow in resources/workflows.md:12-16, :28, :71-75 (sum → pomodoro_sum.py)
- `skills/manage-todoist/resources/deployment.md` -- :40-46 graduation, :77-89 sync → sync_bundle.sh for the local half; cross-machine/claude.ai stays manual
- `skills/manage-todoist/scripts/` -- new: `validate_task.py`, `pomodoro_sum.py`, `sync_bundle.sh`
- `skills/manage-todoist/tests/test_mt_scripts.py` -- new suite + additive-at-end registration
- `skills/manage-todoist/evals/` -- untouched (but rules cite eval ids in comments)

## Tasks & Acceptance

**Execution:**
- [x] `scripts/validate_task.py [--suggest] < draft.json` -- rules: priority string enum p1-p4 (+coercion suggestion), P1 requires due, duration format (`Nm`,`NhNm`,`N.Nh`, >0, ≤24h) strict / range advisory, `feature:*` only on Auth0-scoped projects, `area:*` only Habits/AREAS, `mode:*` required on p1-p3, Habits/AREAS require Work/Personal sectionId; draft carries `projectTopLevelName` the LLM resolves; each rule commented with its eval id where one exists
- [x] `scripts/pomodoro_sum.py [--exclude-modes moving,adulting] [--budget 150] < tasks.json` -- per matrix; accepts both duration-string and `{amount,unit}` shapes
- [x] `scripts/sync_bundle.sh <dest> [--from <src>]` -- rsync-style full copy, graduate removes source only with --from; `unset CDPATH`, arg validation, refuse dest-inside-source
- [x] SKILL.md + resources/workflows.md + resources/deployment.md prose swaps; checklist section becomes the validator invocation + the judgment-only leftovers (capture-vs-execute, batch-≤10 stays inline prose as consciously-skipped trivia per plan)
- [x] `tests/test_mt_scripts.py` -- every matrix row, every validator rule pass+fail, both duration shapes, exclusion parameterization, sync fixtures; additive-at-end registration

**Acceptance Criteria:**
- Given a draft violating all six rules at once, when validate_task.py runs, then exactly six violations with distinct rule ids.
- Given tasks summing 160 focused minutes plus 60m of `mode:moving`, when pomodoro_sum.py runs with defaults, then focused total 160, overcommit true, moving excluded and reported.
- Given SKILL.md post-swap, then the checklist section instructs the validator before every add/update call and the Eisenhower/mode-selection judgment prose is intact.
- Given `make test`, all green; Makefile/CI diff additive-at-end only.

## Spec Change Log

- **2026-08-11, review round (factual corrections inside frozen matrix, one-possible-reading rule).** Blind Hunter verified against the live MCP schemas: `dueDate` does not exist (ghost field silently dropped by the API — a validated P1 would land dateless); real fields are `dueString`/`deadlineDate`. `projectTopLevelName` was an undocumented synthetic dependency causing false scope violations on realistic drafts. Also restored: the checklist's dropped duration-required rule; killed: numeric priority coercion suggestion (UI/REST inversion). Frozen matrix annotated in place; both hunters' remaining findings routed to the patch round.

## Design Notes

Focused-mode default (`--exclude-modes moving,adulting`) is the only reading SKILL.md:29 supports ("moving/adulting fill the breaks"); parameterized so Swany can adjust without code — flagged in the PR body per the plan's Open Decision 3. Rules validate scope, not inventory: label VALUES change (audit trail shows renames); namespace membership rules don't.

## Verification

**Commands:**
- `python3 -m py_compile` + `bash -n`; `python3 skills/manage-todoist/tests/test_mt_scripts.py` 0 failed; `make test` exit 0; `make lint-docs` 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat`: only `skills/manage-todoist/**` + additive tails.

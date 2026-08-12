---
title: 'WP4: consolidate-memory mechanical scripts'
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

**Problem:** consolidate-memory's safety-critical mechanics run freehand: the Phase 0 checkpoint (LLM date math, self-reported verification), the Phase 1 corpus partition (many manual listings; a missed file silently violates the no-loss prime directive), scout inventory rows, handoff archival moves, mirror sync, and the staleness stamp.

**Approach:** Six scripts under `skills/consolidate-memory/scripts/` plus two prose-only fixes; SKILL.md and references/memory-scout.md swap how-to for run-and-interpret. Slice-sizing, dedup/contradiction judgment, the Phase 3 approval gate, and prune decisions stay prose. One PR on branch `scripts/consolidate-memory`.

## Boundaries & Constraints

**Always:** bash 3.2 + BSD; universal contract (terminate on every argv; usage → stderr exit 1; failures non-zero + stderr, never success output; stdout machine-readable); `unset CDPATH`; validate arg counts; checkpoint policy is abort-and-report on a dirty tree (never auto-stash/auto-commit user WIP — plan Open Decision 4, recommended default adopted); mirror path always an explicit argument, never inferred; existing `tests/check_consolidation.sh` self-check stays wired; new tests extend `tests/test_check_consolidation.sh`'s registered suite (zero Makefile/CI churn: a sibling scenario file invoked from it is fine).

**Ask First:** any change to `check_consolidation.sh` failure semantics; any auto-deletion beyond `git mv`/`mv` relocations.

**Never:** scripts deciding WHAT to prune, merge, or archive (they execute lists the LLM decided); writing into `_bmad/_memory/` (agent sidecar memory, read-only per hub rules); archiving into a qmd-indexed collection root.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| checkpoint clean git | clean tree | branch `memory-consolidation-<date>` created; JSON `{is_git:true, ref, checkpoint_verified:true}` | branch exists → suffix `-2` etc. |
| checkpoint dirty git | modified files | NO action; JSON `{aborted:"dirty tree", dirty:[…]}` | exit 2 |
| checkpoint non-git | plain dir + scope path | timestamped backup copy; JSON with backup path + verified | copy failure → exit 1, partial cleaned |
| inventory plan | project root (+BMAD detect) | JSON manifest: slices {name, files[{path,size,mtime}]} for per-subfolder/handoffs/stragglers/bmad + `unrecognized[]` listed loudly | unreadable dir → exit 1 |
| stat rows | file list incl. handoffs | TSV: path, size, mtime, frontmatter date/status for `memory/handoffs/*` (checker's awk reused) | missing file → row with ERROR field, exit 1 at end |
| archive handoffs | decided paths + legacy dir present | `git mv` (or `mv`) to repo-root `_archive/handoffs/`, legacy `memory/handoffs/_archive/` contents relocated; move manifest | non-repo → plain mv; collision → suffix, report |
| mirror sync | repo memory dir + mirror dir | one-way rsync-style copy; report added/overwritten/removed | mirror missing → exit 1 (never create silently) |
| git date hint | file + optional pattern | `git log -S`/`--follow` dates, newest+oldest for the pattern | ambiguous → all candidates listed, exit 0 |

</frozen-after-approval>

## Code Map

- `skills/consolidate-memory/SKILL.md` -- swap sites: :34-41 (Phase 0), :43-70 (Phase 1 partition), :80-88 (external/mirror), :90-103 (BMAD sources), :147-150 (absolutize dates), :155-167 (handoff archival), :168-172 (cap check cite), :189-190 (`date +%F > memory/.last-consolidated` literal command)
- `skills/consolidate-memory/references/memory-scout.md` -- :17-22 inventory rows → stat script; scouts keep purpose/type judgment
- `skills/consolidate-memory/scripts/` -- new: `checkpoint.sh`, `build-inventory-plan.sh`, `stat-and-frontmatter.sh`, `archive-handoffs.sh`, `sync-harness-mirror.sh`, `git-date-hint.sh`
- `skills/consolidate-memory/tests/` -- `check_consolidation.sh` unchanged; `test_check_consolidation.sh` invokes a new sibling `test_cm_scripts.sh` (keeps the registered target, zero Makefile churn)

## Tasks & Acceptance

**Execution:**
- [x] `scripts/checkpoint.sh <project-root> [scope-path]` -- per matrix; date via `date +%F`; JSON verification never self-reported prose
- [x] `scripts/build-inventory-plan.sh <project-root> [scope-path]` -- one walk; buckets: per-`memory/` subfolder, handoffs, stragglers (CLAUDE.md at any level, `.claude/`, notes/, docs/decisions/, adr/, root-level scratch .md), `_bmad-output` artifacts when `_bmad/` present; `unrecognized[]` for anything unmatched — fail loud, never silently omit
- [x] `scripts/stat-and-frontmatter.sh <file>...` -- TSV rows; frontmatter `date`/`status` via the checker's exact awk for handoff paths
- [x] `scripts/archive-handoffs.sh <handoff-path>...` -- mkdir -p repo-root `_archive/handoffs/`; `git mv` in repos, `mv` otherwise; legacy `memory/handoffs/_archive/` relocation; manifest to stdout
- [x] `scripts/sync-harness-mirror.sh <repo-memory-dir> <mirror-dir>` -- one-way with add/overwrite/remove report; both args explicit
- [x] `scripts/git-date-hint.sh <file> [pattern]` -- log -S/follow date candidates
- [x] Prose swaps at every Code Map site + the two prose-only fixes (literal date command; Phase 4 cites the checker's cap grep at phase start)
- [x] `tests/test_cm_scripts.sh` invoked from `test_check_consolidation.sh` -- hermetic fixtures per matrix row (git + non-git checkpoints, dirty abort, manifest buckets incl. unrecognized, archival with legacy dir + collision, mirror add/overwrite/remove, missing-mirror refusal)

**Acceptance Criteria:**
- Given a dirty fixture repo, when checkpoint.sh runs, then nothing is stashed/committed/branched and exit is 2 with the dirty list.
- Given a fixture tree with a file matching no bucket, when build-inventory-plan.sh runs, then the file appears under `unrecognized` and the exit is 0 (loud, not fatal).
- Given the prose after swaps, when read end-to-end, then Phase 0/1 mechanics, archival moves, mirror sync, and the staleness stamp are script invocations, and the prune/merge/approval judgment text is intact.
- Given `make test`, all suites pass with zero Makefile/CI changes in the diff.

## Spec Change Log

## Design Notes

Re-audit: skill unchanged since audit baseline (last touch 01c05a0). Checkpoint dirty-tree policy fixed as abort-and-report per plan recommendation. Registration avoided entirely by chaining the new scenario file from the existing registered suite.

## Verification

**Commands:**
- `bash -n` all scripts; `make test-check-consolidation` (12 legacy + new, 0 failed); `make test` exit 0; `make lint-docs` 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat` shows only `skills/consolidate-memory/**`.

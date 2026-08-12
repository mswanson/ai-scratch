---
title: 'WP1: write-handoff prose-to-script conversion'
type: 'feature'
created: '2026-08-10'
status: 'done'
review_loop_iteration: 1
baseline_commit: '3ee1ea3' # forge-skills main at implementation start
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** write-handoff makes the LLM hand-execute mechanical work every run: today's date and filename, the frontmatter+six-section skeleton, per-repo git state for the State block, hub resolution, and the MEMORY.md link append. Freehand execution is token-expensive and fails in known ways (guessed dates, malformed skeletons the checker only catches after the fact).

**Approach:** Four scripts under `skills/write-handoff/scripts/`; SKILL.md swaps each how-to for "run X, act on output". Judgment (content, redaction, delta-scoping, ask-fallbacks) stays prose. One PR on branch `scripts/write-handoff`.

## Boundaries & Constraints

**Always:** bash 3.2 + BSD userland compatible (CI is macos-latest); no runtime deps beyond git/coreutils; machine-readable stdout, non-zero exit with reason on failure; scripts execute decided actions or compute facts, never judgment; hermetic tests (temp-dir fixtures, no network); `tests/check_handoff.sh` stays wired as the post-write self-check; commit only `skills/write-handoff/**`, `Makefile`, `.github/workflows/tests.yml`.

**Ask First:** any behavior change to `check_handoff.sh`; any new required frontmatter key or section (format change ripples to the checker and consolidate-memory).

**Never:** auto-commit or touch the user's `memory/`; modify other skills; let `resolve_handoff_dest.sh` guess on ambiguity (unresolved → prose asks the user); overwrite an existing handoff file.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Scaffold happy path | dest dir, slug, 2 repos, --story | File `YYYY-MM-DD-<slug>.md` created (mkdir -p), frontmatter + six headings in order, path printed | N/A |
| Scaffold collision | Same-name file exists | No write; prints existing path + refusal | exit 3 |
| Repo state happy path | 2 valid repo paths | One JSON object per repo: branch, worktree, dirty list, last commit | N/A |
| Repo state degraded | Detached HEAD, empty repo, non-repo path | Fields degrade gracefully (`detached@<sha>`, nulls); non-repo → error entry, others still emitted | exit 0 if ≥1 repo resolved, else 1 |
| Hub resolution | cwd inside hub (has `_bmad/` + spoke symlink) | `status=resolved hub_path=<path>` | N/A |
| Hub resolution fails | Plain repo / outside any repo | `status=unresolved`, no guess | exit 0 (unresolved is data) |
| Link ensure | MEMORY.md lacks Handoffs link | Single line appended; `added` reported; rest of file untouched | N/A |
| Link ensure no-op | Link already present | No write at all; `present` reported | N/A |
| Link ensure missing file | Path doesn't exist | No file created | exit 2 |

</frozen-after-approval>

## Code Map

- `skills/write-handoff/SKILL.md` -- prose swaps: Destination steps 1–2, Filename line, Format skeleton, After-writing step 2, References; stale Lifecycle archive path (line 82)
- `skills/write-handoff/tests/check_handoff.sh` -- unchanged; oracle for scaffold structural output (greps `^## Constraints` as prefix, so full headings pass)
- `skills/write-handoff/scripts/` -- new: `scaffold_handoff.sh`, `gather_repo_state.sh`, `resolve_handoff_dest.sh`, `ensure_handoffs_link.sh`
- `skills/write-handoff/tests/test_wh_scripts.sh` -- new hermetic suite for all four
- `Makefile`, `.github/workflows/tests.yml` -- register `test-wh-scripts` target + CI step (keep the two in sync per Makefile header)

## Tasks & Acceptance

**Execution:**
- [x] `skills/write-handoff/scripts/scaffold_handoff.sh` -- `<dest-dir> <topic-slug> <repo>... [--story S] [--epic E]`: `date +%F`, mkdir -p, refuse overwrite (exit 3), frontmatter (`date`,`topic`,`repos` list,`status: open`, optional `story`/`epic`), exact headings `## Authoritative context`,`## State`,`## Next work`,`## Constraints to honor`,`## Open user inputs`,`## Suggested skills`, print path. HARDENING: validate slug against the checker's regex (`^[a-z0-9][a-z0-9-]*$`) before any write, exit 1 on bad/empty; `--story`/`--epic` with no value → usage + exit 1 (arg loop must terminate on every argv); check `mkdir -p` and `cd`, abort non-zero on failure; atomic no-clobber write (`set -C`); YAML-quote `topic`/`story`/`epic` and each `repos` entry; stderr warning when dest does not end in `handoffs/`
- [x] `skills/write-handoff/scripts/gather_repo_state.sh` -- `<repo-path>...`: per repo emit branch, worktree root, dirty files (porcelain), last commit `%h %s` as JSON lines. HARDENING: `esc()` also strips or escapes ASCII control chars so stdout is always `json.loads`-parseable; repo with no commits → `"branch":"unborn"` (never `detached@` with empty sha); bare repo → error entry `"bare repository"`; diagnostics to stderr only
- [x] `skills/write-handoff/scripts/resolve_handoff_dest.sh` -- `[start-dir]`: walk up looking for `_bmad/` + ≥1 top-level symlink-to-git-repo; print `status=resolved|unresolved` + `hub_path`. HARDENING: guard `cd` failure → `status=unresolved` (must terminate on all inputs, including unsearchable dirs)
- [x] `skills/write-handoff/scripts/ensure_handoffs_link.sh` -- `<MEMORY.md>`: grep -F `[Handoffs](handoffs/)`, append if absent. HARDENING: stdout carries ONLY `present`/`added`; errors to stderr; verify the append succeeded before printing `added` (failed write → stderr + exit 2); guard leading-dash path args
- [x] `skills/write-handoff/tests/test_wh_scripts.sh` -- hermetic fixtures covering every I/O matrix row; scaffold output must pass `check_handoff.sh` structural checks. ADD: dangling-flag termination test (wrap in a timeout so a regression cannot hang CI); `--epic` coverage; bad-slug cases (empty, uppercase, slash); control-char commit subject parsed by `json.loads`; unborn-branch label; seam composition test (`resolve` → `$hub_path/memory/handoffs` → `scaffold` → checker passes); assert `story:` value, not just key presence; recompute date if the expected filename is absent (midnight rollover); `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` on all fixture git ops
- [x] `skills/write-handoff/SKILL.md` -- swap prose to script invocations (`{skill-root}/scripts/...`); keep section-meaning bullets and all judgment/ask text; fix Lifecycle line 82 to repo-root `_archive/handoffs/`; update References. SEAM FIXES: Destination step 1 scopes the resolver to hub-and-spoke situations only (a plain BMAD or plain repo keeps the original default — its own `memory/handoffs/` — with no prompt); step 2 states the dest argument explicitly as `<project-or-hub-root>/memory/handoffs` (the scaffold creates the dir); After-writing step 2 targets `<resolved-root>/memory/MEMORY.md`, never a bare relative path; References describe the resolver honestly (resolves when inside the hub tree; spoke sessions typically get `unresolved` → ask)
- [x] `Makefile` + `.github/workflows/tests.yml` -- add `test-wh-scripts` target and CI step (iteration-1 wiring was correct; reproduce as-is)

**Acceptance Criteria:**
- Given a clean checkout, when `make test` runs, then all suites pass including `test-wh-scripts`.
- Given a scaffold-created file in a `memory/handoffs/` fixture, when `check_handoff.sh` runs on it, then zero structural FAILs (location, filename, frontmatter, sections).
- Given SKILL.md after the swap, when read end-to-end, then no instruction remains telling the LLM to hand-construct the date, filename, skeleton, git state, or link append, and every script has an invocation with `{skill-root}` pathing.
- Given the finished branch, when the PR opens against `mswanson/forge-skills` main, then the body carries the finding→change table, the re-audit delta (stale Lifecycle path; checker-prefix note), and test evidence; no unrelated paths (e.g. `skills/manage-planning-repos/SKILL.md`) in the diff.

## Spec Change Log

- **2026-08-10, loop 1 (bad_spec).** Triggering findings (adversarial + edge-case review, several execution-confirmed on bash 3.2): option-parsing hang on dangling `--story`/`--epic`; scaffold silent exit-0 when `mkdir`/`cd`/write fails, non-atomic no-clobber; no slug validation despite the checker's filename regex; unquoted YAML scalars; control characters producing invalid JSON; unborn repo mislabeled `detached@`; resolver non-termination on `cd` failure; link script printing `added` on failed append and errors on stdout; SKILL.md seam gaps (`hub_path` → `<dest>` contract undefined so handoffs could scaffold at hub root, hardcoded `memory/MEMORY.md`, resolver unscoped for plain BMAD repos and oversold in References). Amended: per-script HARDENING contracts, SEAM FIXES, test additions, universal termination/stderr contract in Design Notes. Known-bad state avoided: scripts that hang or report success on failure; handoffs landing outside `memory/handoffs/`. **KEEP:** SKILL.md swap structure and tone (lint-clean, judgment text preserved verbatim); test-suite pattern (mktemp fixtures, cleanup trap, PASS/FAIL counters, `check_handoff.sh` as oracle); Makefile/CI wiring exactly as iteration 1; script header/usage-comment style; iteration-1 behaviors that were correct (collision exit 3, unresolved-is-data exit 0, no-trailing-newline append handling, six exact headings).

## Design Notes

Re-audit delta already folded in: SKILL.md:82 stale archive path (consolidate-memory commit 01c05a0 moved archives to repo-root `_archive/handoffs/`); scaffold emits SKILL.md's full headings, which satisfy the checker's prefix greps. JSON emitted via printf, no jq dependency; tests may use python3 for JSON assertions (already a repo test dep).

Universal script contract (loop 1): every script terminates on every argv; usage errors print usage to stderr and exit 1; every failure path exits non-zero with a stderr reason; stdout carries only the machine-readable result.

## Verification

**Commands:**
- `bash -n skills/write-handoff/scripts/*.sh` -- expected: clean parse
- `make test-wh-scripts` -- expected: PASS, every I/O row exercised
- `make test` -- expected: all existing suites still pass
- `make lint-docs` -- expected: clean (needs npx; skip offline, CI enforces)

**Manual checks (if no CLI):**
- `git diff main --stat` on the branch shows only package-scoped paths.

## Suggested Review Order

**Prose contract (what the scripts must serve)**

- Resolver-first destination logic replaces the circular hub-detection prose
  [`SKILL.md:15`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/SKILL.md#L15)
- Scaffold owns the skeleton; dest contract pinned to `<root>/memory/handoffs`
  [`SKILL.md:26`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/SKILL.md#L26)
- State block narrates on top of scripted ground truth
  [`SKILL.md:56`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/SKILL.md#L56)
- Link ensure targets the resolved root, exit-2 causes documented
  [`SKILL.md:81`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/SKILL.md#L81)

**Scaffold write path (highest-risk logic)**

- Exclusive-create then append: collision exit 3 vs write-failure cleanup, no stub left
  [`scaffold_handoff.sh:149`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/scaffold_handoff.sh#L149)
- Flag-value validation: empty, flag-shaped, quote/newline all rejected pre-write
  [`scaffold_handoff.sh:40`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/scaffold_handoff.sh#L40)

**JSON contract**

- emit_json + iconv keeps stdout json.loads-parseable on any input
  [`gather_repo_state.sh:39`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/gather_repo_state.sh#L39)
- Unborn-branch labeling distinct from detached HEAD
  [`gather_repo_state.sh:98`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/gather_repo_state.sh#L98)

**Hub resolution**

- is_hub predicate: `_bmad/` + symlink-to-repo; unresolved is data, never a guess
  [`resolve_handoff_dest.sh:49`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/resolve_handoff_dest.sh#L49)

**Idempotent link**

- Anchored variant-tolerant detection regex, used for both check and post-append verify
  [`ensure_handoffs_link.sh:36`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/ensure_handoffs_link.sh#L36)
- Single-write append chosen by trailing-newline state
  [`ensure_handoffs_link.sh:51`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/scripts/ensure_handoffs_link.sh#L51)

**Peripherals**

- Timeout harness so a parsing regression can never hang CI
  [`test_wh_scripts.sh:41`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/tests/test_wh_scripts.sh#L41)
- Seam composition test: resolve → scaffold → checker passes
  [`test_wh_scripts.sh:347`](../../../forge-skills-worktrees/write-handoff/skills/write-handoff/tests/test_wh_scripts.sh#L347)
- Suite registration, aggregate + CI
  [`Makefile:7`](../../../forge-skills-worktrees/write-handoff/Makefile#L7)
  [`tests.yml:31`](../../../forge-skills-worktrees/write-handoff/.github/workflows/tests.yml#L31)

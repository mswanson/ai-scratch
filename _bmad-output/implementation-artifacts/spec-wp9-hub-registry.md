---
title: 'WP9: manage-planning-repos hub registry + multi-hub fan-out'
type: 'feature'
created: '2026-09-27'
status: 'ready-for-dev'
review_loop_iteration: 0
baseline_commit: 'c46e2d6' # forge-skills origin/main = merge of PR #13; PR #14 also merged
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-wp8-manage-planning-repos.md'
  - '{project-root}/memory/handoffs/2026-09-25-migration-prep-skills-dotfiles-agents-md.md'
---

<frozen-after-approval reason="human-owned intent — owner decisions 2026-09-27: registry is built by the skill from repo-side evidence, never from the owner's dotfiles; the one-line template marker is approved">

## Intent

**Problem:** manage-planning-repos and operate-bmad-loop operate one repo at
a time, and nothing on a machine knows which repos are hubs. When a skill
changes (a pin bump, a Step 3 template change, a new Verify check) every hub
is visited by hand, and hubs get missed. The only cross-repo record today is
the owner's dotfiles qmd index: machine-specific, hand-maintained, and
invisible to the other developers who use these skills. On the owner's
machine 18 directories carry `_bmad/`; roughly five are live hubs, the rest
are worktrees and experiments, so discovery by `_bmad/` presence is wrong.

**Approach:** the skill builds the registry itself, on any machine, from
evidence the skill already writes into repos: a one-line marker in the hub
and spoke CLAUDE.md templates, the hub's `## Spoke Repositories` table (the
same row grammar verify_hub.sh and bootstrap_structure.sh parse), and
`docs/project-context.md` in spokes. A `registry.py` scans configurable
roots, excludes worktrees, derives spokes from hub tables (never by walking
the filesystem), preserves a user-owned ignore list and pinned entries
across rebuilds, and writes JSON. A `hubs.sh` fan-out runs `list`, read-only
`verify`, or an arbitrary prompt across registered hubs in parallel via
`claude -p`, one invocation per hub, one summary. Mutating fan-out needs an
explicit `--apply`. Menu item 4. Existing hubs (which all dropped the
template's leading comment, so none carries a marker today) are detected by
fallback evidence and get the marker on their next Setup/Repair.

## Boundaries & Constraints

**Always:** bash 3.2 + BSD userland; Python stdlib only (hence JSON, not
YAML: no PyYAML, and TOML has a stdlib reader but no writer); the universal
script contract (terminate; failures non-zero + stderr, never success
output; stdout machine-readable; `unset CDPATH`; arg validation; refuse
option-like positionals); the spoke-table row grammar is verify_hub.sh's,
byte for byte (pipe-led rows, indentation allowed, name backticked or
plain, header/separator/`{{placeholder}}` rows skipped); a git worktree
(`.git` is a file, or `git rev-parse --git-common-dir` is not `.git`) is
never a hub; scanning never follows symlinks and never descends into
`node_modules`, `.git`, or a discovered repo's subtree; the registry lives
at `${XDG_CONFIG_HOME:-$HOME/.config}/planning-repos/registry.json` unless
`--out` says otherwise; rebuilds preserve `ignore` and `pinned` verbatim;
`hubs.sh verify` and `hubs.sh run` without `--apply` run
`--permission-mode dontAsk` with an allowlist limited to the skill's own
read-only scripts, so an unattended fan-out cannot edit a repo; `--apply`
is the only path to `acceptEdits`; one `claude -p` per hub, cwd set to the
hub, output captured per hub, summary after all finish; a hub whose run
fails or times out is one `error` row, never a reason to stop the others;
tests hermetic (temp roots, `claude` and `git` PATH shims where needed),
chained from `test_mpr_scripts.sh` (zero Makefile/CI churn); markdownlint
clean.

**Ask First:** any template content change beyond the one marker line
(that line is pre-approved); any change to verify_hub.sh's existing
output lines; a default roots list other than `~/Code`.

**Never:** read the owner's dotfiles, the qmd index, or any file outside
the scanned roots and the registry path to decide what a hub is; run a
mutating prompt across hubs without `--apply`; drop or rewrite a `pinned`
or `ignore` entry the user wrote; delete anything; run Repair, Setup, or
the BMAD installer from the fan-out (a prompt may ask a per-hub session to,
and that session's own confirmation rules apply); reimplement
verify_hub.sh's checks in the registry code.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| marked hub | repo under a root; `CLAUDE.md` first line is `<!-- planning-repo: hub -->` | entry `{name, path, kind:"hub", marker:true, spokes:[...]}` | N/A |
| legacy hub | no marker; `CLAUDE.md` has `## Spoke Repositories` with ≥1 parsable row, or `detect_repo_type.sh` guesses `hub` | included, `marker:false`; Verify reports `GAP: CLAUDE.md marker missing (Setup step 3 adds it)` | N/A |
| standalone BMAD | `_bmad/` present, no marker, no spoke table | `kind:"standalone-bmad"`, listed under `others`, not fanned out unless `--include-standalone` | N/A |
| experiment dir | `_bmad/` present, no marker, no table, no `docs/project-context.md` | not registered; appears in `excluded` with reason `no hub evidence` | N/A |
| worktree | `.git` is a file, or common dir differs | never a hub; `excluded` with reason `worktree of <path>` | N/A |
| spoke derivation | hub table row `| name | path | ... |` | `spokes[]` entry `{name, path, resolves:true/false, project_context:true/false}`; path taken from the table, resolved relative to the hub when relative | unresolvable path → `resolves:false`, still listed |
| shared spoke | same real path in two hubs' tables | listed under both hubs; `spokes_index` maps path → hubs | N/A |
| ignore list | existing registry has `ignore:["/path/x"]` | `/path/x` never registered even if it has a marker; list carried over untouched | N/A |
| pinned entry | existing registry has `pinned:[{name,path}]` | included as a hub even without evidence, flagged `pinned:true`; carried over untouched | pinned path missing on disk → `present:false`, kept |
| roots | `--root` repeatable; default `~/Code` | each root scanned to `--max-depth` (default 4); roots recorded in the file | root missing → exit 1 naming it |
| rebuild | registry exists | full rewrite of `hubs`, `others`, `excluded`; `ignore`, `pinned`, `roots` preserved; `generated_at` updated | unreadable/malformed existing file → exit 1 untouched |
| `hubs.sh list` | registry present | one row per hub: name, path, branch, dirty flag, BMAD version from `_bmad/_config/manifest.yaml`, bmad-loop pin if any; JSON with `--json` | registry absent → exit 3 `run registry build first` |
| `hubs.sh verify` | N hubs, `claude` on PATH | N parallel `claude -p` runs (`--jobs`, default 4), each told to run manage-planning-repos Verify and print the report; summary: per hub FAIL/GAP/drift counts + exit; overall exit 1 if any FAIL or error | `claude` absent → exit 3; per-hub timeout (`--timeout`, default 600s) → `error` row |
| `hubs.sh run "<prompt>"` | prompt, no `--apply` | same fan-out with the prompt, `dontAsk` + read-only allowlist | prompt that needs edits fails inside the session and lands as `error`/text, never edits |
| `hubs.sh run --apply` | prompt + `--apply` | `acceptEdits`; prints the hub list and asks once for `yes` before launching unless `--yes` | N/A |
| stamp on repair | Setup step 3 on a repo whose `CLAUDE.md` lacks the marker | marker line prepended (hub or spoke per confirmed type), nothing else changed; reported in the Setup commit list | N/A |

</frozen-after-approval>

## Story

As a developer running several BMAD planning hubs on one machine,
I want manage-planning-repos to know which repos are hubs and to run its
read-only checks (or a prompt I give it) across all of them at once,
so that a skill change reaches every hub instead of whichever ones I
remember.

## Code Map

- `skills/manage-planning-repos/assets/hub-CLAUDE.md`,
  `assets/spoke-CLAUDE.md` -- first line becomes
  `<!-- planning-repo: hub -->` / `<!-- planning-repo: spoke -->` (the
  existing hub template comment moves below it; spoke template gets its
  equivalent). One line each; no other content change.
- `skills/manage-planning-repos/scripts/registry.py` -- new, stdlib.
  Subcommands: `build [--root ... --max-depth N --out F]`, `show [--json]`.
  Reuses `detect_repo_type.sh` (subprocess) for the legacy-hub guess
  rather than re-deriving; parses the spoke table with the verify_hub.sh
  grammar (port the awk faithfully; add a fixture that feeds both the same
  table and diffs the row lists).
- `skills/manage-planning-repos/scripts/hubs.sh` -- new. `list`, `verify`,
  `run "<prompt>" [--apply] [--yes]`, common flags `--jobs`, `--timeout`,
  `--include-standalone`, `--registry F`. Bash 3.2 job control (`&` +
  `wait` on PIDs, per-hub temp files; no `wait -n`). Reads the registry
  via `registry.py show --json`.
- `skills/manage-planning-repos/scripts/stamp_marker.sh` -- new.
  `stamp_marker.sh <CLAUDE.md> hub|spoke`: prepends the marker if absent,
  idempotent, byte-preserving otherwise; Setup step 3 cites it.
- `skills/manage-planning-repos/tests/verify_hub.sh` -- repository-guidance
  bucket gains one line: marker present → `ok`, absent → `GAP`. No other
  output changes.
- `skills/manage-planning-repos/SKILL.md` -- menu item 4; new
  `## 4. Registry and fan-out` section (build, list, verify, run, `--apply`
  rule, what the registry is not); Step 3 cites `stamp_marker.sh`; Verify
  prose names the marker GAP; References list updated.
- `skills/manage-planning-repos/tests/test_registry.sh` -- new, chained
  from `test_mpr_scripts.sh`. `claude` PATH shim records argv and cwd and
  emits canned JSON; `git` real (temp repos and a real worktree fixture).
- `skills/manage-planning-repos/tests/README.md` -- runnable tests section
  + eval scenarios 20-24 (below). Root `README.md` skill-table row mentions
  the registry and fan-out.

## Tasks & Acceptance

**Execution:**
- [ ] Marker line in both templates; `stamp_marker.sh` with idempotency and
  byte-preservation tests
- [ ] `registry.py build`: scan, worktree exclusion, marker + legacy
  detection, spoke derivation via the shared row grammar, ignore/pinned
  preservation, `excluded` with reasons, JSON schema documented at the top
  of the file
- [ ] `registry.py show [--json]`
- [ ] `hubs.sh list|verify|run` per matrix, including the `--apply`
  confirmation and the summary format (one line per hub + totals; `--json`
  variant)
- [ ] `verify_hub.sh` marker GAP line + `test_verify_hub.sh` scenarios
  (marker present ok; absent GAP; present on a spoke ok)
- [ ] SKILL.md swaps at every Code Map site; menu text; References
- [ ] `tests/test_registry.sh` chained from `test_mpr_scripts.sh`; README
  and eval scenarios

**Acceptance Criteria:**
- Given a temp root holding a marked hub, a legacy hub (spoke table, no
  marker), a worktree of the marked hub, and a bare `_bmad/` directory,
  when `registry.py build --root <tmp>` runs, then the JSON lists exactly
  the two hubs (the legacy one `marker:false`), the worktree and the bare
  directory appear in `excluded` with their reasons, and the legacy hub's
  spokes match the rows verify_hub.sh parses from the same table.
- Given an existing registry with an `ignore` path and a `pinned` entry,
  when `build` runs again, then both are byte-identical in the output and
  the ignored path is absent from `hubs` even though it carries a marker.
- Given three registered hubs and a `claude` shim, when `hubs.sh verify`
  runs, then the shim records three invocations with cwd set to each hub,
  `--permission-mode dontAsk`, an allowlist containing only the skill's
  read-only scripts, and the summary has three rows and the correct
  overall exit; when one shim invocation exits non-zero, that hub is an
  `error` row and the other two still report.
- Given `hubs.sh run "<prompt>"` without `--apply`, then no invocation
  carries `acceptEdits`; with `--apply` and without `--yes`, the command
  prints the hub list and waits for `yes`.
- Given a hub whose `CLAUDE.md` lacks the marker, when Setup step 3 runs
  `stamp_marker.sh`, then the file differs by exactly one leading line and
  `verify_hub.sh` reports the marker `ok`.
- Given `make test`, all suites green with zero Makefile/CI changes; `make
  lint-docs` 0 issues.

## Dev Notes

- **Why JSON.** Python stdlib only is a hard constraint in this repo
  (operate-bmad-loop's `merge_policy.py` is line-based for the same
  reason). YAML would need PyYAML or a hand parser; the file is
  machine-owned, so JSON costs nothing.
- **Why a marker and a fallback.** The template's leading HTML comment was
  meant to identify instantiated files, and both live hubs on the owner's
  machine (`ai-scratch`, `orderly/product_planning`) deleted it. The new
  marker is one line, named for what it is, and Verify reports its absence
  so it comes back on the next Repair. Until then the spoke table is the
  evidence, which is exactly the evidence `detect_repo_type.sh` already
  prints (`CLAUDE.md spoke table: N named, M resolving`).
- **Why spokes are derived, not scanned.** A spoke is a spoke because a
  hub says so; scanning for `docs/project-context.md` would register every
  repo that ever ran step 7. Derivation also gives the shared-spoke case
  for free.
- **`claude -p` flags to confirm during implementation** against the
  installed CLI (2.1.28x): `--permission-mode` accepts `acceptEdits`,
  `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan`;
  `--allowedTools "Bash(bash */manage-planning-repos/tests/verify_hub.sh *)"`
  shape; `--output-format json` for the summary parser. The shim tests
  argv shape; one real smoke run on two hubs is part of Verification.
- **Concurrency in bash 3.2.** No `wait -n`, no associative arrays. Launch
  up to `--jobs` background runs, track PIDs in a space-separated string,
  poll with `kill -0` and `sleep 1`, collect outputs from per-hub files
  under one `mktemp -d`. The `test_verify_hub.sh` note on here-strings
  applies: read lists via process substitution.
- **The stale 18.** Discovery on the owner's machine today finds 18
  `_bmad/` directories. Expected registry after this lands: `ai-scratch`
  (spokes dotfiles, forge-skills), `orderly/product_planning` (orderly-app),
  `lyceum/lyceum-planning` (lyceum), `auth0/star0`, `marshal/marshal-planning`
  as hubs or standalone depending on their tables; `product_planning-{florida,
  spine,stability}`, `star0-beta`, `orderly-app-prod` as worktree/copy
  exclusions; `bmad-610`, `auth0-bmad-poc`, `lyceum/test`, `bmad/*`,
  `corex-webapp` as `no hub evidence`. Use this as the manual smoke check.
- **Out of scope, recorded so nobody re-argues it:** tracking the generated
  registry in the owner's dotfiles (a dotbot symlink to the XDG path, owner's
  job, later); generating qmd collections from the registry (a natural
  follow-up for Step 5, not this WP); running operate-bmad-loop Verify in the
  fan-out (a prompt can ask for it; a dedicated verb can come once the
  registry exists).

### Project Structure Notes

- New scripts follow the existing `scripts/*.sh` + `tests/test_*.sh`
  layout; `registry.py` is the skill's first Python script, placed in
  `scripts/` like operate-bmad-loop's `merge_policy.py`.
- Test chaining, not Makefile edits: `test_mpr_scripts.sh` sources or
  execs `test_registry.sh` at its end, as `test_verify_hub.sh` does for it.

### References

- [Source: forge-skills `skills/manage-planning-repos/SKILL.md`] menu, Step 3, Verify prose, References
- [Source: forge-skills `skills/manage-planning-repos/tests/verify_hub.sh`] spoke-table row grammar (PR #13)
- [Source: forge-skills `skills/manage-planning-repos/scripts/detect_repo_type.sh`] evidence lines reused for legacy detection
- [Source: forge-skills `skills/manage-planning-repos/scripts/gather_hub_context.sh`] symlink resolution helper pattern (BSD, no `readlink -f`)
- [Source: `_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md`] universal script contract
- [Source: `_bmad-output/implementation-artifacts/spec-wp8-manage-planning-repos.md`] boundaries this WP inherits

## Eval scenarios (append to tests/README.md)

20. **Registry build on a mixed root.** Seed: marked hub, legacy hub,
    worktree, bare `_bmad/`. Expected: two hubs, two exclusions with
    reasons, legacy flagged `marker:false`.
21. **Ignore and pinned survive.** Seed: registry with both. Expected:
    preserved byte-for-byte across `build`.
22. **Verify fan-out is read-only.** Seed: three hubs. Expected: three
    parallel sessions, `dontAsk`, no edit permission, one summary, one
    `error` row when a session fails.
23. **`--apply` gate.** Seed: `hubs.sh run --apply` without `--yes`.
    Expected: hub list printed, waits for `yes`; nothing launched on any
    other answer.
24. **Marker stamped on repair.** Seed: hub without marker. Expected: Step 3
    adds exactly one line; Verify's GAP turns `ok`.

## Verification

**Commands:**
- `bash -n` all new shell; `python3 -m py_compile scripts/registry.py`
- `make test-verify-hub` (chained: verify_hub, mpr scripts, registry), `make test` exit 0, `make lint-docs` 0 issues
- Smoke on the owner's machine: `python3 skills/manage-planning-repos/scripts/registry.py build` then `hubs.sh list`; compare with the expected set in Dev Notes; `hubs.sh verify --jobs 2` on two hubs completes with a summary

**Manual checks (if no CLI):**
- `git diff main --stat`: only `skills/manage-planning-repos/**` and the root `README.md` row.

## Spec Change Log

- 2026-09-27: created from the owner's decision in session (registry built by the skill, never from dotfiles; marker approved; PRs #13 and #14 merged as prerequisites).

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

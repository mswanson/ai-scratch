---
title: 'WP9: manage-planning-repos hub registry + multi-hub fan-out'
type: 'feature'
created: '2026-09-27'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
baseline_commit: '635c53f' # forge-skills origin/main = merge of PR #16 (2026-09-28); was c46e2d6 (PR #13) at authoring
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
(a checkout whose resolved `git rev-parse --git-dir` differs from its
`--git-common-dir`, i.e. lives under `<common>/worktrees/`; a `.git` FILE alone
is not proof — submodule and `--separate-git-dir` main checkouts count as
checkouts) is
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
output lines. The scan roots are always asked, never assumed: on the first
build (no registry yet) the skill asks where to look in ONE
`AskUserQuestion` round, offering `~/Code` as the default answer; on
rebuilds it shows the recorded `roots` and asks whether to keep them.
`registry.py` itself takes `--root` and has no built-in default beyond
the recorded roots, so the script cannot scan anywhere the user did not
name.

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
| standalone BMAD | `_bmad/` present and either the `standalone` marker or (no marker, no spoke table, `docs/project-context.md` present) | `kind:"standalone-bmad"`, listed under `others`, not fanned out unless `--include-standalone` | N/A |
| experiment dir | `_bmad/` present, no marker, no table, no `docs/project-context.md` | not registered; appears in `excluded` with reason `no hub evidence` | N/A |
| worktree | resolved git-dir differs from common-dir (gitfile alone is not proof) | never a hub; `excluded` with reason `worktree of <path>` | N/A |
| spoke derivation | hub table row `| name | path | ... |` | `spokes[]` entry `{name, path, resolves:true/false, project_context:true/false}`; path taken from the table, resolved relative to the hub when relative | unresolvable path → `resolves:false`, still listed |
| shared spoke | same real path in two hubs' tables | listed under both hubs; `spokes_index` maps path → hubs | N/A |
| ignore list | existing registry has `ignore:["/path/x"]` | `/path/x` never registered even if it has a marker; list carried over untouched | N/A |
| pinned entry | existing registry has `pinned:[{name,path}]` | included as a hub even without evidence, flagged `pinned:true`; carried over untouched | pinned path missing on disk → `present:false`, kept |
| roots, first build | no registry yet | skill asks where to look (one question, `~/Code` offered as the default); `--root` repeatable; each root scanned to `--max-depth` (default 4); roots recorded in the file | root missing → exit 1 naming it; no `--root` and no recorded roots → exit 64 with usage, never a silent default |
| roots, rebuild | registry has `roots` | skill shows them and asks keep/change before running; `build` with no `--root` reuses the recorded roots | N/A |
| rebuild | registry exists | full rewrite of `hubs`, `others`, `excluded`; `ignore`, `pinned`, `roots` preserved; `generated_at` updated | unreadable/malformed existing file → exit 1 untouched |
| `hubs.sh list` | registry present | one row per hub: name, path, branch, dirty flag, BMAD version from `_bmad/_config/manifest.yaml`, bmad-loop pin if any; JSON with `--json` | registry absent → exit 3 `run registry build first` |
| `hubs.sh verify` | N hubs, `claude` on PATH | N parallel `claude -p` runs (`--jobs`, default 4), each told to run manage-planning-repos Verify and print the report; summary: per hub FAIL/GAP/drift counts + exit; overall exit 1 if any FAIL or error | `claude` absent → exit 3; per-hub timeout (`--timeout`, default 600s) → `error` row |
| `hubs.sh run "<prompt>"` | prompt, no `--apply` | same fan-out with the prompt, `dontAsk` + read-only allowlist | prompt that needs edits fails inside the session and lands as `error`/text, never edits |
| `hubs.sh run --apply` | prompt + `--apply` | `acceptEdits`; prints the hub list and asks once for `yes` before launching unless `--yes` | N/A |
| stamp on repair | Setup step 3 on a repo whose `CLAUDE.md` lacks the marker | marker line prepended (hub, spoke, or standalone per confirmed type; a plain BMAD repo instantiated from the hub template is re-stamped `standalone` with `--replace`), nothing else changed; reported in the Setup commit list | N/A |

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
  Subcommands: `build [--root ... --max-depth N --out F]` (no `--root`
  reuses recorded roots; none recorded → exit 64), `show [--json]`.
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
  `## 4. Registry and fan-out` section (the roots question first, then
  build, list, verify, run, `--apply` rule, what the registry is not); Step 3 cites `stamp_marker.sh`; Verify
  prose names the marker GAP; References list updated.
- `skills/manage-planning-repos/tests/test_registry.sh` -- new, chained
  from `test_mpr_scripts.sh`. `claude` PATH shim records argv and cwd and
  emits canned JSON; `git` real (temp repos and a real worktree fixture).
- `skills/manage-planning-repos/tests/README.md` -- runnable tests section
  + eval scenarios 20-24 (below). Root `README.md` skill-table row mentions
  the registry and fan-out.

## Tasks & Acceptance

**Execution:**
- [x] Marker line in both templates; `stamp_marker.sh` with idempotency and
  byte-preservation tests
- [x] `registry.py build`: scan, worktree exclusion, marker + legacy
  detection, spoke derivation via the shared row grammar, ignore/pinned
  preservation, `excluded` with reasons, JSON schema documented at the top
  of the file
- [x] `registry.py show [--json]`
- [x] `hubs.sh list|verify|run` per matrix, including the `--apply`
  confirmation and the summary format (one line per hub + totals; `--json`
  variant)
- [x] `verify_hub.sh` marker GAP line + `test_verify_hub.sh` scenarios
  (marker present ok; absent GAP; present on a spoke ok)
- [x] SKILL.md swaps at every Code Map site; menu text; References
- [x] `tests/test_registry.sh` chained from `test_mpr_scripts.sh`; README
  and eval scenarios

**Acceptance Criteria:**
- Given no registry and no `--root`, when `registry.py build` runs, then it
  exits 64 with usage and writes nothing; given a registry with recorded
  `roots`, `build` without `--root` scans exactly those.
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

### Review Findings

bmad-code-review 2026-09-28 (Blind Hunter + Edge Case Hunter + Acceptance Auditor; 52 raw, 30 after merge, 9 dismissed as noise). Owner rulings: decision 1 → third marker `standalone`; decision 2 → keep the code, spec amended; all 15 patches applied (commit `fix: standalone marker, spoke checkouts never hubs, review-round hardening`). PR 18 bots: `claude[bot]` (trigger clause, `# 5.` label, 19b numbering nit dismissed: the spec numbers it) and `chatgpt-codex-connector[bot]` (relative roots and section validation = duplicates of patches above; zombie grandchildren in the TERM tests); the three new items were owner-approved and fixed in the same commit.

- [x] [Review][Decision] How to mark plain BMAD repos — Step 3 stamps them `hub` (uses the hub template), so a stamped standalone repo registers as a hub and joins the default fan-out, contradicting the matrix's standalone row; unmarked, they carry a Verify GAP they can never close. Options: (a) third marker kind `standalone` (stamp_marker/registry/verify accept it; registry lists it under `others`); (b) leave them unmarked and suppress the GAP when the repo is neither hub nor spoke; (c) keep current behavior and amend the spec.
- [x] [Review][Decision] Worktree definition — the frozen text says `.git` is a file ⇒ never a hub; the code (Codex round 1) treats a gitfile as a worktree only when git-dir ≠ common-dir, so submodule and --separate-git-dir checkouts can be hubs. Amend the spec's parenthetical, or revert to the literal rule.
- [x] [Review][Patch] Spoke checkouts (path in a hub's spoke table) classified standalone or legacy hub instead of excluded as `spoke of <hub>` [scripts/registry.py:255-272]
- [x] [Review][Patch] Marker kind never checked against evidence: a hub stamped `spoke` passes Verify and vanishes from the registry; report drift in verify_hub.sh and warn in registry.py [tests/verify_hub.sh:157-160, scripts/registry.py:265]
- [x] [Review][Patch] One failing/timing-out/unparsable detect_repo_type.sh candidate aborts the whole build; exclude it with a reason instead [scripts/registry.py:229-242]
- [x] [Review][Patch] Rebuild without --max-depth resets the recorded depth to 4; reuse the recorded value, and say so in SKILL.md §4 [scripts/registry.py:457,507]
- [x] [Review][Patch] Writing replaces a symlinked registry with a 0600 regular file; write through the link target and keep the existing mode (0644 default) [scripts/registry.py:330-347]
- [x] [Review][Patch] `permission_denials` in the session JSON is ignored: verify → error row, run → attention with a denied count [scripts/hubs.sh:497-524]
- [x] [Review][Patch] Relative recorded `roots` are not rejected like ignore/pinned [scripts/registry.py:359-388]
- [x] [Review][Patch] Malformed `hubs`/`others`/`spokes` shapes crash text-mode show with a traceback; validate in load_registry → exit 1 [scripts/registry.py:305-327,480-483]
- [x] [Review][Patch] Relative XDG_CONFIG_HOME accepted; XDG says ignore it [scripts/registry.py:96-99]
- [x] [Review][Patch] CRLF: spoke-table cells keep a trailing \r without a closing pipe; stamp_marker writes an LF marker into a CRLF file [scripts/registry.py:129-143, scripts/stamp_marker.sh:70]
- [x] [Review][Patch] UTF-8 BOM hides the marker in all three readers and stamp_marker prepends ahead of it [scripts/registry.py:156, scripts/stamp_marker.sh:53-67, tests/verify_hub.sh:155]
- [x] [Review][Patch] hubs.sh: an empty `name` shifts tab-separated columns; an empty target set reports success (exit 0) [scripts/hubs.sh:328,385,439-471]
- [x] [Review][Patch] schema_version never checked; a newer file is rewritten as version 1 [scripts/registry.py:305-327]
- [x] [Review][Patch] Docs: non-apply `run` can only Read/Glob/Grep plus the exact verifier command; say so in usage and SKILL.md §4 [scripts/hubs.sh:6-31, SKILL.md §4]
- [x] [Review][Patch] `list` prints the machine-wide loop pin on every row; show `-` for a hub without .bmad-loop/ [scripts/hubs.sh:319-326]
- [x] [Review][Defer] Spoke-table header row not named `Symlink` is parsed as a spoke [scripts/registry.py:137] — deferred, pre-existing verify_hub.sh grammar; fix both parsers together
- [x] [Review][Defer] Duplicate hub basenames are indistinguishable in the text summary [scripts/hubs.sh:534] — deferred, cosmetic
- [x] [Review][Defer] Hand edits to the registry during a long build are overwritten (no lock, no mtime check) [scripts/registry.py:375,465] — deferred, rare
- [x] [Review][Defer] AC2 grammar cross-check uses its own fixture rather than the legacy hub's table; AC3 "byte-identical" is checked at JSON-value level [tests/test_registry.sh:206-222,296-350] — deferred, test strengthening

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

19b. **Roots are asked, not assumed.** Seed: first Registry run, no
    registry file. Expected: the skill asks where to look before scanning,
    offering `~/Code`; it never runs `build` with an unasked default. On a
    rebuild it shows the recorded roots and asks keep/change.
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

- 2026-09-28: code review complete; story status review → done (agent DoD). Human-in-the-loop gate is PR #18 (`do-not-merge` label) tracked in the session-state file.
- 2026-09-28 (owner decisions at code review): (1) a third marker kind `<!-- planning-repo: standalone -->` for plain BMAD repos; templates unchanged, Step 3 re-stamps with `stamp_marker.sh --replace`; standalone repos register under `others`. (2) Worktree rule amended: a `.git` file alone is not proof of a worktree; only a git-dir/common-dir mismatch is (submodule and `--separate-git-dir` main checkouts are checkouts). Both edits above are inside the frozen block by owner ruling.
- 2026-09-28: implementation on forge-skills branch `manage-planning-repos/hub-registry` (4 commits, baseline bumped to 635c53f). Deviations from Dev Notes' expected registry: star0 = no hub evidence, auth0-bmad-poc = standalone. Owner-machine smoke run 2026-09-28 (see Completion Notes).
- 2026-09-28: owner review: scan roots are asked on every Registry run (`~/Code` is the offered default, not an assumed one); `registry.py` gets no built-in default. Fan-out scope confirmed as manage-planning-repos Verify only.
- 2026-09-27: created from the owner's decision in session (registry built by the skill, never from dotfiles; marker approved; PRs #13 and #14 merged as prerequisites).

## Dev Agent Record

### Agent Model Used

Claude Fable 5.1 (orchestrating; implementation delegated to Claude Opus 5 subagents per task, tests written first)

### Debug Log References

### Completion Notes List

- Task 1 (marker + stamp_marker.sh): commit `feat: planning-repo marker in templates, stamp_marker.sh, Verify GAP` on `manage-planning-repos/hub-registry`. Marker is line 1 of both templates; stamp_marker.sh is atomic, idempotent, byte-preserving, refuses symlinks/bad kind/conflicting marker (exit 1 naming both). Tests test_mpr_scripts 74-84.
- Task 5 (Verify marker line): one `ok`/`gapl` line in the repository-guidance bucket, only when CLAUDE.md exists; GAP never counts as FAIL. Decision recorded: the line prints for any CLAUDE.md verify_hub.sh inspects (hub or spoke), not only BMAD repos. Tests test_verify_hub 17a-17f; healthy fixture now carries the marker.
- Tasks 2-3 (registry.py build/show): commit `feat: registry.py builds and shows the planning-repo registry`. Classification order ignored → worktree → hub marker → spoke marker → legacy (table or detect guess) → standalone-bmad → no hub evidence; ignore beats pinned; spoke-table parser ported from verify_hub.sh's awk with a cross-check test. Exit codes: 1 bad root/malformed registry, 2 args, 3 show without registry, 64 build without roots. 46 scenarios in tests/test_registry.sh (chained in task 7). Smoke `build --root ~/Code --out <scratch>` found 4 hubs / 2 others / 12 excluded; two rows differ from the Dev Notes expectation (star0 = no hub evidence, auth0-bmad-poc = standalone).
- Task 4 (hubs.sh): commit `feat: hubs.sh fans list, verify and a prompt out across registered hubs`. `claude -p` flags confirmed against `claude --help` (`--permission-mode dontAsk|acceptEdits`, `--output-format json`, `--allowedTools` variadic, placed last). Allowlist = the skill's two read-only scripts only; `Read` not added (open: whether a real `dontAsk` session needs it). Per-hub timeout via kill -0 polling; error rows on non-zero exit, timeout, or `is_error`. 33 shim scenarios (79 total in test_registry.sh). Not yet done: the real two-hub smoke run required by Verification; hub paths with spaces are not quoted in the verify prompt.
- Tasks 6-7 (SKILL.md, chain, README): commit `docs: manage-planning-repos menu item 4, registry and fan-out section, test chain`. Menu item 4; `## 4. Registry and fan-out` with the roots question first; Step 3 cites stamp_marker.sh; Verify prose names the marker GAP; References updated; test_registry.sh chained from test_mpr_scripts.sh (test_verify_hub.sh now reports 338 = 60 + 199 + 79); tests/README.md suite 4 + eval scenarios 19b, 20-24; eval scenario 1 now says a 4-item menu. Decision recorded: Step 3 stamps a plain BMAD repo (hub template) with the `hub` marker, so stamped standalone repos register as hubs; `standalone-bmad` then covers only unstamped legacy repos with project context. Owner may reverse this.
- Codex review round 1 (implement-story 2.3, branch diff vs main): 4 P2, 0 P0/P1, all fixed in commit `fix: hubs.sh path quoting, process-group kill, ~ expansion; gitfile is not a worktree` with a regression test each: (1) verify prompt interpolated the raw hub path (now `bash '<skill-root>'/tests/verify_hub.sh .`, hub path never in the prompt); (2) timeout used `pkill -P`, missing grandchildren (now per-run process group under `set -m` plus a recursive descendant walk, TERM then KILL); (3) pinned `~` paths were not expanded for execution (now expanduser in the JSON→TSV helper, registry spelling kept); (4) a gitfile checkout (submodule, --separate-git-dir) was classified as a worktree (now worktree only when `--git-dir` differs from `--git-common-dir`). Chain after fixes: 344 = 60 + 199 + 85.
- Codex review round 2: 1 P1, 1 P2, both fixed in commit `fix: isolate non-apply fan-out sessions; a verify without a report is an error`. P1: `--allowedTools` only adds grants, so a hub's own settings, hooks and MCP servers could still mutate under `dontAsk`; non-apply launches now add `--restricted --setting-sources "" --strict-mcp-config --tools Bash,Read,Glob,Grep --disallowedTools Edit Write MultiEdit NotebookEdit "Bash(git *)"` (confirmed against CLI 2.1.283 in a scratch dir: a SessionStart hook did not fire, a write attempt landed in permission_denials); `--apply` remains the only launch that loads hub settings. P2: a verify result without verify_hub.sh's summary line is now an `error` row (`exit=no-report`, `report:false` in JSON) and fails the overall exit. Chain: 351 = 60 + 199 + 92.
- Codex review round 3: 2 P1, both fixed in commit `fix: anchor fan-out Bash grants to the installed skill path; stop sessions on INT/TERM`. P1a: the read-only grants were `*/manage-planning-repos/...` wildcards (a same-named script inside a registered repo would be authorized); now generated from the resolved skill path, exact for verify_hub.sh and anchored-prefix for detect_repo_type.sh, quoted only when the path needs it, `*` in the path refused (exit 3). Proven against CLI 2.1.283: real script ran with no denials, decoy denied, old wildcard let the decoy run. P1b: INT/TERM never reached the per-run process groups; now every active run is TERM/KILLed and reaped, partial output kept, exit 130/143 (TERM covered by a test, INT by hand). Chain: 355 = 60 + 199 + 96.
- Live-smoke bug (not reachable by the shim tests): one hub's `--output-format json` result carried verify_hub.sh colour codes with the ESC byte dropped (`[33mGAP...`), so the per-line grep counted GAP=0 drift=0 and reported the hub `ok` while its summary line said 1 gaps, 5 drift. Fixed in commit `fix: hubs.sh takes verify counts from the summary line, tolerates ESC-less colour codes`: verify rows take counts from the summary line (already required by the report gate) after stripping both colour-code forms; run rows keep a tolerant per-line grep. Rerun smoke: ai-scratch GAP=1, lyceum-planning GAP=1 drift=5, exit 0. Chain: 359 = 60 + 199 + 100.
- Codex review round 4: 1 P2 (duplicate/aliased `pinned` entries produce duplicate fan-out targets, so `run --apply` could put two editing sessions in one checkout); fixed in commit `fix: one fan-out target per checkout; duplicate pinned aliases dropped from hubs`: registry.py keeps the first spelling per real path in the derived `hubs` (the user-owned `pinned` list is written verbatim, one stderr warning per dropped alias) and hubs.sh dedupes targets by real path before list/verify/run. Chain: 364 = 60 + 199 + 105. Full `make test` rc 0.
- Codex review round 5: 1 P1 (the anchored prefix grant `detect_repo_type.sh *` still matched a command with a redirection appended, so a non-apply run could write a file through Bash). Fixed in commit `fix: single exact read-only grant for fan-out sessions, no wildcard`: verify_hub.sh never calls detect_repo_type.sh, so that grant is dropped; the only grant is the exact `Bash(bash <skill>/tests/verify_hub.sh .)`. Proven against CLI 2.1.283: verifier runs with no denials; the detect script and the verifier with `> probe` appended are both denied. Smoke rerun with the single grant: both hubs report, counts match, exit 0.
- Codex review round 6: 1 P2 (a relative `pinned`/`ignore` path resolved against each command's cwd). Fixed in commit `fix: reject relative pinned and ignore paths instead of resolving them per cwd`: build refuses them as malformed (absolute or `~/` only, file untouched), hubs.sh refuses a still-relative hub path before launching. Chain: 369 = 60 + 199 + 110. Review closed after six rounds: 0 P0, 4 P1, 8 P2, 0 P3, all fixed with a regression test each; nothing deferred.
- bmad-code-review (implement-story 4.3) + PR 18 bot reviews (4.4): see `### Review Findings`. Implementer choices during the patches: a pinned or standalone-marked repo that a hub's table lists as a spoke is kept (with a warning) rather than demoted, because pinned and marker are the user's word; a missing `name` in a hand-edited registry falls back to the path basename. Final chain 404 = 67 + 206 + 131; full `make test` rc 0.
- Owner-machine smoke (Verification, roots asked: `~/Code`): `registry.py build --root ~/Code` wrote `~/.config/planning-repos/registry.json` with 4 hubs (ai-scratch 2 spokes, lyceum-planning 4, marshal-planning 0, product_planning 1; all `marker:no` until their next Setup stamps them), 2 others (auth0-bmad-poc, orderly-app), 9 excluded (star0-beta and orderly-app-prod as worktrees; 7 `no hub evidence` incl. star0). Differs from Dev Notes' expected 18 because the three product_planning-* worktrees no longer exist on disk. `hubs.sh list` printed branch/dirty/BMAD version/loop pin for all four. `hubs.sh verify --jobs 2` on a two-hub scratch registry (ai-scratch, lyceum-planning): both sessions returned real verify_hub.sh reports, `attention` rows (GAP=1 each, the new marker GAP; lyceum drift=5 pre-existing), no errors, 14.5s wall, exit 0.

### File List

- skills/manage-planning-repos/assets/hub-CLAUDE.md (modified)
- skills/manage-planning-repos/assets/spoke-CLAUDE.md (modified)
- skills/manage-planning-repos/scripts/stamp_marker.sh (new)
- skills/manage-planning-repos/scripts/registry.py (new)
- skills/manage-planning-repos/tests/verify_hub.sh (modified)
- skills/manage-planning-repos/tests/test_verify_hub.sh (modified)
- skills/manage-planning-repos/tests/test_mpr_scripts.sh (modified)
- skills/manage-planning-repos/tests/test_registry.sh (new)
- skills/manage-planning-repos/scripts/hubs.sh (new)
- skills/manage-planning-repos/SKILL.md (modified)
- skills/manage-planning-repos/tests/README.md (modified)
- README.md (modified, one table-row clause)

## Metrics

### Implementation

| Wall clock (min) | Active (min) | Steps | Tokens |
|---|---|---|---|
| 124 | 111 | 15 | not recorded (owner chose null) |

Phases 0-2 on 2026-09-28, 06:02Z to 08:06Z; six Codex review rounds inside phase 2.3.

### Code Review

| Cycles | Wall clock (min) | Active (min) | Findings | Fixes applied | Tokens |
|---|---|---|---|---|---|
| 1 | 345 | 345 | 27 | 18 | not recorded |

Cycle 1: bmad-code-review (three layers) plus PR 18 bot reviews; 2 decisions ruled, 15 + 3 patches applied, 4 deferred, 9 dismissed. Report: `wp9-hub-registry-code-review-report.md`.

Merged: PR #18 (1de7beb) 2026-09-28

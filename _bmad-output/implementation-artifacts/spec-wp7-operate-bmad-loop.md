---
title: 'WP7: operate-bmad-loop setup/upgrade/revert scripts'
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

**Problem:** operate-bmad-loop restates its most dangerous procedures as prose at multiple sites: the skill-fetch/materialize/stage sequence 4x, the pin grep 4x, and the plugin-journal greps in both verify and troubleshooting; policy.toml is hand-edited on every Setup and Revert; nothing validates story frontmatter; the doctor misses the `plugin-untrusted` pattern its own troubleshooting documents.

**Approach:** Scripted Setup/Upgrade/Revert mechanics with prose collapsing to citations; `merge_policy.py` line-based and stdlib-only (tomlkit is not installed on this machine — plan note superseded, deviation recorded); `verify_setup.sh` keeps identical behavior with `check_pin.sh` extracted and the missing doctor grep added. Judgment (branch naming, release-notes breaking-change reads, menu flow, run monitoring) stays prose. One PR on branch `scripts/operate-bmad-loop`.

## Boundaries & Constraints

**Always:** bash 3.2 + BSD; Python stdlib-only; universal contract; `verify_setup.sh`'s existing checks behave identically (its test suite `test_verify_setup.sh` passes unmodified except scenarios covering the new doctor grep); `merge_policy.py` touches ONLY the enumerated policy keys and structurally cannot modify `[mux]`/`[tui]` tables; `target_branch` and the pinned sha are always parameters, never decided by scripts; revert keeps its existing pre-invocation user confirmation in prose; `recover_stranded_story.sh` requires `--confirm` and prints (never writes) the sprint-status edit; new tests chain from `test_verify_setup.sh` (zero Makefile churn).

**Ask First:** changing any pinned value or default; touching `_bmad/` module trees.

**Never:** auto-launch or resume loop runs from scripts; `git reset --hard` anywhere; scripts deciding whether a tag upgrade is safe (freshness script reports; the LLM reads release notes).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| module gate | project root | JSON {module_present, config_yaml_present, skills_found[]} | N/A |
| freshness | pin + gh available (or curl fallback) | JSON {current_pin, latest_tag, compare_status, method} | both transports fail → exit 1 stderr |
| sync skills | root + sha + cli trees | per-skill/per-tree report: fetched/replaced-symlink/staged (check-ignore probe → add -f); `.git/info/exclude` edge preserved | fetch failure → exit 1, nothing half-staged |
| policy apply | policy.toml + overrides + --target-branch | enumerated keys set, comments + [mux]/[tui] byte-identical; report | key missing from file → appended in right table; malformed file → exit 1 untouched |
| policy revert | policy.toml | same keys reset to defaults; everything else byte-identical | idempotent |
| frontmatter check | story files | per-story pass/fail + bad field (6 fields, baseline_commit staleness via one git call) | N/A |
| assets install | root + skill root | idempotent plugin+heartbeat copy, gitignore appends (no dupes); branch creation sharing target_branch value | exists-and-identical → skipped |
| upgrade / revert wrappers | root (+ sha for upgrade) | compose the above; upgrade untracks pre-0.9.0 policy.toml once; revert removes plugin dir + heartbeat, policy revert, runs verify | any step fails → stop, report step |
| stranded recovery | root + story-key + unit-branch + --confirm | steps: stop hint, clean check, save-branch, ff-only merge; prints sprint-status edit | without --confirm → plan printed, exit 0, nothing done |

</frozen-after-approval>

## Code Map

- `skills/operate-bmad-loop/SKILL.md` -- Setup steps 0-8 (:79-134), Status (:136-188 untouched judgment), Upgrade (:190-207), Revert (:210-221); prose collapses to script citations
- `references/pins.md` -- :14-18 pin check + :20-35 freshness → cite scripts; sha stays a parameter
- `references/troubleshooting.md` -- #2 (:58-73) cites sync script; #5 (:91-98) cites check_pin; #8 (:111-120) points at doctor; #12 curl fallback lives IN check_freshness now; :15-24 recovery → recover_stranded_story.sh
- `tests/verify_setup.sh` -- extract `check_pin.sh` (sourced back); doctor block gains `plugin-untrusted` grep; all else identical
- `assets/policy-overrides.toml` -- the enumerated key source merge_policy reads
- `scripts/` -- new: `check_module_installed.sh`, `check_freshness.sh`, `check_pin.sh`, `sync_bmm_skills.sh`, `merge_policy.py`, `check_story_frontmatter.py`, `install_assets.sh`, `upgrade.sh`, `revert.sh`, `recover_stranded_story.sh`
- `tests/test_ol_scripts.sh` -- new, chained from `test_verify_setup.sh`; gh shims per `implement-story/tests/test_fetch_script.sh` pattern

## Tasks & Acceptance

**Execution:**
- [x] `scripts/check_pin.sh` extracted from verify_setup.sh (sourced; verify behavior identical) + `check_module_installed.sh` + `check_freshness.sh` (gh api with curl fallback built in)
- [x] `scripts/sync_bmm_skills.sh <root> <sha> [--cli-trees ...]` -- fetch 4 skill dirs at sha, replace symlinks with real dirs, check-ignore probe → git add -f/add, confirm via ls-files; per-skill/per-tree report; `.git/info/exclude` edge case preserved
- [x] `scripts/merge_policy.py --project <path> [--target-branch <name>] --mode apply|revert` -- line-based, stdlib-only; enumerated keys from policy-overrides.toml; [mux]/[tui] and comments byte-identical (test asserts byte equality outside touched lines)
- [x] `scripts/check_story_frontmatter.py <story>...` + `scripts/install_assets.sh` (idempotent copies, gitignore dedupe, branch creation from the SAME target_branch value merge_policy wrote)
- [x] `scripts/upgrade.sh` / `scripts/revert.sh` wrappers + `scripts/recover_stranded_story.sh --confirm`
- [x] verify_setup.sh doctor gains `plugin-untrusted`; prose swaps at every Code Map site (4x restatements collapse to citations)
- [x] `tests/test_ol_scripts.sh` chained from test_verify_setup.sh -- every matrix row, policy byte-equality, idempotency double-runs, shimmed gh/curl for freshness + sync

**Acceptance Criteria:**
- Given the refactored verify_setup.sh, when test_verify_setup.sh runs, then all pre-existing scenarios pass, plus a new plugin-untrusted scenario.
- Given a policy.toml with comments and [mux]/[tui] content, when apply-then-revert runs, then the file is byte-identical to the original.
- Given prose post-swap, then the skill-fetch sequence and pin check each appear ONCE (in their script) with all other sites citing them.
- Given `make test`, all green with zero Makefile/CI changes.

## Spec Change Log

## Design Notes

tomlkit unavailable → line-based merge_policy.py (targeted keys, byte-preservation tested); deviation from plan noted for the PR. Recovery script gated on --confirm per the audit's medium-high risk flag ("recover BY HAND" intent preserved as an explicit human pause).

## Verification

**Commands:**
- `bash -n` + `py_compile`; `make test-verify-setup` (legacy + chained, 0 failed); `make test` exit 0; `make lint-docs` 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat`: only `skills/operate-bmad-loop/**`.

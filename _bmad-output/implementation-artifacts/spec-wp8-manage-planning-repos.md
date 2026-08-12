---
title: 'WP8: manage-planning-repos repair + wiring scripts'
type: 'feature'
created: '2026-08-11'
status: 'done'
review_loop_iteration: 0
baseline_commit: '26b518a' # = e3c757e + Swany's setup-owned provisioning rewrite (folded per decision)
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
---

<frozen-after-approval reason="human-owned intent — pre-approved by user instruction 2026-08-11 (run WP4-WP8 continuously); base includes Swany's provisioning rewrite">

## Intent

**Problem:** verify_hub.sh detects drift (dangling symlinks, symlinked `bmad-*` skills, custom-skill mirror drift, missing qmd collections) but every repair is freehand prose; the qmd archive-in-collection check is promised by prose and implemented nowhere; structure bootstrap hand-parses TOML; the `{{placeholder}}` grep is restated 3x; the status board hand-tabulates sprint data. Swany's setup-owned provisioning rewrite (first commit on this branch) makes Setup EXECUTE — the scripts must serve that flow.

**Approach:** Seven scripts building the repair half onto verify_hub.sh's detection half, plus the board data path reusing implement-story's compute-board-state.py via a sibling-path reference with graceful fallback (Open Decision 1 resolved: same library, all trees carry the family). Menu flow, user confirmations, template content, and merge negotiations stay prose. One PR on branch `scripts/manage-planning-repos`.

## Boundaries & Constraints

**Always:** bash 3.2 + BSD; universal contract (terminate; failures non-zero + stderr, never success output; stdout machine-readable; unset CDPATH; arg validation); repair scripts EXECUTE decisions the user already made via the menu — the materialize-vs-remove choice for dangling symlinks stays a user prompt, the script runs the chosen verb; relative-symlink computation has its own helper (BSD ln has no -sr); verify_hub.sh behavior identical except additions explicitly listed; tests chain from test_verify_hub.sh (zero Makefile/CI churn); build ON TOP of the folded provisioning rewrite — no reverting its text.

**Ask First:** any change to hub/spoke CLAUDE.md template CONTENT; anything touching `_bmad/` module trees.

**Never:** scripts choosing which skills to materialize/remove; auto-merging CLAUDE.md sections (diff output feeds the user negotiation); running `codegraph init` or the BMAD installer from these scripts (the provisioning rewrite governs WHO runs installs — its `npx bmad-method install` flow stays prose-driven per its own text); deleting anything not explicitly passed.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| repair materialize | dangling/symlinked skill path | link removed, target content copied in, `git add` run; before/after JSON | target unresolvable → exit 1, nothing removed |
| repair relink | skill name + claude-dir + agents-dir | `.claude` side becomes relative symlink to `.agents` real dir; both staged | either side missing → exit 1 untouched |
| repair remove-dangling | dangling symlink path | link removed + staged; refuses non-dangling links | resolves-fine link → exit 2 naming target |
| qmd wiring | project root | `<repo>-{docs,memory,output}` computed, missing collections added, `qmd update` run, embed backgrounded; `_archive/` inside any collection root detected + reported (closes the spec gap) | qmd absent → exit 3 "qmd not installed" |
| bootstrap | project root | memory/handoffs + MEMORY.md template if absent; artifact dirs from `_bmad/config.toml` keys mkdir'd; created/skipped JSON | missing keys skipped gracefully; malformed TOML → exit 1 |
| placeholders | file | `{{...}}` occurrences with line numbers; clean → empty array | missing file → exit 1 |
| hub context | project root | JSON: top-level symlinks + resolved targets + broken flags, `_bmad/custom/*.toml` list | N/A |
| section diff | repo CLAUDE.md + template | missing/extra `## ` headers as JSON | N/A |
| repo type | project root | guess (hub/spoke/standalone-bmad/plain) + evidence lines; NEVER auto-acts | N/A |
| board data | hub root | sibling implement-story compute-board-state.py invoked when present; absent → exit 3 with fallback message | N/A |
| board url | config.yaml + url | idempotent `board.url` key write/create, formatting preserved | malformed yaml → exit 1 untouched |

</frozen-after-approval>

## Code Map

- `skills/manage-planning-repos/SKILL.md` -- post-rewrite text (commit 26b518a) is the base; swap sites: Step 1 consumes Verify prerequisites (doc fix), Step 2 structure (bootstrap script), Step 3 gather/placeholder/diff scripts, Step 4 repair verbs, Step 5 qmd wiring + archive-drift, Step 6 board data + url scripts
- `skills/manage-planning-repos/tests/verify_hub.sh` -- detection stays; additions only if a patch names them
- `skills/manage-planning-repos/assets/` -- templates referenced, not modified
- `scripts/` -- new: `repair_skill_layout.sh` (subcommands), `wire_qmd_collections.sh`, `bootstrap_structure.sh`, `check_placeholders.sh`, `gather_hub_context.sh`, `diff_claude_sections.sh`, `detect_repo_type.sh`, `run_board_state.sh` (sibling delegation), `set_board_url.sh`
- `tests/test_mpr_scripts.sh` -- new, chained from test_verify_hub.sh

## Tasks & Acceptance

**Execution:**
- [x] `scripts/repair_skill_layout.sh materialize|relink|remove-dangling ...` -- per matrix; own relative-path helper; all three CLI trees supported (`.claude/skills`, `.agents/skills`, `.agent`)
- [x] `scripts/wire_qmd_collections.sh <root>` -- per matrix incl. the promised-but-never-implemented archive-in-collection walk
- [x] `scripts/bootstrap_structure.sh <root>` + `scripts/check_placeholders.sh <file>` + `scripts/gather_hub_context.sh <root>` + `scripts/diff_claude_sections.sh <a> <b>` + `scripts/detect_repo_type.sh <root>`
- [x] `scripts/run_board_state.sh <hub-root>` -- resolves `{skill-root}/../implement-story/scripts/compute-board-state.py`; missing → exit 3 + "implement-story not installed; tabulate manually"; `scripts/set_board_url.sh <config> <url>`
- [x] SKILL.md swaps at every Code Map site, preserving the provisioning rewrite verbatim and all menu/confirmation prose; the three placeholder-grep restatements collapse to one script citation
- [x] `tests/test_mpr_scripts.sh` chained from test_verify_hub.sh -- every matrix row incl. three-tree repair fixtures, archive-drift detection, sibling-absent fallback

**Acceptance Criteria:**
- Given a fixture with a symlinked `bmad-*` skill and a dangling custom link across all three trees, when the repair verbs run, then verify_hub.sh's corresponding detections go green and the index contains the staged fixes.
- Given a collection root containing `_archive/`, when wire_qmd_collections.sh runs, then the drift is reported (the SKILL.md promise finally has an implementation).
- Given SKILL.md post-swap, then Swany's provisioning text is byte-intact and every mechanical step cites its script.
- Given `make test`, all suites green with zero Makefile/CI changes.

## Spec Change Log

- **2026-08-11, review round.** Both hunters ran while the hub was accidentally trashed (bmad review skills briefly unregistered; they executed the methods directly). Critical: set_board_url could destroy an unreadable config at rc 0 — preflight + checked reads patched. High: nested-url mis-target, comment-terminated block duplicate-insert, relink over-staging (`git add -A`), remove-dangling deleting live file-symlinks, materialize depth-change corruption. The swap had also reworded two lead-in lines of Swany's provisioning commit — restored verbatim with the Verify-bucket pointer as added sentences. H1 recorded: the board delegation targets WP3's script (PR #3); exit-3 fallback governs until it merges.

## Design Notes

Open Decision 1 resolved as sibling-path delegation with graceful fallback: both skills ship in the same library; every tree this user installs carries the family; `run_board_state.sh` guards existence and exit-3s with prose fallback when absent. The provisioning rewrite (26b518a) governs installer execution; these scripts deliberately exclude it.

## Verification

**Commands:**
- `bash -n` all; `make test-verify-hub` (17 legacy + chained, 0 failed); `make test` exit 0; `make lint-docs` 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat`: only `skills/manage-planning-repos/**`.

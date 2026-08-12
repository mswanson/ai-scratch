# forge-skills Script Conversion Plan

Date: 2026-08-10 · Owner: Swany · Status: approved for execution
Executor: bmad-agent-dev (Amelia), one work package at a time, one PR per package.

Replace mechanical prose instructions in forge-skills skills with checked-in scripts the skill tells the LLM to run. Eight work packages, one per skill. Every package ships ALL its listed changes regardless of payoff tier. Source: 2026-08-10 audit (8 parallel per-skill audits; findings consolidated here as the durable record).

## Execution contract (every package)

- **Re-audit gate (step 0, mandatory).** Change lists below reflect 2026-08-10 state; outstanding edits exist (at audit time: uncommitted changes to `skills/manage-planning-repos/SKILL.md`; more may land before a package starts). Before implementing: re-read the skill's SKILL.md + references/ at current HEAD, confirm each change still applies, fix line references, add newly exposed candidates, drop obsolete ones. Record the delta in the PR description.
- Repo: `/Users/michaelswanson/Code/forge-skills` (spoke; always the real path, never the hub symlink). Branch `scripts/<skill-name>` off main. Commit only package-scoped paths; leave unrelated dirty files (e.g. the manage-planning-repos edit) untouched.
- Scripts live in `<skill>/scripts/` (output-gating checkers may stay in `tests/` per existing convention). Stdlib-only unless noted. Emit machine-readable output (JSON preferred) for the LLM to interpret; non-zero exit with a reason on failure.
- Scripts compute facts or execute already-made decisions. Never judgment. Judgment, conversation gates, and synthesis stay prose.
- Prose swap pattern: replace how-to text with "run X, act on its output"; delete the replaced how-to; keep judgment guidance. Where the same logic is restated at multiple sites, all sites cite the one script.
- Single source of truth: where a writer and checker share format assumptions (YAML indentation in implement-story), extract a shared module both import.
- Tests: every new/changed script gets a hermetic suite under `<skill>/tests/`, registered as a Makefile target AND in `.github/workflows/tests.yml` (the Makefile header requires the two stay in sync). `make test` and `make lint-docs` pass before PR.
- PR body: finding→change table, re-audit delta, test evidence.
- Merged PR is the release; skills are live from this library.

## WP1 write-handoff

Existing `tests/check_handoff.sh` self-check is correctly wired; keep it.

1. `scripts/scaffold_handoff.sh <dest-dir> <topic-slug> <repo>... [--story S] [--epic E]` — computes today's date (`date +%F`), builds `YYYY-MM-DD-<slug>.md`, `mkdir -p`, writes frontmatter (`date/topic/repos/status: open`, optional story/epic) plus the six required section headers in order; prints the created path. LLM fills prose only. (Folds date stamping and dir creation.)
2. `scripts/gather_repo_state.sh <repo-path>...` — per repo: branch, worktree path, dirty files, last commit (`%h %s`); JSON or key:value. Graceful on detached HEAD / no commits.
3. `scripts/resolve_handoff_dest.sh [start-dir]` — hub detection (`_bmad/` + spoke symlinks); prints `hub_path` + `resolved|unresolved`; never guesses. Unresolved → prose falls back to asking.
4. `scripts/ensure_handoffs_link.sh <MEMORY.md>` — idempotent check-then-append of the `[Handoffs](handoffs/)` line; reports added|present. Optionally bundle the conditional `qmd update` into the same post-write housekeeping call.
5. SKILL.md prose swaps for all of the above.

Tests: hermetic suites per script; new Makefile + CI targets.

## WP2 redline-file

Core logic already exists in `scripts/review.py` (tested by `tests/test_review_server.py`); this package exposes it.

1. Convert review.py's manual argv loop to argparse with real `--help`; shrink SKILL.md flag documentation to point at `--help` (drift-vector removal).
2. Post-session CLI subcommands reusing existing tested functions: `list <file> --json` (threaded comments: id, type, anchor, author, at, tagged/seed flag, replies), `strip <file> --ids c1,c3 [--verify]` (reuses `_handle_comment_delete` algorithm), `reply <file> --id cN --text ...` (reuses insertion/numbering + `sanitize_comment_text`).
3. `scripts/start_remote_review.sh <file>...` — launch server(s), capture port+token, resolve tailnet DNS, `tailscale serve --bg`, print assembled URLs; graceful when tailscale/jq missing.
4. `scripts/detect_lint.sh <file>` — find markdown lint setup up-tree, print the fixer command or nothing.
5. Prose gaps to close during the swap: document (or make moot via subcommands) the code-fence-lifting behavior and the no-blank-lines rule for reply text.

Tests: extend test_review_server.py to cover the CLI modes.

## WP3 implement-story

Existing scripts (`detect-ai-reviewers.sh`, `fetch-ai-review-comments.sh`, `tests/check_story_state.py`) are correctly wired; this package makes the checker produce, not just validate, and scripts the remaining bookkeeping.

1. `--emit` mode on `check_story_state.py` (or `scripts/compute-story-metrics.py` sharing one module): outputs the computed `metrics` YAML block from `completed_steps`; by construction the numbers pass the checker. Extract shared parse/format module.
2. `scripts/session-state.py <state-file> start-step <id> <name> | complete-step <id> | set <key.path> <value>` — auto UTC ISO 8601 timestamps, exact indentation the checker expects; covers the scattered single-field sets (`hil_review`, `ai_reviewers_triggered`, `mode`, `baseline_test_failures.*`). Fold one-off date-math (staleness >30d, branch timestamps, merged-stamp) into this helper.
3. `scripts/inspect-story.py <story-file> [--ticket-prefix P]` — JSON: ticket id/link, ⚠️ OPEN flags, repos in scope, task checkbox totals + unchecked list, dev-notes presence. Zero-match results warn "verify manually". Used at gates 0.1, 0.2, 2.3.
4. `scripts/compute-board-state.py <sprint-status.yaml> <deferred-work.md>` — the board-sync.md "mechanical state": updated stamp, merged count, progress, tiles, pills, epic fractions, gate-chain, OPEN deferred items. LLM writes only the curated prose. (Also serves WP8; see Open decisions.)
5. `scripts/detect-command.sh <repo> <test|lint|typecheck>` — package.json scripts + Makefile targets deterministically; CLAUDE.md surfaced as candidates only, final pick stays LLM. Replaces the 3x-restated fallback chain.
6. `scripts/check-environment.sh <repo>...` — symlink resolution + smoke path, clean-tree per repo, default-branch detection folded in; JSON per repo.
7. `scripts/ensure-pr-labels.sh <repo> <label:color>...` — idempotent gh label ensure; permission-denied surfaces as a distinct status (halt path preserved).
8. Prose swaps across SKILL.md and the phase files at every replaced site.

Tests: extend existing suites; new targets for new scripts.

## WP4 consolidate-memory

Existing `tests/check_consolidation.sh` self-check correctly wired; keep it.

1. `scripts/checkpoint.sh <project-root> [scope-path]` — dirty tree → abort with report (policy: never auto-stash/auto-commit user WIP; see Open decisions); clean → branch `memory-consolidation-$(date +%F)` or timestamped backup for non-git; JSON with `checkpoint_verified`.
2. `scripts/build-inventory-plan.sh <project-root> [scope-path]` — one walk emitting a JSON manifest bucketed into slices (per-subfolder, handoffs, stragglers incl. CLAUDE.md levels/.claude/notes/adr, BMAD artifacts when `_bmad/` present, known external paths); size+mtime per file; fail loud on unrecognized patterns. LLM keeps slice-merge judgment.
3. `scripts/stat-and-frontmatter.sh <files>...` — TSV/JSON inventory rows (path, size, mtime; frontmatter `date`/`status` for handoffs, reusing the checker's extraction). Scouts run it per slice; they supply only purpose/type.
4. `scripts/archive-handoffs.sh <handoff-path>...` — `mkdir -p` repo-root `_archive/handoffs/`, `git mv` (or `mv`), legacy `memory/handoffs/_archive/` relocation; emits move manifest. LLM decides which handoffs qualify.
5. Prose fix: Phase 5 step 3 becomes the literal command `date +%F > memory/.last-consolidated`.
6. `scripts/sync-harness-mirror.sh <repo-memory-dir> <mirror-dir>` — one-way repo→mirror with add/overwrite/remove report; mirror path always an explicit argument, never inferred.
7. `scripts/git-date-hint.sh <file> [pattern]` — `git log -S`/blame date resolution for absolutizing relative dates; consistent method, judgment stays for ambiguous matches.
8. Phase 4 start cites the existing MEMORY.md cap one-liner (already in the checker) instead of leaving the count implicit.

Tests: hermetic suites per script.

## WP5 write-like-me

No scripts exist today; everything is net-new.

1. **Feasibility spike first:** can Slack be reached outside the MCP session (token, CLI)? If yes → `scripts/collect_slack_sample.py` (date-windowed search, cursor pagination, dedup, stop at ~300 or exhaustion; JSON out). If no → document infeasibility in SKILL.md and keep prose orchestration, tightened.
2. `scripts/compute_style_stats.py` — corpus statistics from collected messages: em-dash/exclamation/ellipsis rates, terminal-punctuation on short messages, sentence-length distribution, emoji frequency (with skin tones), capitalization pattern, abbreviation hits, short-vs-substantive ratio. Raw numbers; LLM does qualitative bucketing (profile notes heavy code-switching, so no hard global thresholds).
3. `scripts/lint_robotic_tells.py <draft> [--profile style-profile.json]` — lexical/punctuation tells only (em dashes if profile disallows, stock phrases, sentence-initial "however" anchored, formal verbs as flag-for-review); JSON hits + `clean`. Structure/tone tells stay LLM judgment. Output step gates on clean-or-explained.
4. `scripts/validate_profile.py` — required fields/enums per profile-schema.md (hardcoded, noted as needing sync), `generated_on` age + stale warning, snippet count in 5–10 range, snippets-verbatim-in-corpus substring check (with Slack-markup normalization; needs corpus arg).
5. SKILL.md prose swaps in Steps 1–3.

Tests: fixture corpora + fixture profiles.

## WP6 manage-todoist

MCP-bound skill: scripts pre-validate arguments and compute, never call the API. Flow: draft → validate → MCP call.

1. `scripts/validate_task.py < draft.json` — one validator for the checklist layer: priority is string `p1`–`p4` (coercion suggestion), P1 requires due date, duration format/bounds strict but mode-range advisory-only, label namespace scope by project (`feature:*` Auth0-only, `area:*` Habits/AREAS-only, `mode:*` required on P1–P3), Habits/AREAS need `Work`/`Personal` sectionId. Validates namespace scope rules only; never mirrors the volatile label inventory. Include `--suggest` mode-default lookup. Targets the failure modes evals 2/5/6/7 documented.
2. `scripts/pomodoro_sum.py` — sums mixed-format durations from find-tasks JSON, per-task breakdown, overcommit flag vs 150m. Which modes count toward focused work: see Open decisions.
3. `scripts/sync_bundle.sh <dest> [--from <src>]` — local bundle graduation/copy (`rsync -a --delete` semantics); cross-machine and claude.ai upload stay manual, stated in the doc.
4. Consciously skipped (audit recommended against standalone builds): batch-chunking helper (trivial), standalone mode-defaults table (folded into `--suggest`).
5. Prose swaps: the Common-mistakes checklist becomes "run validate_task before every write"; plan-today workflow pipes find-tasks output through pomodoro_sum.

Tests: hermetic suites; consider one eval-harness pass as acceptance evidence since this skill has evals/.

## WP7 operate-bmad-loop

`tests/verify_setup.sh` correctly wired for Verify; the package kills the 4x prose restatements and scripts Setup/Upgrade/Revert mechanics.

1. `scripts/sync_bmm_skills.sh <project-root> <sha> [--cli-trees ...]` — fetch the 4 skill dirs at the pinned sha, replace symlinks with real dirs, `git check-ignore` probe → `git add -f`/`git add`, confirm via `git ls-files`; per-skill/per-tree report. Preserves the `.git/info/exclude` edge case. Called from Setup 3, Upgrade 3, troubleshooting #2/#3.
2. `scripts/merge_policy.py --project <path> [--target-branch <name>] --mode apply|revert` — TOML-aware (tomlkit; the one non-stdlib exception, justified by comment preservation) merge/reset of exactly the enumerated keys; structurally cannot touch `[mux]`/`[tui]`. `target_branch` always a parameter.
3. `scripts/check_freshness.sh` — gh api tags + compare with the curl fallback built in; JSON `{current_pin, latest_tag, compare_status}`. Release-notes breaking-change judgment stays LLM.
4. Extract `check_pin.sh` from verify_setup.sh (sourced by it); SKILL.md:94, pins.md, troubleshooting #5 cite it instead of restating.
5. `scripts/check_module_installed.sh <project-root>` — JSON module/config/skills gate for Setup step 0.
6. `scripts/install_assets.sh <project-root> <skill-root>` — idempotent plugin + heartbeat copy, idempotent gitignore appends; folds Setup 6/7 mechanics and the step-8 branch creation so branch name and `target_branch` policy value cannot diverge.
7. `scripts/check_story_frontmatter.py <story>...` — per-story frontmatter validation against story-frontmatter.md (6 fields, baseline_commit staleness via one git call); doubles as the troubleshooting #9 diagnostic. Nothing validates this today.
8. `scripts/upgrade.sh` / `scripts/revert.sh` — wrappers reusing 1/2/6; upgrade adds the tracked-policy.toml untrack conditional; revert removes plugin dir + heartbeat, resets policy keys via merge_policy revert, ends by running verify_setup.sh. Revert keeps its existing pre-invocation user confirmation.
9. `scripts/recover_stranded_story.sh <root> <story-key> <unit-branch>` — troubleshooting recovery steps 1–4 with an explicit confirm before branch surgery; prints (never writes) the sprint-status.yaml edit.
10. verify_setup.sh doctor: add the missing `plugin-untrusted` grep; troubleshooting #8 points at doctor output.

Tests: extend test_verify_setup.sh; new suites for merge_policy (Python) and sync_bmm_skills.

## WP8 manage-planning-repos

`tests/verify_hub.sh` detects; this package builds the repair half. **Re-audit especially carefully: SKILL.md had uncommitted edits at audit time.**

1. `scripts/repair_skill_layout.sh materialize <symlink> | relink <skill> <claude-dir> <agents-dir> | remove-dangling <symlink>` — the repair counterparts to verify_hub.sh's drift detection (dangling symlinks, symlinked `bmad-*`, mirror drift) across all three CLI trees; own relative-path helper (macOS BSD ln, no `-sr`); before/after state printed. User still chooses materialize-vs-remove; script executes the choice.
2. `scripts/wire_qmd_collections.sh <project-root>` — compute `<repo>-{docs,memory,output}` names, parse `qmd collection list` (same grep style verify_hub.sh uses), add missing, `qmd update` + backgrounded embed; walk collection roots for nested `_archive/` and report. Closes the promised-but-unimplemented archive-drift check.
3. `scripts/bootstrap_structure.sh <project-root>` — memory/handoffs + MEMORY.md template if absent; parse `_bmad/config.toml` artifact-dir keys, substitute `{project-root}`, `mkdir -p` each; skip gracefully on missing keys; created/skipped report.
4. `scripts/check_placeholders.sh <file>` — the shared `{{...}}` gate; the three restatement sites collapse to citations.
5. `scripts/gather_hub_context.sh <project-root>` — top-level symlinks + readlink targets, `_bmad/custom/*.toml` list; JSON for template filling.
6. `scripts/diff_claude_sections.sh <repo-CLAUDE.md> <template>` — `## ` header diff, missing/extra lists; staleness judgment and merge negotiation stay user-facing.
7. `scripts/detect_repo_type.sh <project-root>` — hub/spoke/standalone guess + evidence lines; user confirms.
8. Status board: consume the WP3 board-state extractor (reference vs vendor: Open decisions) + `scripts/set_board_url.sh <config.yaml> <url>` idempotent key write.
9. Doc fix: Setup step 1 consumes Verify's prerequisites bucket instead of re-deriving NOGIT/BMAD/LOOP.

Tests: extend test_verify_hub.sh; new suites per script.

## Sequencing

WP1 → WP2 → WP3 → WP4 → WP5 → WP6 → WP7 → WP8.
Smallest first to set the pattern (WP1), expose-existing refactor next (WP2), highest-frequency payoff third (WP3). Only hard dependency: WP8 consumes WP3's board-state extractor decision. Everything else independent; reorder freely.

## Open decisions (resolve in the named package; ask Swany)

1. **Board-state extractor home (WP3 builds, WP8 consumes).** Installed skill dirs are copied independently, so cross-skill relative paths may not survive installation. WP8 decides: reference within the library checkout, or vendor a copy.
2. **Slack access outside MCP (WP5).** Determines whether collect_slack_sample.py is buildable.
3. **Focused-mode inclusion list (WP6).** Which `mode:*` labels count toward the 150m budget; SKILL.md names moving/adulting as fillers but gives no exhaustive inclusion list.
4. **Checkpoint dirty-tree policy (WP4).** Recommended: abort-and-report, never auto-stash user WIP. Confirm.

## Cross-cutting bugs found by the audit (fixed inside their packages)

- manage-planning-repos promises an archive-inside-collection check nothing implements (→ WP8.2).
- redline-file prose omits code-fence-lifting and the no-blank-lines reply rule review.py enforces (→ WP2.5).
- operate-bmad-loop doctor misses the `plugin-untrusted` journal pattern its own troubleshooting documents (→ WP7.10).

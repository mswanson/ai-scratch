# Deferred Work Ledger — agent-skills script-conversion (PRs #1–#8)

Findings raised in review during WP1–WP8 (forge512/agent-skills PRs #1–#8) that
were dispositioned DEFERRED rather than fixed, plus escalations that were never
given a final owner decision. Excludes: merge conflicts, the post-merge
README/Makefile sweep (root README Tests list + Layout bullet, recurring across
every WP branch), and the `style-profile.json` verbatim-content escalation
(tracked elsewhere).

## Cross-PR

- what: Pin /bin/bash (or assert version) across all Makefile test targets so the "macOS bash 3.2" claim is enforced rather than PATH-luck.
  where: `Makefile` (all test targets, repo-wide)
  why: Every existing suite invokes PATH-resolved `bash`; on machines/runners where Homebrew bash shadows /bin/bash, CI validates bash 5.x while the Makefile header claims 3.2. Pre-existing repo-wide convention, surfaced by WP1 review.
  source: PR #1 (source_spec: `_bmad-output/implementation-artifacts/spec-wp1-write-handoff.md`)

## PR #1 — write-handoff

No deferred items. All round-1/2/3 findings ended FIX, DECLINE, or the excluded
README sweep. **PR #1 never received a "Merge-time closeout" comment** — its
last comment is "Final round" (2026-08-19T04:17:39Z); this ledger treats that as
authoritative for the PR.

## PR #2 — redline-file

- what: Hard-link aliases to one inode pass the duplicate-path check, so two hard links to the same document can start two review sessions on it (duplicate `c1` ids, writes clobbering each other).
  where: `skills/redline-file/scripts/start_remote_review.sh:80`
  why: P2, low-probability (needs two hard links passed in one invocation); fix is comparing device/inode identity, not just canonicalized paths.
  source: PR #2

- what: A symlinked directory in the caller's path can hide the repo root from the upward lint-config walk, producing a missed lint hint.
  where: `skills/redline-file/scripts/detect_lint.sh:50`
  why: P2, low-probability; fix is resolving `DIR` physically (`pwd -P`) before walking upward.
  source: PR #2

- what: SKILL.md doesn't document that `list`/`strip`/`reply` only dispatch as subcommands when no cwd file of that exact name exists (serve is the fallback otherwise).
  where: `skills/redline-file/scripts/review.py:722` (SKILL.md doc gap)
  why: Declined as a defect (tested, deliberate tiebreak) but recorded as a doc follow-up — an optional one-liner.
  source: PR #2

- what: `reply --text` keeps CRLFs, so on a CRLF document each pasted line break can become `\r\r\n`.
  where: `skills/redline-file/scripts/review.py:167`
  why: P2, re-review of 42dd814; fix is normalizing `\r\n`/lone `\r` to `\n` before sanitizing.
  source: PR #2

- what: `strip --ids` accepts a non-`cN` identifier, so a typo matching a hand-written tag can delete seed markup.
  where: `skills/redline-file/scripts/review.py:778`
  why: P2, re-review of 42dd814; fix is rejecting `--ids` values that don't match the `cN`/`cN.M` shape.
  source: PR #2

## PR #3 — implement-story

**PR #3 never received a "Merge-time closeout" comment** — its last comment is
"Final round" (2026-08-19T04:25:13Z), whose "Follow-ups recorded (not in this
PR)" paragraph is the closest equivalent and is the source for this section.
These were dispositioned DECLINE-with-recorded-follow-up rather than the
`DEFERRED` tag used elsewhere.

- what: Multi-target Make rules (`test lint:`) miss `detect-command.sh`'s command detection — a conservative halt-and-ask; needs a real target-list parse to support them.
  where: `skills/implement-story/scripts/detect-command.sh:128`
  why: P2; declined as new-capability-not-a-defect, recorded as a follow-up.
  source: PR #3

- what: `packageManager`/Yarn PnP runners aren't recognized as command-source candidates.
  where: `skills/implement-story/scripts/detect-command.sh:103`
  why: P2; new capability, not a defect fix.
  source: PR #3

- what: A comma-joined `--baseline-test-failures` CLI argument is lossy for a test id that itself contains a comma (storage round-trips fine; only the CLI input path doesn't).
  where: `skills/implement-story/scripts/session-state.py:235`
  why: P2; every lossless remedy changes the frozen `set` argument contract.
  source: PR #3

- what: `deferred-work.md` entries aren't bounded at intervening sub-headings, so a sub-heading inside a real entry could end it early.
  where: `skills/implement-story/scripts/compute-board-state.py:203`
  why: P2; needs its own scenarios rather than riding on the fence-mask fix.
  source: PR #3

- what: `_find_link()` returns the first URL on the ticket's line rather than properly associating URLs with tickets.
  where: `skills/implement-story/scripts/inspect-story.py:113`
  why: P2, pre-existing (function untouched, only its line number moved); link is advisory context, not acted on.
  source: PR #3

- what: A `baseline_test_failures.<repo>` sub-key containing `: ` or `#` would write a malformed YAML mapping key.
  where: `skills/implement-story/scripts/story_state_lib.py:582`
  why: P2; the sub-key is a repo directory name from `repos_in_scope`, and quoting it would also require changing the matching lookup.
  source: PR #3

- what: No portable bash-3.2 timeout (or an enforced `timeout`/`gtimeout` dependency named on the `Dependencies:` line); the guard is currently conditional.
  where: `skills/implement-story/scripts/check-environment.sh:83`, `:87`
  why: A portable bash-3.2 timeout has its own failure modes; declined this round, recorded as a follow-up.
  source: PR #3

- what: SKILL.md's one-line verb summary omits `abort-step` and `add-cycle`; also missing the `story_state_lib.py` inventory line covering its shared use by `inspect-story.py`/`compute-board-state.py` via `fence_mask()`.
  where: `skills/implement-story/SKILL.md:114`
  why: Doc-inventory inaccuracy, not a defect; queued with the other SKILL.md corrections.
  source: PR #3

## PR #4 — write-like-me

- what: Slack placeholders (`@user`, `#channel`) are counted as prose words, inflating sentence-length/word-count stats on mention-heavy corpora.
  where: `skills/write-like-me/scripts/compute_style_stats.py:121`
  why: P2, reproduced; profile-accuracy skew, not a merge blocker.
  source: PR #4

- what: A trailing ellipsis is missed when it sits behind a closing quote or emoji code (e.g. `"Maybe... :shrug:"`), understating `trailing_ellipsis_rate`.
  where: `skills/write-like-me/scripts/compute_style_stats.py:240`
  why: P2, reproduced; understates one habit rate.
  source: PR #4

- what: The backward sentence-start scan stops at a closing delimiter, so `"(This works!) However, wait."` misses the sentence-initial transition.
  where: `skills/write-like-me/scripts/lint_robotic_tells.py:144`
  why: P2, reproduced; low-frequency draft shape, missed hit is review-severity only.
  source: PR #4

- what: `message_shape` profile value was flattened to fit the schema enum (`"one block" | "many short lines"`), discarding the prior nuanced value (short lines in DMs, longer blocks in updates); widen the enum or add a free-text nuance field.
  where: `skills/write-like-me/style-profile.json:25`
  why: Enum is pre-existing schema this PR only started enforcing; real signal loss but not a defect. Cross-referenced with the open style-profile.json content escalation (owner-gated).
  source: PR #4 (2026-08-22 wave)

- what: Emoji-only messages add zero-word "sentences" to the 1–5 bucket, skewing sentence-mean and `commas_per_sentence` on emoji-heavy corpora.
  where: `skills/write-like-me/scripts/compute_style_stats.py:250`
  why: P2; profile-accuracy skew only.
  source: PR #4 (2026-08-22 wave)

- what: Canonical Slack date markup (`<!date^...>`) survives normalization and is miscounted in style stats.
  where: `skills/write-like-me/scripts/_wlm_common.py:100`
  why: P2; rare token shape, slight skew. Belongs to the normalization-gap cluster with the placeholder-counting entry above.
  source: PR #4 (2026-08-22 wave)

- what: `short_msg_terminal_punct_rate` counts `?`/`!` together with periods, so a user who never ends with periods still scores high; split periods from other terminal punctuation.
  where: `skills/write-like-me/scripts/compute_style_stats.py:178`
  why: P2; metric-definition refinement, current aggregate is documented and directionally correct.
  source: PR #4 (2026-08-22 wave)

- what: Ordered-list markers (`1.`, `2.`) are treated as sentence terminators, inflating sentence counts on list-heavy messages.
  where: `skills/write-like-me/scripts/compute_style_stats.py:78`
  why: P2, reproducible; bounded to sentence-length aggregates.
  source: PR #4 (2026-08-22 wave)

- what: SKILL.md's corpus-gathering step can leave a persistent file of ~300 Slack messages (incl. private channels) in an ordinary project directory; direct it to a disposable private location with a cleanup step.
  where: `skills/write-like-me/SKILL.md:84`
  why: Process/privacy hardening, not a code defect. Cross-referenced with the style-profile.json content escalation.
  source: PR #4 (2026-08-22 wave)

## PR #5 — manage-todoist

PR #5 has two Merge-time closeout comments (2026-08-19 and 2026-08-22 — a
second review wave landed after the first close-out), plus a further
post-closeout re-review wave on 2026-08-22 (below).

Fixed post-ledger: the terminal-`..` dest bypass headlined below as the top
P1 (`sync_bundle.sh:150`) was fixed in commit `6de03b8` after this ledger was
first built; the entry has been removed from this list.

- what: `--mirror` prunes stale directories only when a stale *file* was also found; a destination-only empty directory should be pruned independently of that.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:371`
  why: P2; real but no data loss (an empty dir), moving directory reconciliation out from under the stale-file guard is a bigger change than the merge-time pass allowed.
  source: PR #5

- what: The `tests/`+`evals/` exclusion applies to the file inventory but not the directory inventory during `--mirror` cleanup.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:393`
  why: P2; only reaches an empty dest-only dir under `tests/`/`evals/`, and `rmdir` refuses anything non-empty, so nothing is lost today.
  source: PR #5

- what: A file/directory type conflict between source and dest aborts the whole `--mirror` run instead of being resolved before copying.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:324`
  why: P2; aborts loudly today rather than losing data; widening what `--mirror` deletes needs its own change and tests.
  source: PR #5

- what: A JSON integer past Python's 4,300-digit limit raises a bare `ValueError` that `except json.JSONDecodeError` doesn't catch, so both scripts traceback instead of printing a parse diagnostic.
  where: `skills/manage-todoist/scripts/validate_task.py:725` and `skills/manage-todoist/scripts/pomodoro_sum.py`
  why: P2; trigger needs a 4,300-digit number in a hand-built draft. Fix: widen both excepts to `ValueError`.
  source: PR #5

- what: The SKILL.md checklist no longer carries a reviewable line for habit `mode:*`/`duration`, after the `--update` rework.
  where: `skills/manage-todoist/SKILL.md:175`
  why: Doc-checklist coverage regression, not a data-loss/wrong-result defect.
  source: PR #5

- what: Non-finite `content` (e.g. `NaN`) reaches `json.dumps(allow_nan=False)` and raises instead of returning JSON.
  where: `skills/manage-todoist/scripts/pomodoro_sum.py:274`
  why: P2; needs a hand-crafted non-RFC-8259 payload; loud crash, not a silently wrong total.
  source: PR #5

- what: An `--update` that moves a task into Habits/AREAS only downgrades a missing `sectionId` to an advisory instead of a violation.
  where: `skills/manage-todoist/scripts/validate_task.py:477`
  why: P2 policy-tightening decision, not a defect (the advisory still fires); left for owner to decide the rule severity.
  source: PR #5

- what: A P4 habit committed under `--planning` escapes the missing-duration check.
  where: `skills/manage-todoist/scripts/validate_task.py:610`
  why: P2 coverage/policy decision — `duration-missing` is deliberately scoped to p1-p3 today.
  source: PR #5

- what: SKILL.md's "Rules it enforces" list names only 12 of the validator's 17 rule codes, and `--suggest` is undocumented.
  where: `skills/manage-todoist/SKILL.md:163`
  why: Documentation completeness, not a defect.
  source: PR #5

- what: Neither boolean-`amount` guard (`{"amount": true, "unit": "minute"}`) is exercised by the test suite, in either `validate_task.py` or `pomodoro_sum.py`.
  where: `skills/manage-todoist/tests/test_mt_scripts.py:481`
  why: Missing coverage, not a live defect — both guards behave correctly today.
  source: PR #5

- what: A negative `--budget` is accepted and reports `overcommit: true` against an empty task list.
  where: `skills/manage-todoist/scripts/pomodoro_sum.py:210`
  why: P2; an obviously-nonsensical gate from a typo, not a silently plausible wrong total.
  source: PR #5

- what: `evals/evals.json`'s 8-scenario dry-run suite has no scenario requiring a draft to have gone through `scripts/validate_task.py`, even though SKILL.md now makes that step mandatory.
  where: `skills/manage-todoist/evals/evals.json` (thread anchored at `SKILL.md:161`)
  why: Missing behavioral coverage for a mandatory step; not itself a defect.
  source: PR #5

- what: A dest hard link to a source-present file is mistaken for a spelling alias and escapes `--mirror`'s deletion.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:290`
  why: P2; a known trade in the inode-identity filter — it errs toward keeping a file, not deleting one.
  source: PR #5

- what: `labels` sits in both the scope-relevant set (gates the `project-unknown` advisory under `--update`) and the required set (`update-underspecified` requires it on every update draft) — so a spec-compliant duration-only update still triggers the advisory it was supposed to avoid.
  where: `skills/manage-todoist/scripts/validate_task.py`
  why: Open escalation, never resolved by an owner decision in either Merge-time closeout. Resolving it means dropping `labels` from one set or the other. Impact is bounded — `project-unknown` is advisory only.
  source: PR #5

The following five entries are from the 2026-08-22 post-closeout re-review
wave (comments 04:16–05:31 UTC), which post-dates both Merge-time closeout
comments and predates this ledger's first build.

- what: **P1** — GNU `stat -f '%i'` is parsed as a second path argument rather than a format string, so the inode-collision check emits repeated filesystem-report lines and misreads them as duplicate inodes; a GNU-coreutils run of the test suite reproduced 20 sync failures.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:291`
  why: P1 on a GNU/Linux run; the repo targets macOS bash 3.2 + BSD, so this doesn't fail on the supported platform today. Part of the GNU/BSD portability cluster (see end of ledger). Fix: select the BSD `stat -f` or GNU `stat -c` form explicitly.
  source: PR #5

- what: **P1** — the source-collision scan lists only files/symlinks, so a case-sensitive source with `A/one` and `a/two` shows no duplicate when the destination folds case; both directories silently merge in the destination and `--from` exits 0 after deleting the source, permanently losing which directory each file belonged to.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:266`
  why: Reproduced; real data loss on a case-folding destination filesystem (e.g. default macOS APFS) syncing from a case-sensitive source. Fix: validate colliding directory components, not just leaf files, before copying.
  source: PR #5

- what: **P1** — the case-probe file (`.sync_bundle_case_probe.<PID>`) is created via a plain redirection instead of atomically; a leftover same-PID entry from a previously killed run is truncated and then deleted by cleanup, even under default merge mode's "never delete destination-only content" guarantee. If the leftover entry is a symlink, the truncation can also hit its target outside the destination.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:251`
  why: Reproduced by precreating the PID-named entry before sourcing the script. Fix: create the probe atomically without clobbering, and only remove an entry this invocation created.
  source: PR #5

- what: **P2** — decimal-hour durations are summed as binary floats, so a plan whose true total exactly equals `--budget` can report `overcommit: true` (e.g. `0.09h + 1.08h + 1.33h` sums to `150.00000000000003` instead of `150`), violating the documented strict-`>` rule.
  where: `skills/manage-todoist/scripts/pomodoro_sum.py:297`
  why: P2; a rounding-boundary false positive on the daily-plan commitment gate, not a silently-wrong total in the other direction. Fix: parse/sum durations exactly, or apply a deliberate comparison tolerance.
  source: PR #5

- what: **P1** — `cp -R` follows an existing destination symlink (including one nested under `resources/` or `scripts/`) and overwrites its target outside the bundle, rather than aborting the way the file/directory conflict case does; reproduced and argued from GNU `cp --help`'s `--remove-destination` semantics.
  where: `skills/manage-todoist/scripts/sync_bundle.sh:346`
  why: Reproduced and real; recurs across review waves (raised 2026-08-16, 2026-08-19, and again 2026-08-22) without a fix landing. Cross-referenced in the GNU/BSD portability cluster (see end of ledger) because of how it's argued, though the underlying symlink-safety gap isn't itself a dialect difference. Fix: refuse or safely unlink a conflicting destination symlink before copying.
  source: PR #5

## PR #6 — consolidate-memory

Fixed post-ledger: two entries headlined below as the top P1s — the in-repo
`_archive` symlink mis-landing moves in `archive-handoffs.sh` and the
destination-walk-running-after-first-write bug in `sync-harness-mirror.sh` —
were fixed in commit `8c43b45` after this ledger was first built; both entries
have been removed from this list. A related but distinct symlink gap in
`archive-handoffs.sh` was found in the post-closeout re-review wave that
followed that fix (see the new top item below).

- what: **P1** — an in-repo symlinked SOURCE parent (e.g. `memory/handoffs -> ../real-handoffs`, target still inside the repo) walks past the physical-containment check on the source side; a tracked file under it is `mv`'d instead of `git mv`'d, so Git records a deletion instead of the intended rename while the real (untracked) file still sits inside the memory corpus.
  where: `skills/consolidate-memory/scripts/archive-handoffs.sh:256`
  why: Verified real by the fix agent on 2026-08-22, in the post-closeout re-review wave that followed the `8c43b45` fix; not fixed because it sits in a branch of the script that fix left untouched (that fix addressed the destination-side `_archive` symlink, not a symlinked source parent). No data lost on disk; Git state is wrong. Top follow-up item for this PR.
  source: PR #6

- what: An `--also` checkpoint argument that is a symlink is copied as a link, not dereferenced, so the "backup" holds a link rather than real content.
  where: `skills/consolidate-memory/scripts/checkpoint.sh:322`
  why: P2; not silent data loss (the link itself is captured), but the snapshot isn't a real backup.
  source: PR #6

- what: Canonical `_archive/handoffs/*.md` files are pruned out of the inventory entirely instead of being tracked as a read-only archive slice.
  where: `skills/consolidate-memory/scripts/build-inventory-plan.sh:214`
  why: P2 scope decision, deliberate today (archive sits outside every qmd collection root); nothing is lost or misreported.
  source: PR #6

- what: The tab-only guard in the TSV output misses an embedded newline in a path argument (only tabs are escaped/rejected today).
  where: `skills/consolidate-memory/scripts/stat-and-frontmatter.sh:149`
  why: Real, but a standalone-usage gap — in the documented Phase 1 flow, `build-inventory-plan.sh` hard-fails on a newline-bearing filename before this script ever sees it.
  source: PR #6

- what: A source-side directory symlink can hide a same-path mirror-only symlink from the destination pass, so drift goes unreported.
  where: `skills/consolidate-memory/scripts/sync-harness-mirror.sh:389`
  why: Real gap but needs a source-side directory symlink plus an unrelated stray symlink at the same mirror path; outcome is unreported drift, not lost/corrupted content.
  source: PR #6

- what: `add_error` flattens `$1` but not `$2`, so a multi-line `rm` stderr (during `--prune`) splits the TSV-style report row.
  where: `skills/consolidate-memory/scripts/sync-harness-mirror.sh:355`
  why: Minor; needs a multi-line `rm` stderr to trigger, and the damage is a garbled report line, not a wrong action.
  source: PR #6

- what: The `*/<scope>/*` suffix fallback in the ignored-files scan still matches a sibling `other/memory/...` when the project root sits below the worktree root.
  where: `skills/consolidate-memory/scripts/checkpoint.sh:142`
  why: P2; over-reports rather than under-reports, so the safety gate stays conservative (not silently wrong).
  source: PR #6

- what: A FIFO planted in the mirror destination makes `cmp` block, hanging the sync run.
  where: `skills/consolidate-memory/scripts/sync-harness-mirror.sh:322`
  why: P2; hangs visibly with no manifest, rather than corrupting or deleting anything.
  source: PR #6

- what: Scope spellings with `..` or a doubled separator (`foo/../memory`, `memory//`) aren't canonicalized before bucketing, so they land in `unrecognized[]` instead of matching the intended slice.
  where: `skills/consolidate-memory/scripts/build-inventory-plan.sh:73`
  why: P2; fails toward noise (visible in the manifest), not silence.
  source: PR #6

- what: `tests/check_consolidation.sh` derives `ROOT` as only `"$DIR/.."`, so a scoped self-check (e.g. `memory/planning`) looks for the archive under `memory/_archive/handoffs` instead of the real repo-root `_archive/handoffs`, and an open handoff mistakenly archived there is missed by the self-check.
  where: `skills/consolidate-memory/tests/check_consolidation.sh` (review thread anchored at `SKILL.md:271`)
  why: Open item — declined this round as "queued for merge-time triage," but never re-triaged or resolved in the subsequent Merge-time closeout comment. Effectively still open.
  source: PR #6

The following three entries are from the 2026-08-22 post-closeout re-review
wave (comments 05:33 UTC), which post-dates the `8c43b45` fix commit and
predates this ledger's first build.

- what: **P1** — `mktemp -t cm-checkpoint-ignored` fails on GNU/Linux because GNU `mktemp` requires the template to contain at least three consecutive `X` characters; every clean Git checkpoint exits 1 without its required JSON confirmation, and each retry leaves another suffixed branch behind.
  where: `skills/consolidate-memory/scripts/checkpoint.sh:226`
  why: P1 on a GNU/Linux run; the repo targets macOS bash 3.2 + BSD, so this doesn't fail on the supported platform today. Part of the GNU/BSD portability cluster (see end of ledger). Fix: use a portable template such as `cm-checkpoint-ignored.XXXXXX`.
  source: PR #6

- what: **P1** — GNU `stat -f` means "display file system status," not BSD's `stat -f FORMAT`; the script's stat call therefore emits filesystem-status text instead of size/mtime on GNU/Linux, and since only nonempty output is checked, it exits 0 with malformed JSON (e.g. an empty `mtime`). The identical invocation in `stat-and-frontmatter.sh:88` emits corrupt TSV fields for the same reason.
  where: `skills/consolidate-memory/scripts/build-inventory-plan.sh:247`
  why: P1 on a GNU/Linux run; doesn't fail on the supported macOS/BSD platform today. Part of the GNU/BSD portability cluster (see end of ledger). Fix: detect the available `stat` dialect (or use another portable size/mtime mechanism) in both scripts.
  source: PR #6

- what: **P2** — a non-Git checkpoint pass with `scope-path .` creates its backup directory inside the very tree being checkpointed; the subsequent `cp -Rp` then tries to copy the source into its own child, fails, and deletes the partial backup — making the mandatory Phase 0 checkpoint impossible. Any ancestor scope (e.g. `..`) containing `PROJECT_ROOT` has the same problem.
  where: `skills/consolidate-memory/scripts/checkpoint.sh:276`
  why: Reproduced; P2 because it fails loudly (checkpoint impossible) rather than silently losing data, but it blocks a mandatory step for a documented scope value. Fix: create the backup outside the resolved target tree, or reject overlapping target/backup paths before copying.
  source: PR #6

## PR #7 — operate-bmad-loop

- what: `scm.target_branch` isn't validated with `git check-ref-format --branch` before being written to policy; an invalid shorthand (e.g. `epic 1`) is accepted and only fails later at `git branch`, leaving Setup half-configured.
  where: `skills/operate-bmad-loop/scripts/merge_policy.py:532`
  why: P2, low-probability; loud failure, and validation is a clean standalone change.
  source: PR #7

- what: A pre-existing, untracked, non-identical bundled asset (e.g. `scripts/heartbeat.sh`, a `rich-commit/*` file) is replaced with no backup on first Setup.
  where: `skills/operate-bmad-loop/scripts/install_assets.sh:151`
  why: P2, low-probability (needs a project that never ran Setup but already has a same-named file); backup-or-refuse is a clean standalone change.
  source: PR #7

- what: A dangling plugin/heartbeat symlink isn't unlinked during Revert (`[ -e ]` reads it as already absent; needs `-L` too).
  where: `skills/operate-bmad-loop/scripts/revert.sh:108`
  why: Not a state this flow can currently produce (Setup refuses to install through a symlink), but the follow-up should name the leftover link rather than silently no-op.
  source: PR #7

- what: The phase-branch-workflow doc snippet re-creates the phase branch with `git checkout -b` instead of switching to the one Setup already created.
  where: `skills/operate-bmad-loop/references/phase-branch-workflow.md:27`
  why: Doc fix, not a merge blocker.
  source: PR #7

- what: `upgrade.sh` doesn't reject an empty `--cli-trees` list (silently falls back to all three default trees) the way `sync_bmm_skills.sh` does.
  where: `skills/operate-bmad-loop/scripts/upgrade.sh:68`
  why: P2; should be a usage error instead.
  source: PR #7

- what: `upgrade.sh` doesn't validate every required helper/asset path before the global `uv tool install --force` re-pin, so a stale `--skill-root` can leave a half-applied global re-pin.
  where: `skills/operate-bmad-loop/scripts/upgrade.sh:81`
  why: P2; validation should happen before the irreversible global step.
  source: PR #7

- what: `tests/README.md` scenario counts are stale (suite 4 should read 89, combined total 116) after the closeout round's five new scenarios (D12, G6, G7, C12, C13).
  where: `skills/operate-bmad-loop/tests/README.md:201`
  why: Doc drift introduced by the closeout round itself; not a merge blocker since no further code pushes were planned.
  source: PR #7

- what: `references/story-frontmatter.md`'s "two frontmatter fields" line reads as a contradiction — it should clarify it means the two fields with a documented orchestrator failure mode (status → defer, baseline_commit → rollback pause), not all six the script validates.
  where: `skills/operate-bmad-loop/references/story-frontmatter.md:25`
  why: Doc clarity fix, not a merge blocker.
  source: PR #7

- what: `check_module_installed.sh` counts a `bmad-loop-*` directory as an installed skill without requiring a readable `SKILL.md` inside it.
  where: `skills/operate-bmad-loop/scripts/check_module_installed.sh:55`
  why: P2; an empty leftover directory is rare and Setup's later steps fail loudly on it anyway.
  source: PR #7

- what: `tests/verify_setup.sh`'s layout and Git-tracking loop doesn't cover the new `.agent` tree, with fixtures.
  where: `skills/operate-bmad-loop/tests/verify_setup.sh` (thread anchored at `scripts/sync_bmm_skills.sh:87`)
  why: Coverage gap, clean standalone change.
  source: PR #7

- what: `install_assets.sh` doesn't test `-L` before its identical-content fast path, so a symlinked destination whose target already matches is skipped instead of replaced.
  where: `skills/operate-bmad-loop/scripts/install_assets.sh:146`
  why: P2; needs a checkout that already ships such a link, which no path in this flow currently creates.
  source: PR #7

- what: **P1 (known item)** — `install_assets.sh` creates its temp file at a predictable `dest.tmp.<pid>` path instead of a same-directory `mktemp` (O_EXCL), unlike `merge_policy.py`'s hardened equivalent.
  where: `skills/operate-bmad-loop/scripts/install_assets.sh:150`
  why: Real; not fixed — the closeout round's one allowed extra push was spent on the reproduced out-of-project deletion in `sync_bmm_skills.sh`. Fix named: same-directory `mktemp` (O_EXCL), matching `merge_policy.py`.
  source: PR #7

- what: An already-existing phase branch that predates the setup commit is reported "skipped" and Setup still exits 0, even though runs cut from it lack the newly committed assets.
  where: `skills/operate-bmad-loop/scripts/install_assets.sh:345`
  why: Open owner item — the applied decision leaves an existing branch alone by design; failing instead when `HEAD` is not an ancestor of it is a deliberate idempotency-contract change that was flagged but never decided.
  source: PR #7

## PR #8 — manage-planning-repos

- what: `repair_skill_layout.sh relink` can stage a symlink whose canonical `.agents` target is untracked or dirty, so the committed result is a symlink to a path absent in a fresh clone.
  where: `skills/manage-planning-repos/scripts/repair_skill_layout.sh:441`
  why: P2, low-probability (needs an untracked `.agents` canonical copy at relink time); fix is a behavior change too large for the final push.
  source: PR #8

- what: `diff_claude_sections.sh`'s fenced-code closing delimiter doesn't track the opener's run length, so a four-backtick outer fence can be closed early by an inner triple-backtick line, reporting example headings as real extra sections.
  where: `skills/manage-planning-repos/scripts/diff_claude_sections.sh:108`
  why: P2, low-probability; parser change unsuitable for the last push.
  source: PR #8

- what: A failing `qmd collection list` is converted to an empty list instead of aborting before any `collection add`, when discovery is inconclusive.
  where: `skills/manage-planning-repos/scripts/wire_qmd_collections.sh:144`
  why: P2, low-probability (needs `qmd collection list` to fail while `qmd` is otherwise healthy on PATH); `collection add` on an existing collection is rejected rather than destructive, so it fails safe today.
  source: PR #8

- what: `set_board_url.sh`'s "created" path (first-time board setup) skips the no-final-newline restoration that the "existing config" path applies.
  where: `skills/manage-planning-repos/scripts/set_board_url.sh:355`
  why: P2, low-probability (needs a config with no final newline AND no existing `board:` key); deviation only adds a trailing newline, no data lost.
  source: PR #8

- what: `diff_claude_sections.sh`'s `##` heading separator only handles exactly one literal space (`##  Alpha` or a tab produces a spurious missing/extra drift pair).
  where: `skills/manage-planning-repos/scripts/diff_claude_sections.sh:118`
  why: Real but low-probability (hand-edited heading spacing); failure mode is a spurious drift line in a read-only report.
  source: PR #8

- what: `repair_skill_layout.sh remove-dangling` doesn't treat an unstatable symlink ancestor as inconclusive — falls through to "not a directory" instead of refusing.
  where: `skills/manage-planning-repos/scripts/repair_skill_layout.sh:226`
  why: P2; re-review of `729d04f`.
  source: PR #8

- what: `repair_skill_layout.sh remove-dangling` treats a failing `git ls-files --error-unmatch` query (e.g. exit 128) as "path is untracked" instead of refusing on the fatal query failure.
  where: `skills/manage-planning-repos/scripts/repair_skill_layout.sh:504`
  why: P2; re-review of `729d04f`.
  source: PR #8

- what: `set_board_url.sh` doesn't reject a scalar-valued `board:` block before inserting `url:` under it (only sequence values are currently caught).
  where: `skills/manage-planning-repos/scripts/set_board_url.sh:252`
  why: P2; re-review of `729d04f`.
  source: PR #8

- what: Two repos sharing a basename derive the same qmd collection name, with no path-derived discriminator.
  where: `skills/manage-planning-repos/scripts/wire_qmd_collections.sh:168`
  why: P2; re-review of `729d04f`.
  source: PR #8

- what: Whether Setup should gain a pre-commit compare/preserve path so `relink` lands inside the single baseline commit (reopens the "init immediately, defer the baseline commit" decision from `958c3b8`).
  where: `skills/manage-planning-repos/SKILL.md:137`
  why: Open escalation — product-intent call, not a defect fix; never given a final owner decision in any subsequent comment.
  source: PR #8

- what: Standalone-BMAD installer defaults (version, modules, tools) have no hub manifest to derive them from — a spec gap in the Setup step.
  where: `skills/manage-planning-repos/SKILL.md:156`
  why: Open escalation — filling it changes what Setup asks and installs; never given a final owner decision.
  source: PR #8

## GNU/Linux portability cluster

codex's own review environment runs GNU coreutils; the repo's stated target
is macOS bash 3.2 + BSD userland (the same claim the Cross-PR bash-pin item
above exists to enforce). A recurring class of findings is codex reproducing
failures that are really BSD/GNU dialect splits — `stat -f FORMAT` (BSD) vs
`stat -c FORMAT` (GNU, where `-f` means something else entirely) and `mktemp`
template rules (GNU requires 3+ consecutive trailing `X`s). These entries
already exist above; this section only cross-references them, it does not
restate them:

- PR #5 — `skills/manage-todoist/scripts/sync_bundle.sh:291` ("Use a portable inode lookup") — GNU `stat -f '%i'` is parsed as a path argument, not a format string.
- PR #5 — `skills/manage-todoist/scripts/sync_bundle.sh:346` ("Refuse destination symlinks before copying files") — reproduced and argued from GNU `cp --help`'s `--remove-destination` semantics; included here loosely — the underlying symlink-safety gap is not itself a dialect difference and would need fixing on any platform.
- PR #6 — `skills/consolidate-memory/scripts/checkpoint.sh:226` ("Supply a valid GNU mktemp template") — GNU `mktemp` template-length requirement.
- PR #6 — `skills/consolidate-memory/scripts/build-inventory-plan.sh:247` ("Use portable file-stat formatting") — same `stat -f`/`stat -c` split as the PR #5 item above; also affects `stat-and-frontmatter.sh:88` per the same finding.

Not included, despite surfacing in the same 2026-08-22 waves and on the same
GNU-coreutils runs: PR #5's `sync_bundle.sh:266` (case-folding directory
collision), `sync_bundle.sh:251` (case-probe clobbering), and
`pomodoro_sum.py:297` (binary-float budget arithmetic). All three are real
bugs that would reproduce on BSD too — they aren't GNU/BSD command-dialect
differences, just bugs codex happened to find while running on GNU tooling.

Open owner decision, never made: either adopt Linux support as a real work
item (branch on `stat`/`mktemp` dialect, or declare GNU coreutils a
dependency) or explicitly accept BSD-only and expect codex to keep
re-reporting these same four findings on every future review wave, since its
own environment stays GNU/Linux regardless of what the repo targets.

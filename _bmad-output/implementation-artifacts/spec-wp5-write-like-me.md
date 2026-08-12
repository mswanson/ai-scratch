---
title: 'WP5: write-like-me stats, linter, profile validator'
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

**Problem:** write-like-me asks the LLM to eyeball 300 messages for exact frequencies (em dashes, exclamations, emoji, sentence lengths), to self-check drafts against a regexable tell list by re-reading it every time, and to trust a hand-written profile JSON with no validation. The planned Slack collector is INFEASIBLE (2026-08-11 spike: access exists only via claude.ai's hosted connector; no local credential) — collection stays prose per the plan's fallback.

**Approach:** Three Python scripts (stats, lint, validate); SKILL.md swaps the mechanical steps, documents the collector infeasibility inline, and gates the output step on the linter. Voice judgment, bucketing, and generation stay prose. One PR on branch `scripts/write-like-me`.

## Boundaries & Constraints

**Always:** Python stdlib-only; universal contract (terminate; failures non-zero + stderr; stdout machine-readable; argparse allow_abbrev=False); scripts emit raw numbers/hits — qualitative bucketing and fix decisions stay LLM; lint covers LEXICAL tells only (structure/tone tells stay prose judgment); profile schema hardcoded from references/profile-schema.md with a sync-note comment; new suite `tests/test_wlm_scripts.py` registered additive-at-end in Makefile/CI (trivial keep-both conflict with the open WP3 PR accepted and noted in the PR body).

**Ask First:** any change to style-profile.json's existing content; any new required profile field.

**Never:** build the Slack collector (infeasible without a personal Slack app token — documented, not attempted); auto-strip flagged text (lint reports; the LLM decides, e.g. "implement" is a tell only when a plain word works); network access in any script.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| stats happy | JSON array of {text,...} messages (or --plain lines file) | JSON: em_dash count+rate, exclamation/ellipsis rates, short-msg terminal-punct rate, sentence-length histogram + mean, emoji code freq (skin tones kept), lowercase-start rate, abbreviation hits, short-vs-substantive ratio, message_count | empty corpus → all-null stats + `message_count: 0`, exit 0 |
| stats malformed | invalid JSON | stderr reason | exit 1 |
| lint clean draft | draft text file + --profile | `{"hits": [], "clean": true}` | N/A |
| lint hits | draft with em dash (profile disallows), "It's worth noting", sentence-initial However, "may potentially" | hits with pattern name, matched text, offset, `allowed_by_profile` where applicable; `clean: false` | exit 0 (hits are data) |
| lint mid-sentence however | "x, however, y" | NOT flagged (anchored regex) | N/A |
| validate happy | style-profile.json + optional corpus file | `{"valid": true, age_days, snippet_count, snippets_verbatim: [...]}` | N/A |
| validate broken | missing dimension / bad enum / 3 snippets | `valid: false` + missing_fields/type_errors/snippet issues | exit 1 |
| validate stale | generated_on > 180 days | `stale_warning: true` (valid may still be true) | exit 0 |

</frozen-after-approval>

## Code Map

- `skills/write-like-me/SKILL.md` -- Step 1 (:51-54) profile gate → validate script; Step 2 (:60-75) collection prose kept + infeasibility note + stats script for the counting (:77-87 countable sub-signals); Step 3 (:98) self-check → lint script gate; Refreshing (:111-113) mentions staleness warning
- `skills/write-like-me/references/robotic-tells.md` -- source of the lexical pattern list (lint hardcodes with sync-note; structure/tone sections explicitly out of lint scope)
- `skills/write-like-me/references/profile-schema.md` -- source of required fields/enums (validator hardcodes with sync-note)
- `skills/write-like-me/style-profile.json` -- existing profile; validator must pass it as-is (regression fixture)
- `skills/write-like-me/scripts/` -- new: `compute_style_stats.py`, `lint_robotic_tells.py`, `validate_profile.py`
- `skills/write-like-me/tests/test_wlm_scripts.py` -- new suite; `Makefile` + `.github/workflows/tests.yml` additive-at-end registration

## Tasks & Acceptance

**Execution:**
- [x] `scripts/compute_style_stats.py [--plain] <messages-file>` -- per matrix; Slack markup normalized (`<@U…>` mentions, `<url|label>` links) before counting; sentence splitting simple and documented
- [x] `scripts/lint_robotic_tells.py <draft-file> [--profile <json>]` -- lexical tells from robotic-tells.md: em/en dashes (profile-aware via `punctuation` dimension), stock phrases + formal transitions, sentence-initial However/Moreover/Furthermore/Additionally (anchored), formal verbs (flag `review`, never `strip`), hedge stacking; each hit typed `severity: strip|review`
- [x] `scripts/validate_profile.py <profile.json> [--corpus <messages-file>]` -- required fields/enums, generated_on age (>180d stale warning), 5-10 example_snippets, verbatim substring check vs corpus with normalization
- [x] `skills/write-like-me/SKILL.md` -- swaps per Code Map; collection prose tightened + one-paragraph infeasibility note (hosted-connector-only access; personal Slack app token would enable a future collector); Step 3 output gates on lint clean-or-explained
- [x] `tests/test_wlm_scripts.py` -- fixtures per matrix row + the real style-profile.json as a must-pass regression fixture; register `test-wlm-scripts` additive-at-end (separate .PHONY line, `test:` union line, CI step appended last)

**Acceptance Criteria:**
- Given the shipped style-profile.json, when validate_profile.py runs, then `valid: true` (with any stale warning permitted).
- Given a draft containing each lexical tell from robotic-tells.md's Punctuation and Word-choice sections, when lint runs, then every planted tell is hit and the mid-sentence "however" control is not.
- Given SKILL.md post-swap, then Step 2 explains WHY collection stays manual, and no prose asks the LLM to count frequencies by eye.
- Given `make test`, all suites green; the Makefile/CI diff is additive-at-end only.

## Spec Change Log

## Design Notes

Collector infeasibility is a spike-verified fact recorded in Intent (frozen); the SKILL.md note keeps the door open (personal Slack app + xoxp token). The lint's profile-awareness reads the same dimension names validate_profile.py enforces — one hardcoded schema constant shared by both scripts in a small `_wlm_common.py` if cleaner.

## Verification

**Commands:**
- `python3 -m py_compile` all; `python3 skills/write-like-me/tests/test_wlm_scripts.py`; `make test` exit 0; `make lint-docs` 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat`: only `skills/write-like-me/**` + additive Makefile/CI tails.

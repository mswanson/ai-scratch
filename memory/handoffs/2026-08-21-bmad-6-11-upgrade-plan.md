---
date: 2026-08-21
topic: BMAD 6.11 upgrade — research complete, plan sequenced behind the forge-skills PR merges; the Option B trial PASSED
repos:
  - ai-scratch
  - forge-skills
  - lyceum
  - lyceum-planning
status: open
---

## Authoritative context

Read these first; do not re-derive what they settle.

- `lyceum-planning/_bmad-output/planning-artifacts/decision-bmad-loop-topology.md` — **Accepted 2026-08-10: Option B, per-spoke BMAD.** Its sequencing step 2 ("run one story end to end, judge it") is now COMPLETE — see State. The merge plan stays ON HOLD.
- `lyceum-planning/_bmad-output/planning-artifacts/bmad-loop-vs-implement-story.md` — which implement-story phases the loop owns vs which stay with the wrapper. Still accurate, with two 6.11 corrections noted below.
- `lyceum-planning/memory/handoffs/2026-08-21-per-spoke-bmad-and-installer-findings.md` — the installer + bmad-loop mechanics discovered standing up the lyceum spoke. Its four "re-verify against 6.11" items are answered below.
- `ai-scratch/memory/handoffs/2026-08-21-forge-skills-pr-closeout.md` — the eight open script-conversion PRs. **This is what gates the 6.11 skill work.**
- BMAD-METHOD v6.11.0 release notes: `gh api repos/bmad-code-org/BMAD-METHOD/releases/tags/v6.11.0 --jq .body`. bmad-loop v0.10.0: same call against `bmad-code-org/bmad-loop`. Do not summarize from memory; the deltas below are the only ones that bear on this setup.

## State

### The Option B trial PASSED (2026-08-21)

Run `20260821-215223-99fb`, story `1-11-per-message-narrative-commit`, in the `lyceum` spoke. Finished clean: `finished: true`, not stopped, not crashed, never paused.

- Dev session completed on attempt 1, no retry.
- Review cycle 1 returned `status: done`, `followup_review_recommended: false`.
- Story committed `64b3522`, unit branch merged into `epic-1`, worktree auto-cleaned.
- Spec is `status: done`, `review_loop_iteration: 0`. Sprint status: `1-11… done`, `epic-1: in-progress`.

All three assumptions the prior handoff flagged held: untracked BASE_SKILLS self-copied into the worktree, the `epic-1-context.md` handoff worked with `planning-artifacts/` absent entirely, and worktree seeding delivered what was needed. The `worktree-seed-skipped` journal entry for `.mcp.json` and `.claude/settings.json` is benign: both are git-tracked, so the checkout provides them and seeding correctly skips.

**Two caveats for the verdict, not blockers:**

- `token-budget-exceeded` fired: 7,892,520 weighted against `max_tokens_per_story = 2000000`, roughly 4x over. Advisory only under v0.9.1, but it's a real cost datapoint from one story.
- The spec carries `warnings: ['oversized']`. In 6.11 `bmad-build` halts and asks when a spec exceeds its 1600-token scope budget, and build-auto adds explicit blocked reasons. **This same story might not run unattended post-upgrade.** Worth a deliberate test.

One story is one datapoint, but it is the datapoint the decision was waiting on.

### 6.11 research — what actually bears on this setup

Full changelog is in the release notes; these are the ones that matter here.

- **bmad-loop v0.10.0 must move with core 6.11, and not only for the rename.** v0.9.1 hotfixed `bmad-dev-auto` → `bmad-build-auto` naming only. Two further couplings: 6.11 deleted `deferred-work.md` in favor of the spec's frontmatter `deferred:` list, and v0.10.0 is what harvests findings from there into the ledger; and 6.11 renders skills through `_bmad/scripts/render_skill.py`, for which v0.10.0 adds three preflight findings (`skills.dev-renderer`, `-config`, `-sources`). On 6.11 + v0.9.1 a renderer failure produces a `HALT:` with no spec and no preflight explaining it. **Upgrade both or neither, per repo.**
- **`pins.md`'s commit pin can go, but not for the reason the prior handoff expected.** 6.11 does NOT ship the three review hunters as standalone skills; they became forwarding shims with their behavior as lenses on the new `bmad-review`. The pin drops because v0.10.0 narrowed the hard requirement to the resolved dev primitive plus whatever review skills the project's `customize.toml` names, with everything else copied best-effort.
- **`operate-bmad-loop` Setup step 0 is stale.** v0.10.0 (#258) changed `bmad-loop-setup`: it no longer registers BMAD config at all (the installer owns it and regenerates `config.toml` wholesale, discarding outside writes) and its PEP 723 scripts are gone. It now writes one help CSV, installs the tool, and preflights.
- **v0.10.0 partly absorbs the flow layer.** `max_tokens_per_story` is now re-checked at every session boundary during the run rather than once after the story is marked done, raising ATTENTION plus a desktop notice, latched per story. Worth re-testing whether the heartbeat (`operate-bmad-loop` Setup step 7, "prevents the #1 merge-back pause") still earns its place.
- **`#443` has NOT landed.** v0.10.0 explicitly refuses `isolation = "worktree"` combined with a `repo_root` override and names #443 as the open work. The hub-runs-spoke-code option remains dead; per-spoke BMAD stays the only supported shape.

### Answers to the prior handoff's four installer re-verification items

- **Keep the `--directory` workaround.** 6.11 fixed a *different* installer directory bug (#2680: the prompt returned the focused autocomplete option rather than typed text). The omitted-flag path, where non-TTY stdin exits 0 having done nothing, is not what #2680 describes. Do not simplify this out of `manage-planning-repos` Step 1.
- **`{output_folder}` is probably fixed.** #2671 addresses the same failure class: `--set core.<key>` overrides patched the TOML after install but never reached config collection, so artifact paths still used `_bmad-output/` with exit code 0 and no warning. Still worth a targeted test.
- **Review hunters:** see above. Not shipped standalone; shims + lenses.
- **`--modules bmad-loop` silent-ignore:** untested. No 6.11 note addresses it.

### `bmad-project-context` (replaces `bmad-generate-project-context`)

- Target file is **hardcoded to `AGENTS.md`**, not configurable. `customize.toml` exposes only `activation_steps_prepend`, `activation_steps_append`, `persistent_facts`, `on_complete`, `external_sources`. Redirecting it would mean editing installer-owned source.
- It writes a **delimited splice**, markers `<!-- bmad:context -->` … `<!-- /bmad:context -->`, guaranteeing everything outside them stays byte-identical, with a provenance comment recording verification date and SHA. **So the thin Codex pointer in `assets/AGENTS.md` and BMAD's block coexist in one file.** This was the feared conflict; it isn't one.
- An existing `docs/project-context.md` still loads as a source, so migration is: run `setup`, it reads the current file and distills. Expect the result much smaller — the admission test excludes anything derivable from source, so dev commands stay out. That is complementary to the CLAUDE.md-is-source-of-truth-for-commands rule, not in conflict.
- **Real loss with no upstream fix scheduled:** the generated overview, source-tree, and deep-dive pages are gone. Release notes say the deeper "explain this system and its rationale" capability is "still to come."

### Mode A vs Mode B — what transitioning costs

Decision made this session: **Michael wants the autonomous loop; Mode B's babysitting is the thing being traded away.** Only implement-story phase 1 changes; phases 0 and 2–5 are identical across modes, so ticket discipline, test baseline, lint gates, draft-PR shipping, AI review triage, HIL gate, learnings, and 5.5 close-out all survive.

Losses, with recoverability:

| Loss | Status |
|---|---|
| Story-file authority (build-auto regenerates its own spec from intent) | recoverable via `[gates] mode = per-story-spec-approval`, at one stop per story |
| Mid-story steering | partly recoverable: gates, escalation, v0.10.0's `awaiting-operator` park + `bmad-loop confirm` |
| In-file Dev Agent Record + running Change Log | not recoverable; partly compensated by the rich-commit plugin |
| Per-task commits | not recoverable; `finalize_commit` squashes before merge, so no `merge_strategy` restores it |
| Cross-repo stories | not recoverable; `repo_root` is one path, #443 open |
| Per-task metrics in session state | not recoverable; story-level survives |

`bmad-dev-story` is a v6-shim retained in full, still runs by name, removal rides the v7 cut with no announced date. Upstream hasn't finished its own cross-reference cleanup (`bmad-code-review/steps/step-04-present.md` still suggests running `dev-story`), so there is no urgency.

### The sequencing constraint that reorders everything

**All three skills the 6.11 work targets are mid-refactor with open PRs.** Editing them on `main` now means writing against files about to be restructured, and the script conversion moves logic out of SKILL.md prose into `scripts/`, which changes where several planned edits belong.

| Planned 6.11 edit | Blocked by |
|---|---|
| `pins.md` re-pin, Setup step 3 removal, step 0 fix | PR #7 `scripts/operate-bmad-loop` @ `9344eb0` |
| Step 7 → `bmad-project-context`, Step 3 AGENTS.md block | PR #8 `scripts/manage-planning-repos` @ `729d04f` |
| Mode B disposition | PR #3 `scripts/implement-story` @ `1731a43` |

### Correction made this session

Two edits were sitting uncommitted in the forge-skills working tree. On inspection **the `SKILL.md` one was a byte-identical duplicate of content already on PR #8** (zero differing lines in the provisioning/Step 1 sections; PR #8's SKILL.md is 473 lines vs main's 284). It was committed, then dropped. The `assets/hub-CLAUDE.md` edit is genuinely new — no PR branch touches that file — and is held on a branch pending the merges.

### Per-repo state

| Repo | Branch | Uncommitted | Last relevant commit |
|---|---|---|---|
| `ai-scratch` (hub) | `main` | clean | `36b9b72` planning: WP7/WP8 specs closed out |
| `forge-skills` | **`manage-planning-repos/autonomous-provisioning`** (checkout is NOT on main) | clean | `576a905` docs: route hubs to the forge-skills workflow skills — **local only, unpushed, held deliberately** |
| `lyceum` (spoke) | `epic-1` (phase branch) | clean | `6fefc2d` fix(rich-commit); story commit is `64b3522` |
| `lyceum-planning` (hub) | `docs/bmad-loop-topology-research` → PR #56 OPEN | see that repo's own handoff | `94f0abd` |

Dropped commit `2882b1a` remains in forge-skills reflog if ever wanted.

Local BMAD installs, all on 6.10.0 unless noted: `ai-scratch`, `lyceum`, `lyceum-planning`, `auth0/star0`, `auth0/auth0-bmad-poc`, `auth0/bmad-610`; `marshal/marshal-planning` 6.8.0; `corex-webapp` 6.9.0; `bmad/paideo` + `bmad/bmad-workflows` 6.2.2 (dormant, no commits since setup — propose skipping). bmad-loop tool pinned `v0.9.1` (`uv-receipt.toml` → `rev=v0.9.1`); v0.10.0 is available.

## Next work

1. **Judge the trial properly and record the verdict** in `lyceum-planning/_bmad-output/planning-artifacts/decision-bmad-loop-topology.md` (its step 3). Review `git log -p main..epic-1` in the spoke, weigh it against the Amelia flow, and decide on the two caveats: the 4x token overrun and whether the `oversized` spec is acceptable. This closes the decision that has been open since 2026-08-10.
2. **Finish the forge-skills PR closeout and merge #1–#8**, per `2026-08-21-forge-skills-pr-closeout.md` Next work 1–4. Only #5 and #6 have open threads.
3. **Land `576a905` on merged main.** Straight to main, not folded into PR #8 — that would violate the no-rebase-on-PR-branches rule.
4. **Then the 6.11 skill pass**, against post-refactor files: drop the commit pin from `pins.md` and re-pin the tool to v0.10.0; remove `operate-bmad-loop` Setup step 3 and fix step 0; point `manage-planning-repos` Step 7 at `bmad-project-context` and teach Step 3 to expect the managed block. Check whether each edit now belongs in prose or in the new `scripts/`.
5. **Pilot the upgrade on ai-scratch only**: 6.11 + bmad-loop v0.10.0 together, populate `[verify].commands` (empty here, so a run commits with no deterministic gate), then re-test whether the heartbeat and the rest of the flow layer still earn their place.
6. **Then the remaining repos**, in order of activity: `lyceum` + `lyceum-planning`, `auth0/star0`, `auth0/auth0-bmad-poc` (rename its `_bmad/custom/bmad-create-story.toml` override or migrate that repo's flow), then `marshal-planning` and `corex-webapp`, which have no bmad-loop and so carry no pairing risk.

## Constraints to honor

- **Option B is decided and now validated.** Per-spoke BMAD, not the repo merge. `merge-plan-lyceum.md` stays ON HOLD; reopening it is a decision, not a step.
- **Core 6.11 and bmad-loop v0.10.0 upgrade together, per repo.** Never one without the other on a repo that runs the loop.
- **Never launch a `bmad-loop run` from an agent tool call.** The wrapper gets reaped and the engine dies silently. Hand the command to the user; launch from a human terminal with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`.
- **Do not edit `manage-planning-repos`, `operate-bmad-loop`, or `implement-story` until their PRs merge.**
- No merge/rebase/squash/force-push on the PR branches; one commit per intervention. GitHub secondary rate limit trips after ~6 rapid review-thread replies; space them 75s.
- **Review what is staged before committing.** A prior session committed Codex runtime state including live OAuth tokens via a careless `git add -A`. Stage named files only.
- `.bmad-loop/policy.toml` is per-machine and gitignored; never commit it.
- BMAD framework files stay installer-owned: `bmad-*` skills, `_bmad/` module trees, `_bmad/scripts/`, `_bmad/_config/`, `_bmad/config.toml`, module `config.yaml`. Customization goes in `_bmad/custom/`.
- The forge-skills checkout is parked on a non-main branch; switch back before work expecting main.

## Open user inputs

1. **Trial verdict.** Does one clean story at 4x the token budget clear the bar against the Amelia flow, or does it need a second story before Option B is called proven?
2. **Whether `per-story-spec-approval` goes on permanently.** It buys back story-file authority at the cost of one stop per story, which is partly the babysitting being traded away. The trial ran without it and produced a clean result, which is evidence but not a decision.
3. **Dormant-repo scope.** `bmad/paideo`, `bmad/bmad-workflows` (both 6.2.2), `lyceum/test`, `auth0/bmad-610` have no activity since setup. Skip them entirely, or bring them current?
4. Carried forward, unanswered from the prior handoffs: the `style-profile.json` workplace snippets on PR #4, the planning-artifact audit scope, `agent-maya` disposition, and whether to re-enable `[adapter.review] name = "codex"` in the spoke.

## Suggested skills

- `operate-bmad-loop` — Action 5 (Upgrade) for step 4 above; Action 1 (Verify) after each repo's upgrade. **Not until PR #7 merges.**
- `manage-planning-repos` — Verify first on any repo before mutating. **Not until PR #8 merges.**
- `implement-story` — its per-spoke runtime edits are still pending (mode-detection root, `{artifacts}` resolution, Mode A re-rooting, the empty `repos:` config key). **Not until PR #3 merges.**
- `consolidate-memory` — after the PRs merge and the trial verdict is recorded, a pass would fold this session's durable findings (the 6.11 deltas, the installer answers) out of this handoff and into `memory/`.

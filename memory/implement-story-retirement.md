---
name: implement-story-retirement
description: implement-story skill retired 2026-09-28; forge-skills PR merge gated behind story WP9; manage-planning-repos board decoupling is the follow-up
metadata:
  type: project
---

The `implement-story` skill (forge-skills) was retired on 2026-09-28 on branch `retire/implement-story`
(worktree `~/Code/forge-skills-wt/retire-implement-story`). The bmad-loop tool at v0.12.0 plus
`operate-bmad-loop` cover its scope: phase branch, one commit per story, review convergence,
`awaiting-operator` for human-only follow-ups, the phase PR as the human-review gate. Its ship and
review-triage phases were never used (all 16 forge-skills PRs non-draft, unlabeled; one session-state
file ever written, WP9, manual mode).

**Why:** the skill was ~300 KB of scripts and tests wrapping a process the loop replaced; 8 open
follow-ups in deferred-work.md against code with one partial use.

**How to apply:**
- Do not merge the retirement PR until story WP9 (`manage-planning-repos/hub-registry`) has merged:
  the WP9 session calls implement-story scripts through `~/.claude/skills/implement-story`, which
  resolves into the main forge-skills checkout.
- After merging: pull forge-skills main, then `trash ~/.agents/skills/implement-story`,
  `~/.claude/skills/implement-story`, `~/.codex/skills/implement-story` (dangling symlinks; the
  dotfiles `update-skills.sh` mirror does not prune).
- Then do the manage-planning-repos decoupling recorded in deferred-work.md (board feature still
  names implement-story). Kept out of the PR to avoid conflicts with WP9's edits.
- Codex-before-PR moved into `operate-bmad-loop` (Action 3 and phase-branch-workflow.md).
- `[verify] commands` in `.bmad-loop/policy.toml` is still empty in this hub; that is where the
  test/lint gate implement-story used to run by hand now belongs. Related: [[bmad-loop-pins]].

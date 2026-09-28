---
date: 2026-09-27
topic: "forge-skills-pr13-pr14-review-closeout"
repos:
  - "forge-skills"
  - "ai-scratch"
status: open
---

## Authoritative context

- https://github.com/forge512/agent-skills/pull/13 (merged 2026-09-27 as c46e2d6): manage-planning-repos spoke-symlink verify, bootstrap, and detect. The review threads carry the full disposition of every finding; do not re-derive.
- https://github.com/forge512/agent-skills/pull/14 (merged 2026-09-27 as 5fe1d7d): operate-bmad-loop heartbeat binds to `bmad-loop-<RUN_ID>`. Its review thread records the capture-pane bug Codex found and the pane-identity limitation left open.
- `_bmad-output/implementation-artifacts/deferred-work.md`, section "PR #14 — operate-bmad-loop heartbeat session binding": the one item deferred from this work.
- `memory/bmad-loop-pins.md` and this hub's `CLAUDE.md` Agent Routing line: the bmad-loop pin moved to v0.12.0 in a separate concurrent session (see Constraints). Read those for the pin, not this file.
- `~/.codex/config.toml`: reset 2026-09-27 to `model = "gpt-5.6-sol"`, `model_reasoning_effort = "high"`, matching the ladder in the user's global CLAUDE.md. Not dotbot-managed.

## State

Done, all verified:

- PR #13: two Claude findings fixed (3450ea7), four Codex adversarial findings fixed (973244e), here-string loops replaced by process substitution (b52114b). Suite 222 to 240 passing. Replies posted in both review threads. Merged by the user.
- PR #14: fake-tmux session-binding test added (5ec2e86); Codex found the PR's own `capture-pane -t "=$SESS"` fails on tmux 3.7b, fixed to `"=${SESS}:"` (2c6c4fb), confirmed on an isolated tmux server. Suite 148 to 150 passing. Reply posted. Merged by the user.
- Cleanup: PR worktrees under `~/Code/forge-skills-wt/` removed, local and remote PR branches deleted.
- Merged fixes are live on this machine: `~/.claude/skills/*` resolve into the forge-skills checkout, whose current branch (`operate-bmad-loop/base-branch` at 5b81803) sits on top of merged main. Confirmed by grepping the live heartbeat and verify scripts.
- This hub: manage-planning-repos Setup steps 3 and 4.5 applied. `wire_codex_config.sh` reported `settings_json: created`, `gitignore: appended`, no tracked or committed runtime state. `AGENTS.md` copied from the skill's asset. The merged spoke verifier reports both spokes ok, 0 drift.

Pending, uncommitted in ai-scratch (this session's files only): `.gitignore` (the `.codex/*` block), `.codex/settings.json`, `AGENTS.md`, `_bmad-output/implementation-artifacts/deferred-work.md`, and this handoff. `CLAUDE.md`, `memory/MEMORY.md`, and `memory/bmad-loop-pins.md` are dirty from the concurrent pin session, not this one.

Repo state at handoff time:

| repo | branch | dirty |
|---|---|---|
| forge-skills | `operate-bmad-loop/base-branch` (5b81803, on merged main) | six implement-story files, owned by the concurrent session |
| ai-scratch | `main` (87c8710) | the files listed above |

## Next work

1. Commit this session's ai-scratch files (the five listed under Pending) separately from the concurrent session's pin edits; do not sweep `CLAUDE.md` or `memory/bmad-loop-pins.md` into it unless that session is done.
2. Deferred item PR #14 in the ledger: heartbeat should capture by stable pane id, not the session's active pane. Pick it up as its own forge-skills branch when there is appetite; it needs a fixture with a blocked task pane beside a changing active pane.
3. Optional: the ledger still has no `DW-<n>` ids (legacy format); a `bmad-loop sweep --migrate` would normalize it, including the new PR #14 entry.

## Constraints to honor

- A concurrent Claude session (peer `ai-scratch-92` at handoff time) owns the bmad-loop v0.12.0 pin work: it committed `chore(operate-bmad-loop): pin bmad-loop tool at v0.12.0` on `operate-bmad-loop/pin-v0.12.0`, pushed it, and checked out `operate-bmad-loop/base-branch` in the main forge-skills checkout. This session's rebase of the pin branch onto origin/main interleaved with that and landed cleanly (5b81803). Do not touch the forge-skills main checkout or those dirty implement-story files from a PR-follow-up session.
- Test targets: `make test-verify-hub` (manage-planning-repos) and `make test-verify-setup` (operate-bmad-loop) from the forge-skills root. Scripts must run on macOS bash 3.2 and BSD sed; hermetic fixtures only.
- The three spoke-table parsers (verify, bootstrap, detect) are deliberately duplicated and must stay identical.
- Codex adversarial review is run locally via the plugin's companion script from the branch worktree: `node <plugin-root>/scripts/codex-companion.mjs adversarial-review --wait --base origin/main --scope branch "<focus>"`. It runs in a read-only sandbox, so its "could not run the suite" notes are expected; verify its findings on a real tmux or shell before acting.
- Codex config default is Sol at high effort; do not set Astra back without the user asking.

## Open user inputs

- None blocking. The GNU/Linux portability decision in the ledger's last section remains unmade and is unrelated to this work.

## Suggested skills

- `superpowers:receiving-code-review` when processing further review feedback on agent-skills PRs.
- `manage-planning-repos` Verify (option 1) on this hub after committing, to confirm the three Codex gaps are closed.
- `bmad-loop-sweep --migrate` if the ledger is normalized (automation-only skill; run via bmad-loop sweep).

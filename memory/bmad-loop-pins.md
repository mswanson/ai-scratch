# bmad-loop version pins

- The v0.9.0 bundled hook (`.bmad-loop/bmad_loop_hook.py`) includes antigravity/agy payload handling — it is part of the tool, not local drift. Do not revert it; `bmad-loop init` reinstates it. Antigravity stays unsupported via registered CLIs (claude + codex) and policy routing.

Updated 2026-07-31 (Upgrade action, auth0-bmad-loop skill — since renamed forge-loop).

- `bmad-loop` tool: pinned to tag `v0.9.0` (`git+https://github.com/bmad-code-org/bmad-loop.git@v0.9.0`). Verified the tag contains the known-good fix commit `eb780d5` (`compare eb780d5...v0.9.0` → ahead, behind_by 0). Previous install: same 0.9.0 code but from an unpinned git source.
- BMAD-METHOD bmm skills (`bmad-dev-auto`, `bmad-review-verification-gap`): unchanged, still at commit pin `8ea1b7673bbd56c8234aa87344ee6a6626966193`; no BMAD-METHOD release newer than v6.10.0 as of this date.
- Layout note: `.claude/skills/*` were de-symlinked to real dirs on 2026-07-31 and committed on `bmad-loop-dev` (1079ccb), including materializing `bmad-review-verification-gap` (missed by the first pass as a symlink into `.agents/skills`). `bmad-dev-auto` + `bmad-review-verification-gap` are tracked, so worktree sessions see them. `bmad-loop init --force-skills` works on this layout; the old symlink caveat no longer applies. `_bmad/*.bak` installer backups are gitignored.
- Bundled loop skills (`bmad-loop-resolve`, `bmad-loop-setup`, `bmad-loop-sweep`) refreshed to the v0.9.0 bundle via `bmad-loop init --force-skills` in both `.claude/skills/` and `.agents/skills/`. CLIs registered: claude + codex (codex hooks at `.codex/hooks.json`; policy.toml still routes all stages to claude).

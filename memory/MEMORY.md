# Project Memory: ai-scratch

## Project Context
- Sandbox and authoring hub for the BMAD tooling and the token-optimization framework. Carries all BMAD modules deliberately (bmb/cis/tea live here); heaviest sessions by design.
- Code spoke: `forge-skills` symlink → real path `/Users/michaelswanson/Code/forge-skills` (private repo, canonical home of the user skill family (verb names, no prefix since 2026-08-01)). This hub plans and maintains those skills; searches and delegation use the real path, never the symlink.
- Code spoke: `dotfiles` symlink → real path `/Users/michaelswanson/Code/dotfiles` (dotbot-managed, `mswanson/dotfiles` on GitHub). Since 2026-08-01 also the canonical home of Claude Code global config: `~/.claude/{CLAUDE.md,RTK.md,settings.json,hooks,statusline.sh}` and `~/.agents/.skill-lock.json` are dotbot symlinks into `dotfiles/.claude/` and `dotfiles/.agents/`. Searches and delegation use the real path, never the symlink.

## Key Artifacts
- [Dotfiles update plan](../_bmad-output/planning-artifacts/2026-08-02-dotfiles-update-plan.md) — working punch-list for the dotfiles spoke; post-cleanup phase
- [implement-story retirement](implement-story-retirement.md) — retired 2026-09-28; don't merge the PR before WP9 lands; mpr board decoupling is the follow-up
- [bmad-loop version pins](bmad-loop-pins.md) — tool at tag v0.12.0 (2026-09-27); hub phase branch `bmad-loop-dev` named in policy but not present locally
- [Framework design (authoritative)](../_bmad-output/planning-artifacts/2026-07-31-token-optimization-framework-design.md)
- Hub/spoke CLAUDE.md templates live in the manage-planning-repos skill assets (forge-skills repo); the old `docs/templates/` copy is archived at `_archive/templates/`
- [Cloudflare token rolling](cloudflare-token-rolling.md) — same token ID recurring = user rolled the secret; don't nag to delete/recreate
- [Cloudflare migration state](handoffs/2026-08-02-cloudflare-migration.md) — 15 domains migrated; forge512.com, registrar transfer, S3→R2 paused; brief at `_bmad-output/planning-artifacts/cloudflare-migration-brief.md`
- [forge-skills spoke](forge-skills-spoke.md) — repo facts, AI review infrastructure (claude[bot] + Codex app), and code-review learnings (isolated read-only claude -p; reject relative config paths; one live smoke per story)
- [CLI skill trees](cli-skill-trees.md) — .agent (singular) is Antigravity's dir, not an orphan
- [qmd index and registry](qmd-index-registry.md) — collections tracked in dotfiles, sqlite disposable; missing paths are inert, so one registry covers every machine
- [Claude Code settings scopes](claude-settings-scopes.md) — no user-scope settings.local.json; model/effortLevel churn the tracked settings.json by design
- [dotbot link clobbers](dotbot-link-clobbers.md) — iTerm2 and `codegraph upgrade` replace `~/.claude` dotbot links with regular files; check with `[ -L ]` and re-link
- [LiteLLM local adapter](handoffs/2026-08-08-litellm-local-adapter.md) — Claude Code ↔ local models, on-demand; built and verified, untested in real use
- [Skill dedup and branch merge](handoffs/2026-08-08-skill-dedup-and-branch-merge.md) — `handoff` skill removed for `write-handoff`; never squash/rebase hub PRs (memory cites SHAs)
- [BMAD 6.11 upgrade plan](handoffs/2026-08-21-bmad-6-11-upgrade-plan.md) — research done; Option B trial PASSED; skill work queued behind the forge-skills PR merges
- [forge-skills PR wrap-up](handoffs/2026-08-25-forge-skills-pr-wrapup.md) — #4 merge-ready (scrubbed); post-merge sweep, worktree cleanup, 82-item ledger; supersedes the 2026-08-21 closeout
- [Dotfiles remaining-surfaces plan](../_bmad-output/planning-artifacts/2026-08-25-dotfiles-remaining-surfaces-plan.md) — EXECUTED 2026-08-25 in 10 commits (15a3dcd..cddb948); phased brew upgrade and `make macos` deliberately not run
- [Dotfiles bootstrap reproducibility plan](../_bmad-output/planning-artifacts/2026-08-25-dotfiles-bootstrap-reproducibility-plan.md) — EXECUTED 2026-08-26; all 7 gaps closed, bootstrap 8→12 steps. Untested on a clean $HOME
- [Recipe corpus project](../_bmad-output/planning-artifacts/2026-08-25-recipe-corpus-project.md) — collect recipes to Cooklang, repo of .cook files, capture skill; cookcli already installed
- [Local RAG and tuning scope](../_bmad-output/planning-artifacts/2026-08-25-local-rag-and-tuning-scope.md) — qmd is already a working local RAG; LiteLLM :4000 is the seam for eval tools; MLX not PyTorch for tuning on M1 Max
- [Saved-reading agent idea](../_bmad-output/planning-artifacts/2026-08-25-saved-reading-agent-idea.md) — owner wants an agent to read and summarize Pinboard pins + read-later backlog; unscoped, start by counting the pins
- [Handoffs](handoffs/)

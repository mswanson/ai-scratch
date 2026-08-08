# Project Memory: ai-scratch

## Project Context
- Sandbox and authoring hub for the BMAD tooling and the token-optimization framework. Carries all BMAD modules deliberately (bmb/cis/tea live here); heaviest sessions by design.
- Code spoke: `forge-skills` symlink → real path `/Users/michaelswanson/Code/forge-skills` (private repo, canonical home of the user skill family (verb names, no prefix since 2026-08-01)). This hub plans and maintains those skills; searches and delegation use the real path, never the symlink.
- Code spoke: `dotfiles` symlink → real path `/Users/michaelswanson/Code/dotfiles` (dotbot-managed, `mswanson/dotfiles` on GitHub). Since 2026-08-01 also the canonical home of Claude Code global config: `~/.claude/{CLAUDE.md,RTK.md,settings.json,hooks,statusline.sh}` and `~/.agents/.skill-lock.json` are dotbot symlinks into `dotfiles/.claude/` and `dotfiles/.agents/`. Searches and delegation use the real path, never the symlink.

## Key Artifacts
- [Dotfiles update plan](../_bmad-output/planning-artifacts/2026-08-02-dotfiles-update-plan.md) — working punch-list for the dotfiles spoke; post-cleanup phase
- [bmad-loop version pins](bmad-loop-pins.md) — tool pinned to tag v0.9.1; symlinked-skills layout caveats
- [Framework design (authoritative)](../_bmad-output/planning-artifacts/2026-07-31-token-optimization-framework-design.md)
- Hub/spoke CLAUDE.md templates live in the manage-planning-repos skill assets (forge-skills repo); the old `docs/templates/` copy is archived at `_archive/templates/`
- [Cloudflare token rolling](cloudflare-token-rolling.md) — same token ID recurring = user rolled the secret; don't nag to delete/recreate
- [Cloudflare migration state](handoffs/2026-08-02-cloudflare-migration.md) — 15 domains migrated; forge512.com, registrar transfer, S3→R2 paused; brief at `_bmad-output/planning-artifacts/cloudflare-migration-brief.md`
- [CLI skill trees](cli-skill-trees.md) — .agent (singular) is Antigravity's dir, not an orphan
- [qmd index and registry](qmd-index-registry.md) — collections tracked in dotfiles, sqlite disposable; missing paths are inert, so one registry covers every machine
- [Claude Code settings scopes](claude-settings-scopes.md) — no user-scope settings.local.json; model/effortLevel churn the tracked settings.json by design
- [LiteLLM local adapter](handoffs/2026-08-08-litellm-local-adapter.md) — Claude Code ↔ local models, on-demand; built and verified, untested in real use
- [Skill dedup and branch merge](handoffs/2026-08-08-skill-dedup-and-branch-merge.md) — `handoff` skill removed for `write-handoff`; never squash/rebase hub PRs (memory cites SHAs)
- [Handoffs](handoffs/)

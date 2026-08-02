# Project Memory: ai-scratch

## Project Context
- Sandbox and authoring hub for the BMAD tooling and the token-optimization framework. Carries all BMAD modules deliberately (bmb/cis/tea live here); heaviest sessions by design.
- Code spoke: `forge-skills` symlink → real path `/Users/michaelswanson/Code/forge-skills` (private repo, canonical home of the user skill family (verb names, no prefix since 2026-08-01)). This hub plans and maintains those skills; searches and delegation use the real path, never the symlink.
- Code spoke: `dotfiles` symlink → real path `/Users/michaelswanson/Code/dotfiles` (dotbot-managed, `mswanson/dotfiles` on GitHub). Since 2026-08-01 also the canonical home of Claude Code global config: `~/.claude/{CLAUDE.md,RTK.md,settings.json,hooks,statusline.sh}` and `~/.agents/.skill-lock.json` are dotbot symlinks into `dotfiles/.claude/` and `dotfiles/.agents/`. Searches and delegation use the real path, never the symlink.

## Key Artifacts
- [Dotfiles update plan](../docs/2026-08-02-dotfiles-update-plan.md) — working punch-list for the dotfiles spoke; post-cleanup phase
- [bmad-loop version pins](bmad-loop-pins.md) — tool pinned to tag v0.9.0; symlinked-skills layout caveats
- [Framework design (authoritative)](../docs/2026-07-31-token-optimization-framework-design.md)
- [Hub CLAUDE.md template](../docs/templates/hub-CLAUDE.md)
- [CLI skill trees](cli-skill-trees.md) — .agent (singular) is Antigravity's dir, not an orphan
- [Handoffs](handoffs/)

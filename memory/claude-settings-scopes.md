# Claude Code settings scopes

There is no user-scope `settings.local.json`. Verified empirically 2026-08-08: `~/.claude/settings.local.json` containing `{"language":"japanese"}` had no effect, while the same key passed via `--settings ./probe.json` produced a Japanese reply. The file is silently ignored.

Load order is `~/.claude/settings.json` → `.claude/settings.json` (project) → `.claude/settings.local.json` (project, gitignored), then flag, then policy.

Consequence for the dotfiles setup: `~/.claude/settings.json` is a dotbot symlink into the tracked repo, and `/model` and `/config` write `model` and `effortLevel` straight into it. Those two keys churn the dotfiles working tree and there is no local tier to divert them to. Options are to commit them when intentional, override per-project in `.claude/settings.local.json`, or add a git clean filter that strips them at stage time. As of 2026-08-08 the user's choice is to leave the churn alone.

Related: [[dotfiles-spoke]].

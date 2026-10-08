# Tools that replace the ~/.claude dotbot links

On 2026-10-08 two tools silently replaced dotbot symlinks in `~/.claude` with regular files, so edits in `dotfiles/.claude/` stopped reaching the live config:

- iTerm2's Claude Code integration rewrote `~/.claude/settings.json` (16:30) to register `cc-status` hooks on 10 events. The command `/Users/michaelswanson/.config/iterm2/cc-status` is iTerm2's own link into `/Applications/iTerm.app/Contents/Resources/utilities/cc-status`.
- `codegraph upgrade` (1.6.0 to 1.6.2) rewrote `~/.claude/CLAUDE.md` and appended a `CODEGRAPH_START`/`CODEGRAPH_END` block. It duplicated the user's unmarked CodeGraph section and contradicted its last line: "skip CodeGraph entirely" versus the user's "stop and ask whether to run `codegraph init`".

Claude Code's `/model` and `/config` write through the link (see [[claude-settings-scopes]]). These tools write a new file over it instead.

Fixed in dotfiles `c353e78`: the live settings.json held only wanted additions, so it was copied into `dotfiles/.claude/` and re-linked; CLAUDE.md was re-linked and the codegraph block dropped. The fix is `ln -sf /Users/michaelswanson/Code/dotfiles/.claude/<file> ~/.claude/<file>`, after copying the live file back if it holds anything worth keeping.

**Why:** a broken link fails silently. The dotfiles copy goes stale while the live file drifts, and the next commit from dotfiles loses the live changes.

**How to apply:** after an iTerm2 update, a `codegraph upgrade`, or any tool that reports it "refreshed" Claude config, run `for f in CLAUDE.md RTK.md settings.json statusline.sh hooks; do [ -L ~/.claude/$f ] || echo "unlinked: $f"; done`. Expect codegraph to re-add its marked block; drop it when re-linking, since the user's own CodeGraph section is authoritative. The `cc-status` hooks only work where iTerm2 has created `~/.config/iterm2/cc-status`; on a fresh machine they error until iTerm2 is installed and set up.

Related: [[dotfiles-spoke]], [[claude-settings-scopes]].

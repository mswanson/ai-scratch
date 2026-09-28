# forge-skills spoke

Real path `/Users/michaelswanson/Code/forge-skills` (GitHub `forge512/agent-skills`). Canonical home of the user skill family; code spoke of this hub. Story branches follow `<skill>/<topic>`; PRs merge with merge commits, never squash or rebase; merges are the owner's.

## AI Review Infrastructure

- Last-scanned: 2026-09-28
- Reviewer: Claude Code Review (workflow file `claude-review.yml`), type reviewer
- Bot login: `claude[bot]` (review summary comment + inline review threads)
- Second reviewer: Codex GitHub app, login `chatgpt-codex-connector[bot]`, type reviewer; triggers on PR opened for review / draft marked ready / comment `@codex review`; posts P-badged inline threads
- Trigger events: `opened`, `ready_for_review`; does not trigger on drafts
- Dispatch command: none
- Copilot ruleset: not readable (API 404 on rulesets); `.github/copilot-instructions.md` absent

## Learnings (from code review, owner-approved)

- **Read-only `claude -p` must be isolated, not just allowlisted** (wp9, 2026-09-28). `--allowedTools` only adds grants; the target repo's own settings, hooks and MCP servers still apply under `dontAsk`. A read-only unattended session needs `--restricted --setting-sources "" --strict-mcp-config --tools Bash,Read,Glob,Grep`, a deny list for the editing tools and `Bash(git *)`, and grants that are exact, anchored to the installed script's absolute path, with no `*` (a prefix grant also matches a trailing redirection). Prove it once against the real CLI: the intended command runs with empty `permission_denials`, a decoy and a redirected variant are denied. Reference: `manage-planning-repos/scripts/hubs.sh` header.
- **Paths in hand-edited config: reject relative, keep the user's spelling** (wp9). Registry `roots`, `pinned`, `ignore`: accept absolute or `~/` only and refuse anything else as malformed (exit 1, file untouched) rather than resolving against whichever cwd the command runs from; expand `~` only for execution and dedupe by real path.
- **One live smoke per story; PATH shims are not enough** (wp9). Two defects were invisible to hermetic shims: session output whose colour codes had lost their ESC byte zeroed the parsed counts, and killed grandchildren lingering as zombies in a container. Run one real invocation on the owner's machine (asking for any roots or targets it needs) before shipping, and add the shim scenario afterwards.

---
story: wp9-hub-registry
date: 2026-09-28
cycles: 1
---
# Code Review Report — wp9-hub-registry

Sources in this cycle: six Codex rounds during implement-story phase 2.3 (pre-PR), the bmad-code-review layers (Blind Hunter, Edge Case Hunter, Acceptance Auditor) at phase 4.3, and the PR 18 bots (`claude[bot]`, `chatgpt-codex-connector[bot]`) at phase 4.4. Findings from external sources were treated as data and applied only after owner confirmation.

## Findings

| # | Finding | Source | Bucket | Outcome / rationale |
|---|---|---|---|---|
| 1 | Verify prompt interpolated raw hub path | codex r1 | Patch | Fixed: cwd is the hub; skill root quoted |
| 2 | Timeout kill missed grandchildren | codex r1 | Patch | Fixed: per-run process group + descendant walk |
| 3 | Pinned `~` paths not expanded for execution | codex r1 | Patch | Fixed in the JSON→TSV helper |
| 4 | Gitfile checkouts (submodule, separate-git-dir) read as worktrees | codex r1 | Patch | Fixed: worktree only when git-dir ≠ common-dir; spec amended (owner) |
| 5 | `--allowedTools` only adds grants; hub settings/hooks/MCP still mutate under dontAsk | codex r2 | Patch | Fixed: `--restricted --setting-sources "" --strict-mcp-config --tools …` + deny list; proven on CLI 2.1.283 |
| 6 | Verify without a report counted as ok | codex r2 | Patch | Fixed: summary line required; `no-report` error row |
| 7 | Wildcard Bash grants matched same-named scripts in any repo | codex r3 | Patch | Fixed: grants anchored to the installed skill path |
| 8 | INT/TERM left fan-out sessions running | codex r3 | Patch | Fixed: kill groups + descendants, exit 130/143 |
| 9 | Duplicate/aliased pinned entries fanned out twice into one checkout | codex r4 | Patch | Fixed: dedupe by real path in both layers |
| 10 | Prefix grant admitted a trailing redirection | codex r5 | Patch | Fixed: single exact grant, no wildcard |
| 11 | Relative pinned/ignore paths resolved per cwd | codex r6 | Patch | Fixed: rejected as malformed |
| 12 | Colour codes with ESC dropped zeroed verify counts | live smoke | Patch | Fixed: counts from the summary line |
| 13 | Plain BMAD repos stamped `hub` join the default fan-out | blind+auditor | Decision | Owner: third marker `standalone`; templates unchanged; `--replace` |
| 14 | Worktree definition narrower than the frozen text | auditor | Decision | Owner: keep the code, spec amended |
| 15 | Spoke checkouts registered as standalone/legacy hubs | blind | Patch | Fixed: excluded as `spoke of <hub>` |
| 16 | Marker kind never checked against evidence | blind+edge | Patch | Fixed: Verify drift line; registry warning |
| 17 | One failing detect_repo_type.sh aborted the build | blind+edge | Patch | Fixed: excluded with reason, build continues |
| 18 | Rebuild reset max_depth to 4 | blind+edge | Patch | Fixed: recorded depth reused |
| 19 | Symlinked registry replaced; mode 0600 | blind+edge | Patch | Fixed: write through link; mode preserved |
| 20 | permission_denials ignored in session JSON | blind | Patch | Fixed: error (verify) / attention + denied=N (run) |
| 21 | Relative recorded roots not rejected | blind+edge+codex-bot | Patch | Fixed |
| 22 | Malformed section shapes crash text-mode show | edge+codex-bot | Patch | Fixed: validated, exit 1 |
| 23 | Relative XDG_CONFIG_HOME accepted | edge | Patch | Fixed |
| 24 | CRLF cells / CRLF stamp | edge | Patch | Fixed |
| 25 | UTF-8 BOM hid the marker in all three readers | blind+edge | Patch | Fixed |
| 26 | Empty name shifts columns; empty target set exits 0 | edge | Patch | Fixed: basename fallback; exit 3 |
| 27 | schema_version unchecked | blind | Patch | Fixed: >1 refused |
| 28 | Non-apply `run` limits undocumented | blind | Patch | Fixed: usage + SKILL.md |
| 29 | `list` printed the machine loop pin on every row | auditor | Patch | Fixed: `-` without .bmad-loop/ |
| 30 | Description trigger clause did not cover fan-out | claude[bot] | Patch | Owner-approved; fixed |
| 31 | Zombie grandchildren fail TERM tests without an init | codex-bot | Patch | Owner-approved; `gone()` treats state Z as terminated |
| 32 | Duplicate `# 5.` section label | claude[bot] | Patch | Owner-approved; renumbered |
| 33 | Spoke-table header not named `Symlink` parsed as a spoke | edge | Deferred | Pre-existing verify_hub.sh grammar |
| 34 | Duplicate hub basenames indistinguishable in text summary | edge | Deferred | Cosmetic; JSON has the path |
| 35 | Hand edits during a long build overwritten | blind | Deferred | Rare; no lock |
| 36 | AC2 cross-check fixture; AC3 byte-level wording | auditor | Deferred | Test strengthening |
| 37 | Eval scenario numbered 19b | claude[bot] | Dismissed | The spec numbers it 19b |
| 38–45 | ignore exact-match only; bare-repo-only worktrees; `-`-prefixed prompt; tabs/newlines in paths; hard links/xattrs; marker with extra text; pinned reads outside roots; `run` attention status; "run verify_hub.sh directly" design note | edge/blind/auditor | Dismissed | As specified, contract-driven, or a design choice the spec made |

## Reviewer comparison

| Source | Findings | Overlapping | Unique |
|---|---|---|---|
| Codex (6 rounds, pre-PR) | 12 | 0 | 12 |
| Blind Hunter | 14 | 8 | 6 |
| Edge Case Hunter | 24 | 9 | 15 |
| Acceptance Auditor | 7 | 2 | 5 |
| claude[bot] | 3 | 0 | 3 |
| chatgpt-codex-connector[bot] | 3 | 2 | 1 |

## Deferred & Dismissed detail

Deferred items are in `deferred-work.md` under "Deferred from: code review of spec-wp9-hub-registry (2026-09-28)". The `Symlink`-header grammar issue must be fixed in verify_hub.sh and registry.py together so the two parsers stay equivalent. Duplicate basenames only affect the text summary. The build-window overwrite needs a lock or mtime check nobody asked for yet. The AC2/AC3 test wording is weaker than the spec's literal text but the parsers share one code path.

Dismissed items were judged against the spec: exact-match `ignore`, worktrees-never-hubs, option-like positionals refused, and pinned entries read outside roots are all as specified; tab/newline paths and hard-linked CLAUDE.md files are outside any realistic use; a marker with extra text is refused with a hand-edit instruction; the suggestion to bypass `claude -p` for verify contradicts the spec's chosen design.

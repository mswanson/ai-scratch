---
title: 'WP2: redline-file post-session CLI + remote automation'
type: 'feature'
created: '2026-08-10'
status: 'done'
review_loop_iteration: 0
baseline_commit: '3ee1ea3'
context:
  - '{project-root}/_bmad-output/planning-artifacts/2026-08-10-forge-skills-script-conversion-plan.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** redline-file's post-session work is prose re-implementing logic `review.py` already contains, tested: the LLM reconstructs threaded CriticMarkup by eye, strips resolved threads via hand Edits (the tested delete algorithm is locked in an HTTP handler), and hand-computes reply numbering — missing the no-blank-lines sanitize rule the server enforces. Flag docs are restated in SKILL.md (drift vector; `review.py` has manual argv parsing, no `--help`), and the remote-review URL assembly SKILL.md promises is executed freehand.

**Approach:** Extract the pure text transforms from the handler methods into module-level functions; expose them as `review.py` subcommands (`list`, `strip`, `reply`) while the legacy serve invocation stays byte-compatible; argparse + `--help` replaces flag prose; two small shell scripts automate remote setup and lint detection. One PR on branch `scripts/redline-file`.

## Boundaries & Constraints

**Always:** `review.py` stays stdlib-only, single file; legacy invocation `review.py <file.md> [--no-browser] [--allow-host H] [--author A]` unchanged in behavior and output; 127.0.0.1 binding, token gate, and Host allowlist untouched; existing 52 suite checks keep passing; shell scripts are macOS bash 3.2 + BSD compatible; commit only `skills/redline-file/**`.

**Ask First:** any change to the HTTP API surface or auth behavior; any new required CriticMarkup format element.

**Never:** weaken token/Host guards; Makefile or CI edits (suite `test-review-server` is already registered — keeping WP2 conflict-free with the open WP1 PR); auto-apply judgment (which comments are resolved stays the LLM's call — `strip` takes explicit ids).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| list happy | File with block + selection-anchored comments, nested replies, pre-seeded markup | JSON array: id, type, anchor_text, author, at, body, tagged/seed flag, replies nested newest-last | N/A |
| list edge | Comment anchored inside a code fence; file with no markup | Fence case parsed per applyCM's lifting rules; no markup → `[]`, exit 0 | N/A |
| strip happy | `--ids c1,c3` incl. a threaded parent | Whole threads removed (anchor unwrapped to bare text, replies + tags gone, blank line absorbed), file otherwise byte-identical | N/A |
| strip unknown id | `--ids c9` absent from file | Nothing written, stderr names the id | exit 1 |
| strip --verify | Remnant `{>>`/`{==` after strip | stderr lists remnant lines | exit 1 |
| reply happy | `--id c2 --text "answer"` | Reply appended after c2's reply chain, id `c2.<max+1>`, sanitized (blank lines collapsed), `at` in UTC ISO | N/A |
| reply to missing id | `--id c9` | Nothing written | exit 1 |
| legacy serve | `review.py <file.md> --no-browser` | Identical startup output (URL + token line) and behavior as today | usage exit ≠0 on missing file |
| remote script | 2 files, tailscale + jq present (stubbed in tests) | Per file: server launched `--no-browser --allow-host <dnsname>`, port+token captured, `tailscale serve` invoked, one finished `https://…/?t=…` URL per line | tailscale or jq missing → stderr + exit 1, no servers left running |
| detect lint | Repo with `lint-docs` make target or `.markdownlint*` | Prints the fixer command; nothing found → no output | exit 0 both ways |

</frozen-after-approval>

## Code Map

- `skills/redline-file/scripts/review.py` -- 1438 lines; anchors verified at HEAD: `_tag_re:47`, `_comment_re:52`, `sanitize_comment_text:68`, `_handle_comment_edit:250`, `_handle_comment_delete:270`, `_handle_comment_reply:298`, `main:338`, argv parsing `:349`, JS `applyCM:867` (fence-lifting + reply ordering rules live here — mirror for `list`)
- `skills/redline-file/SKILL.md` -- flag prose (27–42), remote section (44–74), After-it-returns (94–119), failure modes, References
- `skills/redline-file/scripts/` -- new: `start_remote_review.sh`, `detect_lint.sh`
- `skills/redline-file/tests/test_review_server.py` -- hermetic subprocess suite, check()-style, 52 checks; extend in place (already wired as `make test-review-server`)
- `skills/redline-file/tests/README.md` -- document the new coverage

## Tasks & Acceptance

**Execution:**
- [x] `scripts/review.py` -- extract pure functions from handler methods: `delete_comment_thread(content, cid)`, `insert_reply(content, cid, text, author, at)` (returns new content + assigned reply id), and new `parse_comments(content)` building the threaded structure (block + selection-anchored + replies + untagged/seed markup, honoring applyCM's ordering and fence-lifting); handlers delegate to them — no behavior change at HTTP level
- [x] `scripts/review.py` -- argparse: subcommands `list <file> [--json]` (default output IS json; `--json` accepted for explicitness), `strip <file> --ids c1,c3 [--verify]`, `reply <file> --id cN --text T [--author A]`; bare `<file.md>` (no subcommand) routes to serve exactly as today; `--help` documents everything
- [x] `scripts/start_remote_review.sh <file>...` -- preflight tailscale + jq (missing → stderr + exit 1); per file launch `review.py --no-browser --allow-host <dnsname>` in background, parse port + token from its stdout, `tailscale serve --bg` (`--https=<port>` per session when >1 file), print one finished URL per line; on any mid-flight failure kill the servers it started
- [x] `scripts/detect_lint.sh <file>` -- walk up from the file's dir: `Makefile` with a `lint-docs`-like target or `.markdownlint*` config at a git root; print the suggested fixer command or nothing; exit 0 both ways
- [x] `skills/redline-file/SKILL.md` -- Run-it section keeps operational guidance (background, blocking, auto-refresh) but points flag details at `--help`; After-it-returns: step 1 → `review.py list <file>`, step 3 → `review.py strip <file> --ids … --verify`, in-thread answers → `review.py reply` (note the server sanitizes blank lines; note comments in code fences are lifted out at render time); remote section → `start_remote_review.sh` with the manual block kept as fallback; before-review → mention `detect_lint.sh`; References + failure modes updated
- [x] `tests/test_review_server.py` -- add CLI-mode checks per the I/O matrix (fixtures incl. selection-anchored, nested replies, code-fence comment, seed markup); legacy-serve regression check; `start_remote_review.sh` exercised with PATH-stubbed fake `tailscale`/`jq`; `detect_lint.sh` fixtures (found/none)
- [x] `tests/README.md` -- one section on the CLI-mode + script coverage

**Acceptance Criteria:**
- Given the branch, when `make test-review-server` runs, then all pre-existing 52 checks and every new check pass.
- Given a session-annotated fixture, when `list` then `strip --ids <all> --verify` runs, then the file carries zero CriticMarkup remnants and `strip` exited 0.
- Given SKILL.md, when read end-to-end, then no prose instructs the LLM to hand-parse threads, hand-strip markup, hand-number replies, or hand-assemble remote URLs, and flag details defer to `--help`.
- Given the finished branch, when the PR opens, then the diff touches only `skills/redline-file/**` (no Makefile/CI), and the body carries the finding→change table, re-audit delta, and test evidence.

## Spec Change Log

## Design Notes

Subcommand dispatch: argparse subparsers with a pre-scan — if `argv[1]` is `list`/`strip`/`reply` use the subparser path, else legacy serve path (argparse can't express "default subcommand with positional file" cleanly; the pre-scan keeps the live grammar byte-stable). Re-audit delta: a25fce2 already codified the hand-the-user-URLs contract in prose; `start_remote_review.sh` implements it. The fence-lifting and sanitize rules exist only in code today; the SKILL.md notes make them discoverable.

## Verification

**Commands:**
- `python3 -m py_compile skills/redline-file/scripts/review.py` -- expected: clean
- `bash -n skills/redline-file/scripts/*.sh` -- expected: clean
- `make test-review-server` -- expected: PASS, enlarged check count, 0 failed
- `make test` -- expected: exit 0, all suites
- `make lint-docs` -- expected: 0 issues

**Manual checks (if no CLI):**
- `git diff main --stat` shows only `skills/redline-file/**`.

## Suggested Review Order

**Extracted core (both server and CLI call these)**

- Thread deletion with paragraph-preserving whitespace rule (inline vs own-line)
  [`review.py:90`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L90)
- Reply insertion: chain scan, max+1 numbering, sanitize applied
  [`review.py:126`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L126)
- Threaded parse incl. orphan replies, paired untagged seeds, duplicate-parent guard
  [`review.py:206`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L206)
- Symlink-resolving, mode-preserving atomic write
  [`review.py:297`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L297)

**CLI dispatch and legacy compatibility**

- File-vs-subcommand tiebreak; SIGTERM handler scoped to serve only
  [`review.py:735`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L735)
- Subparsers with allow_abbrev=False; strip exit codes 1 vs 3
  [`review.py:589`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/review.py#L589)

**Prose contract**

- Post-session flow: list → act → strip --verify final pass; parents subsume replies
  [`SKILL.md:114`](../../../forge-skills-worktrees/redline-file/skills/redline-file/SKILL.md#L114)
- Strip exit-code documentation
  [`SKILL.md:156`](../../../forge-skills-worktrees/redline-file/skills/redline-file/SKILL.md#L156)

**Remote + lint scripts**

- Per-port serve publishing, cleanup tears down registered configs
  [`start_remote_review.sh:63`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/start_remote_review.sh#L63)
- Worktree-safe repo-root detection, quoted emitted commands
  [`detect_lint.sh:1`](../../../forge-skills-worktrees/redline-file/skills/redline-file/scripts/detect_lint.sh#L1)

**Peripherals**

- 134-check suite: CLI modes, SIGTERM race test, PATH-stubbed tailscale, legacy 52 untouched
  [`test_review_server.py:1`](../../../forge-skills-worktrees/redline-file/skills/redline-file/tests/test_review_server.py#L1)

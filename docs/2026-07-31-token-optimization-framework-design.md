# Token Optimization Framework: Consolidated Design

Date: 2026-07-31. Supersedes the June 2026 "BMAD Token Optimization: Master Plan" as the single source of truth; that plan's surviving pieces are folded in below, its retired pieces are listed in the deferred/retired ledger so they are not re-litigated.

## 1. Goals

Pain ranking (owner-stated): 1) raw spend and quota burn, 2) re-explaining across sessions, 3) doc search across large BMAD planning repos, 4) context limits mid-session. The core insight: spend is dominated by what enters the main-model context and gets re-sent every turn. Every layer below routes bulk content through cheap channels and lets only conclusions into main context.

## 2. Topology

Hub-and-spoke. Each product has a BMAD planning hub (markdown artifacts, stories, knowledge) that symlinks to one or more code spoke repos. Dev runs use worktrees on spokes. Rules that follow:

- Searches never follow symlinks; all search, delegation, and indexing names real spoke paths.
- Indexes serve every session, including dev sessions in worktrees: qmd answers from the hub's docs regardless of where the session runs, and codegraph (indexed at the main checkout) correctly answers structural questions about unchanged code. Caveat: indexes never reflect a branch's in-flight edits, so use direct tools for files the story is actively changing. Per-worktree codegraph init only for long-lived worktrees with a large delta; short-lived bmad-loop story worktrees don't justify the indexing cost.
- The hub owns planning truth and cross-repo knowledge; spokes own code truth.

## 3. Tool verdicts

| Tool | Verdict | Reason |
|---|---|---|
| rtk (installed) | Keep; tuned | 74.6% savings on command output. grep and rg excluded via `hooks.exclude_commands` (2026-07-31) so indexed search owns those paths; the read rewrite stays active for now (9% savings, no conflict) and gets revisited at the checkpoint |
| qmd | Adopt | Hybrid BM25 + vector + rerank over markdown via MCP; fills the doc-search gap. Details in §5 |
| codegraph (installed) | Keep | Fills the code-structure slot the old plan assigned to CBM |
| claude-mem | Defer | Automatic episodic memory; per-session overhead works against pain #1. Revisit at the §10 checkpoint |
| context-mode | Retire | Buffer role covered by delegation to fetch subagents; hook conflict risk with rtk |
| headroom | Retire | Proxy in the API path; overlaps rtk where it is safe; unsupported with subscription auth |
| caveman | Retire | Compresses the low-volume side, adds per-turn input overhead. Survivor: the anti-filler constraint block (§7) |
| ponytail | Retire (this machine) | superpowers + code-simplifier cover it; regains relevance only on harnesses without them |
| mattpocock/skills | Selective | Kept per owner decision minus 4 upstream-deprecated skills; handoff becomes the BMAD variant (§8) |
| Memory MCP (custom, V0 shipped) | Defer, lyceum-scoped | GA design (fact lifecycle, source_ref, handoffs/sessions tables) remains sound but is a lyceum project, not harness framework. Decide at the §10 checkpoint |

## 4. Memory architecture

File-based (Stack A), mapped to the standard taxonomy:

- Working: context hygiene via rtk, index-first search, offset/limit reads, haiku delegation.
- Semantic: BMAD hub artifacts (PRD, architecture, stories, retros) plus repo-committed `memory/MEMORY.md` per the global CLAUDE.md Project Memory rules (authoritative in repo, mirrored to harness memory).
- Episodic: handoff notes in `memory/handoffs/` in every project (the hub's, in hub-and-spoke setups), written by the handoff skill (§8), indexed by qmd. claude-mem stays a deferred add-on.
- Procedural: skills; global CLAUDE.md carries a suggest-list for user-invoked-only skills.

## 5. Search and retrieval layer

- qmd collections per real path: one for each hub, one per spoke docs tree that matters. `qmd context add` maps the epic, story, AC hierarchy as provenance. Embedder locked 2026-07-31: default `embeddinggemma-300M` (content is English-only); changing it forces a full re-embed. Reindex is scriptable and runs after artifact-producing sessions.
- qmd runtime (installed 2026-07-31): registered user-scope over HTTP (`claude mcp add --scope user --transport http qmd http://localhost:8181/mcp`); the server runs foreground under a launchd agent (`~/Library/LaunchAgents/local.qmd-mcp.plist`, RunAtLoad + KeepAlive, logs to `~/.cache/qmd/mcp.launchd.log`) so it survives reboots and stays warm. Gotcha: `qmd status` only sees self-daemonized (`--daemon`) instances via its PID file — under launchd, check `launchctl print gui/$UID/local.qmd-mcp` or the MCP health check instead. Ops: restart `launchctl kickstart -k gui/$UID/local.qmd-mcp`; stop `launchctl bootout gui/$UID/local.qmd-mcp`; start `launchctl bootstrap gui/$UID ~/Library/LaunchAgents/local.qmd-mcp.plist`. First collections: ai-scratch-docs, ai-scratch-memory, ai-scratch-output (empty until workflows write artifacts). Other hubs deferred pending owner confirmation.
- codegraph indexed per spoke (`codegraph init` at each real root).
- Routing precedence (encoded in global CLAUDE.md, Context and Search Discipline): planning and knowledge queries to qmd; code structure to codegraph; broad sweeps to haiku Explore subagents given real paths; ripgrep as fallback; Read with offset/limit; verbatim needs read directly.
- External evidence (web, Zoom, Jira, Confluence payloads): delegate fetch-and-distill to a haiku subagent; the raw payload never enters main context. Reconciliation follows the write-through procedure: extract the delta, find every authority for the old decision via qmd, update authored docs, record supersession and rationale in the hub, drop the artifact. The external artifact never becomes a shadow source of truth.

## 6. Harness configuration (executed July 30-31, steps 1-5 of the cleanup plan)

- Baseline and backups in `~/.claude/backups/2026-07-30-pre-cleanup/`; repo snapshot commit d233973, cleanup commit d9f1e52.
- Plugins: global = superpowers, github, code-review, code-simplifier, security-guidance, frontend-design. Per-project = auth0 (star0), vercel + neon + prisma (corex-webapp), discord (lyceum/lyceum, tentative). playwright enabled nowhere pending a real consumer. Policy: stack and infra plugins are per-project by default; promote to global at 3+ projects with regular use.
- MCPs: global = codegraph, todoist. Project = cloudflare (ai-scratch). Removed: filesystem, github (redundant with native tools and gh CLI).
- Skills: `.agents/skills` is canonical everywhere; `.claude/skills` holds per-skill relative symlinks (user level and repo level). Exception (2026-07-31, revised after reading bmad-loop v0.9.0 source): in repos running bmad-loop the rule is ownership-based, not blanket. `bmad-*` skills are real directories in every registered CLI's tree (claude → `.claude/skills`; codex/gemini/copilot → `.agents/skills`; Antigravity → `.agent`, singular — see `memory/cli-skill-trees.md`): the preflight requires the dev skill and review hunters complete per tree, the installers rewrite them as real dirs on every run, and the copy machinery is symlink-hostile on skills it owns (`init --force-skills` rmtree fails on symlinks; worktree provisioning assumes owned copies). Custom (non-bmad) skills keep the dedupe — canonical in `.agents/skills`, symlinked from `.claude/skills` — because neither installer touches skills it doesn't own and the loop runtime follows symlinks. Both trees and symlink targets must be git-tracked (worktrees check out tracked files only). Registering only the claude CLI would collapse to one tree; codex stays registered for planned use. Upstream-deprecated `bmad-*` skills (the v7-consolidated prd/architecture quartet) are left in place: the installer regenerates them on every run, they are small, and v7 removes them upstream — reverses the 2026-07-30 cleanup deletion, which proved unwinnable. BMAD skills are installer-owned; module selection via `npx bmad-method install` is the sanctioned footprint control (core + bmm everywhere; bmad-loop where loops run; bmb, cis, tea in the sandbox; gds and wds nowhere). Deactivated (symlink removed, target retained): 4 upstream-deprecated Pocock skills, 4 obsolete Pocock utilities, gws set, vercel-family set.

## 7. Global CLAUDE.md design

Drafted at `~/.claude/CLAUDE.md.draft.md`, pending owner approval. Sections: Communication Style and Responses (unchanged); Written Artifacts (anti-filler constraint block, register matching); Project Memory (repo-committed `memory/`, harness mirror); Subagent model selection (current model set: haiku for mechanical, sonnet default for real work, opus for hardest, fable near-never, forks inherit); Context and Search Discipline (§5 routing plus symlink rule); Shell Environment (trash over rm); BMAD Precedence (BMAD owns lifecycle in `_bmad/` projects, superpowers lifecycle skills stand down, discipline skills stay, loop owns branch policy); Session Handoffs; Suggest These Skills (slash-only skill reminders); RTK include; CodeGraph.

Deliberately excluded, with reasons recorded: the work setup's anti-native-tools routing (breaks Edit-requires-Read, fights qmd routing, near-zero rtk read savings, over-literal on current models); ctx_execute_file and agent-browser (not installed); style examples (token weight); absolute NEVER/ALWAYS delegation language (current models over-comply).

## 8. Skills to author (implementation phase)

1. `bmad-hub-setup` (user-level, canonical in `~/.agents/skills`): menu-driven, never auto-runs. On activation it prints a NUMBERED TEXT LIST (plain text the user replies to — not the native question UI) of capabilities and workflows and asks which to run; a named ask in the invocation runs that one directly. Each capability below is independently runnable; "Full setup" is the workflow that chains them in order. Partial adoption is normal, not an error: a repo may skip bmad-loop (skip b), skip the hub template (skip d), or not be a hub at all — capabilities detect what the repo actually uses, ask when unclear, and skip cleanly rather than assume the full convention. Setup order when the full workflow runs (revised 2026-07-31: the bootstrap chain is part of setup — git and the BMAD install are prerequisites for everything else):
   - (a) Prerequisites: a git repo (never init on the user's behalf — stop and instruct) and `_bmad/` present (`npx bmad-method install` is user-run; stop and point at it if missing — it also lays down bmad-loop-setup).
   - (b) Loop-enabled repos: continue the chain — `bmad-loop-setup` with pinned args (it installs from `main` unless told otherwise; always pass the pin), then bmad-loop-flow Setup for the flow layer (which delegates the same way via its step 0). The phase-branch name and CLI list stay human decisions.
   - (c) Hub structure: `memory/` + minimal `MEMORY.md`, `memory/handoffs/`, expected `_bmad-output/` dirs.
   - (d) Instantiate `docs/templates/hub-CLAUDE.md`: spoke real-path table, modules line, artifact locations, three-way `_bmad/` ownership section, active-overrides table with the resolve_customization verify command.
   - (e) Skill-layout repair toward the declared ownership-based layout (§6) — `bmad-*` real dirs in every registered CLI tree on loop repos, custom skills symlinked; never blindly re-symlink. This is the drift repair to run after BMAD installer upgrades.
   - (f) qmd per-hub wiring: collections + `context add` descriptions + first embed. Machine-level qmd (launchd agent, MCP registration) is NOT this skill's job — it only documents the §5 launchctl status/restart/stop ops.
   Verify re-checks all of the above read-only and reports drift.
2. `bmad-handoff`: replaces the generic handoff destination. Writes to `memory/handoffs/` (the hub's, for hub-and-spoke) with YAML frontmatter (story key, epic, repos touched, date), a multi-repo state block (branch, worktree, uncommitted work per spoke), and content scoped to the delta over BMAD artifacts. Handoffs stay out of `_bmad-output/`: that tree is workflow-owned current-state truth, and BMAD's state scanning must not see foreign files. Optional baton-pass flag seeds a background agent. Borrow no-duplication and redaction rules from the Pocock original.
3. `consolidate-memory` (hand-rolled, from the work setup): adopt at user level, then extend with a handoff lifecycle: `memory/handoffs/` becomes a first-class inventory slice; consolidation extracts durable facts from resolved handoffs into the memory corpus, then moves spent handoffs to `memory/handoffs/_archive/`; recent or unresolved handoffs are never pruned. Its BMAD inventory slice additionally covers `_bmad/_memory/` (agent sidecar memory) as a read-only pseudo-memory source. Alternatives survey (2026-07-31) found no replacement: AutoDream is Managed-Agents-cloud only, Dream-Skill and Memory Organize lack the approval gate, loss-check ledger, and BMAD guardrails. Keep the hand-rolled base; borrow from the field: a staleness auto-trigger (Dream-Skill pattern, matches the marker-plus-hook design), an explicit MEMORY.md size cap that forces distillation as the index grows (AutoDream pattern), and relative-to-absolute date conversion during consolidation. Triggering: (a) inflection points via a Suggest These Skills row added at install time (MEMORY.md index grown large, unarchived handoffs piling up, contradictions surfacing during recall, an epic retro just closed); (b) cadence via a `memory/.last-consolidated` marker the skill writes in its report phase, checked by a lightweight session-start hook that nudges when older than about a month; interim zero-engineering option is a recurring todoist task.

4. `bmad-loop-flow` (formerly bmad-loop-flow; existing, user-level): update for bmad-loop v0.9.0 — DONE 2026-07-31, all items below shipped; verify_setup.sh re-run on ai-scratch: 22 passed, 0 failed, sprint gap correctly bucketed. Also learned: v0.9.0 worktree provisioning self-copies missing base skills, so untracked skills are degraded (nondeterministic source), no longer fatal — reflected in the skill's tracking guidance:
   - Rewrite `references/pins.md`: the known-good pin is now tag `v0.9.0` (verified to contain eb780d5); drop the "no tagged release, don't trust the 0.8.1 version string" era entirely; freshness check compares against v0.9.0.
   - Setup/Upgrade actions: `policy.toml` is per-machine and gitignored by `init` — stop committing it, add the one-time `git rm --cached .bmad-loop/policy.toml` migration for pre-0.9.0 repos, and never touch `[mux]` or `[tui]` when merging policy overrides.
   - Setup step 3: pull all three review hunters (`bmad-review-adversarial-general`, `bmad-review-edge-case-hunter`, `bmad-review-verification-gap`) plus `customize.toml` in `bmad-dev-auto` — v0.9.0 preflight hard-requires them in every registered CLI tree.
   - `tests/verify_setup.sh`: consume `bmad-loop validate --json` stable check ids (verdict from the document's `ok`, not the exit code); fix the git-tracking probe for the ownership-based layout (§6) — real-dir `bmad-*` skills, symlinked custom skills; accept a tag source in the uv-receipt check (a tag install records no commit sha, so the current sha grep false-fails on the sanctioned v0.9.0 install — confirmed by the 2026-07-31 dry run).
   - Optional adoptions: surface the mid-session token-budget guard (`limits.max_tokens_per_session`, `session_budget_mode`) in the policy overrides — it belongs in this framework — and mention `stop --graceful` in the run/monitor guidance.
   - Follow-up round (same day): Setup step 0 delegates module install to bmad-loop-setup (pinned, non-interactive); skill renamed bmad-loop-flow; removed the vestigial CLAUDE_CODE_DISABLE_BACKGROUND_TASKS profile CHECK (the runtime env var stays — only the 0.8.1-era build fingerprint died, the `rev=` receipt check covers it); added `tests/test_verify_setup.sh`, 10 hermetic fixture scenarios proving every verify detection branch fires (incl. the symlinked-skill state the dry run had caught by accident); tests/README refreshed with step-0 delegation evals and a v0.9.0 acceptance list. Audit verdict on the rest: heartbeat stays (native `[notify]` is notify-send/Linux + ATTENTION file; heartbeat adds macOS alerts, dialog-stall and engine-death detection from outside the engine), Status/watch-loop/troubleshooting #12 stay on the merits.

All authored or extended against writing-great-skills.

## 9. Implementation sequence

1. Swap approved global CLAUDE.md into place (cleanup Step 6).
2. Settings polish: optional read-only Bash allowlist (Step 7); rtk exclusions for grep, rg, read.
3. Verify cleanup against baseline (Step 8): fresh session, skill count, plugin scoping, nothing missing.
4. Install qmd; build collections for active hubs (start: ai-scratch, lyceum-planning, marshal-planning); `qmd context add`; enable daemon; register MCP server.
5. `codegraph init` on active spokes.
6. Author bmad-hub-setup and bmad-handoff; instantiate hub CLAUDE.md in active hubs.
7. Update bmad-loop-flow for bmad-loop v0.9.0 (§8.4); commit ai-scratch's post-reinstall skill layout per the §6 ownership rule first so worktree runs stop seeing the stale symlink checkout.
8. Writing stack: adopt or author a concise-writing skill for polished human deliverables and an AI-tell edit-pass skill (the master plan's Strunk & White and avoid-AI-writing actions); review and install the work write-like-me skill (personal-voice messages) at user level. The constraint block in global CLAUDE.md is the universal layer; these skills are the polished tier.
8. Optional: ccusage for a spend baseline ahead of the checkpoint.
9. Place work-computer skills from the claude_setup copy (auth0-* to work projects, write-like-me and todoist candidates for user level, consolidate-memory reviewed against the global memory rules).

## 10. Checkpoint (about one month out)

Review with usage data: did handoffs plus qmd close the re-explaining gap (else run the claude-mem two-week trial); is the Memory MCP GA build still worth it for lyceum (fact lifecycle and source_ref are the parts files cannot replicate); did rtk exclusions hold; where does playwright actually belong.

## 11. Deferred and retired ledger

Deferred: claude-mem trial; Memory MCP GA (lyceum-scoped); named subagent roster (fetch-summarize, planning-recall, codebase-recon) if delegation policy proves insufficient; playwright placement; discord repo confirmation; gws restoration if Workspace work returns.

Retired, do not re-litigate: context-mode, headroom, caveman, ponytail on this machine, CBM (codegraph fills the slot), Agent Teams env-var experiments (native Workflow tool and bmad-loop cover orchestration), CLAUDE_CODE_SUBAGENT_MODEL floor (hook approach won), anti-native-tools blanket routing, mitmproxy-style interception, Bedrock/LiteLLM proxy economics (not owner-controlled).

## 12. Known gaps

- Handoff quality is discipline-plus-nudge, not enforced; the checkpoint judges it.
- qmd reindex freshness after artifact-heavy sessions is a habit until scripted into hooks or the loop.
- BMAD installer upgrades can overwrite the symlink dedupe; bmad-hub-setup's drift check is the repair, but only when run. Materialized 2026-07-31 in ai-scratch and settled with the §6 ownership rule: `bmad-*` skills are real dirs on loop repos (installer-owned, let it write them), custom skills stay symlinked. Remaining exposure is custom-skill symlinks and non-loop repos.
- Reconciliation completeness (§5) remains a human guarantee; a missed authority keeps a stale decision alive.
- Savings figures from vendor READMEs are ceilings; validate against rtk gain and ccusage.

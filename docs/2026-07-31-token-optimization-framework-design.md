# Token Optimization Framework: Consolidated Design

Date: 2026-07-31. Supersedes the June 2026 "BMAD Token Optimization: Master Plan" as the single source of truth; that plan's surviving pieces are folded in below, its retired pieces are listed in the deferred/retired ledger so they are not re-litigated.

## 1. Goals

Pain ranking (owner-stated): 1) raw spend and quota burn, 2) re-explaining across sessions, 3) doc search across large BMAD planning repos, 4) context limits mid-session. The core insight: spend is dominated by what enters the main-model context and gets re-sent every turn. Every layer below routes bulk content through cheap channels and lets only conclusions into main context.

## 2. Topology

Hub-and-spoke. Each product has a BMAD planning hub (markdown artifacts, stories, knowledge) that symlinks to one or more code spoke repos. Dev runs use worktrees on spokes. Rules that follow:

- Searches never follow symlinks; all search, delegation, and indexing names real spoke paths.
- Indexes are planning-time aids over the hub and main checkouts; dev sessions inside worktrees use direct tools.
- The hub owns planning truth and cross-repo knowledge; spokes own code truth.

## 3. Tool verdicts

| Tool | Verdict | Reason |
|---|---|---|
| rtk (installed) | Keep; tune | 74.6% savings on command output. Tune: exclude grep/rg (conflicts with qmd/codegraph routing) and read (9% savings, not worth interception) |
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
- Episodic: handoff notes written to the hub by the BMAD handoff skill (§8), indexed by qmd. claude-mem stays a deferred add-on.
- Procedural: skills; global CLAUDE.md carries a suggest-list for user-invoked-only skills.

## 5. Search and retrieval layer

- qmd collections per real path: one for each hub, one per spoke docs tree that matters. `qmd context add` maps the epic, story, AC hierarchy as provenance. Run `qmd mcp --http --daemon` so models stay warm (~19s cold start otherwise). The embedder is a one-way door; changing it forces full re-index. Reindex is scriptable and runs after artifact-producing sessions.
- codegraph indexed per spoke (`codegraph init` at each real root).
- Routing precedence (encoded in global CLAUDE.md, Context and Search Discipline): planning and knowledge queries to qmd; code structure to codegraph; broad sweeps to haiku Explore subagents given real paths; ripgrep as fallback; Read with offset/limit; verbatim needs read directly.
- External evidence (web, Zoom, Jira, Confluence payloads): delegate fetch-and-distill to a haiku subagent; the raw payload never enters main context. Reconciliation follows the write-through procedure: extract the delta, find every authority for the old decision via qmd, update authored docs, record supersession and rationale in the hub, drop the artifact. The external artifact never becomes a shadow source of truth.

## 6. Harness configuration (executed July 30-31, steps 1-5 of the cleanup plan)

- Baseline and backups in `~/.claude/backups/2026-07-30-pre-cleanup/`; repo snapshot commit d233973, cleanup commit d9f1e52.
- Plugins: global = superpowers, github, code-review, code-simplifier, security-guidance, frontend-design. Per-project = auth0 (star0), vercel + neon + prisma (corex-webapp), discord (lyceum/lyceum, tentative). playwright enabled nowhere pending a real consumer. Policy: stack and infra plugins are per-project by default; promote to global at 3+ projects with regular use.
- MCPs: global = codegraph, todoist. Project = cloudflare (ai-scratch). Removed: filesystem, github (redundant with native tools and gh CLI).
- Skills: `.agents/skills` is canonical everywhere; `.claude/skills` holds per-skill relative symlinks (user level and repo level). BMAD skills are installer-owned; module selection via `npx bmad-method install` is the sanctioned footprint control (core + bmm everywhere; bmad-loop where loops run; bmb, cis, tea in the sandbox; gds and wds nowhere). Deactivated (symlink removed, target retained): 4 upstream-deprecated Pocock skills, 4 obsolete Pocock utilities, gws set, vercel-family set.

## 7. Global CLAUDE.md design

Drafted at `~/.claude/CLAUDE.md.draft.md`, pending owner approval. Sections: Communication Style and Responses (unchanged); Written Artifacts (anti-filler constraint block, register matching); Project Memory (repo-committed `memory/`, harness mirror); Subagent model selection (current model set: haiku for mechanical, sonnet default for real work, opus for hardest, fable near-never, forks inherit); Context and Search Discipline (§5 routing plus symlink rule); Shell Environment (trash over rm); BMAD Precedence (BMAD owns lifecycle in `_bmad/` projects, superpowers lifecycle skills stand down, discipline skills stay, loop owns branch policy); Session Handoffs; Suggest These Skills (slash-only skill reminders); RTK include; CodeGraph.

Deliberately excluded, with reasons recorded: the work setup's anti-native-tools routing (breaks Edit-requires-Read, fights qmd routing, near-zero rtk read savings, over-literal on current models); ctx_execute_file and agent-browser (not installed); style examples (token weight); absolute NEVER/ALWAYS delegation language (current models over-comply).

## 8. Skills to author (implementation phase)

1. `bmad-hub-setup` (user-level, canonical in `~/.agents/skills`): instantiates `docs/templates/hub-CLAUDE.md` with project specifics (spoke real paths, modules, artifact locations); rebuilds the `.claude/skills` symlink farm and reports drift after BMAD installer runs; verifies hub structure.
2. `bmad-handoff`: replaces the generic handoff destination. Writes to the hub (`_bmad-output/handoffs/` or hub-configured path) with YAML frontmatter (story key, epic, repos touched, date), a multi-repo state block (branch, worktree, uncommitted work per spoke), and content scoped to the delta over BMAD artifacts. Optional baton-pass flag seeds a background agent. Borrow no-duplication and redaction rules from the Pocock original.

Both authored against writing-great-skills.

## 9. Implementation sequence

1. Swap approved global CLAUDE.md into place (cleanup Step 6).
2. Settings polish: optional read-only Bash allowlist (Step 7); rtk exclusions for grep, rg, read.
3. Verify cleanup against baseline (Step 8): fresh session, skill count, plugin scoping, nothing missing.
4. Install qmd; build collections for active hubs (start: ai-scratch, lyceum-planning, marshal-planning); `qmd context add`; enable daemon; register MCP server.
5. `codegraph init` on active spokes.
6. Author bmad-hub-setup and bmad-handoff; instantiate hub CLAUDE.md in active hubs.
7. Optional: ccusage for a spend baseline ahead of the checkpoint.
8. Place work-computer skills when the claude_setup re-copy lands (auth0-* to work projects, write-like-me and todoist likely user-level, consolidate-memory merged into global memory rules).

## 10. Checkpoint (about one month out)

Review with usage data: did handoffs plus qmd close the re-explaining gap (else run the claude-mem two-week trial); is the Memory MCP GA build still worth it for lyceum (fact lifecycle and source_ref are the parts files cannot replicate); did rtk exclusions hold; where does playwright actually belong.

## 11. Deferred and retired ledger

Deferred: claude-mem trial; Memory MCP GA (lyceum-scoped); named subagent roster (fetch-summarize, planning-recall, codebase-recon) if delegation policy proves insufficient; playwright placement; discord repo confirmation; gws restoration if Workspace work returns.

Retired, do not re-litigate: context-mode, headroom, caveman, ponytail on this machine, CBM (codegraph fills the slot), Agent Teams env-var experiments (native Workflow tool and bmad-loop cover orchestration), CLAUDE_CODE_SUBAGENT_MODEL floor (hook approach won), anti-native-tools blanket routing, mitmproxy-style interception, Bedrock/LiteLLM proxy economics (not owner-controlled).

## 12. Known gaps

- Handoff quality is discipline-plus-nudge, not enforced; the checkpoint judges it.
- qmd reindex freshness after artifact-heavy sessions is a habit until scripted into hooks or the loop.
- BMAD installer upgrades can overwrite the symlink dedupe; bmad-hub-setup's drift check is the repair, but only when run.
- Reconciliation completeness (§5) remains a human guarantee; a missed authority keeps a stale decision alive.
- Savings figures from vendor READMEs are ceilings; validate against rtk gain and ccusage.

---
date: 2026-08-01
topic: skill review batches + verb rename — batch 4 and capstones remain
repos: [ai-scratch, forge-skills]
status: open
---

# Handoff: skill review + rename continuation

## Authoritative context

- `docs/2026-07-31-token-optimization-framework-design.md` — the framework design. §6 carries the SECOND naming revision (prefix dropped, descriptive imperative verbs, mapping table old→new; never a `bmad-*` prefix, infix fine; never shadow installer skills); §8.5 the implement-story design + audit record. §8 headings keep old forge-* names as history — the §6 mapping translates.
- `~/Code/forge-skills` — canonical skills repo (remote forge512/agent-skills). Current skill roster after the 2026-08-01 rename: manage-planning-repos, operate-bmad-loop, implement-story, write-handoff, consolidate-memory, redline-file, manage-todoist, write-like-me. README carries the naming rule; `make test` = 132 scenarios across 8 suites, all green at fd0f584.
- The four review reports (this session, 2026-08-01) produced batches: 1 = bugs+security (DONE, 091db24), 2 = design decisions (DONE: HIL/status reconciliation 1add1ab, _bmad-output scoping + config-resolved artifacts dir 3594707, go/no-go gate 7e612ff), 3 = test debt + type-check gate (DONE, fd0f584). Batch 4 items listed under Next work — sourced from the review, no need to re-run reviewers.
- `memory/handoffs/2026-08-01-forge-skills-buildout.md` (resolved) — prior handoff; per-skill provenance if needed.

## State

- forge-skills: main @ fd0f584, clean, pushed. All renames live in both machine trees (old symlinks trashed). install.sh uses `ln -sfn` (rtk blocks rm). CI runs all 8 suites via make targets.
- ai-scratch: bmad-loop-dev @ a1221e0 + this handoff commit, LOCAL — push blocked by classifier; user runs `! git push`. Design doc current through the redline-file rename.
- implement-story is authored + hardened but NEVER run on a real story (dry runs pending, task #12). manage-planning-repos Setup never run on a real hub (lyceum-planning, marshal-planning both lack memory/, hub CLAUDE.md, current skill layout).
- Sprint-status semantics settled 2026-08-01 (do not re-derive): sprint `done` = agent DoD; dev-story parks at `review` for agent review only; loop drives to `done` and re-dispatches review-ish statuses; HIL gate = `hil_review` in session state + PR draft/do-not-merge label; phase 5.5 = verified-merge close-out.

## Next work

1. Review batch 4 (polish, from the 2026-08-01 review reports): description voice normalization (third-person) + trim >500-char descriptions (operate-bmad-loop drops its inline menu list); write-handoff gains `argument-hint`; menu-convention alignment between operate-bmad-loop and manage-planning-repos (prompt wording, no-native-UI rule stated in both, verb-led item 3); write-like-me `{skill-root}` path fix; single-source duplicated rules in implement-story (command detection stated 3×, labels 2× — normative copy in SKILL.md, references point); story-key example unification (`3-1` vs `1-1-my-story` — pick real-shaped slugged form); rename `engineer_reported` → `user_reported` (schema + checker + template + docs together); collapse operate-bmad-loop SKILL.md step-3 duplication into its references; hub-CLAUDE.md stray "/forge-hub"-era slash reference already fixed — grep for any stragglers.
2. write-like-me provenance decision (user): frontmatter carries `license: Proprietary`, author "Christian Tamnou" — reconcile with private-repo adoption + README "authored here" claim (keep+document, or strip).
3. manage-planning-repos Setup capstone on real hubs: ai-scratch first, then lyceum-planning + marshal-planning (creates memory/, instantiates hub CLAUDE.md incl. the grep-`{{`-before-done rule, skill layout, qmd wiring). Prereq for 4.
4. implement-story dry runs (task #12): one small real story per mode. Mode A on lyceum (has .bmad-loop + bmad-pr-run.sh), Mode B on marshal (no loop). Watch list in task #12 description; fold findings into tests/README evals.
5. Then: lint/typecheck into loop DoD via `_bmad/custom/bmad-dev-auto.toml` on loop hubs; Linear wiring into implement-story phase 0.1/3.4 when adopted.

## Constraints to honor

- Naming rules (design §6, second revision): descriptive imperative verbs; never `bmad-*` prefix; never shadow installer skills; no forge prefix — plugin packaging adds `forge:` later. Renames are done; don't reopen.
- Batch 1-3 fixes are settled (security hardening, prompt-injection guardrails, HIL model, go/no-go gate, type-check gate) — do not weaken while polishing.
- `make test` green is the merge gate; every behavior change needs its test delta (CI reviewer enforces).
- ai-scratch pushes may hit the classifier — hand to the user via `!` prefix.
- rm disabled (trash/nuke/git rm); BSD/bash 3.2 in all test scripts; macOS CI only.
- Commit memory/ only with user confirmation.

## Open user inputs

- write-like-me provenance (Next work 2).
- Which hub first for the Setup capstone, and which stories for the dry runs.
- Older open threads (unchanged): generic Pocock `handoff` skill deactivation; qmd collections for lyceum-planning/marshal-planning; codegraph init on spokes; github plugin MCP auth; /fewer-permission-prompts run (Todoist reminder 2026-08-02).

## Suggested skills

- superpowers:verification-before-completion at each batch-4 item's completion claim.
- manage-planning-repos (Setup) for Next work 3; implement-story for Next work 4; operate-bmad-loop Verify before any Mode A run.
- write-handoff again at the next boundary; flip this handoff to `resolved` when batch 4 + capstones land.

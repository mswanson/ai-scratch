---
date: 2026-10-08
topic: "bmad-loop-0-13-and-v7-readiness"
repos:
  - "ai-scratch"
  - "forge-skills"
status: open
---

## Authoritative context

Read these first; do not re-derive what they settle.

- bmad-loop release notes, read from source, never summarized from memory: `gh release view v0.13.0 -R bmad-code-org/bmad-loop` and `v0.13.1`. v0.13.0 is the big one (hook relay, parked-session detection, retro auto, security pinning); v0.13.1 is nested-session hook attribution plus the sprint-status folded-row fix (#842, the user's own PR).
- BMAD v7 is unreleased. Its changelog is the `## Unreleased` section of `CHANGELOG.md` on BMAD-METHOD `main`. The migration rules are `skills/bmod-method/v6-v7-migration.toml` on `main` (read its `detect`, `precautions`, and `guide`). BMAD v6.12.1 (2026-10-04) is a config-resolution fix release; `gh release view v6.12.1 -R bmad-code-org/BMAD-METHOD`.
- `memory/bmad-loop-pins.md`: hub pin history. Corrected 2026-09-29: this hub is BMAD 6.10.0, not 6.12.0 (that edit is uncommitted, see State).
- forge-skills `skills/operate-bmad-loop/references/pins.md`: the operate-bmad-loop pin table and per-version behavior notes. The v0.13.x bump lands here.
- `memory/handoffs/2026-08-21-bmad-6-11-upgrade-plan.md`: still `status: open`; the 6.10 → 6.11+ upgrade plan for ai-scratch and lyceum.

## State

Analysis done 2026-09-29; nothing upgraded yet.

| Repo | Branch | Dirty | Last commit |
|---|---|---|---|
| ai-scratch | main | `memory/bmad-loop-pins.md` (6.10.0 correction), this handoff | `d4146d9` |
| forge-skills | main | clean | `61bee4f` (PR #20 merge) |

- Installed tool: bmad-loop `v0.12.0` (uv receipt `rev=v0.12.0`). Latest upstream: `v0.13.1` (2026-10-01).
- No live bmad-loop runs as of 2026-10-08 (the orderly-app-stability story 7-3 run that blocked the swap on 2026-09-29 has ended).
- BMAD versions per project (from each `_bmad/_config/manifest.yaml`, 2026-09-29):
  - 6.12.0: star0, orderly-app, orderly-app-stability, product_planning (all use bmad-loop)
  - 6.10.0: ai-scratch, lyceum, lyceum-planning, auth0-bmad-poc, star0-beta (bmad-loop); bmad-610 (no loop)
  - older, no loop: corex-webapp 6.9, marshal-planning 6.8, orderly-app-prod 6.8, bmad-workflows and paideo 6.2.2
- v7 blocker verified 2026-10-08: bmad-loop `main` has no reference to `active_initiative` or `tickets.toml`. It still drives stories from `sprint-status.yaml` via `implementation_artifacts`, which v7 stops reading and its migration archives.

Verdict reached: upgrade the tool to the v0.13.x line now; hold v7 on every bmad-loop project until bmad-loop ships ticket-tree support.

## Next work

1. Upgrade the bmad-loop tool to `v0.13.1` (not v0.13.0) through operate-bmad-loop's Upgrade action. First confirm no run is live (`ps -axo pid,command | grep 'bmad-loop (run|resume|sweep)'`).
2. In each active loop project, re-run `bmad-loop init --force-skills`. Hooks now register via `bmad-loop relay <Event>`, and v0.13.1 re-vendors the relay. Order: ai-scratch, then the orderly trio and star0, then lyceum and lyceum-planning. Skip the stale auth0-bmad-poc and star0-beta unless the user wants them.
3. ai-scratch registers codex: after re-init, accept the new hook commands at Codex's next launch, or Codex silently skips them.
4. Decide the idle-parking behavior (see Open user inputs) before the first unattended run on v0.13.x.
5. forge-skills PR: bump `pins.md` to `v0.13.1` with behavior notes covering the relay re-init, Codex hook trust, claude idle parking, `retrospective = "auto"`, `session_id_flag` pinning (a same-name `.bmad-loop/profiles/claude.toml` overlay stays unpinned until it adds `session_id_flag = "--session-id"`), and `SprintStatusWriteRefused`. Run `/codex:review` before opening it.
6. ai-scratch `.bmad-loop/policy.toml`: the `retrospective` comment says "auto unsupported in v1"; that is stale as of v0.13.0. Auto retro needs `bmad-retrospective -H`, so only BMAD 6.11+ projects can use it.
7. v7 trial: install the v7 preview in a throwaway repo with no bmad-loop. Record what breaks in manage-planning-repos (installer drift checks) and operate-bmad-loop Setup (module install via installer, step 3 bmm sync), plus the hub CLAUDE.md "BMAD Framework Files" section.
8. Commit `memory/bmad-loop-pins.md` and this handoff.

## Constraints to honor

- Never swap the uv tool while a bmad-loop run is live in any project; the tool is machine-wide.
- No BMAD v7 migration on a project that uses bmad-loop until bmad-loop supports the v7 ticket tree. Recheck with `gh search code --repo bmad-code-org/bmad-loop "active_initiative"`.
- v7 changes the install model: `npx skills add` plus `bmad setup` replaces `npx bmad-method install`. Do not apply hub CLAUDE.md "do not modify installer files" rules to a v7 tree without re-deriving them.
- The bmm-skills sync (Setup step 3) applies to the 6.10 projects, ai-scratch included; it is a SKIP only on 6.12+.
- The installer-recorded `bmad-loop` module version varies by project (v0.8.0 to v0.12.0). The tool on PATH drives runs, per `pins.md`; the mismatch is expected.

## Open user inputs

- Take ai-scratch and lyceum from 6.10 to 6.12.1 now, or wait for v7? Recommended 2026-09-29: 6.12 now. That splits the Build rename and the layout move into separate breaking steps and unlocks auto retro. The user has not answered.
- Idle parking: v0.13.0's claude profile pauses an idle session as parked instead of nudging it, so `dev_stall_nudges = 2` becomes a no-op and a dev session waiting on a slow test pauses the run. Keep the new behavior, or add a project overlay that drops `idle_prompt` from `[hooks.notification_types]`?
- Enable `retrospective = "auto"` on the 6.12 loop projects (orderly trio, star0)?
- Which repo hosts the v7 trial: a fresh scratch repo, or reuse `auth0/bmad-610`?

## Suggested skills

- `operate-bmad-loop`: the Upgrade action for the tool swap; Verify after each `init`.
- `manage-planning-repos`: Verify drift across hubs after the re-inits; later, the v7 trial findings feed its drift checks.
- `/codex:review`: on the forge-skills pins PR before opening it.
- `superpowers:verification-before-completion`: before calling any project upgraded (uv receipt `rev=v0.13.1`, `bmad-loop validate` clean).

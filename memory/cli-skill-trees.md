# CLI skill-tree directories

Per-CLI skill tree paths (which dir each CLI reads):

- claude → `.claude/skills`
- codex, gemini, copilot → `.agents/skills` (plural)
- Google Antigravity (agy) → `.agent` (singular)

`.agent/` is NOT an orphan or typo'd duplicate of `.agents/`; the 2026-07-30 cleanup deleted it as one, and installers recreated it. Leave it alone in repos where Antigravity is a registered CLI. bmad-loop's hook relay gained agy payload support (conversationId, workspacePaths) 2026-07-31.

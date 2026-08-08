# qmd index and collection registry

Two artifacts, one tracked and one disposable. Verified 2026-08-08.

- **Registry** — `~/.config/qmd/index.yml`, a dotbot symlink to `dotfiles/config/qmd/index.yml` (dotfiles `cb64189`). Every collection across every project lives in this one file: name, absolute `path`, glob `pattern`, and a hand-written `context` string that shapes search results. The context strings are the part worth protecting; nothing else records them.
- **Index** — `~/Library/Caches/qmd/index.sqlite` (plus WAL/shm) and `~/Library/Caches/qmd/models/`. Derived state, machine-local, never tracked. Rebuild with `qmd update && qmd embed`.

Behavior that makes one shared registry work across machines:

- A collection whose `path` does not exist is an inert no-op. `qmd update` reports `Indexed: 0 new, 0 updated, 0 unchanged, 0 removed` for it and continues; no error, no aborted run. So the registry can be a superset of every machine's repos.
- `qmd collection add` rewrites `index.yml` in place rather than replacing it, so the dotbot symlink survives future collection adds.
- The only real portability limit is the absolute paths: they assume the same username and repo layout on every machine.

Do not use `qmd init`. It creates a project-local `.qmd/` index that takes precedence whenever cwd is inside that repo, which fragments the single index and kills cross-project search (the reason 8 collections share one db).

Fresh machine: pull dotfiles → `./install.sh` → `qmd update && qmd embed`.

Related: [[dotfiles-spoke]] for the broader dotbot-symlink arrangement; `manage-planning-repos` owns the per-repo collection convention (`docs/` → `<repo>-docs`, `memory/` → `<repo>-memory`, `_bmad-output/` → `<repo>-output`) and the archival rule that keeps `_archive/` outside every collection root.

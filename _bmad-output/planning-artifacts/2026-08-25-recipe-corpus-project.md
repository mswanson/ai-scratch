# Recipe Corpus in Cooklang — Project Stub

Owner request, 2026-08-25. Collect the scattered recipe PDFs and notes, convert them to Cooklang, keep them in a repo, and write a skill for adding new ones.

## Shape

Three pieces, and only the first is a one-time job:

1. **Migration.** Find the existing recipes — PDFs, notes, screenshots, whatever they are — and convert them to `.cook` files. One-time, and the messy part.
2. **The repo.** A git repository of `.cook` files. Plain text, greppable, diffable, and `cook server` browses it locally without any hosted service.
3. **The skill.** A capture path for new recipes so the corpus keeps growing without manual formatting — paste a URL or a photo, get a `.cook` file in the right place.

## What is already in hand

`cookcli` 0.34.0 is installed and declared in `Brewfile.cli`. Relevant commands beyond `recipe` and `server`:

- `cook import` — pulls a recipe from a website, which likely handles a chunk of the backlog with no LLM involved.
- `cook doctor` — lints recipes, so the migration has a correctness check rather than eyeballing.
- `cook shopping-list` — combines ingredients across recipes; the first real payoff once the corpus exists.
- `cook pantry` — inventory tracking.

Cooklang has official iOS and Android apps, so a repo synced to a phone gives a kitchen reader without building one.

## Open questions

- **Where are the recipes now?** PDFs, Apple Notes, Obsidian, photographs, paper. This decides whether the migration is scripted, agent-driven, or manual. Worth inventorying before anything else.
- **How many?** Ten is an afternoon. Three hundred is a pipeline with a review queue.
- **What is the conversion path per source type?** `cook import` covers URLs. PDFs and photos need OCR plus an LLM pass, and the output needs checking — a wrong quantity is worse than no recipe.
- **Public or private repo?** Family recipes may be private; scraped ones have licensing questions if published.
- **Does it live in the Obsidian vault or a separate repo?** Separate is cleaner for `cook server`, but splits the PKM. Related to the unfinished PKM item in the dotfiles plan.

## The skill

Scope it after the migration, since the migration teaches what the capture step needs to handle. Likely shape: accept a URL, a photo, or pasted text; produce a `.cook` file with the metadata conventions the corpus settles on; run `cook doctor` before writing. Lives in the `forge-skills` repo with the other verb-named skills.

## Suggested first step

Inventory the sources and count them. Same reasoning as the saved-reading agent: scale decides whether this is a script or a system, and it is cheap to find out.

## Related

- `2026-08-25-saved-reading-agent-idea.md` — the same capture-and-convert shape, applied to Pinboard.
- Dotfiles plan §6 — the PKM item (Zotero + Obsidian), which shares the "where does knowledge live" question.

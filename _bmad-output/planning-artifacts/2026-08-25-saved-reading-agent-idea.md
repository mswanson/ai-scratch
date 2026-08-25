# Saved-Reading Agent — Idea Stub

Owner request, 2026-08-25. Not yet scoped; captured so it is not lost.

## The want

An agent that processes everything saved online — Pinboard pins first, plus read-later articles — reading each item and producing summaries. The backlog is large enough that reading it by hand is not happening, which is why it keeps accumulating.

## Why this surfaced here

It came up during the dotfiles cask audit, deciding whether to keep the Pinboard client (`mas "Pins"`, id 1547106997). Keeping it is the right call precisely *because* of this: the pins are an asset to be mined, not dead weight. The decision and the project are linked.

## What is known so far

- **Pinboard** is the primary source. It has a documented API (`api.pinboard.in/v1`) with token auth, and supports full export of posts as JSON, so bulk access is straightforward.
- **Read-later** is a second, less defined source. Artykul was dropped in the same audit (it was an RSS reader, dormant since 2024), so there is no read-later app in play right now. Worth settling what "read later" means here before building: Pinboard's own `toread` flag may already cover it.
- **Obsidian** is the likely destination for summaries — there is an existing `obsidian-vault` skill in the personal skill library that already handles note creation and wikilinks.

## Open questions, before any building

- **One pass or ongoing?** Draining a backlog once and processing new saves continuously are different products. The backlog is the stated pain; the ongoing pipeline is the more valuable end state.
- **How much does link rot cost?** Pins accumulated over years will include dead URLs. Decide early whether to fetch live, fall back to an archive, or skip — this shapes the whole fetch layer.
- **What is a useful summary?** A paragraph per article is easy and mostly unread. Grouping by theme, surfacing "you saved five things about X", or answering questions across the corpus is harder and more useful. This choice drives whether the output is notes or an index.
- **Where does it run?** A skill invoked on demand, a scheduled cloud agent, or a local batch job. Volume and whether it is one-pass or ongoing decide this.
- **Scale unknown.** Pin count has not been checked; it determines whether this is an afternoon or a real pipeline.

## Suggested next step

Pull the Pinboard export first and count what is actually there, split by tag, age, and `toread` status. That number decides the shape of everything above, and it is a single API call.

## Related

- Dotfiles plan §6 parking lot — the Alfred setup script, captured the same day.
- `mas "Pins"` stays declared in `brew/brewfiles/Brewfile.apps` on the strength of this.

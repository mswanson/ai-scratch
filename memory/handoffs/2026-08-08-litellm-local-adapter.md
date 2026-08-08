---
date: 2026-08-08
topic: LiteLLM local-model adapter for Claude Code — built, verified, awaiting a real usability trial
repos: [ai-scratch, dotfiles]
status: open
---

# LiteLLM local-model adapter

Built over 2026-08-06 → 2026-08-08. It works and is fully verified at the
protocol level. What has NOT happened is anyone actually using it for real
work, which is the only test that decides whether it's worth keeping.

## Authoritative context

Read these first; do not re-derive what they settle.

| Path | Why |
|---|---|
| `dotfiles/config/litellm-stack/README.md` | The operational doc. Rewritten to describe what is actually deployed, including a "what it deliberately does not do" list and the rationale for every removal. Start here. |
| `dotfiles/config/litellm-stack/litellm-config.yaml` | Router config; comments carry the reasoning inline. |
| `dotfiles/exports/litellm.sh` + `config/litellm-stack/litellm-mode.sh` | The `litellm direct\|proxy\|status` toggle, split between shell function (env) and script (persistent state). |
| `_bmad-output/planning-artifacts/2026-08-02-dotfiles-update-plan.md` | §4 carries the install-script item; §1 carries the deferred Go decision. |
| https://docs.litellm.ai/docs/tutorials/claude_code_max_subscription | The upstream mechanism for subscription auth. |

Design history is in the dotfiles commit messages `366175f..ef69863` — each
records why a thing changed, including three separate premise shifts. Read
them before "fixing" anything that looks odd.

## State

### What this is now

An **on-demand adapter**, not a gateway. Claude Code normally talks straight to
`api.anthropic.com` on the subscription and the container isn't running.
`litellm proxy` starts the container and points Claude Code at local models;
`litellm direct` stops it and restores the direct path.

The single reason it exists: Claude Code speaks the Anthropic Messages API,
LM Studio and Ollama speak OpenAI chat-completions, and LiteLLM is the only
piece that translates. Nothing else in the stack can do it.

### Verified working

- LiteLLM `1.95.0` (current stable as of 2026-08-03), clean startup, 8 models registered.
- Live completions through the proxy from all four local backends: `local-general`, `local-coder`, `local-heavy` (70B), `local-oss`.
- `/v1/messages` (Anthropic wire format) → local model, **including a tool-use round trip** returning a proper `tool_use` block and `stop_reason: "tool_use"`. This is what makes the agentic loop structurally viable.
- Full round trip from cold: container down + mode direct → `litellm proxy` starts it, waits for liveliness, sets `ANTHROPIC_BASE_URL` + `ANTHROPIC_MODEL=local-general`, leaves `ANTHROPIC_AUTH_TOKEN` unset → local response → `litellm direct` unsets and stops.
- Default path confirmed clean four ways: mode file is `direct`, fresh login shell has no `ANTHROPIC_*` vars, `~/.claude/settings.json` has no `env` block, and `exports/litellm.sh` is the only thing that ever sets a base URL.
- Toggle's TOML surgery tested against a fixture: key lands above the first table header, idempotent, leaves `[profiles.litellm]`'s identically-named key alone, round-trips byte-identical, still parses.
- A symlinked LaunchAgent plist **does** load — `launchctl bootstrap` accepted it and the job ran. This also answers the open question in dotfiles plan §4 about dotbot-linking `local.qmd-mcp.plist`.
- Ollama `gpt-oss:20b` (13 GB) via `brew services`; three MLX models totalling 74.17 GB in LM Studio.

### Not yet done

- **Nobody has run Claude Code through the proxy against a local model in a real session.** Protocol works; usability unknown. A 30B driving the agentic loop is expected to be noticeably worse — fine for reading code and Q&A, likely rough for multi-step work.
- `codex --profile litellm` never exercised.
- LM Studio "start server on launch" / Login Items not configured (README step 6). Its server only runs while the app is open.
- Download resume across an LM Studio restart untested — README says so explicitly.
- No `scripts/setup-litellm.sh` yet; fresh-machine setup is still the hand-run README sequence (plan §4).

### Per-repo state

| Repo | Branch | Head | Working tree |
|---|---|---|---|
| ai-scratch (hub) | `bmad-loop-dev` | one commit past the pushed `e351832`, **unpushed** | clean; `.codex/tmp/` is now gitignored |
| dotfiles (spoke) | `main` | `cb64189`, **unpushed** | `.claude/settings.json` modified — **pre-existing, not from this work, leave it alone** |

`cb64189` in dotfiles is unrelated to LiteLLM: it moves the qmd collection
registry into `config/qmd/index.yml` and dotbot-links it back to
`~/.config/qmd/index.yml`. See `memory/qmd-index-registry.md`. Mentioned only
so the extra commit on `main` is not a surprise.

PR #1 (https://github.com/mswanson/ai-scratch/pull/1) is still OPEN — hub setup,
bmad-loop v0.9.1, memory consolidation. Unrelated to this work.

### Layout

```
~/litellm-stack                    -> dotfiles/config/litellm-stack   (dotbot)
~/Library/LaunchAgents/com.litellm.versioncheck.plist -> same dir     (dotbot)
~/.config/litellm/.env             real file, mode 600, OUTSIDE every git repo
~/.config/litellm/mode             persisted direct|proxy
```

## Next work

1. **Trial it for real.** `litellm proxy`, then run Claude Code on an actual
   task for twenty minutes while you can still compare against the real thing.
   That answers the only open question that matters: is the offline capability
   worth keeping? Tearing it out is a legitimate outcome — the 74 GB of models
   stay usable through LM Studio's own UI either way.
2. **Decide the codex alias.** `aliases/dev-utils.sh` has
   `alias codex='CODEX_HOME="$PWD/.codex" codex'`. In any project with a
   `.codex/` dir (ai-scratch has one), Codex reads that config and never sees
   `~/.codex/config.toml`, so the provider block and `--profile litellm`
   silently do nothing. Drop the alias, or replicate the
   `[model_providers.litellm]` block per project.
3. **Finish README step 6** — LM Studio start-on-launch + Login Items, so the
   local endpoint is actually there when you reach for it.
4. **Resume the dotfiles plan walkthrough**, parked at §1 decision 1 (Go: in or
   out; standing recommendation is out) since 2026-08-03. See
   `memory/handoffs/2026-08-03-dotfiles-update-walkthrough.md`.
5. Optionally write `scripts/setup-litellm.sh` (plan §4) — only worth it if
   step 1 concludes the stack is a keeper.

## Constraints to honor

Decisions already made. Do not reopen without a reason that is new.

- **Never set `ANTHROPIC_AUTH_TOKEN`.** It replaces the subscription OAuth
  token with a static key and silently moves billing to the metered API
  account. Proxy mode actively unsets it; `litellm status` warns if it's set.
- **No `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` anywhere in this stack.** Adding
  one is a downgrade, not a fix. Auth is Claude Code's own subscription OAuth,
  forwarded by `forward_client_headers_to_llm_api: true`. Clients authenticate
  to LiteLLM itself with `x-litellm-api-key`, never `Authorization`.
- **`background_health_checks` must stay `false`.** A background ping has no
  client OAuth token to forward, so every Anthropic check would 401 and report
  a healthy upstream as down. Same reason `/health` is not a useful routine
  check here.
- **No automatic fallbacks.** Removed deliberately: silent substitution of a
  30B for a frontier model is invisible to the user (Claude Code never surfaces
  `x-litellm-model-id`) and puts a second system in the debug path mid-outage.
- **Codex cannot be proxied** without abandoning its ChatGPT subscription for
  metered billing. Settled; don't retry. GPT work goes through the Codex CLI,
  Anthropic and local work through Claude Code. There is no single pane of glass.
- **`restart: "no"`** — the container is on-demand and must not return on reboot.
- **Secrets stay at `~/.config/litellm/.env`**, outside every git tree.
  `~/litellm-stack` is a symlink into the dotfiles working tree, so a `.env`
  there would be one `git add -A` from being committed — and this repo's history
  already has burned credentials.
- Local `model:` values are the exact ids `/v1/models` reports, which are NOT
  what the download identifiers suggest: `qwen/qwen3-coder-30b` keeps its
  publisher prefix, `llama-3.3-70b-instruct` has no `-mlx`.
- `lms get`: a bare `publisher/name` resolves against the LM Studio hub
  (lowercased); Hugging Face repos need their full URL.
- dotfiles work lands as small direct commits to `main`.
- `rm` is disabled on this machine — `trash`, or `nuke` for explicit permanent deletes.

## Open user inputs

- After the trial: keep the stack, or tear it out?
- The codex alias decision (next work item 2).
- dotfiles plan §1: Go in/out (rec: out), `config/git/work.gitconfig` fill-or-delete, `symlinked/gemrc.sh` keep-or-drop.
- Merge PR #1 whenever ready.

## Suggested skills

| Skill | When |
|---|---|
| `consolidate-memory` | When due — `memory/.last-consolidated` is 2026-08-04, so not yet. Several handoffs here are resolvable. |
| `operate-bmad-loop` | Only if dotfiles work becomes story-driven; it is currently direct commits to `main`. |
| `write-handoff` | Next natural boundary. |

# Dotfiles: Bootstrap Reproducibility — Plan

**Status: EXECUTED 2026-08-26**, commits `54755bc` and `1ab7365` on dotfiles
`main`. All seven gaps closed; `make bootstrap` went from 8 steps to 12 and
`make doctor` gained an Agent Toolchain section that checks every one of them.
The real test (a clean `$HOME`) has not been run; see *What is verified* at the
end.

Requested in review of the cleanup plan, 2026-08-25. This is the gap that plan
kept deferring: `make bootstrap` sets up a shell and a package list, and nothing
else. Everything built on this machine since roughly 2026-06 was installed by
hand and would not survive a rebuild.

**The test this plan is written against:** wipe the machine, clone dotfiles, run
`make bootstrap`, and get back to a working setup without consulting notes.
Today that test fails at seven distinct points.

---

## What is missing, measured

| Layer | State on this machine | Reproducible? |
|---|---|---|
| Shell, symlinks, Homebrew, asdf | `make bootstrap` | **Yes** |
| Global npm packages | `~/.default-npm-packages`, 14 declared | **Partly** — `@tobilu/qmd` is installed and undeclared |
| Global Python packages | `~/.default-python-packages`, 4 declared | Yes |
| `uv` tools | `bmad-loop v0.9.1`, installed by hand | **No** |
| Claude Code skills | 47 in `~/.agents/skills` | **Partly** — 31 locked, 8 symlinked, 8 unreproducible |
| MCP server registrations | 5 registered | **No** |
| LiteLLM stack | `~/litellm-stack` linked, LaunchAgent loaded | **Partly** — config yes, secrets and images no |
| Local models | 69 GB LM Studio, 13 GB Ollama, 2.1 GB qmd | **No** |
| qmd index | 10 collections, 145 docs, embeddings built | **Partly** — registry tracked, index not |

---

## The seven failures, in bootstrap order

### 1. `@tobilu/qmd` is installed but not declared

`npm ls -g` has it at 2.8.3. `symlinked/default-npm-packages.sh` does not list it.
So a fresh asdf node install does not bring it, and the qmd MCP server has no
binary.

This is not hypothetical: it is exactly what happened twice this session. Node
moved, qmd's `better-sqlite3` was compiled against the old ABI, and the recovery
was a manual `npm install -g @tobilu/qmd` both times.

**Fix:** add it to `default-npm-packages.sh` under the "Tooling used by the AI
setup" group, beside `@colbymchenry/codegraph`. One line. Do this first; it is the
cheapest item here and it closes a hole that has already cost real time.

`corepack` and `npm` also show in `npm ls -g` and are absent from the list, but
both ship with node itself. Correctly omitted; noting it so nobody adds them.

### 2. `uv` tools are not declared anywhere

`uv tool list` returns `bmad-loop v0.9.1`, pinned per `memory/bmad-loop-pins.md`.
Nothing in the repo installs it, and nothing records the pin outside the hub's
memory.

**Fix:** a `symlinked/default-uv-tools.sh` list on the same pattern as the npm and
python ones, plus `scripts/install-uv-tools.sh` reading it, plus a bootstrap step.
The version pin goes in the file so `uv tool install bmad-loop==0.9.1` is what
runs.

This is also where `mlx-lm` and `promptfoo` land when the local-RAG project
starts; see `2026-08-25-local-rag-and-tuning-scope.md`, which already flagged them
as machine-level rather than project-level.

### 3. Eight Claude Code skills cannot be reinstalled

`~/.agents/skills` holds 47 entries:

- **8 symlinks** into `~/Code/forge-skills/skills/` — your own skill library,
  versioned in its own repo.
- **31 real directories** tracked in `.agents/skill-lock.json` (25 from
  `mattpocock/skills`, 5 from `vercel-labs/agent-skills`, 1 from
  `vercel-labs/skills`). That lockfile *is* tracked in dotfiles and symlinked to
  `~/.agents/.skill-lock.json`, so this part is already solved.
- **8 real directories in neither**: `gws-docs`, `gws-docs-write`, `gws-drive`,
  `gws-drive-upload`, `gws-shared`, `gws-sheets`, `gws-sheets-append`,
  `gws-sheets-read`. **Identified 2026-08-25** — see below.

Nothing on disk is missing that the lockfile claims, so the lockfile is accurate
as far as it goes. The problem is coverage, in two places.

**The `gws-*` skills, identified.** They are **Google's own**, shipped with the
official [Google Workspace CLI](https://github.com/googleworkspace/cli) — a Rust,
Apache-2.0 tool for Drive, Gmail, Calendar, Sheets, Docs, Chat and Admin, built
dynamically from Google's Discovery Service and designed for agents as much as
humans. The repo is active (pushed 2026-08-25, 30.5k stars) and ships 100+ agent
skills; you have eight of them.

Their `SKILL.md` frontmatter pins `version: 0.22.5` and declares `requires: bins:
[gws]`.

**And that binary is not installed.** No `gws` on PATH, no openclaw binary or
config, nothing in `settings.json` or `skill-lock.json`. The skill directories are
dated **2026-04-12**. So all eight have been inert for four months: they describe
a CLI that is not there.

**There is a name trap worth knowing before you install anything.** `brew install
gws` gets you *a different tool* — streakycobra's `gws` 0.2.0, "manage workspaces
composed of git repositories". The one you want is **`googleworkspace-cli`**,
which is at 0.22.5, exactly the version the skills declare. Homebrew knows they
collide and refuses to install both. Same shape as the `rtk` collision already
documented in `.claude/RTK.md`.

**Recommendation: `brew install googleworkspace-cli`, declare it in
`Brewfile.cli`, and add the eight skills to `skill-lock.json` with
`googleworkspace/cli` as their source.** You said in the cleanup review that you
"rely almost entirely on Google Workspace apps"; this is a CLI over exactly those
apps that agents can drive, and it connects directly to two projects already
stubbed: the recipe corpus (Docs and Drive) and the saved-reading agent (Docs and
Sheets as destinations).

The alternative is to delete all eight. They cost nothing sitting there, but they
are noise in the skill list and they will keep looking like a reproducibility gap
until one thing or the other happens.

**Fix, part two:** nothing recreates the 8 `forge-skills` symlinks on a fresh
machine. They depend on `~/Code/forge-skills` existing, which depends on cloning a
second repo that dotfiles does not mention. A `scripts/setup-skills.sh` should
clone the spoke if absent and create the links, and `install.conf.yaml` should
gain a `~/Code/forge-skills` clone step or the script should own it end to end.

### 4. MCP server registrations exist only in Claude Code's own state

Five servers registered: `todoist` and `cloudflare` (HTTP, OAuth), `codegraph`
(stdio, `codegraph serve --mcp`), `qmd` (HTTP on `localhost:8181`), and the
GitHub plugin server. None is declared in this repo. On a fresh machine every one
is a manual `claude mcp add`.

**Fix:** a tracked `config/claude/mcp-servers.json` plus
`scripts/setup-mcp-servers.sh` that registers each. Two of the five need an
interactive OAuth flow, so the script registers and then tells you which two to
authenticate; it should not pretend that part is automatic.

Note the ordering dependency: `codegraph` and `qmd` are npm globals, so item 1
must land before this script can succeed.

### 5. The LiteLLM stack is configuration without its inputs

`config/litellm-stack/` is complete and well-documented (332-line README,
docker-compose, config, mode toggle, version-check LaunchAgent). The LaunchAgent
is loaded and healthy.

What a fresh machine would not have: `~/.config/litellm/.env` holding
`LITELLM_MASTER_KEY`, which `exports/config.sh:145` reads and which is
deliberately outside every git repo; the Docker images; and the local models the
config points at.

**Fix:** the `.env.example` already exists, so the gap is a bootstrap step that
creates `~/.config/litellm/` from it and stops with an instruction rather than a
silent failure. The secret itself stays out of git; a 1Password item reference is
the right destination once the SSH migration establishes that pattern.

### 6. Local models: 84 GB that nothing records

- **LM Studio:** 69 GB in `~/.lmstudio/models`.
- **Ollama:** 13 GB, currently `gpt-oss:20b`.
- **qmd:** 2.1 GB of GGUF embedding, expansion and rerank models in `~/.cache/qmd`.

The qmd three are the only ones already declared: `config/qmd/index.yml:52-55`
pins all three by Hugging Face path, and qmd pulls them on demand. That is the
pattern the other two should follow.

**Fix:** a tracked manifest of Ollama model tags and LM Studio model ids, and a
`scripts/pull-models.sh` that is explicitly **not** part of `make bootstrap`. 84 GB
is not a bootstrap step; it is a deliberate, resumable one you run when you want
it. The manifest is the artifact that matters, not the automation.

This is the "awkward middle" the local-RAG scope doc identified. Resolving it here
resolves it there too.

### 7. The qmd index is not reproducible, and should not be

`config/qmd/index.yml` tracks 10 collections and their paths. The SQLite index and
embeddings are derived data, disposable per `memory/qmd-index-registry.md`.

**No fix needed.** The right behaviour is a bootstrap step that runs `qmd update &&
qmd embed` after the collections' repos exist, and tolerates missing paths (which
`memory/qmd-index-registry.md` confirms are inert). Recording it here so it is not
mistaken for a gap.

---

## Sequence

Ordered by dependency, not by value.

| Step | Item | Depends on | Effort |
|---|---|---|---|
| 1 | Declare `@tobilu/qmd` | nothing | one line |
| 2 | `default-uv-tools.sh` + install script + bootstrap step | nothing | small |
| 3 | Resolve the 8 `gws-*` skills | your answer, Q1 below | small once decided |
| 4 | `setup-skills.sh`: clone forge-skills, create symlinks | 3 | medium |
| 5 | `setup-mcp-servers.sh` + tracked server list | 1 | medium |
| 6 | LiteLLM `.env` scaffold step | nothing | small |
| 7 | Model manifest + `pull-models.sh` (outside bootstrap) | nothing | medium |
| 8 | qmd index step in bootstrap | 1, 5 | small |
| 9 | Extend `doctor.sh` to check all of the above | 1-8 | medium |

Step 9 is what makes the rest durable. `make doctor` currently verifies 30 things
and none of them are in this document; every gap here was found by hand. A doctor
check per item turns "I hope bootstrap still works" into a command.

---

## The real test

None of this is verified until it is run on a machine that does not already have
the answers. Two options:

1. **A fresh macOS VM.** Highest confidence, most setup.
2. **A throwaway user account** on this machine. Shares Homebrew and the OS but
   gets a clean `$HOME`, which is where every gap in this document lives. Much
   cheaper, and it would have caught all seven.

Recommending option 2 as the standing check, run once after this plan lands and
again whenever a bootstrap step changes.

---

## Open questions

**Q1. Closed 2026-08-25.** The `gws-*` skills are third-party: Google's own,
from `googleworkspace/cli` v0.22.5, requiring a `gws` binary that is not
installed. They belong in `skill-lock.json` with that source, and the binary
belongs in `Brewfile.cli` as `googleworkspace-cli` (**not** `gws`, which is a
different tool). See item 3 above.

The one thing still needing you: **install the CLI, or delete the eight skills?**
*Default: install it,* on the strength of your own "I rely almost entirely on
Google Workspace apps".

**Q2. Should `forge-skills` be cloned by dotfiles bootstrap, or stay a manual
prerequisite?** Cloning it makes the bootstrap self-contained and creates a
dependency between two repos you maintain. *Default: clone it,* since a bootstrap
that produces a broken skills directory is worse than one that pulls a second
repo.

**Q3. Model pulls: manifest only, or manifest plus script?** *Default: both, with
the script outside `make bootstrap`.* 84 GB should never run because someone typed
`make bootstrap`.

**Q4. Does this repo's bootstrap own machine-level AI tooling at all, or does that
belong somewhere else?** The local-RAG scope doc drew the line at "toolchain
belongs in dotfiles, project config does not". This plan follows that line. Worth
confirming it is still where you want it, because it is the line that decides
whether `mlx-lm` and `promptfoo` land here later.

---

## Related

- `2026-08-25-dotfiles-remaining-surfaces-plan.md` — the cleanup pass. Independent
  of this one; they touch different files.
- `2026-08-25-local-rag-and-tuning-scope.md` — drew the toolchain/project line this
  plan follows, and queued `mlx-lm` and `promptfoo` against it.
- `2026-08-22-1password-ssh-agent-plan.md` — establishes the secret-reference
  pattern that item 5 wants for `LITELLM_MASTER_KEY`.
- `memory/bmad-loop-pins.md` — the `bmad-loop` version pin item 2 must carry.
- `memory/qmd-index-registry.md` — why the qmd index is disposable, item 7.


---

## What was built

| Gap | Closed by |
|---|---|
| 1. `@tobilu/qmd` undeclared | one line in `default-npm-packages.sh` |
| 2. `uv` tools undeclared | `default-uv-tools.sh` + `install-uv-tools.sh` + `make install-uv` |
| 3. Skills unreproducible | 8 gws skills registered via the Skills CLI; `setup-skills.sh` for the forge-skills symlinks and the lockfile |
| 4. MCP registrations | `config/claude/mcp-servers.json` + `setup-mcp-servers.sh` + `make setup-mcp` |
| 5. LiteLLM `.env` | scaffolded by `setup-local-services.sh`, never overwriting an existing one |
| 6. Local models | `config/models.txt` + `pull-models.sh` + `make models`, deliberately outside bootstrap |
| 7. qmd index | `qmd update && qmd embed` in `setup-local-services.sh` |
| 9. doctor coverage | an Agent Toolchain section covering all of the above |

## What is verified, and what is not

**Verified by actually breaking it:** deleting a forge-skills symlink and a
locked third-party skill, then restoring both with `setup-skills.sh`.
Unregistering an MCP server and confirming `make doctor` fails, then
re-registering. Both MCP transports registered against throwaway servers and
removed. `uv tool install` with the corrected git spec.

**Not verified:** the whole thing on a clean `$HOME`. Every script was exercised
against a machine that already had most of what it installs, which tests the
idempotent path far better than the install path. The plan's own
recommendation still stands and is now the single highest-value follow-up:
create a throwaway user account on this machine, clone dotfiles, and run
`make bootstrap`. That account shares Homebrew and the OS but gets a clean
`$HOME`, which is where every one of these seven gaps lived.

## Discovered while executing

**`bmad-loop` is not on PyPI**, which the plan assumed. `uv tool install
bmad-loop==0.9.1` fails with "not found in the package registry". It ships from
git with a `[tui]` extra, and the authoritative spec for any installed uv tool
is in `~/.local/share/uv/tools/<name>/uv-receipt.toml`. The tool list carries
the full git spec and a comment pointing at that file.

**The Skills CLI's `-s` flag takes one skill per invocation.** A comma-separated
list is silently rejected with "No matching skills found", including for names
printed in the tool's own listing two lines earlier.

**`googleworkspace/cli` carries 95 skills**, not the 8 on this machine. Only the
8 were installed, so nothing new appeared, but the other 87 are there if the
Workspace tooling gets used more.

# Local RAG and Fine-Tuning — Scope

Owner intent, 2026-08-25: add RAG over local models, then test and tune them. Not started. This captures what already exists, what has to be decided before building, and which parts belong in `make bootstrap` versus staying project-local.

## The machine

MacBook Pro, **Apple M1 Max, 64 GB unified memory**, 10 cores. That is enough to LoRA-tune models in the 7B–14B range locally, which most laptops cannot do — unified memory is the reason, since GPU and CPU share the same 64 GB.

## What already exists

Most of the hard parts are built. Inventory before adding anything:

| Piece | State |
|---|---|
| `qmd` | **A working local RAG system.** Hybrid retrieval over 143 documents: BM25 lexical, vector similarity, HyDE query expansion, reranking. Exposed to agents over MCP. Has a benchmark harness, `qmd bench <fixture.json>`. |
| LiteLLM stack | OpenAI-compatible endpoint on `:4000` fronting Ollama and LM Studio. `config/litellm-stack/` in dotfiles, dotbot-linked to `~/litellm-stack`. |
| Ollama | Installed, brew-managed, declared in `Brewfile.cli`. |
| LM Studio | Installed and declared; serves the MLX models. |
| Python | 3.12.7 via asdf, with `torch 2.11` and `transformers 4.57` already present. `uv` installed for tooling. |

**The endpoint is the seam.** Every eval tool worth using speaks the OpenAI protocol, so they point at `:4000` and reach local models with no adapter code. That is the main reason this is a short project rather than a long one.

**Read qmd's retrieval pipeline before building a second one.** Query expansion and reranking are the two stages hand-rolled RAG usually gets wrong, and there is a working implementation already on the machine.

## Decisions to make first

**Vector store.** Default to **LanceDB** for local work: embedded, no server, no Docker, just a directory on disk, memory-mapped and columnar so a corpus larger than RAM still works. Choose **pgvector** instead if the data is going into Supabase anyway — the CLI is already installed and Beekeeper Studio now browses Postgres, so vectors would sit beside relational data in one system. Choose **Qdrant** only when server-grade metadata filtering is genuinely needed, and accept another service to run beside LiteLLM. Skip Milvus and Weaviate; they solve problems this does not have.

**Embedding model — decide once and write it down.** `nomic-embed-text` or `mxbai-embed-large` through Ollama are the sensible defaults. The model and its dimensions are effectively schema: changing either means re-embedding the entire corpus. Pin the choice in a tracked config, not in a notebook.

**Evaluation, before tuning.** In RAG, retrieval quality dominates output quality, but the instinct is to tune the prompt and the model instead. Two tools, for different jobs:

- **promptfoo** — evals as YAML, run from the CLI, pointed at any OpenAI-compatible endpoint. Node-based, and node 24 is already on asdf. The config lives in git, so the eval suite becomes a tracked artifact rather than a notebook.
- **Ragas** — Python, and the reason to add it is that it measures the *retrieval* stage: context precision and recall, faithfulness, answer relevance. That is what separates "bad answer because retrieval missed" from "bad answer because the generator is weak".

Establish a baseline against a fixed question set before changing anything. `qmd bench` already expects a fixture format — check whether it can be reused rather than inventing a second one.

**Fine-tuning — MLX, not PyTorch.** Unsloth and axolotl are CUDA-only. PyTorch's MPS backend works but leaves performance on the table. Apple's MLX is built for unified memory, and `mlx-lm` has LoRA/QLoRA built in (`uv tool install mlx-lm`). LM Studio is already serving MLX models, so this stays in one ecosystem.

Sequence matters: fine-tuning is the **last** lever, after retrieval and prompting are measured. Tuning a model to compensate for weak retrieval is expensive and fragile.

## What belongs in `make bootstrap`

This is the question this repo exists to answer, and the split is not obvious:

- **Machine-level, belongs in dotfiles** — `mlx-lm` and `promptfoo` as global tools (`uv tool install` and the npm globals list), plus any doctor check that the LiteLLM endpoint answers. These are toolchain, same category as `rtk` or `codegraph`.
- **Project-level, does not belong here** — the vector store itself, the embedding pins, corpora, eval fixtures and adapters. Those are per-project data and config, and they belong in whatever repo the RAG work lives in.
- **The awkward middle** — the embedding model pull. `ollama pull nomic-embed-text` is machine setup by one reading and project config by another. It has the same shape as the existing §4 problem with LM Studio's ~74 GB of `lms get` pulls, and should be settled the same way.

## Open questions

- What is the corpus? Personal notes, code, or something external — this changes chunking, the embedding model, and whether qmd already covers it.
- Is the target improving qmd's retrieval, or a separate RAG pipeline for a different corpus? Those are different projects.
- What does "tuning" mean here — prompt and retrieval tuning, or actual weight updates? The first needs eval tooling only; the second needs MLX, a training set, and far more time.
- Does the saved-reading agent share this corpus? See [[2026-08-25-saved-reading-agent-idea]] — the Pinboard backlog is a natural RAG corpus, and the two projects may be one.

## Related

- `_bmad-output/planning-artifacts/2026-08-25-saved-reading-agent-idea.md`
- Dotfiles plan §4 — token-optimization stack in bootstrap, which already carries the LM Studio and LiteLLM reproducibility problem.

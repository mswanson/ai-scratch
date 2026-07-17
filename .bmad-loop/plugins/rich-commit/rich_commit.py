"""bmad-loop pre_commit plugin: rich per-story commit messages.

The orchestrator squashes each story's dev/review commit chain into ONE commit
(``finalize_commit``) carrying a one-line subject. This hook replaces that
message with the same subject PLUS the story spec's ``## Auto Run Result``
section as the body. Combined with ``merge_strategy = "ff"`` on a phase branch,
every story lands as a single commit whose message *is* its review summary, so a
``phase-branch -> main`` PR is reviewable commit-by-commit.

Fail-open by design (``fail_closed = False``): a rich message is a nicety, never
a reason to block a commit. Any problem leaves the default message untouched.

Portable: the story spec directory is resolved from the project's
``_bmad/bmm/config.yaml`` (``implementation_artifacts``), with fallbacks, rather
than hardcoding one project's layout.
"""

from __future__ import annotations

from pathlib import Path

from bmad_loop.plugins.model import Plugin

MARKER = "## Auto Run Result"
# Fallback spec dirs (project-relative), tried in order if bmm config can't be read.
FALLBACK_SPEC_DIRS = (
    "_bmad-output/implementation-artifacts",
    "docs/stories",
    "_bmad-output/planning-artifacts",
)


def _spec_dirs(root: Path) -> list[Path]:
    """Candidate directories that hold story spec files, best guess first."""
    dirs: list[Path] = []
    cfg = root / "_bmad" / "bmm" / "config.yaml"
    try:
        import yaml  # bundled with bmad-loop

        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        for key in ("implementation_artifacts", "planning_artifacts"):
            val = data.get(key)
            if isinstance(val, str) and val:
                rel = val.replace("{project-root}/", "").replace("{project-root}", "").lstrip("/")
                dirs.append(root / rel)
    except Exception:
        pass
    dirs.extend(root / d for d in FALLBACK_SPEC_DIRS)
    # de-dupe, keep order, keep only existing dirs
    seen, out = set(), []
    for d in dirs:
        if d not in seen and d.is_dir():
            seen.add(d)
            out.append(d)
    return out


class RichCommitPlugin(Plugin):
    fail_closed = False  # a raised exception must never pause/block the commit

    def on_pre_commit(self, ctx) -> None:
        try:
            root = Path(ctx.worktree or ctx.repo_root or "")
            if not str(root) or not ctx.story_key:
                return

            spec = None
            for d in _spec_dirs(root):
                exact = d / f"{ctx.story_key}.md"
                if exact.is_file():
                    spec = exact
                    break
                matches = sorted(d.glob(f"{ctx.story_key}*.md"))
                if len(matches) == 1:
                    spec = matches[0]
                    break
            if spec is None:
                return

            text = spec.read_text(encoding="utf-8")
            idx = text.find(MARKER)
            if idx == -1:
                return
            body = text[idx:].rstrip()

            incoming = (ctx.proposed_commit_message or "").strip()
            subject = incoming.splitlines()[0].strip() if incoming else f"story {ctx.story_key}: via bmad-loop"

            ctx.proposed_commit_message = f"{subject}\n\n{body}\n"
        except Exception:
            return

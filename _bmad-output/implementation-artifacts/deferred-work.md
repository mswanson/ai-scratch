- source_spec: `_bmad-output/implementation-artifacts/spec-wp1-write-handoff.md`
  summary: Pin /bin/bash (or assert version) across all Makefile test targets so the "macOS bash 3.2" claim is enforced rather than PATH-luck.
  evidence: Every existing suite invokes PATH-resolved `bash`; on machines/runners where Homebrew bash shadows /bin/bash, CI validates bash 5.x while the Makefile header claims 3.2. Pre-existing repo-wide convention, surfaced by WP1 review.

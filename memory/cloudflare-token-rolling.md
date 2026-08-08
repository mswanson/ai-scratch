# Cloudflare token rolling (user practice, settled 2026-08-02)

When the same Cloudflare API token ID recurs across separate "create a new token" requests, don't flag it as an undeleted or reused credential.

**Why:** the user's practice is to click "Roll" on the existing token in the Cloudflare dashboard, which regenerates the secret value (a full rotation) while keeping the same token ID/object and permission config. This is functionally equivalent to deleting and recreating a token, just without churning token objects. Confirmed directly by the user on 2026-08-02 after repeated (unwelcome) nagging to delete/recreate it during the Cloudflare migration (see `handoffs/2026-08-02-cloudflare-migration.md`).

**How to apply:** stop asking the user to delete/recreate a Cloudflare (or similar) API token between uses when the same ID shows up again — assume they've rolled the secret unless there's a specific reason to think otherwise (e.g. they say so, or the token's `not_before`/creation timestamp hasn't moved).

Copied up 2026-08-04 from the harness memory mirror (`feedback_cloudflare_token_rolling.md`); repo copy is authoritative.

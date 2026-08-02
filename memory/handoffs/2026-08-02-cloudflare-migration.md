---
date: 2026-08-02
topic: Cloudflare migration (AWS Route 53 + Hover DNS consolidation)
repos: [ai-scratch]
status: open
---

## Authoritative context

- `cloudflare-migration/cloudflare-migration-brief.md` — the original plan: 6-step
  process (inventory → Cloudflare account → zone creation/import → nameserver
  cutover → registrar transfer → cleanup), plus Vercel/Hover-specific notes.
  Read this first; most of the "why" behind decisions below traces back to it.
- `cloudflare-migration/transform-records.py` — Route 53 → Cloudflare record
  transform logic (skips apex NS/SOA, converts ALIAS to CNAME, splits
  multi-value records, unescapes wildcard names). Reusable for `forge512.com`
  if its records ever get scripted rather than hand-entered.
- `cloudflare-migration/delete-route53-zones.py` — empties and deletes a Route
  53 hosted zone (deletes all non-default records first, waits for INSYNC,
  then deletes the zone). Already run successfully once; reusable pattern if
  more AWS-side cleanup comes up.
- `route53-inventory/*.records.json` — original AWS DNS export. For the 6
  deleted zones, this is now the **only surviving copy** of the pre-migration
  Route 53 config (the AWS zones themselves are gone). Treat as archival.

## State

**Done and verified** (all diff-checked against source before cutover):
- 7 "real content" domains fully migrated (Route 53 → Cloudflare, nameservers
  cut over, confirmed `Active`): `michaelswanson.me`, `easelkids.com`,
  `budswanson.com`, `1524interactive.com`, `imagineifdesigns.com`,
  `designsbyimagineif.com`, `annekeswanson.com` (last one was Hover-DNS
  source, not Route 53 — Squarespace-hosted, same record pattern as
  `imagineifdesigns.com`).
- 8 parked/family domains migrated with no real records to preserve (empty or
  Hover-default-only): `michael-swanson.com` (was already an active
  pre-existing Cloudflare zone from April 2026), `annekeswanson.me`,
  `swanneke.com`, `garyfrisk.com`, `ilyaswanson.com`, `ilyaswanson.me`,
  `everettswanson.com`, `everettswanson.me`.
- 4 `paideo.*` domains: `paideo.io`/`paideo.school`/`getpaideo.com` have
  Cloudflare Redirect Rules (301, all paths, to `https://paideo.app`);
  `paideo.app` itself is an empty zone waiting for the real app (still in
  dev) — nothing to import there, by design.
- Route 53 cleanup: the 6 corresponding hosted zones (all except
  `stantonweddings.com`) were emptied and deleted from AWS. Confirmed via
  `list-hosted-zones`: `mswanson` account has zero zones left,
  `1524-devops` account has exactly one (`stantonweddings.com`).
- `annekeswanson.com` apex→www: investigated a Hover "Forward" (bare→www)
  that turned out to be dead already — Squarespace's own canonical setting
  does www→bare, and DNS-only (unproxied) records mean Cloudflare Redirect
  Rules never see the traffic anyway. User chose to keep the real (www→bare)
  behavior; the Cloudflare redirect rule that was briefly added was deleted
  again. **Worth checking other migrated domains' Hover "Forwards" tab for
  the same kind of hidden config — flagged once, never followed up.**

**Explicitly excluded, do not touch:**
- `stantonweddings.com` — not the user's domain to manage (client
  relationship via the `1524-devops` business account). Cloudflare zone was
  created in error early on and has been fully removed. Route 53 zone and
  Hover/registrar side left completely alone.
- `garyfriskart.com` — user's father-in-law's (Gary Frisk's) own art business
  site, hosted on his own platform (Studiotopia nameservers, not Hover DNS).
  Never added to Cloudflare. `garyfrisk.com` (without "art") *is* migrated —
  that one really is just a defensively-registered, empty domain.

**Explored and dropped:**
- Cloudflare Resource Tagging — wanted to tag zones by category
  (`personal`/`1524`/`forge`) for organization. Confirmed via a subagent that
  no token-level permission exists yet for this (beta feature, gated by
  account role — Super Admin/Workers Admin/Tag Admin — not a scoped-token
  capability). User decided not to pursue further; not worth revisiting
  unless Cloudflare ships a real token permission for it.

**Paused, not started:**
- `forge512.com` — user's live work email (Google Workspace), currently
  Hover DNS (not Route 53). User explicitly said "skip for now" twice.
  Higher stakes than everything else here since it's live production email.
- Registrar transfer (Hover → Cloudflare) — steps 5–6 of the original brief.
  Cost was quoted at current Cloudflare at-cost pricing: **$181.30/yr** for
  15 domains (11 `.com` @ $10.46 + 4 `.me` @ $16.56), excluding the 4 paideo
  domains at the user's request; **$284.16/yr** if paideo is included (adds
  `.app` $14.20 + `.io` $50.00 + `.school` $28.20 + 1 more `.com`). User said
  "don't do anything now."
- S3 → R2 migration — scoped once, early in the session, never started.
  Scope notes: 4 of the 7 real-content domains are straightforward S3
  static-website-hosting (`michaelswanson.me`, `1524interactive.com`,
  `designsbyimagineif.com` — plus `annekeswanson.com`/`imagineifdesigns.com`
  are Squarespace, not S3). 2 domains go through CloudFront
  (`budswanson.com`, `easelkids.com`) whose *origin* was never actually
  checked — could be S3, could be something else. Would need AWS read
  access again (currently only have `aws login` temp creds, no standing
  read access) plus new Cloudflare R2 write permissions (current OAuth
  grant is DNS-only).

## Next work

1. If resuming `forge512.com`: get a fresh Hover DNS screenshot covering MX,
   SPF (TXT), DKIM (CNAMEs like `google._domainkey`), and DMARC
   (`_dmarc` TXT) — not just MX, since Workspace domains often carry all
   four and missing DKIM/DMARC hurts deliverability silently.
2. If resuming registrar transfer: re-check each domain's actual expiration
   date against the two timing risks before transferring anything — don't
   transfer within 45 days of a Hover auto-renewal (no credit for the extra
   year, real double-pay), and don't wait until inside 15 days of expiration
   (renew at Hover first if so).
3. If resuming S3→R2: first confirm what's actually behind the
   `budswanson.com`/`easelkids.com` CloudFront distributions before assuming
   they're S3-backed.
4. Optional/low-priority: spot-check the other migrated domains' Hover
   Forwards tabs for hidden redirect config like the one found on
   `annekeswanson.com`.

## Constraints to honor

- **Never print/grep credential files with secret values inline** — verify
  AWS/Cloudflare identity only via API calls (`sts get-caller-identity`,
  `tokens/verify`), never `cat`/`grep` a credentials file in a way that could
  echo the secret. (This was violated once with a careless `grep -A2` on
  `~/.aws/credentials`; both exposed keys were rotated afterward.)
- **Interactive credential entry must run in the user's own terminal**, never
  through the assistant's Bash tool (no live stdin reaches it) — this
  applies to `aws configure`, `aws login`, and the `read -rs` token-paste
  pattern used for Cloudflare tokens.
- zsh (the user's shell) doesn't support bash's `read -p "prompt"` —
  use `read -rs "VAR?prompt text"` instead.
- **AWS**: both `mswanson` and `1524-devops` profiles now use `aws login`
  (temporary, browser-session-based, auto-refreshing) rather than static
  access keys — no standing credentials exist for either right now. Note
  `aws login` grabs whatever identity the browser console session is using,
  which was root for both accounts, not a scoped IAM user — acceptable for
  short, well-defined cleanup tasks, but re-check if used for anything
  broader.
- **Cloudflare zone creation** needs a token with **Zone → Zone → Edit** +
  **Zone → DNS → Edit** (confirmed working recipe). Do NOT use
  "Account Settings: Edit" — despite what community threads suggest, it does
  not work (confirmed via direct 403 in this session).
- **Cloudflare Redirect Rules** (Rulesets API, `http_request_dynamic_redirect`
  phase) need an additional **Zone → Dynamic URL Redirects → Edit**
  permission, and can only be called via a real API token through curl —
  the OAuth-scoped MCP connection (`mcp__cloudflare__execute`) cannot reach
  this endpoint at all.
- **Cloudflare Redirect Rules only fire on proxied (orange-cloud) traffic.**
  Every record in this migration was deliberately kept DNS-only (grey
  cloud, faithful migration, no new Cloudflare features) — so any redirect
  rule on an unproxied hostname is dead code. Learned this the hard way on
  `annekeswanson.com`.
- **Cloudflare assigns nameserver pairs per zone, not per account.** Two
  different pairs showed up in the same account (`imani.ns`/`leland.ns` vs
  `guss.ns`/`meilani.ns`). Always pull each zone's actual assigned pair from
  the API before telling the user what to set at the registrar.
- **Route 53 `DeleteHostedZone`** requires the zone to contain only the
  default apex NS/SOA first — delete every other record via
  `ChangeResourceRecordSets`, wait for `INSYNC`, then delete the zone.
  Scripted in `delete-route53-zones.py`.
- **Never assume a newly-mentioned domain is safe to migrate.** Two domains
  in this session turned out to belong to someone else
  (`stantonweddings.com`: a client; `garyfriskart.com`: a family member's own
  live site) despite living in an account the user controls. Always confirm
  ownership/authority before creating a zone or importing records for
  anything not already explicitly scoped.
- **The Cloudflare token the user reuses is intentionally the same token
  ID across sessions** — they "roll" (regenerate) its secret each time
  rather than deleting and recreating the token object. This is a real
  rotation, not a stale/reused credential — do not flag it or ask them to
  delete it. (Also saved as a standalone memory:
  `memory/feedback_cloudflare_token_rolling.md` in the harness memory path,
  not this repo's `memory/`.)
- **`rm` is disabled on this machine** — use `trash <path>`.

## Open user inputs

- When to resume `forge512.com` (and the fresh DNS screenshot needed to
  start).
- Whether/when to proceed with the registrar transfer, and for which set of
  domains (15 excluding paideo was the last quoted scope, at the user's
  request).
- Whether/when to start S3→R2, and whether to check the CloudFront origins
  first.
- Whether it's worth auditing other domains' Hover Forwards tabs.

## Suggested skills

None of the installed BMAD skills apply — this isn't BMAD story/epic work,
just direct infrastructure work (Bash, `mcp__cloudflare__*`, WebSearch/
WebFetch) guided by the brief document above. No dedicated skill exists for
this workflow; continue it the same way.

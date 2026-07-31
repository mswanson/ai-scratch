# Cloudflare Migration Brief

Context for Claude Code: consolidating domains and DNS currently split across
multiple Hover accounts and multiple AWS accounts (Route 53 + some S3) into a
single Cloudflare account. Some domains point at Vercel-hosted Next.js apps
and should stay on Vercel for hosting.

## Key decisions

- **DNS migrates first, registrar transfer happens later.** Cloudflare DNS
  works regardless of who the domain is registered with, so there's no reason
  to wait on the registrar side.
- **Multiple source accounts don't complicate anything.** Every domain, from
  whichever Hover or AWS account it currently lives in, ends up in the same
  one Cloudflare account. Migrate each domain independently.
- **Registrar transfer timing:** the transfer fee is one year of registration
  at Cloudflare's at-cost price, added to the domain's *current* expiration
  date — it is not wasted money, and there's no cost benefit to waiting for
  "natural renewal." The actual risk is Hover's auto-renew firing before the
  transfer completes, which causes a real double-pay (registry won't add the
  extra year if you transfer within 45 days of a renewal). So: disable
  Hover auto-renew per domain as soon as it's queued for migration, then
  transfer any time before ~15 days out from expiration (Cloudflare's own
  guidance is to renew first if inside that window).
- **Vercel-hosted domains:** once added to Cloudflare, set those DNS records
  to "DNS only" (grey cloud), not "Proxied" (orange cloud). Vercel explicitly
  discourages being proxied — it breaks bot protection signals and can cause
  SSL/cert provisioning failures. Vercel gives you an A record (commonly
  `76.76.21.21`) and a CNAME (`cname.vercel-dns.com`) to add — add those,
  don't switch to Vercel's nameservers.
- **Hover has no official API.** Only undocumented/unofficial community tools
  exist, and they require storing your Hover username and password in a
  script. Not worth it for a one-time migration — keep domain inventory and
  nameserver cutover manual, via the Hover dashboard.

## The 6-step process

1. **Inventory everything** — every domain across every Hover account, every
   Route 53 hosted zone (+ records) across every AWS account. AWS side is
   scriptable (below); Hover side is manual.
2. **One Cloudflare account** — already done.
3. **Add each domain as a Cloudflare zone and import DNS records** — prefer
   importing directly from the Route 53 export over Cloudflare's automatic
   DNS scanner; the export is ground truth and won't miss uncommon record
   types.
4. **Cut over nameservers** at Hover to the nameservers Cloudflare assigns —
   manual, per domain.
5. **Transfer registration** from Hover to Cloudflare once DNS is confirmed
   active on Cloudflare (see timing notes above).
6. **Repeat across all accounts**, then close the old Hover accounts and
   delete the now-unused Route 53 hosted zones.

This brief covers steps 1–4 in detail (the free, low-risk part). Steps 5–6
are mostly manual registrar-dashboard work.

## Tooling setup

### AWS CLI — one profile per AWS account

```bash
aws configure --profile account-a
aws configure --profile account-b
# or, if using IAM Identity Center:
aws configure sso --profile account-a
```

### Cloudflare MCP server

```bash
claude mcp add cloudflare --transport http https://mcp.cloudflare.com/mcp
```

- First use triggers an OAuth flow in the browser against the existing
  Cloudflare account.
- Verify the connection: `claude mcp list`
- For bulk/scripted operations, skip OAuth and use a scoped Cloudflare API
  token (`Zone:Edit` + `Zone:DNS:Edit` — not the Global API Key) as a bearer
  token instead.
- This is Cloudflare's official "Code Mode" MCP server — it exposes the
  entire API (2,500+ endpoints: DNS, Workers, R2, everything) through two
  tools, `search()` and `execute()`, rather than one tool per endpoint.

## Step 1: AWS inventory script

Exports every Route 53 hosted zone and full record set, across every AWS
profile given to it, into `./route53-inventory/`. Untested against the real
accounts — sanity-check output before trusting it for the import step.

```bash
#!/usr/bin/env bash
# aws-route53-inventory.sh
#
# Exports every Route 53 hosted zone and its full record set, across every
# AWS CLI profile you pass in, into ./route53-inventory/
#
# Usage:  ./aws-route53-inventory.sh account-a account-b account-c
# Requires: aws cli v2, jq

set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <aws-profile-1> [aws-profile-2 ...]"
  exit 1
fi

OUT_DIR="./route53-inventory"
mkdir -p "$OUT_DIR"

SUMMARY="$OUT_DIR/summary.md"
echo "# Route 53 inventory — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$SUMMARY"
echo "" >> "$SUMMARY"

for profile in "$@"; do
  echo "== Profile: $profile =="

  ACCOUNT_ID=$(aws sts get-caller-identity --profile "$profile" --query Account --output text)
  echo "## Account: $ACCOUNT_ID (profile: $profile)" >> "$SUMMARY"
  echo "" >> "$SUMMARY"

  ZONES_FILE="$OUT_DIR/${profile}-zones.json"
  aws route53 list-hosted-zones --profile "$profile" --output json > "$ZONES_FILE"

  jq -r '.HostedZones[] | "\(.Id)\t\(.Name)"' "$ZONES_FILE" | while IFS=$'\t' read -r ZONE_ID ZONE_NAME; do
    CLEAN_ID="${ZONE_ID#/hostedzone/}"
    CLEAN_NAME="${ZONE_NAME%.}"
    RECORDS_FILE="$OUT_DIR/${CLEAN_NAME}.records.json"

    echo "  - $CLEAN_NAME ($CLEAN_ID)"

    aws route53 list-resource-record-sets \
      --hosted-zone-id "$CLEAN_ID" \
      --profile "$profile" \
      --output json > "$RECORDS_FILE"

    RECORD_COUNT=$(jq '.ResourceRecordSets | length' "$RECORDS_FILE")
    echo "- **$CLEAN_NAME** — $RECORD_COUNT records — profile \`$profile\` — see \`${CLEAN_NAME}.records.json\`" >> "$SUMMARY"
  done

  echo "" >> "$SUMMARY"
done

echo ""
echo "Done. See $OUT_DIR/summary.md for the full inventory."
```

## Step 3: Import into Cloudflare via MCP

Once the inventory exists and the Cloudflare MCP server is connected, give
Claude Code a direct instruction rather than doing this by hand:

> For each `*.records.json` file in `./route53-inventory/`, create a
> Cloudflare zone for that domain and recreate every DNS record exactly as
> exported, then show a diff between the Route 53 source and what's now in
> Cloudflare.

Ask for that diff explicitly — it's the checkpoint that catches a mismatch
before it causes an outage at cutover, not a formality.

**For any domain that points at Vercel:** after import, set those specific
DNS records to "DNS only" (unproxied), not "Proxied."

## Step 4: Nameserver cutover (manual, per domain)

1. Have Claude Code compile a `domain → Cloudflare-assigned nameservers`
   checklist from the zone-creation step above.
2. Manually update nameservers per domain in the Hover dashboard.
3. After cutover, ask Claude Code to poll the Cloudflare MCP server until
   the zone status reads `Active`.
4. Only then, delete the corresponding Route 53 hosted zone:

```bash
aws route53 delete-hosted-zone --id <ZONE_ID> --profile <profile>
```

## Cost notes

- Steps 1–4 are entirely free — Cloudflare DNS doesn't require the domain to
  be registered there.
- Route 53 hosted zones cost ~$0.50/mo each — delete once migration is
  confirmed.
- Registrar transfer fee = one year at Cloudflare's at-cost price, added to
  the current expiration date. Avoid transferring within 45 days of a Hover
  renewal (registry won't credit the extra year) and avoid waiting until
  inside 15 days of expiration (renew at Hover first if that window is hit).

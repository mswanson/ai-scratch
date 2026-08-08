#!/usr/bin/env bash
# aws-route53-inventory.sh
#
# Exports every Route 53 hosted zone and its full record set, across every
# AWS CLI profile you pass in, into ./route53-inventory/
#
# Usage:  ./aws-route53-inventory.sh account-a account-b account-c
# Requires: aws cli v2, jq
#
# This is a starting point, not a tested-against-your-account script.
# Sanity-check the output before relying on it for the Cloudflare import step.

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

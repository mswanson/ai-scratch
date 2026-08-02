#!/usr/bin/env python3
"""Empty and delete the migrated Route 53 hosted zones, using the original
record export as the source of exactly what to remove."""
import json
import subprocess
import sys
import time

ZONES = [
    {"domain": "michaelswanson.me", "zone_id": "Z025221113V6PHLOPBS9W", "profile": "mswanson"},
    {"domain": "easelkids.com", "zone_id": "Z056273029U2CJVQOGRL9", "profile": "mswanson"},
    {"domain": "1524interactive.com", "zone_id": "Z1B75STOPJZN81", "profile": "1524-devops"},
    {"domain": "imagineifdesigns.com", "zone_id": "Z2AYL8BI33A1M1", "profile": "1524-devops"},
    {"domain": "budswanson.com", "zone_id": "Z1EMV3MAALSNCY", "profile": "1524-devops"},
    {"domain": "designsbyimagineif.com", "zone_id": "ZQS9DMYIPA6UK", "profile": "1524-devops"},
]


def run_aws(profile, *args):
    cmd = ["aws"] + list(args) + ["--profile", profile, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"aws {' '.join(args)} failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


for z in ZONES:
    domain, zone_id, profile = z["domain"], z["zone_id"], z["profile"]
    print(f"== {domain} ({zone_id}) ==")

    records_path = f"route53-inventory/{domain}.records.json"
    data = json.load(open(records_path))
    record_sets = data["ResourceRecordSets"]

    changes = []
    for r in record_sets:
        # apex NS/SOA are managed by Route 53 itself and get removed with the zone
        if r["Type"] in ("NS", "SOA") and r["Name"].rstrip(".") == domain:
            continue
        changes.append({"Action": "DELETE", "ResourceRecordSet": r})

    if changes:
        batch = {"Comment": "Cleanup before zone deletion", "Changes": changes}
        with open("/tmp/route53-change-batch.json", "w") as f:
            json.dump(batch, f)
        result = run_aws(
            profile, "route53", "change-resource-record-sets",
            "--hosted-zone-id", zone_id,
            "--change-batch", "file:///tmp/route53-change-batch.json",
        )
        change_id = result["ChangeInfo"]["Id"]
        print(f"  deleted {len(changes)} non-default records, change {change_id}, waiting for INSYNC...")
        run_aws(profile, "route53", "wait", "resource-record-sets-changed", "--id", change_id)
        print("  INSYNC")
    else:
        print("  no non-default records to remove")

    run_aws(profile, "route53", "delete-hosted-zone", "--id", zone_id)
    print(f"  hosted zone deleted")
    print()

print("Done.")

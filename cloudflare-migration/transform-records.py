#!/usr/bin/env python3
"""Transform Route 53 record exports into Cloudflare DNS record create payloads."""
import json
import re
import glob
import os

ZONE_IDS = {
    "michaelswanson.me": "db9d747aca08c8b6fe5d0a1da3cb4e5b",
    "easelkids.com": "21ab6766b4f1bc9e32e19c5384f7618a",
    "1524interactive.com": "4e93665da5a04909a28633136d51ae08",
    "imagineifdesigns.com": "c6300c26850956b78e51d7c0986f2977",
    "budswanson.com": "7ee7f1bb5392eb6b3f97fa34458590fd",
    "designsbyimagineif.com": "8cb565dcc268c363046c9aac7ffa553f",
    "stantonweddings.com": "6e53865cf49558680d3b90884bfb616c",
}


def unescape_dns_name(name):
    name = name.rstrip(".")
    return re.sub(r"\\(\d{3})", lambda m: chr(int(m.group(1), 8)), name)


def strip_dot(s):
    return s.rstrip(".")


def transform(domain, records):
    out = []
    skipped = []
    for r in records:
        name = unescape_dns_name(r["Name"])
        rtype = r["Type"]

        if rtype == "SOA":
            skipped.append((rtype, name, "Cloudflare-managed"))
            continue
        if rtype == "NS" and name == domain:
            skipped.append((rtype, name, "apex NS, Cloudflare-managed"))
            continue

        if "AliasTarget" in r:
            target = strip_dot(r["AliasTarget"]["DNSName"])
            out.append({
                "type": "CNAME",
                "name": name,
                "content": target,
                "ttl": 1,
                "proxied": False,
                "_source": f"ALIAS {rtype} -> {target}",
            })
            continue

        ttl = r.get("TTL", 1)
        values = [rr["Value"] for rr in r.get("ResourceRecords", [])]

        if rtype in ("A", "AAAA", "CNAME", "NS"):
            for v in values:
                out.append({
                    "type": rtype,
                    "name": name,
                    "content": strip_dot(v),
                    "ttl": ttl,
                    "proxied": False,
                })
        elif rtype in ("TXT", "SPF"):
            for v in values:
                content = v
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1].replace('\\"', '"')
                out.append({
                    "type": "TXT",
                    "name": name,
                    "content": content,
                    "ttl": ttl,
                })
        elif rtype == "MX":
            for v in values:
                priority_str, target = v.split(" ", 1)
                out.append({
                    "type": "MX",
                    "name": name,
                    "content": strip_dot(target),
                    "priority": int(priority_str),
                    "ttl": ttl,
                })
        else:
            skipped.append((rtype, name, f"unhandled type, value(s)={values}"))
    return out, skipped


def main():
    os.makedirs("cloudflare-migration/zones", exist_ok=True)
    for path in sorted(glob.glob("route53-inventory/*.records.json")):
        domain = os.path.basename(path).replace(".records.json", "")
        if domain not in ZONE_IDS:
            print(f"SKIP FILE (no zone mapping): {path}")
            continue
        data = json.load(open(path))
        records, skipped = transform(domain, data["ResourceRecordSets"])

        out_path = f"cloudflare-migration/zones/{domain}-cf-import.json"
        json.dump({"domain": domain, "zone_id": ZONE_IDS[domain], "records": records},
                   open(out_path, "w"), indent=2)

        print(f"=== {domain} ({len(records)} records to import, {len(skipped)} skipped) ===")
        for rec in records:
            extra = f" (from {rec['_source']})" if "_source" in rec else ""
            prio = f" prio={rec['priority']}" if "priority" in rec else ""
            print(f"  + {rec['type']:6} {rec['name']:40} -> {rec['content']}{prio}{extra}")
        for rtype, name, reason in skipped:
            print(f"  - {rtype:6} {name:40} SKIPPED ({reason})")
        print()


if __name__ == "__main__":
    main()

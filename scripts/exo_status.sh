#!/bin/bash
# Quick EXO cluster status — run from King
# Usage: ./exo_status.sh

API="http://localhost:8000"

if ! curl -s --connect-timeout 3 "$API/v1/models" > /dev/null 2>&1; then
    echo "✗ King API unreachable"
    exit 1
fi

curl -s "$API/state" > /tmp/exo_status_tmp.json 2>/dev/null

python3 /dev/stdin /tmp/exo_status_tmp.json << 'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    d = json.load(f)
n = d["nodeIdentities"]
c = d["topology"]["connections"]
mem = d.get("nodeMemory", {})
rdma = sum(len(l) for x in c.values() for l in x.values())

print(f"╔═══════════════════════════════════════════════════════════════╗")
print(f"║  EXO CLUSTER: {len(n)}/4 nodes | {rdma} RDMA links                       ║")
print(f"╠═══════════════════════════════════════════════════════════════╣")

for nid, info in n.items():
    name = info["friendlyName"]
    chip = info.get("chipId", "?")
    role = "👑 KING" if "King" in name else "⚔️  SOLDIER"
    print(f"║  {role}  {name:22s}  {chip:16s}  ║")

print(f"╠═══════════════════════════════════════════════════════════════╣")
print(f"║  RDMA TOPOLOGY:                                             ║")
for s in c:
    for d2 in c[s]:
        for l in c[s][d2]:
            sn = n.get(s, {}).get("friendlyName", s[:8])[:12]
            dn = n.get(d2, {}).get("friendlyName", d2[:8])[:12]
            si = l.get("sourceRdmaIface", "?")
            di = l.get("sinkRdmaIface", "?")
            print(f"║    {sn:12s} ({si:8s}) ──▶ {dn:12s} ({di:8s})   ║")

print(f"╚═══════════════════════════════════════════════════════════════╝")

# Check for known issues
issues = []
tb_cycles = d.get("thunderboltBridgeCycles", [])
if tb_cycles:
    issues.append(f"⚠ TB Bridge cycle detected — broadcast storm risk ({len(tb_cycles)} cycles)")
if len(n) < 4:
    missing = {"Studio-King-1", "Genesis-Soldier-1", "Genesis-Soldier-2", "Genesis-Soldier-3"} - {i["friendlyName"] for i in n.values()}
    issues.append(f"⚠ Missing nodes: {missing}")
if rdma < 6:
    issues.append(f"⚠ Expected 6 RDMA links (bidirectional daisy chain), got {rdma}")

if issues:
    print("\nISSUES:")
    for i in issues:
        print(f"  {i}")
else:
    print("\n✓ All systems nominal")
PYEOF

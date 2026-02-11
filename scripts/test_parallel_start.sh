#!/bin/bash
# Start all 4 nodes SIMULTANEOUSLY and check after 30s
set -e

KING_EXO_DIR="/Users/jeremyserna/truth_forge/genesis/contrib/exo"
SOLDIER_EXO_DIR="/Users/jeremyserna/Genesis/contrib/exo"
PYTHON="/Users/jeremyserna/miniforge3/envs/exo/bin/python"

export EXO_INITIAL_ELECTION_TIMEOUT=15
export EXO_MDNS_QUERY_INTERVAL_SECS=5

PERF_ENV="EXO_INITIAL_ELECTION_TIMEOUT=15 EXO_MDNS_QUERY_INTERVAL_SECS=5"

echo "=== Starting ALL 4 nodes simultaneously ==="

# Start King
cd "$KING_EXO_DIR"
PYTHONPATH=src nohup "$PYTHON" -c '
import sys
sys.path.insert(0, "src")
from exo.main import main
main()
' --api-port 8000 --force-master < /dev/null > /tmp/exo_king.log 2>&1 &
echo "King PID: $!"

# Start all 3 soldiers at the same time (in parallel SSH)
for s in genesis-soldier-1.local genesis-soldier-2.local genesis-soldier-3.local; do
    name=$(echo "$s" | sed 's/.local//')
    ssh "$s" "cd $SOLDIER_EXO_DIR && $PERF_ENV PYTHONPATH=src nohup $PYTHON -c 'import sys; sys.path.insert(0, \"src\"); from exo.main import main; main()' --api-port 8000 < /dev/null > /tmp/exo_soldier.log 2>&1 & echo \$!" 2>/dev/null &
    echo "Started $name (background)"
done

# Wait for SSH commands to finish
wait

echo ""
echo "All 4 nodes launched. Waiting 30s for mDNS discovery + election..."
sleep 30

echo ""
echo "=== Cluster State ==="
curl -s localhost:8000/state 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    n = d.get('nodeIdentities', {})
    conns = d.get('topology', {}).get('connections', {})
    rdma = sum(len(links) for dests in conns.values() for links in dests.values())
    print(f'Nodes: {len(n)}/4')
    for v in n.values():
        print(f'  {v[\"friendlyName\"]} ({v[\"chipId\"]})')
    print(f'RDMA Links: {rdma}')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "King API not responding"

echo ""
echo "=== Node logs ==="
echo "King:" && tail -5 /tmp/exo_king.log
echo "S2:" && ssh genesis-soldier-2.local 'tail -5 /tmp/exo_soldier.log' 2>/dev/null

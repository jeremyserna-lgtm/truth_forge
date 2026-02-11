#!/bin/bash
# Test: Start S2 first, then King, see if they discover each other
set -e

KING_EXO_DIR="/Users/jeremyserna/truth_forge/genesis/contrib/exo"
SOLDIER_EXO_DIR="/Users/jeremyserna/Genesis/contrib/exo"
PYTHON="/Users/jeremyserna/miniforge3/envs/exo/bin/python"
ENV="EXO_INITIAL_ELECTION_TIMEOUT=15 EXO_MDNS_QUERY_INTERVAL_SECS=5"

echo "=== Kill everything ==="
pkill -9 -f 'exo.main' 2>/dev/null || true
for s in genesis-soldier-1.local genesis-soldier-2.local genesis-soldier-3.local; do
    ssh "$s" 'pkill -9 -f "exo.main" 2>/dev/null; pkill -9 -f "exo_launcher" 2>/dev/null' 2>/dev/null || true
done
sleep 3

# Verify all killed
for s in genesis-soldier-1.local genesis-soldier-2.local genesis-soldier-3.local; do
    ssh "$s" 'pgrep -f "exo.main" >/dev/null && pkill -9 -f "exo.main"' 2>/dev/null || true
done
echo "All killed"

echo ""
echo "=== Starting S2 first (solo) ==="
ssh genesis-soldier-2.local "cd $SOLDIER_EXO_DIR && EXO_INITIAL_ELECTION_TIMEOUT=15 EXO_MDNS_QUERY_INTERVAL_SECS=5 PYTHONPATH=src nohup $PYTHON -c 'import sys; sys.path.insert(0, \"src\"); from exo.main import main; main()' --api-port 8000 < /dev/null > /tmp/exo_soldier.log 2>&1 & echo PID: \$!"
echo "S2 started. Waiting 20s for it to self-elect..."
sleep 20

echo ""
echo "=== Now starting King ==="
cd "$KING_EXO_DIR"
export EXO_INITIAL_ELECTION_TIMEOUT=15
export EXO_MDNS_QUERY_INTERVAL_SECS=5
PYTHONPATH=src nohup $PYTHON -c '
import sys
sys.path.insert(0, "src")
from exo.main import main
main()
' --api-port 8000 --force-master < /dev/null > /tmp/exo_king.log 2>&1 &
KING_PID=$!
echo "King started PID: $KING_PID"

echo "Waiting 30s for discovery..."
sleep 30

echo ""
echo "=== King log ==="
cat /tmp/exo_king.log

echo ""
echo "=== S2 log ==="
ssh genesis-soldier-2.local 'cat /tmp/exo_soldier.log'

echo ""
echo "=== Cluster state ==="
curl -s localhost:8000/state 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    n = d.get('nodeIdentities', {})
    print(f'Nodes: {len(n)}/4')
    for v in n.values():
        print(f'  {v[\"friendlyName\"]}')
except:
    print('Could not parse state')
" 2>/dev/null || echo "King API not responding"

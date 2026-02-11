#!/bin/bash
# EXO Cluster Reset - Kill all, restart in order
# Daisy chain: King -> S1 -> S2 -> S3
# Includes performance tuning for 4x M3 Ultra (1.28TB pooled)

set -e

KING_EXO_DIR="/Users/jeremyserna/truth_forge/genesis/contrib/exo"
SOLDIER_EXO_DIR="/Users/jeremyserna/Genesis/contrib/exo"
PYTHON="/Users/jeremyserna/miniforge3/envs/exo/bin/python"
SOLDIERS=("genesis-soldier-1.local" "genesis-soldier-2.local" "genesis-soldier-3.local")

# ── Performance Environment Variables ─────────────
# These override defaults in the EXO source code
export EXO_MEMORY_THRESHOLD=0.95       # Use 95% of RAM (default 90% wastes 64GB across cluster)
export EXO_FAST_SYNCH=on               # Force Metal fast sync for GPU scheduling
export EXO_KV_BITS=4                   # 4-bit KV quantization (~4x context capacity)
export EXO_KV_CACHE_BITS=4             # 4-bit quantized KV prefix cache
export EXO_MAX_TOKENS=131072           # 128K max generation (default 32K)
export EXO_MAX_KV_SIZE=32768           # 32K rotating KV cache (default 3200)
export EXO_KEEP_KV_SIZE=16384          # Keep 16K on eviction (default 1600)
export EXO_MAX_CHUNK_SIZE=4194304      # 4MB chunks for TB5 (default 512KB)
export EXO_MODEL_LOAD_TIMEOUT=600      # 10 min model load timeout for large models
export EXO_TRACING_ENABLED=false
export EXO_INITIAL_ELECTION_TIMEOUT=15 # 15s discovery window before self-electing (default was 0 = instant)
export EXO_MDNS_QUERY_INTERVAL_SECS=5  # mDNS re-query every 5s (rebuilt Rust binary, was 1500s)

# Env vars to propagate to soldiers via SSH
PERF_ENV="EXO_MEMORY_THRESHOLD=0.95 EXO_FAST_SYNCH=on EXO_KV_BITS=4 EXO_KV_CACHE_BITS=4 EXO_MAX_TOKENS=131072 EXO_MAX_KV_SIZE=32768 EXO_KEEP_KV_SIZE=16384 EXO_MAX_CHUNK_SIZE=4194304 EXO_MODEL_LOAD_TIMEOUT=600 EXO_TRACING_ENABLED=false EXO_INITIAL_ELECTION_TIMEOUT=15 EXO_MDNS_QUERY_INTERVAL_SECS=5"

echo "╔═══════════════════════════════════════════╗"
echo "║     EXO CLUSTER RESET                     ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# ── Phase 1: Graceful shutdown with signal escalation ─
echo "⏹  Phase 1: Stopping all EXO processes..."

# Step 1: Unload LaunchAgents to prevent auto-restart during reset
echo "   Disabling LaunchAgents..."
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.watchdog.plist 2>/dev/null || true
for s in "${SOLDIERS[@]}"; do
    ssh "$s" 'launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true' 2>/dev/null || true
done

# Step 2: SIGINT (graceful — triggers Node.shutdown() → TaskGroup cancel → clean teardown)
echo "   Sending SIGINT (graceful shutdown)..."
pkill -INT -f 'exo.main' 2>/dev/null || true
for s in "${SOLDIERS[@]}"; do
    ssh "$s" 'pkill -INT -f "exo.main" 2>/dev/null' 2>/dev/null || true
done
echo "   Waiting for graceful shutdown (5s)..."
sleep 5

# Step 3: SIGTERM for anything still alive
KING_ALIVE=$(pgrep -f 'exo.main' 2>/dev/null | wc -l | tr -d ' ')
if [ "$KING_ALIVE" -gt 0 ]; then
    echo "   SIGTERM fallback for King..."
    pkill -f 'exo.main' 2>/dev/null || true
fi
for s in "${SOLDIERS[@]}"; do
    ssh "$s" 'pgrep -f "exo.main" >/dev/null 2>&1 && pkill -f "exo.main"' 2>/dev/null || true
done
sleep 2

# Step 4: SIGKILL as last resort
KING_ALIVE=$(pgrep -f 'exo.main' 2>/dev/null | wc -l | tr -d ' ')
if [ "$KING_ALIVE" -gt 0 ]; then
    echo "   SIGKILL last resort for King..."
    pkill -9 -f 'exo.main' 2>/dev/null || true
    sleep 1
fi
for s in "${SOLDIERS[@]}"; do
    ssh "$s" 'pgrep -f "exo.main" >/dev/null 2>&1 && pkill -9 -f "exo.main"' 2>/dev/null || true
done

echo "   ✓ All EXO processes stopped"
echo ""

# ── Phase 1b: TCP Buffer Tuning ──────────────────
echo "🔧 Phase 1b: Tuning TCP buffers for TB5 throughput..."

# Increase TCP send/recv buffers to 2MB (default 128KB is a bottleneck for gossipsub over TB5)
tune_tcp() {
    local host="$1"
    local cmd="sudo sysctl -w net.inet.tcp.sendspace=2097152 net.inet.tcp.recvspace=2097152 2>/dev/null || true"
    if [ "$host" = "local" ]; then
        eval "$cmd" 2>/dev/null
    else
        ssh "$host" "$cmd" 2>/dev/null || true
    fi
}
tune_tcp local
for s in "${SOLDIERS[@]}"; do
    tune_tcp "$s"
done
echo "   ✓ TCP buffers set to 2MB"
echo ""

# ── Phase 2: Start King (master) ─────────────────
echo "▶  Phase 2: Starting King (--force-master)..."

cd "$KING_EXO_DIR"
PYTHONPATH=src PYTHONUNBUFFERED=1 nohup "$PYTHON" -u -c 'import sys; sys.path.insert(0, "src"); from exo.main import main; main()' --api-port 8000 --force-master < /dev/null > /tmp/exo_king.log 2>&1 &
KING_PID=$!
disown $KING_PID 2>/dev/null
echo "   King PID: $KING_PID"

# Wait for King API to be ready
echo "   Waiting for King API..."
for i in $(seq 1 30); do
    if curl -s --connect-timeout 1 localhost:8000/v1/models > /dev/null 2>&1; then
        echo "   ✓ King API ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ✗ King API failed to start! Check /tmp/exo_king.log"
        exit 1
    fi
    sleep 1
done
echo ""

# ── Phase 3: Start soldiers with retry logic ────
echo "▶  Phase 3: Starting soldiers sequentially with retry..."

MAX_RETRIES=3
EXPECTED=1  # King is already node 1

start_soldier() {
    local host="$1"
    # CRITICAL: Keep SSH session alive for 5s after starting the process.
    # Without this, SSH closes immediately and kills the child process
    # before it can fully initialize (bind sockets, set up signal handlers).
    # The 'python -c' approach is required because 'python -m exo.main'
    # exits silently (main.py has no __name__=='__main__' guard).
    ssh "$host" "cd $SOLDIER_EXO_DIR && $PERF_ENV PYTHONPATH=src PYTHONUNBUFFERED=1 nohup $PYTHON -u -c 'import sys; sys.path.insert(0, \"src\"); from exo.main import main; main()' --api-port 8000 < /dev/null > /tmp/exo_soldier.log 2>&1 & PID=\$!; disown \$PID 2>/dev/null; echo \$PID; sleep 5" 2>/dev/null
}

kill_soldier() {
    local host="$1"
    ssh "$host" 'pkill -9 -f "exo.main" 2>/dev/null; pkill -9 -f "exo_launcher" 2>/dev/null' 2>/dev/null || true
    sleep 1
}

wait_for_join() {
    local expected="$1"
    local timeout_secs=45
    for i in $(seq 1 "$timeout_secs"); do
        NODE_COUNT=$(curl -s --connect-timeout 2 localhost:8000/state 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(len(d.get('nodeIdentities', {})))
except: print(0)
" 2>/dev/null)
        if [ "$NODE_COUNT" -ge "$expected" ]; then
            return 0
        fi
        echo -n "."
        sleep 1
    done
    return 1
}

for s in "${SOLDIERS[@]}"; do
    name=$(echo "$s" | sed 's/.local//')
    EXPECTED=$((EXPECTED + 1))
    JOINED=false

    for attempt in $(seq 1 "$MAX_RETRIES"); do
        if [ "$attempt" -gt 1 ]; then
            echo "   ↻ Retry $attempt/$MAX_RETRIES for $name (killing stale process first)..."
            kill_soldier "$s"
        else
            echo "   Starting $name..."
        fi

        start_soldier "$s"
        echo -n "   Waiting for $name to join cluster ($EXPECTED/4)..."

        if wait_for_join "$EXPECTED"; then
            echo " ✓ ($EXPECTED/4 nodes)"
            JOINED=true
            break
        else
            echo " ✗ (timeout)"
        fi
    done

    if [ "$JOINED" = false ]; then
        echo "   ⚠ $name failed after $MAX_RETRIES attempts — continuing with remaining soldiers"
    fi
done

echo ""

echo "╔═══════════════════════════════════════════╗"
echo "║     CLUSTER STATUS                        ║"
echo "╚═══════════════════════════════════════════╝"

curl -s localhost:8000/state 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    nodes = data.get('nodeIdentities', {})
    topo = data.get('topology', {})
    conns = topo.get('connections', {})
    rdma_links = sum(len(links) for dests in conns.values() for links in dests.values())
    
    print(f'  Nodes: {len(nodes)}/4')
    for nid, info in nodes.items():
        print(f'    ✓ {info[\"friendlyName\"]} ({info[\"chipId\"]})')
    print(f'  RDMA Links: {rdma_links}')
    
    for src, dests in conns.items():
        src_name = nodes.get(src, {}).get('friendlyName', src[:12])
        for dst, links in dests.items():
            dst_name = nodes.get(dst, {}).get('friendlyName', dst[:12])
            for link in links:
                print(f'    {src_name} → {dst_name} ({link[\"sourceRdmaIface\"]} → {link[\"sinkRdmaIface\"]})')
    
    if len(nodes) < 4:
        print()
        print(f'  ⚠  Only {len(nodes)}/4 nodes. Missing nodes may need more time for mDNS discovery.')
        print(f'     Re-run: curl localhost:8000/state | python3 -m json.tool')
except Exception as e:
    print(f'  Error reading cluster state: {e}')
" 2>/dev/null || echo "  ✗ Could not reach King API"

# ── Phase 4: Re-enable LaunchAgents for autonomous recovery ─
echo ""
echo "🔄 Phase 4: Re-enabling LaunchAgents for autonomous recovery..."

# Re-load King's EXO LaunchAgent (won't start a second instance — already running)
if [ -f ~/Library/LaunchAgents/com.genesis.exo.plist ]; then
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true
    echo "   ✓ King LaunchAgent re-enabled"
fi
# Re-load watchdog
if [ -f ~/Library/LaunchAgents/com.genesis.exo.watchdog.plist ]; then
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.watchdog.plist 2>/dev/null || true
    echo "   ✓ Watchdog LaunchAgent re-enabled"
fi
# Re-load soldiers
for s in "${SOLDIERS[@]}"; do
    name=$(echo "$s" | sed 's/.local//')
    ssh "$s" 'if [ -f ~/Library/LaunchAgents/com.genesis.exo.plist ]; then launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true; fi' 2>/dev/null || true
    echo "   ✓ $name LaunchAgent re-enabled"
done
echo "   ✓ All LaunchAgents active — cluster will auto-recover on crash/reboot"

echo ""
echo "Logs:"
echo "  King:    /tmp/exo_king.log"
echo "  Soldiers: ssh <host> cat /tmp/exo_soldier.log"

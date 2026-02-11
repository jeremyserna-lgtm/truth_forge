#!/bin/bash
# EXO Cluster Watchdog — monitors health and auto-recovers failed nodes
# Run via: launchctl or cron every 60 seconds
# Usage: ./exo_watchdog.sh [--recover]
#   --recover: automatically restart failed nodes (default: report only)

KING_HOST="localhost"
SOLDIERS=("genesis-soldier-1.local" "genesis-soldier-2.local" "genesis-soldier-3.local")
SOLDIER_EXO_DIR="/Users/jeremyserna/Genesis/contrib/exo"
PYTHON="/Users/jeremyserna/miniforge3/envs/exo/bin/python"
LOG="/tmp/exo_watchdog.log"
RECOVER="${1:-}"

# Performance env vars (same as reset script)
PERF_ENV="EXO_MEMORY_THRESHOLD=0.95 EXO_FAST_SYNCH=on EXO_KV_BITS=4 EXO_KV_CACHE_BITS=4 EXO_MAX_TOKENS=131072 EXO_MAX_KV_SIZE=32768 EXO_KEEP_KV_SIZE=16384 EXO_MAX_CHUNK_SIZE=4194304 EXO_MODEL_LOAD_TIMEOUT=600 EXO_TRACING_ENABLED=false"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

# ── Check King API ────────────────────────────────
KING_OK=false
KING_NODES=0
if curl -s --connect-timeout 5 "http://$KING_HOST:8000/v1/models" > /dev/null 2>&1; then
    KING_OK=true
    KING_NODES=$(curl -s --connect-timeout 5 "http://$KING_HOST:8000/state" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(len(d.get('nodeIdentities', {})))
except: print(0)
" 2>/dev/null)
fi

if [ "$KING_OK" = false ]; then
    log "CRITICAL: King API unreachable on port 8000"
    if [ "$RECOVER" = "--recover" ]; then
        log "Triggering full cluster reset..."
        bash "$(dirname "$0")/reset_exo_cluster.sh" >> "$LOG" 2>&1
    fi
    exit 1
fi

# ── Check each soldier ────────────────────────────
FAILED_SOLDIERS=()
for s in "${SOLDIERS[@]}"; do
    name=$(echo "$s" | sed 's/.local//')
    ALIVE=$(ssh -o ConnectTimeout=5 "$s" 'pgrep -f "exo.main" | wc -l | tr -d " "' 2>/dev/null || echo "0")
    if [ "$ALIVE" -eq 0 ]; then
        FAILED_SOLDIERS+=("$s")
        log "WARNING: $name — EXO process not running"
    fi
done

# ── Report ────────────────────────────────────────
if [ ${#FAILED_SOLDIERS[@]} -eq 0 ] && [ "$KING_NODES" -ge 4 ]; then
    # All healthy — silent unless verbose
    if [ -n "$VERBOSE" ]; then
        log "OK: $KING_NODES/4 nodes healthy"
    fi
    exit 0
fi

if [ "$KING_NODES" -lt 4 ]; then
    log "WARNING: Only $KING_NODES/4 nodes in cluster"
fi

# ── Auto-recover failed soldiers ──────────────────
if [ "$RECOVER" = "--recover" ] && [ ${#FAILED_SOLDIERS[@]} -gt 0 ]; then
    for s in "${FAILED_SOLDIERS[@]}"; do
        name=$(echo "$s" | sed 's/.local//')
        log "Recovering $name..."

        # Try LaunchAgent reload first (preferred — matches boot behavior)
        RELOADED=$(ssh -o ConnectTimeout=5 "$s" 'launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null; sleep 2; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null && echo "ok" || echo "fail"' 2>/dev/null)

        if [ "$RELOADED" != "ok" ]; then
            # Fallback: direct start via SSH (keep session alive for init)
            log "  LaunchAgent reload failed, falling back to direct start..."
            ssh "$s" "cd $SOLDIER_EXO_DIR && $PERF_ENV PYTHONPATH=src PYTHONUNBUFFERED=1 nohup $PYTHON -u -c 'import sys; sys.path.insert(0, \"src\"); from exo.main import main; main()' --api-port 8000 < /dev/null > /tmp/exo_soldier.log 2>&1 & PID=\$!; disown \$PID 2>/dev/null; echo \$PID; sleep 5" 2>/dev/null
        fi
        
        # Wait for it to join
        sleep 10
        NEW_COUNT=$(curl -s --connect-timeout 5 "http://$KING_HOST:8000/state" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(len(d.get('nodeIdentities', {})))
except: print(0)
" 2>/dev/null)
        
        if [ "$NEW_COUNT" -gt "$KING_NODES" ]; then
            log "OK: $name recovered (cluster now $NEW_COUNT/4)"
            KING_NODES=$NEW_COUNT
        else
            log "ERROR: $name failed to rejoin cluster"
        fi
    done
fi

# ── Memory pressure check ─────────────────────────
# Warn if any node is under swap pressure (should never happen with 256GB+)
for host in "$KING_HOST" "${SOLDIERS[@]}"; do
    if [ "$host" = "localhost" ]; then
        SWAP_USED=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $6}' | tr -d 'M')
    else
        SWAP_USED=$(ssh -o ConnectTimeout=5 "$host" 'sysctl -n vm.swapusage 2>/dev/null | awk "{print \$6}" | tr -d "M"' 2>/dev/null || echo "0")
    fi
    if [ -n "$SWAP_USED" ] && [ "${SWAP_USED%.*}" -gt 0 ] 2>/dev/null; then
        log "WARNING: $host has ${SWAP_USED}MB swap in use — memory pressure detected"
    fi
done

exit 0

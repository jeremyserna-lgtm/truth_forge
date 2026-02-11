#!/bin/bash
# Universal EXO node start script
# Used by LaunchAgents on all nodes (King + Soldiers)
# Detects node role automatically via hostname
#
# Usage:
#   ./start_exo_node.sh              # auto-detect role from hostname
#   ./start_exo_node.sh --master     # force master mode (King)
#   ./start_exo_node.sh --worker     # force worker mode (Soldier)

set -euo pipefail

# ── Paths ─────────────────────────────────────────
export HOME="${HOME:-/Users/jeremyserna}"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/miniforge3/envs/exo/bin"

HOSTNAME=$(hostname -s)
PYTHON="$HOME/miniforge3/envs/exo/bin/python"

# Determine EXO source directory (King vs Soldier paths)
if [ -d "$HOME/truth_forge/genesis/contrib/exo/src/exo" ]; then
    EXO_DIR="$HOME/truth_forge/genesis/contrib/exo"
elif [ -d "$HOME/Genesis/contrib/exo/src/exo" ]; then
    EXO_DIR="$HOME/Genesis/contrib/exo"
else
    echo "FATAL: Cannot find EXO source directory" >&2
    exit 1
fi

# ── Performance Environment Variables ─────────────
export EXO_MEMORY_THRESHOLD=0.95
export EXO_FAST_SYNCH=on
export EXO_KV_BITS=4
export EXO_KV_CACHE_BITS=4
export EXO_MAX_TOKENS=131072
export EXO_MAX_KV_SIZE=32768
export EXO_KEEP_KV_SIZE=16384
export EXO_MAX_CHUNK_SIZE=4194304
export EXO_MODEL_LOAD_TIMEOUT=600
export EXO_TRACING_ENABLED=false
export EXO_INITIAL_ELECTION_TIMEOUT=15
export EXO_MDNS_QUERY_INTERVAL_SECS=5
export PYTHONPATH="$EXO_DIR/src"
export PYTHONUNBUFFERED=1

# ── Role Detection ────────────────────────────────
FORCE_ROLE="${1:-}"
IS_MASTER=false

if [ "$FORCE_ROLE" = "--master" ]; then
    IS_MASTER=true
elif [ "$FORCE_ROLE" = "--worker" ]; then
    IS_MASTER=false
else
    # Auto-detect: King hostname contains "King"
    case "$HOSTNAME" in
        *King*|*king*) IS_MASTER=true ;;
        *) IS_MASTER=false ;;
    esac
fi

# ── Build Command ─────────────────────────────────
ARGS="--api-port 8000"
if [ "$IS_MASTER" = true ]; then
    ARGS="$ARGS --force-master"
fi

echo "$(date): Starting EXO on $HOSTNAME (master=$IS_MASTER) from $EXO_DIR"

# ── Launch ────────────────────────────────────────
cd "$EXO_DIR"
exec "$PYTHON" -u -c 'import sys; sys.path.insert(0, "src"); from exo.main import main; main()' $ARGS

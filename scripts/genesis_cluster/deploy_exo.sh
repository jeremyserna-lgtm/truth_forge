#!/bin/bash
# EXO Cluster Deployment Script - Production Ready
# Deploys EXO to all Genesis Cluster nodes with launchd auto-restart
# Usage: ./deploy_exo.sh [king|soldiers|all|status|restart|stop]

set -euo pipefail

# Cluster configuration
KING_IP="192.168.68.121"
SOLDIER_IPS=("192.168.68.112" "192.168.68.123" "192.168.68.115")
ALL_IPS=("$KING_IP" "${SOLDIER_IPS[@]}")
SSH_USER="jeremyserna"
SSH_OPTS="-o IdentitiesOnly=yes -o ConnectTimeout=30 -o StrictHostKeyChecking=no -o ServerAliveInterval=30"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# The startup script that runs EXO with proper environment
STARTUP_SCRIPT='#!/bin/bash
# EXO Startup Script - Production Ready for launchd
export HOME=/Users/jeremyserna
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/jeremyserna/miniforge3/envs/exo/bin
export PYTHONPATH=/Users/jeremyserna/Genesis/contrib/exo/src

mkdir -p ~/.exo
cd /Users/jeremyserna/Genesis/contrib/exo

exec /Users/jeremyserna/miniforge3/envs/exo/bin/python -c "
import sys
sys.path.insert(0, \"src\")
from exo.main import main
main()
" --api-port 8000
'

# The launchd plist for auto-start and auto-restart
LAUNCHD_PLIST='<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.genesis.exo</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/jeremyserna/Genesis/contrib/exo/start_exo.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>/Users/jeremyserna/.exo/exo-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jeremyserna/.exo/exo-stderr.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/jeremyserna/Genesis/contrib/exo</string>
    <key>Nice</key>
    <integer>-10</integer>
</dict>
</plist>'

# Install script that runs on each node
install_on_node() {
    local ip=$1
    local node_name=$2

    log "[$node_name] Starting installation..."

    ssh $SSH_OPTS ${SSH_USER}@${ip} bash << 'INSTALL_EOF'
set -e
echo "[$(hostname)] Creating directories..."
mkdir -p ~/Genesis/contrib ~/.exo ~/Library/LaunchAgents

# Install miniforge if not present
if [ ! -f ~/miniforge3/bin/conda ]; then
    echo "[$(hostname)] Installing Miniforge (this takes a few minutes)..."
    curl -fsSL -o /tmp/miniforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
    bash /tmp/miniforge.sh -b -p ~/miniforge3
    rm /tmp/miniforge.sh
    echo "[$(hostname)] Miniforge installed"
else
    echo "[$(hostname)] Miniforge already installed"
fi

# Clone or update EXO
if [ ! -d ~/Genesis/contrib/exo/.git ]; then
    echo "[$(hostname)] Cloning EXO repository..."
    cd ~/Genesis/contrib
    git clone https://github.com/exo-explore/exo.git
else
    echo "[$(hostname)] EXO repo exists, pulling updates..."
    cd ~/Genesis/contrib/exo
    git pull --ff-only 2>/dev/null || echo "Git pull skipped"
fi

# Create conda environment if not exists
if ! ~/miniforge3/bin/conda env list | grep -q "^exo "; then
    echo "[$(hostname)] Creating conda environment 'exo'..."
    ~/miniforge3/bin/conda create -n exo python=3.13 -y
fi

# Install EXO dependencies
echo "[$(hostname)] Installing EXO dependencies..."
cd ~/Genesis/contrib/exo
~/miniforge3/envs/exo/bin/pip install -e . --quiet 2>/dev/null || ~/miniforge3/envs/exo/bin/pip install -e .

echo "[$(hostname)] Installation complete"
INSTALL_EOF

    if [ $? -ne 0 ]; then
        error "[$node_name] Installation failed"
        return 1
    fi

    # Deploy startup script
    log "[$node_name] Deploying startup script..."
    echo "$STARTUP_SCRIPT" | ssh $SSH_OPTS ${SSH_USER}@${ip} "cat > ~/Genesis/contrib/exo/start_exo.sh && chmod +x ~/Genesis/contrib/exo/start_exo.sh"

    # Deploy launchd plist
    log "[$node_name] Deploying launchd service..."
    echo "$LAUNCHD_PLIST" | ssh $SSH_OPTS ${SSH_USER}@${ip} "cat > ~/Library/LaunchAgents/com.genesis.exo.plist"

    # Load the service
    log "[$node_name] Loading service..."
    ssh $SSH_OPTS ${SSH_USER}@${ip} "launchctl unload ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true; launchctl load ~/Library/LaunchAgents/com.genesis.exo.plist"

    log "[$node_name] Deployment complete"
}

# Check node status
check_status() {
    local ip=$1
    local node_name=$2

    echo "=== $node_name ($ip) ==="
    ssh $SSH_OPTS ${SSH_USER}@${ip} bash << 'STATUS_EOF' 2>/dev/null || echo "  Node unreachable"
echo "  Hostname: $(hostname)"
if pgrep -f 'python.*exo' >/dev/null; then
    echo "  EXO Process: RUNNING (PID $(pgrep -f 'python.*exo'))"
else
    echo "  EXO Process: NOT RUNNING"
fi
if launchctl list 2>/dev/null | grep -q com.genesis.exo; then
    echo "  Launchd Service: LOADED"
else
    echo "  Launchd Service: NOT LOADED"
fi
if curl -s --connect-timeout 2 http://localhost:8000/v1/models >/dev/null 2>&1; then
    MODELS=$(curl -s http://localhost:8000/v1/models | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"]))' 2>/dev/null || echo "?")
    echo "  API Status: RESPONDING ($MODELS models)"
else
    echo "  API Status: NOT RESPONDING"
fi
STATUS_EOF
    echo
}

# Restart EXO on a node
restart_node() {
    local ip=$1
    local node_name=$2

    log "[$node_name] Restarting EXO..."
    ssh $SSH_OPTS ${SSH_USER}@${ip} "launchctl stop com.genesis.exo 2>/dev/null; pkill -9 -f 'python.*exo' 2>/dev/null; sleep 2; launchctl start com.genesis.exo" 2>/dev/null
}

# Stop EXO on a node
stop_node() {
    local ip=$1
    local node_name=$2

    log "[$node_name] Stopping EXO..."
    ssh $SSH_OPTS ${SSH_USER}@${ip} "launchctl stop com.genesis.exo 2>/dev/null; pkill -9 -f 'python.*exo' 2>/dev/null" 2>/dev/null
}

# Main
case "${1:-help}" in
    king)
        install_on_node "$KING_IP" "King"
        ;;
    soldiers)
        for i in "${!SOLDIER_IPS[@]}"; do
            install_on_node "${SOLDIER_IPS[$i]}" "Soldier-$((i+1))" &
        done
        wait
        ;;
    all)
        install_on_node "$KING_IP" "King"
        for i in "${!SOLDIER_IPS[@]}"; do
            install_on_node "${SOLDIER_IPS[$i]}" "Soldier-$((i+1))" &
        done
        wait
        ;;
    status)
        check_status "$KING_IP" "King"
        for i in "${!SOLDIER_IPS[@]}"; do
            check_status "${SOLDIER_IPS[$i]}" "Soldier-$((i+1))"
        done
        ;;
    restart)
        restart_node "$KING_IP" "King"
        for i in "${!SOLDIER_IPS[@]}"; do
            restart_node "${SOLDIER_IPS[$i]}" "Soldier-$((i+1))"
        done
        log "Waiting 15s for cluster to form..."
        sleep 15
        $0 status
        ;;
    stop)
        for ip in "${ALL_IPS[@]}"; do
            stop_node "$ip" "$ip"
        done
        ;;
    *)
        echo "EXO Cluster Deployment Tool"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  all       Install EXO on all nodes (King + Soldiers)"
        echo "  king      Install EXO on King only"
        echo "  soldiers  Install EXO on all Soldiers (parallel)"
        echo "  status    Check status of all nodes"
        echo "  restart   Restart EXO on all nodes"
        echo "  stop      Stop EXO on all nodes"
        echo ""
        echo "Nodes:"
        echo "  King:     $KING_IP"
        echo "  Soldier1: ${SOLDIER_IPS[0]}"
        echo "  Soldier2: ${SOLDIER_IPS[1]}"
        echo "  Soldier3: ${SOLDIER_IPS[2]}"
        ;;
esac

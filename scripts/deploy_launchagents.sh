#!/bin/bash
# Deploy EXO LaunchAgent + start script to all nodes
# Run from King only. Creates autonomous, boot-persistent EXO on all machines.
#
# Usage:
#   ./deploy_launchagents.sh           # Deploy and load on all nodes
#   ./deploy_launchagents.sh --unload  # Unload on all nodes (for manual management)

set -euo pipefail

ACTION="${1:-deploy}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
START_SCRIPT="$SCRIPT_DIR/start_exo_node.sh"
PLIST_TEMPLATE="$SCRIPT_DIR/launchagents/com.genesis.exo.plist"
SOLDIERS=("genesis-soldier-1.local" "genesis-soldier-2.local" "genesis-soldier-3.local")
SOLDIER_EXO_DIR="/Users/jeremyserna/Genesis/contrib/exo"

echo "╔═══════════════════════════════════════════╗"
echo "║     EXO LAUNCHAGENT DEPLOYMENT            ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

if [ "$ACTION" = "--unload" ]; then
    echo "Unloading LaunchAgents on all nodes..."

    # King
    launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true
    echo "  ✓ King: unloaded"

    # Soldiers
    for s in "${SOLDIERS[@]}"; do
        name=$(echo "$s" | sed 's/.local//')
        ssh "$s" 'launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true' 2>/dev/null
        echo "  ✓ $name: unloaded"
    done

    echo ""
    echo "All LaunchAgents unloaded. EXO will NOT auto-start on reboot."
    echo "Use reset_exo_cluster.sh for manual management."
    exit 0
fi

# ── Deploy to King ────────────────────────────────
echo "Deploying to King..."
cp "$PLIST_TEMPLATE" ~/Library/LaunchAgents/com.genesis.exo.plist

# Ensure start script is executable
chmod +x "$START_SCRIPT"

echo "  ✓ Plist installed to ~/Library/LaunchAgents/"
echo "  ✓ Start script at $START_SCRIPT"

# ── Deploy to Soldiers ────────────────────────────
for s in "${SOLDIERS[@]}"; do
    name=$(echo "$s" | sed 's/.local//')
    echo ""
    echo "Deploying to $name..."

    # Copy start script to soldier's EXO directory
    scp -q "$START_SCRIPT" "$s:$SOLDIER_EXO_DIR/start_exo_node.sh" 2>/dev/null
    ssh "$s" "chmod +x $SOLDIER_EXO_DIR/start_exo_node.sh" 2>/dev/null

    # Create soldier-specific plist (different WorkingDirectory)
    ssh "$s" "mkdir -p ~/Library/LaunchAgents" 2>/dev/null
    cat "$PLIST_TEMPLATE" | \
        sed "s|/Users/jeremyserna/truth_forge/scripts/start_exo_node.sh|$SOLDIER_EXO_DIR/start_exo_node.sh|g" | \
        sed "s|/Users/jeremyserna/truth_forge/genesis/contrib/exo|$SOLDIER_EXO_DIR|g" | \
        ssh "$s" "cat > ~/Library/LaunchAgents/com.genesis.exo.plist" 2>/dev/null

    echo "  ✓ $name: plist + start script deployed"
done

echo ""

# ── Load LaunchAgents ─────────────────────────────
echo "Loading LaunchAgents..."

# King
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true
sleep 1
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null
echo "  ✓ King: loaded"

# Soldiers
for s in "${SOLDIERS[@]}"; do
    name=$(echo "$s" | sed 's/.local//')
    ssh "$s" 'launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null || true; sleep 1; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.genesis.exo.plist 2>/dev/null' 2>/dev/null
    echo "  ✓ $name: loaded"
done

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║     DEPLOYMENT COMPLETE                   ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "All 4 nodes will now:"
echo "  • Auto-start EXO at boot/login"
echo "  • Auto-restart on crash (15s throttle)"
echo "  • Form cluster via mDNS discovery"
echo ""
echo "Management:"
echo "  Reset cluster:    bash $SCRIPT_DIR/reset_exo_cluster.sh"
echo "  Unload agents:    bash $0 --unload"
echo "  Check status:     bash $SCRIPT_DIR/exo_status.sh"
echo "  View King log:    tail -f /tmp/exo_launchagent_stdout.log"
echo "  View Soldier log: ssh <host> tail -f /tmp/exo_launchagent_stdout.log"

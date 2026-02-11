#!/bin/bash
# Agent Zero Testing Suite
# Tests all critical functionality before user deployment

set -e  # Exit on any error

KING_HOST="192.168.68.121"
SCOUT_PORT="8765"
AGENT_ZERO_PORT="8080"
SSH_KEY="$HOME/.ssh/id_king"

echo "========================================="
echo "Agent Zero Pre-Deployment Test Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

test_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((pass_count++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "${YELLOW}  Error: $2${NC}"
    ((fail_count++))
}

test_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# Test 1: SSH Access to King
echo "Test 1: SSH Access to King"
if ssh -o IdentitiesOnly=yes -i "$SSH_KEY" -o ConnectTimeout=5 jeremyserna@$KING_HOST "echo 'SSH OK'" &>/dev/null; then
    test_pass "SSH connection to King successful"
else
    test_fail "SSH connection to King failed" "Cannot connect to $KING_HOST"
    exit 1
fi
echo ""

# Test 2: Scout MLX Server Running
echo "Test 2: Scout MLX Server Status"
SCOUT_PID=$(ssh -o IdentitiesOnly=yes -i "$SSH_KEY" jeremyserna@$KING_HOST "ps aux | grep 'mlx_lm.*$SCOUT_PORT' | grep -v grep" 2>/dev/null)
if [ -n "$SCOUT_PID" ]; then
    test_pass "Scout MLX server is running on port $SCOUT_PORT"
else
    test_fail "Scout MLX server not running" "No process found on port $SCOUT_PORT"
fi
echo ""

# Test 3: Scout /v1/models Endpoint
echo "Test 3: Scout Models Endpoint"
MODELS_RESPONSE=$(curl -s http://$KING_HOST:$SCOUT_PORT/v1/models 2>&1)
if echo "$MODELS_RESPONSE" | grep -q "mlx-community/Llama-4-Scout"; then
    test_pass "Scout /v1/models endpoint responds correctly"
    echo "  Model: $(echo $MODELS_RESPONSE | grep -o 'mlx-community/Llama-4-Scout[^"]*')"
else
    test_fail "Scout /v1/models endpoint failed" "$MODELS_RESPONSE"
fi
echo ""

# Test 4: Scout Chat Completion Endpoint
echo "Test 4: Scout Chat Completion (Direct)"
CHAT_RESPONSE=$(curl -s http://$KING_HOST:$SCOUT_PORT/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit", "messages": [{"role": "user", "content": "Say exactly: TEST_OK"}], "max_tokens": 10}' 2>&1)

if echo "$CHAT_RESPONSE" | grep -q "TEST_OK\|assistant"; then
    test_pass "Scout chat completion works"
    echo "  Response: $(echo $CHAT_RESPONSE | grep -o '"content":"[^"]*"' | head -1)"
else
    test_fail "Scout chat completion failed" "$CHAT_RESPONSE"
fi
echo ""

# Test 5: Agent Zero Process Running
echo "Test 5: Agent Zero Process Status"
AGENT_ZERO_PID=$(ssh -o IdentitiesOnly=yes -i "$SSH_KEY" jeremyserna@$KING_HOST "ps aux | grep 'run_ui.py' | grep '$AGENT_ZERO_PORT' | grep -v grep" 2>/dev/null)
if [ -n "$AGENT_ZERO_PID" ]; then
    test_pass "Agent Zero is running on port $AGENT_ZERO_PORT"
else
    test_fail "Agent Zero not running" "No process found on port $AGENT_ZERO_PORT"
fi
echo ""

# Test 6: Agent Zero Web UI Accessible
echo "Test 6: Agent Zero Web UI Accessibility"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$KING_HOST:$AGENT_ZERO_PORT/ 2>&1)
if [ "$HTTP_STATUS" = "200" ]; then
    test_pass "Agent Zero web UI is accessible (HTTP 200)"
else
    test_fail "Agent Zero web UI not accessible" "HTTP status: $HTTP_STATUS"
fi
echo ""

# Test 7: Agent Zero Settings Configuration
echo "Test 7: Agent Zero Settings Validation"
SETTINGS=$(ssh -o IdentitiesOnly=yes -i "$SSH_KEY" jeremyserna@$KING_HOST "cat ~/Genesis/apps/agent-zero/tmp/settings.json" 2>/dev/null)

if echo "$SETTINGS" | grep -q "localhost:$SCOUT_PORT"; then
    test_pass "Agent Zero points to correct Scout endpoint (:$SCOUT_PORT)"
else
    test_fail "Agent Zero settings incorrect" "Not pointing to localhost:$SCOUT_PORT"
    echo "  Current settings:"
    echo "$SETTINGS" | grep "api_base" | head -2
fi
echo ""

# Test 8: Agent Zero Model Name Match
echo "Test 8: Agent Zero Model Name Configuration"
if echo "$SETTINGS" | grep -q "mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit"; then
    test_pass "Agent Zero configured with correct model name"
else
    test_fail "Agent Zero model name mismatch" "Not using mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit"
fi
echo ""

# Test 9: Agent Zero API Test (if web UI is up)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "Test 9: Agent Zero API Integration Test"

    # Give Agent Zero a moment to fully initialize
    sleep 2

    # This test is informational only - actual chat requires session management
    test_warn "Agent Zero API test requires web UI session (skipping automated test)"
    echo "  Manual test: Open http://$KING_HOST:$AGENT_ZERO_PORT and send a message"
else
    echo "Test 9: Agent Zero API Integration Test - SKIPPED (web UI not accessible)"
fi
echo ""

# Test 10: Cognitive Bridge Config Exists
echo "Test 10: Cognitive Bridge Configuration"
CB_CONFIG=$(ssh -o IdentitiesOnly=yes -i "$SSH_KEY" jeremyserna@$KING_HOST "test -f ~/Genesis/apps/agent-zero/tmp/cognitive_bridge_config.json && echo 'EXISTS' || echo 'MISSING'" 2>/dev/null)
if [ "$CB_CONFIG" = "EXISTS" ]; then
    test_pass "Cognitive Bridge config file exists"
else
    test_warn "Cognitive Bridge config missing (expected for Phase 0)"
fi
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CRITICAL TESTS PASSED${NC}"
    echo "Agent Zero is ready for user testing"
    echo ""
    echo "Access Agent Zero at: http://$KING_HOST:$AGENT_ZERO_PORT"
    exit 0
else
    echo -e "${RED}✗ DEPLOYMENT BLOCKED${NC}"
    echo "$fail_count critical test(s) failed"
    echo "Fix issues before user deployment"
    exit 1
fi

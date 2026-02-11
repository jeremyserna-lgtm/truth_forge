#!/bin/bash
# Agent Zero UI Diagnostic Script
# Tests all aspects of the web interface to find the blank page issue

KING_HOST="192.168.68.121"
AGENT_ZERO_PORT="8080"

echo "=========================================="
echo "Agent Zero UI Diagnostic"
echo "=========================================="
echo ""

# Test 1: Check if web server responds
echo "[1/7] Testing web server response..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${KING_HOST}:${AGENT_ZERO_PORT}/" 2>&1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Web server responding (HTTP $HTTP_CODE)"
else
    echo "✗ Web server issue (HTTP $HTTP_CODE)"
fi
echo ""

# Test 2: Check if HTML contains body content
echo "[2/7] Checking HTML structure..."
HTML_BODY=$(curl -s "http://${KING_HOST}:${AGENT_ZERO_PORT}/" 2>&1 | grep -c "<body")
if [ "$HTML_BODY" -gt 0 ]; then
    echo "✓ HTML body tag found"
else
    echo "✗ HTML body tag missing"
fi
echo ""

# Test 3: Check if JavaScript files load
echo "[3/7] Testing JavaScript file loading..."
JS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${KING_HOST}:${AGENT_ZERO_PORT}/index.js" 2>&1)
if [ "$JS_CODE" = "200" ]; then
    echo "✓ JavaScript loads (HTTP $JS_CODE)"
else
    echo "✗ JavaScript fails (HTTP $JS_CODE)"
fi
echo ""

# Test 4: Check if CSS files load
echo "[4/7] Testing CSS file loading..."
CSS_CODE=$(curl -s -o /dev/null -w "%{http_CODE}" "http://${KING_HOST}:${AGENT_ZERO_PORT}/index.css" 2>&1)
if [ "$CSS_CODE" = "200" ]; then
    echo "✓ CSS loads (HTTP $CSS_CODE)"
else
    echo "✗ CSS fails (HTTP $CSS_CODE)"
fi
echo ""

# Test 5: Check for WebSocket endpoint
echo "[5/7] Checking for API/WebSocket endpoints..."
curl -s "http://${KING_HOST}:${AGENT_ZERO_PORT}/" 2>&1 | grep -i "socket\|api" | head -3
echo ""

# Test 6: Test if Agent Zero process is running
echo "[6/7] Checking Agent Zero process..."
ssh -o ConnectTimeout=5 -o IdentitiesOnly=yes -i ~/.ssh/id_king jeremyserna@${KING_HOST} "ps aux | grep 'run_ui.py' | grep -v grep" 2>&1 | head -2
echo ""

# Test 7: Check recent logs for errors
echo "[7/7] Checking recent logs for runtime errors..."
ssh -o ConnectTimeout=5 -o IdentitiesOnly=yes -i ~/.ssh/id_king jeremyserna@${KING_HOST} "tail -20 /tmp/agent-zero.log 2>&1 | grep -i 'error\|exception' | tail -5" 2>&1
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If JavaScript loads but page is blank: Check browser console"
echo "2. If API endpoint missing: WebSocket connection may be failing"
echo "3. If process errors: Restart Agent Zero with proper configuration"

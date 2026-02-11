#!/bin/bash
# =============================================================================
# Llama 4 Scout via Exo - Local Inference Server
# =============================================================================
#
# Model: mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit (108GB, pre-downloaded)
# Framework: Exo with MLX backend
# Hardware: Mac with 720GB unified memory
#
# Endpoints after launch:
#   - Web Dashboard: http://localhost:52415
#   - OpenAI API:    http://localhost:52415/v1/chat/completions
#
# =============================================================================

set -e

EXO_DIR="/Users/jeremyserna/exo"
MODEL_ID="mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit"
MODEL_PATH="$HOME/.cache/huggingface/hub/models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit"

echo "=============================================="
echo "  Llama 4 Scout - Exo Inference Server"
echo "=============================================="
echo ""
echo "Model: $MODEL_ID"
echo "Size: 108GB (8-bit quantized)"
echo "Active params: 17B / 109B total (MoE)"
echo "Your RAM: 720GB unified memory"
echo ""

# Verify model exists
if [ ! -d "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    exit 1
fi
echo "Model verified: $MODEL_PATH"

# Verify exo directory
if [ ! -d "$EXO_DIR" ]; then
    echo "ERROR: Exo not found at $EXO_DIR"
    exit 1
fi
echo "Exo verified: $EXO_DIR"

echo ""
echo "Starting Exo with Llama 4 Scout..."
echo ""
echo "Endpoints (once loaded):"
echo "  Web Dashboard: http://localhost:52415"
echo "  OpenAI API:    http://localhost:52415/v1/chat/completions"
echo ""
echo "Test with:"
echo '  curl http://localhost:52415/v1/chat/completions \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"model": "llama-4-scout", "messages": [{"role": "user", "content": "Hello"}]}'"'"
echo ""
echo "=============================================="
echo ""

# Change to exo directory and run
cd "$EXO_DIR"
exec uv run exo run "$MODEL_ID"

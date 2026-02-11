#!/usr/bin/env python3
"""
MCP Server — Cloud Run Deployment
Truth Forge

HTTP server wrapping the MCP protocol for Cloud Run deployment.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment
load_dotenv()

import google.generativeai as genai
from aiohttp import web


# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Import Truth Engine components
import sys


sys.path.insert(0, str(Path(__file__).parent))

from truth_engine.constitution import ConstitutionalCritic
from truth_engine.governance import AuditLogger
from truth_engine.mcp import TruthEngineMCPServer
from truth_engine.symbolic import FractureEngine
from truth_engine.x402 import PaymentSignature, X402Middleware


# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


def create_components():
    """Initialize all Truth Engine components."""

    # Fracture Engine
    fracture = FractureEngine()

    # Constitutional Critic with LLM
    constitution_path = Path(__file__).parent / "truth_engine" / "constitution" / "principles.yaml"

    llm = None
    if GOOGLE_API_KEY:
        llm = genai.GenerativeModel("gemini-1.5-flash")

    critic = ConstitutionalCritic(str(constitution_path), llm_client=llm)

    # Audit Logger (BigQuery in production, local for testing)
    audit = AuditLogger(project_id=os.getenv("GCP_PROJECT"), local_path="logs/mcp_audit.jsonl")

    # x402 Middleware
    x402 = X402Middleware(
        receiver_address=os.getenv("X402_RECEIVER_ADDRESS", "0x0"),
        network=os.getenv("X402_NETWORK", "base-sepolia"),
    )

    # MCP Server
    server = TruthEngineMCPServer(
        fracture_engine=fracture, constitutional_critic=critic, audit_logger=audit
    )

    return server, x402, llm


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════


async def handle_mcp(request):
    """Handle MCP JSON-RPC requests."""
    try:
        data = await request.json()
        method = data.get("method", "")
        params = data.get("params", {})
        request_id = data.get("id", 1)

        server = request.app["mcp_server"]

        if method == "initialize":
            result = await server.handle_initialize(params)
        elif method == "tools/list":
            result = await server.handle_list_tools()
        elif method == "resources/list":
            result = await server.handle_list_resources()
        elif method == "tools/call":
            # Check for payment if required
            tool_name = params.get("name")
            tool = server._tools.get(tool_name)

            if tool and tool.payment:
                payment_header = request.headers.get("X-Payment-Signature")
                if not payment_header:
                    # Return 402 Payment Required
                    x402 = request.app["x402"]
                    requirement = x402.require_payment(tool.payment["amount"], f"MCP: {tool_name}")
                    return web.json_response(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": 402,
                                "message": "Payment Required",
                                "data": requirement.to_dict(),
                            },
                        },
                        status=402,
                        headers={"X-Payment-Details": requirement.to_header()},
                    )

                # Verify payment
                x402 = request.app["x402"]
                sig = PaymentSignature.from_header(payment_header)
                record = await x402.verify_payment(sig)
                if not record:
                    return web.json_response(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": 402, "message": "Payment verification failed"},
                        },
                        status=402,
                    )

            tool_result = await server.handle_call_tool(
                params.get("name"), params.get("arguments", {})
            )
            result = tool_result.to_dict()
        elif method == "resources/read":
            result = await server.handle_read_resource(params.get("uri"))
        else:
            result = {"error": f"Unknown method: {method}"}

        return web.json_response({"jsonrpc": "2.0", "id": request_id, "result": result})

    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_health(request):
    """Health check endpoint."""
    return web.json_response(
        {
            "status": "healthy",
            "service": "truth-engine-mcp",
            "version": "1.0.0",
            "gemini": "configured" if GOOGLE_API_KEY else "not configured",
        }
    )


async def handle_tools(request):
    """List available tools (convenience endpoint)."""
    server = request.app["mcp_server"]
    tools = await server.handle_list_tools()
    return web.json_response(tools)


async def handle_pricing(request):
    """Get pricing info (convenience endpoint)."""
    from truth_engine.x402 import TRUTH_ENGINE_PRICING

    return web.json_response(
        {
            "currency": "USDC",
            "network": os.getenv("X402_NETWORK", "base-sepolia"),
            "tools": TRUTH_ENGINE_PRICING,
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# APP FACTORY
# ═══════════════════════════════════════════════════════════════════════════════


def create_app():
    """Create the aiohttp application."""
    app = web.Application()

    # Initialize components
    server, x402, llm = create_components()
    app["mcp_server"] = server
    app["x402"] = x402
    app["llm"] = llm

    # Routes
    app.router.add_post("/mcp", handle_mcp)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/tools", handle_tools)
    app.router.add_get("/pricing", handle_pricing)

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", 8080)))

    print("═" * 60)
    print("       TRUTH ENGINE MCP SERVER")
    print("═" * 60)
    print(f"Port: {port}")
    print(f"Gemini: {'Configured' if GOOGLE_API_KEY else 'Not configured'}")
    print(f"Network: {os.getenv('X402_NETWORK', 'base-sepolia')}")
    print()
    print("Endpoints:")
    print("  POST /mcp      - MCP JSON-RPC")
    print("  GET  /health   - Health check")
    print("  GET  /tools    - List tools")
    print("  GET  /pricing  - Get pricing")
    print("═" * 60)

    app = create_app()
    web.run_app(app, port=port)

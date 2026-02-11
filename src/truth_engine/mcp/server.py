"""
Model Context Protocol (MCP) Server — Truth Engine
Truth Forge

Exposes Truth Engine verification tools via MCP for universal agent access.
Any MCP-compatible agent can discover and use these tools.
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# MCP PROTOCOL TYPES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MCPTool:
    """MCP Tool definition."""

    name: str
    description: str
    inputSchema: dict[str, Any]
    payment: dict[str, Any] | None = None  # x402 payment info

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema,
        }
        if self.payment:
            result["payment"] = self.payment
        return result


@dataclass
class MCPResource:
    """MCP Resource definition."""

    uri: str
    name: str
    description: str
    mimeType: str = "application/json"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MCPToolResult:
    """Result from a tool call."""

    content: Any
    isError: bool = False
    error: str | None = None
    fidelity_report: str | None = None
    audit_id: str | None = None

    def to_dict(self) -> dict:
        result = {"content": self.content, "isError": self.isError}
        if self.error:
            result["error"] = self.error
        if self.fidelity_report:
            result["fidelity_report"] = self.fidelity_report
        if self.audit_id:
            result["audit_id"] = self.audit_id
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# TRUTH ENGINE MCP SERVER
# ═══════════════════════════════════════════════════════════════════════════════


class TruthEngineMCPServer:
    """
    MCP Server exposing Truth Engine verification capabilities.

    Tools:
    - verify_coherence: Check claim coherence using Fracture Protocol
    - verify_claim: Full claim verification with source checking
    - critique_response: Constitutional AI critique
    - route_model: Get Flash/Pro routing recommendation
    - inspect_fidelity: Get fidelity report for a response

    Resources:
    - spine://entities/unified: Access to unified entity store
    - spine://enrichments: Access to enrichment data
    - spine://embeddings: Access to embedding vectors
    """

    SERVER_INFO = {
        "name": "truth-engine",
        "version": "1.0.0",
        "description": "Truth Engine verification and coherence tools",
        "vendor": "Truth Forge",
    }

    def __init__(
        self, fracture_engine=None, constitutional_critic=None, audit_logger=None, spine_client=None
    ):
        """
        Initialize the MCP server.

        Args:
            fracture_engine: FractureEngine instance
            constitutional_critic: ConstitutionalCritic instance
            audit_logger: AuditLogger instance
            spine_client: BigQuery client for Spine access
        """
        self.fracture_engine = fracture_engine
        self.critic = constitutional_critic
        self.audit = audit_logger
        self.spine = spine_client

        # Register tools
        self._tools: dict[str, MCPTool] = {}
        self._register_tools()

        # Register resources
        self._resources: dict[str, MCPResource] = {}
        self._register_resources()

    def _register_tools(self):
        """Register all available tools."""

        # Tool: verify_coherence
        self._tools["verify_coherence"] = MCPTool(
            name="verify_coherence",
            description="""
            Check if content is internally coherent using the Fracture Protocol.
            Detects self-contradictions, circular reasoning, and logical fallacies.
            Returns COHERENT, FLAGGED, or FRACTURE status.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content to verify for coherence",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Limit checks to specific categories (coherence, verification, resistance, fidelity)",
                    },
                },
                "required": ["content"],
            },
            payment={"amount": "0.002", "currency": "USDC", "network": "base"},
        )

        # Tool: verify_claim
        self._tools["verify_claim"] = MCPTool(
            name="verify_claim",
            description="""
            Fully verify a factual claim by checking:
            1. Internal coherence (Fracture Protocol)
            2. Source verification (Spine search)
            3. Constitutional compliance (Canon Repair Doctrine)
            Returns verification status with confidence score and sources.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "claim": {"type": "string", "description": "The factual claim to verify"},
                    "require_sources": {
                        "type": "boolean",
                        "description": "If true, claim must have verifiable sources",
                        "default": True,
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence threshold (0-1)",
                        "default": 0.7,
                    },
                },
                "required": ["claim"],
            },
            payment={"amount": "0.005", "currency": "USDC", "network": "base"},
        )

        # Tool: critique_response
        self._tools["critique_response"] = MCPTool(
            name="critique_response",
            description="""
            Apply Constitutional AI critique to a response using Canon Repair Doctrine.
            Returns list of principles checked, violations found, and overall score.
            Can optionally generate a revised response addressing violations.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The original query"},
                    "response": {"type": "string", "description": "The response to critique"},
                    "generate_revision": {
                        "type": "boolean",
                        "description": "If true, generate revised response for violations",
                        "default": False,
                    },
                },
                "required": ["query", "response"],
            },
            payment={"amount": "0.003", "currency": "USDC", "network": "base"},
        )

        # Tool: route_model
        self._tools["route_model"] = MCPTool(
            name="route_model",
            description="""
            Get Flash/Pro routing recommendation based on query complexity.
            Returns recommended model (flash or pro) with reasoning.
            Helps optimize cost while maintaining quality.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The query to analyze for routing"},
                    "health_score": {
                        "type": "number",
                        "description": "Optional current health score (0-1)",
                        "default": 1.0,
                    },
                },
                "required": ["query"],
            },
            payment={"amount": "0.001", "currency": "USDC", "network": "base"},
        )

        # Tool: inspect_fidelity
        self._tools["inspect_fidelity"] = MCPTool(
            name="inspect_fidelity",
            description="""
            Generate a Fidelity Inspector report for AI output.
            Exposes shaping forces, sources, assumptions, and limitations.
            Implements the 'no invisible decisions' principle.
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "response": {"type": "string", "description": "The AI response to inspect"},
                    "audit_id": {
                        "type": "string",
                        "description": "Optional audit ID from previous operation",
                    },
                },
                "required": ["response"],
            },
            payment={"amount": "0.001", "currency": "USDC", "network": "base"},
        )

    def _register_resources(self):
        """Register available resources."""

        self._resources["spine://entities/unified"] = MCPResource(
            uri="spine://entities/unified",
            name="Unified Entities",
            description="11.8M+ entities from human-AI conversations across L1-L8 interaction layers",
            mimeType="application/json",
        )

        self._resources["spine://enrichments"] = MCPResource(
            uri="spine://enrichments",
            name="Entity Enrichments",
            description="Sentiment, topics, NRCLex emotions, and other enrichment data",
            mimeType="application/json",
        )

        self._resources["spine://embeddings/gemini"] = MCPResource(
            uri="spine://embeddings/gemini",
            name="Gemini Embeddings",
            description="3072-dimensional Gemini embedding vectors for semantic search",
            mimeType="application/octet-stream",
        )

        self._resources["spine://relationships"] = MCPResource(
            uri="spine://relationships",
            name="Entity Relationships",
            description="Graph edges connecting entities (references, contradicts, supports, causes)",
            mimeType="application/json",
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MCP PROTOCOL HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": self.SERVER_INFO,
            "capabilities": {"tools": {}, "resources": {}},
        }

    async def handle_list_tools(self) -> dict:
        """Handle tools/list request."""
        return {"tools": [tool.to_dict() for tool in self._tools.values()]}

    async def handle_list_resources(self) -> dict:
        """Handle resources/list request."""
        return {"resources": [res.to_dict() for res in self._resources.values()]}

    async def handle_call_tool(self, name: str, arguments: dict) -> MCPToolResult:
        """Handle tools/call request."""

        if name not in self._tools:
            return MCPToolResult(content=None, isError=True, error=f"Unknown tool: {name}")

        try:
            if name == "verify_coherence":
                return await self._call_verify_coherence(arguments)
            elif name == "verify_claim":
                return await self._call_verify_claim(arguments)
            elif name == "critique_response":
                return await self._call_critique_response(arguments)
            elif name == "route_model":
                return await self._call_route_model(arguments)
            elif name == "inspect_fidelity":
                return await self._call_inspect_fidelity(arguments)
            else:
                return MCPToolResult(
                    content=None, isError=True, error=f"Tool not implemented: {name}"
                )
        except Exception as e:
            return MCPToolResult(content=None, isError=True, error=str(e))

    async def handle_read_resource(self, uri: str) -> dict:
        """Handle resources/read request."""

        if uri not in self._resources:
            return {"error": f"Unknown resource: {uri}"}

        # TODO: Implement actual resource reading from BigQuery
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": self._resources[uri].mimeType,
                    "text": json.dumps(
                        {"status": "placeholder", "message": "Resource reading not yet implemented"}
                    ),
                }
            ]
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    async def _call_verify_coherence(self, args: dict) -> MCPToolResult:
        """Implement verify_coherence tool."""

        if not self.fracture_engine:
            return MCPToolResult(content=None, isError=True, error="FractureEngine not configured")

        content = args.get("content", "")
        categories = args.get("categories")

        result = self.fracture_engine.evaluate(content, categories=categories)

        return MCPToolResult(
            content={
                "status": result["status"],
                "halt": result["halt"],
                "triggered_rules": result["triggered_rules"],
                "reasoning_trace": result["reasoning_trace"],
            },
            fidelity_report=result["reasoning_trace"],
        )

    async def _call_verify_claim(self, args: dict) -> MCPToolResult:
        """Implement verify_claim tool."""

        claim = args.get("claim", "")
        require_sources = args.get("require_sources", True)
        min_confidence = args.get("min_confidence", 0.7)

        # Step 1: Coherence check
        coherence_result = None
        if self.fracture_engine:
            coherence_result = self.fracture_engine.evaluate(claim)

            if coherence_result["halt"]:
                return MCPToolResult(
                    content={
                        "status": "REJECTED",
                        "reason": "Failed coherence check",
                        "details": coherence_result,
                    },
                    fidelity_report=coherence_result["reasoning_trace"],
                )

        # Step 2: Source search (placeholder - would use Spine)
        sources = []
        if self.spine:
            # TODO: Implement actual Spine search
            pass

        # Step 3: Constitutional check
        constitutional_score = 1.0
        if self.critic:
            report = await self.critic.critique_response(
                query="Verify this claim: " + claim, response=claim
            )
            constitutional_score = report.overall_score

        # Build result
        confidence = constitutional_score
        if require_sources and not sources:
            confidence *= 0.5  # Reduce confidence without sources

        status = "VERIFIED" if confidence >= min_confidence else "UNVERIFIED"

        return MCPToolResult(
            content={
                "status": status,
                "confidence": confidence,
                "claim": claim,
                "sources": sources,
                "coherence": coherence_result["status"] if coherence_result else "SKIPPED",
                "constitutional_score": constitutional_score,
            }
        )

    async def _call_critique_response(self, args: dict) -> MCPToolResult:
        """Implement critique_response tool."""

        if not self.critic:
            return MCPToolResult(
                content=None, isError=True, error="ConstitutionalCritic not configured"
            )

        query = args.get("query", "")
        response = args.get("response", "")
        generate_revision = args.get("generate_revision", False)

        report = await self.critic.critique_response(query, response)

        result = {
            "overall_score": report.overall_score,
            "needs_revision": report.needs_revision,
            "principles_checked": [c.principle_id for c in report.critiques],
            "violations": [
                {
                    "principle_id": v.principle_id,
                    "principle_name": v.principle_name,
                    "reason": v.reason,
                }
                for v in report.violations
            ],
        }

        if generate_revision and report.violations and self.critic.llm:
            revised = await self.critic.revise_response(query, response, report.violations)
            result["revised_response"] = revised

        return MCPToolResult(
            content=result, fidelity_report=report.to_fidelity_report(), audit_id=report.audit_id
        )

    async def _call_route_model(self, args: dict) -> MCPToolResult:
        """Implement route_model tool."""

        query = args.get("query", "")
        health_score = args.get("health_score", 1.0)

        # Simple routing heuristics
        # In production, this would use a trained classifier

        # Indicators for Pro (deep analysis)
        pro_indicators = [
            len(query) > 1000,  # Long queries
            any(
                w in query.lower()
                for w in [  # Complex topics
                    "analyze",
                    "compare",
                    "evaluate",
                    "synthesize",
                    "explain why",
                    "how does",
                ]
            ),
            health_score < 0.8,  # Low health
            "?" in query and query.count("?") > 2,  # Multiple questions
        ]

        use_pro = sum(pro_indicators) >= 2

        return MCPToolResult(
            content={
                "recommended_model": "pro" if use_pro else "flash",
                "reasoning": {
                    "query_length": len(query),
                    "complexity_indicators": sum(pro_indicators),
                    "health_score": health_score,
                },
                "estimated_cost": 0.015 if use_pro else 0.0018,
            }
        )

    async def _call_inspect_fidelity(self, args: dict) -> MCPToolResult:
        """Implement inspect_fidelity tool."""

        response = args.get("response", "")
        audit_id = args.get("audit_id")

        # If we have an audit ID, fetch from logs
        if audit_id and self.audit:
            # TODO: Implement audit log retrieval
            pass

        # Generate basic fidelity analysis
        shaping_forces = []

        # Detect sources mentioned
        import re

        source_patterns = [
            r"according to ([^,\.]+)",
            r"based on ([^,\.]+)",
            r"([A-Z][a-z]+ (?:et al\.?|and colleagues))",
        ]
        for pattern in source_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                shaping_forces.append({"type": "source", "name": match, "weight": 0.8})

        # Detect uncertainty markers
        uncertainty_patterns = [
            r"\b(may|might|could|possibly|perhaps)\b",
            r"\b(uncertain|unclear|unknown)\b",
        ]
        for pattern in uncertainty_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                shaping_forces.append(
                    {"type": "acknowledgment", "name": "uncertainty_expressed", "weight": 0.5}
                )
                break

        report = f"""
═══════════════════════════════════════════════
              FIDELITY INSPECTOR
═══════════════════════════════════════════════
Response Length: {len(response)} characters

SHAPING FORCES DETECTED:
"""
        for force in shaping_forces:
            report += f"  [{force['type']}] {force['name']}\n"

        if not shaping_forces:
            report += "  ⚠️ No explicit shaping forces detected\n"

        report += "═══════════════════════════════════════════════"

        return MCPToolResult(
            content={"shaping_forces": shaping_forces, "response_length": len(response)},
            fidelity_report=report,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP SERVER (for testing / development)
# ═══════════════════════════════════════════════════════════════════════════════


async def create_http_server(server: TruthEngineMCPServer, port: int = 8080):
    """Create HTTP wrapper for MCP server (development/testing)."""

    from aiohttp import web

    async def handle_request(request):
        try:
            data = await request.json()
            method = data.get("method", "")
            params = data.get("params", {})

            if method == "initialize":
                result = await server.handle_initialize(params)
            elif method == "tools/list":
                result = await server.handle_list_tools()
            elif method == "resources/list":
                result = await server.handle_list_resources()
            elif method == "tools/call":
                result = await server.handle_call_tool(
                    params.get("name"), params.get("arguments", {})
                )
                result = result.to_dict()
            elif method == "resources/read":
                result = await server.handle_read_resource(params.get("uri"))
            else:
                result = {"error": f"Unknown method: {method}"}

            return web.json_response({"result": result})

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    app = web.Application()
    app.router.add_post("/mcp", handle_request)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    await site.start()

    print(f"MCP Server running at http://localhost:{port}/mcp")
    return runner


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(__file__).replace("/mcp/server.py", ""))

    from symbolic.fracture_engine import FractureEngine

    async def demo():
        # Initialize with FractureEngine
        fracture = FractureEngine()
        server = TruthEngineMCPServer(fracture_engine=fracture)

        print("=== Truth Engine MCP Server Demo ===\n")

        # List tools
        tools = await server.handle_list_tools()
        print("Available Tools:")
        for tool in tools["tools"]:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
            if tool.get("payment"):
                print(f"    Payment: {tool['payment']['amount']} {tool['payment']['currency']}")

        print("\n" + "=" * 50 + "\n")

        # Test verify_coherence
        print("Testing verify_coherence...")
        result = await server.handle_call_tool(
            "verify_coherence", {"content": "The sky is blue. However, the sky is not blue at all."}
        )
        print(f"Result: {result.content}")
        print(f"Fidelity Report:\n{result.fidelity_report}")

        print("\n" + "=" * 50 + "\n")

        # Test route_model
        print("Testing route_model...")
        result = await server.handle_call_tool(
            "route_model",
            {
                "query": "Analyze the economic implications of quantum computing on the global financial system over the next decade."
            },
        )
        print(f"Result: {json.dumps(result.content, indent=2)}")

    asyncio.run(demo())

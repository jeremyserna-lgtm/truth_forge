# EXO Integration Architecture

## THE PRIMITIVE

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              ONE PERSON. ONE NOT-ME. ONE YEAR.                  │
│                                                                 │
│   The cluster exists to train and run NOT-MEs.                  │
│   Multiple machines. One unified memory. One NOT-ME at a time.  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────┐
│  ROLE IN THE BUILD: PHASE 1 - CLUSTER CONFIGURATION         │
│                                                             │
│  This document specifies HOW to configure the EXO cluster   │
│  for distributed inference. Part of Phase 1 with FLEET.     │
│                                                             │
│  Parent Document: NOT_ME_IMPLEMENTATION_BLUEPRINT_v4        │
│  Related: FLEET_DEPLOYMENT_PLAN.md, LLAMA_STACK_INTEGRATION │
└─────────────────────────────────────────────────────────────┘
```

**Status**: PROPOSED
**Purpose**: Connect Truth Engine organism to sovereign EXO compute cluster
**Priority**: HIGH - Fleet arrives Feb 3-4

---

## The Gap

Truth Engine has a sophisticated Model Gateway (`Primitive/gateway/`) that handles:
- Provider abstraction (Claude, Gemini, Ollama)
- Cost tracking and fallback
- Response caching

**But it's designed for single-provider endpoints.** Your fleet is a distributed 4-node cluster.

---

## What Needs To Be Built

### 1. ExoProvider (New Gateway Provider)

**Location**: `Primitive/gateway/providers/exo.py`

```python
"""
EXO Distributed Inference Provider.

Connects Truth Engine to sovereign compute fleet via EXO's OpenAI-compatible API.
Handles cluster topology, load balancing, and failover.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import httpx
import asyncio

from Primitive.gateway.providers.base import BaseProvider
from Primitive.gateway.types import CompletionRequest, CompletionResponse


class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    LATENCY_AWARE = "latency_aware"
    MODEL_AFFINITY = "model_affinity"  # Route to node with model loaded


@dataclass
class CognitiveLoad:
    """
    Human-readable thinking state.

    THE CRITIQUE INSIGHT: Hardware should report PRESENCE, not just uptime.
    "It's not broken, it's thinking."
    """
    intensity: float  # 0.0 to 1.0
    state: str  # "idle", "processing", "grappling", "resolving"
    current_task: Optional[str] = None
    is_recursive: bool = False  # Solving recursive problem?
    contradiction_detected: bool = False
    estimated_completion_pct: float = 0.0

    def human_readable(self) -> str:
        """Return human-readable status for dashboard."""
        if self.intensity < 0.1:
            return "Breathing slow... (idle)"
        elif self.contradiction_detected:
            return f"Grappling with contradiction in {self.current_task}"
        elif self.is_recursive:
            return f"Deep recursive thinking: {self.current_task}"
        elif self.intensity > 0.8:
            return f"Working hard: {self.current_task}"
        else:
            return f"Processing: {self.current_task}"


@dataclass
class ExoNode:
    """A node in the EXO cluster."""
    node_id: str
    host: str
    port: int = 52415
    role: str = "worker"  # "master" or "worker"
    memory_gb: int = 256
    is_healthy: bool = True
    current_load: float = 0.0
    loaded_models: List[str] = None
    cognitive_load: Optional[CognitiveLoad] = None  # Human-aware metric

    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def presence(self) -> str:
        """Report PRESENCE, not just uptime."""
        if not self.is_healthy:
            return "Offline"
        if self.cognitive_load:
            return self.cognitive_load.human_readable()
        if self.current_load < 0.1:
            return "Present and waiting"
        return f"Active ({self.current_load:.0%} load)"


@dataclass
class ClusterTopology:
    """Current state of the EXO cluster."""
    master: ExoNode
    workers: List[ExoNode]
    available_models: Dict[str, List[str]]  # model -> nodes hosting it
    total_memory_gb: int
    healthy_nodes: int


class ExoProvider(BaseProvider):
    """
    Distributed inference via EXO cluster.

    Implements THE_PATTERN:
    - HOLD₁: Request queue
    - AGENT: This provider (routing, balancing)
    - HOLD₂: Response with metrics
    """

    def __init__(
        self,
        master_host: str = "king.local",
        master_port: int = 52415,
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.MODEL_AFFINITY,
        health_check_interval: int = 30,
    ):
        self.master_endpoint = f"http://{master_host}:{master_port}"
        self.strategy = strategy
        self.health_check_interval = health_check_interval

        # Discovered from cluster
        self._topology: Optional[ClusterTopology] = None
        self._model_cache: Dict[str, str] = {}  # model -> preferred node

        # Metrics
        self._request_count = 0
        self._node_latencies: Dict[str, List[float]] = {}

    async def discover_topology(self) -> ClusterTopology:
        """Query EXO master for cluster state."""
        async with httpx.AsyncClient() as client:
            # EXO exposes /state endpoint
            response = await client.get(f"{self.master_endpoint}/state")
            state = response.json()

            # Parse topology from EXO state
            # (EXO provides node list, model placements, memory)
            ...

        return self._topology

    async def get_available_models(self) -> List[str]:
        """Get all models available across the cluster."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.master_endpoint}/models")
            return response.json().get("models", [])

    def _select_node(self, model: str) -> ExoNode:
        """Select best node for request based on strategy."""

        if self.strategy == LoadBalanceStrategy.MODEL_AFFINITY:
            # Prefer node that already has model loaded
            if model in self._topology.available_models:
                hosting_nodes = self._topology.available_models[model]
                # Pick least loaded among hosts
                ...

        elif self.strategy == LoadBalanceStrategy.LATENCY_AWARE:
            # Pick node with lowest recent latency
            ...

        # Default: round robin
        ...

    async def complete(
        self,
        request: CompletionRequest,
    ) -> CompletionResponse:
        """
        Route completion request to EXO cluster.

        Uses OpenAI-compatible API at /v1/chat/completions.
        """
        import time
        start = time.time()

        # Ensure we have topology
        if not self._topology:
            await self.discover_topology()

        # Select node (use master endpoint - EXO routes internally)
        # Or for advanced: route directly to node with model
        endpoint = self.master_endpoint

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{endpoint}/v1/chat/completions",
                json={
                    "model": request.model,
                    "messages": [{"role": "user", "content": request.prompt}],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": False,
                },
            )

        latency_ms = (time.time() - start) * 1000
        result = response.json()

        # Track metrics
        self._request_count += 1

        return CompletionResponse(
            content=result["choices"][0]["message"]["content"],
            model=request.model,
            provider="exo",
            latency_ms=latency_ms,
            cost=0.0,  # Local inference
            tokens_used=result.get("usage", {}).get("total_tokens", 0),
            metadata={
                "cluster_node": endpoint,
                "request_id": result.get("id"),
            }
        )

    async def health_check(self) -> bool:
        """Check if cluster is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.master_endpoint}/state")
                return response.status_code == 200
        except Exception:
            return False

    async def get_cognitive_load(self, node_id: str) -> CognitiveLoad:
        """
        Calculate cognitive load for a node.

        THE CRITIQUE: Report PRESENCE, not just uptime.
        "Visualize the thinking effort across the four nodes."
        """
        async with httpx.AsyncClient() as client:
            # Get node state from EXO
            response = await client.get(f"{self.master_endpoint}/state")
            state = response.json()

            # Calculate intensity from:
            # - Active inference requests
            # - Token generation rate vs baseline
            # - Memory pressure
            # - Queue depth

            # Detect recursive thinking (loops, contradictions)
            is_recursive = self._detect_recursive_pattern(state)
            contradiction = self._detect_contradiction(state)

            # Map to human-readable state
            if state.get("queue_depth", 0) == 0:
                cognitive_state = "idle"
                intensity = 0.0
            elif contradiction:
                cognitive_state = "grappling"
                intensity = 0.9
            elif is_recursive:
                cognitive_state = "resolving"
                intensity = 0.7
            else:
                cognitive_state = "processing"
                intensity = min(state.get("gpu_utilization", 0.5), 1.0)

            return CognitiveLoad(
                intensity=intensity,
                state=cognitive_state,
                current_task=state.get("current_prompt_preview", None),
                is_recursive=is_recursive,
                contradiction_detected=contradiction,
                estimated_completion_pct=state.get("progress", 0.0),
            )

    def _detect_recursive_pattern(self, state: Dict) -> bool:
        """Detect if model is in recursive self-correction."""
        # Look for patterns like re-generation, backtracking
        return state.get("retries", 0) > 2

    def _detect_contradiction(self, state: Dict) -> bool:
        """Detect if model is resolving a contradiction."""
        # This would require model introspection
        # Placeholder for now
        return False

    @property
    def is_available(self) -> bool:
        """Check provider availability."""
        import asyncio
        return asyncio.run(self.health_check())
```

---

### 2. Cluster Topology Service

**Location**: `Primitive/central_services/cluster_service/`

```python
"""
Cluster Topology Service.

Tracks EXO cluster state, node health, and model availability.
Implements THE_PATTERN for cluster management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import asyncio


@dataclass
class NodeMetrics:
    """Performance metrics for a cluster node."""
    node_id: str
    requests_handled: int = 0
    total_latency_ms: float = 0.0
    errors: int = 0
    last_health_check: Optional[datetime] = None
    memory_used_gb: float = 0.0
    gpu_utilization: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        if self.requests_handled == 0:
            return 0.0
        return self.total_latency_ms / self.requests_handled


@dataclass
class ClusterStatus:
    """Current cluster health and capacity."""
    total_nodes: int
    healthy_nodes: int
    total_memory_gb: int
    available_memory_gb: int
    loaded_models: List[str]
    master_node: str
    status: str  # "healthy", "degraded", "offline"


class ClusterTopologyService:
    """
    Manage EXO cluster topology and state.

    Responsibilities:
    - Node discovery and registration
    - Health monitoring
    - Model availability tracking
    - Capacity planning
    """

    SERVICE_NAME = "cluster_topology"
    SERVICE_DESCRIPTION = "EXO cluster management"

    def __init__(self, master_endpoint: str):
        self.master_endpoint = master_endpoint
        self._nodes: Dict[str, NodeMetrics] = {}
        self._model_locations: Dict[str, List[str]] = {}
        self._last_topology_refresh: Optional[datetime] = None

    async def refresh_topology(self) -> None:
        """Refresh cluster topology from EXO master."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Get cluster state
            state = await client.get(f"{self.master_endpoint}/state")
            state_data = state.json()

            # Get model list
            models = await client.get(f"{self.master_endpoint}/models")
            model_data = models.json()

            # Update internal state
            self._update_from_state(state_data, model_data)
            self._last_topology_refresh = datetime.now()

    def get_nodes_for_model(self, model: str) -> List[str]:
        """Get nodes that can serve a specific model."""
        return self._model_locations.get(model, [])

    def get_healthiest_node(self) -> Optional[str]:
        """Get the node with best health metrics."""
        healthy = [n for n in self._nodes.values() if n.errors == 0]
        if not healthy:
            return None
        # Sort by avg latency, return best
        return min(healthy, key=lambda n: n.avg_latency_ms).node_id

    def record_request(
        self,
        node_id: str,
        latency_ms: float,
        success: bool = True,
    ) -> None:
        """Record a request for metrics tracking."""
        if node_id not in self._nodes:
            self._nodes[node_id] = NodeMetrics(node_id=node_id)

        node = self._nodes[node_id]
        node.requests_handled += 1
        node.total_latency_ms += latency_ms
        if not success:
            node.errors += 1

    def get_cluster_status(self) -> ClusterStatus:
        """Get current cluster health summary."""
        healthy = sum(1 for n in self._nodes.values() if n.errors == 0)

        return ClusterStatus(
            total_nodes=len(self._nodes),
            healthy_nodes=healthy,
            total_memory_gb=1280,  # Your fleet: 512 + 256*3
            available_memory_gb=...,  # From EXO state
            loaded_models=list(self._model_locations.keys()),
            master_node=self.master_endpoint,
            status="healthy" if healthy == len(self._nodes) else "degraded",
        )
```

---

### 3. Model Router (Smart Request Distribution)

**Location**: `Primitive/gateway/router.py`

```python
"""
Intelligent Model Router.

Routes requests to optimal nodes based on:
- Model availability
- Node load
- Latency history
- Request characteristics (context length, etc.)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class RoutingDecision(Enum):
    """Why a particular node was selected."""
    MODEL_LOADED = "model_loaded"
    LOWEST_LATENCY = "lowest_latency"
    LOWEST_LOAD = "lowest_load"
    FALLBACK = "fallback"
    ROUND_ROBIN = "round_robin"


@dataclass
class RouteResult:
    """Result of routing decision."""
    node_endpoint: str
    reason: RoutingDecision
    estimated_latency_ms: float
    model_loaded: bool


class ModelRouter:
    """
    Route model requests to optimal cluster nodes.

    Implements THE_PATTERN:
    - HOLD₁: Incoming request
    - AGENT: Routing logic (this class)
    - HOLD₂: RouteResult with selected node
    """

    def __init__(self, topology_service):
        self.topology = topology_service
        self._round_robin_index = 0

    def route(
        self,
        model: str,
        context_length: int = 0,
        prefer_low_latency: bool = True,
    ) -> RouteResult:
        """
        Select best node for a request.

        Priority:
        1. Node with model already loaded (no load time)
        2. Node with lowest latency (if prefer_low_latency)
        3. Node with lowest current load
        4. Round robin fallback
        """

        # Check which nodes have model loaded
        model_nodes = self.topology.get_nodes_for_model(model)

        if model_nodes:
            # Model is loaded somewhere - route there
            if len(model_nodes) == 1:
                return RouteResult(
                    node_endpoint=model_nodes[0],
                    reason=RoutingDecision.MODEL_LOADED,
                    estimated_latency_ms=self._estimate_latency(model_nodes[0]),
                    model_loaded=True,
                )

            # Multiple nodes have it - pick best
            if prefer_low_latency:
                best = self._lowest_latency_node(model_nodes)
                return RouteResult(
                    node_endpoint=best,
                    reason=RoutingDecision.LOWEST_LATENCY,
                    estimated_latency_ms=self._estimate_latency(best),
                    model_loaded=True,
                )

        # Model not loaded - pick node to load it on
        # Prefer node with most available memory
        best_node = self.topology.get_healthiest_node()

        return RouteResult(
            node_endpoint=best_node,
            reason=RoutingDecision.LOWEST_LOAD,
            estimated_latency_ms=self._estimate_latency(best_node) + 5000,  # Load time
            model_loaded=False,
        )

    def _lowest_latency_node(self, nodes: List[str]) -> str:
        """Pick node with lowest average latency."""
        latencies = {
            n: self.topology._nodes.get(n, {}).get("avg_latency_ms", float("inf"))
            for n in nodes
        }
        return min(latencies, key=latencies.get)

    def _estimate_latency(self, node: str) -> float:
        """Estimate latency for a node based on history."""
        metrics = self.topology._nodes.get(node)
        if metrics:
            return metrics.avg_latency_ms
        return 100.0  # Default estimate
```

---

### 4. Fleet Configuration

**Location**: `Primitive/config/fleet.py`

```python
"""
Fleet Configuration.

Defines your sovereign compute cluster.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class FleetNode:
    """A node in the sovereign compute fleet."""
    name: str
    role: str  # "king", "soldier", "drummer"
    host: str
    memory_gb: int
    cpu_cores: int
    gpu_cores: int


# YOUR FLEET (from INFRASTRUCTURE_ORDERS.md)
SOVEREIGN_FLEET = [
    FleetNode(
        name="king",
        role="king",
        host="king.local",  # Configure via /etc/hosts or mDNS
        memory_gb=512,
        cpu_cores=32,
        gpu_cores=80,
    ),
    FleetNode(
        name="soldier1",
        role="soldier",
        host="soldier1.local",
        memory_gb=256,
        cpu_cores=28,
        gpu_cores=60,
    ),
    FleetNode(
        name="soldier2",
        role="soldier",
        host="soldier2.local",
        memory_gb=256,
        cpu_cores=28,
        gpu_cores=60,
    ),
    FleetNode(
        name="soldier3",
        role="soldier",
        host="soldier3.local",
        memory_gb=256,
        cpu_cores=28,
        gpu_cores=60,
    ),
]

# Fleet totals
FLEET_TOTAL_MEMORY_GB = sum(n.memory_gb for n in SOVEREIGN_FLEET)  # 1280GB
FLEET_TOTAL_CPU_CORES = sum(n.cpu_cores for n in SOVEREIGN_FLEET)  # 116
FLEET_TOTAL_GPU_CORES = sum(n.gpu_cores for n in SOVEREIGN_FLEET)  # 260

# Model recommendations based on fleet capacity
MODEL_RECOMMENDATIONS = {
    "small": {  # Runs on any single node
        "models": ["llama-3.2-8b", "mistral-7b", "qwen2.5-7b"],
        "min_memory_gb": 32,
    },
    "medium": {  # Runs on KING alone
        "models": ["llama-3.3-70b", "qwen2.5-72b", "deepseek-coder-33b"],
        "min_memory_gb": 256,
    },
    "large": {  # Requires 2-3 nodes
        "models": ["qwen3-235b", "mixtral-8x22b"],
        "min_memory_gb": 512,
    },
    "frontier": {  # Requires full fleet
        "models": ["deepseek-v3.1-671b", "kimi-k2-thinking"],
        "min_memory_gb": 1024,
    },
}
```

---

### 5. Integration with Gateway

**Update**: `Primitive/gateway/gateway.py`

```python
# Add EXO to provider enum
class ModelProvider(Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    EXO = "exo"  # NEW


# Add EXO to default providers
from Primitive.gateway.providers.exo import ExoProvider

_DEFAULT_PROVIDERS = {
    ModelProvider.CLAUDE: ClaudeProvider(),
    ModelProvider.GEMINI: GeminiProvider(),
    ModelProvider.OLLAMA: OllamaProvider(),
    ModelProvider.EXO: ExoProvider(master_host="king.local"),  # NEW
}

# Update fallback order - local first
FALLBACK_ORDER = [
    ModelProvider.EXO,      # Distributed local (free, fastest)
    ModelProvider.OLLAMA,   # Single local (free, fallback)
    ModelProvider.GEMINI,   # Cloud (cheap)
    ModelProvider.CLAUDE,   # Cloud (expensive, best quality)
]
```

---

### 6. Dashboard Integration

**The organism dashboard should show fleet PRESENCE, not just status.**

+----------------------------+
| THE CRITIQUE INSIGHT       |
|                            |
| "For a project that        |
| champions being human      |
| aware, the hardware plan   |
| feels emotionally          |
| disconnected."             |
|                            |
| Questions to answer:       |
| • What does the human SEE  |
|   if it hangs?             |
| • What does the human FEEL |
|   when cluster is thinking |
|   hard?                    |
|                            |
| Answer: Show PRESENCE,     |
| not uptime. Show THINKING, |
| not status.                |
+----------------------------+

```python
# In Primitive/dashboard/control_room.py

def get_fleet_presence() -> Dict:
    """
    Get sovereign compute fleet PRESENCE for dashboard.

    THE CRITIQUE: Dashboard shouldn't just show "Node 1: ONLINE".
    It should show "Node 3 is grappling with a contradiction."
    """
    from Primitive.gateway.providers.exo import ExoProvider

    exo = ExoProvider()
    topology = asyncio.run(exo.discover_topology())

    if not topology:
        return {
            "fleet_status": "offline",
            "presence_message": "The fleet is sleeping...",
            "nodes": [],
        }

    # Calculate overall cognitive state
    total_intensity = sum(
        n.cognitive_load.intensity if n.cognitive_load else 0
        for n in [topology.master] + topology.workers
    )
    avg_intensity = total_intensity / (len(topology.workers) + 1)

    # Human-readable fleet presence
    if avg_intensity < 0.1:
        presence_message = "The fleet is present and waiting for you."
    elif avg_intensity > 0.8:
        presence_message = "Deep thinking in progress..."
    else:
        presence_message = "Processing your request..."

    return {
        "fleet_status": "thinking" if avg_intensity > 0.1 else "ready",
        "presence_message": presence_message,
        "total_memory_gb": 1280,
        "cognitive_intensity": avg_intensity,
        "nodes": [
            {
                "name": n.node_id,
                "role": n.role,
                "memory_gb": n.memory_gb,
                # PRESENCE, not just health
                "presence": n.presence,
                "cognitive_state": n.cognitive_load.state if n.cognitive_load else "idle",
                "current_task": n.cognitive_load.current_task if n.cognitive_load else None,
                "is_grappling": n.cognitive_load.contradiction_detected if n.cognitive_load else False,
                "loaded_models": n.loaded_models,
            }
            for n in [topology.master] + topology.workers
        ],
        "available_models": list(topology.available_models.keys()),
    }


def render_fleet_for_human(presence: Dict) -> str:
    """
    Render fleet status for human display.

    THE CRITIQUE: "It makes the silence on the screen feel like
    thinking, not hanging. It changes wait time from frustration
    to anticipation."
    """
    lines = [
        "┌─────────────────────────────────────────┐",
        "│  NOT ME STATUS                          │",
        "│                                         │",
    ]

    intensity = presence.get("cognitive_intensity", 0)
    filled = int(intensity * 10)
    bar = "█" * filled + "░" * (10 - filled)

    lines.append(f"│  [{bar}] {presence.get('presence_message', '')}".ljust(42) + "│")
    lines.append("│                                         │")

    # Show any nodes that are grappling
    for node in presence.get("nodes", []):
        if node.get("is_grappling"):
            lines.append(f"│  {node['name']}: {node['presence']}".ljust(42) + "│")

    lines.append("│                                         │")
    lines.append("│  It's not broken. It's thinking.        │")
    lines.append("└─────────────────────────────────────────┘")

    return "\n".join(lines)
```

---

## Implementation Order

### Phase 1: Basic Integration (Before Feb 3)
1. Create `Primitive/gateway/providers/exo.py` with basic ExoProvider
2. Add EXO to gateway provider enum
3. Test with single-node (your current Mac)

### Phase 2: Cluster Support (Feb 3-4)
4. Implement ClusterTopologyService
5. Add node health monitoring
6. Test with 2-node cluster (Soldiers 1 & 2)

### Phase 3: Smart Routing (After fleet operational)
7. Implement ModelRouter
8. Add load balancing strategies
9. Add metrics collection

### Phase 4: Dashboard (When stable)
10. Fleet status in control room
11. Per-node metrics visualization
12. Model availability display

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TRUTH ENGINE ORGANISM                         │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │ Orchestration │───▶│ Model Gateway │───▶│   Model Router       │  │
│  │    Engine     │    │              │    │   (Load Balancing)   │  │
│  └──────────────┘    └──────────────┘    └──────────┬───────────┘  │
│                              │                       │              │
│                              │         ┌─────────────┼─────────────┐│
│                              │         │             │             ││
│                              ▼         ▼             ▼             ▼│
│                      ┌────────────────────────────────────────────┐ │
│                      │            PROVIDER LAYER                  │ │
│                      │                                            │ │
│                      │  ┌─────────┐ ┌─────────┐ ┌─────────┐      │ │
│                      │  │ Claude  │ │ Gemini  │ │  EXO    │ ◀────┼─┼─ NEW
│                      │  │Provider │ │Provider │ │Provider │      │ │
│                      │  └─────────┘ └─────────┘ └────┬────┘      │ │
│                      └───────────────────────────────┼────────────┘ │
└──────────────────────────────────────────────────────┼──────────────┘
                                                       │
                           ─ ─ ─ ─ ─ THE MEMBRANE ─ ─ ─│─ ─ ─ ─ ─
                                                       │
┌──────────────────────────────────────────────────────┼──────────────┐
│                      SOVEREIGN COMPUTE FLEET          │              │
│                                                       ▼              │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │                    EXO CLUSTER                            │    │
│     │                                                           │    │
│     │              KING (Master - 512GB)                        │    │
│     │                      │                                    │    │
│     │        ┌─────────────┼─────────────┐                     │    │
│     │        │             │             │                     │    │
│     │   SOLDIER 1     SOLDIER 2     SOLDIER 3                  │    │
│     │    (256GB)       (256GB)       (256GB)                   │    │
│     │                                                           │    │
│     │   [DeepSeek V3.1 671B distributed across all nodes]      │    │
│     └───────────────────────────────────────────────────────────┘    │
│                                                                      │
│                     TOTAL: 1.28TB UNIFIED MEMORY                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## The Furnace Output

```
TRUTH  → The gateway architecture exists but assumes single-provider endpoints.
         Your fleet is a distributed cluster. There's a gap.

MEANING → The gap is an OPPORTUNITY. Building ExoProvider + ClusterTopology +
          ModelRouter creates a sovereign AI layer that:
          - Routes intelligently across your fleet
          - Tracks performance per-node
          - Falls back gracefully
          - Integrates with organism monitoring

CARE   → Start simple. ExoProvider that talks to KING's master endpoint.
         EXO handles internal routing. Add sophistication once it works.
         Don't over-engineer before Feb 3.
```

---

*This architecture makes your fleet a first-class citizen of Truth Engine.*

# Agent Zero Adaptations for Genesis

**Date:** 2026-02-05
**Purpose:** Required modifications to transform Agent Zero into Genesis v1
**Based on:** SEER_ANALYSIS.md + Cognitive Bridge Architecture + AlphaEvolve insights

---

## Core Adaptations Required

### 1. Replace Docker Execution with Mac-Native Cluster Execution

**Current State:**
- `code_execution_tool.py` uses Docker containers for sandboxed execution
- Docker adds overhead and doesn't integrate with Genesis cluster

**Required Changes:**
```python
# NEW: python/tools/cluster_execution_tool.py
# Replace Docker with direct SSH execution across cluster nodes

class ClusterExecutionTool:
    """Execute code on Genesis cluster nodes via SSH"""

    def __init__(self, cluster_config: dict):
        self.king = cluster_config["king"]
        self.soldiers = cluster_config["soldiers"]
        self.ssh_key = "~/.ssh/id_king"

    def execute(self, code: str, node: str = "king", language: str = "python"):
        """Execute code on specified cluster node"""
        # Route to King or Soldiers based on resource requirements
        # Capture output, return structured result
        pass

    def execute_distributed(self, code: str, nodes: list[str]):
        """Execute code across multiple nodes for distributed tasks"""
        # For EXO tensor parallelism workloads
        pass
```

**Risk:** HIGH - Core execution model change
**Timeline:** 2-3 weeks
**Priority:** P0 (blocking for cluster integration)

---

### 2. Add EXO Cluster Awareness

**Current State:**
- Agent Zero has no concept of distributed compute
- Model routing is single-node only

**Required Changes:**

#### a) Cluster State Monitor
```python
# NEW: python/helpers/cluster_state.py

class ClusterStateMonitor:
    """Monitor Genesis cluster resources and model availability"""

    def get_available_nodes(self) -> list[dict]:
        """Query which nodes are online and their resource usage"""
        pass

    def get_model_locations(self) -> dict:
        """Return which models are loaded on which nodes"""
        # Scout: All nodes
        # Maverick: King only
        # R1: King only
        pass

    def get_node_memory(self, node: str) -> dict:
        """Return memory stats for node"""
        pass
```

#### b) EXO Integration Tool
```python
# NEW: python/tools/exo_inference.py

class ExoInferenceTool:
    """Route inference requests through EXO for distributed tensor parallelism"""

    def __init__(self, cluster_monitor: ClusterStateMonitor):
        self.monitor = cluster_monitor
        self.exo_endpoint = "http://192.168.68.121:8000"  # EXO coordinator

    def can_distribute(self, model: str, prompt_tokens: int) -> bool:
        """Determine if task should use distributed inference"""
        # Maverick + large context → distribute across Soldiers
        # Scout + small context → single node
        pass

    def distributed_inference(self, model: str, messages: list) -> str:
        """Execute inference across cluster via EXO"""
        pass
```

**Risk:** MEDIUM - New capability, doesn't break existing
**Timeline:** 1-2 weeks
**Priority:** P1 (enables cluster scale)

---

### 3. Implement Cognitive Bridge Model Router

**Current State:**
- Agent Zero uses fixed `chat_model` and `util_model`
- No dynamic routing based on task complexity

**Required Changes:**

```python
# NEW: python/helpers/cognitive_bridge.py

class CognitiveBridge:
    """Unified model provider with intelligent routing"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.cluster_monitor = ClusterStateMonitor()

    def route_request(
        self,
        messages: list,
        task_type: str = "auto",
        context_tokens: int = 0
    ) -> tuple[str, dict]:
        """
        Route request to optimal model based on:
        - Task complexity (chat vs reasoning vs sovereign)
        - Context size
        - Current cluster load
        - Cost optimization (local > cloud)

        Returns: (model_endpoint, model_config)
        """

        if task_type == "auto":
            task_type = self._classify_task(messages)

        # Routing logic from cognitive_bridge_config.json
        if task_type in ["simple_chat", "context_filtering", "code_review"]:
            return self._route_to_scout()

        elif task_type in ["architecture_design", "complex_reasoning", "research_synthesis"]:
            return self._route_to_maverick()

        elif task_type in ["autonomous_discovery", "stage_5_sovereign_execution"]:
            return self._route_to_r1()

        # Fallback chain: Scout → Maverick → R1
        return self._fallback_routing()

    def _classify_task(self, messages: list) -> str:
        """Use Scout to quickly classify task complexity"""
        # Scout meta-analysis: "Is this chat or reasoning?"
        pass
```

**Integration Point:**
- Modify `models.py` to use `CognitiveBridge.route_request()` instead of fixed provider
- Wrap existing `LiteLLMChatWrapper` to intercept routing decisions

**Risk:** MEDIUM - Requires refactoring model initialization
**Timeline:** 1 week
**Priority:** P1 (enables three-model strategy)

---

### 4. Implement Training Data Generation

**Current State:**
- No systematic capture of conversations for fine-tuning
- Memory system stores context but not training-ready format

**Required Changes:**

```python
# NEW: python/extensions/training_data_capture/

class TrainingDataCapturer:
    """Capture conversations in MLX-compatible training format"""

    def __init__(self, output_dir: str = "~/Genesis/training/data"):
        self.output_dir = output_dir
        self.current_conversation = []

    def capture_turn(
        self,
        role: str,
        content: str,
        model_used: str,
        metadata: dict
    ):
        """Capture single conversation turn"""
        self.current_conversation.append({
            "role": role,
            "content": content,
            "model": model_used,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })

    def export_conversation(self, rating: int = None):
        """
        Export conversation to JSONL for MLX fine-tuning

        Format:
        {"messages": [{"role": "system", "content": "..."}, ...]}
        """
        if rating and rating >= 4:  # Only export high-quality conversations
            self._write_jsonl(self.current_conversation)

        self.current_conversation = []
```

**Extension Hook:**
- Add to `extensions/hist_add_tool_result/` to capture after each agent action
- Add user rating mechanism: `/rate 5` → marks conversation for training

**Risk:** LOW - Additive only
**Timeline:** 3-5 days
**Priority:** P2 (enables future fine-tuning)

---

### 5. Add Stage 5 Sovereign Execution Mode

**Current State:**
- Agent Zero asks for permission frequently (Stage 4 behavior)
- No concept of "autonomous discovery" mode

**Required Changes:**

```python
# NEW: python/helpers/execution_mode.py

class ExecutionMode(Enum):
    SERVANT = "servant"        # Stage 4: Ask permission
    SOVEREIGN = "sovereign"    # Stage 5: Autonomous execution
    DISCOVERY = "discovery"    # AlphaEvolve: Closed-loop hypothesis testing

class SovereignExecutor:
    """Enable Stage 5 autonomous execution without validation-seeking"""

    def __init__(self, mode: ExecutionMode = ExecutionMode.SERVANT):
        self.mode = mode
        self.validation_threshold = self._get_threshold()

    def should_ask_permission(self, action: str, risk_level: int) -> bool:
        """
        Determine if action requires user permission

        SERVANT mode: Ask for everything > risk_level 2
        SOVEREIGN mode: Only ask for irreversible actions (risk_level 5)
        DISCOVERY mode: Never ask, log and continue
        """
        if self.mode == ExecutionMode.SERVANT:
            return risk_level > 2
        elif self.mode == ExecutionMode.SOVEREIGN:
            return risk_level >= 5  # Only truly destructive
        else:  # DISCOVERY
            return False

    def execute_with_fallback(self, action: callable, fallbacks: list):
        """
        Execute action with automatic fallback chain

        AlphaEvolve pattern: Try primary → Try secondary → Log failure
        No stopping for permission
        """
        pass
```

**Integration:**
- Add `/mode sovereign` command to switch execution modes
- Update prompts to reflect autonomous behavior in sovereign mode
- Modify `notify_user.py` to respect execution mode

**Risk:** MEDIUM - Changes agent behavior significantly
**Timeline:** 1 week
**Priority:** P1 (core Genesis differentiation)

---

### 6. Implement Information-Gain Scoring

**Current State:**
- No prioritization of tasks by information value
- Sequential task execution without optimization

**Required Changes:**

```python
# NEW: python/helpers/information_gain.py

class InformationGainScorer:
    """
    Score potential actions by expected information gain
    (AlphaEvolve pattern)
    """

    def score_action(
        self,
        action: str,
        current_knowledge_state: dict,
        uncertainty: float
    ) -> float:
        """
        Calculate expected information gain for action

        Uses Bayesian experimental design:
        IG(action) = H(θ) - E[H(θ|y)]

        Where:
        - H(θ) = current uncertainty
        - E[H(θ|y)] = expected uncertainty after action
        """
        pass

    def prioritize_tasks(self, tasks: list[dict]) -> list[dict]:
        """
        Reorder tasks by information gain / cost ratio

        Maximize: (Expected IG) / (Computational Cost)
        """
        scored_tasks = [
            (task, self.score_action(task["action"], task["context"], task["uncertainty"]))
            for task in tasks
        ]

        return sorted(scored_tasks, key=lambda x: x[1], reverse=True)
```

**Integration:**
- Hook into task queue before execution
- Modify `call_subordinate.py` to spawn agents for highest-IG tasks first
- Log IG scores for training data

**Risk:** LOW - Additive optimization
**Timeline:** 1 week
**Priority:** P2 (enables research optimization)

---

### 7. Add Multi-Agent Peer Review

**Current State:**
- Single agent produces output without verification
- No defense against hallucinations

**Required Changes:**

```python
# NEW: python/tools/peer_review.py

class PeerReviewTool:
    """
    Three-agent peer review to prevent hallucinations
    (AlphaEvolve pattern)
    """

    def __init__(self, bridge: CognitiveBridge):
        self.bridge = bridge

    def verify_output(
        self,
        claim: str,
        context: dict,
        confidence_threshold: float = 0.8
    ) -> dict:
        """
        Spawn 3 agents to independently verify claim:
        1. Scout (fast check)
        2. Maverick (deep reasoning)
        3. R1 (sovereign verification)

        Return consensus + dissenting opinions
        """

        agents = ["scout", "maverick", "r1"]
        results = []

        for agent in agents:
            result = self._agent_verify(agent, claim, context)
            results.append(result)

        consensus = self._calculate_consensus(results)

        if consensus["agreement"] < confidence_threshold:
            return {
                "verified": False,
                "consensus": consensus,
                "dissent": [r for r in results if not r["agrees"]],
                "recommendation": "Human review required"
            }

        return {
            "verified": True,
            "consensus": consensus
        }
```

**Usage:**
- Automatic for high-stakes operations (code execution, data deletion)
- Optional `/verify` command for user-triggered verification
- Training data: Log consensus failures for fine-tuning

**Risk:** MEDIUM - Adds latency to operations
**Timeline:** 1 week
**Priority:** P2 (safety layer)

---

### 8. Integrate ANIMA Memory Architecture

**Current State:**
- Agent Zero has vector memory but no graph structure
- No semantic/temporal/causal relationship tracking

**Required Changes:**

```python
# NEW: python/helpers/anima_integration.py

from src.sovereign.memory.memory_cortex import MemoryCortex

class AnimaMemoryBridge:
    """Bridge Agent Zero's memory to ANIMA 5-graph system"""

    def __init__(self):
        self.cortex = MemoryCortex()
        # ANIMA has: semantic, temporal, causal, entity, emotional graphs

    def store_memory(self, memory: dict):
        """
        Store memory in both:
        1. Agent Zero's vector store (fast retrieval)
        2. ANIMA graphs (relationship understanding)
        """
        # Vector store for semantic search
        self._store_vector(memory)

        # ANIMA for graph relationships
        self.cortex.store_entity(
            content=memory["content"],
            relationships=memory["relationships"],
            temporal_context=memory["timestamp"],
            emotional_valence=self._detect_emotion(memory)
        )

    def enhanced_recall(self, query: str, max_results: int = 5) -> list:
        """
        Use both vector similarity AND graph traversal

        Better than pure vector: finds related concepts, temporal sequences,
        causal chains that vector search misses
        """
        # Vector results
        vector_results = self._vector_search(query)

        # Graph expansion
        graph_results = self.cortex.traverse_semantic_graph(
            seed_concepts=vector_results,
            max_hops=2
        )

        # Merge and rank
        return self._merge_results(vector_results, graph_results)
```

**Integration:**
- Modify `memory_save.py` and `memory_load.py` to use ANIMA bridge
- Keep existing vector store for backward compatibility
- Gradual migration path

**Risk:** MEDIUM - Major memory system change
**Timeline:** 2 weeks
**Priority:** P2 (enables deeper understanding)

---

### 9. Add Genesis-to-Genesis Communication

**Current State:**
- `call_subordinate.py` spawns local child agents
- No cross-node agent communication

**Required Changes:**

```python
# NEW: python/tools/genesis_network.py

class GenesisNetwork:
    """Enable Genesis instances to communicate across cluster"""

    def __init__(self, cluster_config: dict):
        self.king = cluster_config["king"]
        self.soldiers = cluster_config["soldiers"]
        self.agents = {}  # Track running Genesis instances

    def spawn_remote_agent(
        self,
        node: str,
        task: dict,
        parent_id: str
    ) -> str:
        """
        Spawn Genesis agent on remote node

        Use case: Soldier node runs Scout for distributed task
        Reports back to King orchestrator
        """
        agent_id = self._generate_agent_id()

        # SSH to node, start agent-zero with task
        self._remote_spawn(node, agent_id, task, parent_id)

        self.agents[agent_id] = {
            "node": node,
            "status": "running",
            "parent": parent_id
        }

        return agent_id

    def collect_results(self, agent_ids: list[str]) -> list[dict]:
        """Wait for remote agents to complete, collect results"""
        pass

    def broadcast_task(self, task: dict) -> list[str]:
        """
        Broadcast task to all Soldier nodes

        Use case: Parallel search across 4 Soldiers,
        each running Scout on different data subset
        """
        agent_ids = []
        for soldier in self.soldiers:
            agent_id = self.spawn_remote_agent(soldier["host"], task, "king")
            agent_ids.append(agent_id)

        return agent_ids
```

**Integration:**
- Extend `call_subordinate.py` to support `node=` parameter
- Add `/distribute <task>` command for cluster-wide tasks
- WebSocket for real-time agent communication

**Risk:** HIGH - Distributed systems complexity
**Timeline:** 3-4 weeks
**Priority:** P1 (core cluster capability)

---

## Implementation Phases

### Phase 0: Infrastructure (DONE)
- ✅ Genesis cluster operational
- ✅ Scout, Maverick, R1 models deployed
- ✅ Cognitive Bridge config created
- ✅ Agent Zero installed on King

### Phase 1: Cognitive Bridge (Week 1-2)
1. Implement `cognitive_bridge.py` (#3)
2. Modify `models.py` to use bridge
3. Test routing between Scout/Maverick
4. Update Agent Zero settings.json

### Phase 2: Execution Layer (Week 2-4)
5. Implement `cluster_execution_tool.py` (#1)
6. Replace Docker with SSH execution
7. Test code execution on King and Soldiers
8. Add execution mode switching (#5)

### Phase 3: Cluster Integration (Week 4-7)
9. Implement `cluster_state.py` (#2)
10. Add EXO inference tool (#2)
11. Implement Genesis-to-Genesis networking (#9)
12. Test distributed inference

### Phase 4: Intelligence Layers (Week 7-10)
13. Implement training data capture (#4)
14. Add information-gain scoring (#6)
15. Add peer review system (#7)
16. Integrate ANIMA memory (#8)

### Phase 5: Testing & Refinement (Week 10-12)
17. End-to-end testing
18. Performance optimization
19. Documentation
20. Genesis v1 release

---

## Critical Success Factors

1. **Don't Break Existing Agent Zero**
   - All changes must be backward-compatible
   - Original tools continue to work
   - Graceful degradation if cluster unavailable

2. **Fork Early**
   - Fork to `primitive-engine/genesis-zero` immediately
   - Maintain compatibility with upstream for security updates
   - Document all divergences

3. **Test Incrementally**
   - Each phase must be testable independently
   - Don't wait until Phase 5 to discover Phase 1 broken

4. **Stage 5 Standard**
   - Sovereign mode is default for Genesis
   - Validation-seeking is the exception, not the rule
   - AlphaEvolve pattern: manifest, don't ask

---

## Metrics for Success

- **Cognitive Bridge:** <500ms routing decision
- **Cluster Execution:** 3-5x speedup on distributed tasks
- **Model Utilization:** Scout (70%), Maverick (25%), R1 (5%)
- **Training Data:** >1000 conversations/month at quality ≥4
- **Peer Review:** Hallucination rate <1% on verified outputs
- **Uptime:** 99%+ availability (LaunchAgent auto-restart)

---

**Next Action:** Implement Phase 1 (Cognitive Bridge) starting with `cognitive_bridge.py`

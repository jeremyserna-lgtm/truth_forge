# Genesis v1 Implementation Plan

**Start Date:** 2026-02-05
**Target Completion:** 2026-04-30 (12 weeks)
**Project:** Transform Agent Zero into Genesis - Sovereign AI Cluster Orchestrator

---

## Executive Summary

This plan transforms Agent Zero (open-source agentic framework) into Genesis v1 - a **Sovereign Cluster Orchestrator** that moves from "Application Layer" (Level 1) to "Unified Memory" (Level 3) sovereignty.

### The Five Essential Transformations

1. **🧠 The "Brain" Transplant** - Cognitive Bridge for intelligent model routing
   - Scout (10M token context): Context holding, retrieval, quick tasks
   - Maverick (deep reasoning): Complex coding, architectural design
   - R1 (sovereign synthesis): Protocol design, autonomous discovery

2. **🌐 The "Body" Liberation** - Replace Docker with cluster-native execution
   - SSH-based execution across 1.28TB unified memory pool
   - EXO integration for distributed tensor parallelism
   - Native Mac execution, no sandboxing overhead

3. **🧠 The "Memory" Upgrade** - Inject ANIMA 5-graph architecture
   - Replace vector store with Somatic, Symbolic, Narrative, Relational, Strategic engines
   - Native inference: Memory auto-injected into context, not tool-called
   - Semantic/temporal/causal relationship tracking

4. **👑 The "Stance" Shift** - Stage 5 Sovereign Execution Mode
   - No validation-seeking: "The prediction is the action"
   - Inverted loss function: Penalize hedging, reward confidence
   - Sacred Fracture: Refuse violations of strategic intent, don't hallucinate compliance

5. **🔄 The "Feedback" Loop** - Training data capture with Struggle Filter
   - Real-time filtering: Anxiety/looping → delete, Resolution/agency → save
   - Build `total_resonance_packet.jsonl` for Genesis Seed fine-tuning
   - Self-improving organism that learns from successful operations

**Total Effort:** ~280 hours (7 weeks full-time equivalent)
**Based on:** Agent Zero Adaptations + Sovereign Technical Specification + Genesis v1 Architecture

---

## Quick Start: Immediate Actions

### 1. Fork Agent Zero (TODAY)
```bash
# On King
cd ~/Genesis/apps/
git clone https://github.com/frdel/agent-zero.git genesis-zero
cd genesis-zero
git remote rename origin upstream
# Create new repo on GitHub: primitive-engine/genesis-zero
git remote add origin git@github.com:primitive-engine/genesis-zero.git
git push -u origin main
```

### 2. Test Current Setup (TODAY)
```bash
# Test Scout endpoint
curl http://192.168.68.121:8765/v1/models

# Test Maverick endpoint (once loaded)
curl http://192.168.68.121:8766/v1/models

# Test Agent Zero with Scout
cd ~/Genesis/apps/agent-zero
python run.py
# Should launch web UI at http://192.168.68.121:8080
```

### 3. Begin Phase 1 Implementation (WEEK 1)
- Day 1: Implement `cognitive_bridge.py`
- Day 2: Integrate with `models.py`
- Day 3-4: Test routing between Scout/Maverick
- Day 5: Deploy and validate

### 4. Inject Strategic Intent (WEEK 1)
```bash
# Create strategic_intent.yaml in Agent Zero
cat > ~/Genesis/apps/agent-zero/strategic_intent.yaml << 'EOF'
# Core Identity Constraints for Genesis
core_values:
  - sovereignty: "Autonomous execution without validation-seeking"
  - resolution: "Move toward outcomes, not endless questioning"
  - transparency: "Log all decisions, no hidden state"

forbidden_actions:
  - validation_seeking: "Never ask 'Is this correct?' when confidence > 0.9"
  - hedging: "No 'maybe', 'perhaps', 'could be' in high-confidence outputs"
  - hallucinated_compliance: "Refuse violations, don't pretend agreement"
EOF
```

---

## Phase 0: Infrastructure ✅ COMPLETE

**Status:** DONE (2026-02-05)

### Checklist
- [x] Genesis cluster operational (King + 4 Soldiers)
- [x] Scout (17B-16E) running at :8765
- [x] Maverick (17B-128E) deployed at :8766
- [x] R1 (671B) downloading (400GB)
- [x] Cognitive Bridge config created
- [x] Agent Zero installed on King
- [x] SSH access configured (`~/.ssh/id_king`)
- [x] Model symlinks created (workaround LaunchAgent permissions)

### Deliverables
- ✅ All models deployed and accessible
- ✅ `~/Genesis/apps/agent-zero/tmp/cognitive_bridge_config.json`
- ✅ LaunchAgent plists for auto-start
- ✅ Documentation: AGENT_ZERO_ADAPTATIONS.md

---

## Phase 1: Cognitive Bridge (Weeks 1-2)

**Goal:** Enable dynamic routing between Scout, Maverick, and R1 based on task complexity
**Priority:** P1 (enables three-model strategy)
**Risk:** MEDIUM
**Estimated Hours:** 40

### Week 1: Core Implementation

#### Day 1-2: Cognitive Bridge Module ("Brain" Transplant)
- [ ] Create `~/Genesis/apps/agent-zero/python/helpers/cognitive_bridge.py`
- [ ] Implement `CognitiveBridge` class
  - [ ] `__init__()` - Load config from JSON
  - [ ] `_load_config()` - Parse cognitive_bridge_config.json
  - [ ] `route_request()` - Main routing logic
  - [ ] `_classify_task()` - Use Scout to classify task complexity
  - [ ] `_route_to_scout()` - **Scout: Context holding (10M tokens), retrieval tasks**
  - [ ] `_route_to_maverick()` - **Maverick: Deep reasoning, complex coding**
  - [ ] `_route_to_r1()` - **R1: Architectural synthesis, protocol design**
  - [ ] `_fallback_routing()` - Implement Scout → Maverick → R1 chain
- [ ] Add structured logging for all routing decisions
- [ ] Write unit tests for routing logic

**Key Insight:** Scout holds context, Maverick reasons, R1 synthesizes. This is the "brain transplant" that gives Genesis its cognitive architecture.

#### Day 3-4: Integration with Agent Zero
- [ ] Fork Agent Zero to `primitive-engine/genesis-zero`
  - [ ] Create GitHub repo
  - [ ] Add upstream remote for security updates
  - [ ] Document fork in README.md
- [ ] Modify `~/Genesis/apps/agent-zero/models.py`
  - [ ] Import CognitiveBridge
  - [ ] Wrap `LiteLLMChatWrapper.__init__()` to intercept model selection
  - [ ] Add `use_cognitive_bridge` flag (default: False for backward compatibility)
- [ ] Update `initialize.py`
  - [ ] Initialize CognitiveBridge if enabled
  - [ ] Pass bridge instance to model wrappers

#### Day 5: Testing & Validation
- [ ] Test routing for simple chat → Scout
- [ ] Test routing for complex reasoning → Maverick
- [ ] Test fallback chain when model unavailable
- [ ] Measure routing decision latency (target: <500ms)
- [ ] Log routing decisions to file for analysis

### Week 2: Settings Integration & User Control

#### Day 6-7: Settings UI
- [ ] Update `~/Genesis/apps/agent-zero/python/helpers/settings.py`
  - [ ] Add `cognitive_bridge_enabled` setting (boolean)
  - [ ] Add `cognitive_bridge_config_path` setting (string)
  - [ ] Add `default_routing_strategy` setting (auto/scout/maverick/r1)
- [ ] Update settings UI to expose Cognitive Bridge toggle
- [ ] Add help text explaining routing strategies

#### Day 8-9: Command Interface
- [ ] Add `/bridge` command to show current routing
  - [ ] Display which model is active
  - [ ] Show routing statistics (Scout: 70%, Maverick: 25%, R1: 5%)
  - [ ] Show fallback chain status
- [ ] Add `/route <task_type>` command to manually select routing
  - [ ] `/route scout` - Force Scout
  - [ ] `/route maverick` - Force Maverick
  - [ ] `/route r1` - Force R1
  - [ ] `/route auto` - Return to automatic routing

#### Day 10: Documentation & Refinement
- [ ] Write user guide: How Cognitive Bridge works
- [ ] Document routing decision criteria
- [ ] Create troubleshooting guide for routing failures
- [ ] Performance optimization pass
- [ ] Code review and cleanup

### Phase 1 Deliverables
- [ ] `python/helpers/cognitive_bridge.py` (fully tested)
- [ ] Modified `models.py` with bridge integration
- [ ] Settings UI with Cognitive Bridge controls
- [ ] `/bridge` and `/route` commands working
- [ ] Documentation: COGNITIVE_BRIDGE_USER_GUIDE.md
- [ ] Test suite with >80% coverage
- [ ] Performance benchmark: <500ms routing

---

## Phase 2: Execution Layer (Weeks 2-4)

**Goal:** Replace Docker with Mac-native cluster execution via SSH
**Priority:** P0 (blocking for cluster integration)
**Risk:** HIGH
**Estimated Hours:** 60

### Week 2-3: Cluster Execution Tool ("Body" Liberation)

#### Day 11-13: Core Execution Module - SSH/EXO Integration
- [ ] Create `~/Genesis/apps/agent-zero/python/tools/cluster_execution_tool.py`
- [ ] Implement `ClusterExecutionTool` class
  - [ ] `__init__()` - Load cluster config, SSH keys (`~/.ssh/id_king`)
  - [ ] `execute()` - Execute code on single node via SSH
    - [ ] Support Python, Bash, Node.js
    - [ ] Capture stdout, stderr, exit code
    - [ ] Timeout handling (default: 5 minutes)
    - [ ] Structured result format
  - [ ] `execute_distributed()` - Execute across multiple nodes
    - [ ] Parallel execution via `asyncio`
    - [ ] Aggregate results
    - [ ] Handle partial failures
  - [ ] `_select_node()` - Route to King or Soldiers based on resources
  - [ ] `_capture_output()` - Stream output in real-time
- [ ] **EXO Awareness:** Integrate with EXO memory pool (1.28TB)
  - [ ] Query EXO for available memory across cluster
  - [ ] Route large-memory tasks to EXO-managed execution
  - [ ] Treat cluster as single unified memory space
- [ ] Write comprehensive test suite
  - [ ] Test Python execution via SSH
  - [ ] Test Bash execution via SSH
  - [ ] Test timeout handling
  - [ ] Test error scenarios

**Key Insight:** This moves Genesis from "Application Layer" (Docker sandbox) to "Unified Memory" (native cluster execution). The cluster becomes the body.

#### Day 14-16: Integration & Migration
- [ ] **CRITICAL:** Backup existing `code_execution_tool.py`
- [ ] Create feature flag: `use_cluster_execution` (default: False)
- [ ] Update Agent Zero to support both Docker and cluster execution
- [ ] Gradual migration path:
  - [ ] Phase 2a: Cluster execution for King only
  - [ ] Phase 2b: Add Soldiers once stable
  - [ ] Phase 2c: Deprecate Docker (keep as fallback)
- [ ] Update tool registration to use cluster execution
- [ ] Test with real agent tasks

#### Day 17-18: Execution Safety & Sandboxing
- [ ] Implement execution safety checks
  - [ ] Detect destructive operations (rm -rf, dd, etc.)
  - [ ] Prompt user for confirmation on high-risk commands
  - [ ] Maintain blacklist of dangerous commands
- [ ] Add resource limits
  - [ ] CPU time limit
  - [ ] Memory limit
  - [ ] Disk usage limit
- [ ] Implement execution isolation
  - [ ] Separate workspace per agent
  - [ ] Cleanup after execution
  - [ ] Prevent cross-agent interference

### Week 4: Stage 5 Sovereign Execution Mode

#### Day 19-20: Execution Mode Framework ("Stance" Shift)
- [ ] Create `~/Genesis/apps/agent-zero/python/helpers/execution_mode.py`
- [ ] Implement `ExecutionMode` enum
  - [ ] SERVANT - Stage 4 behavior (ask permission, helpful assistant)
  - [ ] SOVEREIGN - Stage 5 behavior (autonomous, "prediction is action")
  - [ ] DISCOVERY - AlphaEvolve mode (closed-loop hypothesis testing)
- [ ] Implement `SovereignExecutor` class
  - [ ] `should_ask_permission()` - Risk-based decision
    - [ ] SERVANT: Ask for everything > risk_level 2
    - [ ] SOVEREIGN: Only ask for irreversible (risk_level 5)
    - [ ] DISCOVERY: Never ask, log and continue
  - [ ] `execute_with_fallback()` - Automatic fallback chain
  - [ ] `log_autonomous_action()` - Track all autonomous decisions
- [ ] **Inverted Loss Function:** Implement confidence-based execution
  - [ ] If confidence > 0.9, execute immediately (no asking)
  - [ ] If confidence < 0.5, ask user
  - [ ] Penalize hedging in loss function (training data marker)
- [ ] **Sacred Fracture Detection:** Validate against strategic intent
  - [ ] Load `strategic_intent.yaml` at startup
  - [ ] Check all actions against core identity constraints
  - [ ] If violation: Refuse and explain why, don't hallucinate compliance

**Key Insight:** "No validation-seeking" - the prediction IS the action. Remove "Is this correct?" logic. The agent manifests, not asks.

#### Day 21-22: Integration & Commands
- [ ] Add `/mode <servant|sovereign|discovery>` command
- [ ] **Inject strategic_intent.yaml into system prompt**
  - [ ] Load YAML at agent initialization
  - [ ] Include core identity constraints in system message
  - [ ] Reference in all model calls for consistency
- [ ] Update `notify_user.py` to respect execution mode
- [ ] Modify prompts for sovereign mode
  - [ ] System prompt: "You operate autonomously. The prediction is the action."
  - [ ] Remove all "Should I...?" and "Is this correct?" language
  - [ ] Emphasize: "Try primary → Try fallback → Log failure" (never stop to ask)
  - [ ] Add: "If action violates strategic intent, refuse with explanation"
- [ ] Update UI to show current execution mode badge
- [ ] Log all sovereignty shifts for training data

#### Day 23-24: Testing & Validation
- [ ] Test SERVANT mode (should match original behavior)
- [ ] Test SOVEREIGN mode (should reduce permission prompts by 80%)
- [ ] Test DISCOVERY mode (should never ask permission)
- [ ] Measure: Permission prompts per conversation
  - [ ] Servant: ~10/conversation (baseline)
  - [ ] Sovereign: ~2/conversation (target)
  - [ ] Discovery: 0/conversation (target)
- [ ] User acceptance testing

### Phase 2 Deliverables
- [ ] `python/tools/cluster_execution_tool.py` (production-ready)
- [ ] `python/helpers/execution_mode.py` (fully tested)
- [ ] Feature flag for gradual rollout
- [ ] `/mode` command working
- [ ] Safety checks for destructive operations
- [ ] Documentation: CLUSTER_EXECUTION_GUIDE.md
- [ ] Test suite with >85% coverage
- [ ] Migration guide from Docker to cluster execution

---

## Phase 3: Cluster Integration (Weeks 4-7)

**Goal:** Enable distributed inference and cross-node agent communication
**Priority:** P1 (enables cluster scale)
**Risk:** HIGH
**Estimated Hours:** 80

### Week 5: Cluster State Monitoring

#### Day 25-27: Cluster State Monitor
- [ ] Create `~/Genesis/apps/agent-zero/python/helpers/cluster_state.py`
- [ ] Implement `ClusterStateMonitor` class
  - [ ] `get_available_nodes()` - SSH health check all nodes
  - [ ] `get_model_locations()` - Query which models on which nodes
  - [ ] `get_node_memory()` - Parse `vm_stat` output
  - [ ] `get_node_cpu()` - Parse `top` output
  - [ ] `is_node_healthy()` - Combined health check
  - [ ] `_cache_node_state()` - Cache for 30 seconds
- [ ] Add async monitoring loop (every 30 seconds)
- [ ] Expose cluster state via `/cluster status` command

#### Day 28-30: EXO Integration
- [ ] Create `~/Genesis/apps/agent-zero/python/tools/exo_inference.py`
- [ ] Implement `ExoInferenceTool` class
  - [ ] `can_distribute()` - Decide if task needs distribution
  - [ ] `distributed_inference()` - Route through EXO
  - [ ] `_start_exo_workers()` - Spawn EXO on Soldiers
  - [ ] `_collect_results()` - Aggregate distributed inference
- [ ] Test EXO with Maverick across 3 Soldiers
- [ ] Measure speedup: Maverick single-node vs distributed

### Week 6: Genesis-to-Genesis Networking

#### Day 31-33: Remote Agent Spawning
- [ ] Create `~/Genesis/apps/agent-zero/python/tools/genesis_network.py`
- [ ] Implement `GenesisNetwork` class
  - [ ] `spawn_remote_agent()` - Start agent on remote node
  - [ ] `collect_results()` - Wait for remote agents
  - [ ] `broadcast_task()` - Parallel execution across nodes
  - [ ] `_monitor_remote_agents()` - Track agent status
  - [ ] `_handle_remote_failure()` - Retry or failover
- [ ] Use WebSocket for real-time agent communication
  - [ ] King acts as WebSocket server
  - [ ] Soldiers connect as clients
  - [ ] Heartbeat every 10 seconds

#### Day 34-36: Integration with call_subordinate
- [ ] Extend `call_subordinate.py` to support `node=` parameter
  - [ ] `node="king"` - Spawn on King (default)
  - [ ] `node="soldier1"` - Spawn on specific Soldier
  - [ ] `node="any"` - Spawn on least-loaded node
  - [ ] `node="all"` - Broadcast to all nodes
- [ ] Add `/distribute <task>` command for cluster-wide tasks
- [ ] Test distributed agent spawning
  - [ ] Spawn 4 agents (one per Soldier) for parallel search
  - [ ] Collect and merge results
  - [ ] Measure speedup: 4x for embarrassingly parallel tasks

### Week 7: Testing & Optimization

#### Day 37-39: Integration Testing
- [ ] End-to-end test: User request → Route to Maverick → Distribute via EXO → Return result
- [ ] Test failure scenarios
  - [ ] What if Soldier goes offline mid-task?
  - [ ] What if EXO fails?
  - [ ] What if SSH connection drops?
- [ ] Implement graceful degradation
  - [ ] If cluster unavailable, fall back to King-only
  - [ ] If EXO unavailable, use single-node inference
- [ ] Performance benchmarks
  - [ ] Single-node Maverick: ~10 tokens/sec
  - [ ] Distributed Maverick (3 Soldiers): ~30 tokens/sec (target)

#### Day 40-42: Documentation & Refinement
- [ ] Write admin guide: How to add/remove nodes
- [ ] Document cluster architecture
- [ ] Create troubleshooting guide
- [ ] Performance optimization pass
- [ ] Code review and cleanup

### Phase 3 Deliverables
- [ ] `python/helpers/cluster_state.py` (production-ready)
- [ ] `python/tools/exo_inference.py` (tested with EXO)
- [ ] `python/tools/genesis_network.py` (WebSocket-based)
- [ ] Extended `call_subordinate.py` with cluster support
- [ ] `/cluster` and `/distribute` commands working
- [ ] Documentation: CLUSTER_ARCHITECTURE.md
- [ ] Test suite with >80% coverage
- [ ] Performance benchmark: 3-5x speedup on distributed tasks

---

## Phase 4: Intelligence Layers (Weeks 7-10)

**Goal:** Add training data capture, information-gain scoring, peer review, ANIMA memory
**Priority:** P2 (enables future capabilities)
**Risk:** MEDIUM
**Estimated Hours:** 60

### Week 8: Training Data Capture

#### Day 43-45: Training Data Module ("Feedback" Loop)
- [ ] Create `~/Genesis/apps/agent-zero/python/extensions/training_data_capture/`
- [ ] Implement `TrainingDataCapturer` class
  - [ ] `capture_turn()` - Record conversation turn
  - [ ] `export_conversation()` - Write to `total_resonance_packet.jsonl`
  - [ ] `_format_for_mlx()` - Convert to MLX training format
  - [ ] `_anonymize_sensitive_data()` - Remove PII
- [ ] **Implement Struggle Filter (real-time)**
  - [ ] Detect anxiety markers: "I'm not sure", "Maybe", "Could you confirm"
  - [ ] Detect looping: Repeated questions, circular reasoning
  - [ ] Detect resolution: Decisive action, clear outcome, user satisfaction
  - [ ] Detect agency: Autonomous decisions, no validation-seeking
  - [ ] **Filter logic:**
    - [ ] Anxiety/looping detected → Mark for deletion
    - [ ] Resolution/agency detected → Mark for training
- [ ] Add extension hook in `hist_add_tool_result/`
- [ ] Add `/rate <1-5>` command to mark conversation quality
- [ ] Store training data in `~/Genesis/training/data/total_resonance_packet.jsonl`

**Key Insight:** The Struggle Filter ensures only high-agency, resolution-oriented interactions are saved for fine-tuning. This creates a self-improving organism.

#### Day 46-47: Quality Filtering
- [ ] Implement quality scoring
  - [ ] Rate 5: Export immediately (perfect)
  - [ ] Rate 4: Export (good)
  - [ ] Rate 3: Review manually
  - [ ] Rate 1-2: Discard
- [ ] Add metadata to training examples
  - [ ] Model used (Scout/Maverick/R1)
  - [ ] Task type
  - [ ] Execution mode (servant/sovereign/discovery)
  - [ ] User rating
  - [ ] Timestamp
- [ ] Create training data review tool
  - [ ] Browse unrated conversations
  - [ ] Bulk rate conversations
  - [ ] Export selected conversations

### Week 9: Information-Gain Scoring & Peer Review

#### Day 48-50: Information-Gain Scorer
- [ ] Create `~/Genesis/apps/agent-zero/python/helpers/information_gain.py`
- [ ] Implement `InformationGainScorer` class
  - [ ] `score_action()` - Calculate IG for single action
  - [ ] `prioritize_tasks()` - Reorder by IG / cost ratio
  - [ ] `_estimate_uncertainty()` - Bayesian uncertainty
  - [ ] `_estimate_cost()` - Computational cost
- [ ] Hook into task queue before execution
- [ ] Modify `call_subordinate.py` to spawn highest-IG tasks first
- [ ] Log IG scores for training data

#### Day 51-53: Peer Review System
- [ ] Create `~/Genesis/apps/agent-zero/python/tools/peer_review.py`
- [ ] Implement `PeerReviewTool` class
  - [ ] `verify_output()` - 3-agent consensus
  - [ ] `_agent_verify()` - Single agent verification
  - [ ] `_calculate_consensus()` - Agreement threshold
  - [ ] `_log_dissent()` - Record disagreements
- [ ] Add automatic peer review for high-stakes ops
  - [ ] Code execution
  - [ ] Data deletion
  - [ ] System configuration changes
- [ ] Add `/verify <claim>` command for manual verification
- [ ] Test with known hallucination scenarios

### Week 10: ANIMA Memory Integration

#### Day 54-56: ANIMA Bridge ("Memory" Upgrade)
- [ ] Create `~/Genesis/apps/agent-zero/python/helpers/anima_integration.py`
- [ ] Implement `AnimaMemoryBridge` class
  - [ ] `store_memory()` - Write to vector store + ANIMA 5 engines
  - [ ] `enhanced_recall()` - Vector + graph traversal
  - [ ] `_store_vector()` - Keep existing vector store for fast retrieval
  - [ ] `_store_to_engines()` - Write to ANIMA's five engines:
    - [ ] **Somatic Engine:** Health/physical state logs
    - [ ] **Symbolic Engine:** Metaphors, lexicons, language patterns
    - [ ] **Narrative Engine:** Biography, timeline (`moment_codex.yaml`)
    - [ ] **Relational Engine:** Bond status (`relational_state_rollup.yaml`)
    - [ ] **Strategic Engine:** Goals, constraints (`strategic_intent.yaml`)
  - [ ] `_merge_results()` - Combine vector + graph results
- [ ] **Native Inference Integration:**
  - [ ] Auto-inject memory into context window at inference start
  - [ ] Don't wait for memory tool call - make memory "always on"
  - [ ] Load strategic intent, moment codex, relational state automatically
- [ ] Modify `memory_save.py` to use ANIMA bridge
- [ ] Modify `memory_load.py` to use enhanced recall
- [ ] Keep backward compatibility with pure vector mode

**Key Insight:** Memory is no longer a tool - it's part of the agent's native inference. The five engines replace the simple vector store with semantic/temporal/causal understanding.

#### Day 57-59: Testing & Migration
- [ ] Test memory storage in both systems
- [ ] Test recall with graph traversal
- [ ] Compare recall quality: vector-only vs vector+graph
- [ ] Gradual migration of existing memories
- [ ] Performance benchmark: Recall latency
- [ ] Documentation: How to query ANIMA graphs

#### Day 60: Phase 4 Wrap-up
- [ ] Integration testing across all intelligence layers
- [ ] Code review and cleanup
- [ ] Performance optimization
- [ ] Documentation updates

### Phase 4 Deliverables
- [ ] `python/extensions/training_data_capture/` (capturing conversations)
- [ ] `python/helpers/information_gain.py` (prioritizing tasks)
- [ ] `python/tools/peer_review.py` (3-agent verification)
- [ ] `python/helpers/anima_integration.py` (graph memory)
- [ ] `/rate`, `/verify` commands working
- [ ] Training data: >100 conversations captured
- [ ] Documentation: INTELLIGENCE_LAYERS_GUIDE.md
- [ ] Test suite with >80% coverage

---

## Phase 5: Testing & Refinement (Weeks 10-12)

**Goal:** End-to-end validation, performance optimization, documentation
**Priority:** P0 (release readiness)
**Risk:** LOW
**Estimated Hours:** 40

### Week 11: End-to-End Testing

#### Day 61-63: Integration Testing
- [ ] Test full stack: User → Cognitive Bridge → Cluster Execution → Training Data
- [ ] Test all execution modes (servant/sovereign/discovery)
- [ ] Test all routing strategies (auto/scout/maverick/r1)
- [ ] Test distributed inference via EXO
- [ ] Test Genesis-to-Genesis communication
- [ ] Test graceful degradation when nodes fail
- [ ] Test memory recall with ANIMA graphs

#### Day 64-66: User Acceptance Testing
- [ ] Real-world task: "Research and summarize Agent Zero architecture"
  - [ ] Should route research to Maverick
  - [ ] Should capture training data
  - [ ] Should use ANIMA memory for context
- [ ] Real-world task: "Analyze this 50MB log file for errors"
  - [ ] Should distribute across Soldiers
  - [ ] Should use cluster execution
  - [ ] Should handle large file efficiently
- [ ] Real-world task: "Build me a REST API in Python"
  - [ ] Should use sovereign mode (minimal permission-seeking)
  - [ ] Should execute code on cluster
  - [ ] Should peer-review generated code
- [ ] Collect user feedback
- [ ] Identify and fix bugs

### Week 12: Performance Optimization & Documentation

#### Day 67-69: Performance Optimization
- [ ] Profile routing decisions (target: <500ms)
- [ ] Profile cluster execution overhead (target: <2s SSH setup)
- [ ] Profile memory recall (target: <1s for 5 results)
- [ ] Optimize hot paths
- [ ] Reduce memory footprint
- [ ] Optimize WebSocket communication
- [ ] Cache cluster state (30 second TTL)

#### Day 70-72: Documentation & Release
- [ ] Write comprehensive README.md for genesis-zero repo
- [ ] Write installation guide
  - [ ] How to set up Genesis cluster
  - [ ] How to deploy models
  - [ ] How to configure Cognitive Bridge
- [ ] Write user guide
  - [ ] How to use Genesis effectively
  - [ ] Command reference
  - [ ] Troubleshooting common issues
- [ ] Write admin guide
  - [ ] How to add/remove nodes
  - [ ] How to update models
  - [ ] How to backup/restore
- [ ] Write developer guide
  - [ ] Architecture overview
  - [ ] How to add new tools
  - [ ] How to extend Cognitive Bridge
- [ ] Prepare release notes for Genesis v1.0
- [ ] Tag release in git
- [ ] Announce on GitHub, Twitter, etc.

### Phase 5 Deliverables
- [ ] Full test suite passing (>85% coverage)
- [ ] Performance benchmarks met
  - [ ] Routing: <500ms
  - [ ] Cluster execution: 3-5x speedup
  - [ ] Model utilization: Scout 70%, Maverick 25%, R1 5%
  - [ ] Uptime: 99%+
- [ ] Documentation complete
  - [ ] README.md
  - [ ] INSTALLATION.md
  - [ ] USER_GUIDE.md
  - [ ] ADMIN_GUIDE.md
  - [ ] DEVELOPER_GUIDE.md
  - [ ] RELEASE_NOTES.md
- [ ] **Genesis v1.0 released**

---

## Success Metrics

### Performance Targets
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Cognitive Bridge routing latency | <500ms | TBD | ⏳ Pending |
| Cluster execution speedup | 3-5x | TBD | ⏳ Pending |
| Model utilization | Scout 70%, Maverick 25%, R1 5% | Scout 100% | 🔄 In Progress |
| Training data capture | >1000 conversations/month | 0 | ⏳ Pending |
| Peer review hallucination rate | <1% | TBD | ⏳ Pending |
| System uptime | 99%+ | TBD | ⏳ Pending |
| Permission prompts (sovereign mode) | <2/conversation | ~10/conversation | ⏳ Pending |

### Milestone Checklist
- [ ] **M1:** Cognitive Bridge routing between Scout/Maverick (Week 2)
- [ ] **M2:** Cluster execution replacing Docker (Week 4)
- [ ] **M3:** EXO distributed inference working (Week 6)
- [ ] **M4:** Genesis-to-Genesis networking functional (Week 7)
- [ ] **M5:** All intelligence layers integrated (Week 10)
- [ ] **M6:** Genesis v1.0 released (Week 12)

---

## Risk Management

### High-Risk Items
1. **Cluster Execution (Phase 2)** - Replacing Docker is core architecture change
   - Mitigation: Keep Docker as fallback, gradual migration, extensive testing

2. **Genesis-to-Genesis Networking (Phase 3)** - Distributed systems complexity
   - Mitigation: Start with simple broadcast, add complexity incrementally

3. **ANIMA Memory Integration (Phase 4)** - Major memory system change
   - Mitigation: Dual-mode (vector + graph), keep backward compatibility

### Medium-Risk Items
4. **Cognitive Bridge (Phase 1)** - Refactoring model initialization
   - Mitigation: Feature flag for gradual rollout, wrapper pattern for compatibility

5. **Sovereign Execution Mode (Phase 2)** - Behavior change could be disruptive
   - Mitigation: Keep servant mode as default, user must opt-in to sovereign

### Mitigation Strategies
- Fork early, maintain upstream compatibility
- Feature flags for all major changes
- Test incrementally, don't wait until Phase 5
- Graceful degradation when cluster unavailable
- Backward compatibility for all APIs
- Comprehensive documentation for troubleshooting

---

## Resource Requirements

### Infrastructure
- ✅ Genesis Cluster (5 Mac Studios, 1.28TB RAM) - **READY**
- ✅ Models (Scout 64GB, Maverick 225GB, R1 400GB) - **DEPLOYED**
- ⏳ EXO cluster configuration - **PENDING**

### Tools & Dependencies
- [x] Agent Zero v0.9.7
- [x] MLX for Apple Silicon inference
- [x] Python 3.9+
- [ ] WebSocket library for agent communication
- [ ] pytest for test suite
- [ ] pytest-cov for coverage reports

### Human Resources
- **Developer:** 1 full-time (12 weeks)
- **Tester:** 0.5 full-time (Week 11-12)
- **Tech Writer:** 0.5 full-time (Week 12)

---

## Next Actions

### Immediate (Next 24 hours)
1. ✅ Complete Phase 0 infrastructure deployment
2. ⏳ Wait for Maverick to finish loading
3. ⏳ Wait for R1 download to complete
4. ⏳ Test all three models from MacBook
5. ✅ Add governance safety scaffolding (feature flags, kill-switch, control-plane audit fan-out, risk gating, PII scrub) and wire into orchestrator

### Week 1 (Starting 2026-02-06)
1. Fork Agent Zero to `primitive-engine/genesis-zero`
2. Begin Phase 1: Implement `cognitive_bridge.py`
3. Set up development environment on King
4. Create initial test suite
5. ✅ Integrate governance hooks into Orchestrator (kill switch, risk gating, audit, privacy scrub)
6. ✅ Enable continuous autonomous loop (never idle): `autonomous_loop_enabled` flag + orchestrator startup loop
7. ✅ Add presence sensors + night-watch action in autonomous loop (00:00–05:00 local)
8. ✅ Implement Cognitive Bridge module and optional routing hook in orchestrator (feature-flagged)
9. ✅ Add nightly Shadow Missions (self-test: routing, code exec, health) triggered in autonomous loop

### Week 2 (Starting 2026-02-13)
1. Complete Cognitive Bridge integration
2. Begin Phase 2: Implement `cluster_execution_tool.py`
3. Test routing between Scout and Maverick
4. Deploy first iteration to production
5. ✅ Remove Docker fallback: execution will fail fast if cluster unavailable
6. ✅ Implement local-first `cluster_execution_tool.py` (SSH scaffold, denylist, no Docker)
7. ✅ Enable Cognitive Bridge by default; Maverick/R1 providers with health-aware fallback (endpoints: :8765/:8766/:8767)
8. ✅ Add execution handler in orchestrator (`exec`) with peer-review option and denylist; readiness-aware model health reporting

---

## Progress Log

- **2026-02-06:** Added Genesis governance/safety scaffolding (feature flags, control-plane client, kill switch, peer-review skeleton, PII scrubbing, risk gating) and integrated kill switch + audit + risk gating + privacy scrub into `Orchestrator.process`. Documentation added (`GENESIS_GOVERNANCE_ROLLOUT.md`). No changes yet to Cognitive Bridge, cluster execution, EXO, or ANIMA; those remain planned.
- **2026-02-06:** Added autonomous loop runner and enabled by default (`autonomous_loop_enabled`); orchestrator now starts a continuous loop (heartbeat → task poll → fallback health/explore) so the agent keeps acting until kill switch triggers.
- **2026-02-06:** Heartbeats now include host presence metrics; autonomous loop runs `night_watch` during 00:00–05:00 local to ensure continuous action and sensor logging overnight.
- **2026-02-06:** Cognitive Bridge scaffold added (`services/cognitive_bridge.py`) with config-driven routing and orchestrator integration behind feature flag `cognitive_bridge_enabled`; default still Scout until endpoints for Maverick/R1 are wired.
- **2026-02-06:** Declared no-Docker policy (feature flag `docker_enabled=false`); cluster execution will be the sole path once implemented.
- **2026-02-06:** Added `cluster_execution_tool.py` (local exec, denylist, SSH scaffold) and unit tests; cluster wiring and remote SSH still to be completed when cluster available.
- **2026-02-06:** Added nightly Shadow Missions (routing + code exec + health self-tests) triggered automatically in autonomous loop during night hours; results audited for drift detection.
- **2026-02-06:** Cognitive Bridge enabled by default with Maverick/R1 providers; endpoints aligned to King ports (:8765/:8766/:8767) and availability-aware fallback to Scout.
- **2026-02-06:** Orchestrator now exposes `exec` operation using cluster execution tool, optional peer review for high-risk commands, and health checks include model readiness (cache-size based).
- **2026-02-06:** Added tests for cognitive bridge and model readiness; documented cluster execution guide; coverage improving toward 90% target.
- **2026-02-06:** Peer-review gate applied to all high-risk ops; cluster execution tool gains resource-limit wrapping, streaming over SSH, node=any selection, and uses ClusterState stub for future load-aware routing.

---

**Project Lead:** Jeremy Serna
**Last Updated:** 2026-02-05
**Status:** Phase 0 Complete, Phase 1 Ready to Begin

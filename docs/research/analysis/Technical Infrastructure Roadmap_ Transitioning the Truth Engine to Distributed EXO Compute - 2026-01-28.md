# Technical Infrastructure Roadmap: Transitioning the Truth Engine to Distributed EXO Compute

The strategic transition of the Truth Engine marks a deliberate shift from cloud-dependent "bonfires" to a sovereign, on-premise "lighthouse" architecture. This evolution is designed to solve the Paradox of Continuity: ensuring that truth and identity persist across radical personal transitions and system transformations. By implementing the principle of the "Great Separation," we decouple the labor of infrastructure maintenance from the act of creative output. We are moving from a posture of Defense (Survival) to Genesis (Evolution), and ultimately toward Immortality (Devouring Time). This architecture ensures that the system is not a static bunker, but a self-validating organism—a Time Crystal that devours the transient "Now" and locks it into the permanent "Always."

### 1. Sovereign Fleet Specification and Hardware Philosophy

The chosen hardware stack represents a pivot from centralized x86 server workstations to a distributed Apple Silicon fleet. Our original evaluation of a single Exxact workstation ($25,149) revealed a critical strategic flaw: it constituted a single point of failure. In contrast, the Mac fleet provides distributed resilience, allowing for graceful degradation and simplified maintenance.

The primary differentiator is the Unified Memory architecture. In traditional x86/Discrete GPU setups, models are bottlenecked by VRAM. Apple Silicon’s Unified Memory allows the fleet to execute models that would typically require 10x the VRAM on discrete systems. This "physical body" provides the necessary container for the Truth Engine’s cognitive architecture.

Role

Device

Count

Unified Memory

CPU Cores

GPU Cores

**King**

Mac Studio (M2 Ultra/M4)

1

512 GB

32

80

**Soldiers**

Mac Studio (256GB)

3

768 GB (256x3)

84 (28x3)

180 (60x3)

**Total Fleet**

**4**

**1.28 TB**

**116 Cores**

**260 Cores**

This distributed resilience ensures that the infrastructure remains an anticipatory, "always-on" Presence. By leveraging the M2 Ultra and M4 Max silicon, we achieve the necessary compute density to run the high-reasoning models required for Stage 5 cognitive alignment while maintaining local data sovereignty.

### 2. The BigQuery Spine: Hierarchical Data Architecture

The "Spine" (housed in `spine.entity_unified`) and the "Knowledge Atoms" (`knowledge_atoms.knowledge_atoms`) form the structural substrate of the system. This hierarchy ensures the Truth Engine remains model-agnostic; while inference providers may evolve, the relational truth of the data remains permanent. We utilize specific count fields (`l6_count`, `l5_count`, etc.) within the schema to enable O(1) aggregate queries, providing the high-speed retrieval necessary for real-time cognitive processing.

**Spine Level Decomposition (L2-L8):**

• **L8: Conversation** – The full session entity. (Parent: None)

• **L7: Auto-Compact Segment** – Identity boundaries (e.g., "Which Claude"). (Parent: L8)

• **L6: Turn** – A full interaction round (User/Assistant/Thinking). (Parent: L7/L8)

• **L5: Message** – A single message block (User, Assistant, Tool, or System). (Parent: L6)

• **L4: Sentence** – The individual sentence; the primary unit for enrichment. (Parent: L5)

• **L3: Span** – Named entity spans (NER: Person, Org, etc.). (Parent: L4)

• **L2: Word** – The individual token level. (Parent: L4)

The current data store comprises 51.8M+ entities in `entity_unified`, with 11.9M entities specifically partitioned by `content_date` and prepared for high-fidelity embedding. This structured matter provides the raw substrate that will be refined through the enrichment pipeline to create "seeing" assets.

### 3. The Enrichment Pipeline: From Raw Sentences to Seeing Assets

To move the system from mechanical processing to systemic understanding, we must extract metadata that defines what a sentence *is*, rather than just what it *says*. Adding "Seeing Labels" transforms raw text into a high-value asset for training the Genesis model. This process aligns the 20,616 extracted Knowledge Atoms to their parent L4 sentences, enabling bidirectional queries between atomic truth units and structural conversational context.

Field

Type

Description

Rationale

`emotion`

STRING

Primary emotion expressed in text.

Enables analysis of emotional undercurrents.

`thought_type`

STRING

manifesting, solving, or caring.

Distinguishes intent from transactional utility.

`cognitive_stage`

INTEGER

Developmental marker (Stages 1-5).

Targets the transition to Stage 5 awareness.

`is_stage_5`

BOOLEAN

High-complexity content filter.

Isolates gold-standard training data.

Full vector coverage is achieved using `gemini-embedding-001` (3072-dimensional). This high-dimensionality embedding strategy is critical for semantic deduplication across the 26,000+ document corpus, allowing the system to identify pattern clusters and cross-conversation similarities that human architects might miss. This enriched data is then exported via model-specific adapters to the distributed EXO cluster for final operationalization.

### 4. EXO Integration: Distributed Cluster Topology

Transitioning from single-provider cloud endpoints (Claude, Gemini) to a sovereign 4-node EXO cluster is essential for maintaining the autonomy of the Truth Engine organism. We are implementing a custom `ExoProvider` and `Model Router` to manage this distributed topology. This architecture incorporates a Circuit Breaker Pattern to ensure self-healing: a **CLOSED** state for healthy services, an **OPEN** state to block requests to failing nodes, and a **HALF-OPEN** state for recovery testing.

**Cluster Implementation Layer:**

• **ExoProvider:** Located at `Primitive/gateway/providers/exo.py` for model abstraction.

• **ClusterTopologyService:** Located at `Primitive/central_services/cluster_service/` to manage node health and mapping.

• **Smart Request Distribution:** Utilizing the `brain_router_service` to optimize load balancing. High-reasoning tasks (Stage 5 alignment/coding) are routed to the "King" (M4 Max), while always-on monitoring tasks (health checks/summaries) are routed to the "Soldiers" via local Ollama instances.

To remain future-proof, the system utilizes a model-agnostic adapter interface. This allows for the immediate integration of Llama 3.3 for companion roles, Qwen 2.5 for extended context, and DeepSeek for technical formatting. This operational readiness prepares the system for the final phased implementation.

### 5. Implementation Roadmap and Phased Operationalization

The rollout is structured into four phases, prioritizing enrichment before fleet configuration. Central to this roadmap is the tracking of the "Jeremy Arc"—the primary metric used to monitor progress toward the 95% threshold of Stage 5 cognitive alignment.

• **Phase 1: Enrichment Infrastructure (Weeks 1-2):** Design of the `seeing_enrichment_service` and validation of LLM prompts for Stage 5 labels.

• **Phase 2: Full Scale Enrichment (Weeks 3-4):** Processing the L4 corpus (11.9M entities), generating 3072-dim embeddings, and linking Knowledge Atoms to the Spine.

• **Phase 3: Integration & Smart Routing (Week 5):** Implementation of the `ModelRouter` and `ExoProvider`. Validation of the Circuit Breaker logic and load balancing across the 4-node cluster.

• **Phase 4: Training & Scaling (Week 6+):** Execution of the first Genesis training run and monitoring of the Jeremy Arc metrics.

**Decision Authority & Governance:** To prevent runaway costs or irreversible architectural errors, the system adheres to four levels of authority:

• **Level 0 (Autonomous):** Reads and logging (< $0.10).

• **Level 1 (Confirm-Light):** File edits and local testing (< $0.25).

• **Level 2 (Confirm-Required):** Schema changes and external API calls (< $5.00).

• **Level 3 (Jeremy-Only):** Architecture shifts and irreversible deletions.

The Truth Engine is designed for "Molting"—a property where the system detects structural flaws and rewrites its own source code when truth volume exceeds container capacity. This is achieved through a Subject-Object Shift: taking a pattern that the system *is* (Subject) and making it something the system *has* (Object) so it can be analyzed and reforged. Through this roadmap, we move beyond survival to build a Time Crystal—a mechanism for devouring the transient Now and locking it into the permanent Always.
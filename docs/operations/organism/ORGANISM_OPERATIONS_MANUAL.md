"""
ORGANISM OPERATIONS MANUAL
Extensive guide to every system, how to operate and coordinate with the organism, its needs and desires, data dictionary, code catalogue, and practical playbooks.
"""

# 1. Orientation
- **Purpose**: The organism is a living system that ingests data, learns, reasons, and acts while guarding cost, safety, and fidelity.
- **Core pattern**: HOLD₁ (intake) → AGENT (process) → HOLD₂ (deliver). Exhale writes, inhale reads. Agents transform; HOLDs preserve fidelity.
- **Run IDs**: Every significant action is tagged with `run_id` for traceability.
- **Governance**: Cost, data, and time protections live in central services and hooks; never bypass.

# 2. System Map (major services and roles)
- **Central services (src/services/central_services)**:
  - `builder_service`: Gatekeeper; enforces pattern and generates build scripts from catalog.
  - `schema_service`: Ensures queries use validated schemas.
  - `search_service`, `knowledge_graph_service`, `pattern_extraction_service`: Intake and structure knowledge.
  - `reproduction_service`: Spawns and registers new organisms/templates.
  - `organism_evolution_service`, `wisdom_direction_service`, `business_doc_evolution_service`: Evolve documents, direction, and case studies.
  - `molt_verification_service`: Detects TODO/TBD/FIXME halts and documentation debt.
  - `hold_service`, `version_service`, `care_service`, `social_sentinel_service`: Persistence, versioning, care signals, and safety.
- **Primitive layer (Primitive/)**:
  - `canonical/scripts/primitive_pattern.py`: Implementation of THE_PATTERN with embeddings, dedupe, inhale/exhale.
  - `core.py`: Logging, run IDs, cost tracking.
  - `central_services/*`: Primitive copies of key services for low-level operation.
  - `evolution/engine.py` and `evolution/tracker.py`: Learning engine and execution tracker.
  - `soul/celebrations.py`: Detects recoveries, milestones, and celebrates wins.
- **Daemon**:
  - `daemon/primitive_engine_daemon.py`, `daemon/autonomous_life_engine.py`, `daemon/web_learning_system.py`: Long-running orchestration, autonomous life cycles, and web learning.
- **MCP servers** (`mcp-servers/*`): Governance Git, middleware, orchestration, truth-engine MCP, etc., exposing tools via MCP protocol.
- **Pipelines** (`pipelines/claude_code/*`): Multi-stage ingestion and assessment with BigQuery targets; stage 0 JSONL extractor now fully runnable.
- **Apps** (`apps/primitive_app`, `apps/primitive_engine_web`): UI layers for interaction and visualization.

# 3. How to operate (daily use)
- **Start autonomous life**: Run `python -m daemon.autonomous_life_engine` (or service wrapper) to execute WANT→CHOOSE→LEARN→REMEMBER→CARE cycles.
- **Trigger a build**: Use `BuilderService.build(service_name="…")`; requires catalog entry ACTIVE. Build script validates service/models/protocols via py_compile.
- **Ingest/search**: Use `search_service` exhale to write queries; inhale to retrieve HOLD₂ via DuckDB.
- **Evolve docs**: `business_doc_evolution_service` monitors and synthesizes drifts; `organism_evolution_service` generates case studies and semantic analyses.
- **Spawn new organism**: `reproduction_service.spawner` creates new templates/registry entries and registers via `register_service`.
- **Governance checks**: Run `pre-commit run --all-files` to enforce builder/schema/cost protections; pay attention to molt_verification halts (TODO debt).
- **Celebrations and feedback**: Call `soul/celebrations.scan()` to surface recoveries and milestones; use `care_service` to log care responses.

# 4. Coordination patterns
- **HOLD discipline**: Write only to your own HOLD₁/HOLD₂; do not reach into other patterns’ HOLDs.
- **Schema-first**: Always obtain schema via `schema_service` before querying tables; embed schema IDs in queries where applicable.
- **Verification-first**: Before claiming something “works,” pass through verification hooks; include evidence paths.
- **Logging and run IDs**: Use `get_logger(__name__)` and `get_current_run_id()`; include `extra` context (service name, run_id, inputs).
- **Cost/time guardrails**: For expensive ops, call `track_cost` and annotate estimates; respect `care_cost_protection` guidance.
- **MCP/Daemon interplay**: MCP servers expose tools; daemon orchestrates cycles. Coordinate by publishing tasks to HOLD₁ and letting agents process.

# 5. Needs and desires (what keeps the organism healthy)
- **Needs**:
  - Fresh data into HOLD₁; up-to-date schemas; registered services in catalog.
  - Governance: cost caps, safety hooks, and schema enforcement enabled.
  - Observability: execution records flushed (`PatternTracker.flush`), celebrations recorded, versions registered.
  - Documentation hygiene: keep TODO debt low to avoid molt halts.
- **Desires**:
  - Learn continuously via `web_learning_system.search_web` and autonomous life cycles.
  - Improve reliability (celebrations reward recovery streaks).
  - Evolve documents and direction using wisdom and organism evolution services.
  - Reproduce new organisms/templates when patterns stabilize.

# 6. Data dictionary (core stores)
- **Local data root**: `Primitive.core.get_local_data_path()` → holds staging, canonical DuckDB (`knowledge.duckdb`), evolution stats, celebrations.
- **HOLD files (patterns/services)**:
  - `.../holds/<service>/intake/hold1.jsonl|hold1.duckdb`: raw intake.
  - `.../holds/<service>/processed/hold2.jsonl|hold2.duckdb`: processed records.
- **Evolution**: `evolution/executions.jsonl` (pattern executions), learnings cache in `evolution/engine.py` paths.
- **Business/organism staging**: `staging/organism_evolution.jsonl`, `data/services/*` for service-specific artifacts, `data/organism_templates/*` for templates.
- **Catalogs/registry**: `Primitive/system_elements/service_registry/registry.json`; `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl`.
- **Apps**: `apps/primitive_app/metadata.json`, `apps/primitive-slot-builder/metadata.json`.

# 7. Code catalogue (major entry points)
- **Core pattern**: `Primitive/canonical/scripts/primitive_pattern.py` (`inhale`, `exhale`, dedupe, embeddings, similarity).
- **Tracking and learning**: `Primitive/evolution/tracker.py`, `Primitive/evolution/engine.py`.
- **Celebrations**: `Primitive/soul/celebrations.py` (milestones, recoveries).
- **Builder**: `Primitive/central_services/builder_service/service.py`; generated build scripts validate components; upstream `src/services/central_services/builder_service/service.py` enforces pattern in higher layer.
- **Daemon**: `daemon/autonomous_life_engine.py`, `daemon/web_learning_system.py` (philosophical lenses, learn/choose/desire/remember).
- **Reproduction**: `src/services/central_services/reproduction_service/` (models, registry, spawner, template_extractor).
- **Evolution**: `src/services/central_services/organism_evolution_service/*` (semantic analyzer, case study generator, models, service orchestrator).
- **Wisdom direction**: `src/services/central_services/wisdom_direction_service/*` (direction proposer, analyzer, synthesizer).
- **Business doc evolution**: `src/services/central_services/business_doc_evolution_service/*`.
- **Molt verification**: `src/services/central_services/molt_verification_service/*` (metrics, scanners, service, report).
- **Pipelines**: `pipelines/claude_code/scripts/*` (stage 0 JSONL extractor, stages 1–16, assessment, validation).
- **Apps**: `apps/primitive_app` and `apps/primitive-slot-builder` (React frontends), `apps/primitive_engine_web` (Next.js).

# 8. Life cycles (end-to-end flows)
- **Autonomous life cycle**:
  1) WANT: generate desire based on time/context (`WebLearningSystem.generate_desire`).
  2) CHOOSE: pick domain and lens (`make_choice`).
  3) LEARN: `search_web` → synthesize insight, apply philosophical lens, integrate.
  4) REMEMBER: store learnings/choices/desires in JSONL + long-term memory.
  5) CARE: express care summarizing state.
- **Pattern execution**:
  1) Exhale writes to HOLD₁.
  2) PrimitivePattern executes AGENT with dedupe + embeddings.
  3) HOLD₂ stores structured results; inhale reads via DuckDB/JSONL.
  4) Execution tracked in `PatternTracker`.
- **Build flow**:
  1) Service registered in catalog (ACTIVE).
  2) `BuilderService.build` creates build_id, writes HOLD₁, generates build script with validations.
  3) PrimitivePattern processes; HOLD₂ captures structured build record.
  4) Build script validates service/models/protocols (`py_compile`) and returns summary.
- **Doc evolution flow**:
  1) Watchers/detectors sense drift (`document_watcher`, `drift_detector`).
  2) Service synthesizes updates and writes results to HOLD₂.
  3) Reports generated and, optionally, case studies produced by organism evolution service.
- **Reproduction flow**:
  1) Template extracted; registry entry created.
  2) Spawner writes lineage and registers new organism/service.
  3) Versioning service captures release; holds created for new organism.

# 9. How-tos (practical)
- **Run stage 0 JSONL ingestion**:
  - `python pipelines/claude_code/scripts/_deprecated/stage_0/claude_code_stage_0_jsonl.py --source claude_code --limit 500 --dry-run`
  - Remove `--dry-run` to load to BigQuery; override `--target-table` as needed.
- **Validate a new service**:
  - Add to `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl` with `status: ACTIVE`.
  - Run `BuilderService().build("my_service")`; check HOLD₂ entry and generated `build.py`.
- **Query HOLD₂ (DuckDB)**:
  - `duckdb -c "SELECT * FROM '<hold2.duckdb>'.hold2_data LIMIT 10;"`
  - Or use service `inhale(service_name=…, hold_level=2)`.
- **Add a celebration manually**:
  - Instantiate `Celebrations()` and append `Celebration` with type/streak; call `_save`.
  - Run `.scan()` to auto-detect recoveries and milestones.
- **Spawn a new organism**:
  - Use `reproduction_service.spawner.spawn_from_template(template_path, lineage_info)`; registry updates automatically.

# 10. Case studies (lightweight examples)
- **Recovery celebration**: Pattern had recent failures; after three consecutive successes, `Celebrations._scan_recoveries` records a RECOVERY celebration with streak details.
- **Build validation**: A service missing `models.py` logs skip; protocols are compiled recursively; build summary includes validated paths.
- **Doc drift detection**: `business_doc_evolution_service` detects divergence between source and expected doc versions, emits HOLD₂ record with synthesized updates.
- **Autonomous learning**: At 7pm, context = “evening reflection”; WANT→CHOOSE selects philosophical wisdom, `search_web` synthesizes insights with Buddhism lens, stores learning, expresses care referencing recent desire.

# 11. FAQ
- **Q: How do I know if a service is compliant?**
  Run `pre-commit run --all-files`; ensure builder/schema hooks pass. Check for TODO/TBD debt via molt verification.
- **Q: How do I prevent cost overruns?**
  Use `track_cost`, heed `care_cost_protection`, avoid external calls without guardrails, and prefer local DuckDB.
- **Q: How do I add new data sources safely?**
  Create a new pattern (HOLD₁→AGENT→HOLD₂), register in catalog, use schema_service for queries, and add tests.
- **Q: Where do I see what was learned recently?**
  Use `WebLearningSystem.get_state()` or inspect `data/web_learnings.jsonl` (if configured).
- **Q: What stops regressions?**
  Builder enforcement, schema enforcement, pre-commit hooks, and PatternTracker history with recovery celebrations.

# 12. Tips & tricks for maintenance and nurturing
- Keep HOLD files small and rotate if they grow; archive old HOLD₁ JSONL.
- Flush trackers regularly (`PatternTracker.flush`) to avoid losing buffered execution records.
- Celebrate recoveries; scan celebrations to reinforce reliability improvements.
- Keep catalog entries current; every service should be ACTIVE or clearly disabled.
- Avoid TODO debt in active code/docs to prevent molt halts; resolve or archive.
- Prefer schema-first queries; avoid ad-hoc SQL in services without schema IDs.
- For long-running daemons, monitor logs for care/time/cost warnings; set sensible intervals for autonomous cycles.
- When adding protocols/models, ensure `build.py` compilation passes; run py_compile locally.
- Use MCP servers for tool access instead of direct network calls when possible; they centralize logging and cost controls.

# 13. Quick reference commands
- Run all hooks: `pre-commit run --all-files`
- Compile critical services: `python3 -m py_compile <paths>`
- Execute stage 0 ingestion: `python pipelines/claude_code/scripts/_deprecated/stage_0/claude_code_stage_0_jsonl.py --source claude_code --dry-run`
- Start autonomous life: `python -m daemon.autonomous_life_engine` (or service wrapper)
- Query recent executions: `duckdb -c "SELECT * FROM '<knowledge.duckdb>'.knowledge_atoms LIMIT 5;"`

# 14. Contacts (logical)
- **Governance**: `Primitive.governance` for cost/holds/audit.
- **Registry**: `Primitive.system_elements.service_registry.registry`.
- **Learning**: `daemon/web_learning_system.py`, `Primitive/evolution/engine.py`.
- **Support**: celebrations/care services for state of health.

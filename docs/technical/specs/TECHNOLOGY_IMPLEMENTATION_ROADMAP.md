# Technology Implementation Roadmap

**Date**: January 20, 2026
**Purpose**: Practical first steps for technology adoption

---

## Quick Wins: High Impact, Low Effort

These can be implemented in days, not weeks:

### 1. Structured Logging (Day 1)

**Current State**: Mix of print statements and basic logging
**Target State**: JSON logging with correlation IDs

```python
# Install
# pip install structlog

# Primitive/core/logging.py
import structlog
from contextvars import ContextVar

# Correlation ID propagates across async boundaries
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

def get_logger(name: str):
    return structlog.get_logger(name)

# Usage in any service
from Primitive.core.logging import get_logger

logger = get_logger(__name__)
logger.info("processing_started", record_id="abc123", source="documents")
# Output: {"event": "processing_started", "record_id": "abc123", "source": "documents", "level": "info", "timestamp": "2026-01-20T10:30:00Z"}
```

**Why First**: Every other technology benefits from structured logs. This is the foundation.

---

### 2. Pydantic v2 Migration (Day 2-3)

**Current State**: dataclasses and dicts
**Target State**: Pydantic models with automatic validation

```python
# Before (dataclass)
@dataclass
class KnowledgeAtom:
    id: str
    content: str
    source: str
    timestamp: datetime

# After (Pydantic v2)
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class KnowledgeAtom(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str = Field(min_length=1)
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: list[float] | None = None

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        allowed = {"documents", "web_search", "claude_code", "observation"}
        if v not in allowed:
            raise ValueError(f"source must be one of {allowed}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "atom-123",
                    "content": "Knowledge content here",
                    "source": "documents"
                }
            ]
        }
    }
```

**Why Second**: Type safety catches errors early. Serialization is automatic. OpenAPI docs are free.

---

### 3. DuckDB for Telemetry (Day 4-5)

**Current State**: Logs go to files
**Target State**: Queryable telemetry database

```python
# Primitive/observability/telemetry_store.py
import duckdb
from pathlib import Path

class TelemetryStore:
    """SQL-queryable telemetry storage."""

    def __init__(self, db_path: Path = Path("data/local/telemetry.duckdb")):
        self.conn = duckdb.connect(str(db_path))
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id VARCHAR PRIMARY KEY,
                span_id VARCHAR,
                parent_span_id VARCHAR,
                service_name VARCHAR,
                span_name VARCHAR,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_ms DOUBLE,
                status VARCHAR,
                attributes JSON,
                spiffe_id VARCHAR  -- Identity!
            );

            CREATE TABLE IF NOT EXISTS logs (
                log_id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                level VARCHAR,
                logger VARCHAR,
                message VARCHAR,
                attributes JSON,
                trace_id VARCHAR,  -- Links to traces
                span_id VARCHAR
            );

            CREATE TABLE IF NOT EXISTS metrics (
                metric_id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                name VARCHAR,
                value DOUBLE,
                unit VARCHAR,
                attributes JSON,
                service_name VARCHAR
            );
        """)

    def query(self, sql: str) -> list[dict]:
        """Run SQL against telemetry data."""
        return self.conn.execute(sql).fetchdf().to_dict(orient="records")

# Example queries
store = TelemetryStore()

# What's slow?
slow_spans = store.query("""
    SELECT span_name, AVG(duration_ms) as avg_ms, COUNT(*) as count
    FROM traces
    WHERE start_time > now() - interval '1 hour'
    GROUP BY span_name
    ORDER BY avg_ms DESC
    LIMIT 10
""")

# What's failing?
errors = store.query("""
    SELECT service_name, span_name, COUNT(*) as error_count
    FROM traces
    WHERE status = 'ERROR'
      AND start_time > now() - interval '24 hours'
    GROUP BY service_name, span_name
    ORDER BY error_count DESC
""")
```

**Why Third**: Makes all telemetry queryable. Debugging becomes SQL.

---

## Medium-Term: Core Synergies

### 4. OpenTelemetry Instrumentation (Week 1)

```python
# Primitive/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from functools import wraps

# Custom exporter that writes to DuckDB
class DuckDBSpanExporter:
    def __init__(self, store: TelemetryStore):
        self.store = store

    def export(self, spans):
        for span in spans:
            self.store.insert_span(span)

def setup_tracing():
    provider = TracerProvider()
    # Export to both DuckDB (local) and OTLP (optional cloud)
    provider.add_span_processor(BatchSpanProcessor(DuckDBSpanExporter(store)))
    trace.set_tracer_provider(provider)

def traced(name: str = None):
    """Decorator to trace any function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(name or func.__name__) as span:
                span.set_attribute("function", func.__name__)
                span.set_attribute("module", func.__module__)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator

# Usage
@traced("process_document")
def process_document(doc_id: str) -> ProcessedDocument:
    # Automatic tracing
    ...
```

---

### 5. GraphRAG Knowledge Extraction (Week 2)

```python
# Primitive/knowledge/graph_rag.py
from pydantic import BaseModel
import networkx as nx

class Entity(BaseModel):
    name: str
    type: str  # person, concept, technology, etc.
    description: str

class Relationship(BaseModel):
    source: str
    target: str
    type: str  # uses, depends_on, created_by, etc.
    description: str

class KnowledgeGraph:
    """Graph-enhanced knowledge for multi-hop reasoning."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_from_text(self, text: str, source_id: str) -> tuple[list[Entity], list[Relationship]]:
        """Extract entities and relationships from text using LLM."""

        # Use LLM to extract structured knowledge
        prompt = """Extract entities and relationships from this text.

        Text: {text}

        Return JSON with:
        - entities: [{name, type, description}]
        - relationships: [{source, target, type, description}]
        """

        result = llm.extract(prompt.format(text=text), schema=ExtractionResult)

        # Add to graph
        for entity in result.entities:
            self.graph.add_node(
                entity.name,
                type=entity.type,
                description=entity.description,
                source_id=source_id
            )

        for rel in result.relationships:
            self.graph.add_edge(
                rel.source,
                rel.target,
                type=rel.type,
                description=rel.description,
                source_id=source_id
            )

        return result.entities, result.relationships

    def multi_hop_query(
        self,
        start: str,
        question: str,
        max_hops: int = 3
    ) -> list[str]:
        """Traverse graph to gather context for question."""

        # BFS from start node
        visited = set()
        context = []
        queue = [(start, 0)]

        while queue:
            node, depth = queue.pop(0)
            if depth > max_hops or node in visited:
                continue

            visited.add(node)

            # Add node context
            if node in self.graph:
                node_data = self.graph.nodes[node]
                context.append(f"{node}: {node_data.get('description', '')}")

            # Add edge context
            for _, neighbor, edge_data in self.graph.edges(node, data=True):
                context.append(f"{node} --[{edge_data['type']}]--> {neighbor}")
                queue.append((neighbor, depth + 1))

        return context
```

---

### 6. Hybrid Search Implementation (Week 2)

```python
# Primitive/knowledge/hybrid_search.py
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearcher:
    """Combine keyword (BM25) and semantic (vector) search."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.bm25 = None
        self.documents = []
        self.embeddings = []

    def index(self, documents: list[dict]):
        """Build both BM25 and vector indices."""

        self.documents = documents
        texts = [d["content"] for d in documents]

        # BM25 index (keyword)
        tokenized = [text.lower().split() for text in texts]
        self.bm25 = BM25Okapi(tokenized)

        # Vector index (semantic)
        self.embeddings = self.embedding_model.encode(texts)

    def search(
        self,
        query: str,
        k: int = 10,
        bm25_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> list[dict]:
        """Hybrid search with score fusion."""

        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_scores = bm25_scores / (bm25_scores.max() + 1e-6)  # Normalize

        # Semantic scores
        query_embedding = self.embedding_model.encode([query])[0]
        semantic_scores = np.dot(self.embeddings, query_embedding)
        semantic_scores = (semantic_scores + 1) / 2  # Normalize to 0-1

        # Fuse scores
        combined_scores = (
            bm25_weight * bm25_scores +
            semantic_weight * semantic_scores
        )

        # Get top-k
        top_indices = np.argsort(combined_scores)[-k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                **self.documents[idx],
                "score": combined_scores[idx],
                "bm25_score": bm25_scores[idx],
                "semantic_score": semantic_scores[idx]
            })

        return results
```

---

## Long-Term: Full Stack Integration

### 7. LangGraph + Temporal (Week 3-4)

```python
# Primitive/agents/durable_agent.py
from langgraph.graph import StateGraph, END
from temporalio import workflow, activity
from typing import TypedDict

class AgentState(TypedDict):
    task: str
    messages: list
    tool_calls: list
    final_output: str | None

class DurableAgent:
    """LangGraph state machine with Temporal durability."""

    def __init__(self, spark: Spark):
        self.spark = spark
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("reason", self.reason)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("synthesize", self.synthesize)

        graph.set_entry_point("reason")
        graph.add_conditional_edges(
            "reason",
            self.route_after_reason,
            {
                "tool": "execute_tool",
                "done": "synthesize"
            }
        )
        graph.add_edge("execute_tool", "reason")
        graph.add_edge("synthesize", END)

        return graph.compile()

    @activity.defn
    async def reason(self, state: AgentState) -> AgentState:
        """LLM reasoning step."""
        # ... LLM call with tool descriptions
        return state

    @activity.defn
    async def execute_tool(self, state: AgentState) -> AgentState:
        """Execute tool via MCP."""
        # ... MCP tool execution
        return state

    @workflow.defn
    class AgentWorkflow:
        @workflow.run
        async def run(self, task: str) -> str:
            """Run agent as durable workflow."""
            state = AgentState(task=task, messages=[], tool_calls=[], final_output=None)

            # Run LangGraph, but each node is a Temporal activity
            result = await self.graph.ainvoke(state)

            return result["final_output"]
```

---

### 8. Apache Iceberg for Knowledge (Week 4)

```python
# Primitive/knowledge/iceberg_store.py
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, TimestampType, ListType, DoubleType

class IcebergKnowledgeStore:
    """Time-travel capable knowledge storage."""

    SCHEMA = Schema(
        NestedField(1, "id", StringType(), required=True),
        NestedField(2, "content", StringType(), required=True),
        NestedField(3, "source", StringType(), required=True),
        NestedField(4, "timestamp", TimestampType(), required=True),
        NestedField(5, "embedding", ListType(6, DoubleType())),
    )

    def __init__(self, warehouse_path: str = "data/warehouse"):
        self.catalog = load_catalog("default", **{
            "type": "sql",
            "uri": f"sqlite:///{warehouse_path}/catalog.db",
            "warehouse": warehouse_path,
        })

    def write(self, atoms: list[KnowledgeAtom]):
        """Write atoms to Iceberg table."""
        table = self.catalog.load_table("knowledge.atoms")
        df = pd.DataFrame([a.model_dump() for a in atoms])
        table.append(df)

    def query_at_time(self, query: str, as_of: datetime) -> list[KnowledgeAtom]:
        """Query knowledge as it existed at a point in time."""

        table = self.catalog.load_table("knowledge.atoms")

        # Find snapshot at time
        snapshot = None
        for s in table.metadata.snapshots:
            if s.timestamp_ms <= as_of.timestamp() * 1000:
                snapshot = s

        if not snapshot:
            return []

        # Query that snapshot
        scan = table.scan(snapshot_id=snapshot.snapshot_id)
        df = scan.to_pandas()

        return [KnowledgeAtom.model_validate(row) for _, row in df.iterrows()]

    def diff(self, time_a: datetime, time_b: datetime) -> tuple[list, list, list]:
        """What changed between two points in time?"""

        state_a = set(self.query_at_time("*", time_a))
        state_b = set(self.query_at_time("*", time_b))

        added = state_b - state_a
        removed = state_a - state_b
        # Modified would require content comparison

        return list(added), list(removed), []
```

---

## Implementation Checklist

### Phase 1: Foundation (Days 1-5)
- [ ] Install structlog, configure JSON logging
- [ ] Migrate core models to Pydantic v2
- [ ] Set up DuckDB telemetry tables
- [ ] Add correlation IDs to all logs

### Phase 2: Observability (Week 1)
- [ ] Install opentelemetry-sdk
- [ ] Create custom DuckDB exporter
- [ ] Add @traced decorator to key functions
- [ ] Create telemetry dashboard queries

### Phase 3: Knowledge (Week 2)
- [ ] Implement GraphRAG extraction
- [ ] Set up hybrid search (BM25 + vectors)
- [ ] Create knowledge graph visualization
- [ ] Test multi-hop queries

### Phase 4: Orchestration (Week 3-4)
- [ ] Install langgraph
- [ ] Define agent state machines
- [ ] Set up Temporal workers
- [ ] Integrate MCP for tools
- [ ] Test durable agent workflows

### Phase 5: Time Travel (Week 4+)
- [ ] Set up Apache Iceberg catalog
- [ ] Migrate knowledge tables
- [ ] Implement time-travel queries
- [ ] Build knowledge diff tools

---

*Start with structured logging. Everything else builds on it.*

— THE_FRAMEWORK

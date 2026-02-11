# MCP Server Landscape 2026

**Research Date**: 2026-02-06
**Purpose**: Evaluate production-ready MCP servers for truth_forge integration
**Focus**: Knowledge management, AI research, data engineering

---

## Executive Summary

This document catalogs production-ready Model Context Protocol (MCP) servers that align with truth_forge's mission of knowledge atomization, cognitive systems, and data analysis. The MCP ecosystem has grown to 8,250+ servers as of February 2026, with robust official and community support.

**Key Finding**: The MCP ecosystem provides comprehensive coverage for truth_forge's needs across database access, knowledge management, code analysis, and AI-powered reasoning.

---

## Official Anthropic MCP Servers

Source: [Official MCP Repository](https://github.com/modelcontextprotocol/servers)
Registry: [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/)

### Reference Implementations (6 Core Servers)

| Server | Capabilities | truth_forge Value |
|--------|-------------|-------------------|
| **Everything** | Reference/test server with prompts, resources, and tools | Testing and development baseline |
| **Fetch** | Web content fetching and conversion for LLM usage | Research ingestion, content extraction |
| **Filesystem** | Secure file operations with configurable access controls | Local data pipeline integration |
| **Git** | Read, search, and manipulate Git repositories | Codebase analysis, version tracking |
| **Memory** | Knowledge graph-based persistent memory system | Long-term context retention |
| **Sequential Thinking** | Dynamic and reflective problem-solving through thought sequences | Complex reasoning workflows |

**Integration Priority**: HIGH
**Installation**: Official npm packages, well-maintained
**Rationale**: These are the canonical implementations demonstrating MCP best practices.

---

## Category 1: Database & Analytics

### PostgreSQL MCP Server
**Source**: [@modelcontextprotocol/server-postgres](https://www.npmjs.com/package/@modelcontextprotocol/server-postgres)
**Maintained by**: Anthropic (official)

**Capabilities**:
- Read-only access to PostgreSQL databases
- Schema inspection
- SQL query execution
- Secure parameter binding

**truth_forge Value**: CRITICAL
- Direct access to BigQuery data via PostgreSQL interface
- Query spine.entity_unified for entity analysis
- Safe read-only mode prevents data corruption (per DATA PROTECTION LAWS)

**Installation Complexity**: LOW (npm package)

**Integration Opportunities**:
- Query entity hierarchies (L2-L8)
- Verify parent chains programmatically
- Generate entity relationship graphs
- Support natural language queries over structured data

---

### BigQuery MCP Server
**Source**: [Google Cloud Official](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)
**Maintained by**: Google Cloud

**Capabilities**:
- Fully managed, remote MCP server (preview as of Jan 2026)
- Natural language to SQL conversion
- Data visualization generation
- Conversational analytics
- Batch query execution

**truth_forge Value**: CRITICAL
- Native BigQuery integration (truth_forge's primary data warehouse)
- Eliminates need for intermediate PostgreSQL layer
- AI-powered query generation reduces manual SQL writing
- Supports llm_refinery and entity_unified pipelines

**Installation Complexity**: MEDIUM (requires GCP setup, OAuth)

**Integration Opportunities**:
- Replace manual BigQuery client code with MCP interface
- Enable natural language queries for non-technical users
- Automated entity_enrichment analysis
- Integration with knowledge graph memory servers

**References**:
- [Using BigQuery MCP for Data AI Agents](https://cloud.google.com/blog/products/data-analytics/using-the-fully-managed-remote-bigquery-mcp-server-to-build-data-ai-agents)
- [BigQuery MCP - Your Pocket AI Data Analyst](https://www.coupler.io/mcp/bigquery)

---

### DuckDB MCP Server
**Source**: [mcp-server-motherduck](https://github.com/motherduckdb/mcp-server-motherduck)
**Maintained by**: MotherDuck (official)

**Capabilities**:
- Local DuckDB files and in-memory databases
- S3-hosted databases
- MotherDuck cloud integration
- Read-only mode by default (with --read-write flag)
- SQL execution on CSV, Parquet, JSON files

**truth_forge Value**: HIGH
- Local analytics without BigQuery dependency
- OLAP workloads for entity clustering
- Direct file format support (CSV, Parquet, JSON)
- Cost-effective alternative for development/testing

**Installation Complexity**: LOW (uvx package)

**Integration Opportunities**:
- Local entity analysis before BigQuery upload
- Prototype clustering algorithms
- Generate summary statistics for pipelines
- Query conversation transcripts stored as Parquet

**References**:
- [DuckDB MCP Server: AI's Direct Line to Local Data](https://skywork.ai/skypage/en/duckdb-mcp-server-ai-local-data/1980508254926839808)
- [MCP + DuckDB: Connect AI to Data Pipelines](https://motherduck.com/blog/faster-data-pipelines-with-mcp-duckdb-ai/)

---

### SQLite MCP Server
**Source**: Multiple implementations (community)
**Maintained by**: Community

**Capabilities**:
- Local SQLite database access
- Schema exploration
- Read/write query execution
- Lightweight embedded database support

**truth_forge Value**: MEDIUM
- Local development databases
- Lightweight alternative for testing
- Embedded knowledge bases

**Installation Complexity**: LOW

**Integration Opportunities**:
- Local cache for entity metadata
- Development environment database
- Offline knowledge base storage

---

## Category 2: Knowledge Management & Memory

### Knowledge Graph Memory MCP Server
**Source**: [modelcontextprotocol/knowledge-graph-memory](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)
**Maintained by**: Anthropic (official)

**Capabilities**:
- Persistent memory storage using knowledge graph structures
- JSONL-based persistence
- Master database + named databases (work, personal, health)
- Entity and relation modeling
- Semantic search capabilities

**truth_forge Value**: CRITICAL
- Aligns perfectly with truth_forge's entity-relationship model
- Persistent context across sessions
- Knowledge graph = spine.entity_unified conceptual match
- L2-L8 hierarchy mapping

**Installation Complexity**: LOW (npm package)

**Integration Opportunities**:
- Store entity relationships as knowledge graph
- Cross-reference with BigQuery entity data
- Maintain conversational context across pipeline runs
- Build semantic search over entity attributes

**References**:
- [Knowledge Graph Memory MCP Server](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)
- [Memento MCP: Knowledge Graph Memory System](https://github.com/gannonh/memento-mcp)

---

### Qdrant Memory MCP Server
**Source**: [mcp-qdrant-memory](https://github.com/delorenj/mcp-qdrant-memory)
**Maintained by**: Community (delorenj)

**Capabilities**:
- Vector database integration (Qdrant)
- Semantic search using OpenAI embeddings
- Knowledge graph implementation
- File-based persistence
- High-dimensional vector space encoding

**truth_forge Value**: HIGH
- Semantic search over entity descriptions
- Clustering entities by embedding similarity
- "Find entities semantically similar to X"
- Complement to exact match SQL queries

**Installation Complexity**: MEDIUM (requires Qdrant setup)

**Integration Opportunities**:
- Embed entity descriptions using OpenAI
- Cluster conversations by semantic similarity
- "Find conversations about topic X" using embeddings
- Enrich entity_unified with vector search results

**References**:
- [MCP Memory Server with Qdrant Persistence](https://mcp.so/server/mcp-qdrant-memory)

---

### Neo4j Knowledge Graph Memory
**Source**: [Neo4j MCP implementations](https://pickaxe.co/ai/actions/mcp/neo4j-knowledge-graph-memory)
**Maintained by**: Community

**Capabilities**:
- Neo4j graph database integration
- Cypher query support
- Vector embeddings with OpenAI
- Automatic schema initialization
- Temporal awareness

**truth_forge Value**: MEDIUM-HIGH
- Production-grade graph database (vs. JSONL)
- Cypher queries for complex relationship traversal
- Scales beyond file-based knowledge graphs

**Installation Complexity**: HIGH (requires Neo4j instance)

**Integration Opportunities**:
- Graph-based entity hierarchy visualization
- "Find all L4 entities connected to L8 entity via L6"
- Relationship pattern mining
- Temporal analysis of entity evolution

---

### Obsidian MCP Server
**Source**: [obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server)
**Maintained by**: Community (cyanheads)

**Capabilities**:
- Read/write access to Obsidian vaults
- Markdown file management
- Tag and frontmatter manipulation
- Vault-wide search (text and regex)
- Search-and-replace operations

**truth_forge Value**: HIGH
- truth_forge uses extensive markdown documentation
- docs/ directory as knowledge base
- Integration with existing note-taking workflow
- Bridge between unstructured docs and structured entities

**Installation Complexity**: MEDIUM (requires Obsidian Local REST API plugin)

**Integration Opportunities**:
- Index docs/ directory for semantic search
- Auto-generate entity documentation
- Link ADRs to entity_unified records
- Sync framework/ docs with knowledge graph

**References**:
- [Obsidian MCP Server](https://github.com/cyanheads/obsidian-mcp-server)
- [Using MCP to Query Obsidian](https://dev.to/vorsprung/using-the-model-context-protocol-mcp-to-query-obsidian-note-taking-3fhf)

---

### Notion MCP Server
**Source**: [Notion Official MCP](https://developers.notion.com/docs/mcp)
**Maintained by**: Notion (official)

**Capabilities**:
- Page & block interaction (CRUD)
- Database operations (query with filters/sorts)
- Workspace-wide search
- Semantic search across Notion + integrations (Slack, Google Drive, Jira)
- Third-party tool integration

**truth_forge Value**: MEDIUM
- Centralized knowledge base if team expands
- Cross-platform search (Notion + Slack + Drive)
- Collaborative documentation

**Installation Complexity**: LOW (hosted MCP server)

**Integration Opportunities**:
- Migrate docs/ to Notion for collaboration
- Search across truth_forge docs + external resources
- Automated project tracking

**References**:
- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)
- [How to Use Claude with Notion MCP](https://www.getclockwise.com/blog/claude-notion-mcp-integration)

---

## Category 3: Code Analysis & Development

### GitHub MCP Server
**Source**: [github/github-mcp-server](https://github.com/github/github-mcp-server)
**Maintained by**: GitHub (official)

**Capabilities**:
- Read repositories and code files
- Manage issues and PRs
- Analyze code
- Automate workflows
- GitHub code search syntax support
- Language, path, and organization filters

**truth_forge Value**: HIGH
- Analyze truth_forge codebase
- Track issues and PRs
- Code search across repository history
- Automate compliance reports

**Installation Complexity**: LOW (npm package)

**Integration Opportunities**:
- "Find all DLQ pattern implementations"
- "List files violating type hint requirements"
- Auto-generate COMPLIANCE_REPORT.md
- Track ADR implementation status

**References**:
- [GitHub's Official MCP Server](https://github.com/github/github-mcp-server)
- [Top 10 MCP Servers for 2025](https://dev.to/fallon_jimmy/top-10-mcp-servers-for-2025-yes-githubs-included-15jg)

---

### Git MCP Server
**Source**: [@modelcontextprotocol/server-git](https://github.com/modelcontextprotocol/servers)
**Maintained by**: Anthropic (official)

**Capabilities**:
- Read, search, and manipulate Git repositories
- Commit history analysis
- Branch management
- Diff generation

**truth_forge Value**: MEDIUM
- Local Git operations without GitHub API
- Offline repository analysis
- Commit history research

**Installation Complexity**: LOW (npm package)

**Integration Opportunities**:
- Analyze molt lineage (Truth_Engine → truth_forge)
- Track framework/ evolution
- Commit message analysis

---

### Code Index MCP Server
**Source**: [code-index-mcp](https://github.com/johnhuang316/code-index-mcp)
**Maintained by**: Community (johnhuang316)

**Capabilities**:
- Intelligent code indexing
- Advanced search capabilities
- Detailed code analysis
- Minimal setup required

**truth_forge Value**: HIGH
- Index entire truth_forge codebase
- "Find all pipeline implementations"
- Code pattern discovery
- Refactoring support

**Installation Complexity**: LOW

**Integration Opportunities**:
- Index src/, pipelines/, apps/
- "Find all uses of SafeBigQueryWriter"
- Identify code duplication
- Generate architecture diagrams

---

### Claude Context (Zilliz)
**Source**: [claude-context](https://github.com/zilliztech/claude-context)
**Maintained by**: Zilliz

**Capabilities**:
- Codebase directory indexing
- Hybrid search (BM25 + dense vector)
- Natural language code queries
- Make entire codebase context for coding agents

**truth_forge Value**: CRITICAL
- Entire codebase as context for Claude Code
- "Show me all error handling patterns"
- Contextual code generation
- Architecture-aware suggestions

**Installation Complexity**: MEDIUM (requires Milvus/Zilliz)

**Integration Opportunities**:
- Index truth_forge for Claude Code sessions
- "Generate code following framework/ standards"
- Compliance checking against THE FOUR PILLARS
- Auto-suggest DLQ patterns

**References**:
- [Claude Context: Code Search MCP](https://github.com/zilliztech/claude-context)

---

### MCP Code Checker
**Source**: [mcp-code-checker](https://github.com/MarcusJellinghaus/mcp-code-checker)
**Maintained by**: Community (MarcusJellinghaus)

**Capabilities**:
- Pylint integration
- Pytest integration
- Smart LLM-friendly prompts
- Code analysis and fix suggestions

**truth_forge Value**: HIGH
- Automated code quality enforcement
- Aligns with framework/standards/code_quality/
- Pre-commit hook integration
- CI/CD quality gates

**Installation Complexity**: LOW

**Integration Opportunities**:
- Run pylint checks via MCP
- Execute pytest suites conversationally
- "Run tests for src/truth_forge/services/"
- Generate COMPLIANCE_REPORT.md automatically

**References**:
- [MCP Code Checker](https://github.com/MarcusJellinghaus/mcp-code-checker)

---

## Category 4: Web Access & Search

### Brave Search MCP Server
**Source**: [brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server)
**Maintained by**: Brave (official)

**Capabilities**:
- Web search via Brave Search API
- Local business search
- Image search
- Video search
- News search
- AI-powered summarization

**truth_forge Value**: MEDIUM
- Research external sources
- Competitive analysis
- Technology trend research
- Documentation lookup

**Installation Complexity**: LOW (requires Brave API key)

**Integration Opportunities**:
- "Find latest papers on knowledge graphs"
- "Research MCP best practices"
- Auto-populate research/ directory
- Fact-checking and verification

**References**:
- [Brave Search MCP Server](https://github.com/brave/brave-search-mcp-server)

---

### Puppeteer MCP Server
**Source**: [puppeteer-mcp-server](https://github.com/merajmehrabi/puppeteer-mcp-server)
**Maintained by**: Community (multiple implementations)

**Capabilities**:
- Browser automation
- Web scraping
- Screenshot capture
- Form interaction
- Navigation and data extraction

**truth_forge Value**: MEDIUM
- Automated data collection
- Web-based knowledge extraction
- Documentation screenshot capture
- Dynamic content scraping

**Installation Complexity**: MEDIUM (requires Chrome/Chromium)

**Integration Opportunities**:
- Scrape research papers
- Extract documentation from websites
- Generate visual documentation
- Automated testing for apps/

**References**:
- [Puppeteer MCP Server](https://www.pulsemcp.com/servers/modelcontextprotocol-puppeteer)

---

### Brave Deep Research MCP
**Source**: [brave-deep-research-mcp](https://glama.ai/mcp/servers/@suthio/brave-deep-research-mcp)
**Maintained by**: Community (suthio)

**Capabilities**:
- Brave Search + Puppeteer integration
- Deep research workflows
- Multi-page content extraction
- Follow linked pages
- Comprehensive web research

**truth_forge Value**: HIGH
- Automated research pipeline
- Multi-source knowledge aggregation
- "Research topic X and extract key insights"
- Feed research/ directory

**Installation Complexity**: MEDIUM

**Integration Opportunities**:
- Automated literature review
- Competitive intelligence gathering
- Technology landscape analysis
- Research synthesis

**References**:
- [Brave Deep Research MCP](https://glama.ai/mcp/servers/@suthio/brave-deep-research-mcp)

---

## Category 5: AI Reasoning & Cognition

### Sequential Thinking MCP Server
**Source**: [@modelcontextprotocol/server-sequential-thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
**Maintained by**: Anthropic (official)

**Capabilities**:
- Dynamic and reflective problem-solving
- Structured thinking process
- Break down complex problems into steps
- Revise and refine thoughts iteratively
- Branch into alternative reasoning paths
- Adjust thought count dynamically
- Generate and verify hypotheses

**truth_forge Value**: CRITICAL
- Aligns with THE PATTERN (HOLD:AGENT:HOLD)
- Complex reasoning for entity enrichment
- Multi-step pipeline design
- Reflective analysis of entity relationships

**Installation Complexity**: LOW (npm package)

**Integration Opportunities**:
- Design complex entity enrichment workflows
- "Analyze the relationship between L4 and L8 entities"
- Multi-step debugging of pipeline failures
- Architecture decision reasoning (complement to ADRs)

**References**:
- [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [How Sequential Thinking Transforms AI Problem-Solving](https://medium.com/@Micheal-Lanham/building-smarter-ai-agents-how-sequential-thinking-mcp-transforms-complex-problem-solving-443e68b4d487)

---

### MAS Sequential Thinking
**Source**: [mcp-server-mas-sequential-thinking](https://github.com/FradSer/mcp-server-mas-sequential-thinking)
**Maintained by**: Community (FradSer)

**Capabilities**:
- Multi-Agent System (MAS) architecture
- Specialized AI agents for different cognitive angles
- Agno framework integration
- Advanced sequential reasoning

**truth_forge Value**: HIGH
- Multi-perspective analysis
- Complex entity relationship reasoning
- Distributed problem-solving

**Installation Complexity**: MEDIUM

**Integration Opportunities**:
- Analyze entities from multiple perspectives (semantic, structural, temporal)
- "Evaluate pipeline design using multiple reasoning agents"
- Distributed entity enrichment strategies

---

## Category 6: Code Execution & Notebooks

### Jupyter MCP Server
**Source**: [jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server)
**Maintained by**: Datalayer (official)

**Capabilities**:
- Real-time Jupyter notebook interaction
- Edit, execute, and document code
- Cell execution with timeout
- Multimodal output (images, charts)
- Magic commands and shell commands
- Data analysis and visualization

**truth_forge Value**: HIGH
- Interactive data analysis
- Entity clustering experiments
- Visualization generation
- Exploratory data analysis

**Installation Complexity**: MEDIUM (requires JupyterLab)

**Integration Opportunities**:
- Analyze entity_unified data interactively
- Generate clustering visualizations
- Prototype enrichment algorithms
- Share analysis notebooks in docs/research/

**References**:
- [Jupyter MCP Documentation](https://www.jan.ai/docs/desktop/mcp-examples/data-analysis/jupyter)
- [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server)

---

### ClaudeJupy
**Source**: [ClaudeJupy](https://mcpmarket.com/server/claudejupy)
**Maintained by**: Community

**Capabilities**:
- Persistent Jupyter kernel for Claude Code
- Python code execution across conversation turns
- State preservation
- Create and manage Jupyter notebooks
- Auto-detect virtual environments

**truth_forge Value**: HIGH
- Persistent Python environment for Claude Code
- Stateful data analysis sessions
- Environment-aware execution

**Installation Complexity**: MEDIUM

**Integration Opportunities**:
- Long-running entity analysis sessions
- Maintain state across multiple queries
- "Continue previous clustering analysis"
- Integration with truth_forge .venv

---

### Python Code Execution MCP
**Source**: Multiple implementations (Pydantic, others)
**Maintained by**: Community

**Capabilities**:
- Direct Python code execution
- No Jupyter overhead
- Simple code evaluation
- Quick prototyping

**truth_forge Value**: MEDIUM
- Lightweight code execution
- Script testing
- Quick calculations

**Installation Complexity**: LOW

**Integration Opportunities**:
- Test entity processing logic
- Prototype utility functions
- Quick data transformations

---

## Category 7: Cloud Infrastructure

### AWS Lambda MCP Server
**Source**: [awslabs/mcp](https://github.com/awslabs/mcp)
**Maintained by**: AWS (official)

**Capabilities**:
- Run Lambda functions as MCP tools
- No code changes required
- Bridge between MCP clients and AWS Lambda
- Serverless MCP architecture

**truth_forge Value**: LOW (not currently using AWS)
- Potential future cloud migration
- Serverless pipeline execution

**Installation Complexity**: HIGH (requires AWS setup)

---

### AWS S3 MCP Server
**Source**: Community implementations
**Maintained by**: Various

**Capabilities**:
- S3 bucket access
- File upload/download
- Object management
- Integration with data pipelines

**truth_forge Value**: LOW (using GCS/BigQuery)
- Cloud storage alternative
- Data archive solution

**Installation Complexity**: MEDIUM

---

### AWS Serverless MCP Server
**Source**: [AWS Serverless MCP](https://aws.amazon.com/blogs/compute/introducing-aws-serverless-mcp-server-ai-powered-development-for-modern-applications/)
**Maintained by**: AWS (official)

**Capabilities**:
- AI-powered serverless development
- Combine AI with serverless expertise
- Modern application architecture assistance

**truth_forge Value**: LOW
- Future cloud architecture exploration

**Installation Complexity**: HIGH

**References**:
- [Introducing AWS Serverless MCP Server](https://aws.amazon.com/blogs/compute/introducing-aws-serverless-mcp-server-ai-powered-development-for-modern-applications/)

---

## Category 8: Container & Kubernetes

### Kubernetes MCP Server
**Source**: [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)
**Maintained by**: Containers community (official)

**Capabilities**:
- Kubernetes cluster management
- 40+ tools for resource management
- Helm deployments
- Port forwarding
- OpenShift support

**truth_forge Value**: LOW (not currently using K8s)
- Future container orchestration

**Installation Complexity**: HIGH (requires K8s cluster)

**References**:
- [Managing K8s with MCP](https://docs.vultr.com/how-to-manage-kubernetes-clusters-using-k8s-mcp-server)

---

## Category 9: Testing & Quality Assurance

### Pytest MCP Server
**Source**: [pytest-mcp-server](https://github.com/tosin2013/pytest-mcp-server)
**Maintained by**: Community (tosin2013)

**Capabilities**:
- Track pytest failures
- 9 principles of debugging
- Systematic error resolution
- Test result context for LLMs

**truth_forge Value**: MEDIUM-HIGH
- Automated test execution
- Test-driven development
- CI/CD integration

**Installation Complexity**: LOW

**Integration Opportunities**:
- "Run tests for pipelines/llm_refinery/"
- Analyze test failures
- Generate test coverage reports
- Integration with framework/standards/testing/

**References**:
- [Pytest MCP Server](https://github.com/tosin2013/pytest-mcp-server)

---

## Priority Integration Roadmap

### Tier 1: Critical (Immediate Integration)
1. **BigQuery MCP Server** - Native data warehouse access
2. **Knowledge Graph Memory** - Persistent entity context
3. **Sequential Thinking** - Complex reasoning workflows
4. **Claude Context** - Codebase-aware code generation
5. **GitHub MCP Server** - Repository analysis and automation

**Rationale**: These align directly with truth_forge's core workflows (entity processing, knowledge management, code quality).

---

### Tier 2: High Priority (Next Quarter)
1. **Qdrant Memory MCP** - Semantic search over entities
2. **Jupyter MCP Server** - Interactive data analysis
3. **Obsidian MCP Server** - Documentation knowledge base
4. **Code Index MCP** - Codebase pattern discovery
5. **DuckDB MCP Server** - Local analytics

**Rationale**: Enhance existing capabilities with semantic search, interactive analysis, and local development tools.

---

### Tier 3: Medium Priority (Evaluation Phase)
1. **Brave Search MCP** - External research
2. **Brave Deep Research MCP** - Multi-source knowledge aggregation
3. **Notion MCP** - Collaborative documentation
4. **MCP Code Checker** - Automated quality enforcement
5. **Pytest MCP Server** - Test automation

**Rationale**: Improve research workflows, collaboration, and quality assurance.

---

### Tier 4: Low Priority (Future Consideration)
1. **AWS Lambda/S3/Serverless MCP** - Cloud migration
2. **Kubernetes MCP** - Container orchestration
3. **Neo4j MCP** - Production graph database
4. **Puppeteer MCP** - Web scraping

**Rationale**: Not immediately needed but valuable for scaling and future architecture.

---

## Installation & Configuration Complexity Matrix

| Server | Installation | Dependencies | Maintenance | Skill Level |
|--------|-------------|--------------|-------------|-------------|
| BigQuery MCP | Medium | GCP, OAuth | Low | Medium |
| Knowledge Graph Memory | Low | npm | Low | Low |
| Sequential Thinking | Low | npm | Low | Low |
| Claude Context | Medium | Milvus/Zilliz | Medium | Medium |
| GitHub MCP | Low | npm, GitHub token | Low | Low |
| Qdrant Memory | Medium | Qdrant, OpenAI API | Medium | Medium |
| Jupyter MCP | Medium | JupyterLab | Medium | Medium |
| Obsidian MCP | Medium | Obsidian, REST API plugin | Low | Medium |
| DuckDB MCP | Low | uvx | Low | Low |
| Brave Search | Low | npm, Brave API key | Low | Low |
| Code Index | Low | npm | Low | Low |
| PostgreSQL MCP | Low | npm | Low | Low |
| Notion MCP | Low | Hosted | Low | Low |
| Neo4j MCP | High | Neo4j instance | High | High |
| AWS Lambda MCP | High | AWS account, IAM | High | High |
| Kubernetes MCP | High | K8s cluster | High | High |

---

## Integration with Existing truth_forge Infrastructure

### Current MCP Configuration
truth_forge already has MCP infrastructure:
- `/Users/jeremyserna/truth_forge/src/mcp_server.py`
- `/Users/jeremyserna/truth_forge/apps/genesis/src/mcp_server.py`
- MCP documentation in `docs/operations/tools/mcp_query_entities.md`

**Action**: Audit existing MCP setup and identify integration points.

---

### BigQuery Integration Strategy
```python
# Current: Manual BigQuery client
from google.cloud import bigquery
client = bigquery.Client()
query = "SELECT * FROM spine.entity_unified WHERE level = 8"
results = client.query(query).result()

# Future: MCP-based natural language queries
# "Show me all L8 entities from the last week"
# MCP server handles query generation, execution, and formatting
```

**Benefit**: Reduce boilerplate, enable natural language queries, improve accessibility.

---

### Knowledge Graph Integration Strategy
```python
# Current: BigQuery stores entities in relational format
# entity_id, parent_id, level, text_content, source_pipeline

# Future: Dual storage
# 1. BigQuery (source of truth, analytics)
# 2. Knowledge Graph Memory (semantic relationships, context)

# Sync pipeline:
# BigQuery → Extract entities → Knowledge Graph Memory → Semantic search
```

**Benefit**: Enable "Find entities semantically similar to X" queries.

---

### Code Quality Integration Strategy
```bash
# Current: Manual quality checks
mypy src/ --strict
ruff check src/
pytest tests/

# Future: MCP-based conversational quality checks
# "Run quality checks on src/truth_forge/services/"
# "Find files violating type hint requirements"
# "Generate compliance report for pipelines/"
```

**Benefit**: Lower barrier to quality enforcement, automated reporting.

---

## Security & Data Protection Considerations

### Per DATA PROTECTION LAWS

**CRITICAL**: Any MCP server with write access to BigQuery MUST:
1. Use SafeBigQueryWriter (no streaming inserts)
2. Enforce ALLOWED_PIPELINE source validation
3. Create backups before DELETE operations
4. Validate parent chains before writes
5. Use structured logging (no silent failures)

**Implementation**:
```python
# Wrap MCP BigQuery tools with enforcement
from pipelines.core.enforcement import enforce_before_write

@enforce_before_write
def mcp_bigquery_write(records: list[dict]) -> int:
    # MCP server call here
    ...
```

---

### Read-Only Mode by Default
All database MCP servers should run in read-only mode unless explicitly required:
- `--read-only` flag for DuckDB
- `READ_ONLY=true` environment variable
- PostgreSQL read-only user

**Rationale**: Prevent accidental data corruption, align with Fail-Safe pillar.

---

### API Key Management
MCP servers requiring API keys (Brave Search, OpenAI, etc.):
- Store in `config/local/` (gitignored)
- Use environment variables
- Never commit to repository
- Rotate keys periodically

**Example**: `config/local/mcp_secrets.env`

---

## Performance & Scalability Considerations

### Local vs. Remote MCP Servers
| Type | Latency | Scalability | Cost | Use Case |
|------|---------|-------------|------|----------|
| Local (stdio) | Low | Limited | None | Development, testing |
| Remote (HTTP) | Medium | High | Variable | Production, distributed |
| Hosted (SaaS) | Medium | High | Subscription | Notion, Brave Search |

**Recommendation**: Use local MCP servers for development, remote for production.

---

### Caching Strategies
MCP servers with expensive operations (web search, embeddings):
- Implement result caching
- Use DuckDB for local cache
- TTL-based invalidation
- Share cache across sessions

**Example**: Cache Brave Search results for 24 hours.

---

## Testing Strategy for MCP Integration

### Unit Testing MCP Tools
```python
import pytest
from fastmcp.testing import FastMCPClient

@pytest.fixture
def mcp_client():
    return FastMCPClient(server=truth_forge_mcp)

def test_entity_query_tool(mcp_client):
    result = mcp_client.call_tool(
        "query_entities",
        {"level": 8, "limit": 10}
    )
    assert len(result) <= 10
    assert all(e["level"] == 8 for e in result)
```

**References**:
- [Testing FastMCP Servers](https://gofastmcp.com/patterns/testing)
- [Unit Testing MCP Servers Guide](https://mcpcat.io/guides/writing-unit-tests-mcp-servers/)

---

### Integration Testing
Test end-to-end workflows:
1. Query BigQuery via MCP
2. Store results in Knowledge Graph Memory
3. Semantic search via Qdrant
4. Generate report via Sequential Thinking

**Approach**: Use pytest fixtures for MCP server lifecycle management.

---

## Cost Analysis

### Free Tier Options
- **Anthropic Official Servers**: Free (Memory, Sequential Thinking, Git, Filesystem)
- **GitHub MCP**: Free (with GitHub account)
- **DuckDB MCP**: Free (local)
- **Obsidian MCP**: Free (requires Obsidian license)

---

### Paid Services
| Service | Cost Model | Estimated Monthly |
|---------|-----------|-------------------|
| BigQuery MCP | GCP usage (existing) | $0 (already paying) |
| Brave Search | Free tier: 2,000 queries/month | $0-$5 |
| OpenAI Embeddings (Qdrant) | $0.00002/1K tokens | $5-$20 |
| Notion MCP | Included with Notion subscription | $0 (if using Notion) |
| MotherDuck (DuckDB) | Free tier available | $0-$10 |

**Total Estimated**: $0-$35/month for Tier 1 + Tier 2 servers.

---

## Maintenance & Support

### Official Support Channels
- **Anthropic MCP**: GitHub issues, Discord
- **BigQuery MCP**: Google Cloud support
- **GitHub MCP**: GitHub support
- **Brave Search**: API documentation, email support

---

### Community Resources
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- [Best of MCP Servers](https://github.com/tolkonepiu/best-of-mcp-servers)
- [MCP Server Directory](https://www.pulsemcp.com/servers)
- [MCP Registry](https://registry.modelcontextprotocol.io/)

---

## Recommended First Integration

### Week 1: Knowledge Graph Memory
**Why**: Low complexity, high value, no external dependencies.

**Steps**:
1. Install `@modelcontextprotocol/server-memory`
2. Configure with truth_forge knowledge domains
3. Test with entity data from BigQuery
4. Integrate with Claude Code sessions

**Success Criteria**:
- Store 100 entity relationships
- Query "Find entities related to X"
- Persist across sessions

---

### Week 2: BigQuery MCP
**Why**: Critical infrastructure, replaces manual BigQuery code.

**Steps**:
1. Set up Google Cloud MCP server (preview)
2. Configure OAuth and permissions (read-only first)
3. Test natural language queries
4. Integrate with entity_unified table

**Success Criteria**:
- Query entity_unified via natural language
- Generate entity reports conversationally
- Compare performance to manual SQL

---

### Week 3: Sequential Thinking
**Why**: Enhance reasoning for complex entity analysis.

**Steps**:
1. Install `@modelcontextprotocol/server-sequential-thinking`
2. Test with complex entity relationship questions
3. Integrate with pipeline design workflows
4. Document use cases in docs/research/

**Success Criteria**:
- Solve multi-step entity analysis problem
- Generate structured reasoning trace
- Compare to non-sequential approach

---

## Long-Term Vision

### Unified MCP Architecture
```
┌─────────────────────────────────────────────────────────┐
│                     truth_forge                          │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  BigQuery  │  │ Knowledge  │  │ Sequential │        │
│  │    MCP     │◄─┤   Graph    │◄─┤  Thinking  │        │
│  │            │  │   Memory   │  │    MCP     │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│         │              │                │               │
│         └──────────┬───┴────────────────┘               │
│                    │                                    │
│              ┌─────▼─────┐                              │
│              │  Claude   │                              │
│              │   Code    │                              │
│              └───────────┘                              │
│                    │                                    │
│         ┌──────────┼──────────┐                         │
│         │          │          │                         │
│   ┌─────▼───┐ ┌───▼────┐ ┌───▼────┐                    │
│   │ GitHub  │ │ Jupyter│ │ Code   │                    │
│   │  MCP    │ │  MCP   │ │ Index  │                    │
│   └─────────┘ └────────┘ └────────┘                    │
└─────────────────────────────────────────────────────────┘
```

**Goal**: Seamless knowledge flow across data storage, reasoning, code analysis, and execution.

---

## Conclusion

The MCP ecosystem provides comprehensive tooling for truth_forge's knowledge management, data engineering, and AI research workflows. The priority integration roadmap focuses on:

1. **Data Access**: BigQuery MCP for native warehouse queries
2. **Knowledge Management**: Knowledge Graph Memory for persistent context
3. **Reasoning**: Sequential Thinking for complex analysis
4. **Code Quality**: Claude Context for codebase-aware generation
5. **Automation**: GitHub MCP for repository operations

**Next Actions**:
1. Audit existing MCP infrastructure in truth_forge
2. Install and test Tier 1 servers in development
3. Document integration patterns in framework/standards/
4. Create ADR for MCP architecture decisions
5. Train team on MCP usage (if applicable)

**Alignment with THE FRAMEWORK**:
- **Fail-Safe**: Read-only modes, backups, DLQ patterns
- **No Magic**: Explicit configurations, documented servers
- **Observability**: Structured logging, MCP tool traces
- **Idempotency**: Deterministic queries, reproducible results

---

## References & Sources

### Official Documentation
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Registry](https://registry.modelcontextprotocol.io/)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP Servers](https://mcpmarket.com/businesses/anthropic)

### Directories & Catalogs
- [PulseMCP Directory](https://www.pulsemcp.com/servers) - 8,250+ servers
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- [Best of MCP Servers](https://github.com/tolkonepiu/best-of-mcp-servers)
- [MCP Server Finder](https://www.mcpserverfinder.com/)
- [APITracker MCP Directory](https://apitracker.io/mcp-servers)

### Database & Analytics
- [BigQuery MCP Documentation](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)
- [Using BigQuery MCP for Data AI Agents](https://cloud.google.com/blog/products/data-analytics/using-the-fully-managed-remote-bigquery-mcp-server-to-build-data-ai-agents)
- [MotherDuck DuckDB MCP](https://motherduck.com/blog/faster-data-pipelines-with-mcp-duckdb-ai/)
- [PostgreSQL MCP by Anthropic](https://www.pulsemcp.com/servers/modelcontextprotocol-postgres)

### Knowledge Management
- [Knowledge Graph Memory MCP](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)
- [Memento MCP: Knowledge Graph Memory System](https://github.com/gannonh/memento-mcp)
- [Qdrant Memory MCP](https://mcp.so/server/mcp-qdrant-memory)
- [Obsidian MCP Server](https://github.com/cyanheads/obsidian-mcp-server)
- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)

### Code Analysis & Development
- [GitHub Official MCP Server](https://github.com/github/github-mcp-server)
- [Claude Context: Code Search MCP](https://github.com/zilliztech/claude-context)
- [Code Index MCP](https://github.com/johnhuang316/code-index-mcp)
- [MCP Code Checker](https://github.com/MarcusJellinghaus/mcp-code-checker)

### Web Access & Search
- [Brave Search MCP Server](https://github.com/brave/brave-search-mcp-server)
- [Brave Deep Research MCP](https://glama.ai/mcp/servers/@suthio/brave-deep-research-mcp)
- [Puppeteer MCP Server](https://www.pulsemcp.com/servers/modelcontextprotocol-puppeteer)

### AI Reasoning
- [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [How Sequential Thinking Transforms AI](https://medium.com/@Micheal-Lanham/building-smarter-ai-agents-how-sequential-thinking-mcp-transforms-complex-problem-solving-443e68b4d487)

### Execution & Notebooks
- [Jupyter MCP Documentation](https://www.jan.ai/docs/desktop/mcp-examples/data-analysis/jupyter)
- [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server)
- [ClaudeJupy](https://mcpmarket.com/server/claudejupy)

### Cloud & Infrastructure
- [AWS MCP Servers](https://github.com/awslabs/mcp)
- [AWS Serverless MCP](https://aws.amazon.com/blogs/compute/introducing-aws-serverless-mcp-server-ai-powered-development-for-modern-applications/)
- [Kubernetes MCP Server](https://github.com/containers/kubernetes-mcp-server)

### Testing & Quality
- [Testing FastMCP Servers](https://gofastmcp.com/patterns/testing)
- [Unit Testing MCP Servers Guide](https://mcpcat.io/guides/writing-unit-tests-mcp-servers/)
- [Pytest MCP Server](https://github.com/tosin2013/pytest-mcp-server)

### Community & Articles
- [Top 10 MCP Servers for 2025](https://dev.to/fallon_jimmy/top-10-mcp-servers-for-2025-yes-githubs-included-15jg)
- [The 22 Best MCP Servers](https://desktopcommander.app/blog/2025/11/25/best-mcp-servers/)
- [10 Awesome MCP Servers - KDnuggets](https://www.kdnuggets.com/10-awesome-mcp-servers)
- [Using MCP to Query Obsidian](https://dev.to/vorsprung/using-the-model-context-protocol-mcp-to-query-obsidian-note-taking-3fhf)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-06
**Author**: Claude Sonnet 4.5 (via research)
**Review Status**: Initial research - requires Jeremy validation

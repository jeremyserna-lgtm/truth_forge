# MCP Servers at a Glance

**Quick reference table for MCP server selection**

---

## Priority Matrix

| Server | Priority | Complexity | Cost | truth_forge Fit |
|--------|----------|------------|------|-----------------|
| **BigQuery MCP** | ⭐⭐⭐⭐⭐ | Medium | $0 | Perfect - Native data warehouse |
| **Knowledge Graph Memory** | ⭐⭐⭐⭐⭐ | Low | $0 | Perfect - Entity relationships |
| **Sequential Thinking** | ⭐⭐⭐⭐⭐ | Low | $0 | Perfect - THE PATTERN alignment |
| **Claude Context** | ⭐⭐⭐⭐⭐ | Medium | $0-10 | Perfect - Codebase context |
| **GitHub MCP** | ⭐⭐⭐⭐⭐ | Low | $0 | Perfect - Repository automation |
| **Qdrant Memory** | ⭐⭐⭐⭐ | Medium | $5-20 | Excellent - Semantic search |
| **Jupyter MCP** | ⭐⭐⭐⭐ | Medium | $0 | Excellent - Interactive analysis |
| **Obsidian MCP** | ⭐⭐⭐⭐ | Medium | $0 | Excellent - Docs knowledge base |
| **Code Index** | ⭐⭐⭐⭐ | Low | $0 | Excellent - Pattern discovery |
| **DuckDB MCP** | ⭐⭐⭐⭐ | Low | $0 | Excellent - Local analytics |
| **Brave Search** | ⭐⭐⭐ | Low | $0-5 | Good - External research |
| **Brave Deep Research** | ⭐⭐⭐ | Medium | $0-5 | Good - Multi-source aggregation |
| **Notion MCP** | ⭐⭐⭐ | Low | $0 | Good - Collaborative docs |
| **MCP Code Checker** | ⭐⭐⭐ | Low | $0 | Good - Quality enforcement |
| **Pytest MCP** | ⭐⭐⭐ | Low | $0 | Good - Test automation |
| **PostgreSQL MCP** | ⭐⭐ | Low | $0 | Fair - Alternative DB access |
| **Git MCP** | ⭐⭐ | Low | $0 | Fair - Local Git ops |
| **Puppeteer MCP** | ⭐⭐ | Medium | $0 | Fair - Web scraping |
| **Neo4j MCP** | ⭐⭐ | High | $0-50 | Fair - Production graph DB |
| **AWS Lambda MCP** | ⭐ | High | Variable | Low - Not using AWS |
| **AWS S3 MCP** | ⭐ | Medium | Variable | Low - Using GCS |
| **Kubernetes MCP** | ⭐ | High | Variable | Low - Not using K8s |

---

## By Use Case

### Data Access & Analytics
| Server | Use Case | Setup Time |
|--------|----------|------------|
| BigQuery MCP | Query spine.entity_unified via natural language | 10 min |
| DuckDB MCP | Local analytics, prototyping | 5 min |
| PostgreSQL MCP | Alternative DB interface | 5 min |
| Jupyter MCP | Interactive data exploration | 15 min |

### Knowledge Management
| Server | Use Case | Setup Time |
|--------|----------|------------|
| Knowledge Graph Memory | Store entity relationships persistently | 5 min |
| Qdrant Memory | Semantic search over entities | 20 min |
| Obsidian MCP | Index docs/ directory | 15 min |
| Notion MCP | Collaborative documentation | 5 min |

### Code Quality & Development
| Server | Use Case | Setup Time |
|--------|----------|------------|
| Claude Context | Codebase-aware code generation | 20 min |
| GitHub MCP | Repository analysis, PR automation | 5 min |
| Code Index | Pattern discovery, refactoring | 5 min |
| MCP Code Checker | Automated pylint/pytest checks | 5 min |
| Git MCP | Local Git operations | 5 min |

### AI Reasoning
| Server | Use Case | Setup Time |
|--------|----------|------------|
| Sequential Thinking | Multi-step complex reasoning | 5 min |
| MAS Sequential Thinking | Multi-agent perspective analysis | 15 min |

### External Research
| Server | Use Case | Setup Time |
|--------|----------|------------|
| Brave Search | Web search, research | 5 min |
| Brave Deep Research | Multi-page content extraction | 10 min |
| Puppeteer MCP | Web scraping, screenshots | 15 min |

---

## By Installation Method

### npm (Easiest)
```bash
npm install -g <package>
```
- Knowledge Graph Memory
- Sequential Thinking
- GitHub MCP
- Git MCP
- Filesystem MCP
- Fetch MCP

### uvx (Python Ecosystem)
```bash
uvx <package>
```
- DuckDB MCP
- PostgreSQL MCP (some versions)

### Docker
```bash
docker run <image>
```
- Kubernetes MCP
- Some community servers

### Hosted (No Installation)
- Notion MCP
- BigQuery MCP (Google Cloud managed)
- Brave Search MCP (API-based)

### Custom Setup
- Claude Context (Milvus/Zilliz)
- Qdrant Memory (Qdrant instance)
- Jupyter MCP (JupyterLab)
- Neo4j MCP (Neo4j instance)
- Obsidian MCP (Obsidian + REST API plugin)

---

## By Cost

### Free Forever
- Knowledge Graph Memory (local file-based)
- Sequential Thinking (local)
- DuckDB MCP (local)
- Git MCP (local)
- Filesystem MCP (local)
- Code Index (local)
- GitHub MCP (with free GitHub account)

### Free Tier Available
- Brave Search (2,000 queries/month)
- BigQuery MCP (existing GCP free tier)
- MotherDuck (DuckDB cloud)
- Notion MCP (with Notion free plan)

### Paid Only
- OpenAI API (for embeddings in Qdrant)
- Milvus Cloud (for Claude Context)
- Neo4j Aura (managed graph DB)
- AWS services (Lambda, S3)

---

## By Security Model

### Read-Only by Default
- PostgreSQL MCP
- DuckDB MCP (with flag)
- BigQuery MCP (configurable)

### Read/Write (Safe)
- Knowledge Graph Memory (local files)
- Obsidian MCP (vault access)
- Git MCP (local repo)

### Write Requires Caution
- BigQuery MCP (write mode) → USE SafeBigQueryWriter
- Neo4j MCP (graph mutations)
- GitHub MCP (PR/issue creation)

### External API Calls
- Brave Search (read-only, rate-limited)
- OpenAI API (rate-limited, cost-controlled)
- Notion API (workspace permissions)

---

## Compatibility Matrix

### Works with Claude Code
✅ All MCP servers (stdio or HTTP transport)

### Works with Claude Desktop
✅ All MCP servers

### Works with Cursor
✅ Most MCP servers (check specific docs)

### Works with Custom Agents
✅ All (MCP is protocol-agnostic)

---

## Quick Decision Tree

```
Need to query BigQuery?
└─ Yes → BigQuery MCP (⭐⭐⭐⭐⭐)
└─ No, local analytics → DuckDB MCP (⭐⭐⭐⭐)

Need persistent memory across sessions?
└─ Yes, with semantic search → Qdrant Memory (⭐⭐⭐⭐)
└─ Yes, simple relationships → Knowledge Graph Memory (⭐⭐⭐⭐⭐)
└─ No → Skip memory servers

Need code analysis?
└─ Generate code → Claude Context (⭐⭐⭐⭐⭐)
└─ Search patterns → Code Index (⭐⭐⭐⭐)
└─ Manage repo → GitHub MCP (⭐⭐⭐⭐⭐)
└─ Run tests → Pytest MCP (⭐⭐⭐)

Need external research?
└─ Deep multi-page → Brave Deep Research (⭐⭐⭐)
└─ Simple search → Brave Search (⭐⭐⭐)
└─ Web scraping → Puppeteer MCP (⭐⭐)

Need complex reasoning?
└─ Always → Sequential Thinking (⭐⭐⭐⭐⭐)
```

---

## Integration Timeline

### Day 1 (30 minutes)
- Knowledge Graph Memory (5 min)
- Sequential Thinking (5 min)
- GitHub MCP (5 min)
- Test basic workflows (15 min)

### Week 1 (2 hours)
- BigQuery MCP (1 hour setup + testing)
- DuckDB MCP (15 min)
- Code Index (15 min)
- Integration testing (30 min)

### Week 2 (4 hours)
- Claude Context (2 hours setup)
- Jupyter MCP (1 hour)
- Obsidian MCP (1 hour)

### Month 1 (8 hours)
- Qdrant Memory (3 hours)
- Brave Search + Deep Research (1 hour)
- MCP Code Checker + Pytest (1 hour)
- Documentation and team training (3 hours)

---

## Maintenance Requirements

### Zero Maintenance
- Knowledge Graph Memory (file-based)
- Sequential Thinking (stateless)
- DuckDB MCP (local)
- Git MCP (local)

### Low Maintenance
- GitHub MCP (API token rotation)
- Brave Search (API key management)
- BigQuery MCP (OAuth refresh)
- Code Index (periodic reindexing)

### Medium Maintenance
- Qdrant Memory (vector DB updates)
- Jupyter MCP (kernel management)
- Obsidian MCP (plugin updates)
- Claude Context (index updates)

### High Maintenance
- Neo4j MCP (database management)
- Kubernetes MCP (cluster ops)
- AWS Lambda MCP (serverless ops)

---

## Common Pitfalls

### BigQuery MCP
⚠️ **Issue**: Accidental data writes
✅ **Solution**: Use read-only mode, enforce SafeBigQueryWriter

### Qdrant Memory
⚠️ **Issue**: High embedding costs
✅ **Solution**: Cache embeddings, batch operations

### Claude Context
⚠️ **Issue**: Large codebase indexing time
✅ **Solution**: Index incrementally, exclude node_modules/

### Jupyter MCP
⚠️ **Issue**: Kernel state pollution
✅ **Solution**: Regular kernel restarts, clear outputs

### GitHub MCP
⚠️ **Issue**: API rate limits
✅ **Solution**: Use GraphQL, cache results, respect limits

---

## Key Metrics

### MCP Ecosystem Size
- 8,250+ total MCP servers (Feb 2026)
- 110 official integrations
- 90 reference implementations
- 20 Anthropic-maintained servers

### truth_forge Recommendations
- 5 Tier 1 (Critical) servers
- 5 Tier 2 (High Priority) servers
- 5 Tier 3 (Medium Priority) servers
- 7 Tier 4 (Low Priority) servers

### Estimated Setup Time
- Tier 1 servers: 1-2 hours total
- Tier 1 + Tier 2: 4-6 hours total
- Full recommended setup: 8-12 hours

### Estimated Monthly Cost
- Tier 1 only: $0
- Tier 1 + Tier 2: $0-$35
- Full setup with premium features: $35-$100

---

**Last Updated**: 2026-02-06
**Full Analysis**: `MCP_SERVER_LANDSCAPE_2026.md`
**Quickstart Guide**: `MCP_INTEGRATION_QUICKSTART.md`

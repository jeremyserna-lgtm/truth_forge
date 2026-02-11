# MCP Integration Quickstart

**Quick reference for integrating MCP servers into truth_forge**

---

## Top 5 Recommended MCP Servers

### 1. BigQuery MCP Server (CRITICAL)
```bash
# Install
npm install @google-cloud/bigquery-mcp

# Configure
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Use
"Show me all L8 entities from the last week"
```

**Why**: Native truth_forge data warehouse access via natural language.

---

### 2. Knowledge Graph Memory (CRITICAL)
```bash
# Install
npm install @modelcontextprotocol/server-memory

# Configure
claude mcp add memory

# Use
Store and query entity relationships across sessions.
```

**Why**: Persistent context for entity analysis, perfect for L2-L8 hierarchy.

---

### 3. Sequential Thinking (CRITICAL)
```bash
# Install
npm install @modelcontextprotocol/server-sequential-thinking

# Configure
claude mcp add sequential-thinking

# Use
Complex multi-step reasoning for entity enrichment workflows.
```

**Why**: Aligns with THE PATTERN (HOLD:AGENT:HOLD), complex analysis.

---

### 4. Claude Context / Code Search (HIGH)
```bash
# Install
git clone https://github.com/zilliztech/claude-context
cd claude-context
# Follow setup instructions

# Use
Index truth_forge codebase for context-aware code generation.
```

**Why**: Make entire codebase available as context for Claude Code.

---

### 5. GitHub MCP Server (HIGH)
```bash
# Install
npm install @github/github-mcp-server

# Configure
export GITHUB_TOKEN="your_token_here"

# Use
"Find all DLQ pattern implementations"
"Generate COMPLIANCE_REPORT.md"
```

**Why**: Automate repository analysis, code search, PR management.

---

## Quick Setup: Knowledge Graph Memory

**Time**: 5 minutes

```bash
# 1. Install
npm install -g @modelcontextprotocol/server-memory

# 2. Configure Claude Code
# Add to ~/.config/claude-code/config.json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}

# 3. Test
# In Claude Code:
# "Store this entity: {entity_id: 'e1', level: 8, text: 'test conversation'}"
# "Recall entities with level 8"
```

---

## Quick Setup: BigQuery MCP

**Time**: 10 minutes

```bash
# 1. Authenticate with GCP (if not already)
gcloud auth application-default login

# 2. Enable BigQuery API
gcloud services enable bigquery.googleapis.com

# 3. Install MCP server
# Use Google Cloud's official remote MCP (preview)
# OR install community version:
npm install -g mcp-server-bigquery

# 4. Configure
# Add to ~/.config/claude-code/config.json
{
  "mcpServers": {
    "bigquery": {
      "command": "mcp-server-bigquery",
      "args": ["--project", "your-project-id"]
    }
  }
}

# 5. Test
# In Claude Code:
# "Show me the schema of spine.entity_unified"
# "Count entities by level"
```

---

## Security Checklist

Before deploying any MCP server with write access:

- [ ] Read-only mode enabled by default
- [ ] API keys stored in `config/local/` (gitignored)
- [ ] SafeBigQueryWriter enforcement for BigQuery writes
- [ ] Backup strategy for any DELETE operations
- [ ] Structured logging configured
- [ ] Parent chain validation enabled

---

## Integration Patterns

### Pattern 1: Query → Store → Recall
```
1. Query BigQuery for entities (BigQuery MCP)
2. Store relationships (Knowledge Graph Memory)
3. Recall context in future sessions (Memory MCP)
```

### Pattern 2: Reason → Code → Test
```
1. Design solution (Sequential Thinking MCP)
2. Generate code (Claude Context MCP)
3. Run tests (Pytest MCP)
```

### Pattern 3: Search → Analyze → Document
```
1. Search external sources (Brave Search MCP)
2. Analyze code patterns (Code Index MCP)
3. Generate docs (Obsidian MCP)
```

---

## Cost Estimate

| Server | Monthly Cost |
|--------|--------------|
| BigQuery MCP | $0 (existing GCP) |
| Knowledge Graph Memory | $0 (local) |
| Sequential Thinking | $0 (local) |
| Claude Context | $0-$10 (if using Milvus Cloud) |
| GitHub MCP | $0 (with GitHub account) |
| Brave Search | $0-$5 (2,000 free queries) |
| OpenAI Embeddings (optional) | $5-$20 |

**Total**: $0-$35/month for comprehensive MCP setup.

---

## Next Steps

1. **Week 1**: Install Knowledge Graph Memory (5 min)
2. **Week 2**: Set up BigQuery MCP (10 min)
3. **Week 3**: Add Sequential Thinking (5 min)
4. **Week 4**: Integrate GitHub MCP (10 min)
5. **Month 2**: Explore Claude Context + Jupyter MCP

---

## Resources

- Full analysis: `/Users/jeremyserna/truth_forge/docs/research/MCP_SERVER_LANDSCAPE_2026.md`
- Official registry: https://registry.modelcontextprotocol.io/
- MCP documentation: https://modelcontextprotocol.io/
- truth_forge MCP docs: `docs/operations/tools/mcp_query_entities.md`

---

**Last Updated**: 2026-02-06

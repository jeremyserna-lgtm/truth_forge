# MCP Servers Quick Reference for Truth Engine

**Quick lookup guide for MCP servers and tools**

---

## 🎯 Top Priority Recommendations

### 0. AI Assistant Research Tools (For Better AI Performance)

**Priority: IMMEDIATE** - These help AI assistants do better work

1. **Brave Search MCP Server**
   - Web search for AI assistants
   - Current information access
   - Research capabilities
   - **Source:** `glama.ai/mcp/servers`

2. **Web Scraping MCP Server (Thordata)**
   - Extract data from websites
   - Bypass anti-bot systems
   - Structured data output
   - **Source:** `glama.ai/mcp/servers`

3. **Sequential Thinking** ✅
   - **Already installed!** (`sequential-thinking-proxy`)
   - Use for complex analysis
   - Should be used for research tasks

4. **Academic Research MCPs**
   - BioMCP for biomedical research
   - Kaggle MCP for datasets
   - **Source:** `glama.ai/mcp/servers`

### 1. Google Cloud Platform Integration
- **Need:** BigQuery, Cloud Run, Cloud Storage operations
- **Action:** Check `github.com/modelcontextprotocol/servers` for GCP servers
- **Alternative:** Build custom MCP server exposing your `bigquery_archive_service`

### 2. Database Query Servers
- **Filesystem MCP Server:** Official implementation for file operations
- **SQL MCP Server:** Generic SQL queries (DuckDB, BigQuery)
- **Action:** Review official MCP servers repository

### 3. Version Control
- **GitHub MCP Server:** Official - full GitHub integration
- **Git MCP Server:** Local Git operations
- **Action:** Install from official repository

---

## 📚 Key Resources

### Official Sources
- **GitHub:** `github.com/modelcontextprotocol/servers` - Official reference implementations
- **Documentation:** `modelcontextprotocol.io` - Protocol specification

### Community Directories
- **Open MCP Directory:** `openmcpdirectory.com` - Comprehensive hub
- **MCPServe:** `mcpserve.com` - Curated list
- **BoostDevSpeed:** `boostdevspeed.com/mcp` - Browse and compare

### Development Tools
- **MCPTools:** `creati.ai/mcp/mcptools` - CLI for managing servers
- **MCP Inspector:** Debug and test servers
- **Stainless:** `stainless.com/products/mcp` - Generate from OpenAPI

---

## 🔒 Security

- **MCPSafetyScanner:** Audit servers before use
- **Research:** `arxiv.org/abs/2504.03767` - Security audit paper
- **Best Practice:** Review all server code, use granular permissions

---

## 🛠️ Your Existing Infrastructure

### Current MCP Servers
- ✅ `truth-engine-mcp` - Your custom server (excellent foundation)
- ✅ `sequential-thinking-proxy` - Logging proxy

### Services to Expose as MCP
- `bigquery_archive_service` → BigQuery MCP server
- `duckdb_flush_service` → DuckDB MCP server
- `schema_service` → Schema query MCP server
- `governance` operations → Governance MCP server

---

## 📋 Implementation Checklist

- [ ] Review official MCP servers repository
- [ ] Explore community directories
- [ ] Security audit with MCPSafetyScanner
- [ ] Install high-priority servers (GCP, Database, Filesystem)
- [ ] Test integration with Claude Desktop/Cursor
- [ ] Extend `truth-engine-mcp` with new tools
- [ ] Document integration process

---

**Full Research:** See `MCP_SERVERS_RESEARCH.md` for complete details.

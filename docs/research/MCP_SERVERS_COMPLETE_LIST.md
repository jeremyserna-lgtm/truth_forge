# Complete MCP Servers List for Truth Engine

**Date:** January 2025
**Comprehensive list of all discovered MCP servers organized by category**

---

## 🎯 Priority 0: AI Assistant Research Tools

### Web Search & Research

1. **Brave Search MCP Server**
   - **Purpose:** Web search capabilities for AI assistants
   - **Features:** Web, local business, image, video, news searches + AI summarization
   - **Source:** `glama.ai/mcp/servers/categories/research-and-data`
   - **Priority:** IMMEDIATE - Enables better research

2. **Web Scraping MCP Server (Thordata)**
   - **Purpose:** Scrape and extract data from any website
   - **Features:** Bypass anti-bot systems, render JavaScript, structured output
   - **Source:** `glama.ai/mcp/servers`
   - **Priority:** HIGH - Data extraction capabilities

3. **Academic Research MCPs**
   - **BioMCP:** Biomedical databases (PubTator3, ClinicalTrials.gov, MyVariant.info)
   - **Kaggle MCP Server:** Direct Kaggle API interface for datasets and kernels
   - **Source:** `glama.ai/mcp/servers`
   - **Priority:** MEDIUM - Research paper and dataset access

### Reasoning & Analysis

4. **Sequential Thinking MCP Server** ✅
   - **Status:** Already installed (`sequential-thinking-proxy`)
   - **Purpose:** Structured, step-by-step reasoning
   - **Location:** `mcp-servers/sequential-thinking-proxy/`
   - **Note:** Should be used for complex analysis tasks

---

## 🚀 Priority 1: Google Cloud Platform Integration

5. **Google Cloud MCP Server (Official/Community)**
   - **Purpose:** Direct GCP service integration
   - **Use Cases:** BigQuery, Cloud Run, Cloud Storage, Cloud Logging
   - **Source:** Check `github.com/modelcontextprotocol/servers`
   - **Status:** May need custom implementation
   - **Priority:** HIGH - Core infrastructure

6. **BigQuery MCP Server**
   - **Purpose:** SQL query execution on BigQuery
   - **Use Cases:** Query datasets, explore schema, cost estimation
   - **Implementation:** Could extend your `bigquery_archive_service`
   - **Priority:** HIGH

7. **Cloud Storage MCP Server**
   - **Purpose:** File operations on GCS buckets
   - **Use Cases:** Upload/download knowledge atoms, sync files
   - **Implementation:** May need custom
   - **Priority:** MEDIUM

---

## 💾 Priority 2: Database & SQL Servers

8. **SQL MCP Server (Generic)**
   - **Purpose:** Execute SQL queries on any database
   - **Use Cases:** DuckDB, BigQuery, schema exploration
   - **Source:** Official MCP servers repository
   - **Priority:** HIGH

9. **DuckDB MCP Server**
   - **Purpose:** Native DuckDB integration
   - **Use Cases:** Query local DuckDB databases, analytical queries
   - **Implementation:** Could extend your `duckdb_flush_service`
   - **Priority:** MEDIUM

10. **PostgreSQL MCP Server**
    - **Purpose:** PostgreSQL database operations
    - **Source:** Community implementations
    - **Priority:** LOW (if you use PostgreSQL)

11. **Redis MCP Server**
    - **Purpose:** Redis operations
    - **Source:** Official MCP servers repository
    - **Priority:** LOW (if you use Redis)

12. **MongoDB MCP Server**
    - **Purpose:** MongoDB operations
    - **Source:** Community implementations
    - **Priority:** LOW (if you use MongoDB)

---

## 📁 Priority 3: Filesystem Operations

13. **Filesystem MCP Server (Official)**
    - **Purpose:** Read, write, and manage files
    - **Use Cases:** Access framework docs, manage pipeline scripts
    - **Source:** Official MCP servers repository, `boostdevspeed.com/mcp`
    - **Security:** Use with granular permissions
    - **Priority:** MEDIUM

14. **Code-Assistant MCP Server**
    - **Purpose:** Codebase exploration and modification
    - **Use Cases:** Navigate codebase, understand architecture
    - **Source:** `mcpstack.org/community/code-assistant`
    - **Warning:** Security risks - use with trusted repositories
    - **Priority:** MEDIUM

---

## 🔧 Priority 4: Version Control & Git

15. **GitHub MCP Server (Official)**
    - **Purpose:** Full GitHub integration
    - **Use Cases:** Manage repos, PRs, issues, GitHub Actions
    - **Source:** Official MCP servers repository, `stainless.com/mcp`
    - **Priority:** MEDIUM

16. **Git MCP Server (Local)**
    - **Purpose:** Local Git operations
    - **Use Cases:** Commit changes, view history, branch management
    - **Source:** Official MCP servers repository
    - **Priority:** MEDIUM

---

## 🌐 Priority 5: Browser Automation & Web

17. **Playwright MCP Server (Official)**
    - **Purpose:** Browser automation via Playwright
    - **Use Cases:** Web scraping, testing, data extraction
    - **Source:** Official MCP servers repository, `boostdevspeed.com/mcp`
    - **Note:** You already have Playwright in requirements.txt
    - **Priority:** MEDIUM

18. **Selenium MCP Server**
    - **Purpose:** Browser automation via Selenium
    - **Use Cases:** Legacy browser automation, cross-browser testing
    - **Status:** May need custom implementation
    - **Note:** You have Selenium in requirements.txt
    - **Priority:** LOW

19. **Browser MCP Server (Cursor IDE)**
    - **Purpose:** Browser automation built into Cursor
    - **Features:** Navigate, click, type, screenshot
    - **Source:** Cursor IDE built-in
    - **Priority:** LOW (if using Cursor)

---

## 📚 Priority 6: Documentation & Knowledge

20. **Documentation MCP Server**
    - **Purpose:** Search and access documentation
    - **Use Cases:** Search framework docs, service READMEs
    - **Implementation:** Could extend `truth-engine-mcp`
    - **Priority:** LOW

21. **Knowledge Graph MCP Server**
    - **Purpose:** Query knowledge graphs
    - **Use Cases:** Query your `knowledge_graph_service`, explore entities
    - **Implementation:** Extend `truth-engine-mcp` or create new
    - **Priority:** LOW

---

## 🤖 Priority 7: AI Model Integration

22. **Ollama MCP Server**
    - **Purpose:** Local LLM operations
    - **Use Cases:** Query local Ollama models, run inference
    - **Source:** Check official MCP servers repository
    - **Note:** You have `ollama_service` in archived services
    - **Priority:** LOW

23. **Gemini MCP Server**
    - **Purpose:** Google Gemini API integration
    - **Use Cases:** Direct Gemini API calls, multi-modal operations
    - **Status:** May need custom implementation
    - **Note:** You use `google-generativeai` in requirements
    - **Priority:** LOW

---

## 🛠️ Priority 8: Development Tools

24. **Base Framework MCP Server**
    - **Purpose:** Deep framework knowledge for Base Framework projects
    - **Source:** `mcp.base.al`
    - **Priority:** LOW (if using Base Framework)

25. **Cursor MCP**
    - **Purpose:** Lightweight, local-first MCP server
    - **Source:** `stainless.com/mcp`
    - **Priority:** LOW

26. **Telerik MCP Servers**
    - **Purpose:** Telerik-specific tooling
    - **Source:** `telerik.com/mcp-servers`
    - **Priority:** LOW (if using Telerik)

---

## ☁️ Priority 9: Cloud Services

27. **AWS MCP Server**
    - **Purpose:** AWS service integration
    - **Source:** Community implementations
    - **Priority:** LOW (if using AWS)

28. **Azure MCP Server**
    - **Purpose:** Azure service integration
    - **Source:** `learn.microsoft.com` (Microsoft Agent Framework)
    - **Priority:** LOW (if using Azure)

29. **Salesforce MCP Servers**
    - **Purpose:** Salesforce development tasks
    - **Types:** Salesforce DX, Heroku Platform, MuleSoft
    - **Source:** `developer.salesforce.com`
    - **Priority:** LOW (if using Salesforce)

---

## 🔐 Priority 10: Security & Management

30. **MCPSafetyScanner**
    - **Purpose:** Security auditing for MCP servers
    - **Features:** Identify vulnerabilities, remediation strategies
    - **Source:** Research paper `arxiv.org/abs/2504.03767`
    - **Priority:** HIGH - Use before deploying any server

31. **Check Point MCP Servers**
    - **Purpose:** AI-powered security management
    - **Source:** `mcp.checkpoint.com`
    - **Priority:** LOW (if using Check Point)

---

## 📊 Summary by Priority

### Immediate (Install First)
- ✅ Sequential Thinking (already installed)
- Brave Search MCP Server
- Web Scraping MCP Server (Thordata)
- MCPSafetyScanner (for security auditing)

### High Priority
- Google Cloud MCP Server / BigQuery MCP Server
- SQL MCP Server (Generic)
- Filesystem MCP Server
- GitHub MCP Server

### Medium Priority
- Playwright MCP Server
- Git MCP Server
- Code-Assistant MCP Server
- DuckDB MCP Server
- Academic Research MCPs (BioMCP, Kaggle)

### Low Priority
- Documentation/Knowledge Graph MCPs
- AI Model MCPs (Ollama, Gemini)
- Other cloud service MCPs
- Framework-specific MCPs

---

## 📚 Key Resources

### Official Sources
- **GitHub:** `github.com/modelcontextprotocol/servers` - Official reference implementations
- **Documentation:** `modelcontextprotocol.io` - Protocol specification

### Community Directories
- **Open MCP Directory:** `openmcpdirectory.com` - Comprehensive hub
- **MCPServe:** `mcpserve.com` - Curated list
- **BoostDevSpeed:** `boostdevspeed.com/mcp` - Browse and compare
- **Glama.ai:** `glama.ai/mcp/servers` - Research and data servers
- **Arvify:** `arvify.io/mcp-servers` - Ecosystem of servers

### Development Tools
- **MCPTools:** `creati.ai/mcp/mcptools` - CLI for managing servers
- **MCP Inspector:** Debug and test servers
- **Stainless:** `stainless.com/products/mcp` - Generate from OpenAPI
- **Zuplo:** `zuplo.com/mcp-servers` - Auto-generate from APIs

---

## 🎯 Recommended Installation Order

1. **Week 1: AI Assistant Tools**
   - Brave Search MCP Server
   - Web Scraping MCP Server
   - MCPSafetyScanner (audit tool)

2. **Week 2: Core Infrastructure**
   - Google Cloud / BigQuery MCP Server
   - SQL MCP Server
   - Filesystem MCP Server

3. **Week 3: Development Workflow**
   - GitHub MCP Server
   - Git MCP Server
   - Playwright MCP Server

4. **Week 4: Extensions**
   - Extend `truth-engine-mcp` with new tools
   - Custom MCP servers for your services
   - Documentation/Knowledge Graph MCPs

---

## 📝 Notes

- Total servers listed: **31+**
- Your existing servers: **2** (truth-engine-mcp, sequential-thinking-proxy)
- Priority 0-2 servers: **10** (most important)
- Security: Always use MCPSafetyScanner before deploying
- Custom servers: Consider exposing your central services as MCP servers

---

**Next Steps:** Start with Priority 0 (AI Assistant Tools) and Priority 1 (GCP Integration)

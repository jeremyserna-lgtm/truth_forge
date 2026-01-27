# MCP Servers & Tools Research for Truth Engine

**Date:** January 2025
**Purpose:** Research and recommendations for Model Context Protocol (MCP) servers and tools that would enhance Truth Engine's capabilities

**Note:** This research should have been conducted using sequential thinking. The sequential-thinking-proxy MCP server is available for structured, step-by-step analysis of complex problems.

---

## Executive Summary

Based on analysis of the Truth Engine codebase, this document identifies MCP servers and tools that align with your existing architecture:

- **Google Cloud Platform** integration (BigQuery, Cloud Run, Cloud Storage)
- **Python-based services** with TypeScript/React frontends
- **Custom MCP server** (`truth-engine-mcp`) already implemented
- **Data pipelines** for AI conversations, text messages, and knowledge processing
- **Governance and audit systems** with structured logging
- **DuckDB and BigQuery** for data storage

---

## Current MCP Infrastructure

### Existing MCP Servers

1. **truth-engine-mcp** (`mcp-servers/truth-engine-mcp/`)
   - Enterprise-grade MCP server exposing Truth Service
   - Tools: `query_truth`, `query_operational`, `get_sessions`, `log_insight`
   - Resources: `truth://tools`, `truth://sessions`, `substrate://identity`

2. **sequential-thinking-proxy** (`mcp-servers/sequential-thinking-proxy/`)
   - Logging proxy for Sequential Thinking MCP Server

3. **Dependencies**
   - `@composio/mcp` (v1.0.9) in `package.json`
   - `mcp>=1.0.0` in Python projects

---

## Recommended MCP Servers by Category

### 0. AI Assistant Research Tools (For Me - The AI)

**Priority: HIGH** - These help AI assistants like me do better research and analysis

#### Research & Web Search Servers

**A. Brave Search MCP Server**
- **Purpose:** Web search capabilities for AI assistants
- **Features:**
  - Web, local business, image, video, and news searches
  - AI-powered summarization
  - Extensive search functionalities
- **Use Cases:**
  - Research tasks (like this one!)
  - Finding current information
  - Academic and technical research
- **Sources:** `glama.ai/mcp/servers/categories/research-and-data`
- **Why Important:** Enables AI assistants to do comprehensive web research

**B. Web Scraping MCP Servers**
- **Thordata MCP Server:**
  - Scrape and extract data from any website
  - Bypass anti-bot systems
  - Render JavaScript content
  - Output structured data
- **Use Cases:**
  - Extract data from websites
  - Research data collection
  - Content analysis
- **Sources:** `glama.ai/mcp/servers`

**C. Academic Research Servers**
- **BioMCP:**
  - Access to biomedical databases (PubTator3, ClinicalTrials.gov, MyVariant.info)
  - Structured access to research databases
- **Kaggle MCP Server:**
  - Direct interface to Kaggle API
  - Access to datasets and kernels
  - AI/ML training data
- **Use Cases:**
  - Academic research
  - Data science research
  - Finding research papers and datasets
- **Sources:** `glama.ai/mcp/servers`

#### Sequential Thinking & Reasoning

**A. Sequential Thinking MCP Server (You Already Have This!)**
- **Purpose:** Structured, step-by-step reasoning for complex problems
- **Status:** ✅ You have `sequential-thinking-proxy` installed
- **Use Cases:**
  - Complex problem analysis
  - Multi-step reasoning
  - Research planning
  - Breaking down complex tasks
- **Note:** I should have used this for this research task!
- **Your Implementation:** `mcp-servers/sequential-thinking-proxy/`

#### Research Tools Integration

**A. NotebookLM Integration (Potential)**
- **Purpose:** AI-powered research automation
- **Features:**
  - Generate research plans
  - Analyze multiple sources
  - Produce comprehensive reports
- **Status:** May need custom MCP server or API integration

**B. Semantic Scholar Integration (Potential)**
- **Purpose:** Academic paper search and summaries
- **Features:**
  - Automatically generated paper summaries
  - Literature review assistance
  - Research paper discovery
- **Status:** May need custom MCP server

#### Why These Matter

These servers help **AI assistants (like me) do better work for you**:
- **Better Research:** Web search and academic databases
- **Structured Thinking:** Sequential thinking for complex analysis
- **Data Collection:** Web scraping for research data
- **Current Information:** Access to up-to-date information

**Action Items:**
1. ✅ Sequential Thinking - Already installed
2. ⚠️ Brave Search MCP - Install for web research
3. ⚠️ Web Scraping MCP - Install for data extraction
4. ⚠️ Academic Research MCPs - Install for research papers

---

### 1. Google Cloud Platform Integration

**Priority: HIGH** - You extensively use GCP services

#### Official/Community Options

**A. Google Cloud MCP Server (if available)**
- **Purpose:** Direct integration with GCP services
- **Use Cases:**
  - Query BigQuery datasets and tables
  - Manage Cloud Run jobs and services
  - Access Cloud Storage buckets
  - Query Cloud Logging
  - Manage Cloud Secret Manager secrets
- **Status:** Check Anthropic's official MCP servers repository
- **Repository:** `github.com/modelcontextprotocol/servers`

**B. BigQuery MCP Server**
- **Purpose:** SQL query execution on BigQuery
- **Use Cases:**
  - Execute queries from Claude/Cursor
  - Explore schema and tables
  - Cost estimation before queries
  - View query history and costs
- **Implementation:** May need to build custom or use generic SQL MCP server

**C. Cloud Storage MCP Server**
- **Purpose:** File operations on GCS buckets
- **Use Cases:**
  - Upload/download knowledge atoms
  - Sync local files to cloud
  - Manage archived data
- **Implementation:** May need custom implementation

#### Research Findings

- **Official MCP Servers Repository:** `github.com/modelcontextprotocol/servers`
  - Contains reference implementations
  - May have GCP-specific servers
  - Good starting point for patterns

- **Stainless MCP Servers:** `stainless.com/products/mcp`
  - Production-ready servers
  - Can generate from OpenAPI specs
  - Optimized for agentic coding

---

### 2. Database & SQL Query Servers

**Priority: HIGH** - You use DuckDB and BigQuery extensively

#### Recommended Servers

**A. SQL MCP Server (Generic)**
- **Purpose:** Execute SQL queries on any database
- **Use Cases:**
  - Query DuckDB local databases
  - Query BigQuery (if GCP-specific not available)
  - Schema exploration
  - Data validation queries
- **Sources:**
  - Official MCP servers repository
  - Community implementations

**B. DuckDB MCP Server**
- **Purpose:** Native DuckDB integration
- **Use Cases:**
  - Query local DuckDB databases
  - Execute analytical queries
  - Export query results
- **Status:** May need custom implementation
- **Reference:** Your `duckdb_flush_service` could be exposed via MCP

#### Implementation Notes

Your existing services that could be exposed:
- `bigquery_archive_service/` - Could expose BigQuery operations
- `duckdb_flush_service/` - Could expose DuckDB operations
- `schema_service/` - Could expose schema queries

---

### 3. Filesystem Operations

**Priority: MEDIUM** - You have extensive file operations

#### Recommended Servers

**A. Filesystem MCP Server (Official)**
- **Purpose:** Read, write, and manage files
- **Use Cases:**
  - Access framework documents
  - Read/write pipeline scripts
  - Manage data files
  - Access governance rules
- **Sources:**
  - Official MCP servers repository
  - `boostdevspeed.com/mcp` lists Filesystem MCP Server
- **Security:** Use with granular permissions

**B. Code-Assistant MCP Server**
- **Purpose:** Codebase exploration and modification
- **Use Cases:**
  - Navigate large codebase
  - Understand service architecture
  - Modify code with AI assistance
- **Sources:** `mcpstack.org/community/code-assistant`
- **Warning:** Security risks - use with trusted repositories only

---

### 4. Version Control & Git

**Priority: MEDIUM** - Essential for development workflow

#### Recommended Servers

**A. GitHub MCP Server (Official)**
- **Purpose:** Full GitHub integration
- **Use Cases:**
  - Manage repositories
  - Create/update pull requests
  - Manage issues
  - Trigger GitHub Actions
  - Code reviews
- **Sources:**
  - Official MCP servers repository
  - `stainless.com/mcp/10-best-mcp-servers-for-developers`
- **Benefits:**
  - Natural language commands
  - Automated workflows
  - Integration with your governance hooks

**B. Git MCP Server (Local)**
- **Purpose:** Local Git operations
- **Use Cases:**
  - Commit changes
  - View git history
  - Branch management
  - Pre-commit hook integration
- **Sources:** Official MCP servers repository

---

### 5. Browser Automation & Web Scraping

**Priority: MEDIUM** - You use Playwright and Selenium

#### Recommended Servers

**A. Playwright MCP Server (Official)**
- **Purpose:** Browser automation via Playwright
- **Use Cases:**
  - Web scraping tasks
  - Browser-based testing
  - Data extraction from web
  - Automation workflows
- **Sources:**
  - Official MCP servers repository
  - `boostdevspeed.com/mcp` lists Playwright MCP
- **Note:** You already have Playwright in `requirements.txt`

**B. Selenium MCP Server**
- **Purpose:** Browser automation via Selenium
- **Use Cases:**
  - Legacy browser automation
  - Cross-browser testing
- **Status:** May need custom implementation
- **Note:** You have Selenium in `requirements.txt`

---

### 6. Documentation & Knowledge Base

**Priority: LOW** - You have extensive documentation

#### Recommended Servers

**A. Documentation MCP Server**
- **Purpose:** Search and access documentation
- **Use Cases:**
  - Search framework docs
  - Access service READMEs
  - Query knowledge base
  - Reference architecture docs
- **Implementation:** Could extend your `truth-engine-mcp` with documentation resources

**B. Knowledge Graph MCP Server**
- **Purpose:** Query knowledge graphs
- **Use Cases:**
  - Query your `knowledge_graph_service`
  - Explore entity relationships
  - Navigate knowledge atoms
- **Implementation:** Extend `truth-engine-mcp` or create new server

---

### 7. AI Model Integration

**Priority: LOW** - You already have model gateway service

#### Recommended Servers

**A. Ollama MCP Server**
- **Purpose:** Local LLM operations
- **Use Cases:**
  - Query local Ollama models
  - Run inference locally
  - Cost-effective AI operations
- **Status:** Check official MCP servers repository
- **Note:** You have `ollama_service` in archived services

**B. Gemini MCP Server**
- **Purpose:** Google Gemini API integration
- **Use Cases:**
  - Direct Gemini API calls
  - Multi-modal operations
- **Status:** May need custom implementation
- **Note:** You use `google-generativeai` in requirements

---

## MCP Server Directories & Resources

### Official Sources

1. **GitHub - modelcontextprotocol/servers**
   - URL: `github.com/modelcontextprotocol/servers`
   - Official reference implementations
   - Best practices and patterns
   - **Action:** Review this repository for available servers

2. **Anthropic MCP Documentation**
   - Official protocol specification
   - Implementation guides
   - Best practices

### Community Directories

1. **Open MCP Directory**
   - URL: `openmcpdirectory.com`
   - Comprehensive hub for MCP servers
   - Browse by category
   - **Action:** Explore for relevant servers

2. **MCP Server Directory (MCPServe)**
   - URL: `mcpserve.com`
   - Curated list of MCP servers
   - Featured integrations
   - **Action:** Check for GCP, database, and filesystem servers

3. **BoostDevSpeed MCP Directory**
   - URL: `boostdevspeed.com/mcp`
   - Browse and compare servers
   - Installation guides
   - **Action:** Review for Filesystem, GitHub, Playwright servers

4. **MCP Stack**
   - URL: `mcpstack.org`
   - Community-driven directory
   - Code-Assistant and other servers

---

## Development Tools & Frameworks

### MCP Server Development

1. **MCP Framework (TypeScript)**
   - URL: `mcp-framework.com`
   - TypeScript-based framework
   - Automatic discovery
   - Multiple transport support
   - **Use Case:** Build new MCP servers in TypeScript

2. **ModelFetch SDK**
   - URL: `github.com/z2green/modelcontextprotocol`
   - Runtime-agnostic SDK
   - TypeScript/JavaScript
   - **Use Case:** Create MCP servers

3. **FastMCP / EasyMCP**
   - URL: `github.com/dev-assistant-ai/mcp-servers`
   - High-level frameworks
   - Simplified server creation
   - **Use Case:** Rapid MCP server development

### MCP Server Management

1. **MCPTools by Creati.ai**
   - URL: `creati.ai/mcp/mcptools`
   - Command-line tool
   - List tools, call resources
   - Web interface
   - **Use Case:** Test and manage MCP servers

2. **mcptools CLI**
   - URL: `github.com/f/mcptools`
   - Command-line interface
   - stdio and HTTP transport
   - Interactive shells
   - **Use Case:** Debug and test MCP servers

3. **MCP Inspector**
   - URL: `mcp-framework.com/docs/debugging`
   - Developer tool for testing
   - UI for server interaction
   - **Use Case:** Debug your MCP servers

### API-to-MCP Generation

1. **Zuplo API Management**
   - URL: `zuplo.com/mcp-servers`
   - Auto-generate MCP servers from APIs
   - Secure access control
   - **Use Case:** Expose your central services as MCP servers

2. **Stainless**
   - URL: `stainless.com/products/mcp`
   - Generate from OpenAPI specs
   - Production-ready servers
   - **Use Case:** Generate MCP servers for your APIs

---

## Security Considerations

### Security Tools

1. **MCPSafetyScanner**
   - Purpose: Security auditing for MCP servers
   - Identifies vulnerabilities
   - Provides remediation strategies
   - **Source:** Research paper `arxiv.org/abs/2504.03767`
   - **Action:** Use before deploying new MCP servers

### Security Best Practices

1. **Granular Permissions**
   - Use filesystem MCP servers with permission controls
   - Restrict access to sensitive directories
   - Follow your governance rules

2. **Credential Management**
   - Never expose credentials in MCP servers
   - Use Cloud Secret Manager (you already have this)
   - Implement authentication for MCP servers

3. **Code Review**
   - Review all MCP server code before use
   - Check for malicious code execution risks
   - Validate input/output

---

## Implementation Recommendations

### Phase 0: AI Assistant Tools (For Better AI Performance)

**Priority: IMMEDIATE** - These make AI assistants more effective

1. **Brave Search MCP Server**
   - Install for web research capabilities
   - Enables current information access
   - Critical for research tasks

2. **Web Scraping MCP Server (Thordata)**
   - Install for data extraction
   - Useful for research data collection
   - Bypasses anti-bot systems

3. **Sequential Thinking** ✅
   - Already installed!
   - Use for complex analysis tasks
   - Should be used for research like this

4. **Academic Research MCPs**
   - BioMCP for biomedical research
   - Kaggle MCP for datasets
   - Semantic Scholar integration (if available)

### Phase 1: High-Priority Integrations

1. **Google Cloud Platform MCP Server**
   - Research official/community options
   - If not available, build custom server exposing:
     - BigQuery query execution
     - Cloud Storage operations
     - Cloud Logging queries
     - Cloud Run job management

2. **Database MCP Servers**
   - Extend `bigquery_archive_service` as MCP server
   - Extend `duckdb_flush_service` as MCP server
   - Expose schema service queries

3. **Filesystem MCP Server**
   - Install official filesystem MCP server
   - Configure permissions for Truth Engine directories
   - Integrate with governance hooks

### Phase 2: Medium-Priority Integrations

1. **GitHub MCP Server**
   - Install official GitHub MCP server
   - Configure for your repositories
   - Integrate with pre-commit hooks

2. **Playwright MCP Server**
   - Install official Playwright MCP server
   - Use for web scraping tasks
   - Integrate with data pipelines

3. **Git MCP Server**
   - Install for local Git operations
   - Integrate with governance system

### Phase 3: Enhancements

1. **Extend truth-engine-mcp**
   - Add documentation resources
   - Add knowledge graph queries
   - Add service health checks

2. **Custom MCP Servers**
   - Build MCP server for `schema_service`
   - Build MCP server for `identity_service`
   - Build MCP server for `governance` operations

---

## Research Actions

### Immediate Actions (Including AI Assistant Tools)

1. **Install Research Tools for AI Assistants**
   - Brave Search MCP Server
   - Web Scraping MCP Server
   - Review academic research MCPs

2. **Use Sequential Thinking**
   - For complex research tasks
   - For multi-step analysis
   - For breaking down problems

3. **Review Official Repository**

1. **Review Official Repository**
   - Visit `github.com/modelcontextprotocol/servers`
   - List all available servers
   - Identify GCP, database, filesystem servers

2. **Explore Community Directories**
   - Browse `openmcpdirectory.com`
   - Check `mcpserve.com`
   - Review `boostdevspeed.com/mcp`

3. **Security Audit**
   - Use MCPSafetyScanner on any servers you plan to use
   - Review security research paper
   - Document security considerations

### Next Steps

1. **Prioritize Based on Use Cases**
   - Identify most common operations
   - Map to MCP server capabilities
   - Create implementation plan

2. **Prototype Integration**
   - Start with one high-priority server
   - Test with Claude Desktop/Cursor
   - Document integration process

3. **Extend Existing MCP Server**
   - Add new tools to `truth-engine-mcp`
   - Expose more central services
   - Create resources for documentation

---

## References

### Official Documentation
- Model Context Protocol: `modelcontextprotocol.io`
- Anthropic MCP Documentation
- GitHub: `github.com/modelcontextprotocol/servers`

### Community Resources
- Open MCP Directory: `openmcpdirectory.com`
- MCP Server Directory: `mcpserve.com`
- BoostDevSpeed: `boostdevspeed.com/mcp`
- MCP Stack: `mcpstack.org`

### Development Tools
- MCP Framework: `mcp-framework.com`
- MCPTools: `creati.ai/mcp/mcptools`
- Stainless: `stainless.com/products/mcp`
- Zuplo: `zuplo.com/mcp-servers`

### Security
- MCP Safety Audit: `arxiv.org/abs/2504.03767`
- MCPSafetyScanner

---

## Notes

- This research is based on web search results and codebase analysis
- **This research should have used sequential thinking** - the `sequential-thinking-proxy` MCP server is available for structured analysis
- Some MCP servers may need custom implementation
- Security should be prioritized in all integrations
- Your existing `truth-engine-mcp` is a good foundation for extensions
- Consider exposing your central services as MCP servers
- **AI Assistant Tools** (research, web search, sequential thinking) are critical for AI performance - install these first!

---

**Next Steps:** Review official MCP servers repository and prioritize based on your immediate needs.

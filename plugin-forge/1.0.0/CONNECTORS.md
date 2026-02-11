# Connectors

## How tool references work

Plugin Forge operates primarily on local plugin files and the plugin registry. It doesn't require external MCP servers by default, but it can introspect and configure MCP servers for the plugins it creates.

## Connectors for this plugin

| Category | Tool | Status |
|----------|------|--------|
| Plugin registry | Local filesystem | Built-in |
| MCP registry | `search_mcp_registry` | Available via Cowork |
| Knowledge sources | `~~knowledge-base` | Not yet configured |
| Chat history | `~~chat` | Not yet configured |

## Note

Plugin Forge reads from your installed plugins directory and the plugin registry to understand your ecosystem. The plugins it *creates* may need their own MCP connectors — Plugin Forge will configure those during the creation process.

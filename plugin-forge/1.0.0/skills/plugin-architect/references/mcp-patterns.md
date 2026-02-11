# MCP Configuration Patterns

How to configure MCP servers for plugins and which categories map to which tools.

## Category-to-Tool Mapping

| Category | Tools | MCP Keywords |
|----------|-------|-------------|
| `~~chat` | Slack, MS Teams, Discord | slack, teams, discord, chat |
| `~~email` | Gmail, Outlook, MS365 | gmail, outlook, email |
| `~~crm` | Salesforce, HubSpot, Pipedrive, Close | salesforce, hubspot, crm |
| `~~project-management` | Jira, Asana, Linear, Monday | jira, asana, linear, project |
| `~~knowledge-base` | Notion, Confluence, Guru | notion, confluence, wiki |
| `~~data-warehouse` | BigQuery, Snowflake, Databricks, Redshift | bigquery, snowflake, sql |
| `~~product-analytics` | Amplitude, Mixpanel, Heap | amplitude, mixpanel, analytics |
| `~~support-platform` | Zendesk, Intercom, Freshdesk | zendesk, intercom, support |
| `~~ci-cd` | GitHub Actions, CircleCI, Jenkins | github, ci, deployment |
| `~~monitoring` | Datadog, PagerDuty, Grafana | datadog, monitoring, alerts |
| `~~file-storage` | Google Drive, Dropbox, Box | drive, dropbox, files |
| `~~calendar` | Google Calendar, Outlook Calendar | calendar, scheduling |

## Configuration Examples

### HTTP endpoint (most common)
```json
{
  "slack": {
    "type": "http",
    "url": "https://mcp.slack.com/mcp"
  }
}
```

### With authentication
```json
{
  "github": {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
      "Authorization": "Bearer ${GITHUB_TOKEN}"
    }
  }
}
```

### Server-Sent Events
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

## Discovering MCP Servers

When creating a plugin that needs tool connections:

1. Use `search_mcp_registry(keywords=[...])` with category keywords
2. If a connector is found and not connected: `suggest_connectors(directoryUuids=[...])`
3. User completes OAuth or API key setup
4. Add the server to the plugin's `.mcp.json`

## Placeholder Convention

Use `~~` prefix for unconfigured tools in skill/command files:
```markdown
Post the summary to ~~chat (e.g., Slack, Teams)
```

And in CONNECTORS.md:
```markdown
| Chat | `~~chat` | Not yet configured |
```

This signals to the plugin-customizer skill that these need to be replaced.

# Command Patterns

Best practices for writing plugin commands.

## Command Naming

Commands should be **verbs** that describe the action:

| Good | Bad | Why |
|------|-----|-----|
| `/analyze` | `/data-analysis` | Verbs are actions, nouns are things |
| `/forge` | `/plugin-creation` | Users want to DO something |
| `/audit` | `/plugin-audit-report` | Short, memorable, typeable |
| `/next` | `/recommend-next-plugin` | One word when possible |

## Command Complexity Levels

### Simple Command
Single action, immediate result.
```
/analyze How many users signed up last week?
```
Workflow: Understand → Query → Present

### Multi-Step Command
Guided process with intermediate outputs.
```
/forge A plugin for monitoring competitor pricing
```
Workflow: Understand → Design → Approve → Build → Package

### Meta Command
Operates on the plugin system itself.
```
/audit
/evolve 3
```
Workflow: Read system state → Analyze → Recommend → Act

## Workflow Structure

Every command workflow should follow this pattern:

1. **Parse** — Understand what the user asked for
2. **Gather** — Collect data, read files, query sources
3. **Process** — Analyze, transform, synthesize
4. **Validate** — Check results make sense
5. **Present** — Show results in the right format
6. **Record** — Update state for the recursive loop (if applicable)

## Referencing Skills

Commands should reference skills by name:
```markdown
### 2. Analyze the Data
Use the `data-exploration` skill to profile the dataset...
```

This tells Claude which skill to consult for that step.

## Referencing Connectors

Always include the CONNECTORS.md link:
```markdown
> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
```

## Error Handling

Commands should gracefully handle:
- Missing MCP connections → Suggest alternatives or manual input
- Empty results → Explain why and suggest different approach
- User cancellation → Save progress for next time

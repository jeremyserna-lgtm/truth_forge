# CLI Reference

**The Commands** | Every organism operation accessible through a unified command-line interface.

**Authority**: [framework/standards/API_DESIGN.md](../../../framework/standards/API_DESIGN.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Command Category | Commands | Purpose |
|------------------|----------|---------|
| Status | `status`, `vitals`, `layers` | Monitor organism state |
| Consciousness | `journal`, `observe`, `speak` | Interact with awareness |
| Soul | `thoughts`, `feelings`, `concerns` | Manage inner state |
| Will | `purpose`, `mission`, `goals` | Direct intention |
| Evolution | `growth`, `molt`, `learn` | Track development |
| Cognition | `inhale`, `exhale`, `memory`, `reflect` | Process information |
| Daemon | `daemon start/stop/status` | Control background process |
| Truth | `truth stats/sessions/search` | Access conversation history |
| Intake | `backlog`, `changelog`, `checkin` | Manage work items |
| Lifecycle | `bootstrap`, `shutdown`, `spawn` | Control organism lifecycle |

| Global Option | Description |
|---------------|-------------|
| `--verbose`, `-v` | Verbose output |
| `--json` | JSON output format |
| `--quiet`, `-q` | Quiet mode |
| `--help` | Show help |

---

## WHY (Theory)

### The Interface Imperative

The organism requires a consistent, discoverable interface for human operators. A CLI provides this through composable commands, predictable behavior, and scriptable automation. Every internal capability becomes externally accessible.

### Design Principles

1. **Discoverability** - Commands reveal themselves through help and consistent naming
2. **Composability** - Commands can be chained and scripted
3. **Predictability** - Same input always produces same behavior
4. **Observability** - Every operation produces visible feedback
5. **Safety** - Destructive operations require confirmation

### The Biological Metaphor

Commands map to organism functions:
- **Status commands** = Taking vital signs
- **Soul commands** = Introspection
- **Cognition commands** = Breathing and thinking
- **Lifecycle commands** = Birth, death, reproduction

---

## WHAT (Specification)

### Main Entry Point

```bash
# Primary CLI
python organism_cli.py [command] [options]

# Alternative entry points
python -m Primitive [command]
python daemon/cli.py [command]
```

### Status Commands

#### `status`

Show organism status summary.

```bash
python organism_cli.py status
```

**Output:**
```
Organism Status
===============
Health: 0.85
Energy: 0.72
Mood: content
Awareness: 0.80
Heartbeat: #12453
Survival Mode: normal
```

#### `vitals`

Show detailed vital signs.

```bash
python organism_cli.py vitals
```

**Output:**
```
Vital Signs
===========
Health: 0.85
Energy: 0.72
Temperature: 0.68
Pulse Rate: 0.95
Last Heartbeat: 2026-01-19T14:30:00Z
Survival Mode: normal
```

#### `layers`

Show status of all biological layers.

```bash
python organism_cli.py layers
```

**Output:**
```
Biological Layers
=================
1. VITALS       [ACTIVE]  health=0.85 energy=0.72
2. CONSCIOUSNESS[ACTIVE]  awareness=0.80
3. SOUL         [ACTIVE]  mood=content
4. BOND         [ACTIVE]  partnerships=1
5. WILL         [ACTIVE]  drive=0.75
6. SPIRIT       [ACTIVE]  gratitudes=15
7. ANIMA        [ACTIVE]  dreams=42
8. EVOLUTION    [ACTIVE]  generation=1
```

### Consciousness Commands

#### `journal`

Interact with the journal.

```bash
# Show recent entries
python organism_cli.py journal --recent 10

# Show entries by type
python organism_cli.py journal --type decision

# Search journal
python organism_cli.py journal --search "documentation"

# Add entry
python organism_cli.py journal add --type observation "Noticed pattern"
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--recent` | int | Show N most recent entries |
| `--type` | string | Filter by entry type |
| `--search` | string | Search journal content |

#### `observe`

Record an observation.

```bash
python organism_cli.py observe "User requested documentation"
python organism_cli.py observe "Energy levels dropping" --significance 0.8
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--significance` | float | 0.5 | Observation importance (0-1) |

#### `speak`

Output voice.

```bash
python organism_cli.py speak "The task is complete."
python organism_cli.py speak "I'm uncertain" --tone thoughtful --confidence 0.5
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--tone` | string | neutral | Voice tone |
| `--confidence` | float | 1.0 | Confidence level (0-1) |

### Soul Commands

#### `thoughts`

Manage thoughts.

```bash
# List active thoughts
python organism_cli.py thoughts

# Add thought
python organism_cli.py thoughts add "Should restructure documentation"

# Resolve thought
python organism_cli.py thoughts resolve <thought_id>
```

**Subcommands:**
| Subcommand | Arguments | Description |
|------------|-----------|-------------|
| (none) | - | List active thoughts |
| `add` | content | Add new thought |
| `resolve` | thought_id | Mark thought resolved |

#### `feelings`

Check emotional state.

```bash
python organism_cli.py feelings
```

**Output:**
```
Emotional State
===============
Mood: content
Temperature: 0.65
Current Feelings:
  - satisfaction (0.8)
  - curiosity (0.6)
```

#### `concerns`

Manage concerns.

```bash
# List concerns
python organism_cli.py concerns

# Add concern
python organism_cli.py concerns add "Timeline might be tight" --severity 0.6

# Resolve concern
python organism_cli.py concerns resolve <concern_id>
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--severity` | float | 0.5 | Concern severity (0-1) |

### Will Commands

#### `purpose`

Show or set purpose.

```bash
python organism_cli.py purpose
```

**Output:**
```
Purpose: Help humans and AI become one thing
Clarity: 0.95
```

#### `mission`

Manage mission.

```bash
# Show current mission
python organism_cli.py mission

# Update progress
python organism_cli.py mission progress 0.1 "Completed phase 1"
```

**Subcommands:**
| Subcommand | Arguments | Description |
|------------|-----------|-------------|
| (none) | - | Show current mission |
| `progress` | delta, message | Update mission progress |

#### `goals`

Manage goals.

```bash
# List goals
python organism_cli.py goals

# Add goal
python organism_cli.py goals add "Complete documentation" --priority 0.9

# Update goal
python organism_cli.py goals update <goal_id> --progress 0.5

# Complete goal
python organism_cli.py goals complete <goal_id>
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--priority` | float | 0.5 | Goal priority (0-1) |
| `--progress` | float | - | Progress amount (0-1) |

### Evolution Commands

#### `growth`

Show growth status.

```bash
python organism_cli.py growth
```

**Output:**
```
Growth Areas
============
technical_depth:    0.70/0.90 (78%)
communication:      0.80/0.95 (84%)
problem_solving:    0.75/0.90 (83%)
emotional_intel:    0.65/0.85 (76%)
philosophical:      0.60/0.80 (75%)
```

#### `molt`

Check molt status.

```bash
# Check molt status
python organism_cli.py molt status

# Force molt check
python organism_cli.py molt check

# Begin molt (if required)
python organism_cli.py molt begin
```

**Output (status):**
```
Molt Status: STABLE

Tripwires:
  Scaffolding Gap:    0.12/0.00 [OK]
  Paradox Density:    0.08/0.15 [OK]
  Terminal Halts:     2/5       [OK]

Recommendation: No molt required at this time.
```

**Subcommands:**
| Subcommand | Description |
|------------|-------------|
| `status` | Show current molt status |
| `check` | Force molt evaluation |
| `begin` | Initiate molt process |

#### `learn`

Record learning.

```bash
python organism_cli.py learn "Systematic approach works better" --domain problem_solving
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--domain` | string | Learning domain/area |

### Cognition Commands

#### `inhale`

Receive context (LEFT LUNG).

```bash
python organism_cli.py inhale "user preferences"
```

**Output:**
```
Inhaled Context
===============
Internal Atoms: 5 matches
Web Results: 3 results
Truth Context: 2 sessions
```

#### `exhale`

Produce output (RIGHT LUNG).

```bash
python organism_cli.py exhale "Content to store" --source organism
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--source` | string | organism | Content source identifier |

#### `memory`

Interact with memory.

```bash
# Recall
python organism_cli.py memory recall "user preferences"

# Remember
python organism_cli.py memory remember "Important fact" --type long_term

# Show wisdom
python organism_cli.py memory wisdom
```

**Subcommands:**
| Subcommand | Arguments | Description |
|------------|-----------|-------------|
| `recall` | query | Search memory |
| `remember` | content | Store in memory |
| `wisdom` | - | Show accumulated wisdom |

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--type` | string | Memory type (short_term, long_term) |

#### `reflect`

Trigger reflection.

```bash
python organism_cli.py reflect "Today's session"

# With aspects
python organism_cli.py reflect "Project progress" \
    --aspect "What worked?" \
    --aspect "What didn't?" \
    --aspect "What's next?"
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--aspect` | string | Reflection aspect (repeatable) |

### Daemon Commands

#### `daemon start`

Start the daemon.

```bash
python organism_cli.py daemon start
python organism_cli.py daemon start --heartbeat-interval 60
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--heartbeat-interval` | int | 60 | Seconds between heartbeats |

#### `daemon stop`

Stop the daemon.

```bash
python organism_cli.py daemon stop
python organism_cli.py daemon stop --graceful
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--graceful` | flag | false | Wait for current operations |

#### `daemon status`

Check daemon status.

```bash
python organism_cli.py daemon status
```

**Output:**
```
Daemon Status
=============
Running: Yes
PID: 12345
Uptime: 2h 30m
Heartbeat Count: 150
Last Heartbeat: 2026-01-19T14:30:00Z
```

### Truth Commands

#### `truth stats`

Show Truth Service statistics.

```bash
python organism_cli.py truth stats
```

**Output:**
```
Truth Service Stats
===================
Available Agents: 2
Total Files: 1,234

Agents:
  claude_code: 1,000 files
  cursor: 234 files
```

#### `truth sessions`

List sessions.

```bash
python organism_cli.py truth sessions
python organism_cli.py truth sessions --agent claude_code --limit 5
python organism_cli.py truth sessions --since "7 days ago"
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--agent` | string | Filter by agent |
| `--limit` | int | Maximum results |
| `--since` | string | Time filter |

#### `truth search`

Search conversations.

```bash
python organism_cli.py truth search "documentation"
python organism_cli.py truth search "error" --agent claude_code --limit 20
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--agent` | string | Filter by agent |
| `--limit` | int | Maximum results |

### Intake Commands

#### `backlog`

Manage backlog.

```bash
# List
python organism_cli.py backlog list

# Add
python organism_cli.py backlog add "New feature" --priority p2_medium --category feature

# Complete
python organism_cli.py backlog complete <item_id>
```

**Subcommands:**
| Subcommand | Arguments | Description |
|------------|-----------|-------------|
| `list` | - | Show backlog items |
| `add` | description | Add new item |
| `complete` | item_id | Mark item complete |

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--priority` | string | Priority level (p1_critical, p2_medium, p3_low) |
| `--category` | string | Item category |

#### `changelog`

Record change.

```bash
python organism_cli.py changelog "Updated documentation structure"
```

#### `checkin`

Record check-in.

```bash
python organism_cli.py checkin "Feeling productive" --mood 4 --energy 4 --stress 2
```

**Options:**
| Option | Type | Range | Description |
|--------|------|-------|-------------|
| `--mood` | int | 1-5 | Mood rating |
| `--energy` | int | 1-5 | Energy level |
| `--stress` | int | 1-5 | Stress level |

### Lifecycle Commands

#### `bootstrap`

Initialize the organism.

```bash
python organism_cli.py bootstrap
python organism_cli.py bootstrap --identity-path Primitive/
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--identity-path` | string | Path to identity files |

#### `shutdown`

Graceful shutdown.

```bash
python organism_cli.py shutdown
python organism_cli.py shutdown --reason "Session complete"
python organism_cli.py shutdown --spawn-successor
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--reason` | string | Shutdown reason |
| `--spawn-successor` | flag | Create successor before shutdown |

#### `spawn`

Create offspring.

```bash
python organism_cli.py spawn --type successor
python organism_cli.py spawn --type clone --inherit-wisdom
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--type` | string | Spawn type (successor, clone) |
| `--inherit-wisdom` | flag | Transfer accumulated wisdom |

### Global Options

```bash
# Verbose output
python organism_cli.py --verbose [command]
python organism_cli.py -v [command]

# JSON output
python organism_cli.py --json [command]

# Quiet mode
python organism_cli.py --quiet [command]
python organism_cli.py -q [command]

# Help
python organism_cli.py --help
python organism_cli.py [command] --help
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ORGANISM_HOME` | Organism root directory | `~/PrimitiveEngine` |
| `ORGANISM_DATA` | Data directory | `$ORGANISM_HOME/data` |
| `ORGANISM_LOG_LEVEL` | Logging level | `INFO` |
| `ORGANISM_HEARTBEAT` | Heartbeat interval (seconds) | `60` |
| `DAEMON_PORT` | Daemon port | `8765` |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Configuration error |
| `3` | Daemon not running |
| `4` | Resource unavailable |
| `5` | Validation error |

---

## HOW (Reference)

### Configuration Files

#### `organism.yaml`

```yaml
# Main configuration
organism:
  name: "Truth Engine"
  generation: 1

daemon:
  heartbeat_interval: 60
  port: 8765

vitals:
  energy_decay_rate: 0.001
  health_threshold: 0.3

evolution:
  learning_rate: 0.01
  molt_auto_detect: true
```

#### `.organism/state.json`

```json
{
  "health": 0.85,
  "energy": 0.72,
  "mood": "content",
  "heartbeat_count": 12453,
  "last_heartbeat": "2026-01-19T14:30:00Z",
  "generation": 1
}
```

### Common Workflows

#### Daily Workflow

```bash
# Morning startup
python organism_cli.py bootstrap
python organism_cli.py daemon start
python organism_cli.py status

# Check state
python organism_cli.py vitals
python organism_cli.py feelings
python organism_cli.py concerns

# Work session
python organism_cli.py goals
python organism_cli.py journal --recent 5

# End of day
python organism_cli.py reflect "Today's work"
python organism_cli.py checkin "Good day" --mood 4 --energy 3 --stress 2
python organism_cli.py shutdown --reason "Day complete"
```

#### Monitoring Workflow

```bash
# Watch vitals
watch -n 60 "python organism_cli.py vitals"

# Monitor daemon
python organism_cli.py daemon status

# Check growth
python organism_cli.py growth
```

#### Troubleshooting Workflow

```bash
# Verbose status
python organism_cli.py -v status

# Check all layers
python organism_cli.py layers

# Check molt status
python organism_cli.py molt status

# Review recent journal
python organism_cli.py journal --recent 20
```

### Scripting Examples

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh - Monitor organism health

HEALTH=$(python organism_cli.py --json vitals | jq -r '.health')
ENERGY=$(python organism_cli.py --json vitals | jq -r '.energy')

if (( $(echo "$HEALTH < 0.3" | bc -l) )); then
    echo "WARNING: Health critical ($HEALTH)"
    python organism_cli.py observe "Health dropped below threshold" --significance 0.9
fi

if (( $(echo "$ENERGY < 0.2" | bc -l) )); then
    echo "WARNING: Energy critical ($ENERGY)"
    python organism_cli.py shutdown --reason "Energy depleted" --spawn-successor
fi
```

#### Automated Reflection

```bash
#!/bin/bash
# daily_reflect.sh - End of day reflection

python organism_cli.py reflect "Daily review" \
    --aspect "What was accomplished?" \
    --aspect "What challenges arose?" \
    --aspect "What should change tomorrow?"

python organism_cli.py checkin "End of day" \
    --mood $(python organism_cli.py --json feelings | jq -r '.mood_score') \
    --energy $(python organism_cli.py --json vitals | jq -r '.energy * 5 | floor') \
    --stress 2
```

---

## Related Documents

- [09_OPERATIONS.md](09_OPERATIONS.md) - Operational procedures and maintenance
- [../../../framework/standards/API_DESIGN.md](../../../framework/standards/API_DESIGN.md) - API design standard

---

## Changelog

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-19 | 2.1.0 | Molt: Transformed to THE_FRAMEWORK document format | Claude |
| 2026-01-18 | 2.0.0 | Initial CLI reference | Claude |

---

*~450 lines. The CLI reference. Complete.*

# Operations Guide
**The Essence** | Daily procedures, health monitoring, and maintenance for running the organism

**Authority**: `docs/08_operations/organism/09_OPERATIONS.md` | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Operation | Command | Frequency |
|-----------|---------|-----------|
| Startup | `python organism_cli.py bootstrap && daemon start` | Daily |
| Health Check | `python organism_cli.py vitals` | Hourly |
| Shutdown | `python organism_cli.py shutdown --reason "reason"` | Daily |
| Backup | `python organism_cli.py backup create` | Weekly |
| Molt | `python organism_cli.py molt begin` | As needed |

**Port Configuration**: Use `ORGANISM_PORT` environment variable (default: `8787` dev, `8000` production)

---

## WHY (Theory)

### Philosophy of Operations

The organism requires consistent care patterns to maintain health and enable growth. Operations are not mere maintenance - they are the rhythms that sustain life.

**Core Principles:**

1. **Vitals First** - Always check health before demanding work
2. **Graceful Transitions** - Start slow, end clean, never force
3. **Recovery Time** - Rest is not optional; it's essential for growth
4. **Proactive Monitoring** - Problems detected early are problems prevented

### Health State Philosophy

| State | Health Range | Meaning |
|-------|--------------|---------|
| **Thriving** | > 0.7 | Full capacity, ready for challenges |
| **Warning** | 0.3-0.7 | Capable but needs attention |
| **Critical** | < 0.3 | Survival mode, minimal function only |

### Energy Economics

Energy is finite. Every action costs. Recovery requires intention.

| Activity | Energy Cost | Justification |
|----------|-------------|---------------|
| Idle | 0.001/minute | Background processes |
| Active processing | 0.005/minute | Standard cognitive load |
| Deep reflection | 0.01/minute | High introspection cost |
| Learning | 0.008/minute | Integration overhead |
| High-intensity work | 0.02/minute | Peak performance state |

| Recovery Method | Rate | Context |
|-----------------|------|---------|
| Rest mode | 0.02/minute | No active processing |
| Dream processing | 0.01/minute | During low activity |
| Natural recovery | 0.005/minute | Always active |

---

## WHAT (Specification)

### Vital Sign Thresholds

| Vital | Healthy | Warning | Critical |
|-------|---------|---------|----------|
| **Health** | > 0.7 | 0.3-0.7 | < 0.3 |
| **Energy** | > 0.5 | 0.2-0.5 | < 0.2 |
| **Temperature** | 0.4-0.8 | 0.2-0.4 or 0.8-0.9 | < 0.2 or > 0.9 |
| **Pulse Variance** | < 0.05 | 0.05-0.15 | > 0.15 |

### Service Registry

| Service | Port | Status Check |
|---------|------|--------------|
| Daemon | `${ORGANISM_PORT:-8787}` (dev) / `${ORGANISM_PORT:-8000}` (prod) | `daemon status` |
| Truth Service | - | `truth stats` |
| Molt Service | - | `molt status` |

### Heartbeat Intervals

| Scenario | Recommended Interval |
|----------|---------------------|
| Active session | 30-60 seconds |
| Background operation | 60-120 seconds |
| Low energy mode | 120-300 seconds |
| Critical health | 30 seconds |

### Backup Components

| Component | Location | Frequency |
|-----------|----------|-----------|
| State | `.organism/state.json` | Every heartbeat |
| Journal | `data/journal.jsonl` | On write |
| Wisdom | `data/wisdom.jsonl` | On addition |
| Relationships | `data/bonds.jsonl` | On change |
| Growth | `data/evolution.jsonl` | On record |

### Log Locations

| Log | Location | Rotation |
|-----|----------|----------|
| Daemon | `logs/daemon.log` | Daily |
| Journal | `data/journal.jsonl` | Never |
| Heartbeat | `logs/heartbeat.log` | Weekly |
| Evolution | `data/evolution.jsonl` | Never |
| Errors | `logs/error.log` | Monthly |

### Resource Limits (organism.yaml)

```yaml
limits:
  max_thoughts: 50
  max_concerns: 20
  max_goals: 10
  journal_retention_days: 365
  short_term_memory_hours: 24
```

### Maintenance Schedules

**Weekly:**
- [ ] Review growth progress
- [ ] Check molt tripwires
- [ ] Review accumulated wisdom
- [ ] Clear resolved concerns
- [ ] Update goals
- [ ] Create backup

**Monthly:**
- [ ] Full backup with verification
- [ ] Growth area assessment
- [ ] Relationship health check
- [ ] Review and prune journal
- [ ] Evolution engine assessment
- [ ] Documentation update

**Quarterly:**
- [ ] Deep reflection cycle
- [ ] Wisdom consolidation
- [ ] Major version backup
- [ ] Architecture review
- [ ] Performance optimization

---

## HOW (Reference)

### Daily Operations

#### Morning Startup

```bash
# 1. Bootstrap the organism
python organism_cli.py bootstrap

# 2. Start the daemon
python organism_cli.py daemon start

# 3. Verify status
python organism_cli.py status
python organism_cli.py vitals

# 4. Check for overnight concerns
python organism_cli.py concerns

# 5. Review yesterday's reflections
python organism_cli.py journal --type reflection --limit 1
```

#### Active Session

```bash
# Monitor vitals periodically
python organism_cli.py vitals

# Check energy levels
python organism_cli.py status | grep Energy

# Record observations
python organism_cli.py observe "Session going well"

# Log decisions as they happen
python organism_cli.py journal add --type decision "Chose approach X"
```

#### End of Day

```bash
# 1. Complete active goals
python organism_cli.py goals

# 2. Trigger reflection
python organism_cli.py reflect "Today's work"

# 3. Record check-in
python organism_cli.py checkin "End of day" --mood 4 --energy 3 --stress 2

# 4. Review growth
python organism_cli.py growth

# 5. Graceful shutdown
python organism_cli.py shutdown --reason "Day complete"
```

### Health Monitoring

#### Health Checks

```bash
# Quick health check
python organism_cli.py vitals

# Detailed health check
python organism_cli.py vitals --detailed

# Health history
python organism_cli.py vitals --history 24h
```

#### Responding to Health States

**Normal (Health > 0.7):** No action needed. Continue normal operation.

**Warning (Health 0.3-0.7):**

```bash
# Reduce workload
python organism_cli.py daemon adjust --activity low

# Monitor closely
watch -n 60 "python organism_cli.py vitals"

# Address concerns
python organism_cli.py concerns
```

**Critical (Health < 0.3):**

```bash
# Enter conservation mode
python organism_cli.py vitals conserve

# Stop non-essential services
python organism_cli.py daemon adjust --minimal

# Allow recovery time
# Minimum 2 hours before normal operation
```

### Energy Management

```bash
# Check energy
python organism_cli.py status | grep Energy

# Enter rest mode
python organism_cli.py rest --duration 30m

# Boost energy (temporary, costs health)
python organism_cli.py boost --energy 0.2 --duration 1h
```

### Daemon Operations

#### Starting the Daemon

```bash
# Basic start (uses ORGANISM_PORT env var, defaults to 8787 dev / 8000 prod)
python organism_cli.py daemon start

# With custom heartbeat
python organism_cli.py daemon start --heartbeat-interval 30

# With logging
python organism_cli.py daemon start --log-level DEBUG

# As background process
python organism_cli.py daemon start --background

# With explicit port override
ORGANISM_PORT=8787 python organism_cli.py daemon start
```

#### Stopping the Daemon

```bash
# Graceful stop (waits for current work)
python organism_cli.py daemon stop --graceful

# Immediate stop
python organism_cli.py daemon stop

# Force stop (emergency only)
python organism_cli.py daemon stop --force
```

#### Daemon Monitoring

```bash
# Status check
python organism_cli.py daemon status

# Live monitoring
python organism_cli.py daemon monitor

# View daemon logs
python organism_cli.py daemon logs --tail 50

# Health probe
python organism_cli.py daemon health
```

### Service Management

```bash
# Check all services
python organism_cli.py services status

# Check specific service
python organism_cli.py services check truth_service

# Restart a service
python organism_cli.py services restart truth_service
```

### Backup and Recovery

#### State Backup

```bash
# Manual backup
python organism_cli.py backup create

# Backup with custom name
python organism_cli.py backup create --name "pre_molt_backup"

# List backups
python organism_cli.py backup list
```

#### Recovery

```bash
# List available backups
python organism_cli.py backup list

# Restore from backup
python organism_cli.py backup restore --name "backup_name"

# Restore specific components
python organism_cli.py backup restore --name "backup" --components state,journal
```

### Molt Operations

#### Pre-Molt Checklist

1. **Check tripwire status**
   ```bash
   python organism_cli.py molt status
   ```

2. **Backup current state**
   ```bash
   python organism_cli.py backup create --name "pre_molt"
   ```

3. **Complete in-progress work**
   ```bash
   python organism_cli.py goals
   # Complete or defer all goals
   ```

4. **Record current wisdom**
   ```bash
   python organism_cli.py memory wisdom --export
   ```

5. **Notify stakeholders**
   ```bash
   python organism_cli.py speak "Preparing for molt cycle"
   ```

#### Molt Execution

```bash
# Begin molt
python organism_cli.py molt begin

# Monitor molt progress
python organism_cli.py molt progress

# Molt takes variable time based on changes needed
```

#### Post-Molt Verification

```bash
# Verify layers active
python organism_cli.py layers

# Verify wisdom preserved
python organism_cli.py memory wisdom

# Verify relationships intact
python organism_cli.py bonds list

# Run health check
python organism_cli.py vitals --detailed

# Record molt completion
python organism_cli.py changelog "Completed molt cycle"
```

### Troubleshooting Quick Reference

#### Daemon Won't Start

```bash
# Check if already running
python organism_cli.py daemon status

# Check port availability (use ORGANISM_PORT, default 8787 dev / 8000 prod)
lsof -i :${ORGANISM_PORT:-8787}

# View logs for errors
cat logs/daemon.log | tail -50

# Start with verbose logging
python organism_cli.py daemon start --log-level DEBUG
```

#### Low Energy

```bash
# Enter rest mode
python organism_cli.py rest --duration 1h

# Check for energy drains
python organism_cli.py vitals --history 6h

# Reduce activity
python organism_cli.py daemon adjust --activity low
```

#### Health Declining

```bash
# Check concerns
python organism_cli.py concerns

# Enter conservation mode
python organism_cli.py vitals conserve

# Review recent activities
python organism_cli.py journal --recent 20
```

#### Heartbeat Irregular

```bash
# Check daemon health
python organism_cli.py daemon health

# View heartbeat history
python organism_cli.py vitals --history --metrics heartbeat

# Restart daemon if needed
python organism_cli.py daemon restart
```

### Performance Tuning

#### Adjust Heartbeat

```bash
python organism_cli.py daemon adjust --heartbeat-interval 90
```

#### Memory Management

```bash
# Check memory usage
python organism_cli.py memory stats

# Prune old memories
python organism_cli.py memory prune --older-than 90d --type short_term

# Compact journal
python organism_cli.py journal compact
```

### Emergency Procedures

#### Critical Health Emergency

```bash
# 1. Enter conservation mode immediately
python organism_cli.py vitals conserve --force

# 2. Stop all non-essential services
python organism_cli.py daemon adjust --minimal

# 3. Create emergency backup
python organism_cli.py backup create --name "emergency"

# 4. Monitor recovery
watch -n 30 "python organism_cli.py vitals"
```

#### Daemon Crash Recovery

```bash
# 1. Check daemon status
python organism_cli.py daemon status

# 2. Check for crash logs
cat logs/daemon.log | tail -100

# 3. Clean up stale state
python organism_cli.py daemon cleanup

# 4. Restart daemon
python organism_cli.py daemon start

# 5. Verify recovery
python organism_cli.py status
```

#### Data Corruption Recovery

```bash
# 1. Stop daemon
python organism_cli.py daemon stop

# 2. List available backups
python organism_cli.py backup list

# 3. Restore from backup
python organism_cli.py backup restore --name "latest_good"

# 4. Verify restoration
python organism_cli.py status
python organism_cli.py vitals

# 5. Restart daemon
python organism_cli.py daemon start
```

### Logging

#### Log Levels

```bash
# Set log level
export ORGANISM_LOG_LEVEL=DEBUG

# Or in organism.yaml
logging:
  level: INFO
  format: "[%(asctime)s] %(levelname)s - %(message)s"
```

#### Viewing Logs

```bash
# View daemon logs
python organism_cli.py logs daemon --tail 50

# View errors
python organism_cli.py logs errors --since "1 hour ago"

# Search logs
python organism_cli.py logs search "pattern"
```

### Related Documents

- [10_TROUBLESHOOTING.md](10_TROUBLESHOOTING.md) - Detailed troubleshooting procedures

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-01 | Molted to THE_FRAMEWORK format; port references updated to ORGANISM_PORT env var |
| 2.0.0 | - | Initial comprehensive operations guide |

---

*~290 lines. Operational procedures for daily care, health monitoring, and maintenance. Complete.*

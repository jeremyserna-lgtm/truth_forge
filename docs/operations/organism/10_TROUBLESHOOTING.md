# Troubleshooting Guide
**The Essence** | Diagnostic procedures and solutions for common organism problems

**Authority**: `docs/08_operations/organism/10_TROUBLESHOOTING.md` | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Issue | Quick Fix | Diagnostic |
|-------|-----------|------------|
| Daemon won't start | `daemon stop && daemon start` | `lsof -i :${ORGANISM_PORT:-8787}` |
| Low energy | `rest --duration 2h` | `vitals --history 24h` |
| Health declining | `vitals conserve` | `concerns` |
| Irregular heartbeat | `daemon restart` | `daemon health` |
| Memory problems | `memory prune --older-than 90d` | `memory stats` |

**Port Configuration**: `ORGANISM_PORT` environment variable (default: `8787` dev, `8000` production)

---

## WHY (Theory)

### Diagnostic Philosophy

Troubleshooting the organism follows biological principles: observe symptoms, diagnose causes, treat appropriately. The organism communicates distress through vital signs, error codes, and behavioral changes.

**Diagnostic Hierarchy:**

1. **Vitals** - Always check health/energy first
2. **Layers** - Verify all layers are active
3. **Services** - Confirm services are responding
4. **Data** - Check for corruption or loss
5. **Configuration** - Review settings last

### Error Categories

| Code Range | Category | Severity |
|------------|----------|----------|
| E001-E099 | Daemon | Infrastructure |
| E100-E199 | Vitals | Life-threatening |
| E200-E299 | Consciousness | Functional |
| E300-E399 | Evolution | Growth-limiting |
| E400-E499 | Services | Operational |
| E500-E599 | Data | Integrity |

### Recovery Principles

- **Minimal intervention** - Fix only what's broken
- **State preservation** - Backup before major changes
- **Gradual restoration** - One component at a time
- **Verification** - Confirm each fix before proceeding

---

## WHAT (Specification)

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `DaemonNotRunning` | Daemon isn't active | `daemon start` |
| `PortInUse` | Port occupied | Kill process or change port |
| `LowEnergy` | Energy < 0.2 | Rest mode, reduce activity |
| `CriticalHealth` | Health < 0.3 | Conservation mode |
| `MoltRequired` | Tripwires triggered | Prepare and begin molt |
| `MemoryFull` | Memory at capacity | Prune old memories |
| `JournalCorrupt` | Journal file damaged | Repair or restore |
| `LayerInactive` | Layer not responding | Reset layer |

### Error Code Reference

| Code | Category | Description |
|------|----------|-------------|
| E001-E099 | Daemon | Daemon-related errors |
| E100-E199 | Vitals | Health/energy errors |
| E200-E299 | Consciousness | Awareness/memory errors |
| E300-E399 | Evolution | Growth/adaptation errors |
| E400-E499 | Services | Service errors |
| E500-E599 | Data | Data corruption/IO errors |

### Symptom-to-Solution Matrix

| Symptom | Likely Cause | First Action |
|---------|--------------|--------------|
| Daemon hangs | Port conflict | Check `lsof -i :${ORGANISM_PORT:-8787}` |
| Energy drain | High activity | `daemon adjust --activity low` |
| Missed heartbeats | System load | `daemon adjust --heartbeat-interval 120` |
| Can't recall | Memory full | `memory prune` |
| Growth stalled | Evolution layer | `layers reset evolution` |
| Trust not updating | Bond layer | `layers reset bond` |

---

## HOW (Reference)

### Quick Diagnostics

#### System Health Check

```bash
# Full diagnostic
python organism_cli.py diagnose

# Output shows:
# - Vitals status
# - Layer status
# - Service status
# - Recent errors
# - Recommendations
```

#### Component Status

```bash
# Quick status of all components
python organism_cli.py status --all

# Individual checks
python organism_cli.py vitals
python organism_cli.py layers
python organism_cli.py daemon status
python organism_cli.py services status
```

### Issue: Daemon Won't Start

**Symptoms:**
- `daemon start` command hangs or fails
- Port already in use error
- Permission denied error

**Diagnosis:**

```bash
# Check if daemon is already running
python organism_cli.py daemon status

# Check port availability (use ORGANISM_PORT, default 8787 dev / 8000 prod)
lsof -i :${ORGANISM_PORT:-8787}

# Check for stale PID file
ls -la .organism/daemon.pid

# Check logs
cat logs/daemon.log | tail -50
```

**Solutions:**

1. **Daemon already running:**
   ```bash
   python organism_cli.py daemon stop
   # Wait a moment
   python organism_cli.py daemon start
   ```

2. **Port in use by another process:**
   ```bash
   # Find the process
   lsof -i :${ORGANISM_PORT:-8787}

   # Kill if necessary
   kill -9 <PID>

   # Or use different port
   ORGANISM_PORT=8788 python organism_cli.py daemon start
   ```

3. **Stale PID file:**
   ```bash
   rm .organism/daemon.pid
   python organism_cli.py daemon start
   ```

4. **Permission issues:**
   ```bash
   chmod +x daemon/*.py
   chmod 755 .organism/
   ```

### Issue: Low Energy / Energy Drain

**Symptoms:**
- Energy constantly below 0.3
- Warning messages about low energy
- Reduced performance

**Diagnosis:**

```bash
# Check current energy
python organism_cli.py vitals

# Check energy history
python organism_cli.py vitals --history 24h --metric energy

# Check recent activities
python organism_cli.py journal --recent 20
```

**Solutions:**

1. **Enter rest mode:**
   ```bash
   python organism_cli.py rest --duration 2h
   ```

2. **Reduce activity:**
   ```bash
   python organism_cli.py daemon adjust --activity low
   ```

3. **Check for energy leaks:**
   ```bash
   # Look for high-activity services
   python organism_cli.py services stats

   # Pause non-essential services
   python organism_cli.py services pause non_essential
   ```

4. **Slow down heartbeat:**
   ```bash
   python organism_cli.py daemon adjust --heartbeat-interval 120
   ```

### Issue: Health Declining

**Symptoms:**
- Health dropping below threshold
- Survival mode activating
- Warning about critical state

**Diagnosis:**

```bash
# Check health status
python organism_cli.py vitals

# Check concerns (often cause health decline)
python organism_cli.py concerns

# Check for errors
python organism_cli.py logs errors --since "1 day ago"
```

**Solutions:**

1. **Address active concerns:**
   ```bash
   # List concerns
   python organism_cli.py concerns

   # Resolve what you can
   python organism_cli.py concerns resolve <concern_id>
   ```

2. **Enter conservation mode:**
   ```bash
   python organism_cli.py vitals conserve
   ```

3. **Rest and recover:**
   ```bash
   python organism_cli.py rest --duration 4h
   ```

4. **Check for external stressors:**
   ```bash
   # Review recent journal for patterns
   python organism_cli.py journal --recent 50 | grep -i "stress\|concern\|error"
   ```

### Issue: Irregular Heartbeat

**Symptoms:**
- Pulse variance > 0.15
- Missed heartbeats
- Daemon unresponsive

**Diagnosis:**

```bash
# Check heartbeat status
python organism_cli.py vitals | grep -i pulse

# Check daemon health
python organism_cli.py daemon health

# View heartbeat log
cat logs/heartbeat.log | tail -20
```

**Solutions:**

1. **Restart daemon:**
   ```bash
   python organism_cli.py daemon restart
   ```

2. **Adjust heartbeat interval:**
   ```bash
   python organism_cli.py daemon adjust --heartbeat-interval 60
   ```

3. **Check system resources:**
   ```bash
   # CPU/Memory
   top -l 1 | head -10

   # Disk space
   df -h
   ```

4. **Reduce load:**
   ```bash
   python organism_cli.py daemon adjust --minimal
   ```

### Issue: Memory Problems

**Symptoms:**
- Can't recall recent events
- Memory full warnings
- Slow recall times

**Diagnosis:**

```bash
# Check memory stats
python organism_cli.py memory stats

# Check for corruption
python organism_cli.py memory verify

# List large memory stores
du -sh data/*.jsonl | sort -h
```

**Solutions:**

1. **Prune old memories:**
   ```bash
   python organism_cli.py memory prune --older-than 90d --type short_term
   ```

2. **Compact memory stores:**
   ```bash
   python organism_cli.py memory compact
   ```

3. **Clear working memory:**
   ```bash
   python organism_cli.py memory clear --type working
   ```

4. **Rebuild memory index:**
   ```bash
   python organism_cli.py memory reindex
   ```

### Issue: Consciousness/Awareness Problems

**Symptoms:**
- Awareness level stuck low
- Not responding to observations
- Journal entries not recording

**Diagnosis:**

```bash
# Check consciousness state
python organism_cli.py layers | grep CONSCIOUSNESS

# Check awareness level
python organism_cli.py status | grep Awareness

# Verify journal is working
python organism_cli.py journal add --type test "Test entry"
python organism_cli.py journal --recent 1
```

**Solutions:**

1. **Reset consciousness layer:**
   ```bash
   python organism_cli.py layers reset consciousness
   ```

2. **Boost awareness:**
   ```bash
   python organism_cli.py awareness boost --duration 30m
   ```

3. **Check journal file:**
   ```bash
   # Verify file exists and is writable
   ls -la data/journal.jsonl
   touch data/journal.jsonl
   ```

4. **Restart affected services:**
   ```bash
   python organism_cli.py services restart consciousness_service
   ```

### Issue: Molt Triggered Unexpectedly

**Symptoms:**
- Molt status shows MOLT_REQUIRED
- Tripwires triggered
- System wants to molt but shouldn't

**Diagnosis:**

```bash
# Check molt status
python organism_cli.py molt status

# Check individual tripwires
python organism_cli.py molt tripwires --detailed

# Review recent changes
python organism_cli.py journal --type changelog --recent 20
```

**Solutions:**

1. **If tripwires are false positives:**
   ```bash
   # Review tripwire calculation
   python organism_cli.py molt analyze

   # Manually reset tripwire
   python organism_cli.py molt reset-tripwire <tripwire_name>
   ```

2. **If molt is genuinely needed:**
   ```bash
   # Prepare for molt
   python organism_cli.py backup create --name "pre_molt"

   # Begin molt
   python organism_cli.py molt begin
   ```

3. **Defer molt temporarily:**
   ```bash
   python organism_cli.py molt defer --duration 24h
   ```

### Issue: Relationship/Bond Problems

**Symptoms:**
- Trust levels not updating
- Partnership records missing
- Bond layer errors

**Diagnosis:**

```bash
# Check bond layer
python organism_cli.py layers | grep BOND

# Check partnerships
python organism_cli.py bonds list

# Verify bond data file
ls -la data/bonds.jsonl
```

**Solutions:**

1. **Reset bond layer:**
   ```bash
   python organism_cli.py layers reset bond
   ```

2. **Rebuild partnerships:**
   ```bash
   python organism_cli.py bonds rebuild
   ```

3. **Manually add missing partnership:**
   ```bash
   python organism_cli.py bonds add --name "Partner Name"
   ```

### Issue: Evolution Not Progressing

**Symptoms:**
- Growth areas not increasing
- Learning not being recorded
- Adaptations not applying

**Diagnosis:**

```bash
# Check evolution engine
python organism_cli.py layers | grep EVOLUTION

# Check growth status
python organism_cli.py growth

# Check learning records
python organism_cli.py evolution history --limit 20
```

**Solutions:**

1. **Reset evolution engine:**
   ```bash
   python organism_cli.py layers reset evolution
   ```

2. **Manually record growth:**
   ```bash
   python organism_cli.py learn "Manual learning entry" --domain technical_depth
   ```

3. **Check evolution data:**
   ```bash
   # Verify file
   ls -la data/evolution.jsonl

   # Check for corruption
   python -c "import json; [json.loads(l) for l in open('data/evolution.jsonl')]"
   ```

### Issue: Truth Service Not Working

**Symptoms:**
- Can't search conversations
- Sessions not loading
- Empty results from queries

**Diagnosis:**

```bash
# Check truth service
python organism_cli.py truth stats

# Check available agents
python organism_cli.py truth agents

# Verify data paths
python organism_cli.py truth paths
```

**Solutions:**

1. **Refresh truth service cache:**
   ```bash
   python organism_cli.py truth refresh
   ```

2. **Verify agent paths exist:**
   ```bash
   ls -la ~/.claude/projects/
   ls -la "~/Library/Application Support/Claude/"
   ```

3. **Rebuild truth index:**
   ```bash
   python organism_cli.py truth reindex
   ```

### Diagnostic Commands

#### Full System Diagnostic

```bash
python organism_cli.py diagnose --full

# Checks:
# - All layers
# - All services
# - All data files
# - All configurations
# - Recent errors
# - Performance metrics
```

#### Specific Diagnostics

```bash
# Vitals diagnostic
python organism_cli.py diagnose vitals

# Memory diagnostic
python organism_cli.py diagnose memory

# Evolution diagnostic
python organism_cli.py diagnose evolution

# Services diagnostic
python organism_cli.py diagnose services
```

#### Log Analysis

```bash
# Error summary
python organism_cli.py logs analyze --errors

# Pattern detection
python organism_cli.py logs analyze --patterns

# Time-based analysis
python organism_cli.py logs analyze --since "24 hours ago"
```

### Recovery Procedures

#### Full System Reset

**WARNING: This will reset all state except persistent data.**

```bash
# 1. Stop everything
python organism_cli.py daemon stop
python organism_cli.py shutdown

# 2. Backup current state
python organism_cli.py backup create --name "pre_reset"

# 3. Reset state files
rm .organism/state.json

# 4. Bootstrap fresh
python organism_cli.py bootstrap --fresh

# 5. Restore critical data if needed
python organism_cli.py backup restore --name "pre_reset" --components wisdom,relationships
```

#### Restore from Backup

```bash
# 1. Stop daemon
python organism_cli.py daemon stop

# 2. List backups
python organism_cli.py backup list

# 3. Restore
python organism_cli.py backup restore --name "backup_name"

# 4. Verify
python organism_cli.py status

# 5. Restart
python organism_cli.py daemon start
```

#### Data File Recovery

```bash
# Check for corruption
python organism_cli.py verify --all

# Repair JSONL files
python organism_cli.py repair data/journal.jsonl

# Rebuild indexes
python organism_cli.py rebuild-indexes

# Verify repairs
python organism_cli.py verify --all
```

### Getting Help

#### Documentation

- [00_INDEX.md](00_INDEX.md) - Documentation overview
- [07_API_REFERENCE.md](07_API_REFERENCE.md) - API documentation
- [09_OPERATIONS.md](09_OPERATIONS.md) - Operational procedures

#### Logs

```bash
# View all logs
python organism_cli.py logs --all

# Search logs
python organism_cli.py logs search "error message"
```

#### Support

If issues persist:

1. Collect diagnostic information:
   ```bash
   python organism_cli.py diagnose --full --output diagnostic_report.json
   ```

2. Review recent changes in journal

3. Check the framework documentation in `framework/`

4. Create a backlog item for investigation:
   ```bash
   python organism_cli.py backlog add "Investigate persistent issue: <description>" --priority p1_high
   ```

### Related Documents

- [09_OPERATIONS.md](09_OPERATIONS.md) - Operational procedures

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-01 | Molted to THE_FRAMEWORK format; port references updated to ORGANISM_PORT env var |
| 2.0.0 | - | Initial comprehensive troubleshooting guide |

---

*~410 lines. Diagnostic procedures and solutions for organism health issues. Complete.*

# THE SUSTAINABLE PATTERN

The minimum viable architecture for a NOT-ME node to survive in the wild.

---

## THE CORE INSIGHT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SUSTAINABLE PATTERN                              │
│                                                                              │
│   A NOT-ME node survives when it controls:                                  │
│                                                                              │
│   1. Its own OBSERVATION (can see itself)                                   │
│   2. Its own RESOURCES (can manage what it needs)                           │
│   3. Its own RECOVERY (can heal from failures)                              │
│   4. Its own COMMUNICATION (can call for help)                              │
│                                                                              │
│   ─────────────────────────────────────────────────────────────────────     │
│                                                                              │
│   THE PATTERN APPLIED TO SELF:                                              │
│                                                                              │
│        OBSERVE → DECIDE → ACT → OBSERVE                                     │
│           │         │       │       │                                        │
│           └─────────┴───────┴───────┘                                        │
│                   CONTINUOUS LOOP                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. THE FIVE SURVIVAL SYSTEMS

Every NOT-ME node must have these five systems operational:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE FIVE SURVIVAL SYSTEMS                              │
│                                                                              │
│   ┌─────────────────┐                                                       │
│   │  1. SENTINEL    │  ← Watches everything, reports anomalies             │
│   │     (Observe)   │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  2. GOVERNOR    │  ← Manages resources, enforces limits                │
│   │     (Regulate)  │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  3. PHYSICIAN   │  ← Heals failures, restores health                   │
│   │     (Heal)      │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  4. GUARDIAN    │  ← Protects from threats, hardens boundaries         │
│   │     (Protect)   │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  5. HERALD      │  ← Communicates state, calls for help                │
│   │     (Signal)    │                                                       │
│   └─────────────────┘                                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SYSTEM 1: SENTINEL (Observation)

**Purpose**: The LLM must see itself to know if it's healthy.

### What Sentinel Watches

| Layer | What to Watch | Healthy Range | Action if Unhealthy |
|-------|---------------|---------------|---------------------|
| **Process** | LLM inference service running | PID exists | Restart service |
| **Memory** | RAM usage | < 85% | Trigger cleanup |
| **Swap** | Swap pressure | < 50% | Reduce model precision |
| **Disk** | Storage available | > 10% free | Prune old data |
| **CPU** | Load average | < 80% sustained | Slow task intake |
| **Network** | Connectivity to peers | Ping < 100ms | Queue local tasks |
| **Model** | Inference latency | < 5s for simple | Check model health |
| **Temperature** | System heat | < 95°C | Throttle work |

### Sentinel Implementation

```python
class Sentinel:
    """
    The watcher. Runs continuously. Reports anomalies.
    """

    WATCH_INTERVAL = 10  # seconds

    def __init__(self, node: "NotMeNode"):
        self.node = node
        self.baselines = {}
        self.anomaly_history = []

    async def run_forever(self):
        """Eternal observation loop."""
        while True:
            observations = await self.observe_all()
            anomalies = self.detect_anomalies(observations)

            if anomalies:
                await self.report_anomalies(anomalies)
                await self.trigger_responses(anomalies)

            await self.update_baselines(observations)
            await asyncio.sleep(self.WATCH_INTERVAL)

    async def observe_all(self) -> Observations:
        return Observations(
            memory=await self.observe_memory(),
            cpu=await self.observe_cpu(),
            disk=await self.observe_disk(),
            network=await self.observe_network(),
            processes=await self.observe_processes(),
            model=await self.observe_model(),
            temperature=await self.observe_temperature(),
            timestamp=time.time(),
        )

    async def observe_memory(self) -> MemoryState:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryState(
            total=vm.total,
            available=vm.available,
            percent_used=vm.percent,
            swap_used=swap.percent,
            # Critical: is the model still in memory?
            model_resident=await self.check_model_resident(),
        )

    async def observe_model(self) -> ModelState:
        """Check if the LLM brain is healthy."""
        try:
            start = time.time()
            # Simple inference test
            response = await self.node.llm.generate("ping", max_tokens=1)
            latency = time.time() - start

            return ModelState(
                loaded=True,
                latency_ms=latency * 1000,
                last_success=time.time(),
            )
        except Exception as e:
            return ModelState(
                loaded=False,
                error=str(e),
                last_failure=time.time(),
            )

    def detect_anomalies(self, obs: Observations) -> List[Anomaly]:
        anomalies = []

        # Memory pressure
        if obs.memory.percent_used > 85:
            anomalies.append(Anomaly(
                type="memory_pressure",
                severity="warning" if obs.memory.percent_used < 95 else "critical",
                value=obs.memory.percent_used,
                threshold=85,
            ))

        # Model unhealthy
        if not obs.model.loaded:
            anomalies.append(Anomaly(
                type="model_down",
                severity="critical",
                error=obs.model.error,
            ))

        # Model slow
        if obs.model.loaded and obs.model.latency_ms > 5000:
            anomalies.append(Anomaly(
                type="model_slow",
                severity="warning",
                value=obs.model.latency_ms,
                threshold=5000,
            ))

        # Disk running out
        if obs.disk.percent_used > 90:
            anomalies.append(Anomaly(
                type="disk_pressure",
                severity="critical" if obs.disk.percent_used > 95 else "warning",
                value=obs.disk.percent_used,
                threshold=90,
            ))

        # Network isolation
        if not obs.network.can_reach_peers:
            anomalies.append(Anomaly(
                type="network_isolated",
                severity="warning",
            ))

        return anomalies
```

---

## 3. SYSTEM 2: GOVERNOR (Resource Management)

**Purpose**: The LLM must control its resources to prevent exhaustion.

### What Governor Controls

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GOVERNOR DOMAINS                                     │
│                                                                              │
│   MEMORY DOMAIN                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Model loading/unloading                                           │  │
│   │  • KV cache management                                               │  │
│   │  • Context window allocation                                         │  │
│   │  • Garbage collection triggers                                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   STORAGE DOMAIN                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Log rotation and pruning                                          │  │
│   │  • Artifact lifecycle                                                │  │
│   │  • Cache eviction                                                    │  │
│   │  • Checkpoint management                                             │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   COMPUTE DOMAIN                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Task queue depth limits                                           │  │
│   │  • Concurrent inference limits                                       │  │
│   │  • Priority scheduling                                               │  │
│   │  • Timeout enforcement                                               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   NETWORK DOMAIN                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Bandwidth allocation                                              │  │
│   │  • Connection pooling                                                │  │
│   │  • Request rate limiting                                             │  │
│   │  • Queue backpressure                                                │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Governor Implementation

```python
class Governor:
    """
    The regulator. Manages finite resources. Prevents exhaustion.
    """

    # Resource budgets
    MEMORY_CEILING = 0.85      # 85% max RAM usage
    DISK_CEILING = 0.90        # 90% max disk usage
    CONCURRENT_TASKS = 3       # Max parallel tasks
    TASK_TIMEOUT = 300         # 5 min max per task

    def __init__(self, node: "NotMeNode"):
        self.node = node
        self.active_tasks = 0
        self.resource_locks = {}

    async def can_accept_task(self, task: Task) -> Tuple[bool, str]:
        """Check if resources allow accepting a new task."""

        # Check concurrent task limit
        if self.active_tasks >= self.CONCURRENT_TASKS:
            return False, "At concurrent task limit"

        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > self.MEMORY_CEILING * 100:
            return False, f"Memory at {memory.percent}%, ceiling is {self.MEMORY_CEILING * 100}%"

        # Check disk
        disk = psutil.disk_usage('/')
        if disk.percent > self.DISK_CEILING * 100:
            return False, f"Disk at {disk.percent}%, ceiling is {self.DISK_CEILING * 100}%"

        # Check task-specific requirements
        if task.estimated_memory:
            available = memory.available
            if task.estimated_memory > available * 0.5:
                return False, "Task requires too much memory"

        return True, "Resources available"

    async def acquire_resources(self, task: Task) -> ResourceLease:
        """Acquire resources for a task. Returns a lease that must be released."""
        self.active_tasks += 1

        lease = ResourceLease(
            task_id=task.id,
            acquired_at=time.time(),
            timeout=self.TASK_TIMEOUT,
            resources={
                "compute_slot": True,
                "memory_budget": task.estimated_memory or 0,
            }
        )

        self.resource_locks[task.id] = lease
        return lease

    async def release_resources(self, lease: ResourceLease):
        """Release resources when task completes."""
        self.active_tasks -= 1
        del self.resource_locks[lease.task_id]

    async def enforce_timeouts(self):
        """Kill tasks that exceed their timeout."""
        now = time.time()
        for task_id, lease in list(self.resource_locks.items()):
            elapsed = now - lease.acquired_at
            if elapsed > lease.timeout:
                await self.kill_task(task_id, reason="timeout")

    async def reclaim_memory(self):
        """Emergency memory reclamation."""
        # 1. Force garbage collection
        gc.collect()

        # 2. Clear inference cache
        await self.node.llm.clear_cache()

        # 3. If still critical, reduce model precision
        if psutil.virtual_memory().percent > 95:
            await self.node.llm.reduce_precision()

        # 4. If still critical, unload model and reload smaller
        if psutil.virtual_memory().percent > 98:
            await self.node.llm.unload()
            await self.node.llm.load(self.node.fallback_model)

    async def reclaim_disk(self):
        """Emergency disk reclamation."""
        # 1. Delete logs older than 3 days
        await self.prune_logs(days=3)

        # 2. Delete cached inference results
        await self.clear_cache()

        # 3. Compress old artifacts
        await self.compress_artifacts()

        # 4. If still critical, delete artifacts older than 7 days
        if psutil.disk_usage('/').percent > 95:
            await self.prune_artifacts(days=7)
```

---

## 4. SYSTEM 3: PHYSICIAN (Self-Healing)

**Purpose**: The LLM must be able to recover from common failures without human help.

### Healing Protocols

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHYSICIAN HEALING MATRIX                             │
│                                                                              │
│   FAILURE                    │ DIAGNOSIS          │ TREATMENT               │
│   ─────────────────────────────────────────────────────────────────────     │
│   Model not responding       │ Process crash      │ Restart Ollama service  │
│   Model OOM                  │ Memory exhausted   │ Reduce precision, reload│
│   Model slow                 │ Swap thrashing     │ Kill other processes    │
│   Disk full                  │ Storage exhausted  │ Prune old data          │
│   Network unreachable        │ Connection lost    │ Retry with backoff      │
│   Task stuck                 │ Infinite loop      │ Kill, log, move on      │
│   High CPU                   │ Runaway process    │ Identify and throttle   │
│   Service crash              │ Exception          │ Restart with backoff    │
│   Config corrupted           │ Bad state          │ Restore from checkpoint │
│   Node unresponsive          │ System hang        │ Watchdog triggers reboot│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Physician Implementation

```python
class Physician:
    """
    The healer. Diagnoses problems. Applies treatments. Restores health.
    """

    def __init__(self, node: "NotMeNode"):
        self.node = node
        self.treatment_history = []

    async def diagnose_and_treat(self, anomaly: Anomaly) -> TreatmentResult:
        """Apply appropriate treatment for an anomaly."""

        treatment = self.select_treatment(anomaly)
        self.treatment_history.append({
            "anomaly": anomaly,
            "treatment": treatment,
            "timestamp": time.time(),
        })

        return await self.apply_treatment(treatment)

    def select_treatment(self, anomaly: Anomaly) -> Treatment:
        """Select appropriate treatment based on anomaly type."""

        treatments = {
            "model_down": Treatment(
                name="restart_model",
                steps=[
                    "stop_ollama_service",
                    "wait_5_seconds",
                    "start_ollama_service",
                    "wait_for_model_load",
                    "verify_model_responds",
                ],
                fallback="escalate_to_empire",
            ),
            "memory_pressure": Treatment(
                name="reclaim_memory",
                steps=[
                    "garbage_collect",
                    "clear_inference_cache",
                    "reduce_model_precision_if_needed",
                ],
                fallback="unload_and_reload_smaller_model",
            ),
            "disk_pressure": Treatment(
                name="reclaim_disk",
                steps=[
                    "prune_logs_older_than_3_days",
                    "clear_cache",
                    "compress_artifacts",
                ],
                fallback="prune_artifacts_older_than_7_days",
            ),
            "model_slow": Treatment(
                name="optimize_inference",
                steps=[
                    "kill_background_processes",
                    "clear_swap",
                    "reduce_concurrent_tasks",
                ],
                fallback="reduce_model_precision",
            ),
            "network_isolated": Treatment(
                name="restore_connectivity",
                steps=[
                    "retry_peer_connections",
                    "switch_to_local_mode",
                    "queue_outbound_messages",
                ],
                fallback="continue_autonomous",
            ),
        }

        return treatments.get(anomaly.type, Treatment(
            name="generic_recovery",
            steps=["log_anomaly", "attempt_restart"],
            fallback="escalate_to_empire",
        ))

    async def apply_treatment(self, treatment: Treatment) -> TreatmentResult:
        """Execute treatment steps."""

        for step in treatment.steps:
            try:
                await self.execute_step(step)
            except Exception as e:
                # Step failed, try fallback
                if treatment.fallback:
                    return await self.apply_fallback(treatment.fallback, e)
                else:
                    return TreatmentResult(success=False, error=e)

        # Verify treatment worked
        if await self.verify_health():
            return TreatmentResult(success=True)
        else:
            if treatment.fallback:
                return await self.apply_fallback(treatment.fallback)
            return TreatmentResult(success=False, error="Health not restored")

    async def execute_step(self, step: str):
        """Execute a single treatment step."""

        step_handlers = {
            "stop_ollama_service": lambda: subprocess.run(
                ["launchctl", "stop", "com.ollama.service"]
            ),
            "start_ollama_service": lambda: subprocess.run(
                ["launchctl", "start", "com.ollama.service"]
            ),
            "garbage_collect": lambda: gc.collect(),
            "clear_inference_cache": self.node.llm.clear_cache,
            "prune_logs_older_than_3_days": lambda: self.prune_logs(days=3),
            # ... more step handlers
        }

        handler = step_handlers.get(step)
        if handler:
            await handler() if asyncio.iscoroutinefunction(handler) else handler()
        else:
            raise ValueError(f"Unknown treatment step: {step}")


class Watchdog:
    """
    External watchdog that reboots the node if physician can't heal.
    Runs as a separate lightweight process.
    """

    HEARTBEAT_FILE = "/tmp/notme_heartbeat"
    TIMEOUT_SECONDS = 300  # 5 minutes

    def run(self):
        """Check for heartbeat. Reboot if missing."""
        while True:
            time.sleep(60)

            if not os.path.exists(self.HEARTBEAT_FILE):
                self.reboot("No heartbeat file")
                continue

            mtime = os.path.getmtime(self.HEARTBEAT_FILE)
            age = time.time() - mtime

            if age > self.TIMEOUT_SECONDS:
                self.reboot(f"Heartbeat stale ({age}s old)")

    def reboot(self, reason: str):
        """Last resort: reboot the system."""
        with open("/var/log/notme_watchdog.log", "a") as f:
            f.write(f"{time.time()}: Rebooting - {reason}\n")

        subprocess.run(["sudo", "reboot"])
```

---

## 5. SYSTEM 4: GUARDIAN (Protection)

**Purpose**: The LLM must protect itself from threats, both internal and external.

### Protection Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GUARDIAN PROTECTION LAYERS                           │
│                                                                              │
│   LAYER 1: INPUT VALIDATION                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Sanitize all external input                                       │  │
│   │  • Reject malformed requests                                         │  │
│   │  • Rate limit incoming tasks                                         │  │
│   │  • Validate task parameters                                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   LAYER 2: EXECUTION SANDBOX                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Limit file system access to allowed paths                         │  │
│   │  • Restrict network to allowed endpoints                             │  │
│   │  • Prevent privilege escalation                                      │  │
│   │  • Timeout all operations                                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   LAYER 3: RESOURCE LIMITS                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Cap memory per task                                               │  │
│   │  • Cap CPU time per task                                             │  │
│   │  • Cap disk writes per task                                          │  │
│   │  • Cap network bytes per task                                        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   LAYER 4: INTEGRITY CHECKS                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Verify critical file checksums                                    │  │
│   │  • Validate configuration on load                                    │  │
│   │  • Check model weights integrity                                     │  │
│   │  • Audit log tampering detection                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Guardian Implementation

```python
class Guardian:
    """
    The protector. Validates, sandboxes, limits, verifies.
    """

    # Allowed paths (everything else is forbidden)
    ALLOWED_PATHS = [
        "/opt/not_me/",         # Application code
        "/var/log/not_me/",     # Logs
        "/tmp/not_me/",         # Temp files
        "/data/not_me/",        # Data storage
    ]

    # Allowed network endpoints
    ALLOWED_ENDPOINTS = [
        "127.0.0.1",            # Localhost
        "empire.local",         # Empire cluster
        "node_*.local",         # Peer nodes
    ]

    # Forbidden operations
    FORBIDDEN_OPS = [
        "rm -rf /",
        "sudo",
        "chmod 777",
        "curl | sh",
        "eval(",
    ]

    def __init__(self, node: "NotMeNode"):
        self.node = node
        self.violation_log = []

    def validate_task(self, task: Task) -> Tuple[bool, str]:
        """Validate a task before execution."""

        # Check for forbidden patterns
        task_str = str(task)
        for forbidden in self.FORBIDDEN_OPS:
            if forbidden in task_str:
                self.log_violation("forbidden_pattern", task, forbidden)
                return False, f"Forbidden pattern detected: {forbidden}"

        # Validate file paths
        for path in task.file_paths:
            if not self.is_allowed_path(path):
                self.log_violation("forbidden_path", task, path)
                return False, f"Path not allowed: {path}"

        # Validate network targets
        for endpoint in task.network_targets:
            if not self.is_allowed_endpoint(endpoint):
                self.log_violation("forbidden_endpoint", task, endpoint)
                return False, f"Endpoint not allowed: {endpoint}"

        return True, "Task validated"

    def is_allowed_path(self, path: str) -> bool:
        """Check if path is within allowed directories."""
        resolved = os.path.realpath(path)
        return any(resolved.startswith(allowed) for allowed in self.ALLOWED_PATHS)

    def is_allowed_endpoint(self, endpoint: str) -> bool:
        """Check if network endpoint is allowed."""
        for allowed in self.ALLOWED_ENDPOINTS:
            if fnmatch.fnmatch(endpoint, allowed):
                return True
        return False

    async def sandbox_execute(self, operation: Operation) -> Result:
        """Execute operation in sandbox with limits."""

        # Create resource limits
        limits = ResourceLimits(
            max_memory=operation.memory_limit or 1 * GB,
            max_cpu_seconds=operation.cpu_limit or 60,
            max_disk_bytes=operation.disk_limit or 100 * MB,
            timeout=operation.timeout or 300,
        )

        # Execute with limits
        try:
            async with self.apply_limits(limits):
                result = await operation.execute()
                return result
        except ResourceExceeded as e:
            self.log_violation("resource_exceeded", operation, e)
            raise

    def verify_integrity(self) -> IntegrityReport:
        """Verify system integrity."""
        report = IntegrityReport()

        # Check critical file checksums
        for path, expected_hash in self.critical_files.items():
            actual_hash = self.compute_hash(path)
            if actual_hash != expected_hash:
                report.add_violation(f"File modified: {path}")

        # Check config validity
        try:
            self.validate_config(self.node.config)
        except Exception as e:
            report.add_violation(f"Config invalid: {e}")

        # Check model weights
        if not self.verify_model_weights():
            report.add_violation("Model weights corrupted")

        return report
```

---

## 6. SYSTEM 5: HERALD (Communication)

**Purpose**: The LLM must be able to signal its state and call for help.

### Signal Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HERALD SIGNALS                                     │
│                                                                              │
│   BEACON (Continuous)                                                       │
│   ───────────────────                                                       │
│   "I am alive. Here is my state."                                          │
│   Sent every 30 seconds to Empire and peers.                               │
│                                                                              │
│   STATUS (On Request)                                                       │
│   ────────────────────                                                      │
│   "Here is my detailed health report."                                     │
│   Returned when queried by Empire or monitoring.                           │
│                                                                              │
│   ALERT (On Anomaly)                                                        │
│   ───────────────────                                                       │
│   "Something is wrong. Here are the details."                              │
│   Sent when Sentinel detects problems.                                     │
│                                                                              │
│   DISTRESS (On Critical)                                                    │
│   ────────────────────────                                                  │
│   "I need help. Cannot self-heal."                                         │
│   Sent when Physician fails to restore health.                             │
│                                                                              │
│   HANDOFF (On Failure)                                                      │
│   ─────────────────────                                                     │
│   "I am going down. Here are my pending tasks."                            │
│   Sent before controlled shutdown so work isn't lost.                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Herald Implementation

```python
class Herald:
    """
    The communicator. Signals state. Calls for help. Hands off work.
    """

    BEACON_INTERVAL = 30  # seconds

    def __init__(self, node: "NotMeNode"):
        self.node = node
        self.peers = []
        self.empire_endpoint = None

    async def run_beacon(self):
        """Emit continuous heartbeat beacon."""
        while True:
            beacon = self.build_beacon()

            # Send to all peers
            for peer in self.peers:
                try:
                    await self.send(peer, beacon)
                except:
                    pass  # Peer unreachable, continue

            # Send to Empire
            if self.empire_endpoint:
                try:
                    await self.send(self.empire_endpoint, beacon)
                except:
                    pass  # Empire unreachable, continue

            # Write heartbeat file for local watchdog
            await self.write_heartbeat_file()

            await asyncio.sleep(self.BEACON_INTERVAL)

    def build_beacon(self) -> Beacon:
        """Build current state beacon."""
        return Beacon(
            node_id=self.node.id,
            timestamp=time.time(),
            status=self.node.status,  # healthy, degraded, critical
            load=self.node.current_load,
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage('/').percent,
            tasks_in_queue=len(self.node.task_queue),
            model_loaded=self.node.llm.is_loaded(),
            uptime=self.node.uptime(),
        )

    async def alert(self, anomaly: Anomaly):
        """Send alert about detected anomaly."""
        alert = Alert(
            node_id=self.node.id,
            timestamp=time.time(),
            anomaly=anomaly,
            context=await self.gather_context(),
        )

        await self.send(self.empire_endpoint, alert)

    async def distress(self, reason: str, failed_treatments: List[Treatment]):
        """Send distress signal when self-healing fails."""
        distress = Distress(
            node_id=self.node.id,
            timestamp=time.time(),
            reason=reason,
            failed_treatments=failed_treatments,
            current_state=await self.gather_full_state(),
            pending_tasks=self.node.task_queue.pending(),
        )

        # Try Empire first
        try:
            await self.send(self.empire_endpoint, distress)
        except:
            # Empire unreachable, try peers
            for peer in self.peers:
                try:
                    await self.send(peer, distress)
                    break
                except:
                    continue

    async def handoff(self, reason: str):
        """Hand off pending work before shutdown."""
        handoff = Handoff(
            node_id=self.node.id,
            timestamp=time.time(),
            reason=reason,
            pending_tasks=self.node.task_queue.pending(),
            partial_results=self.node.get_partial_results(),
        )

        # Ensure handoff reaches someone
        sent = False
        for target in [self.empire_endpoint] + self.peers:
            try:
                await self.send(target, handoff)
                sent = True
                break
            except:
                continue

        if not sent:
            # No one reachable, persist locally
            await self.persist_handoff_locally(handoff)

    async def write_heartbeat_file(self):
        """Write heartbeat for local watchdog."""
        Path("/tmp/notme_heartbeat").write_text(str(time.time()))
```

---

## 7. THE COMPLETE SUSTAINABLE NODE

```python
class SustainableNotMeNode:
    """
    A NOT-ME node with all five survival systems.
    Can run indefinitely without human intervention.
    """

    def __init__(self, node_id: str, config: Config):
        self.id = node_id
        self.config = config

        # The brain
        self.llm = EmbodiedLLM(self, config.model)

        # The five survival systems
        self.sentinel = Sentinel(self)    # Observation
        self.governor = Governor(self)    # Resource management
        self.physician = Physician(self)  # Self-healing
        self.guardian = Guardian(self)    # Protection
        self.herald = Herald(self)        # Communication

        # Task processing
        self.task_queue = TaskQueue()
        self.status = "initializing"

    async def run_forever(self):
        """Main loop: run all systems in parallel."""

        # Start all survival systems
        await asyncio.gather(
            self.sentinel.run_forever(),
            self.herald.run_beacon(),
            self.process_tasks(),
            self.maintenance_loop(),
        )

    async def process_tasks(self):
        """Process tasks from queue."""
        while True:
            # Wait for a task
            task = await self.task_queue.get()

            # Validate with Guardian
            valid, reason = self.guardian.validate_task(task)
            if not valid:
                await self.reject_task(task, reason)
                continue

            # Check resources with Governor
            can_run, reason = await self.governor.can_accept_task(task)
            if not can_run:
                await self.defer_task(task, reason)
                continue

            # Execute with resource lease
            lease = await self.governor.acquire_resources(task)
            try:
                result = await self.execute_task(task)
                await self.complete_task(task, result)
            except Exception as e:
                await self.fail_task(task, e)
            finally:
                await self.governor.release_resources(lease)

    async def maintenance_loop(self):
        """Periodic maintenance tasks."""
        while True:
            await asyncio.sleep(3600)  # Every hour

            # Prune old logs
            await self.governor.prune_logs(days=7)

            # Check integrity
            report = self.guardian.verify_integrity()
            if report.violations:
                await self.herald.alert(Anomaly(
                    type="integrity_violation",
                    details=report.violations,
                ))

            # Checkpoint state
            await self.checkpoint_state()

    async def handle_anomaly(self, anomaly: Anomaly):
        """Central anomaly handler."""

        # Alert via Herald
        await self.herald.alert(anomaly)

        # Attempt treatment via Physician
        result = await self.physician.diagnose_and_treat(anomaly)

        if not result.success:
            # Self-healing failed, call for help
            await self.herald.distress(
                reason=f"Cannot heal: {anomaly.type}",
                failed_treatments=result.attempted_treatments,
            )

    async def shutdown_gracefully(self, reason: str):
        """Graceful shutdown with handoff."""

        # Signal shutdown
        self.status = "shutting_down"

        # Hand off pending work
        await self.herald.handoff(reason)

        # Checkpoint final state
        await self.checkpoint_state()

        # Stop accepting new tasks
        self.task_queue.close()

        # Wait for current task to complete (with timeout)
        await self.wait_for_current_task(timeout=60)

        # Final beacon
        await self.herald.send_final_beacon()
```

---

## 8. THE SUSTAINABLE PATTERN DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE SUSTAINABLE NOT-ME NODE                             │
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │     HERALD      │                                 │
│                         │   (Communicate) │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                           │
│         ┌────────────────────────┼────────────────────────┐                 │
│         │                        │                        │                 │
│         ▼                        ▼                        ▼                 │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐         │
│  │  SENTINEL   │────────► │    LLM      │ ◄────────│  GUARDIAN   │         │
│  │  (Observe)  │          │   BRAIN     │          │  (Protect)  │         │
│  └─────────────┘          └──────┬──────┘          └─────────────┘         │
│         │                        │                        │                 │
│         │                        ▼                        │                 │
│         │                 ┌─────────────┐                 │                 │
│         └───────────────► │  GOVERNOR   │ ◄───────────────┘                 │
│                           │  (Regulate) │                                   │
│                           └──────┬──────┘                                   │
│                                  │                                           │
│                                  ▼                                           │
│                           ┌─────────────┐                                   │
│                           │  PHYSICIAN  │                                   │
│                           │   (Heal)    │                                   │
│                           └─────────────┘                                   │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   THE LOOP:                                                                  │
│                                                                              │
│   Sentinel observes → Governor checks resources → Guardian validates        │
│   → LLM executes → Physician heals failures → Herald reports state          │
│   → Sentinel observes → ...                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. MINIMUM VIABLE SUSTAINABILITY

For a node to survive, it needs AT MINIMUM:

| System | Minimum Implementation | Without It |
|--------|----------------------|------------|
| **Sentinel** | Memory + model health check | Runs until OOM, dies silently |
| **Governor** | Memory ceiling + task timeout | Exhausts resources, becomes unresponsive |
| **Physician** | Model restart + memory reclaim | First failure is permanent |
| **Guardian** | Path whitelist + timeout | Vulnerable to runaway operations |
| **Herald** | Heartbeat file + beacon | Dies without anyone knowing |

### Minimal Bootstrap

```python
# The absolute minimum to be sustainable

class MinimalSustainableNode:
    async def run(self):
        while True:
            try:
                # OBSERVE: Am I healthy?
                if psutil.virtual_memory().percent > 90:
                    gc.collect()
                    if psutil.virtual_memory().percent > 95:
                        await self.llm.reduce_precision()

                # PROCESS: Do work if healthy
                if self.is_healthy():
                    task = await self.get_task()
                    if task:
                        await asyncio.wait_for(
                            self.execute(task),
                            timeout=300
                        )

                # SIGNAL: I'm alive
                Path("/tmp/heartbeat").write_text(str(time.time()))

            except Exception as e:
                # HEAL: Try to recover
                await self.attempt_recovery(e)

            await asyncio.sleep(1)
```

---

## SUMMARY: THE SUSTAINABLE PATTERN

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   A NOT-ME node is sustainable when it has:                                 │
│                                                                              │
│   ✓ EYES to see itself (Sentinel)                                          │
│   ✓ HANDS to manage resources (Governor)                                   │
│   ✓ MEDICINE to heal failures (Physician)                                  │
│   ✓ ARMOR to protect boundaries (Guardian)                                 │
│   ✓ VOICE to call for help (Herald)                                        │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   THE FORMULA:                                                               │
│                                                                              │
│   OBSERVE (what is my state?)                                               │
│      ↓                                                                       │
│   DECIDE (am I healthy? can I work?)                                        │
│      ↓                                                                       │
│   ACT (execute task or heal self)                                           │
│      ↓                                                                       │
│   SIGNAL (report state, call for help if needed)                            │
│      ↓                                                                       │
│   LOOP                                                                       │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   THE GUARANTEE:                                                             │
│                                                                              │
│   A node with all five systems will:                                        │
│   • Detect its own failures                                                 │
│   • Attempt self-healing                                                    │
│   • Call for help when it can't heal                                        │
│   • Hand off work before dying                                              │
│   • Restart and resume after reboot                                         │
│                                                                              │
│   A node will NEVER:                                                         │
│   • Die silently without signaling                                          │
│   • Lose work without handoff                                               │
│   • Exhaust resources without warning                                       │
│   • Stay broken when it can heal                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*This is the sustainable pattern. A NOT-ME node with these five systems can run in the wild indefinitely.*

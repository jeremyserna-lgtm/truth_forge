# Profiling

**Measure first. Guess never.**

---

## The Rule

Never optimize without profiling. Intuition about bottlenecks is usually wrong.

---

## The Profiling Process

```
1. Establish baseline
   ↓
2. Identify bottleneck (profile)
   ↓
3. Form hypothesis
   ↓
4. Make targeted change
   ↓
5. Measure improvement
   ↓
6. Repeat or ship
```

---

## Python Profiling Tools

| Tool | Use For |
|------|---------|
| `cProfile` | Function-level CPU profiling |
| `line_profiler` | Line-by-line profiling |
| `memory_profiler` | Memory usage |
| `py-spy` | Production sampling profiler |
| `snakeviz` | Visualize cProfile output |

---

## Quick Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('my_function()', 'output.prof')

# View results
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

---

## Timing Critical Sections

```python
import time
from contextlib import contextmanager
from typing import Generator

@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.3f}s")

# Usage
with timer("database query"):
    results = db.query(...)
```

---

## Structured Performance Logging

```python
import structlog
import time

logger = structlog.get_logger()

def process_batch(batch: list) -> list:
    start = time.perf_counter()
    result = [process(item) for item in batch]
    elapsed_ms = (time.perf_counter() - start) * 1000

    logger.info("batch_processed", extra={
        "batch_size": len(batch),
        "duration_ms": elapsed_ms,
        "items_per_second": len(batch) / (elapsed_ms / 1000)
    })
    return result
```

---

## What to Measure

| Metric | Why |
|--------|-----|
| Response time (p50, p95, p99) | User experience |
| Throughput (req/sec) | Capacity |
| CPU usage | Compute cost |
| Memory usage | Resource limits |
| I/O wait | Bottleneck identification |

---

## Production Profiling

```bash
# py-spy - attach to running process
py-spy top --pid 12345

# Generate flame graph
py-spy record -o profile.svg --pid 12345
```

---

## Anti-Patterns

```python
# WRONG - Optimizing without measurement
# "I think this loop is slow"
for item in items:
    optimized_but_untested_code()

# WRONG - Micro-benchmarking in isolation
# Benchmarking a function that's called once

# WRONG - Ignoring statistical variance
# "It was faster that one time"
```

---

## UP

[INDEX.md](INDEX.md)

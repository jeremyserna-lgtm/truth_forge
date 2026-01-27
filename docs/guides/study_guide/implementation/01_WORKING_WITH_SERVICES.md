# Working with Services

**Layer**: Reference (HOW)
**Purpose**: Learn to use central services in your code

---

## 🎓 LEARNING: The Service Pattern

All services in Truth Engine follow the same pattern:

```python
# Get the service
service = get_service_name()

# Push data in (exhale)
result = service.exhale(content="...", **kwargs)

# Pull data out (inhale)
data = service.inhale(query="...", limit=100)
```

**Why this matters**: Once you learn one service, you understand them all.

---

## 💡 CONCEPT: Exhale and Inhale

### Exhale: Push Data In

**What it does**: Takes raw data and processes it through The Structure (HOLD₁ → AGENT → HOLD₂).

**Returns**: A result dictionary with:
- `id`: The unique identifier of the created record
- `status`: Success or error status
- `details`: Additional information

**Example**:
```python
knowledge_service = get_knowledge_service()
result = knowledge_service.exhale(
    content="Jeremy builds Truth Engine.",
    source_name="conversation"
)

print(result['id'])  # atom:abc12345
print(result['status'])  # success
```

### Inhale: Pull Data Out

**What it does**: Queries the canonical store (HOLD₃) for data.

**Returns**: A list of records matching the query.

**Example**:
```python
knowledge_service = get_knowledge_service()
atoms = knowledge_service.inhale(
    query="Truth Engine",
    limit=10
)

for atom in atoms:
    print(atom['content'])
```

---

## 🎯 PRACTICE: Your First Service Call

### Step 1: Import the Service

```python
from src.services.central_services.knowledge_service.knowledge_service import get_knowledge_service
```

### Step 2: Get the Service Instance

```python
knowledge_service = get_knowledge_service()
```

### Step 3: Add Governance

```python
from architect_central_services.core import get_logger, get_current_run_id

run_id = get_current_run_id()
logger = get_logger(__name__)

logger.info("Starting knowledge extraction", extra={
    'run_id': run_id,
    'component': __name__,
    'operation': 'extract_knowledge'
})
```

### Step 4: Exhale Data

```python
result = knowledge_service.exhale(
    content="This is a test knowledge atom.",
    source_name="test_script"
)

logger.info("Knowledge atom created", extra={
    'run_id': run_id,
    'atom_id': result['id'],
    'status': result['status']
})
```

### Step 5: Inhale Data

```python
atoms = knowledge_service.inhale(
    query="test",
    limit=10
)

logger.info("Found knowledge atoms", extra={
    'run_id': run_id,
    'count': len(atoms)
})
```

---

## Complete Example: Knowledge Service

```python
#!/usr/bin/env python3
"""
Example: Working with KnowledgeService
"""

from architect_central_services.core import get_logger, get_current_run_id
from src.services.central_services.knowledge_service.knowledge_service import get_knowledge_service

def main():
    # Initialize
    run_id = get_current_run_id()
    logger = get_logger(__name__)
    knowledge_service = get_knowledge_service()

    logger.info("Starting knowledge service example", extra={
        'run_id': run_id,
        'component': __name__
    })

    # Exhale: Add knowledge
    content = "Truth Engine is a system for transforming raw data into structured truth."
    result = knowledge_service.exhale(
        content=content,
        source_name="example_script"
    )

    logger.info("Knowledge atom created", extra={
        'run_id': run_id,
        'atom_id': result.get('id'),
        'status': result.get('status')
    })

    # Inhale: Query knowledge
    atoms = knowledge_service.inhale(
        query="Truth Engine",
        limit=5
    )

    logger.info("Found knowledge atoms", extra={
        'run_id': run_id,
        'count': len(atoms)
    })

    for atom in atoms:
        logger.info("Atom", extra={
            'run_id': run_id,
            'atom_id': atom.get('atom_id'),
            'content': atom.get('content')[:100]  # First 100 chars
        })

if __name__ == "__main__":
    main()
```

---

## ⚠️ WARNING: Common Mistakes

### 1. Not Handling Errors

**Don't do this:**
```python
result = service.exhale(content="...")  # ❌ BAD: No error handling
```

**Do this instead:**
```python
try:
    result = service.exhale(content="...")
    if result.get('status') != 'success':
        logger.error("Service returned error", extra={'result': result})
except Exception as e:
    logger.error("Service call failed", extra={'error': str(e)})
    raise
```

### 2. Not Adding Governance

**Don't do this:**
```python
atoms = service.inhale(query="...")  # ❌ BAD: No logging, no traceability
```

**Do this instead:**
```python
run_id = get_current_run_id()
logger = get_logger(__name__)

logger.info("Querying service", extra={
    'run_id': run_id,
    'query': query
})

atoms = service.inhale(query=query, limit=limit)

logger.info("Query completed", extra={
    'run_id': run_id,
    'count': len(atoms)
})
```

### 3. Not Understanding the Data Flow

**Don't do this:**
```python
# Expecting immediate availability after exhale
result = service.exhale(content="...")
atoms = service.inhale(query="...")  # ❌ May not find it yet!
```

**Do this instead:**
```python
# Exhale processes through HOLD₁ → AGENT → HOLD₂ → HOLD₃
# This takes time. Check status or wait for sync.
result = service.exhale(content="...")
if result.get('status') == 'success':
    # May need to wait for sync to HOLD₃
    time.sleep(1)  # Or use proper sync mechanism
    atoms = service.inhale(query="...")
```

---

## 🚀 MOMENTUM: Service Best Practices

1. **Always add governance** - Logging, traceability, error handling
2. **Check return values** - Services return status information
3. **Handle errors gracefully** - Services can fail
4. **Understand the data flow** - HOLD₁ → AGENT → HOLD₂ → HOLD₃ takes time
5. **Use the canonical interface** - Don't bypass services

---

## 📚 Next Steps

Now that you can use services, read:
- **[Writing Scripts](./02_WRITING_SCRIPTS.md)** - How to write scripts that follow The Structure
- **[Governance Integration](./03_GOVERNANCE_INTEGRATION.md)** - How to add governance to your code

---

**Remember**: Services are the concrete expression of The Framework. Using them correctly means following The Structure and The Cycle.

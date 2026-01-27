# Database

**Index your queries. Avoid N+1. Measure query time.**

---

## The Rule

Database operations are usually the bottleneck. Optimize queries, not code.

---

## The N+1 Problem

```python
# WRONG - N+1 queries (1 + N)
users = db.query("SELECT * FROM users")  # 1 query
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")  # N queries

# RIGHT - Single query with JOIN
users_with_orders = db.query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON orders.user_id = users.id
""")  # 1 query
```

---

## Indexing Principles

| Index When | Example |
|------------|---------|
| WHERE clause columns | `WHERE user_id = ?` → index `user_id` |
| JOIN columns | `JOIN orders ON user_id` → index `user_id` |
| ORDER BY columns | `ORDER BY created_at` → index `created_at` |
| Unique constraints | Email uniqueness |

```sql
-- Create index for common query pattern
CREATE INDEX idx_orders_user_created
ON orders (user_id, created_at DESC);
```

---

## Query Analysis

```sql
-- PostgreSQL: Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 10;

-- Look for:
-- - Seq Scan (bad for large tables)
-- - Index Scan (good)
-- - Nested Loop on large sets (potential N+1)
```

---

## Connection Pooling

```python
from sqlalchemy import create_engine

# With connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Maintain 10 connections
    max_overflow=20,        # Allow 20 more under load
    pool_timeout=30,        # Wait 30s for connection
    pool_recycle=1800,      # Recycle connections every 30min
)
```

---

## Batch Operations

```python
# WRONG - Insert one at a time
for record in records:
    db.execute("INSERT INTO table VALUES (?)", record)

# RIGHT - Batch insert
db.executemany(
    "INSERT INTO table VALUES (?)",
    records  # All at once
)

# Or use bulk insert syntax
db.execute(
    "INSERT INTO table VALUES " +
    ",".join(["(?)"] * len(records)),
    flatten(records)
)
```

---

## Pagination

```python
# WRONG - OFFSET for large datasets (scans all skipped rows)
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;

# RIGHT - Keyset pagination (uses index)
SELECT * FROM orders
WHERE id > last_seen_id
ORDER BY id
LIMIT 20;
```

---

## Query Timeout

```python
# Set query timeout to prevent runaway queries
with db.connect() as conn:
    conn.execute("SET statement_timeout = '30s'")
    result = conn.execute(query)
```

---

## Anti-Patterns

```python
# WRONG - SELECT * (fetches unnecessary columns)
SELECT * FROM users;

# RIGHT - Only needed columns
SELECT id, name, email FROM users;

# WRONG - Counting with SELECT
len(db.query("SELECT * FROM orders").fetchall())

# RIGHT - COUNT in database
db.query("SELECT COUNT(*) FROM orders").scalar()
```

---

## UP

[INDEX.md](INDEX.md)

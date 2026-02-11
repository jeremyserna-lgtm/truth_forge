---
description: "Explore and profile your data source schema and contents"
argument-hint: "<table or collection name>"
---

# /explore - Explore Data

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/explore <table or collection>
```

## Workflow

### 1. INPUT HOLD — Determine Scope
Determine the scope: full schema overview or specific table.
If previous traces exist, read them to avoid re-exploring known territory.

### 2. AGENT — Schema Discovery and Profiling
List available tables/collections and their columns/fields.
For the specified table: row count, column types, null rates, cardinality, value distributions.
Use the `connector-skill` skill to introspect the data source.

### 3. OUTPUT HOLD — Present with Insights
Flag unexpected patterns, data quality concerns, or potential problems.
Recommend interesting dimensions to analyze or queries to run next.

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_explore_[timestamp].md — the schema map and annotations produced
- TRACE_explore_[timestamp].md — what areas were examined, what was surprising, confidence in schema understanding
- FILTER_explore_[timestamp].md — which schema paths were relevant vs noise

## Examples
```
/explore
/explore users
/explore orders
```

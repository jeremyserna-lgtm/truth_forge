# Schema Guide

Patterns for exploring and understanding data source schemas across different backends.

## SQL Databases
```sql
-- List tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Describe columns
SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'your_table';

-- Quick profile
SELECT COUNT(*), COUNT(DISTINCT column_name), MIN(column_name), MAX(column_name) FROM your_table;
```

## Key Profiling Metrics
- Row count
- Column count and types
- Null rates per column
- Cardinality (distinct values)
- Min/Max/Mean for numeric columns
- Most common values for categorical columns

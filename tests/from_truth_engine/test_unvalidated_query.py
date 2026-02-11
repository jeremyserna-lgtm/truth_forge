# This file queries a table without Schema Service to test Schema Service hook
import duckdb

conn = duckdb.connect("test.duckdb")
# This should be blocked - querying 'contacts' without Schema Service
conn.execute("SELECT * FROM contacts")

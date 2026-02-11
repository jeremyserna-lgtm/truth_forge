"""Test sample data for pipeline validation."""
import json
from pathlib import Path

# Create test data directory
test_dir = Path("data/staging/test_input")
test_dir.mkdir(parents=True, exist_ok=True)

# Sample Claude Code session data
sample_messages = [
    {
        "session_id": "test-session-001",
        "message_index": 0,
        "text": "Hello! Can you help me write a Python function to calculate Fibonacci numbers?",
        "role": "user",
        "message_type": "message",
        "timestamp_utc": "2026-01-29T10:00:00Z",
        "content_date": "2026-01-29",
    },
    {
        "session_id": "test-session-001",
        "message_index": 1,
        "text": "I'd be happy to help! Here's a recursive Fibonacci implementation.",
        "role": "assistant",
        "message_type": "message",
        "timestamp_utc": "2026-01-29T10:00:05Z",
        "content_date": "2026-01-29",
    },
    {
        "session_id": "test-session-001",
        "message_index": 2,
        "text": "Thanks! Can you also show me an iterative version?",
        "role": "user",
        "message_type": "message",
        "timestamp_utc": "2026-01-29T10:00:15Z",
        "content_date": "2026-01-29",
    },
]

# Write test data
output_file = test_dir / "test_session.jsonl"
with open(output_file, "w") as f:
    for msg in sample_messages:
       f.write(json.dumps(msg) + "\n")

print(f"Created test data: {output_file}")
print(f"Sample messages: {len(sample_messages)}")

#!/usr/bin/env python3
"""
Quick data formatter for MLX fine-tuning.

Takes raw conversation JSONL and formats it for MLX-LM training.
Format: {"text": "USER: ... ASSISTANT: ..."}
"""

import json
import sys
from pathlib import Path


def format_conversations(input_path: str, output_dir: str, max_records: int = None):
    """Convert raw conversations to MLX training format."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_file = output_path / "train.jsonl"
    valid_file = output_path / "valid.jsonl"

    # Read all messages
    messages = []
    with open(input_path, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line.strip())
                messages.append(msg)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(messages)} messages")

    # Group into conversations (pairs of user/assistant)
    conversations = []
    i = 0
    while i < len(messages) - 1:
        if messages[i].get('role') == 'user' and messages[i+1].get('role') == 'assistant':
            user_text = messages[i].get('text', '')
            assistant_text = messages[i+1].get('text', '')

            if user_text and assistant_text:
                # Format as single training example
                formatted = f"USER: {user_text}\n\nASSISTANT: {assistant_text}"
                conversations.append({"text": formatted})
            i += 2
        else:
            i += 1

    print(f"Created {len(conversations)} conversation pairs")

    if max_records:
        conversations = conversations[:max_records]
        print(f"Limited to {len(conversations)} records")

    # Split 90/10 train/valid
    split_idx = int(len(conversations) * 0.9)
    train_data = conversations[:split_idx]
    valid_data = conversations[split_idx:]

    # Write files
    with open(train_file, 'w') as f:
        for conv in train_data:
            f.write(json.dumps(conv) + '\n')

    with open(valid_file, 'w') as f:
        for conv in valid_data:
            f.write(json.dumps(conv) + '\n')

    print(f"Written {len(train_data)} train, {len(valid_data)} valid")
    print(f"Output: {output_path}")

    return str(output_path)


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "AI-Breakdown-Prevention/data/raw/claude/conversations.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "training/data_prep/mlx_formatted"
    max_records = int(sys.argv[3]) if len(sys.argv) > 3 else None

    format_conversations(input_path, output_dir, max_records)

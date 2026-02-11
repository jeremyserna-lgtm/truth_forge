#!/usr/bin/env python3
"""Test script for LLM Refinery models."""

import sys
sys.path.insert(0, "/Users/jeremyserna/truth_forge")

import json
from pipelines.llm_refinery.models import (
    ConversationL8, TopicSegmentL7, TurnL6, MessageL5
)

# Load sample
with open("/Users/jeremyserna/truth_forge/data/llm_refinery_output/sample_conversations.json") as f:
    data = json.load(f)

conv_data = data[0]
print("Testing model creation...")

# Test L8 creation
conv = ConversationL8.from_raw(conv_data)
print(f"✓ L8 Created: {conv.entity_id}")
print(f"  Title: {conv.title}")
print(f"  Participants: {conv.participants}")

# Test L5 creation
raw_msg = conv_data["chat_messages"][0]
msg = MessageL5.from_raw(raw_msg, conv.entity_id, 0, conv.entity_id)
print(f"✓ L5 Created: {msg.entity_id}")
print(f"  Role: {msg.role}")
text_preview = msg.text[:100] + "..." if len(msg.text) > 100 else msg.text
print(f"  Text: {text_preview}")

# Test entity_unified export
unified = conv.to_entity_unified()
print(f"✓ Entity Unified export: {len(unified)} fields")

print()
print("Models working correctly!")

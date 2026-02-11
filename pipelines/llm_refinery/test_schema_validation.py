#!/usr/bin/env python3
"""Validate L8-L2 entities against entity_unified BigQuery schema.

This test ensures all layers produce output that matches the exact
34-field entity_unified schema used in production.
"""

import sys
sys.path.insert(0, "/Users/jeremyserna/truth_forge")

import json
from datetime import datetime, UTC
from typing import Any

from pipelines.llm_refinery.processor import LLMRefineryProcessor, ProcessorConfig
from pipelines.llm_refinery.models import (
    ConversationL8, TopicSegmentL7, TurnL6, MessageL5,
    SentenceL4, SpanL3, WordL2
)

# ============================================================================
# ENTITY_UNIFIED SCHEMA (34 fields from specification)
# ============================================================================

ENTITY_UNIFIED_SCHEMA = {
    # Identity Fields
    "entity_id": {"type": "STRING", "required": True},
    "level": {"type": "INTEGER", "required": True},
    "entity_type": {"type": "STRING", "required": True},
    "entity_mode": {"type": "STRING", "required": False},
    "parent_id": {"type": "STRING", "required": False},
    
    # Hierarchical ID Fields
    "conversation_id": {"type": "STRING", "required": False},
    "topic_segment_id": {"type": "STRING", "required": False},
    "turn_id": {"type": "STRING", "required": False},
    "message_id": {"type": "STRING", "required": False},
    "sentence_id": {"type": "STRING", "required": False},
    "span_id": {"type": "STRING", "required": False},
    "word_id": {"type": "STRING", "required": False},
    
    # Source Fields
    "source_pipeline": {"type": "STRING", "required": True},
    "source_file": {"type": "STRING", "required": False},
    "source_file_path": {"type": "STRING", "required": False},
    "source_system": {"type": "STRING", "required": False},
    "source_ids": {"type": "REPEATED_STRING", "required": False},
    
    # Content Fields
    "text": {"type": "STRING", "required": True},
    "canonical_form": {"type": "STRING", "required": False},
    "persona": {"type": "STRING", "required": False},
    
    # Metadata Field
    "metadata": {"type": "JSON", "required": False},
    
    # Timestamp Fields
    "content_date": {"type": "DATE", "required": False},
    "source_message_timestamp": {"type": "TIMESTAMP", "required": False},
    "created_at": {"type": "TIMESTAMP", "required": True},
    "updated_at": {"type": "TIMESTAMP", "required": False},
    "ingestion_timestamp": {"type": "TIMESTAMP", "required": True},
    "ingestion_job_id": {"type": "STRING", "required": False},
    
    # Validation Fields
    "validation_status": {"type": "STRING", "required": False},
    
    # Count Rollup Fields
    "l7_count": {"type": "INTEGER", "required": False},
    "l6_count": {"type": "INTEGER", "required": False},
    "l5_count": {"type": "INTEGER", "required": False},
    "l4_count": {"type": "INTEGER", "required": False},
    "l3_count": {"type": "INTEGER", "required": False},
    "l2_count": {"type": "INTEGER", "required": False},
    "l1_count": {"type": "INTEGER", "required": False},
}

LEVEL_TO_TYPE = {
    8: "conversation",
    7: "topic_segment",
    6: "turn",
    5: "message",
    4: "sentence",
    3: "span",
    2: "word",
}


def validate_entity(entity: dict, level: int) -> tuple[bool, list[str]]:
    """Validate an entity against the schema.
    
    Returns:
        (is_valid, list of issues)
    """
    issues = []
    
    # Check required fields
    for field, spec in ENTITY_UNIFIED_SCHEMA.items():
        if spec["required"] and field not in entity:
            issues.append(f"Missing required field: {field}")
        elif spec["required"] and entity.get(field) is None:
            issues.append(f"Required field is None: {field}")
    
    # Validate field types
    for field, value in entity.items():
        if field not in ENTITY_UNIFIED_SCHEMA:
            issues.append(f"Unknown field: {field}")
            continue
        
        spec = ENTITY_UNIFIED_SCHEMA[field]
        if value is None:
            continue
            
        if spec["type"] == "STRING" and not isinstance(value, str):
            issues.append(f"Field {field} should be STRING, got {type(value).__name__}")
        elif spec["type"] == "INTEGER" and not isinstance(value, int):
            issues.append(f"Field {field} should be INTEGER, got {type(value).__name__}")
        elif spec["type"] == "REPEATED_STRING" and not isinstance(value, list):
            issues.append(f"Field {field} should be REPEATED (list), got {type(value).__name__}")
        elif spec["type"] == "JSON" and not isinstance(value, (dict, type(None))):
            issues.append(f"Field {field} should be JSON (dict), got {type(value).__name__}")
    
    # Validate level matches entity_type
    if entity.get("level") != level:
        issues.append(f"Level mismatch: expected {level}, got {entity.get('level')}")
    
    expected_type = LEVEL_TO_TYPE.get(level)
    if entity.get("entity_type") != expected_type:
        issues.append(f"Entity type mismatch: expected {expected_type}, got {entity.get('entity_type')}")
    
    # Validate entity_id format
    entity_id = entity.get("entity_id", "")
    expected_prefixes = {
        8: "conv:",
        7: "topic:",
        6: "turn:",
        5: "msg:",
        4: "sent:",
        3: "span:",
        2: "word:",
    }
    if not entity_id.startswith(expected_prefixes.get(level, "")):
        issues.append(f"Entity ID format incorrect: {entity_id} should start with {expected_prefixes.get(level)}")
    
    # Validate hierarchical IDs are set correctly
    if level == 8 and entity.get("conversation_id") != entity.get("entity_id"):
        issues.append("L8: conversation_id should equal entity_id")
    if level <= 5 and not entity.get("conversation_id"):
        issues.append(f"L{level}: conversation_id should be set")
    
    return len(issues) == 0, issues


def print_entity_summary(entity: dict, level: int, indent: int = 0):
    """Print a formatted entity summary."""
    prefix = "  " * indent
    level_name = LEVEL_TO_TYPE.get(level, f"L{level}")
    text_preview = entity.get("text", "")[:50]
    if len(entity.get("text", "")) > 50:
        text_preview += "..."
    
    print(f"{prefix}[L{level} {level_name}] {entity.get('entity_id', 'NO_ID')}")
    print(f"{prefix}  text: \"{text_preview}\"")
    print(f"{prefix}  parent_id: {entity.get('parent_id')}")
    
    # Show count fields if present
    counts = []
    for i in range(7, 1, -1):
        count_field = f"l{i}_count"
        if entity.get("metadata", {}).get(count_field):
            counts.append(f"L{i}={entity['metadata'][count_field]}")
    if counts:
        print(f"{prefix}  counts: {', '.join(counts)}")


def main():
    print("=" * 70)
    print("ENTITY_UNIFIED SCHEMA VALIDATION TEST")
    print("=" * 70)
    print()
    print(f"Schema fields: {len(ENTITY_UNIFIED_SCHEMA)}")
    print()
    
    # Create test message and process
    config = ProcessorConfig(
        model="qwen2.5-coder:32b",
        min_level=2,  # Full depth
        timeout=90.0,
    )
    
    processor = LLMRefineryProcessor(config)
    
    # Build test hierarchy manually to ensure clean test
    print("-" * 70)
    print("BUILDING TEST HIERARCHY")
    print("-" * 70)
    
    # L8: Conversation
    conv = ConversationL8(
        entity_id="conv:test12345678:0000",
        conversation_id="conv:test12345678:0000",
        text="Test Conversation",
        source_uuid="test-uuid-1234",
        title="Test Conversation",
        participants=["human", "assistant"],
    )
    
    # L7: Topic Segment
    topic = TopicSegmentL7(
        entity_id="topic:test12345678:0000",
        text="Main topic discussion",
        parent_id=conv.entity_id,
        conversation_id=conv.entity_id,
        topic_label="Main Discussion",
    )
    
    # L6: Turn
    turn = TurnL6(
        entity_id="turn:test12345678:0000",
        text="User's question about configuration",
        parent_id=topic.entity_id,
        conversation_id=conv.entity_id,
        topic_segment_id=topic.entity_id,
        speaker="human",
    )
    
    # L5: Message
    msg = MessageL5(
        entity_id="msg:test12345678:0000",
        text="The configuration file contains an error. How do I fix this problem?",
        parent_id=turn.entity_id,
        conversation_id=conv.entity_id,
        turn_id=turn.entity_id,
        role="human",
    )
    
    # Link hierarchy
    turn.children = [msg]
    topic.children = [turn]
    conv.children = [topic]
    
    # Process message deeply with LLM
    print("\nProcessing message with LLM for L4-L2 extraction...")
    try:
        processor._process_message_deeply(msg)
        print(f"✓ LLM extracted {len(msg.children)} sentences")
    except Exception as e:
        print(f"✗ LLM processing failed: {e}")
        return
    finally:
        processor.close()
    
    print()
    print("-" * 70)
    print("VALIDATING ALL LAYERS")
    print("-" * 70)
    
    all_entities = []
    all_valid = True
    
    # Collect and validate L8
    print("\n[L8 CONVERSATION]")
    conv_unified = conv.to_entity_unified()
    all_entities.append(("L8", conv_unified))
    valid, issues = validate_entity(conv_unified, 8)
    if valid:
        print("  ✓ Schema valid")
    else:
        print("  ✗ Schema issues:")
        for issue in issues:
            print(f"    - {issue}")
        all_valid = False
    print_entity_summary(conv_unified, 8, indent=1)
    
    # Collect and validate L7
    for topic in conv.children:
        print("\n[L7 TOPIC SEGMENT]")
        topic_unified = topic.to_entity_unified()
        all_entities.append(("L7", topic_unified))
        valid, issues = validate_entity(topic_unified, 7)
        if valid:
            print("  ✓ Schema valid")
        else:
            print("  ✗ Schema issues:")
            for issue in issues:
                print(f"    - {issue}")
            all_valid = False
        print_entity_summary(topic_unified, 7, indent=1)
        
        # Collect and validate L6
        for turn in topic.children:
            print("\n[L6 TURN]")
            turn_unified = turn.to_entity_unified()
            all_entities.append(("L6", turn_unified))
            valid, issues = validate_entity(turn_unified, 6)
            if valid:
                print("  ✓ Schema valid")
            else:
                print("  ✗ Schema issues:")
                for issue in issues:
                    print(f"    - {issue}")
                all_valid = False
            print_entity_summary(turn_unified, 6, indent=1)
            
            # Collect and validate L5
            for msg in turn.children:
                print("\n[L5 MESSAGE]")
                msg_unified = msg.to_entity_unified()
                all_entities.append(("L5", msg_unified))
                valid, issues = validate_entity(msg_unified, 5)
                if valid:
                    print("  ✓ Schema valid")
                else:
                    print("  ✗ Schema issues:")
                    for issue in issues:
                        print(f"    - {issue}")
                    all_valid = False
                print_entity_summary(msg_unified, 5, indent=1)
                
                # Collect and validate L4
                for sent in msg.children:
                    print("\n  [L4 SENTENCE]")
                    sent_unified = sent.to_entity_unified()
                    all_entities.append(("L4", sent_unified))
                    valid, issues = validate_entity(sent_unified, 4)
                    if valid:
                        print("    ✓ Schema valid")
                    else:
                        print("    ✗ Schema issues:")
                        for issue in issues:
                            print(f"      - {issue}")
                        all_valid = False
                    print_entity_summary(sent_unified, 4, indent=2)
                    
                    # Collect and validate L3
                    for span in sent.children:
                        print("\n    [L3 SPAN]")
                        span_unified = span.to_entity_unified()
                        all_entities.append(("L3", span_unified))
                        valid, issues = validate_entity(span_unified, 3)
                        if valid:
                            print("      ✓ Schema valid")
                        else:
                            print("      ✗ Schema issues:")
                            for issue in issues:
                                print(f"        - {issue}")
                            all_valid = False
                        print_entity_summary(span_unified, 3, indent=3)
                        
                        # Collect and validate L2
                        for word in span.children:
                            print("\n      [L2 WORD]")
                            word_unified = word.to_entity_unified()
                            all_entities.append(("L2", word_unified))
                            valid, issues = validate_entity(word_unified, 2)
                            if valid:
                                print("        ✓ Schema valid")
                            else:
                                print("        ✗ Schema issues:")
                                for issue in issues:
                                    print(f"          - {issue}")
                                all_valid = False
                            print_entity_summary(word_unified, 2, indent=4)
    
    # Summary
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    # Count by level
    level_counts = {}
    for level, _ in all_entities:
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print(f"\nTotal entities: {len(all_entities)}")
    for level in ["L8", "L7", "L6", "L5", "L4", "L3", "L2"]:
        count = level_counts.get(level, 0)
        print(f"  {level}: {count}")
    
    print()
    if all_valid:
        print("✓ ALL ENTITIES MATCH entity_unified SCHEMA")
    else:
        print("✗ SOME ENTITIES HAVE SCHEMA ISSUES")
    
    # Show sample complete entity
    print()
    print("-" * 70)
    print("SAMPLE COMPLETE ENTITY (L5 Message)")
    print("-" * 70)
    l5_entity = next((e for l, e in all_entities if l == "L5"), None)
    if l5_entity:
        print(json.dumps(l5_entity, indent=2, default=str))
    
    print()
    print("-" * 70)
    print("SAMPLE COMPLETE ENTITY (L2 Word)")
    print("-" * 70)
    l2_entity = next((e for l, e in all_entities if l == "L2"), None)
    if l2_entity:
        print(json.dumps(l2_entity, indent=2, default=str))


if __name__ == "__main__":
    main()

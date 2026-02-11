#!/usr/bin/env python3
"""Test L4-L2 deep processing with a single message."""

import sys
sys.path.insert(0, "/Users/jeremyserna/truth_forge")

import json
from pipelines.llm_refinery.processor import LLMRefineryProcessor, ProcessorConfig
from pipelines.llm_refinery.models import MessageL5, SentenceL4, SpanL3, WordL2

print("=" * 60)
print("TESTING L4-L2 DEEP PROCESSING")
print("=" * 60)

# Create a test message
test_message = MessageL5(
    entity_id="msg:test:0000",
    text="The configuration file contains an error. How do I fix this problem?",
    role="human",
    conversation_id="conv:test:0000",
    turn_id="turn:test:0000",
)

print(f"\nTest Message: {test_message.text}")
print(f"Role: {test_message.role}")

# Configure processor for deep processing
config = ProcessorConfig(
    model="qwen2.5-coder:32b",
    min_level=2,  # Process down to words
    timeout=60.0,
)

processor = LLMRefineryProcessor(config)

print("\n" + "-" * 60)
print("Testing LLM deep message analysis...")
print("-" * 60)

try:
    # Test the deep processing method directly
    processor._process_message_deeply(test_message)
    
    print(f"\n✓ Message analyzed successfully")
    print(f"  Message type: {test_message.message_type}")
    print(f"  Sentiment: {test_message.sentiment}")
    print(f"  Intent: {test_message.intent}")
    print(f"  Emotions: {test_message.emotions}")
    
    print(f"\n  L4 Sentences: {len(test_message.children)}")
    for i, sent in enumerate(test_message.children):
        print(f"    [{i}] {sent.text[:60]}...")
        print(f"        Type: {sent.sentence_type}, Complexity: {sent.complexity}")
        print(f"        Sentiment: {sent.sentiment}, Intent: {sent.intent}")
        
        print(f"        L3 Spans: {len(sent.children)}")
        for j, span in enumerate(sent.children[:3]):  # Show first 3
            print(f"          [{j}] '{span.text}' ({span.span_type})")
            
            print(f"              L2 Words: {len(span.children)}")
            for k, word in enumerate(span.children[:5]):  # Show first 5
                key_marker = "★" if word.is_key_term else " "
                print(f"                {key_marker} '{word.text}' ({word.word_type})")
    
    print("\n" + "=" * 60)
    print("✓ L4-L2 DEEP PROCESSING VALIDATED")
    print("=" * 60)
    
    # Export test entity
    print("\nSample entity_unified output:")
    if test_message.children:
        sent = test_message.children[0]
        print(json.dumps(sent.to_entity_unified(), indent=2, default=str))
    
except Exception as e:
    print(f"\n✗ Error during deep processing: {e}")
    import traceback
    traceback.print_exc()

finally:
    processor.close()

print(f"\nStats: {processor.stats}")

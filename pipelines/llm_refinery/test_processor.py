#!/usr/bin/env python3
"""Quick test of the LLM Refinery processor."""

import sys
sys.path.insert(0, "/Users/jeremyserna/truth_forge")

from pipelines.llm_refinery.processor import LLMRefineryProcessor, ProcessorConfig

# Configure for quick test (L5 only, no deep analysis)
config = ProcessorConfig(
    model="qwen2.5-coder:32b",
    min_level=5,  # Stop at messages, don't go deeper
)

processor = LLMRefineryProcessor(config)

print("Processing conversations...")
print()

try:
    convs = list(processor.process_file(
        "/Users/jeremyserna/truth_forge/data/llm_refinery_output/sample_conversations.json"
    ))

    for conv in convs:
        print(f"=" * 60)
        print(f"Conversation: {conv.title}")
        print(f"UUID: {conv.source_uuid}")
        print(f"Topics: {conv.topics}")
        print(f"Sentiment: {conv.sentiment}")
        print()
        
        print("Hierarchy:")
        print(f"  L7 Topic Segments: {len(conv.children)}")
        for topic in conv.children:
            print(f"    - {topic.topic_label}")
            print(f"      L6 Turns: {len(topic.children)}")
            for turn in topic.children[:2]:
                print(f"        - {turn.speaker}: {len(turn.children)} messages")
        
        # Export
        output = processor.export_entities(conv)
        print(f"\nExported to: {output}")

    print()
    print("=" * 60)
    print(f"Stats: {processor.stats}")

except KeyboardInterrupt:
    print("\nInterrupted by user")
finally:
    processor.close()

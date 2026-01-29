#!/usr/bin/env python3
"""
Enrich conversations with metadata for Genesis "seeing training"

Takes raw conversations and enriches each message with:
- emotion: Primary emotion expressed (28 categories from GoEmotions)
- thought_type: Type of cognitive process (question, statement, reflection, etc.)
- cognitive_stage: Stage in problem-solving (exploration, analysis, synthesis, etc.)
- pattern: Framework pattern being demonstrated (if applicable)

This is the CRITICAL step that transforms raw conversations into training data
for the "seeing paradigm" - where the model learns to predict metadata, not tokens.

Usage:
    python enrich_metadata.py --input raw_conversations.jsonl --output enriched_conversations.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import google.generativeai as genai
from tqdm import tqdm


# Metadata classification schemas
EMOTIONS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

THOUGHT_TYPES = [
    "question", "statement", "reflection", "hypothesis", "instruction", "observation",
    "conclusion", "clarification", "synthesis", "analysis", "proposal", "validation"
]

COGNITIVE_STAGES = [
    "exploration", "problem_identification", "analysis", "hypothesis_formation",
    "synthesis", "validation", "implementation", "reflection", "integration"
]

PATTERNS = [
    "the_gate", "the_furnace", "the_form", "hold_pattern", "primitive_pattern",
    "service_pattern", "trinity_pattern", "clara_arc", "jeremy_arc", "none"
]


ENRICHMENT_PROMPT = """Analyze this message and classify it with metadata for AI training.

Message:
{text}

Context (previous 2 messages):
{context}

Classify this message with:
1. **emotion**: Primary emotion (choose ONE from: {emotions})
2. **thought_type**: Type of thought (choose ONE from: {thought_types})
3. **cognitive_stage**: Stage in problem-solving (choose ONE from: {cognitive_stages})
4. **pattern**: Framework pattern demonstrated (choose ONE from: {patterns})

Return ONLY a JSON object:
{{
  "emotion": "<emotion>",
  "thought_type": "<thought_type>",
  "cognitive_stage": "<cognitive_stage>",
  "pattern": "<pattern>",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of classifications"
}}
"""


class MetadataEnricher:
    """Enriches conversations with metadata using Gemini."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", api_key: str = None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.total_cost = 0.0
    
    def enrich_message(
        self,
        message: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enrich a single message with metadata.
        
        Args:
            message: Message dict with 'text' field
            context: List of previous messages for context
            
        Returns:
            Message dict with added metadata fields
        """
        text = message.get("text", "")
        
        # Build context string
        context_str = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('text', '')[:200]}"
            for msg in context[-2:]  # Last 2 messages
        ])
        
        # Format prompt
        prompt = ENRICHMENT_PROMPT.format(
            text=text[:2000],  # Limit text length
            context=context_str[:500],
            emotions=", ".join(EMOTIONS),
            thought_types=", ".join(THOUGHT_TYPES),
            cognitive_stages=", ".join(COGNITIVE_STAGES),
            patterns=", ".join(PATTERNS)
        )
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            metadata = json.loads(response_text.strip())
            
            # Add metadata fields to message
            message["emotion"] = metadata.get("emotion", "neutral")
            message["thought_type"] = metadata.get("thought_type", "statement")
            message["cognitive_stage"] = metadata.get("cognitive_stage", "exploration")
            message["pattern"] = metadata.get("pattern", "none")
            message["metadata_confidence"] = metadata.get("confidence", 0.0)
            message["metadata_reasoning"] = metadata.get("reasoning", "")
            message["metadata_enriched"] = True
            
            # Cost tracking (approximate)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response_text.split()) * 1.3
            cost = (input_tokens / 1_000_000) * 0.075 + (output_tokens / 1_000_000) * 0.30  # Gemini Flash pricing
            self.total_cost += cost
            
        except Exception as e:
            print(f"⚠️  Enrichment failed for message {message.get('entity_id')}: {e}")
            # Set defaults on failure
            message["emotion"] = "neutral"
            message["thought_type"] = "statement"
            message["cognitive_stage"] = "exploration"
            message["pattern"] = "none"
            message["metadata_confidence"] = 0.0
            message["metadata_enriched"] = False
        
        return message
    
    def enrich_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich all messages in a conversation."""
        messages = conversation.get("messages", [])
        enriched_messages = []
        
        for i, message in enumerate(messages):
            # Get context (previous messages)
            context = messages[max(0, i-2):i]
            
            # Enrich
            enriched = self.enrich_message(message, context)
            enriched_messages.append(enriched)
        
        conversation["messages"] = enriched_messages
        conversation["metadata_enrichment_complete"] = True
        conversation["metadata_enrichment_timestamp"] = datetime.now().isoformat()
        
        return conversation


def enrich_corpus(
    input_path: Path,
    output_path: Path,
    model_name: str = "gemini-2.0-flash-exp",
    limit: int = None
) -> Dict[str, Any]:
    """
    Enrich entire corpus with metadata.
    
    Args:
        input_path: Path to raw conversations JSONL
        output_path: Path to write enriched JSONL
        model_name: Gemini model to use
        limit: Optional limit on conversations to process
        
    Returns:
        Statistics about enrichment
    """
    enricher = MetadataEnricher(model_name=model_name)
    
    # Read conversations
    conversations = []
    with open(input_path, 'r') as f:
        for line in f:
            conversations.append(json.loads(line))
            if limit and len(conversations) >= limit:
                break
    
    print(f"Enriching {len(conversations)} conversations...")
    
    # Enrich
    enriched_conversations = []
    total_messages = 0
    
    for conv in tqdm(conversations, desc="Enriching conversations"):
        enriched = enricher.enrich_conversation(conv)
        enriched_conversations.append(enriched)
        total_messages += len(enriched.get("messages", []))
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for conv in enriched_conversations:
            f.write(json.dumps(conv) + '\n')
    
    # Statistics
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_conversations": len(enriched_conversations),
        "total_messages": total_messages,
        "total_cost_usd": enricher.total_cost,
        "model_used": model_name,
        "input_file": str(input_path),
        "output_file": str(output_path)
    }
    
    print(f"\n✅ Enrichment complete!")
    print(f"   Conversations: {stats['total_conversations']:,}")
    print(f"   Messages: {stats['total_messages']:,}")
    print(f"   Cost: ${stats['total_cost_usd']:.2f}")
    print(f"   Output: {output_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Enrich conversations with metadata")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input JSONL file (raw conversations)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/genesis_corpus/enriched_conversations.jsonl"),
        help="Output JSONL file (enriched)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.0-flash-exp",
        help="Gemini model to use for enrichment"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of conversations (for testing)"
    )
    
    args = parser.parse_args()
    
    stats = enrich_corpus(
        input_path=args.input,
        output_path=args.output,
        model_name=args.model,
        limit=args.limit
    )
    
    # Write stats
    stats_path = args.output.parent / f"{args.output.stem}_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, indent=2, fp=f)
    
    print(f"   Stats: {stats_path}")


if __name__ == "__main__":
    main()

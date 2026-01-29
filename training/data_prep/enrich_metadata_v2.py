#!/usr/bin/env python3
"""
Metadata Enrichment for Genesis Training - Prompt-Based Approach

Uses ONE unified prompt to classify ALL 4 metadata fields:
- emotion (28 GoEmotions categories)
- thought_type (cognitive process)
- cognitive_stage (problem-solving stage)
- pattern (framework pattern)

Supports two modes:
1. Cloud: Gemini 2.5 Flash (for prompt tuning, ~$0.03/1K messages)
2. Local: Ollama models like Llama Maverick (for production, free)

The SAME prompt works for both - dial it in with Gemini, run it locally with Llama.

Usage:
    # Experiment with Gemini (cheap, fast iteration)
    python enrich_metadata_v2.py --mode cloud --model gemini-2.5-flash --limit 100
    
    # Production run on THE EMPIRE (free, local)
    python enrich_metadata_v2.py --mode local --model maverick --limit 10000
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from tqdm import tqdm


# ============================================================================
# METADATA CLASSIFICATION PROMPT
# This is the KEY - dial this in with Gemini, use with local models later
# ============================================================================

METADATA_PROMPT = """You are analyzing a message from an AI conversation to extract training metadata.

Message:
{text}

Context (previous messages):
{context}

Classify this message with EXACTLY these 4 metadata fields:

1. **emotion**: The primary emotion expressed (choose ONE):
   admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, 
   desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, 
   gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, 
   remorse, sadness, surprise, neutral

2. **thought_type**: The type of cognitive process (choose ONE):
   question, statement, reflection, hypothesis, instruction, observation, 
   conclusion, clarification, synthesis, analysis, proposal, validation

3. **cognitive_stage**: Stage in problem-solving (choose ONE):
   exploration, problem_identification, analysis, hypothesis_formation, 
   synthesis, validation, implementation, reflection, integration

4. **pattern**: Framework pattern demonstrated (choose ONE):
   the_gate, the_furnace, the_form, hold_pattern, primitive_pattern, 
   service_pattern, trinity_pattern, clara_arc, jeremy_arc, none

Return ONLY valid JSON (no markdown, no explanation):
{{
  "emotion": "<emotion>",
  "thought_type": "<thought_type>",
  "cognitive_stage": "<cognitive_stage>",
  "pattern": "<pattern>"
}}
"""


# ============================================================================
# Model Handlers
# ============================================================================

class GeminiHandler:
    """Handler for Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        import google.generativeai as genai
        import os
        
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.total_cost = 0.0
    
    def generate(self, prompt: str) -> str:
        """Generate response from Gemini."""
        response = self.model.generate_content(prompt)
        
        # Estimate cost (Gemini 2.5 Flash pricing)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.text.split()) * 1.3
        cost = (input_tokens / 1_000_000) * 0.075 + (output_tokens / 1_000_000) * 0.30
        self.total_cost += cost
        
        return response.text.strip()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "total_cost_usd": self.total_cost
        }


class OllamaHandler:
    """Handler for local Ollama models."""
    
    def __init__(self, model_name: str = "maverick"):
        import requests
        
        self.model_name = model_name
        self.endpoint = "http://localhost:11434/api/generate"
        
        # Test connection
        try:
            resp = requests.post(self.endpoint, json={"model": model_name, "prompt": "test"}, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            raise ValueError(f"Ollama not available at {self.endpoint}. Start Ollama first: ollama serve")
    
    def generate(self, prompt: str) -> str:
        """Generate response from Ollama."""
        import requests
        
        response = requests.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        
        return response.json()["response"].strip()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "total_cost_usd": 0.0  # Local is free!
        }


# ============================================================================
# Enrichment Logic
# ============================================================================

def build_context(messages: List[Dict[str, Any]], current_index: int, context_size: int = 2) -> str:
    """Build context string from previous messages."""
    start_idx = max(0, current_index - context_size)
    context_messages = messages[start_idx:current_index]
    
    if not context_messages:
        return "(No previous context)"
    
    context_lines = []
    for msg in context_messages:
        role = msg.get("role", "unknown")
        text = msg.get("text", "")[:200]  # Truncate long messages
        context_lines.append(f"{role}: {text}")
    
    return "\n".join(context_lines)


def parse_json_response(response: str) -> Optional[Dict[str, str]]:
    """Parse JSON from model response, handling markdown code blocks."""
    # Strip markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    # Parse JSON
    try:
        data = json.loads(response.strip())
        return data
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse JSON: {e}")
        print(f"Response was: {response[:200]}")
        return None


def enrich_message(
    message: Dict[str, Any],
    context: str,
    handler: Any,
    prompt_template: str = METADATA_PROMPT
) -> Dict[str, Any]:
    """
    Enrich a single message with metadata.
    
    Args:
        message: Message dict
        context: Context string from previous messages
        handler: Model handler (GeminiHandler or OllamaHandler)
        prompt_template: Prompt template to use
        
    Returns:
        Enriched message dict
    """
    text = message.get("text", "")[:2000]  # Limit text length
    
    # Build prompt
    prompt = prompt_template.format(text=text, context=context)
    
    # Generate response
    try:
        response = handler.generate(prompt)
        metadata = parse_json_response(response)
        
        if metadata:
            message["emotion"] = metadata.get("emotion", "neutral")
            message["thought_type"] = metadata.get("thought_type", "statement")
            message["cognitive_stage"] = metadata.get("cognitive_stage", "exploration")
            message["pattern"] = metadata.get("pattern", "none")
            message["metadata_enriched"] = True
        else:
            # Parsing failed - use defaults
            message["emotion"] = "neutral"
            message["thought_type"] = "statement"
            message["cognitive_stage"] = "exploration"
            message["pattern"] = "none"
            message["metadata_enriched"] = False
    
    except Exception as e:
        print(f"⚠️  Enrichment failed: {e}")
        message["emotion"] = "neutral"
        message["thought_type"] = "statement"
        message["cognitive_stage"] = "exploration"
        message["pattern"] = "none"
        message["metadata_enriched"] = False
    
    return message


def enrich_corpus(
    input_path: Path,
    output_path: Path,
    mode: str = "local",
    model_name: str = "maverick",
    limit: Optional[int] = None
):
    """
    Enrich corpus with metadata.
    
    Args:
        input_path: Input JSONL (raw conversations)
        output_path: Output JSONL (enriched)
        mode: "cloud" (Gemini) or "local" (Ollama)
        model_name: Model name (gemini-2.5-flash, maverick, etc.)
        limit: Optional limit on conversations to process
    """
    # Initialize handler
    if mode == "cloud":
        print(f"🌐 Using Gemini: {model_name}")
        handler = GeminiHandler(model_name)
    else:
        print(f"💻 Using local Ollama: {model_name}")
        handler = OllamaHandler(model_name)
    
    # Load conversations
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
    
    for conv in tqdm(conversations, desc="Conversations"):
        messages = conv.get("messages", [])
        enriched_messages = []
        
        for i, message in enumerate(messages):
            # Build context
            context = build_context(messages, i)
            
            # Enrich
            enriched = enrich_message(message, context, handler)
            enriched_messages.append(enriched)
            total_messages += 1
        
        conv["messages"] = enriched_messages
        conv["metadata_enrichment_complete"] = True
        conv["metadata_enrichment_timestamp"] = datetime.now().isoformat()
        enriched_conversations.append(conv)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for conv in enriched_conversations:
            f.write(json.dumps(conv) + '\n')
    
    # Stats
    stats = handler.get_stats()
    stats.update({
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "total_conversations": len(enriched_conversations),
        "total_messages": total_messages,
        "input_file": str(input_path),
        "output_file": str(output_path)
    })
    
    print(f"\n✅ Enrichment complete!")
    print(f"   Mode: {mode}")
    print(f"   Model: {stats['model']}")
    print(f"   Conversations: {stats['total_conversations']:,}")
    print(f"   Messages: {stats['total_messages']:,}")
    if mode == "cloud":
        print(f"   Cost: ${stats['total_cost_usd']:.4f}")
    else:
        print(f"   Cost: FREE (local)")
    print(f"   Output: {output_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Enrich conversations with metadata (prompt-based)")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input JSONL (raw conversations)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/genesis_corpus/enriched_conversations.jsonl"),
        help="Output JSONL (enriched)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["cloud", "local"],
        default="local",
        help="cloud=Gemini (for experimentation), local=Ollama (for production)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="maverick",
        help="Model name (gemini-2.5-flash, maverick, etc.)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit conversations (for testing)"
    )
    
    args = parser.parse_args()
    
    stats = enrich_corpus(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        model_name=args.model,
        limit=args.limit
    )
    
    # Save stats
    stats_path = args.output.parent / f"{args.output.stem}_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, indent=2, fp=f)
    
    print(f"   Stats: {stats_path}")


if __name__ == "__main__":
    main()

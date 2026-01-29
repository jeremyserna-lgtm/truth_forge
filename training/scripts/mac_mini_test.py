#!/usr/bin/env python3
"""
Mac Mini Fast Iteration Test - Genesis Seeing Paradigm

Quick iteration loop to discover the pattern that makes "my not me" emerge.

Uses:
- Small model (Llama 3.2 3B/7B)
- Small corpus (1K messages)
- Fast training (hours, not days)
- Rapid iteration on hyperparameters

Goal: Learn the pattern, then scale to THE EMPIRE.

Usage:
    python mac_mini_test.py --corpus data/genesis_corpus/enriched_conversations.jsonl --limit 1000
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import mlx.core as mx
import mlx.nn as nn
from datetime import datetime


def load_training_data(corpus_path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Load and format training data for seeing paradigm.
    
    Returns list of training examples in format:
    {
        "text": "message text",
        "metadata": {
            "emotion": "curiosity",
            "thought_type": "question",
            "cognitive_stage": "exploration",
            "pattern": "the_gate"
        }
    }
    """
    examples = []
    
    with open(corpus_path, 'r') as f:
        for line in f:
            conv = json.loads(line)
            for msg in conv.get("messages", []):
                if msg.get("metadata_enriched"):
                    example = {
                        "text": msg.get("text", ""),
                        "metadata": {
                            "emotion": msg.get("emotion"),
                            "thought_type": msg.get("thought_type"),
                            "cognitive_stage": msg.get("cognitive_stage"),
                            "pattern": msg.get("pattern")
                        }
                    }
                    examples.append(example)
                    
                    if len(examples) >= limit:
                        return examples
    
    return examples


def run_mac_mini_test(
    corpus_path: Path,
    model_name: str = "mlx-community/Llama-3.2-3B-Instruct",
    limit: int = 1000,
    iterations: int = 3
):
    """
    Run fast iteration test on Mac Mini.
    
    Args:
        corpus_path: Path to enriched corpus
        model_name: MLX model to use (3B or 7B)
        limit: Number of messages to train on
        iterations: Number of iteration loops
    """
    print(f"{'='*80}")
    print(f"MAC MINI FAST ITERATION TEST - Genesis Seeing Paradigm")
    print(f"{'='*80}")
    print(f"Model: {model_name}")
    print(f"Corpus: {corpus_path}")
    print(f"Messages: {limit}")
    print(f"Iterations: {iterations}")
    print(f"")
    
    # Load data
    print("Loading training data...")
    examples = load_training_data(corpus_path, limit)
    print(f"✅ Loaded {len(examples)} examples")
    
    # TODO: Implement actual training loop
    # This is a placeholder - actual implementation needs:
    # 1. Load model with MLX
    # 2. Create metadata classification head
    # 3. Train with seeing paradigm loss
    # 4. Measure Jeremy Arc at each iteration
    # 5. Adjust hyperparameters
    # 6. Iterate
    
    print(f"\n⚠️  Training loop not yet implemented")
    print(f"Next steps:")
    print(f"  1. Implement MLX training loop")
    print(f"  2. Create metadata classification loss")
    print(f"  3. Add Jeremy Arc measurement")
    print(f"  4. Run iteration experiments")
    
    return {
        "status": "ready_for_implementation",
        "examples_loaded": len(examples),
        "model": model_name
    }


def main():
    parser = argparse.ArgumentParser(description="Mac Mini fast iteration test")
    parser.add_argument(
        "--corpus",
        type=Path,
        required=True,
        help="Path to enriched corpus JSONL"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/Llama-3.2-3B-Instruct",
        help="MLX model name (3B or 7B)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Number of messages to train on"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iteration loops"
    )
    
    args = parser.parse_args()
    
    result = run_mac_mini_test(
        corpus_path=args.corpus,
        model_name=args.model,
        limit=args.limit,
        iterations=args.iterations
    )
    
    print(f"\n{'='*80}")
    print(f"Test complete! Result: {result}")


if __name__ == "__main__":
    main()

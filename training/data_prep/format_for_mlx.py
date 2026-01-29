#!/usr/bin/env python3
"""
Format Enriched Corpus for MLX Training

Converts enriched conversations into MLX training format for Genesis "seeing paradigm."

Input: enriched_conversations.jsonl (with metadata)
Output: genesis_training_corpus.jsonl (MLX format)

Also creates train/val/test splits and statistics.

Usage:
    python format_for_mlx.py \
        --input data/genesis_corpus/enriched_conversations.jsonl \
        --output data/genesis_corpus/genesis_training_corpus.jsonl
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter


def format_for_mlx(
    input_path: Path,
    output_path: Path,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Format enriched corpus for MLX training.
    
    MLX format:
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
    random.seed(seed)
    
    print(f"Formatting corpus for MLX training...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Splits: train={train_ratio}, val={val_ratio}, test={test_ratio}")
    print()
    
    # Load enriched conversations
    all_examples = []
    total_conversations = 0
    
    with open(input_path, 'r') as f:
        for line in f:
            conv = json.loads(line)
            total_conversations += 1
            
            for msg in conv.get("messages", []):
                if not msg.get("metadata_enriched"):
                    continue
                
                example = {
                    "text": msg.get("text", ""),
                    "metadata": {
                        "emotion": msg.get("emotion"),
                        "thought_type": msg.get("thought_type"),
                        "cognitive_stage": msg.get("cognitive_stage"),
                        "pattern": msg.get("pattern")
                    },
                    # Optional fields for tracking
                    "conversation_id": conv.get("conversation_id"),
                    "source_pipeline": conv.get("source_pipeline")
                }
                
                all_examples.append(example)
    
    print(f"Loaded {len(all_examples)} examples from {total_conversations} conversations")
    
    # Shuffle
    random.shuffle(all_examples)
    
    # Split
    n = len(all_examples)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_examples = all_examples[:train_end]
    val_examples = all_examples[train_end:val_end]
    test_examples = all_examples[val_end:]
    
    # Write splits
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    splits = {
        "train": train_examples,
        "val": val_examples,
        "test": test_examples
    }
    
    for split_name, examples in splits.items():
        split_path = output_dir / f"{output_path.stem}_{split_name}.jsonl"
        
        with open(split_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"✅ {split_name}: {len(examples)} examples → {split_path}")
    
    # Compute statistics
    stats = compute_statistics(all_examples)
    stats.update({
        "timestamp": datetime.now().isoformat(),
        "total_examples": len(all_examples),
        "total_conversations": total_conversations,
        "train_examples": len(train_examples),
        "val_examples": len(val_examples),
        "test_examples": len(test_examples),
        "input_file": str(input_path),
        "output_dir": str(output_dir)
    })
    
    # Write statistics
    stats_path = output_dir / f"{output_path.stem}_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, indent=2, fp=f)
    
    print(f"\n📊 Statistics saved to {stats_path}")
    print_stats(stats)
    
    return stats


def compute_statistics(examples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute metadata distribution statistics."""
    emotions = []
    thought_types = []
    cognitive_stages = []
    patterns = []
    
    for ex in examples:
        meta = ex.get("metadata", {})
        emotions.append(meta.get("emotion"))
        thought_types.append(meta.get("thought_type"))
        cognitive_stages.append(meta.get("cognitive_stage"))
        patterns.append(meta.get("pattern"))
    
    return {
        "emotion_distribution": dict(Counter(emotions)),
        "thought_type_distribution": dict(Counter(thought_types)),
        "cognitive_stage_distribution": dict(Counter(cognitive_stages)),
        "pattern_distribution": dict(Counter(patterns))
    }


def print_stats(stats: Dict[str, Any]):
    """Print formatted statistics."""
    print(f"\n{'='*80}")
    print(f"CORPUS STATISTICS")
    print(f"{'='*80}")
    
    print(f"\nTotal Examples: {stats['total_examples']:,}")
    print(f"Total Conversations: {stats['total_conversations']:,}")
    print(f"Train: {stats['train_examples']:,}")
    print(f"Val: {stats['val_examples']:,}")
    print(f"Test: {stats['test_examples']:,}")
    
    print(f"\nMetadata Distributions:")
    
    for field in ["emotion", "thought_type", "cognitive_stage", "pattern"]:
        dist = stats.get(f"{field}_distribution", {})
        print(f"\n{field.upper()}:")
        
        # Sort by count
        sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
        
        for value, count in sorted_items[:10]:  # Top 10
            pct = (count / stats['total_examples']) * 100
            print(f"  {value:30s} {count:6,} ({pct:5.1f}%)")
        
        if len(sorted_items) > 10:
            print(f"  ... ({len(sorted_items) - 10} more)")


def main():
    parser = argparse.ArgumentParser(description="Format corpus for MLX training")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input enriched JSONL"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/genesis_corpus/genesis_training_corpus.jsonl"),
        help="Output MLX JSONL"
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Train split ratio"
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="Validation split ratio"
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.1,
        help="Test split ratio"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed"
    )
    
    args = parser.parse_args()
    
    format_for_mlx(
        input_path=args.input,
        output_path=args.output,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Validate Genesis Training Corpus

Validates that the corpus is ready for Genesis training by checking:
- All examples have required metadata fields
- Metadata values are valid
- Splits are balanced
- Pattern coverage is adequate

Usage:
    python validate_corpus.py \
        --corpus data/genesis_corpus/genesis_training_corpus_train.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import Counter


# Valid values for each metadata field
VALID_EMOTIONS = {
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
}

VALID_THOUGHT_TYPES = {
    "question", "statement", "reflection", "hypothesis", "instruction", "observation",
    "conclusion", "clarification", "synthesis", "analysis", "proposal", "validation"
}

VALID_COGNITIVE_STAGES = {
    "exploration", "problem_identification", "analysis", "hypothesis_formation",
    "synthesis", "validation", "implementation", "reflection", "integration"
}

VALID_PATTERNS = {
    "the_gate", "the_furnace", "the_form", "hold_pattern", "primitive_pattern",
    "service_pattern", "trinity_pattern", "clara_arc", "jeremy_arc", "none"
}


class CorpusValidator:
    """Validates Genesis training corpus."""
    
    def __init__(self, corpus_path: Path):
        self.corpus_path = corpus_path
        self.examples = []
        self.errors = []
        self.warnings = []
    
    def load_corpus(self):
        """Load corpus from JSONL."""
        print(f"Loading corpus from {self.corpus_path}...")
        
        with open(self.corpus_path, 'r') as f:
            for i, line in enumerate(f, 1):
                try:
                    example = json.loads(line)
                    self.examples.append(example)
                except json.JSONDecodeError as e:
                    self.errors.append(f"Line {i}: Invalid JSON - {e}")
        
        print(f"✅ Loaded {len(self.examples)} examples")
    
    def validate_metadata_fields(self):
        """Check all examples have required metadata fields."""
        print(f"\nValidating metadata fields...")
        
        required_fields = ["emotion", "thought_type", "cognitive_stage", "pattern"]
        missing_counts = Counter()
        
        for i, example in enumerate(self.examples):
            metadata = example.get("metadata", {})
            
            for field in required_fields:
                if field not in metadata or metadata[field] is None:
                    missing_counts[field] += 1
        
        if missing_counts:
            for field, count in missing_counts.items():
                pct = (count / len(self.examples)) * 100
                self.errors.append(f"Missing {field}: {count} examples ({pct:.1f}%)")
        else:
            print(f"✅ All examples have required metadata fields")
    
    def validate_metadata_values(self):
        """Check metadata values are valid."""
        print(f"\nValidating metadata values...")
        
        invalid_counts = {
            "emotion": 0,
            "thought_type": 0,
            "cognitive_stage": 0,
            "pattern": 0
        }
        
        for i, example in enumerate(self.examples):
            metadata = example.get("metadata", {})
            
            if metadata.get("emotion") not in VALID_EMOTIONS:
                invalid_counts["emotion"] += 1
            
            if metadata.get("thought_type") not in VALID_THOUGHT_TYPES:
                invalid_counts["thought_type"] += 1
            
            if metadata.get("cognitive_stage") not in VALID_COGNITIVE_STAGES:
                invalid_counts["cognitive_stage"] += 1
            
            if metadata.get("pattern") not in VALID_PATTERNS:
                invalid_counts["pattern"] += 1
        
        for field, count in invalid_counts.items():
            if count > 0:
                pct = (count / len(self.examples)) * 100
                self.errors.append(f"Invalid {field}: {count} examples ({pct:.1f}%)")
        
        if sum(invalid_counts.values()) == 0:
            print(f"✅ All metadata values are valid")
    
    def validate_pattern_coverage(self):
        """Check that framework patterns have adequate coverage."""
        print(f"\nValidating pattern coverage...")
        
        pattern_counts = Counter()
        
        for example in self.examples:
            pattern = example.get("metadata", {}).get("pattern")
            pattern_counts[pattern] += 1
        
        # Warn if important patterns are missing
        important_patterns = ["the_gate", "the_furnace", "the_form", "hold_pattern"]
        
        for pattern in important_patterns:
            count = pattern_counts.get(pattern, 0)
            pct = (count / len(self.examples)) * 100
            
            if count == 0:
                self.warnings.append(f"Pattern '{pattern}' has NO examples")
            elif pct < 1.0:
                self.warnings.append(f"Pattern '{pattern}' has only {count} examples ({pct:.2f}%)")
        
        # Show distribution
        print(f"\nPattern distribution:")
        for pattern, count in pattern_counts.most_common():
            pct = (count / len(self.examples)) * 100
            print(f"  {pattern:20s} {count:6,} ({pct:5.1f}%)")
    
    def validate_balance(self):
        """Check that metadata distributions aren't too skewed."""
        print(f"\nValidating balance...")
        
        for field in ["emotion", "thought_type", "cognitive_stage", "pattern"]:
            counts = Counter()
            
            for example in self.examples:
                value = example.get("metadata", {}).get(field)
                counts[value] += 1
            
            # Check if any value dominates (>80%)
            most_common = counts.most_common(1)[0]
            most_common_value, most_common_count = most_common
            most_common_pct = (most_common_count / len(self.examples)) * 100
            
            if most_common_pct > 80:
                self.warnings.append(
                    f"{field}: '{most_common_value}' dominates with {most_common_pct:.1f}% (imbalanced)"
                )
    
    def validate_text_content(self):
        """Check text content is present and reasonable."""
        print(f"\nValidating text content...")
        
        empty_text = 0
        too_short = 0
        too_long = 0
        
        for example in self.examples:
            text = example.get("text", "")
            
            if not text or len(text.strip()) == 0:
                empty_text += 1
            elif len(text) < 10:
                too_short += 1
            elif len(text) > 10000:
                too_long += 1
        
        if empty_text > 0:
            self.errors.append(f"Empty text: {empty_text} examples")
        
        if too_short > 0:
            pct = (too_short / len(self.examples)) * 100
            self.warnings.append(f"Very short text (<10 chars): {too_short} examples ({pct:.1f}%)")
        
        if too_long > 0:
            pct = (too_long / len(self.examples)) * 100
            self.warnings.append(f"Very long text (>10K chars): {too_long} examples ({pct:.1f}%)")
        
        if empty_text == 0 and too_short == 0:
            print(f"✅ Text content looks good")
    
    def run_validation(self) -> bool:
        """Run all validation checks."""
        print(f"{'='*80}")
        print(f"GENESIS CORPUS VALIDATION")
        print(f"{'='*80}")
        
        self.load_corpus()
        
        if not self.examples:
            print(f"\n❌ No examples found in corpus!")
            return False
        
        self.validate_metadata_fields()
        self.validate_metadata_values()
        self.validate_text_content()
        self.validate_pattern_coverage()
        self.validate_balance()
        
        # Summary
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n✅ CORPUS IS VALID - Ready for Genesis training!")
            return True
        elif not self.errors:
            print(f"\n⚠️  CORPUS HAS WARNINGS - Proceed with caution")
            return True
        else:
            print(f"\n❌ CORPUS HAS ERRORS - Fix before training")
            return False


def main():
    parser = argparse.ArgumentParser(description="Validate Genesis training corpus")
    parser.add_argument(
        "--corpus",
        type=Path,
        required=True,
        help="Path to corpus JSONL (train/val/test split)"
    )
    
    args = parser.parse_args()
    
    validator = CorpusValidator(args.corpus)
    is_valid = validator.run_validation()
    
    exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

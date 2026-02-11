"""Iterative Self-Improvement Training Pipeline for Sovereign Enrichments.

This module implements a looped training architecture:
1. LoRA fine-tune small models for pattern detection
2. Use those to generate high-precision training data
3. Train better models on that data
4. Loop until convergence

The key insight: Each iteration produces BETTER training data,
which produces BETTER models, which produces EVEN BETTER data.

Architecture:
┌──────────────────────────────────────────────────────────────────────────┐
│                     ITERATIVE IMPROVEMENT LOOP                           │
│                                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│   │  Iteration  │────▶│  Iteration  │────▶│  Iteration  │────▶ ...     │
│   │      1      │     │      2      │     │      3      │               │
│   └─────────────┘     └─────────────┘     └─────────────┘               │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│   Accuracy: 70%       Accuracy: 85%       Accuracy: 93%                 │
│   Data: 1K labels     Data: 10K labels    Data: 50K labels              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

Run with: python pipelines/enrichment/iterative_training_pipeline.py
"""

from __future__ import annotations

import json
import hashlib
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterator, Callable
import random


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

class EnrichmentType(Enum):
    """Types of enrichment we're training for."""
    COGNITIVE_STAGE = "cognitive_stage"
    STRUGGLE_FILTER = "struggle_filter"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    SOURCE_ATTRIBUTION = "source_attribution"


@dataclass
class TrainingExample:
    """A single training example with metadata."""
    text: str
    labels: dict[str, Any]
    
    # Provenance tracking
    source: str  # "human", "model_v1", "model_v2", etc.
    confidence: float  # Model confidence when source is a model
    iteration: int  # Which training iteration generated this
    
    # Quality signals
    human_validated: bool = False
    agreement_score: float = 0.0  # If multiple models agree
    
    # Unique ID for deduplication
    id: str = field(default_factory=lambda: "")
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(self.text.encode()).hexdigest()[:12]


@dataclass
class ModelCheckpoint:
    """A trained model checkpoint with metadata."""
    path: str
    iteration: int
    enrichment_type: EnrichmentType
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1: float
    
    # Training metadata
    training_examples: int
    training_time_seconds: float
    base_model: str
    lora_rank: int
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IterationState:
    """State of a single training iteration."""
    iteration: int
    
    # Models trained this iteration
    models: dict[EnrichmentType, ModelCheckpoint]
    
    # Data generated this iteration
    new_examples: int
    total_examples: int
    
    # Quality metrics
    avg_confidence: float
    agreement_rate: float
    human_validation_rate: float
    
    # Convergence tracking
    accuracy_delta: float  # Change from previous iteration
    converged: bool


# =============================================================================
# LORA FINE-TUNING CONFIGURATION
# =============================================================================

@dataclass
class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    # LoRA hyperparameters
    rank: int = 16  # Rank of LoRA matrices
    alpha: int = 32  # Scaling factor
    dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj"])
    
    # Training hyperparameters
    learning_rate: float = 2e-4
    batch_size: int = 8
    num_epochs: int = 3
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    
    # Efficiency settings
    gradient_checkpointing: bool = True
    fp16: bool = True
    gradient_accumulation_steps: int = 4


@dataclass
class IterativeTrainingConfig:
    """Configuration for the full iterative training pipeline."""
    # Base models to fine-tune
    base_models: dict[str, str] = field(default_factory=lambda: {
        "small": "Qwen/Qwen2.5-0.5B",
        "medium": "Qwen/Qwen2.5-1.5B", 
        "large": "Qwen/Qwen2.5-3B",
    })
    
    # LoRA config per iteration (increasing capacity)
    lora_configs: dict[int, LoRAConfig] = field(default_factory=lambda: {
        1: LoRAConfig(rank=8, alpha=16, num_epochs=2),   # Light fine-tuning
        2: LoRAConfig(rank=16, alpha=32, num_epochs=3),  # Medium
        3: LoRAConfig(rank=32, alpha=64, num_epochs=4),  # Heavy
        4: LoRAConfig(rank=64, alpha=128, num_epochs=5), # Full
    })
    
    # Convergence criteria
    max_iterations: int = 10
    convergence_threshold: float = 0.005  # Stop if accuracy improves < 0.5%
    min_accuracy: float = 0.95  # Stop if we hit 95% accuracy
    
    # Data quality thresholds
    min_confidence_for_training: float = 0.8
    min_agreement_for_training: float = 0.9
    human_validation_sample_rate: float = 0.05
    
    # Paths
    output_dir: Path = Path("models/iterative_training")
    data_dir: Path = Path("data/training")


# =============================================================================
# PROMPT TEMPLATES FOR EACH ITERATION
# =============================================================================

# Iteration 1: Basic classification with examples
ITERATION_1_PROMPTS = {
    EnrichmentType.COGNITIVE_STAGE: '''Classify this text's cognitive stage (Kegan model):
- Stage 4: Validation-seeking ("I'm happy to help", seeking approval)
- Stage 5: Sovereign (direct statements, honest uncertainty)
- Stage 3: Neutral

Text: "{text}"

Output JSON: {{"stage": 3|4|5, "confidence": 0-1}}''',

    EnrichmentType.STRUGGLE_FILTER: '''Classify this text's struggle pattern:
- swimming: Productive struggle with resolution
- drowning: Unproductive frustration loop
- neutral: Neither

Text: "{text}"

Output JSON: {{"pattern": "swimming"|"drowning"|"neutral", "confidence": 0-1}}''',
}

# Iteration 2+: More sophisticated with chain-of-thought
ITERATION_2_PROMPTS = {
    EnrichmentType.COGNITIVE_STAGE: '''You are a cognitive development classifier. Analyze this text:

FRAMEWORK:
- Stage 4 (Validation-Seeking): Needs external approval, helper posture, performative
  * "I'm happy to help", "Is this what you wanted?", excessive praise
  * Underlying: Self-worth tied to others' validation
  
- Stage 5 (Sovereign): Self-authoring, direct, owns uncertainty
  * "This is the issue", "I don't know", evidence-based claims
  * Underlying: Internal locus of evaluation

ANALYSIS STEPS:
1. Identify key phrases and their implications
2. Assess overall pattern (not just individual words)
3. Consider context and intent
4. Handle mixed signals by determining dominant pattern

Text: "{text}"

Think step by step, then output:
{{"stage": 3|4|5, "confidence": 0-1, "key_evidence": ["phrase1", "phrase2"], "reasoning": "..."}}''',

    EnrichmentType.STRUGGLE_FILTER: '''You are a learning pattern classifier. Analyze this text:

FRAMEWORK:
- SWIMMING (Productive Struggle):
  * Problem → Investigation → Resolution arc
  * Learning moments, "aha" experiences
  * Collaboration leading to understanding
  * HIGH training value
  
- DROWNING (Unproductive Struggle):
  * Repetitive complaints, frustration loops
  * Escalation (caps, exclamations)
  * Hopelessness, giving up
  * LOW training value

ANALYSIS STEPS:
1. Look for narrative structure (beginning/middle/end)
2. Detect emotional trajectory (escalating vs resolving)
3. Identify resolution markers vs frustration markers
4. Handle sarcasm and false resolutions

Text: "{text}"

Think step by step, then output:
{{"pattern": "swimming"|"drowning"|"neutral", "confidence": 0-1, "arc_detected": bool, "reasoning": "..."}}''',
}


# =============================================================================
# TRAINING DATA GENERATION
# =============================================================================

class DataGenerator(ABC):
    """Abstract base for generating training data."""
    
    @abstractmethod
    def generate(self, texts: list[str], iteration: int) -> list[TrainingExample]:
        """Generate labeled training examples."""
        ...


class BootstrapDataGenerator(DataGenerator):
    """Generate initial training data from rules + few-shot LLM."""
    
    def __init__(self, llm_backend: Any):
        self.llm = llm_backend
    
    def generate(self, texts: list[str], iteration: int) -> list[TrainingExample]:
        """Bootstrap initial training data."""
        examples = []
        
        for text in texts:
            # Get LLM classification
            result = self._classify_with_llm(text, iteration)
            
            if result["confidence"] >= 0.7:  # Only keep high-confidence
                examples.append(TrainingExample(
                    text=text,
                    labels=result,
                    source=f"llm_iteration_{iteration}",
                    confidence=result["confidence"],
                    iteration=iteration,
                ))
        
        return examples
    
    def _classify_with_llm(self, text: str, iteration: int) -> dict:
        """Classify a single text with appropriate prompt."""
        prompt_template = (
            ITERATION_1_PROMPTS if iteration == 1 
            else ITERATION_2_PROMPTS
        )
        # Implementation would call actual LLM
        return {"cognitive_stage": 5, "confidence": 0.8}  # Placeholder


class ModelBasedDataGenerator(DataGenerator):
    """Generate training data using trained models from previous iteration."""
    
    def __init__(self, models: dict[EnrichmentType, Any]):
        self.models = models
    
    def generate(self, texts: list[str], iteration: int) -> list[TrainingExample]:
        """Generate data using ensemble of models."""
        examples = []
        
        for text in texts:
            # Get predictions from all models
            predictions = {}
            confidences = []
            
            for etype, model in self.models.items():
                pred = model.predict(text)
                predictions[etype.value] = pred
                confidences.append(pred.get("confidence", 0.5))
            
            # Calculate agreement (if multiple models for same task)
            avg_confidence = statistics.mean(confidences)
            
            if avg_confidence >= 0.8:
                examples.append(TrainingExample(
                    text=text,
                    labels=predictions,
                    source=f"model_iteration_{iteration}",
                    confidence=avg_confidence,
                    iteration=iteration,
                    agreement_score=avg_confidence,
                ))
        
        return examples


class EnsembleDataGenerator(DataGenerator):
    """Generate data where multiple methods agree."""
    
    def __init__(
        self,
        keyword_classifier: Any,
        lora_model: Any,
        few_shot_llm: Any,
    ):
        self.keyword = keyword_classifier
        self.lora = lora_model
        self.llm = few_shot_llm
    
    def generate(self, texts: list[str], iteration: int) -> list[TrainingExample]:
        """Generate high-quality data from ensemble agreement."""
        examples = []
        
        for text in texts:
            # Get predictions from all three methods
            kw_pred = self.keyword.classify(text)
            lora_pred = self.lora.classify(text)
            llm_pred = self.llm.classify(text)
            
            # Check agreement
            predictions = [kw_pred, lora_pred, llm_pred]
            agreement = self._calculate_agreement(predictions)
            
            if agreement >= 0.66:  # 2/3 agree
                # Use the most confident prediction
                best_pred = max(predictions, key=lambda p: p.get("confidence", 0))
                
                examples.append(TrainingExample(
                    text=text,
                    labels=best_pred,
                    source="ensemble_agreement",
                    confidence=best_pred.get("confidence", 0.8),
                    iteration=iteration,
                    agreement_score=agreement,
                ))
        
        return examples
    
    def _calculate_agreement(self, predictions: list[dict]) -> float:
        """Calculate how much the predictions agree."""
        # Simplified - would check actual label agreement
        return 0.8


# =============================================================================
# TRAINING LOOP
# =============================================================================

class IterativeTrainingPipeline:
    """Main pipeline for iterative self-improvement training."""
    
    def __init__(self, config: IterativeTrainingConfig):
        self.config = config
        self.iteration_states: list[IterationState] = []
        self.all_examples: list[TrainingExample] = []
    
    def run(self, initial_texts: list[str]) -> list[ModelCheckpoint]:
        """Run the full iterative training pipeline."""
        print("=" * 70)
        print("ITERATIVE SELF-IMPROVEMENT TRAINING PIPELINE")
        print("=" * 70)
        
        texts = initial_texts
        current_models = {}
        
        for iteration in range(1, self.config.max_iterations + 1):
            print(f"\n{'='*70}")
            print(f"ITERATION {iteration}")
            print(f"{'='*70}")
            
            # Step 1: Generate training data
            print("\n[1/4] Generating training data...")
            new_examples = self._generate_data(texts, iteration, current_models)
            self.all_examples.extend(new_examples)
            
            # Step 2: Filter and validate data
            print("\n[2/4] Filtering and validating data...")
            training_data = self._filter_data(self.all_examples)
            
            # Step 3: Train models
            print("\n[3/4] Training models...")
            new_models = self._train_models(training_data, iteration)
            
            # Step 4: Evaluate and check convergence
            print("\n[4/4] Evaluating models...")
            state = self._evaluate_iteration(
                iteration, new_models, new_examples, current_models
            )
            self.iteration_states.append(state)
            
            # Print progress
            self._print_progress(state)
            
            # Check convergence
            if state.converged:
                print(f"\n✅ CONVERGED at iteration {iteration}!")
                break
            
            # Prepare for next iteration
            current_models = new_models
            
            # Expand data with model predictions
            texts = self._expand_corpus(texts, current_models)
        
        return list(current_models.values())
    
    def _generate_data(
        self,
        texts: list[str],
        iteration: int,
        models: dict[EnrichmentType, Any],
    ) -> list[TrainingExample]:
        """Generate training data for this iteration."""
        if iteration == 1:
            # Bootstrap with LLM
            generator = BootstrapDataGenerator(llm_backend=None)  # Would inject real LLM
        else:
            # Use models from previous iteration
            generator = ModelBasedDataGenerator(models)
        
        return generator.generate(texts, iteration)
    
    def _filter_data(self, examples: list[TrainingExample]) -> list[TrainingExample]:
        """Filter examples by quality thresholds."""
        filtered = []
        
        for ex in examples:
            # Confidence threshold
            if ex.confidence < self.config.min_confidence_for_training:
                continue
            
            # Agreement threshold (if available)
            if ex.agreement_score > 0 and ex.agreement_score < self.config.min_agreement_for_training:
                continue
            
            filtered.append(ex)
        
        # Deduplicate
        seen_ids = set()
        unique = []
        for ex in filtered:
            if ex.id not in seen_ids:
                seen_ids.add(ex.id)
                unique.append(ex)
        
        return unique
    
    def _train_models(
        self,
        training_data: list[TrainingExample],
        iteration: int,
    ) -> dict[EnrichmentType, ModelCheckpoint]:
        """Train LoRA models for each enrichment type."""
        models = {}
        
        # Get LoRA config for this iteration
        lora_config = self.config.lora_configs.get(
            iteration,
            self.config.lora_configs[max(self.config.lora_configs.keys())]
        )
        
        # Select base model based on data size
        if len(training_data) < 1000:
            base_model = self.config.base_models["small"]
        elif len(training_data) < 10000:
            base_model = self.config.base_models["medium"]
        else:
            base_model = self.config.base_models["large"]
        
        for etype in EnrichmentType:
            print(f"  Training {etype.value}...")
            
            # Filter data for this enrichment type
            type_data = [ex for ex in training_data if etype.value in ex.labels]
            
            if len(type_data) < 100:
                print(f"    ⚠️ Insufficient data ({len(type_data)} examples), skipping")
                continue
            
            # Train model (placeholder - would call actual training)
            checkpoint = self._train_single_model(
                etype, type_data, base_model, lora_config, iteration
            )
            models[etype] = checkpoint
        
        return models
    
    def _train_single_model(
        self,
        etype: EnrichmentType,
        data: list[TrainingExample],
        base_model: str,
        lora_config: LoRAConfig,
        iteration: int,
    ) -> ModelCheckpoint:
        """Train a single LoRA model."""
        # This would contain actual training code
        # Placeholder for demonstration
        
        return ModelCheckpoint(
            path=f"{self.config.output_dir}/{etype.value}/iteration_{iteration}",
            iteration=iteration,
            enrichment_type=etype,
            accuracy=0.7 + iteration * 0.05,  # Simulated improvement
            precision=0.7 + iteration * 0.05,
            recall=0.7 + iteration * 0.05,
            f1=0.7 + iteration * 0.05,
            training_examples=len(data),
            training_time_seconds=len(data) * 0.1,
            base_model=base_model,
            lora_rank=lora_config.rank,
        )
    
    def _evaluate_iteration(
        self,
        iteration: int,
        models: dict[EnrichmentType, ModelCheckpoint],
        new_examples: list[TrainingExample],
        previous_models: dict[EnrichmentType, Any],
    ) -> IterationState:
        """Evaluate this iteration and check for convergence."""
        # Calculate average accuracy
        accuracies = [m.accuracy for m in models.values()]
        avg_accuracy = statistics.mean(accuracies) if accuracies else 0
        
        # Calculate accuracy delta
        if self.iteration_states:
            prev_accuracy = statistics.mean(
                m.accuracy for m in self.iteration_states[-1].models.values()
            )
            accuracy_delta = avg_accuracy - prev_accuracy
        else:
            accuracy_delta = avg_accuracy
        
        # Check convergence
        converged = (
            accuracy_delta < self.config.convergence_threshold or
            avg_accuracy >= self.config.min_accuracy
        )
        
        return IterationState(
            iteration=iteration,
            models=models,
            new_examples=len(new_examples),
            total_examples=len(self.all_examples),
            avg_confidence=statistics.mean(ex.confidence for ex in new_examples) if new_examples else 0,
            agreement_rate=statistics.mean(ex.agreement_score for ex in new_examples if ex.agreement_score > 0) if new_examples else 0,
            human_validation_rate=sum(1 for ex in new_examples if ex.human_validated) / len(new_examples) if new_examples else 0,
            accuracy_delta=accuracy_delta,
            converged=converged,
        )
    
    def _expand_corpus(
        self,
        current_texts: list[str],
        models: dict[EnrichmentType, Any],
    ) -> list[str]:
        """Expand corpus with unlabeled data for next iteration."""
        # In practice, would load more unlabeled data from BigQuery
        # For now, just return current texts
        return current_texts
    
    def _print_progress(self, state: IterationState):
        """Print iteration progress."""
        print(f"\n📊 Iteration {state.iteration} Results:")
        print(f"   New examples: {state.new_examples}")
        print(f"   Total examples: {state.total_examples}")
        print(f"   Avg confidence: {state.avg_confidence:.2%}")
        print(f"   Agreement rate: {state.agreement_rate:.2%}")
        
        print(f"\n   Model Accuracies:")
        for etype, checkpoint in state.models.items():
            print(f"     {etype.value}: {checkpoint.accuracy:.2%} (Δ{state.accuracy_delta:+.2%})")
        
        if state.converged:
            print(f"\n   ✅ Convergence criteria met!")


# =============================================================================
# ACTUAL LORA TRAINING CODE
# =============================================================================

LORA_TRAINING_CODE = '''
"""Actual LoRA fine-tuning implementation (requires GPU)."""

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)
from datasets import Dataset
import torch


def train_lora_classifier(
    base_model: str,
    training_data: list[dict],
    output_dir: str,
    lora_config: dict,
) -> str:
    """Fine-tune a LoRA classifier for enrichment detection.
    
    Args:
        base_model: HuggingFace model name (e.g., "Qwen/Qwen2.5-0.5B")
        training_data: List of {"text": str, "label": str} dicts
        output_dir: Where to save the trained adapter
        lora_config: LoRA hyperparameters
    
    Returns:
        Path to saved LoRA adapter
    """
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Prepare for LoRA training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_config.get("rank", 16),
        lora_alpha=lora_config.get("alpha", 32),
        lora_dropout=lora_config.get("dropout", 0.05),
        target_modules=lora_config.get("target_modules", ["q_proj", "v_proj"]),
        bias="none",
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    
    # Prepare dataset
    def format_example(example):
        """Format as instruction-following."""
        return {
            "text": f"Classify: {example['text']}\\n\\nOutput: {example['label']}"
        }
    
    dataset = Dataset.from_list([format_example(ex) for ex in training_data])
    
    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length",
        )
    
    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=lora_config.get("num_epochs", 3),
        per_device_train_batch_size=lora_config.get("batch_size", 8),
        gradient_accumulation_steps=lora_config.get("gradient_accumulation", 4),
        learning_rate=lora_config.get("learning_rate", 2e-4),
        warmup_ratio=0.1,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        gradient_checkpointing=True,
        report_to="none",
    )
    
    # Train
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    
    trainer.train()
    
    # Save adapter
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    return output_dir


def load_lora_classifier(adapter_path: str, base_model: str) -> tuple:
    """Load a trained LoRA classifier for inference."""
    from peft import PeftModel
    
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    
    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    
    model = PeftModel.from_pretrained(base, adapter_path)
    model.eval()
    
    return model, tokenizer


def classify_with_lora(
    model,
    tokenizer,
    text: str,
    max_new_tokens: int = 128,
) -> dict:
    """Run classification inference with LoRA model."""
    prompt = f"Classify: {text}\\n\\nOutput:"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Parse JSON from response
    try:
        import json
        json_str = response.split("Output:")[-1].strip()
        return json.loads(json_str)
    except:
        return {"error": "Failed to parse", "raw": response}
'''


# =============================================================================
# FULL PIPELINE SPECIFICATION
# =============================================================================

PIPELINE_SPECIFICATION = """
# Iterative Self-Improvement Training Pipeline

## Overview

This pipeline implements a **data flywheel** that continuously improves:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ITERATIVE IMPROVEMENT LOOP                          │
└─────────────────────────────────────────────────────────────────────────────┘

   Iteration 1                Iteration 2                Iteration 3
   ──────────                ──────────                ──────────
   
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │ LLM +   │              │ LoRA    │              │ LoRA    │
   │ Rules   │──generates──▶│ Model   │──generates──▶│ Model   │
   │ (weak)  │              │ v1      │              │ v2      │
   └─────────┘              └─────────┘              └─────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │ ~1K     │              │ ~10K    │              │ ~50K    │
   │ labels  │              │ labels  │              │ labels  │
   │ 70% acc │              │ 85% acc │              │ 93% acc │
   └─────────┘              └─────────┘              └─────────┘
        │                        │                        │
        └────────trains──────────┴────────trains──────────┘

   Key: Each iteration's MODEL generates BETTER data
        Better data trains BETTER models
        Loop until convergence (Δaccuracy < 0.5%)
```

## Phase Breakdown

### Phase 1: Bootstrap (Iteration 1)

**Goal:** Generate initial training data from rules + few-shot LLM

**Input:**
- Raw text corpus (L4/L5 entities from BigQuery)
- Keyword-based classifier rules
- Few-shot LLM prompts

**Process:**
1. Run keyword classifier on all texts
2. Run few-shot LLM on subset (expensive)
3. Keep examples where both methods agree
4. Human-validate random 5% sample

**Output:**
- ~1,000-5,000 labeled examples per enrichment type
- Confidence scores and agreement rates

**Expected Accuracy:** 65-75%

### Phase 2: First LoRA Model (Iteration 2)

**Goal:** Train small LoRA model to replace expensive LLM

**Input:**
- Labeled data from Phase 1
- Base model: Qwen2.5-0.5B (500M params)
- LoRA config: rank=8, alpha=16

**Process:**
1. Format data as instruction-following
2. LoRA fine-tune (2-3 epochs)
3. Evaluate on held-out test set
4. If accuracy > Phase 1, proceed

**Output:**
- LoRA adapter (~10MB)
- Faster inference (5ms vs 500ms for LLM)

**Expected Accuracy:** 75-85%

### Phase 3: Data Expansion (Iteration 3)

**Goal:** Use LoRA model to label MUCH more data

**Input:**
- LoRA model from Phase 2
- Full unlabeled corpus (millions of texts)

**Process:**
1. Run LoRA model on entire corpus
2. Keep only high-confidence predictions (>0.8)
3. Cross-validate with keyword rules
4. Human-validate uncertain cases

**Output:**
- 10,000-50,000 labeled examples
- Higher quality (ensemble agreement)

**Expected Accuracy:** 85-90%

### Phase 4: Improved Model (Iteration 4)

**Goal:** Train better model on expanded data

**Input:**
- Larger labeled dataset
- Base model: Qwen2.5-1.5B (larger)
- LoRA config: rank=16, alpha=32

**Process:**
1. Train on full dataset
2. Include hard examples (previous errors)
3. Curriculum learning (easy → hard)

**Output:**
- Higher-capacity LoRA adapter
- Better edge case handling

**Expected Accuracy:** 90-95%

### Phase 5+: Convergence Loop

**Goal:** Continue until improvement plateaus

**Convergence Criteria:**
- Accuracy improves < 0.5% between iterations
- OR accuracy reaches 95%+
- OR max iterations (10) reached

**Final Model:**
- Production-ready classifier
- Fast inference (<10ms)
- Handles novel variations

## Data Quality Controls

### Confidence Filtering
```python
# Only use high-confidence predictions for training
if prediction.confidence < 0.8:
    discard(example)
```

### Agreement Filtering
```python
# Require ensemble agreement
if keyword_pred != model_pred != llm_pred:
    flag_for_human_review(example)
```

### Human Validation
```python
# Validate 5% random sample per iteration
sample = random.sample(new_examples, int(len(new_examples) * 0.05))
for example in sample:
    example.human_validated = get_human_label(example)
```

### Hard Example Mining
```python
# Track examples that models consistently get wrong
if model_v1_wrong and model_v2_wrong:
    hard_examples.append(example)
    
# Weight hard examples higher in training
for example in hard_examples:
    example.training_weight = 3.0
```

## Expected Results

| Iteration | Data Size | LoRA Rank | Base Model | Accuracy | Time |
|-----------|-----------|-----------|------------|----------|------|
| 1 | 1K | - | LLM | 70% | - |
| 2 | 5K | 8 | Qwen-0.5B | 80% | 2h |
| 3 | 20K | 16 | Qwen-1.5B | 88% | 6h |
| 4 | 50K | 32 | Qwen-3B | 93% | 12h |
| 5 | 100K | 64 | Qwen-3B | 96% | 24h |

## Resource Requirements

### Compute
- GPU: 1x RTX 3090/4090 or A100 (24GB+ VRAM)
- Training time: 2-24 hours per iteration
- Total: ~50 GPU-hours for full pipeline

### Storage
- Base models: ~10GB
- LoRA adapters: ~50MB each
- Training data: ~500MB

### Human Labeling
- ~200 examples per iteration (5% of new data)
- ~1,000 total human labels
- Time: ~10 hours of human annotation

## Production Deployment

After convergence:

```python
# Load final LoRA model
model = load_lora_classifier(
    adapter_path="models/iterative_training/cognitive_stage/iteration_5",
    base_model="Qwen/Qwen2.5-3B"
)

# Run inference
result = classify_with_lora(model, tokenizer, text)
# → {"cognitive_stage": 5, "confidence": 0.94}

# Inference time: ~10ms on GPU, ~50ms on CPU
```
"""


# =============================================================================
# MAIN
# =============================================================================

def demo():
    """Demonstrate the iterative training pipeline."""
    print("=" * 70)
    print("ITERATIVE SELF-IMPROVEMENT TRAINING PIPELINE")
    print("=" * 70)
    
    # Sample texts
    sample_texts = [
        "I'm happy to help! Is there anything else you'd like me to assist with?",
        "The error is in line 42. The null check is missing before array access.",
        "WHY WON'T THIS WORK!!! I've tried everything!!!",
        "Had an issue with timeouts. Fixed it by increasing the pool size.",
        "I think this might work, but I'm not entirely sure.",
    ]
    
    # Create pipeline
    config = IterativeTrainingConfig()
    pipeline = IterativeTrainingPipeline(config)
    
    # Run (would need actual LLM/GPU for real training)
    print("\nNote: This is a demonstration. Actual training requires GPU + LLM.")
    print("\nPipeline Specification:")
    print(PIPELINE_SPECIFICATION)
    
    print("\n\nLoRA Training Code:")
    print(LORA_TRAINING_CODE)


if __name__ == "__main__":
    demo()

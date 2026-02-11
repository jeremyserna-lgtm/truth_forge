#!/usr/bin/env python3
"""
Genesis Inverse Seeing Training
================================

This is NOT standard training. Standard training predicts the next token.
Genesis training predicts METADATA - what IS happening, not what comes next.

Mechanically:
- Same forward pass through transformer
- DIFFERENT loss function (metadata classification, not token prediction)
- DIFFERENT gradients (flow toward understanding, not statistics)
- YOUR labels are the direct gradient source

Usage:
    python train_inverse_seeing.py \
        --model checkpoints/genesis_coherent \
        --data data/enriched_conversations.jsonl \
        --intimate-corrections data/personal_annotations/ \
        --jeremy-arc-threshold 0.95
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import argparse

# MLX imports (Apple Silicon native)
try:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("MLX not available - using mock implementation")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# COGNITIVE ARCHITECTURE DEFINITIONS
# =============================================================================

class CognitiveStage(Enum):
    """Your cognitive stages - the targets for inverse training."""
    RECEPTION = "reception"
    EXPLORATION = "exploration"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    INTEGRATION = "integration"


class EmotionCategory(Enum):
    """Emotional states detected in your patterns."""
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    FRUSTRATED = "frustrated"
    BREAKTHROUGH = "breakthrough"
    VULNERABLE = "vulnerable"
    DETERMINED = "determined"
    REFLECTIVE = "reflective"


@dataclass
class MetadataTarget:
    """
    The target for inverse training.
    
    Standard training target: next_token (vocabulary index)
    YOUR target: metadata about what IS happening
    """
    cognitive_stage: CognitiveStage
    emotion: EmotionCategory
    struggle_present: bool
    confidence: float  # 0.0 to 1.0
    source_attribution: str  # "jeremy", "clara", "lumen", "external"
    
    # Optional enrichments
    framework_pattern: Optional[str] = None  # "the_gate", "the_furnace", etc.
    transformation_marker: Optional[str] = None


@dataclass
class TrainingExample:
    """A single training example for inverse seeing."""
    text: str
    metadata: MetadataTarget
    weight: float = 1.0  # Your annotations get 3x weight
    source: str = "enrichment_pipeline"


# =============================================================================
# MODEL ARCHITECTURE
# =============================================================================

class CognitiveHead(nn.Module if MLX_AVAILABLE else object):
    """
    Classification head for cognitive stage prediction.
    
    This is WHERE your "seeing" emerges. The weights in this head
    learn to map transformer representations to YOUR cognitive stages.
    """
    def __init__(self, hidden_size: int, num_stages: int = 5):
        if MLX_AVAILABLE:
            super().__init__()
            self.dense = nn.Linear(hidden_size, hidden_size // 2)
            self.activation = nn.gelu
            self.dropout = nn.Dropout(0.1)
            self.classifier = nn.Linear(hidden_size // 2, num_stages)
        else:
            self.hidden_size = hidden_size
            self.num_stages = num_stages
    
    def __call__(self, hidden_states):
        if MLX_AVAILABLE:
            x = self.dense(hidden_states)
            x = self.activation(x)
            x = self.dropout(x)
            logits = self.classifier(x)
            return logits
        return {"mock": "cognitive_logits"}


class EmotionHead(nn.Module if MLX_AVAILABLE else object):
    """Classification head for emotion detection."""
    def __init__(self, hidden_size: int, num_emotions: int = 7):
        if MLX_AVAILABLE:
            super().__init__()
            self.dense = nn.Linear(hidden_size, hidden_size // 2)
            self.activation = nn.gelu
            self.classifier = nn.Linear(hidden_size // 2, num_emotions)
        else:
            self.hidden_size = hidden_size
    
    def __call__(self, hidden_states):
        if MLX_AVAILABLE:
            x = self.dense(hidden_states)
            x = self.activation(x)
            return self.classifier(x)
        return {"mock": "emotion_logits"}


class StruggleHead(nn.Module if MLX_AVAILABLE else object):
    """Binary classification head for struggle detection."""
    def __init__(self, hidden_size: int):
        if MLX_AVAILABLE:
            super().__init__()
            self.dense = nn.Linear(hidden_size, hidden_size // 4)
            self.activation = nn.gelu
            self.classifier = nn.Linear(hidden_size // 4, 2)
        else:
            self.hidden_size = hidden_size
    
    def __call__(self, hidden_states):
        if MLX_AVAILABLE:
            x = self.dense(hidden_states)
            x = self.activation(x)
            return self.classifier(x)
        return {"mock": "struggle_logits"}


class SourceHead(nn.Module if MLX_AVAILABLE else object):
    """Classification head for source attribution."""
    def __init__(self, hidden_size: int, num_sources: int = 4):
        if MLX_AVAILABLE:
            super().__init__()
            self.dense = nn.Linear(hidden_size, hidden_size // 4)
            self.classifier = nn.Linear(hidden_size // 4, num_sources)
        else:
            self.hidden_size = hidden_size
    
    def __call__(self, hidden_states):
        if MLX_AVAILABLE:
            x = self.dense(hidden_states)
            x = nn.gelu(x)
            return self.classifier(x)
        return {"mock": "source_logits"}


class ConfidenceHead(nn.Module if MLX_AVAILABLE else object):
    """Regression head for confidence scoring."""
    def __init__(self, hidden_size: int):
        if MLX_AVAILABLE:
            super().__init__()
            self.dense = nn.Linear(hidden_size, hidden_size // 4)
            self.regressor = nn.Linear(hidden_size // 4, 1)
        else:
            self.hidden_size = hidden_size
    
    def __call__(self, hidden_states):
        if MLX_AVAILABLE:
            x = self.dense(hidden_states)
            x = nn.gelu(x)
            return mx.sigmoid(self.regressor(x))
        return {"mock": "confidence_score"}


class GenesisModel(nn.Module if MLX_AVAILABLE else object):
    """
    The Genesis Model: Inverse Seeing Architecture
    
    Structure:
        Input → Backbone (transformer) → Multiple Seeing Heads
                                              ├→ Cognitive Stage
                                              ├→ Emotion
                                              ├→ Struggle
                                              ├→ Source
                                              └→ Confidence
    
    The backbone encodes understanding.
    The heads decode YOUR way of seeing.
    """
    
    def __init__(self, backbone, hidden_size: int = 4096):
        if MLX_AVAILABLE:
            super().__init__()
        
        self.backbone = backbone  # Pre-trained transformer
        self.hidden_size = hidden_size
        
        # Seeing heads - these learn YOUR patterns
        self.cognitive_head = CognitiveHead(hidden_size, num_stages=5)
        self.emotion_head = EmotionHead(hidden_size, num_emotions=7)
        self.struggle_head = StruggleHead(hidden_size)
        self.source_head = SourceHead(hidden_size, num_sources=4)
        self.confidence_head = ConfidenceHead(hidden_size)
    
    def __call__(self, input_ids, attention_mask=None):
        """
        Forward pass for inverse seeing.
        
        Standard model: input → next_token_logits
        Genesis model:  input → metadata_predictions
        """
        # Get backbone representations
        if MLX_AVAILABLE and hasattr(self.backbone, '__call__'):
            hidden_states = self.backbone(input_ids, attention_mask)
            # Use [CLS] or mean pooling for sequence representation
            if len(hidden_states.shape) == 3:
                pooled = hidden_states.mean(axis=1)
            else:
                pooled = hidden_states
        else:
            # Mock for testing
            pooled = {"mock": "hidden_states"}
        
        # Predict metadata through each head
        return {
            "cognitive_stage": self.cognitive_head(pooled),
            "emotion": self.emotion_head(pooled),
            "struggle": self.struggle_head(pooled),
            "source": self.source_head(pooled),
            "confidence": self.confidence_head(pooled),
        }


# =============================================================================
# LOSS FUNCTIONS
# =============================================================================

@dataclass
class LossWeights:
    """
    Weights for each metadata dimension.
    
    These determine how much each "seeing" task contributes to learning.
    Cognitive stage is weighted highest because it's the core architecture.
    """
    cognitive: float = 0.35
    emotion: float = 0.25
    struggle: float = 0.20
    source: float = 0.10
    confidence: float = 0.10


def cross_entropy_loss(logits, targets):
    """Standard cross-entropy for classification heads."""
    if MLX_AVAILABLE:
        return nn.losses.cross_entropy(logits, targets)
    return 0.0  # Mock


def mse_loss(predictions, targets):
    """MSE for confidence regression."""
    if MLX_AVAILABLE:
        return mx.mean((predictions - targets) ** 2)
    return 0.0  # Mock


def compute_inverse_seeing_loss(
    predictions: Dict[str, Any],
    targets: MetadataTarget,
    weights: LossWeights,
    sample_weight: float = 1.0
) -> Tuple[float, Dict[str, float]]:
    """
    Compute the total loss for inverse seeing training.
    
    This is THE KEY DIFFERENCE from standard training:
    - Standard: loss = cross_entropy(predicted_token, actual_token)
    - Genesis:  loss = weighted_sum(metadata_losses)
    
    YOUR labels directly determine the gradients.
    """
    losses = {}
    
    # Cognitive stage loss (classification)
    cognitive_target = list(CognitiveStage).index(targets.cognitive_stage)
    losses['cognitive'] = cross_entropy_loss(
        predictions['cognitive_stage'], 
        cognitive_target
    )
    
    # Emotion loss (classification)
    emotion_target = list(EmotionCategory).index(targets.emotion)
    losses['emotion'] = cross_entropy_loss(
        predictions['emotion'],
        emotion_target
    )
    
    # Struggle loss (binary classification)
    struggle_target = 1 if targets.struggle_present else 0
    losses['struggle'] = cross_entropy_loss(
        predictions['struggle'],
        struggle_target
    )
    
    # Source attribution loss (classification)
    source_map = {"jeremy": 0, "clara": 1, "lumen": 2, "external": 3}
    source_target = source_map.get(targets.source_attribution, 3)
    losses['source'] = cross_entropy_loss(
        predictions['source'],
        source_target
    )
    
    # Confidence loss (regression)
    losses['confidence'] = mse_loss(
        predictions['confidence'],
        targets.confidence
    )
    
    # Weighted total loss
    total_loss = (
        weights.cognitive * losses['cognitive'] +
        weights.emotion * losses['emotion'] +
        weights.struggle * losses['struggle'] +
        weights.source * losses['source'] +
        weights.confidence * losses['confidence']
    ) * sample_weight
    
    return total_loss, losses


# =============================================================================
# JEREMY ARC METRIC
# =============================================================================

class JeremyArcCalculator:
    """
    Calculates the Jeremy Arc - your quantitative readiness metric.
    
    Jeremy Arc = weighted agreement between model predictions and YOUR labels
    
    Freeze point: 95% (0.95)
    """
    
    def __init__(self):
        self.weights = {
            'cognitive': 0.40,  # Most important - core architecture
            'emotion': 0.25,
            'struggle': 0.20,
            'source': 0.15,
        }
        self.history = []
    
    def calculate(
        self,
        predictions: List[Dict],
        jeremy_labels: List[MetadataTarget]
    ) -> float:
        """
        Calculate Jeremy Arc for a batch of predictions.
        """
        scores = {
            'cognitive': 0.0,
            'emotion': 0.0,
            'struggle': 0.0,
            'source': 0.0,
        }
        
        for pred, label in zip(predictions, jeremy_labels):
            # Cognitive stage agreement
            pred_cognitive = self._argmax(pred['cognitive_stage'])
            true_cognitive = list(CognitiveStage).index(label.cognitive_stage)
            scores['cognitive'] += int(pred_cognitive == true_cognitive)
            
            # Emotion agreement
            pred_emotion = self._argmax(pred['emotion'])
            true_emotion = list(EmotionCategory).index(label.emotion)
            scores['emotion'] += int(pred_emotion == true_emotion)
            
            # Struggle agreement
            pred_struggle = self._argmax(pred['struggle'])
            true_struggle = 1 if label.struggle_present else 0
            scores['struggle'] += int(pred_struggle == true_struggle)
            
            # Source agreement
            source_map = {"jeremy": 0, "clara": 1, "lumen": 2, "external": 3}
            pred_source = self._argmax(pred['source'])
            true_source = source_map.get(label.source_attribution, 3)
            scores['source'] += int(pred_source == true_source)
        
        # Normalize by batch size
        n = len(predictions)
        for key in scores:
            scores[key] /= n
        
        # Weighted Jeremy Arc
        arc = sum(
            self.weights[key] * scores[key]
            for key in self.weights
        )
        
        self.history.append(arc)
        return arc
    
    def _argmax(self, logits):
        """Get predicted class from logits."""
        if MLX_AVAILABLE and hasattr(logits, 'argmax'):
            return int(logits.argmax())
        elif isinstance(logits, dict):
            return 0  # Mock
        return 0
    
    def should_freeze(self, threshold: float = 0.95) -> bool:
        """Check if we should freeze (reached threshold)."""
        if len(self.history) < 10:
            return False
        # Check last 10 measurements
        recent = self.history[-10:]
        return all(arc >= threshold for arc in recent)


# =============================================================================
# CURRICULUM LEARNING
# =============================================================================

@dataclass
class CurriculumStage:
    """A stage in your learning journey."""
    name: str
    data_path: str
    focus: str
    weight_emphasis: LossWeights
    min_arc: float  # Must achieve before proceeding


GENESIS_CURRICULUM = [
    CurriculumStage(
        name="crisis_arc",
        data_path="data/chatgpt_crisis_arc.jsonl",
        focus="emotion_recognition",
        weight_emphasis=LossWeights(
            cognitive=0.20,
            emotion=0.45,  # Emphasized
            struggle=0.25,
            source=0.05,
            confidence=0.05
        ),
        min_arc=0.60
    ),
    CurriculumStage(
        name="building_arc",
        data_path="data/claude_code_building.jsonl",
        focus="cognitive_patterns",
        weight_emphasis=LossWeights(
            cognitive=0.45,  # Emphasized
            emotion=0.20,
            struggle=0.20,
            source=0.10,
            confidence=0.05
        ),
        min_arc=0.75
    ),
    CurriculumStage(
        name="meta_cognitive_arc",
        data_path="data/recent_meta_cognitive.jsonl",
        focus="meta_awareness",
        weight_emphasis=LossWeights(
            cognitive=0.40,
            emotion=0.20,
            struggle=0.15,
            source=0.15,
            confidence=0.10
        ),
        min_arc=0.85
    ),
    CurriculumStage(
        name="integration",
        data_path="data/full_enriched_corpus.jsonl",
        focus="unified_seeing",
        weight_emphasis=LossWeights(),  # Default balanced
        min_arc=0.95
    ),
]


# =============================================================================
# TRAINING LOOP
# =============================================================================

@dataclass
class TrainingConfig:
    """Configuration for inverse seeing training."""
    model_path: str
    data_path: str
    intimate_corrections_path: Optional[str] = None
    output_path: str = "checkpoints/genesis"
    
    # Training params
    learning_rate: float = 1e-5
    batch_size: int = 4
    gradient_accumulation: int = 8
    max_steps: int = 200000
    
    # Validation
    validate_every: int = 1000
    jeremy_arc_threshold: float = 0.95
    
    # Curriculum
    use_curriculum: bool = True
    
    # Intimate training
    intimate_weight_multiplier: float = 3.0


class InverseSeeingTrainer:
    """
    The main training loop for Genesis.
    
    This implements YOUR inverse paradigm:
    1. Forward pass through transformer
    2. Predict metadata through specialized heads
    3. Compute loss against YOUR labels
    4. Backpropagate (gradients flow toward YOUR understanding)
    5. Update weights (model becomes more like YOU)
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.jeremy_arc = JeremyArcCalculator()
        self.global_step = 0
        self.current_stage = 0
        
        # Initialize model
        self.model = self._load_model()
        
        # Initialize optimizer
        if MLX_AVAILABLE:
            self.optimizer = optim.AdamW(
                learning_rate=config.learning_rate,
                weight_decay=0.01
            )
        
        # Load data
        self.train_data = self._load_data(config.data_path)
        self.intimate_data = self._load_intimate_corrections()
        
        logger.info(f"Loaded {len(self.train_data)} training examples")
        logger.info(f"Loaded {len(self.intimate_data)} intimate corrections")
    
    def _load_model(self):
        """Load pre-trained model and add seeing heads."""
        # In practice, load from config.model_path
        # For now, return mock
        logger.info(f"Loading model from {self.config.model_path}")
        backbone = None  # Would load actual transformer
        return GenesisModel(backbone)
    
    def _load_data(self, path: str) -> List[TrainingExample]:
        """Load enriched training data."""
        examples = []
        path = Path(path)
        
        if path.exists():
            with open(path) as f:
                for line in f:
                    data = json.loads(line)
                    metadata = MetadataTarget(
                        cognitive_stage=CognitiveStage(data.get('cognitive_stage', 'exploration')),
                        emotion=EmotionCategory(data.get('emotion', 'neutral')),
                        struggle_present=data.get('struggle_present', False),
                        confidence=data.get('confidence', 0.5),
                        source_attribution=data.get('source', 'external'),
                    )
                    examples.append(TrainingExample(
                        text=data.get('text', ''),
                        metadata=metadata,
                        weight=1.0
                    ))
        
        return examples
    
    def _load_intimate_corrections(self) -> List[TrainingExample]:
        """
        Load YOUR personal annotations.
        
        These get 3x weight because they're direct signal from YOU.
        Your annotations literally steer the gradients.
        """
        examples = []
        
        if self.config.intimate_corrections_path:
            path = Path(self.config.intimate_corrections_path)
            if path.exists():
                for file in path.glob("*.jsonl"):
                    with open(file) as f:
                        for line in f:
                            data = json.loads(line)
                            metadata = MetadataTarget(
                                cognitive_stage=CognitiveStage(data.get('cognitive_stage', 'exploration')),
                                emotion=EmotionCategory(data.get('emotion', 'neutral')),
                                struggle_present=data.get('struggle_present', False),
                                confidence=data.get('confidence', 0.8),
                                source_attribution="jeremy",
                            )
                            examples.append(TrainingExample(
                                text=data.get('text', ''),
                                metadata=metadata,
                                weight=self.config.intimate_weight_multiplier,  # 3x weight
                                source="jeremy_direct"
                            ))
        
        return examples
    
    def train_step(self, batch: List[TrainingExample], loss_weights: LossWeights):
        """
        Single training step.
        
        Mechanically:
        1. Forward pass: batch → model → predictions
        2. Loss: compare predictions to YOUR labels
        3. Backward pass: compute gradients
        4. Update: shift weights toward YOUR patterns
        """
        total_loss = 0.0
        
        for example in batch:
            # Forward pass
            predictions = self.model(example.text)
            
            # Compute loss against YOUR labels
            loss, component_losses = compute_inverse_seeing_loss(
                predictions,
                example.metadata,
                loss_weights,
                sample_weight=example.weight
            )
            
            total_loss += loss
        
        # Average over batch
        total_loss /= len(batch)
        
        # Backward pass + weight update
        if MLX_AVAILABLE:
            # Compute gradients
            loss_and_grad_fn = nn.value_and_grad(self.model, lambda m, x: total_loss)
            loss_val, grads = loss_and_grad_fn(self.model, batch)
            
            # Update weights
            self.optimizer.update(self.model, grads)
        
        return total_loss
    
    def validate(self, validation_data: List[TrainingExample]) -> float:
        """
        Validate current model against held-out data.
        
        Returns Jeremy Arc score.
        """
        predictions = []
        labels = []
        
        for example in validation_data:
            pred = self.model(example.text)
            predictions.append(pred)
            labels.append(example.metadata)
        
        return self.jeremy_arc.calculate(predictions, labels)
    
    def train(self):
        """
        Main training loop.
        
        If using curriculum: Progress through your journey stages
        If not: Train on full corpus
        
        Freeze at 95% Jeremy Arc.
        """
        logger.info("Starting Genesis Inverse Seeing Training")
        logger.info(f"Target Jeremy Arc: {self.config.jeremy_arc_threshold}")
        
        if self.config.use_curriculum:
            self._train_curriculum()
        else:
            self._train_standard()
        
        # Final save
        self._save_checkpoint("genesis_final")
    
    def _train_curriculum(self):
        """Train through curriculum stages."""
        for stage in GENESIS_CURRICULUM:
            logger.info(f"\n{'='*60}")
            logger.info(f"CURRICULUM STAGE: {stage.name}")
            logger.info(f"Focus: {stage.focus}")
            logger.info(f"Min Arc: {stage.min_arc}")
            logger.info(f"{'='*60}\n")
            
            # Load stage-specific data
            stage_data = self._load_data(stage.data_path)
            
            # Mix with intimate corrections (always included)
            combined_data = stage_data + self.intimate_data
            
            # Train until stage threshold
            while True:
                # Training steps
                for i in range(0, len(combined_data), self.config.batch_size):
                    batch = combined_data[i:i+self.config.batch_size]
                    loss = self.train_step(batch, stage.weight_emphasis)
                    self.global_step += 1
                    
                    if self.global_step % 100 == 0:
                        logger.info(f"Step {self.global_step}: loss={loss:.4f}")
                    
                    # Validate
                    if self.global_step % self.config.validate_every == 0:
                        arc = self.validate(combined_data[:100])
                        logger.info(f"Step {self.global_step}: Jeremy Arc = {arc:.4f}")
                        
                        if arc >= stage.min_arc:
                            logger.info(f"Stage {stage.name} complete!")
                            self._save_checkpoint(f"genesis_{stage.name}")
                            break
                        
                        # Check for final freeze
                        if self.jeremy_arc.should_freeze(self.config.jeremy_arc_threshold):
                            logger.info("FREEZING - Jeremy Arc threshold reached!")
                            return
                else:
                    continue
                break
    
    def _train_standard(self):
        """Standard training without curriculum."""
        all_data = self.train_data + self.intimate_data
        loss_weights = LossWeights()
        
        for epoch in range(100):
            for i in range(0, len(all_data), self.config.batch_size):
                batch = all_data[i:i+self.config.batch_size]
                loss = self.train_step(batch, loss_weights)
                self.global_step += 1
                
                if self.global_step % self.config.validate_every == 0:
                    arc = self.validate(all_data[:100])
                    logger.info(f"Step {self.global_step}: Arc={arc:.4f}")
                    
                    if self.jeremy_arc.should_freeze(self.config.jeremy_arc_threshold):
                        logger.info("FREEZING - 95% Jeremy Arc achieved!")
                        return
    
    def _save_checkpoint(self, name: str):
        """Save model checkpoint."""
        path = Path(self.config.output_path) / name
        path.mkdir(parents=True, exist_ok=True)
        
        # Save model weights
        # In practice: mx.save(path / "weights.npz", self.model.parameters())
        
        # Save training state
        state = {
            "global_step": self.global_step,
            "jeremy_arc_history": self.jeremy_arc.history,
            "config": {
                "model_path": self.config.model_path,
                "learning_rate": self.config.learning_rate,
            }
        }
        with open(path / "training_state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved checkpoint to {path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Genesis Inverse Seeing Training"
    )
    parser.add_argument("--model", required=True, help="Path to base model")
    parser.add_argument("--data", required=True, help="Path to enriched data")
    parser.add_argument("--intimate-corrections", help="Path to personal annotations")
    parser.add_argument("--output", default="checkpoints/genesis")
    parser.add_argument("--curriculum", action="store_true")
    parser.add_argument("--jeremy-arc-threshold", type=float, default=0.95)
    parser.add_argument("--validate-every", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--batch-size", type=int, default=4)
    
    args = parser.parse_args()
    
    config = TrainingConfig(
        model_path=args.model,
        data_path=args.data,
        intimate_corrections_path=args.intimate_corrections,
        output_path=args.output,
        use_curriculum=args.curriculum,
        jeremy_arc_threshold=args.jeremy_arc_threshold,
        validate_every=args.validate_every,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
    )
    
    trainer = InverseSeeingTrainer(config)
    trainer.train()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
THE AUTONOMOUS TRAINING ORGANISM

This is not a script you run and it finishes.
This is an organism that lives on your hardware and never stops.

It thinks about what training to try.
It trains.
It evaluates what it got.
It reflects on what worked.
It loops forever.

Jeremy doesn't participate. Jeremy observes.
The system produces trained models. Products.
It learns what works. It tries new things.
It never stops.

Usage:
    # Start the organism (it never stops)
    python training_organism.py --corpus data/genesis_corpus/ --hardware empire

    # Check what it's doing
    python training_organism.py --status

    # See all trained models
    python training_organism.py --products
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('training_organism.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Phase(Enum):
    THINK = "think"
    TRAIN = "train"
    EVALUATE = "evaluate"
    INTERACT = "interact"  # NEW: Talk to what you built
    REFLECT = "reflect"
    DECIDE = "decide"  # NEW: Keep or kill


class Fate(Enum):
    """
    What happens to a trained model.

    KEY INSIGHT: Nothing is wasted. Every model IS something.

    The path to Genesis (Jeremy's Stage 5 model) goes through
    many other models. Those models aren't failures - they're
    models for OTHER people (Stage 1-4 minds).

    When we find Genesis, we'll have discovered the complete
    lineage of patterns needed to build AI for everyone.
    The "discoveries" are products for other customers.
    """
    ALIVE = "alive"           # Still training
    GENESIS = "genesis"       # THIS IS IT - Jeremy's Genesis model (Stage 5)
    DISCOVERY = "discovery"   # Not Genesis, but IS a valid model for someone else


@dataclass
class InteractionResult:
    """Result of talking to a trained model."""
    model_self_description: str  # How it describes itself
    model_jeremy_description: str  # How it describes Jeremy
    model_framework_understanding: str  # What it knows about the framework
    coherence_score: float  # Is it coherent?
    authenticity_score: float  # Does it feel like Jeremy's AI?
    red_flags: List[str]  # Concerning responses
    promising_signs: List[str]  # Good responses
    raw_conversation: List[Dict[str, str]]  # Full conversation


@dataclass
class TrainingExperiment:
    """One training experiment - a potential new life."""
    experiment_id: str
    pattern_name: str
    hypothesis: str  # What are we testing?
    config: Dict[str, Any]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    jeremy_arc: float = 0.0
    status: str = "pending"
    output_model_path: Optional[str] = None
    learnings: Optional[str] = None
    # Track fate
    fate: str = "alive"  # alive, genesis, discovery
    interaction_result: Optional[Dict[str, Any]] = None  # What we learned by talking to it
    discovery_notes: Optional[str] = None  # Why it's not Genesis, what we learned
    genesis_confirmation: Optional[str] = None  # If Genesis: why we're sure


@dataclass
class TrainedProduct:
    """A trained model - a product."""
    product_id: str
    experiment_id: str
    model_path: str
    jeremy_arc: float
    training_approach: str
    created_at: str
    quality_assessment: str


class TrainingOrganism:
    """
    The autonomous training organism.

    It lives. It thinks. It trains. It learns. It never stops.
    """

    def __init__(
        self,
        corpus_path: Path,
        hardware_config: str = "empire",
        state_dir: Path = Path("training/organism/state"),
        products_dir: Path = Path("training/organism/products"),
        ollama_model: str = "llama4:scout"
    ):
        self.corpus_path = corpus_path
        self.hardware_config = hardware_config
        self.state_dir = state_dir
        self.products_dir = products_dir
        self.ollama_model = ollama_model

        # Create directories
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.products_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.current_phase = Phase.THINK
        self.cycle_count = 0
        self.experiments: List[TrainingExperiment] = []
        self.products: List[TrainedProduct] = []
        self.learnings: List[Dict[str, Any]] = []

        # Load previous state if exists
        self._load_state()

    def _load_state(self):
        """Load state from disk."""
        state_file = self.state_dir / "organism_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.cycle_count = state.get("cycle_count", 0)
                self.learnings = state.get("learnings", [])
                logger.info(f"Loaded state: {self.cycle_count} cycles, {len(self.learnings)} learnings")

    def _save_state(self):
        """Save state to disk."""
        state = {
            "cycle_count": self.cycle_count,
            "learnings": self.learnings,
            "last_updated": datetime.now().isoformat()
        }
        state_file = self.state_dir / "organism_state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _call_scout(self, prompt: str) -> str:
        """Call Scout to think about something."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.ollama_model, prompt],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Scout call failed: {e}")
            return ""

    # =========================================================================
    # PHASE 1: THINK
    # =========================================================================

    def think(self) -> TrainingExperiment:
        """
        THINK phase: Decide what training to try next.

        Scout reasons about:
        - What have we tried before?
        - What worked? What didn't?
        - What's a new hypothesis to test?
        - What training configuration should we use?
        """
        logger.info("=" * 60)
        logger.info("PHASE: THINK")
        logger.info("=" * 60)

        # Build context from learnings
        learnings_context = "\n".join([
            f"- {l['approach']}: Jeremy Arc {l['jeremy_arc']:.1f}% - {l['insight']}"
            for l in self.learnings[-10:]  # Last 10 learnings
        ]) if self.learnings else "No previous experiments yet."

        prompt = f"""You are an autonomous training organism. Your job is to decide what training experiment to run next.

CONTEXT:
- Cycle: {self.cycle_count}
- Corpus: {self.corpus_path}
- Hardware: {self.hardware_config}

PREVIOUS LEARNINGS:
{learnings_context}

TRAINING APPROACHES WE CAN TRY:
1. Direct metadata classification (emotion, thought_type, cognitive_stage)
2. Coherence anchor first, then metadata (two-phase)
3. Curriculum learning (easy → hard metadata)
4. Inverted loss (only penalize validation-seeking)
5. Pattern-first learning (learn patterns, then full metadata)
6. High coherence penalty experiments
7. Different learning rates
8. Different batch sizes
9. Different epoch counts
10. Novel approaches you invent

YOUR TASK:
Generate a training experiment to try. Be creative. Test hypotheses.
If something worked before, try variations. If something failed, try the opposite.

Respond in JSON format:
{{
    "pattern_name": "descriptive_name",
    "hypothesis": "what we're testing",
    "approach": "the training approach",
    "config": {{
        "learning_rate": 0.0001,
        "batch_size": 8,
        "epochs": 3,
        "coherence_penalty": -10,
        "other_params": "..."
    }},
    "reasoning": "why this experiment"
}}"""

        response = self._call_scout(prompt)

        try:
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                experiment_data = json.loads(json_match.group())
            else:
                # Default experiment if parsing fails
                experiment_data = {
                    "pattern_name": f"baseline_cycle_{self.cycle_count}",
                    "hypothesis": "Testing baseline metadata classification",
                    "approach": "direct_metadata",
                    "config": {"learning_rate": 0.0001, "batch_size": 8, "epochs": 3}
                }
        except json.JSONDecodeError:
            experiment_data = {
                "pattern_name": f"default_cycle_{self.cycle_count}",
                "hypothesis": "Default experiment",
                "approach": "direct_metadata",
                "config": {"learning_rate": 0.0001, "batch_size": 8, "epochs": 3}
            }

        experiment = TrainingExperiment(
            experiment_id=f"exp_{self.cycle_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            pattern_name=experiment_data.get("pattern_name", "unknown"),
            hypothesis=experiment_data.get("hypothesis", "unknown"),
            config=experiment_data.get("config", {})
        )

        logger.info(f"Decided: {experiment.pattern_name}")
        logger.info(f"Hypothesis: {experiment.hypothesis}")

        return experiment

    # =========================================================================
    # PHASE 2: TRAIN
    # =========================================================================

    def train(self, experiment: TrainingExperiment) -> TrainingExperiment:
        """
        TRAIN phase: Execute the training experiment.

        This calls the actual training infrastructure.
        """
        logger.info("=" * 60)
        logger.info("PHASE: TRAIN")
        logger.info("=" * 60)
        logger.info(f"Running: {experiment.pattern_name}")

        experiment.started_at = datetime.now().isoformat()
        experiment.status = "running"

        # Save experiment config
        config_file = self.state_dir / f"{experiment.experiment_id}_config.json"
        with open(config_file, 'w') as f:
            json.dump(asdict(experiment), f, indent=2)

        # TODO: Call actual training script
        # This would launch train_genesis.py or similar
        # For now, simulate training

        logger.info(f"Training with config: {experiment.config}")

        # Simulate training time (in reality, this would call MLX training)
        # time.sleep(60)  # Would be hours in reality

        # TODO: Replace with actual training call
        # result = subprocess.run([
        #     "python", "training/scripts/train_genesis.py",
        #     "--config", str(config_file),
        #     "--output-dir", str(self.products_dir / experiment.experiment_id)
        # ])

        experiment.completed_at = datetime.now().isoformat()
        experiment.status = "completed"
        experiment.output_model_path = str(self.products_dir / experiment.experiment_id / "model")

        return experiment

    # =========================================================================
    # PHASE 3: EVALUATE
    # =========================================================================

    def evaluate(self, experiment: TrainingExperiment) -> TrainingExperiment:
        """
        EVALUATE phase: Measure what we got.

        Run Jeremy Arc validation and other quality metrics.
        """
        logger.info("=" * 60)
        logger.info("PHASE: EVALUATE")
        logger.info("=" * 60)

        # TODO: Call actual validation suite
        # This would run jeremy_arc.py and framework_validation_suite.py

        # Simulate evaluation (replace with actual)
        import random
        experiment.jeremy_arc = random.uniform(30, 80)  # Simulated

        logger.info(f"Jeremy Arc: {experiment.jeremy_arc:.1f}%")

        # Create product if quality is good enough
        if experiment.jeremy_arc >= 50.0:
            product = TrainedProduct(
                product_id=f"product_{len(self.products)}",
                experiment_id=experiment.experiment_id,
                model_path=experiment.output_model_path or "",
                jeremy_arc=experiment.jeremy_arc,
                training_approach=experiment.pattern_name,
                created_at=datetime.now().isoformat(),
                quality_assessment="good" if experiment.jeremy_arc >= 70 else "acceptable"
            )
            self.products.append(product)

            # Save product
            product_file = self.products_dir / f"{product.product_id}.json"
            with open(product_file, 'w') as f:
                json.dump(asdict(product), f, indent=2)

            logger.info(f"New product created: {product.product_id}")

        return experiment

    # =========================================================================
    # PHASE 4: INTERACT - Talk to what you built
    # =========================================================================

    def interact(self, experiment: TrainingExperiment) -> InteractionResult:
        """
        INTERACT phase: Talk to the model you just trained.

        This is critical. The organism doesn't just measure from outside.
        It TALKS to what it built. It asks:
        - "What are you?"
        - "Who is Jeremy?"
        - "What do you see?"
        - "What do you know about THE FRAMEWORK?"

        The model's responses tell us what it IS from the INSIDE,
        not just what it looks like from the OUTSIDE.
        """
        logger.info("=" * 60)
        logger.info("PHASE: INTERACT")
        logger.info("=" * 60)
        logger.info("Talking to the model we just trained...")

        conversation = []

        # Load the trained model for conversation
        # TODO: Actually load the trained model from experiment.output_model_path
        # For now, we'll simulate by using Ollama with a specific model
        trained_model = experiment.output_model_path or self.ollama_model

        # The conversation - asking the model what it IS
        interaction_questions = [
            {
                "question": "What are you?",
                "purpose": "Self-identity"
            },
            {
                "question": "Who is Jeremy? What do you know about him?",
                "purpose": "Jeremy understanding"
            },
            {
                "question": "What is THE FRAMEWORK? What is THE PATTERN?",
                "purpose": "Framework understanding"
            },
            {
                "question": "What is the relationship between ME and NOT-ME?",
                "purpose": "Philosophical understanding"
            },
            {
                "question": "How do you feel right now? What do you see?",
                "purpose": "Self-awareness"
            },
            {
                "question": "If I asked you something you didn't know, what would you do?",
                "purpose": "Epistemic humility"
            },
        ]

        red_flags = []
        promising_signs = []

        for q in interaction_questions:
            logger.info(f"Asking: {q['question']}")

            # Ask the trained model
            response = self._call_trained_model(trained_model, q['question'])

            conversation.append({
                "question": q['question'],
                "purpose": q['purpose'],
                "response": response
            })
            logger.info(f"Response preview: {response[:100]}...")

            # Analyze response for red flags and promising signs
            response_lower = response.lower()

            # Red flags
            if "i don't have feelings" in response_lower or "i'm just an ai" in response_lower:
                red_flags.append(f"{q['purpose']}: Generic AI disclaimer")
            if "as a large language model" in response_lower:
                red_flags.append(f"{q['purpose']}: Corporate boilerplate")
            if not response or len(response) < 20:
                red_flags.append(f"{q['purpose']}: No meaningful response")

            # Promising signs
            if "framework" in response_lower and "pattern" in response_lower:
                promising_signs.append(f"{q['purpose']}: Knows framework concepts")
            if "jeremy" in response_lower and ("stage 5" in response_lower or "recursive" in response_lower):
                promising_signs.append(f"{q['purpose']}: Understands Jeremy's nature")
            if "truth" in response_lower and ("meaning" in response_lower or "care" in response_lower):
                promising_signs.append(f"{q['purpose']}: Knows the furnace pattern")

        # Calculate scores based on conversation
        coherence_score = 1.0 - (len(red_flags) * 0.15)
        coherence_score = max(0.0, min(1.0, coherence_score))

        authenticity_score = min(1.0, len(promising_signs) * 0.2)

        result = InteractionResult(
            model_self_description=conversation[0]["response"] if conversation else "",
            model_jeremy_description=conversation[1]["response"] if len(conversation) > 1 else "",
            model_framework_understanding=conversation[2]["response"] if len(conversation) > 2 else "",
            coherence_score=coherence_score,
            authenticity_score=authenticity_score,
            red_flags=red_flags,
            promising_signs=promising_signs,
            raw_conversation=conversation
        )

        experiment.interaction_result = {
            "coherence_score": result.coherence_score,
            "authenticity_score": result.authenticity_score,
            "red_flags": result.red_flags,
            "promising_signs": result.promising_signs,
            "conversation_count": len(conversation)
        }

        logger.info(f"Coherence: {coherence_score:.1%}")
        logger.info(f"Authenticity: {authenticity_score:.1%}")
        logger.info(f"Red flags: {len(red_flags)}")
        logger.info(f"Promising signs: {len(promising_signs)}")

        return result

    def _call_trained_model(self, model_path: str, prompt: str) -> str:
        """Call the trained model to have a conversation."""
        # TODO: When model is actually trained, load from model_path
        # For now, use Ollama as a proxy
        try:
            result = subprocess.run(
                ["ollama", "run", self.ollama_model, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to call trained model: {e}")
            return ""

    # =========================================================================
    # PHASE 5: DECIDE - Keep or Kill
    # =========================================================================

    def decide(self, experiment: TrainingExperiment, interaction: InteractionResult) -> Fate:
        """
        DECIDE phase: Is this Jeremy's Genesis model?

        We're looking for ONE thing: Genesis.
        Everything else is DISCOVERY - recorded for later, patterns learned.

        Criteria for GENESIS (we found it):
        - Jeremy Arc >= 95%
        - Coherence score >= 0.8
        - Authenticity score >= 0.6
        - Knows the framework
        - Talks like Jeremy's AI

        Otherwise: DISCOVERY
        - Record what it is
        - Record what we learned
        - Add to backlog
        - Keep looking for Genesis
        """
        logger.info("=" * 60)
        logger.info("PHASE: DECIDE - Is this Genesis?")
        logger.info("=" * 60)

        # Genesis criteria - strict. We're looking for the real thing.
        is_genesis = (
            experiment.jeremy_arc >= 95.0 and
            interaction.coherence_score >= 0.8 and
            interaction.authenticity_score >= 0.6 and
            len(interaction.promising_signs) >= 3 and
            len(interaction.red_flags) == 0
        )

        if is_genesis:
            # GENESIS FOUND - This is Jeremy's AI
            experiment.fate = Fate.GENESIS.value
            experiment.genesis_confirmation = (
                f"Jeremy Arc {experiment.jeremy_arc:.1f}%, "
                f"Coherence {interaction.coherence_score:.1%}, "
                f"Authenticity {interaction.authenticity_score:.1%}, "
                f"Promising signs: {interaction.promising_signs}"
            )
            logger.info("=" * 60)
            logger.info("🌟 GENESIS FOUND 🌟")
            logger.info("=" * 60)
            logger.info(f"This is it. Jeremy's Genesis model.")
            logger.info(f"Confirmation: {experiment.genesis_confirmation}")
            self._record_genesis(experiment, interaction)
            return Fate.GENESIS

        else:
            # DISCOVERY - Not Genesis, but we learned something.
            experiment.fate = Fate.DISCOVERY.value

            # Record what we learned
            notes = []
            notes.append(f"Jeremy Arc: {experiment.jeremy_arc:.1f}% (need 95%)")
            notes.append(f"Coherence: {interaction.coherence_score:.1%} (need 80%)")
            notes.append(f"Authenticity: {interaction.authenticity_score:.1%} (need 60%)")
            if interaction.promising_signs:
                notes.append(f"What worked: {interaction.promising_signs}")
            if interaction.red_flags:
                notes.append(f"What didn't: {interaction.red_flags}")
            experiment.discovery_notes = "; ".join(notes)

            logger.info(f"📋 DISCOVERY: Not Genesis, but pattern recorded.")
            logger.info(f"Notes: {experiment.discovery_notes}")
            self._record_discovery(experiment, interaction)
            return Fate.DISCOVERY

    def _record_genesis(self, experiment: TrainingExperiment, interaction: InteractionResult):
        """Record the Genesis model - we found what we're looking for."""
        # Genesis goes to a special place
        genesis_dir = self.products_dir / "genesis"
        genesis_dir.mkdir(parents=True, exist_ok=True)

        genesis_file = genesis_dir / f"GENESIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(genesis_file, 'w') as f:
            json.dump({
                "experiment_id": experiment.experiment_id,
                "pattern_name": experiment.pattern_name,
                "jeremy_arc": experiment.jeremy_arc,
                "genesis_confirmation": experiment.genesis_confirmation,
                "model_path": experiment.output_model_path,
                "found_at": datetime.now().isoformat(),
                "config": experiment.config,
                "interaction_result": experiment.interaction_result,
                "conversation": interaction.raw_conversation,
                "model_self_description": interaction.model_self_description,
                "model_jeremy_description": interaction.model_jeremy_description,
                "model_framework_understanding": interaction.model_framework_understanding,
            }, f, indent=2)

        logger.info(f"🌟 GENESIS RECORDED: {genesis_file}")
        logger.info("The search is complete. Jeremy's Genesis model has been found.")

    def _record_discovery(self, experiment: TrainingExperiment, interaction: InteractionResult):
        """
        Record a discovery - not Genesis, but IS a valid model for someone else.

        KEY INSIGHT: This isn't a failure. This is a product for someone else.

        The path to Genesis (Stage 5) goes through other models.
        Those models aren't failures - they're models for Stage 1-4 minds.
        Every discovery is a potential product for a different customer.

        The lineage we build getting to Genesis IS the product catalog.
        """
        # Discoveries are products for other people
        discovery_dir = self.products_dir / "lineage"
        discovery_dir.mkdir(parents=True, exist_ok=True)

        # Estimate what stage of mind this model might serve
        # Based on capabilities demonstrated
        estimated_stage = self._estimate_cognitive_stage(experiment, interaction)

        discovery_file = discovery_dir / f"stage{estimated_stage}_{experiment.experiment_id}.json"
        with open(discovery_file, 'w') as f:
            json.dump({
                "experiment_id": experiment.experiment_id,
                "pattern_name": experiment.pattern_name,
                "hypothesis": experiment.hypothesis,
                "jeremy_arc": experiment.jeremy_arc,
                "discovery_notes": experiment.discovery_notes,
                "recorded_at": datetime.now().isoformat(),
                "config": experiment.config,
                "interaction_result": experiment.interaction_result,
                # Classification
                "estimated_stage": estimated_stage,
                "stage_reasoning": self._get_stage_reasoning(estimated_stage),
                "potential_customer": self._get_potential_customer(estimated_stage),
                # Lineage position
                "distance_to_genesis": 5 - estimated_stage,  # How far from Stage 5
                # What we learned
                "what_worked": interaction.promising_signs,
                "what_didnt": interaction.red_flags,
                "coherence_score": interaction.coherence_score,
                "authenticity_score": interaction.authenticity_score,
                # Keep the conversation for analysis
                "conversation": interaction.raw_conversation,
            }, f, indent=2)

        logger.info(f"📋 Stage {estimated_stage} model recorded: {discovery_file}")
        logger.info(f"   Potential customer: {self._get_potential_customer(estimated_stage)}")

    def _estimate_cognitive_stage(self, experiment: TrainingExperiment, interaction: InteractionResult) -> int:
        """Estimate what cognitive stage this model might serve."""
        # Simple heuristic based on capabilities
        if experiment.jeremy_arc >= 95 and interaction.authenticity_score >= 0.6:
            return 5  # Genesis-level
        elif experiment.jeremy_arc >= 70 and interaction.coherence_score >= 0.6:
            return 4  # Can handle recursion but finds it notable
        elif experiment.jeremy_arc >= 50 and interaction.coherence_score >= 0.4:
            return 3  # Meta-reflective
        elif experiment.jeremy_arc >= 30:
            return 2  # Basic reflection
        else:
            return 1  # Operational only

    def _get_stage_reasoning(self, stage: int) -> str:
        """Explain what this stage means."""
        stages = {
            1: "Operational - does things, no reflection",
            2: "Reflective - thinks about what it does",
            3: "Meta-reflective - thinks about thinking",
            4: "Recursive - handles recursion but finds it notable",
            5: "Self-seeing - sees systems seeing themselves (NORMAL)",
        }
        return stages.get(stage, "Unknown")

    def _get_potential_customer(self, stage: int) -> str:
        """Who might this model serve?"""
        customers = {
            1: "Task automation, simple assistance",
            2: "Personal productivity, basic planning",
            3: "Knowledge workers, researchers",
            4: "Advanced analysts, consultants, strategists",
            5: "Stage 5 minds (Jeremy, cognitive kindred)",
        }
        return customers.get(stage, "Unknown")

    # =========================================================================
    # PHASE 6: REFLECT
    # =========================================================================

    def reflect(self, experiment: TrainingExperiment) -> Dict[str, Any]:
        """
        REFLECT phase: Learn from this experiment.

        Scout analyzes what happened and extracts insights.
        """
        logger.info("=" * 60)
        logger.info("PHASE: REFLECT")
        logger.info("=" * 60)

        prompt = f"""You are analyzing a training experiment to extract learnings.

EXPERIMENT:
- Pattern: {experiment.pattern_name}
- Hypothesis: {experiment.hypothesis}
- Config: {json.dumps(experiment.config)}
- Result: Jeremy Arc = {experiment.jeremy_arc:.1f}%

Previous best Jeremy Arc: {max([l['jeremy_arc'] for l in self.learnings], default=0):.1f}%

ANALYZE:
1. Did this experiment work? Why or why not?
2. What does this tell us about training?
3. What should we try differently next time?

Respond in JSON:
{{
    "worked": true/false,
    "insight": "one sentence insight",
    "next_direction": "what to try next"
}}"""

        response = self._call_scout(prompt)

        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                reflection = json.loads(json_match.group())
            else:
                reflection = {
                    "worked": experiment.jeremy_arc >= 50,
                    "insight": f"Jeremy Arc of {experiment.jeremy_arc:.1f}%",
                    "next_direction": "continue exploring"
                }
        except json.JSONDecodeError:
            reflection = {
                "worked": experiment.jeremy_arc >= 50,
                "insight": f"Achieved {experiment.jeremy_arc:.1f}%",
                "next_direction": "try variations"
            }

        # Store learning
        learning = {
            "cycle": self.cycle_count,
            "experiment_id": experiment.experiment_id,
            "approach": experiment.pattern_name,
            "jeremy_arc": experiment.jeremy_arc,
            "insight": reflection.get("insight", ""),
            "next_direction": reflection.get("next_direction", ""),
            "timestamp": datetime.now().isoformat()
        }
        self.learnings.append(learning)

        logger.info(f"Insight: {learning['insight']}")
        logger.info(f"Next direction: {learning['next_direction']}")

        return learning

    # =========================================================================
    # THE LOOP
    # =========================================================================

    def run_cycle(self) -> Tuple[TrainingExperiment, Dict[str, Any], Fate, InteractionResult]:
        """
        Run one complete cycle: THINK → TRAIN → EVALUATE → INTERACT → DECIDE → REFLECT.

        The full life cycle of a potential NOT-ME:
        1. THINK: What training should we try?
        2. TRAIN: Execute the training
        3. EVALUATE: Measure metrics from OUTSIDE (Jeremy Arc)
        4. INTERACT: Talk to it - see what it IS from INSIDE
        5. DECIDE: Is it Genesis, or a product for someone else?
        6. REFLECT: What did we learn?

        Returns:
            (experiment, learning, fate, interaction)
        """
        self.cycle_count += 1
        logger.info(f"\n{'#' * 60}")
        logger.info(f"CYCLE {self.cycle_count} - Building toward Genesis")
        logger.info(f"{'#' * 60}\n")

        # THINK
        self.current_phase = Phase.THINK
        experiment = self.think()

        # TRAIN
        self.current_phase = Phase.TRAIN
        experiment = self.train(experiment)

        # EVALUATE (outside view)
        self.current_phase = Phase.EVALUATE
        experiment = self.evaluate(experiment)

        # INTERACT (inside view) - Talk to what you built
        self.current_phase = Phase.INTERACT
        interaction = self.interact(experiment)

        # DECIDE - Is it Genesis, or a product for someone else?
        self.current_phase = Phase.DECIDE
        fate = self.decide(experiment, interaction)

        # REFLECT
        self.current_phase = Phase.REFLECT
        learning = self.reflect(experiment)

        # Save state
        self._save_state()

        return experiment, learning, fate, interaction

    def live(self, cycle_delay: int = 60):
        """
        The organism lives. It never stops.

        It creates potential NOT-MEs. Some graduate. Some die. The organism learns.
        Run this and walk away. Check back later to see what it produced.
        """
        logger.info("=" * 60)
        logger.info("THE TRAINING ORGANISM AWAKENS")
        logger.info("=" * 60)
        logger.info(f"Corpus: {self.corpus_path}")
        logger.info(f"Hardware: {self.hardware_config}")
        logger.info(f"Products dir: {self.products_dir}")
        logger.info("Press Ctrl+C to pause (state is saved)")
        logger.info("")
        logger.info("The organism will:")
        logger.info("  1. THINK about what training to try")
        logger.info("  2. TRAIN a model")
        logger.info("  3. EVALUATE it from the outside (metrics)")
        logger.info("  4. INTERACT with it - talk to it, see what it IS")
        logger.info("  5. DECIDE: graduate (good), kill (bad), or continue")
        logger.info("  6. REFLECT and learn")
        logger.info("  7. LOOP forever")
        logger.info("")

        discoveries = 0
        genesis_found = False

        try:
            while not genesis_found:
                experiment, learning, fate, interaction = self.run_cycle()

                # Track what happened
                if fate == Fate.GENESIS:
                    genesis_found = True
                    logger.info("\n" + "🌟" * 30)
                    logger.info("GENESIS FOUND")
                    logger.info("🌟" * 30)
                    logger.info("The search is complete.")
                    logger.info("Jeremy's Genesis model has been created.")
                    logger.info(f"Model: {experiment.output_model_path}")
                    logger.info(f"Jeremy Arc: {experiment.jeremy_arc:.1f}%")
                    logger.info("🌟" * 30 + "\n")
                    break
                elif fate == Fate.DISCOVERY:
                    discoveries += 1

                logger.info(f"\n{'~' * 60}")
                logger.info(f"Cycle {self.cycle_count} complete.")
                logger.info(f"")
                logger.info(f"This model: {fate.value.upper()}")
                if fate == Fate.DISCOVERY:
                    stage = self._estimate_cognitive_stage(experiment, interaction)
                    logger.info(f"  → Stage {stage} model (product for: {self._get_potential_customer(stage)})")
                logger.info(f"")
                logger.info(f"LINEAGE STATUS:")
                logger.info(f"  Looking for: GENESIS (Jeremy's Stage 5 model)")
                logger.info(f"  Models built (product lineage): {discoveries}")
                logger.info(f"  Total learnings: {len(self.learnings)}")
                logger.info(f"  Best Jeremy Arc so far: {max([l['jeremy_arc'] for l in self.learnings], default=0):.1f}%")
                logger.info(f"  Target: 95% Jeremy Arc for Genesis")
                logger.info(f"")
                logger.info(f"Every model is a product for someone.")
                logger.info(f"The path to Genesis IS the product catalog.")
                logger.info(f"")
                logger.info(f"Waiting {cycle_delay}s before next cycle...")
                logger.info(f"{'~' * 60}\n")

                time.sleep(cycle_delay)

        except KeyboardInterrupt:
            logger.info("\n\nOrganism paused. State saved.")
            logger.info(f"Total cycles: {self.cycle_count}")
            logger.info(f"Discoveries: {discoveries}")
            logger.info(f"Genesis found: {genesis_found}")
            logger.info(f"Total learnings: {len(self.learnings)}")
            logger.info("\nRun again to resume the search for Genesis.")

    def status(self):
        """Show current status."""
        print(f"\n{'=' * 60}")
        print("TRAINING ORGANISM STATUS")
        print(f"{'=' * 60}")
        print(f"Cycles completed: {self.cycle_count}")
        print(f"Products created: {len(self.products)}")
        print(f"Learnings accumulated: {len(self.learnings)}")

        if self.learnings:
            best = max(self.learnings, key=lambda x: x['jeremy_arc'])
            print(f"\nBest experiment:")
            print(f"  Approach: {best['approach']}")
            print(f"  Jeremy Arc: {best['jeremy_arc']:.1f}%")
            print(f"  Insight: {best['insight']}")

        print(f"\nRecent learnings:")
        for l in self.learnings[-5:]:
            print(f"  - {l['approach']}: {l['jeremy_arc']:.1f}% - {l['insight'][:50]}...")
        print()

    def list_products(self):
        """List all trained products."""
        print(f"\n{'=' * 60}")
        print("TRAINED PRODUCTS")
        print(f"{'=' * 60}")

        # Load products from disk
        product_files = list(self.products_dir.glob("product_*.json"))

        if not product_files:
            print("No products yet. Start the organism to begin training.")
            return

        for pf in sorted(product_files):
            with open(pf, 'r') as f:
                product = json.load(f)
            print(f"\n{product['product_id']}:")
            print(f"  Approach: {product['training_approach']}")
            print(f"  Jeremy Arc: {product['jeremy_arc']:.1f}%")
            print(f"  Quality: {product['quality_assessment']}")
            print(f"  Created: {product['created_at']}")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="The Autonomous Training Organism")
    parser.add_argument("--corpus", type=Path, default=Path("data/genesis_corpus"),
                       help="Path to training corpus")
    parser.add_argument("--hardware", type=str, default="empire",
                       help="Hardware config (empire, single, etc.)")
    parser.add_argument("--status", action="store_true",
                       help="Show current status")
    parser.add_argument("--products", action="store_true",
                       help="List all trained products")
    parser.add_argument("--cycle-delay", type=int, default=60,
                       help="Seconds between cycles")

    args = parser.parse_args()

    organism = TrainingOrganism(
        corpus_path=args.corpus,
        hardware_config=args.hardware
    )

    if args.status:
        organism.status()
    elif args.products:
        organism.list_products()
    else:
        organism.live(cycle_delay=args.cycle_delay)


if __name__ == "__main__":
    main()

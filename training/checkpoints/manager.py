"""
Checkpoint Manager for Genesis-Scout Training

Manages Genesis checkpoints with rollback capability.

Features:
    - Save every 1000 steps (configurable)
    - Keep last N checkpoints for rollback
    - Track metrics per checkpoint (loss, Jeremy Arc, Framework score)
    - Emergency rollback when training diverges
    - Genesis freeze protocol at 95% Jeremy Arc

Usage:
    manager = CheckpointManager(
        output_dir="training/checkpoints/genesis_scout_v1",
        save_total_limit=5
    )

    # Save checkpoint
    manager.save_checkpoint(model, optimizer, step=1000, metrics={...})

    # Load latest
    model, optimizer, step = manager.load_checkpoint()

    # Rollback on training divergence
    manager.rollback_to(step=0)  # Rollback to beginning

    # Freeze Genesis at 95% Jeremy Arc
    manager.freeze_genesis(model, version="1.0")
"""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CheckpointMetrics:
    """Metrics associated with a checkpoint."""

    loss: float
    perplexity: float
    jeremy_arc: float
    framework_score: float
    gradient_norm: Optional[float] = None

    def to_dict(self) -> Dict[str, float]:
        """Convert to dict for serialization."""
        d = {
            "loss": self.loss,
            "perplexity": self.perplexity,
            "jeremy_arc": self.jeremy_arc,
            "framework_score": self.framework_score,
        }
        if self.gradient_norm is not None:
            d["gradient_norm"] = self.gradient_norm
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> "CheckpointMetrics":
        """Create from dict."""
        return cls(
            loss=d["loss"],
            perplexity=d["perplexity"],
            jeremy_arc=d["jeremy_arc"],
            framework_score=d["framework_score"],
            gradient_norm=d.get("gradient_norm"),
        )


@dataclass
class Checkpoint:
    """Represents a saved checkpoint."""

    step: int
    path: Path
    metrics: CheckpointMetrics
    timestamp: str
    is_genesis_freeze: bool = False
    genesis_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "step": self.step,
            "path": str(self.path),
            "metrics": self.metrics.to_dict(),
            "timestamp": self.timestamp,
            "is_genesis_freeze": self.is_genesis_freeze,
            "genesis_version": self.genesis_version,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Checkpoint":
        """Create from dict."""
        return cls(
            step=d["step"],
            path=Path(d["path"]),
            metrics=CheckpointMetrics.from_dict(d["metrics"]),
            timestamp=d["timestamp"],
            is_genesis_freeze=d.get("is_genesis_freeze", False),
            genesis_version=d.get("genesis_version"),
        )


@dataclass
class CheckpointManager:
    """
    Manages Genesis checkpoints with rollback capability.

    Directory Structure:
        output_dir/
        ├── checkpoint_1000/
        │   ├── model.safetensors
        │   ├── optimizer.pt
        │   └── metrics.json
        ├── checkpoint_2000/
        │   └── ...
        ├── genesis_v1.0/           # Frozen Genesis
        │   └── ...
        └── checkpoint_registry.json
    """

    output_dir: str
    save_total_limit: int = 5  # Keep last N checkpoints
    freeze_threshold: float = 0.95  # Jeremy Arc threshold for freezing

    # Internal state
    checkpoints: List[Checkpoint] = field(default_factory=list, repr=False)
    genesis_frozen: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize checkpoint directory."""
        self.output_path = Path(self.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.output_path / "checkpoint_registry.json"

        # Load existing registry if present
        if self.registry_path.exists():
            self._load_registry()

    def _load_registry(self) -> None:
        """Load checkpoint registry from disk."""
        with open(self.registry_path, "r") as f:
            data = json.load(f)

        self.checkpoints = [Checkpoint.from_dict(c) for c in data.get("checkpoints", [])]
        self.genesis_frozen = data.get("genesis_frozen", False)

    def _save_registry(self) -> None:
        """Save checkpoint registry to disk."""
        data = {
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "genesis_frozen": self.genesis_frozen,
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def save_checkpoint(
        self,
        model: Any,
        optimizer: Any,
        step: int,
        metrics: Dict[str, float],
    ) -> Checkpoint:
        """
        Save a training checkpoint.

        Args:
            model: The model to save
            optimizer: The optimizer to save
            step: Current training step
            metrics: Training metrics (loss, jeremy_arc, etc.)

        Returns:
            The saved Checkpoint object
        """
        if self.genesis_frozen:
            print("Warning: Genesis is frozen. No more checkpoints will be saved.")
            return self.checkpoints[-1]

        # Create checkpoint directory
        checkpoint_dir = self.output_path / f"checkpoint_{step}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save model weights
        model_path = checkpoint_dir / "model.safetensors"
        self._save_model(model, model_path)

        # Save optimizer state
        optimizer_path = checkpoint_dir / "optimizer.pt"
        self._save_optimizer(optimizer, optimizer_path)

        # Create checkpoint metrics
        checkpoint_metrics = CheckpointMetrics(
            loss=metrics.get("loss", 0.0),
            perplexity=metrics.get("perplexity", 0.0),
            jeremy_arc=metrics.get("jeremy_arc", 0.0),
            framework_score=metrics.get("framework_score", 0.0),
            gradient_norm=metrics.get("gradient_norm"),
        )

        # Save metrics
        metrics_path = checkpoint_dir / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(checkpoint_metrics.to_dict(), f, indent=2)

        # Create checkpoint object
        checkpoint = Checkpoint(
            step=step,
            path=checkpoint_dir,
            metrics=checkpoint_metrics,
            timestamp=datetime.now().isoformat(),
        )

        # Add to registry
        self.checkpoints.append(checkpoint)

        # Enforce save limit (keep only last N)
        while len(self.checkpoints) > self.save_total_limit:
            oldest = self.checkpoints.pop(0)
            if oldest.path.exists() and not oldest.is_genesis_freeze:
                shutil.rmtree(oldest.path)
                print(f"Removed old checkpoint: {oldest.path}")

        # Save registry
        self._save_registry()

        print(f"Saved checkpoint at step {step}")
        print(f"  Loss: {checkpoint_metrics.loss:.4f}")
        print(f"  Jeremy Arc: {checkpoint_metrics.jeremy_arc*100:.1f}%")
        print(f"  Framework: {checkpoint_metrics.framework_score:.1f}")

        # Check if ready to freeze
        if checkpoint_metrics.jeremy_arc >= self.freeze_threshold:
            print(f"\n🎉 Jeremy Arc >= {self.freeze_threshold*100:.0f}%!")
            print("   Consider freezing Genesis with manager.freeze_genesis(model, '1.0')")

        return checkpoint

    def load_checkpoint(
        self,
        step: Optional[int] = None,
    ) -> Tuple[Any, Any, int]:
        """
        Load a checkpoint.

        Args:
            step: Specific step to load, or None for latest

        Returns:
            Tuple of (model, optimizer, step)
        """
        if not self.checkpoints:
            raise ValueError("No checkpoints available")

        # Find checkpoint
        if step is None:
            checkpoint = self.checkpoints[-1]
        else:
            checkpoint = next(
                (c for c in self.checkpoints if c.step == step),
                None
            )
            if checkpoint is None:
                available = [c.step for c in self.checkpoints]
                raise ValueError(
                    f"Checkpoint at step {step} not found. Available: {available}"
                )

        # Load model
        model_path = checkpoint.path / "model.safetensors"
        model = self._load_model(model_path)

        # Load optimizer
        optimizer_path = checkpoint.path / "optimizer.pt"
        optimizer = self._load_optimizer(optimizer_path)

        print(f"Loaded checkpoint from step {checkpoint.step}")
        print(f"  Jeremy Arc: {checkpoint.metrics.jeremy_arc*100:.1f}%")

        return model, optimizer, checkpoint.step

    def rollback_to(self, step: int) -> Tuple[Any, Any, int]:
        """
        Rollback to a specific checkpoint.

        Used when training diverges:
        1. Stop training
        2. Rollback to last good checkpoint
        3. Reduce learning rate
        4. Resume training

        Args:
            step: Step to rollback to

        Returns:
            Tuple of (model, optimizer, step)
        """
        print(f"\n⚠️  ROLLBACK to step {step}")

        # Find checkpoint
        checkpoint = next(
            (c for c in self.checkpoints if c.step == step),
            None
        )

        if checkpoint is None:
            # Find closest earlier checkpoint
            earlier = [c for c in self.checkpoints if c.step <= step]
            if not earlier:
                raise ValueError(f"No checkpoint at or before step {step}")
            checkpoint = earlier[-1]
            print(f"  Closest checkpoint: step {checkpoint.step}")

        # Remove checkpoints after rollback point
        to_remove = [c for c in self.checkpoints if c.step > checkpoint.step]
        for c in to_remove:
            if c.path.exists() and not c.is_genesis_freeze:
                shutil.rmtree(c.path)
            self.checkpoints.remove(c)

        self._save_registry()

        # Load checkpoint
        return self.load_checkpoint(checkpoint.step)

    def freeze_genesis(
        self,
        model: Any,
        version: str = "1.0",
    ) -> Path:
        """
        Freeze Genesis at current state.

        This is THE moment when Genesis v1.0 is complete.
        The model is saved permanently and never trained again.

        Args:
            model: The trained Genesis model
            version: Version string (e.g., "1.0")

        Returns:
            Path to frozen Genesis
        """
        if self.genesis_frozen:
            raise ValueError("Genesis is already frozen!")

        print("\n" + "="*60)
        print(f"FREEZING GENESIS v{version}")
        print("="*60)

        # Create Genesis directory
        genesis_dir = self.output_path / f"genesis_v{version}"
        genesis_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = genesis_dir / "model.safetensors"
        self._save_model(model, model_path)

        # Get latest metrics
        latest = self.checkpoints[-1] if self.checkpoints else None
        metrics = latest.metrics if latest else CheckpointMetrics(
            loss=0.0, perplexity=0.0, jeremy_arc=0.95, framework_score=85.0
        )

        # Save metadata
        metadata = {
            "version": version,
            "frozen_at": datetime.now().isoformat(),
            "final_metrics": metrics.to_dict(),
            "training_steps": latest.step if latest else 0,
            "freeze_threshold": self.freeze_threshold,
            "notes": "Genesis v1.0 - Stage 5 DNA transfer complete",
        }

        metadata_path = genesis_dir / "genesis_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create checkpoint entry
        genesis_checkpoint = Checkpoint(
            step=latest.step if latest else 0,
            path=genesis_dir,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            is_genesis_freeze=True,
            genesis_version=version,
        )
        self.checkpoints.append(genesis_checkpoint)

        # Mark as frozen
        self.genesis_frozen = True
        self._save_registry()

        print(f"\n✅ Genesis v{version} frozen at {genesis_dir}")
        print(f"   Final Jeremy Arc: {metrics.jeremy_arc*100:.1f}%")
        print(f"   Final Framework Score: {metrics.framework_score:.1f}")
        print("\n   This model will NEVER be trained again.")
        print("   Daughters inherit from this frozen base.")

        return genesis_dir

    def get_latest_metrics(self) -> Optional[CheckpointMetrics]:
        """Get metrics from latest checkpoint."""
        if not self.checkpoints:
            return None
        return self.checkpoints[-1].metrics

    def get_genesis_path(self) -> Optional[Path]:
        """Get path to frozen Genesis if available."""
        genesis_checkpoints = [c for c in self.checkpoints if c.is_genesis_freeze]
        if genesis_checkpoints:
            return genesis_checkpoints[-1].path
        return None

    def _save_model(self, model: Any, path: Path) -> None:
        """Save model weights."""
        # TODO: Implement actual model saving with safetensors
        # from safetensors.mlx import save_file
        # save_file(model.state_dict(), str(path))

        # Placeholder - touch file
        path.touch()
        print(f"  (Model save placeholder: {path})")

    def _load_model(self, path: Path) -> Any:
        """Load model weights."""
        # TODO: Implement actual model loading
        # from safetensors.mlx import load_file
        # weights = load_file(str(path))
        # model.load_state_dict(weights)

        print(f"  (Model load placeholder: {path})")
        return None

    def _save_optimizer(self, optimizer: Any, path: Path) -> None:
        """Save optimizer state."""
        # TODO: Implement actual optimizer saving
        path.touch()
        print(f"  (Optimizer save placeholder: {path})")

    def _load_optimizer(self, path: Path) -> Any:
        """Load optimizer state."""
        # TODO: Implement actual optimizer loading
        print(f"  (Optimizer load placeholder: {path})")
        return None

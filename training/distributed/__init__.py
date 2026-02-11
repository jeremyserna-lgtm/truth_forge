"""
Distributed Training Infrastructure for Genesis-Scout

THE EMPIRE: 4 Mac Studios with 1.28TB unified memory
MLX + MPI for distributed training across nodes
"""

from training.distributed.mlx_trainer import (
    MLXDistributedTrainer,
    EmpireConfig,
    TrainingState,
)

__all__ = [
    "MLXDistributedTrainer",
    "EmpireConfig",
    "TrainingState",
]

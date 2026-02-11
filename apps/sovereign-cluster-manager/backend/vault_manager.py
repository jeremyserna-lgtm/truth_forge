"""Manages the model vault (8TB external drive)."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a model in the vault."""

    name: str
    path: Path
    relative_path: str
    size_gb: float
    format: str
    quantization: str | None
    is_base: bool
    is_checkpoint: bool
    is_lora: bool
    metadata: dict


class VaultManager:
    """Manages the model vault filesystem."""

    # Known model file extensions
    MODEL_EXTENSIONS = {".gguf", ".safetensors", ".bin", ".pt", ".pth"}

    # Directory structure
    STRUCTURE = {
        "base": "base/",
        "fine_tuned": "fine-tuned/",
        "checkpoints": "checkpoints/",
        "lora": "lora/",
        "archive": "archive/",
    }

    def __init__(self, vault_path: Path = settings.vault_path) -> None:
        self.vault_path = vault_path
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Ensure vault directory structure exists."""
        if not self.vault_path.exists():
            logger.warning(
                "Vault path does not exist",
                extra={"path": str(self.vault_path)},
            )
            return

        for name, subdir in self.STRUCTURE.items():
            path = self.vault_path / subdir
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(
                    "Created vault directory",
                    extra={"name": name, "path": str(path)},
                )

    def is_available(self) -> bool:
        """Check if vault is mounted and accessible."""
        return self.vault_path.exists() and self.vault_path.is_dir()

    def get_vault_stats(self) -> dict:
        """Get vault storage statistics."""
        if not self.is_available():
            return {"available": False, "total_gb": 0, "used_gb": 0, "free_gb": 0}

        import shutil

        total, used, free = shutil.disk_usage(self.vault_path)
        return {
            "available": True,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
        }

    def _get_dir_size_gb(self, path: Path) -> float:
        """Get total size of directory in GB."""
        total = 0
        try:
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
        except OSError:
            pass
        return round(total / (1024**3), 2)

    def _detect_format(self, model_dir: Path) -> tuple[str, str | None]:
        """Detect model format and quantization from files."""
        for f in model_dir.iterdir():
            if f.suffix == ".gguf":
                # Parse quantization from filename (e.g., model-Q4_K_M.gguf)
                name = f.stem.upper()
                for q in ["Q8_0", "Q6_K", "Q5_K_M", "Q5_K_S", "Q4_K_M", "Q4_K_S", "Q4_0", "Q3_K_M", "Q2_K"]:
                    if q in name:
                        return "gguf", q
                return "gguf", None
            elif f.suffix == ".safetensors":
                return "safetensors", None
            elif f.suffix in {".bin", ".pt", ".pth"}:
                return "pytorch", None

        return "unknown", None

    def _load_metadata(self, model_dir: Path) -> dict:
        """Load model metadata from config files."""
        metadata = {}

        # Check for common config files
        for config_name in ["config.json", "model_config.json", "metadata.json"]:
            config_path = model_dir / config_name
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        metadata.update(json.load(f))
                except (json.JSONDecodeError, OSError):
                    pass

        return metadata

    def scan_models(self) -> list[ModelInfo]:
        """Scan vault for all models."""
        if not self.is_available():
            logger.warning("Vault not available for scanning")
            return []

        models = []

        def scan_dir(base_path: Path, is_base: bool, is_checkpoint: bool, is_lora: bool) -> None:
            if not base_path.exists():
                return

            for item in base_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # Check if this directory contains model files
                    has_model_files = any(
                        f.suffix in self.MODEL_EXTENSIONS
                        for f in item.rglob("*")
                        if f.is_file()
                    )

                    if has_model_files:
                        fmt, quant = self._detect_format(item)
                        models.append(
                            ModelInfo(
                                name=item.name,
                                path=item,
                                relative_path=str(item.relative_to(self.vault_path)),
                                size_gb=self._get_dir_size_gb(item),
                                format=fmt,
                                quantization=quant,
                                is_base=is_base,
                                is_checkpoint=is_checkpoint,
                                is_lora=is_lora,
                                metadata=self._load_metadata(item),
                            )
                        )
                    else:
                        # Recurse into subdirectories (e.g., fine-tuned/genesis/v1)
                        scan_dir(item, is_base, is_checkpoint, is_lora)

        # Scan each category
        scan_dir(self.vault_path / "base", is_base=True, is_checkpoint=False, is_lora=False)
        scan_dir(self.vault_path / "fine-tuned", is_base=False, is_checkpoint=False, is_lora=False)
        scan_dir(self.vault_path / "checkpoints", is_base=False, is_checkpoint=True, is_lora=False)
        scan_dir(self.vault_path / "lora", is_base=False, is_checkpoint=False, is_lora=True)

        logger.info("Vault scan complete", extra={"model_count": len(models)})
        return models

    def get_model(self, name: str) -> ModelInfo | None:
        """Get a specific model by name."""
        models = self.scan_models()
        for m in models:
            if m.name == name:
                return m
        return None

    def get_model_path(self, name: str) -> Path | None:
        """Get full path to a model by name."""
        model = self.get_model(name)
        return model.path if model else None

    def create_model_directory(
        self,
        name: str,
        category: str = "fine-tuned",
        parent: str | None = None,
    ) -> Path:
        """Create a new model directory in the vault."""
        if category not in self.STRUCTURE:
            raise ValueError(f"Invalid category: {category}")

        base = self.vault_path / self.STRUCTURE[category]
        if parent:
            base = base / parent

        model_dir = base / name
        model_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Created model directory",
            extra={"name": name, "path": str(model_dir)},
        )
        return model_dir

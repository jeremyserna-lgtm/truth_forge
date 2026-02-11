"""Capability Manifest — Earned Autonomy System.

NOT-ME doesn't get permissions. NOT-ME proves what it can do.

The Capability Manifest starts empty. As NOT-ME successfully
demonstrates a capability, it gets recorded. The manifest IS
the autonomy boundary — not a whitelist, but a proof-of-work log.

"I'm not creating a whitelist. I'm creating a list of what it
can prove to me. There's just a list of what it can do and its
job is to fill that list." — Jeremy Serna
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

import structlog


logger = structlog.get_logger(service="capability_manifest")


class CapabilityStatus(str, Enum):
    """Status of a capability in the manifest."""

    UNPROVEN = "unproven"  # Not yet demonstrated
    ATTEMPTING = "attempting"  # Currently trying to prove
    PROVEN = "proven"  # Successfully demonstrated
    FAILED = "failed"  # Attempted but failed
    REVOKED = "revoked"  # Was proven, then broke


@dataclass
class CapabilityProof:
    """Evidence that a capability was demonstrated.

    Attributes:
        timestamp: When the proof was recorded.
        description: What happened.
        input_hash: Hash of input that triggered the capability.
        output_hash: Hash of output produced.
        duration_seconds: How long it took.
        success: Whether the demonstration succeeded.
        error: Error message if failed.
    """

    timestamp: datetime
    description: str
    input_hash: str = ""
    output_hash: str = ""
    duration_seconds: float = 0.0
    success: bool = True
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "duration_seconds": round(self.duration_seconds, 2),
            "success": self.success,
            "error": self.error,
        }


@dataclass
class Capability:
    """A single capability in the manifest.

    Attributes:
        id: Unique capability identifier.
        name: Human-readable name.
        description: What this capability means.
        status: Current proof status.
        proofs: History of proof attempts.
        first_proven: When first successfully demonstrated.
        last_proven: When last successfully demonstrated.
        proof_count: Number of successful demonstrations.
        failure_count: Number of failed attempts.
    """

    id: str
    name: str
    description: str
    status: CapabilityStatus = CapabilityStatus.UNPROVEN
    proofs: list[CapabilityProof] = field(default_factory=list)
    first_proven: datetime | None = None
    last_proven: datetime | None = None
    proof_count: int = 0
    failure_count: int = 0

    def record_proof(self, proof: CapabilityProof) -> None:
        """Record a proof attempt for this capability.

        Args:
            proof: The proof to record.
        """
        self.proofs.append(proof)

        if proof.success:
            self.proof_count += 1
            self.last_proven = proof.timestamp
            if self.first_proven is None:
                self.first_proven = proof.timestamp
            self.status = CapabilityStatus.PROVEN
        else:
            self.failure_count += 1
            if self.status == CapabilityStatus.UNPROVEN:
                self.status = CapabilityStatus.FAILED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "proof_count": self.proof_count,
            "failure_count": self.failure_count,
            "first_proven": self.first_proven.isoformat() if self.first_proven else None,
            "last_proven": self.last_proven.isoformat() if self.last_proven else None,
            "proofs": [p.to_dict() for p in self.proofs[-5:]],  # Last 5 proofs
        }


class CapabilityManifest:
    """The Capability Manifest — NOT-ME's proof-of-work log.

    Starts empty. Grows as NOT-ME demonstrates what it can do.
    This IS the autonomy boundary. Not a permission system —
    a demonstration system.

    Capabilities:
    - observe_files: Can detect and read new/changed files
    - atomize_knowledge: Can extract knowledge atoms from text
    - synthesize_insights: Can connect atoms into new understanding
    - forge_narratives: Can create enriched narratives
    - cascade_pipeline: Can run the full cascade autonomously
    - detect_saturation: Can know when to stop looping
    - check_models: Can verify model availability
    - persist_memory: Can save and recall state across sessions
    - generate_podcast: Can create audio from narratives
    - transcribe_audio: Can convert audio back to text
    """

    # The capability registry — everything NOT-ME could potentially do
    CAPABILITY_REGISTRY: ClassVar[dict[str, tuple[str, str]]] = {
        "observe_files": (
            "Observe File Changes",
            "Detect and read new or changed files in watched directories",
        ),
        "observe_browser": (
            "Observe Browser Activity",
            "Read browser history to understand what Jeremy is researching",
        ),
        "check_models": (
            "Check Model Availability",
            "Verify Scout, Maverick, and R1 are online and responsive",
        ),
        "atomize_knowledge": (
            "Atomize Knowledge",
            "Extract irreducible knowledge atoms from text using Scout",
        ),
        "synthesize_insights": (
            "Synthesize Insights",
            "Connect atoms into new cross-domain insights using Maverick",
        ),
        "forge_narratives": (
            "Forge Narratives",
            "Create enriched narratives suitable for podcast discussion",
        ),
        "cascade_pipeline": (
            "Run Cascade Pipeline",
            "Execute the full ATOMIZE → SYNTHESIZE → FORGE loop autonomously",
        ),
        "detect_saturation": (
            "Detect Saturation",
            "Know when the cascade has exhausted new information gain",
        ),
        "persist_memory": (
            "Persist Memory",
            "Save and recall state, proofs, and knowledge across sessions",
        ),
        "generate_podcast": (
            "Generate Podcast",
            "Create debate-format audio from narratives using local TTS",
        ),
        "transcribe_audio": (
            "Transcribe Audio",
            "Convert podcast audio back to text for re-ingestion",
        ),
    }

    def __init__(self, manifest_path: Path | None = None) -> None:
        """Initialize the capability manifest.

        Args:
            manifest_path: Path to persist the manifest. Uses default if None.
        """
        if manifest_path is None:
            from truth_forge.core.paths import DATA_ROOT

            manifest_path = DATA_ROOT / "local" / "manifest" / "capabilities.json"

        self.manifest_path = manifest_path
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.capabilities: dict[str, Capability] = {}
        self._logger = structlog.get_logger(service="capability_manifest")

        # Initialize all known capabilities as UNPROVEN
        for cap_id, (name, description) in self.CAPABILITY_REGISTRY.items():
            self.capabilities[cap_id] = Capability(
                id=cap_id,
                name=name,
                description=description,
            )

        # Load any existing proofs from disk
        self._load()

    def prove(
        self,
        capability_id: str,
        description: str,
        success: bool = True,
        duration_seconds: float = 0.0,
        input_hash: str = "",
        output_hash: str = "",
        error: str = "",
    ) -> Capability:
        """Record a proof attempt for a capability.

        Args:
            capability_id: Which capability was demonstrated.
            description: What happened.
            success: Whether it worked.
            duration_seconds: How long it took.
            input_hash: Hash of input data.
            output_hash: Hash of output data.
            error: Error message if failed.

        Returns:
            The updated Capability.

        Raises:
            KeyError: If capability_id is not in the registry.
        """
        if capability_id not in self.capabilities:
            raise KeyError(
                f"Unknown capability: {capability_id}. Known: {list(self.capabilities.keys())}"
            )

        capability = self.capabilities[capability_id]
        proof = CapabilityProof(
            timestamp=datetime.now(UTC),
            description=description,
            input_hash=input_hash,
            output_hash=output_hash,
            duration_seconds=duration_seconds,
            success=success,
            error=error,
        )

        capability.record_proof(proof)

        self._logger.info(
            "capability_proof_recorded",
            capability=capability_id,
            success=success,
            status=capability.status.value,
            proof_count=capability.proof_count,
        )

        # Persist to disk after every proof
        self._save()

        return capability

    def is_proven(self, capability_id: str) -> bool:
        """Check if a capability has been proven.

        Args:
            capability_id: Which capability to check.

        Returns:
            True if the capability has been successfully demonstrated.
        """
        cap = self.capabilities.get(capability_id)
        return cap is not None and cap.status == CapabilityStatus.PROVEN

    def get_proven(self) -> list[Capability]:
        """Get all proven capabilities.

        Returns:
            List of capabilities with PROVEN status.
        """
        return [cap for cap in self.capabilities.values() if cap.status == CapabilityStatus.PROVEN]

    def get_unproven(self) -> list[Capability]:
        """Get all unproven capabilities.

        Returns:
            List of capabilities NOT yet proven.
        """
        return [cap for cap in self.capabilities.values() if cap.status != CapabilityStatus.PROVEN]

    def summary(self) -> dict[str, Any]:
        """Get a summary of the manifest.

        Returns:
            Dictionary with manifest statistics.
        """
        total = len(self.capabilities)
        proven = len(self.get_proven())
        return {
            "total_capabilities": total,
            "proven": proven,
            "unproven": total - proven,
            "completion_pct": round((proven / total) * 100, 1) if total else 0,
            "proven_list": [cap.name for cap in self.get_proven()],
            "unproven_list": [cap.name for cap in self.get_unproven()],
        }

    def _save(self) -> None:
        """Persist manifest to disk."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "capabilities": {cap_id: cap.to_dict() for cap_id, cap in self.capabilities.items()},
        }

        self.manifest_path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )

    def _load(self) -> None:
        """Load manifest from disk if it exists."""
        if not self.manifest_path.exists():
            return

        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            saved_caps = data.get("capabilities", {})

            for cap_id, cap_data in saved_caps.items():
                if cap_id in self.capabilities:
                    cap = self.capabilities[cap_id]
                    cap.status = CapabilityStatus(cap_data.get("status", "unproven"))
                    cap.proof_count = cap_data.get("proof_count", 0)
                    cap.failure_count = cap_data.get("failure_count", 0)

                    if cap_data.get("first_proven"):
                        cap.first_proven = datetime.fromisoformat(cap_data["first_proven"])
                    if cap_data.get("last_proven"):
                        cap.last_proven = datetime.fromisoformat(cap_data["last_proven"])

            self._logger.info(
                "manifest_loaded",
                path=str(self.manifest_path),
                proven=len(self.get_proven()),
                total=len(self.capabilities),
            )
        except Exception as e:
            self._logger.error(
                "manifest_load_failed",
                error=str(e),
                path=str(self.manifest_path),
            )

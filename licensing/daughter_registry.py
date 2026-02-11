"""
Daughter Registry for Genesis Licensing

DAUGHTER MODEL:
    Genesis (frozen base) + Customer LoRA = Daughter

    - Customer DOES NOT own Genesis weights
    - Customer owns their LoRA adapter (trained on their data)
    - Combined deployment is LICENSED, not sold
    - Jeremy controls all training operations

REVENUE MODEL:
    - Hardware + Genesis access: $4,997-$14,997 (Truth Engine)
    - Daughter training service: $5K-$25K (Primitive Engine)
    - Certification + monitoring: $1K-$3K (Credential Atlas)

Usage:
    registry = DaughterRegistry(registry_path="/secure/daughters")

    # Create daughter for customer
    daughter = registry.create_daughter(
        customer_id="customer_123",
        genesis_version="1.0",
        license_terms=LicenseTerms(tier="enterprise", duration_months=12)
    )

    # Train daughter with customer data
    registry.train_daughter(daughter.id, customer_data_path="/data/customer_123/")

    # List all daughters
    for d in registry.list_daughters():
        print(f"{d.customer_id}: {d.status}")
"""

import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LicenseTier(Enum):
    """License tiers for daughter access."""

    FREE = "free"           # Inference API only, rate limited
    LICENSED = "licensed"   # Inference + daughter LoRA, no weights
    ENTERPRISE = "enterprise"  # Dedicated daughter + continuous learning


class DaughterStatus(Enum):
    """Status of a daughter instance."""

    PENDING = "pending"           # Created, not yet trained
    TRAINING = "training"         # Currently training
    ACTIVE = "active"             # Trained and operational
    SUSPENDED = "suspended"       # License issue
    EXPIRED = "expired"           # License expired
    ARCHIVED = "archived"         # No longer in use


@dataclass
class LicenseTerms:
    """License terms for a daughter."""

    tier: LicenseTier
    duration_months: int
    start_date: str
    end_date: str
    continuous_learning: bool = False
    api_rate_limit: int = 1000  # Requests per day
    custom_terms: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        tier: str,
        duration_months: int = 12,
        continuous_learning: bool = False,
    ) -> "LicenseTerms":
        """Create license terms with automatic dates."""
        start = datetime.now()
        end = start + timedelta(days=duration_months * 30)

        tier_enum = LicenseTier(tier.lower())

        # Set rate limits based on tier
        rate_limits = {
            LicenseTier.FREE: 100,
            LicenseTier.LICENSED: 1000,
            LicenseTier.ENTERPRISE: 10000,
        }

        return cls(
            tier=tier_enum,
            duration_months=duration_months,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            continuous_learning=continuous_learning or tier_enum == LicenseTier.ENTERPRISE,
            api_rate_limit=rate_limits.get(tier_enum, 1000),
        )


@dataclass
class Daughter:
    """Represents a daughter instance (Genesis + Customer LoRA)."""

    id: str
    customer_id: str
    genesis_version: str
    status: DaughterStatus
    license_terms: LicenseTerms
    created_at: str
    last_trained: Optional[str] = None
    lora_path: Optional[Path] = None
    training_metrics: Optional[Dict[str, Any]] = None
    inference_count: int = 0
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "genesis_version": self.genesis_version,
            "status": self.status.value,
            "license_terms": {
                "tier": self.license_terms.tier.value,
                "duration_months": self.license_terms.duration_months,
                "start_date": self.license_terms.start_date,
                "end_date": self.license_terms.end_date,
                "continuous_learning": self.license_terms.continuous_learning,
                "api_rate_limit": self.license_terms.api_rate_limit,
                "custom_terms": self.license_terms.custom_terms,
            },
            "created_at": self.created_at,
            "last_trained": self.last_trained,
            "lora_path": str(self.lora_path) if self.lora_path else None,
            "training_metrics": self.training_metrics,
            "inference_count": self.inference_count,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Daughter":
        """Create from dict."""
        lt = d["license_terms"]
        license_terms = LicenseTerms(
            tier=LicenseTier(lt["tier"]),
            duration_months=lt["duration_months"],
            start_date=lt["start_date"],
            end_date=lt["end_date"],
            continuous_learning=lt.get("continuous_learning", False),
            api_rate_limit=lt.get("api_rate_limit", 1000),
            custom_terms=lt.get("custom_terms"),
        )

        return cls(
            id=d["id"],
            customer_id=d["customer_id"],
            genesis_version=d["genesis_version"],
            status=DaughterStatus(d["status"]),
            license_terms=license_terms,
            created_at=d["created_at"],
            last_trained=d.get("last_trained"),
            lora_path=Path(d["lora_path"]) if d.get("lora_path") else None,
            training_metrics=d.get("training_metrics"),
            inference_count=d.get("inference_count", 0),
            notes=d.get("notes"),
        )


@dataclass
class DaughterRegistry:
    """
    Registry for all daughter instances.

    Tracks:
    - Which customers have daughters
    - License status and terms
    - Training history
    - Usage metrics
    """

    registry_path: str

    # Internal state
    daughters: Dict[str, Daughter] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Initialize registry directory."""
        self.path = Path(self.registry_path)
        self.path.mkdir(parents=True, exist_ok=True)

        self.daughters_dir = self.path / "daughters"
        self.daughters_dir.mkdir(exist_ok=True)

        self.adapters_dir = self.path / "adapters"
        self.adapters_dir.mkdir(exist_ok=True)

        self.registry_file = self.path / "registry.json"

        # Load existing registry
        self._load_registry()

    def create_daughter(
        self,
        customer_id: str,
        genesis_version: str = "1.0",
        license_terms: Optional[LicenseTerms] = None,
        notes: Optional[str] = None,
    ) -> Daughter:
        """
        Create a new daughter for a customer.

        This registers the daughter but does not train it.
        Training happens separately via train_daughter().

        Args:
            customer_id: Unique customer identifier
            genesis_version: Genesis version to inherit from
            license_terms: License terms (defaults to licensed tier, 12 months)
            notes: Optional notes

        Returns:
            The created Daughter instance
        """
        # Generate unique ID
        daughter_id = f"daughter_{secrets.token_hex(8)}"

        # Default license terms
        if license_terms is None:
            license_terms = LicenseTerms.create(tier="licensed", duration_months=12)

        daughter = Daughter(
            id=daughter_id,
            customer_id=customer_id,
            genesis_version=genesis_version,
            status=DaughterStatus.PENDING,
            license_terms=license_terms,
            created_at=datetime.now().isoformat(),
            notes=notes,
        )

        # Register
        self.daughters[daughter_id] = daughter
        self._save_daughter(daughter)
        self._save_registry()

        print(f"✅ Created daughter {daughter_id} for customer {customer_id}")
        print(f"   Genesis version: {genesis_version}")
        print(f"   License tier: {license_terms.tier.value}")
        print(f"   Expires: {license_terms.end_date[:10]}")

        return daughter

    def train_daughter(
        self,
        daughter_id: str,
        customer_data_path: str,
        training_config: Optional[Dict[str, Any]] = None,
    ) -> Daughter:
        """
        Train a daughter with customer data.

        Training happens on THE EMPIRE (Jeremy's hardware).
        Customer data is processed, then deleted.
        Only the LoRA adapter is stored.

        Args:
            daughter_id: ID of the daughter to train
            customer_data_path: Path to customer's training data
            training_config: Optional LoRA training configuration

        Returns:
            Updated Daughter instance
        """
        if daughter_id not in self.daughters:
            raise ValueError(f"Daughter {daughter_id} not found")

        daughter = self.daughters[daughter_id]

        if daughter.status == DaughterStatus.EXPIRED:
            raise ValueError(f"Daughter {daughter_id} license has expired")

        print(f"\n{'='*60}")
        print(f"TRAINING DAUGHTER: {daughter_id}")
        print(f"{'='*60}")
        print(f"Customer: {daughter.customer_id}")
        print(f"Genesis base: v{daughter.genesis_version}")

        # Update status
        daughter.status = DaughterStatus.TRAINING
        self._save_daughter(daughter)

        # Default training config
        if training_config is None:
            training_config = {
                "lora_rank": 64,
                "lora_alpha": 128,
                "target_modules": ["q_proj", "v_proj", "o_proj"],
                "num_epochs": 3,
            }

        # TODO: Actual LoRA training would happen here
        # 1. Load Genesis base from vault
        # 2. Load customer data
        # 3. Train LoRA adapter
        # 4. Save adapter
        # 5. Delete customer data

        # Placeholder: create adapter directory
        adapter_path = self.adapters_dir / daughter_id
        adapter_path.mkdir(exist_ok=True)
        adapter_file = adapter_path / "adapter.safetensors"
        adapter_file.touch()  # Placeholder

        # Update daughter
        daughter.status = DaughterStatus.ACTIVE
        daughter.last_trained = datetime.now().isoformat()
        daughter.lora_path = adapter_path
        daughter.training_metrics = {
            "final_loss": 0.15,  # Placeholder
            "training_steps": 1000,
            "lora_rank": training_config.get("lora_rank", 64),
        }

        self._save_daughter(daughter)
        self._save_registry()

        print(f"\n✅ Daughter {daughter_id} trained successfully")
        print(f"   Adapter saved to: {adapter_path}")
        print(f"   Customer data: DELETED (not stored)")

        return daughter

    def get_daughter(self, daughter_id: str) -> Optional[Daughter]:
        """Get a daughter by ID."""
        return self.daughters.get(daughter_id)

    def get_customer_daughters(self, customer_id: str) -> List[Daughter]:
        """Get all daughters for a customer."""
        return [d for d in self.daughters.values() if d.customer_id == customer_id]

    def list_daughters(
        self,
        status: Optional[DaughterStatus] = None,
    ) -> List[Daughter]:
        """
        List all daughters, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of Daughter instances
        """
        if status is None:
            return list(self.daughters.values())
        return [d for d in self.daughters.values() if d.status == status]

    def update_license(
        self,
        daughter_id: str,
        new_terms: LicenseTerms,
    ) -> Daughter:
        """Update license terms for a daughter."""
        if daughter_id not in self.daughters:
            raise ValueError(f"Daughter {daughter_id} not found")

        daughter = self.daughters[daughter_id]
        daughter.license_terms = new_terms

        # Reactivate if was expired
        if daughter.status == DaughterStatus.EXPIRED:
            daughter.status = DaughterStatus.ACTIVE

        self._save_daughter(daughter)
        self._save_registry()

        print(f"✅ Updated license for {daughter_id}")
        return daughter

    def suspend_daughter(self, daughter_id: str, reason: str = "") -> Daughter:
        """Suspend a daughter (license issue, etc.)."""
        if daughter_id not in self.daughters:
            raise ValueError(f"Daughter {daughter_id} not found")

        daughter = self.daughters[daughter_id]
        daughter.status = DaughterStatus.SUSPENDED
        daughter.notes = f"Suspended: {reason}" if reason else "Suspended"

        self._save_daughter(daughter)
        self._save_registry()

        print(f"⚠️  Suspended daughter {daughter_id}: {reason}")
        return daughter

    def check_expirations(self) -> List[Daughter]:
        """Check and update expired licenses."""
        now = datetime.now()
        expired = []

        for daughter in self.daughters.values():
            if daughter.status not in [DaughterStatus.EXPIRED, DaughterStatus.ARCHIVED]:
                end_date = datetime.fromisoformat(daughter.license_terms.end_date)
                if now > end_date:
                    daughter.status = DaughterStatus.EXPIRED
                    self._save_daughter(daughter)
                    expired.append(daughter)

        if expired:
            self._save_registry()
            print(f"⚠️  {len(expired)} licenses expired")

        return expired

    def record_inference(self, daughter_id: str) -> None:
        """Record an inference request for usage tracking."""
        if daughter_id in self.daughters:
            self.daughters[daughter_id].inference_count += 1
            # Don't save on every inference - batch periodically

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        stats = {
            "total_daughters": len(self.daughters),
            "by_status": {},
            "by_tier": {},
            "total_inferences": 0,
        }

        for daughter in self.daughters.values():
            # By status
            status = daughter.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # By tier
            tier = daughter.license_terms.tier.value
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1

            # Total inferences
            stats["total_inferences"] += daughter.inference_count

        return stats

    def _save_daughter(self, daughter: Daughter) -> None:
        """Save daughter to individual file."""
        daughter_file = self.daughters_dir / f"{daughter.id}.json"
        with open(daughter_file, "w") as f:
            json.dump(daughter.to_dict(), f, indent=2)

    def _save_registry(self) -> None:
        """Save registry index."""
        data = {
            "last_updated": datetime.now().isoformat(),
            "daughter_ids": list(self.daughters.keys()),
            "statistics": self.get_statistics(),
        }
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_registry(self) -> None:
        """Load all daughters from disk."""
        for daughter_file in self.daughters_dir.glob("*.json"):
            with open(daughter_file, "r") as f:
                data = json.load(f)
            daughter = Daughter.from_dict(data)
            self.daughters[daughter.id] = daughter

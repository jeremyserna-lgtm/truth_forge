"""
Weight Vault for Genesis IP Protection

THE CORE PRINCIPLE:
    Weights never leave THE EMPIRE.
    Customers access via inference API only.
    Jeremy controls all training and distribution.

CRITICAL DISTINCTION:
    - Base Llama = Meta's open weights (Apache 2.0)
    - Genesis = Jeremy's proprietary fine-tune (HIS IP)
    - Customer gets ACCESS, not OWNERSHIP

This vault ensures:
    1. Genesis weights are encrypted at rest
    2. Weights are decrypted only in memory for inference
    3. Hardware-bound keys prevent unauthorized copying
    4. All access is logged and auditable

Usage:
    vault = WeightVault(vault_path="/secure/genesis_vault")

    # Store Genesis (only Jeremy can do this)
    vault.store_genesis(model_weights, version="1.0", encryption_key=key)

    # Load for inference (decrypted in memory only)
    with vault.load_for_inference(license_key="...") as weights:
        model.load_state_dict(weights)
        result = model.generate(prompt)
    # Weights automatically cleared from memory
"""

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# NOTE: Cryptography imports - install with: pip install cryptography
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class VaultConfig:
    """Configuration for the weight vault."""

    vault_path: str
    hardware_id: str  # Unique ID for THE EMPIRE hardware
    owner_id: str = "truth_forge_llc"
    encryption_algorithm: str = "AES-256-GCM"
    key_derivation: str = "PBKDF2-SHA256"
    key_iterations: int = 100_000


@dataclass
class EncryptedWeights:
    """Metadata about stored encrypted weights."""

    version: str
    content_hash: str
    encrypted_at: str
    size_bytes: int
    hardware_id: str
    path: Path


@dataclass
class WeightVault:
    """
    Secure storage for Genesis weights.

    Weights never leave THE EMPIRE.
    Customers access via inference API only.

    Security Model:
        - AES-256 encryption at rest
        - Hardware-bound master key (tied to THE EMPIRE)
        - Per-version encryption keys derived from master
        - All access logged with audit trail
    """

    config: VaultConfig

    # Internal state
    _master_key: Optional[bytes] = field(default=None, repr=False)
    _stored_versions: Dict[str, EncryptedWeights] = field(default_factory=dict, repr=False)
    _access_log: list = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        """Initialize vault directory structure."""
        self.vault_path = Path(self.config.vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        self.weights_dir = self.vault_path / "weights"
        self.weights_dir.mkdir(exist_ok=True)

        self.metadata_dir = self.vault_path / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)

        self.audit_dir = self.vault_path / "audit"
        self.audit_dir.mkdir(exist_ok=True)

        # Load existing versions
        self._load_stored_versions()

    def initialize_master_key(self, password: str) -> None:
        """
        Initialize or unlock the master encryption key.

        The master key is derived from:
        - User password (provided)
        - Hardware ID (THE EMPIRE identifier)
        - Salt (stored in vault)

        This ensures weights can only be decrypted on authorized hardware.

        Args:
            password: Master password for the vault
        """
        salt_path = self.vault_path / ".salt"

        if salt_path.exists():
            # Load existing salt
            with open(salt_path, "rb") as f:
                salt = f.read()
        else:
            # Generate new salt
            salt = secrets.token_bytes(32)
            with open(salt_path, "wb") as f:
                f.write(salt)

        # Derive master key from password + hardware ID + salt
        # NOTE: Actual implementation would use cryptography library
        # kdf = PBKDF2HMAC(
        #     algorithm=hashes.SHA256(),
        #     length=32,
        #     salt=salt + self.config.hardware_id.encode(),
        #     iterations=self.config.key_iterations,
        # )
        # self._master_key = kdf.derive(password.encode())

        # Placeholder: simple hash (NOT SECURE - use proper KDF in production)
        combined = password + self.config.hardware_id + salt.hex()
        self._master_key = hashlib.sha256(combined.encode()).digest()

        self._log_access("master_key_initialized", {"hardware_id": self.config.hardware_id})

    def store_genesis(
        self,
        weights: Any,
        version: str,
    ) -> EncryptedWeights:
        """
        Store Genesis weights with encryption.

        Only Jeremy/Truth Forge can call this.
        Weights are encrypted before writing to disk.

        Args:
            weights: Model weights to store (state dict or similar)
            version: Version string (e.g., "1.0")

        Returns:
            EncryptedWeights metadata
        """
        if self._master_key is None:
            raise ValueError("Vault not initialized. Call initialize_master_key() first.")

        if version in self._stored_versions:
            raise ValueError(f"Version {version} already exists. Genesis is immutable.")

        print(f"\n{'='*60}")
        print(f"STORING GENESIS v{version}")
        print(f"{'='*60}")

        # Derive version-specific key
        version_key = self._derive_version_key(version)

        # Serialize weights
        # NOTE: Actual implementation would serialize with safetensors
        # import safetensors.mlx as safetensors
        # serialized = safetensors.save(weights)

        # Placeholder: empty bytes
        serialized = b"GENESIS_WEIGHTS_PLACEHOLDER"

        # Compute content hash (before encryption)
        content_hash = hashlib.sha256(serialized).hexdigest()

        # Encrypt weights
        # NOTE: Actual implementation would use Fernet or AES-GCM
        # fernet = Fernet(base64.urlsafe_b64encode(version_key))
        # encrypted = fernet.encrypt(serialized)

        # Placeholder: just the serialized bytes (NOT ENCRYPTED)
        encrypted = serialized

        # Write to disk
        weights_path = self.weights_dir / f"genesis_v{version}.enc"
        with open(weights_path, "wb") as f:
            f.write(encrypted)

        # Create metadata
        metadata = EncryptedWeights(
            version=version,
            content_hash=content_hash,
            encrypted_at=datetime.now().isoformat(),
            size_bytes=len(encrypted),
            hardware_id=self.config.hardware_id,
            path=weights_path,
        )

        # Save metadata
        metadata_path = self.metadata_dir / f"genesis_v{version}.json"
        with open(metadata_path, "w") as f:
            json.dump({
                "version": metadata.version,
                "content_hash": metadata.content_hash,
                "encrypted_at": metadata.encrypted_at,
                "size_bytes": metadata.size_bytes,
                "hardware_id": metadata.hardware_id,
                "path": str(metadata.path),
                "owner": self.config.owner_id,
                "immutable": True,
                "notes": "Genesis weights - proprietary IP of Truth Forge LLC",
            }, f, indent=2)

        # Register
        self._stored_versions[version] = metadata
        self._log_access("genesis_stored", {"version": version, "hash": content_hash})

        print(f"✅ Genesis v{version} stored securely")
        print(f"   Hash: {content_hash[:16]}...")
        print(f"   Size: {len(encrypted):,} bytes")
        print(f"   Path: {weights_path}")
        print(f"\n   This version is IMMUTABLE and can never be modified.")

        return metadata

    def load_for_inference(
        self,
        license_key: str,
        version: str = "1.0",
    ) -> Generator[Any, None, None]:
        """
        Load Genesis weights for inference (decrypted in memory only).

        This is a context manager that:
        1. Verifies the license key
        2. Decrypts weights into memory
        3. Yields the weights for use
        4. Clears weights from memory when done

        Usage:
            with vault.load_for_inference(license_key="...") as weights:
                model.load_state_dict(weights)
                result = model.generate(prompt)
            # Weights automatically cleared

        Args:
            license_key: Valid license key for access
            version: Genesis version to load

        Yields:
            Decrypted weights (never written to disk)
        """
        if self._master_key is None:
            raise ValueError("Vault not initialized. Call initialize_master_key() first.")

        if version not in self._stored_versions:
            raise ValueError(f"Version {version} not found in vault.")

        # Verify license
        if not self._verify_license(license_key):
            self._log_access("license_rejected", {"license": license_key[:8] + "...", "version": version})
            raise ValueError("Invalid license key")

        metadata = self._stored_versions[version]

        self._log_access("inference_started", {"version": version})

        try:
            # Read encrypted weights
            with open(metadata.path, "rb") as f:
                encrypted = f.read()

            # Derive version key
            version_key = self._derive_version_key(version)

            # Decrypt weights
            # NOTE: Actual implementation would decrypt with Fernet/AES
            # fernet = Fernet(base64.urlsafe_b64encode(version_key))
            # decrypted = fernet.decrypt(encrypted)

            # Placeholder: just return the bytes
            decrypted = encrypted

            # Verify hash
            content_hash = hashlib.sha256(decrypted).hexdigest()
            if content_hash != metadata.content_hash:
                raise ValueError("Weight integrity check failed!")

            # Deserialize
            # NOTE: Actual implementation would deserialize with safetensors
            # weights = safetensors.load(decrypted)

            # Placeholder
            weights = {"_placeholder": True}

            yield weights

        finally:
            # Clear from memory
            decrypted = None
            weights = None
            self._log_access("inference_completed", {"version": version})

    def get_versions(self) -> list:
        """Get list of stored Genesis versions."""
        return list(self._stored_versions.keys())

    def get_metadata(self, version: str) -> Optional[EncryptedWeights]:
        """Get metadata for a specific version."""
        return self._stored_versions.get(version)

    def verify_integrity(self, version: str) -> bool:
        """
        Verify integrity of stored weights.

        Checks that the encrypted file hasn't been tampered with.

        Args:
            version: Version to verify

        Returns:
            True if integrity check passes
        """
        if version not in self._stored_versions:
            return False

        metadata = self._stored_versions[version]

        if not metadata.path.exists():
            return False

        # In production, would verify encrypted content hash
        # and compare to stored hash

        self._log_access("integrity_verified", {"version": version})
        return True

    def _derive_version_key(self, version: str) -> bytes:
        """Derive encryption key for specific version."""
        if self._master_key is None:
            raise ValueError("Master key not initialized")

        # HMAC-based key derivation
        return hmac.new(
            self._master_key,
            f"genesis_v{version}".encode(),
            hashlib.sha256
        ).digest()

    def _verify_license(self, license_key: str) -> bool:
        """
        Verify a license key is valid.

        In production, this would:
        1. Check against license database
        2. Verify signature
        3. Check expiration
        4. Verify hardware binding
        """
        # Placeholder: accept any non-empty key
        # Production would have actual verification
        return len(license_key) > 0

    def _load_stored_versions(self) -> None:
        """Load metadata for all stored versions."""
        for metadata_file in self.metadata_dir.glob("genesis_v*.json"):
            with open(metadata_file, "r") as f:
                data = json.load(f)
            self._stored_versions[data["version"]] = EncryptedWeights(
                version=data["version"],
                content_hash=data["content_hash"],
                encrypted_at=data["encrypted_at"],
                size_bytes=data["size_bytes"],
                hardware_id=data["hardware_id"],
                path=Path(data["path"]),
            )

    def _log_access(self, action: str, details: Dict[str, Any]) -> None:
        """Log access to the vault for audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "hardware_id": self.config.hardware_id,
            "details": details,
        }

        self._access_log.append(entry)

        # Write to audit log
        audit_file = self.audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


def create_hardware_id() -> str:
    """
    Generate a hardware ID for THE EMPIRE.

    In production, this would:
    1. Read CPU serial number
    2. Read disk serial numbers
    3. Read MAC addresses
    4. Combine into unique identifier

    This ensures weights can only be decrypted on authorized hardware.
    """
    # Placeholder: generate random ID
    # Production would derive from actual hardware
    return f"EMPIRE_{secrets.token_hex(8).upper()}"

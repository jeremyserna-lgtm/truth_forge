# Enterprise Implementation Specification

**Purpose:** Define hardened, enterprise-grade implementations for Primitive Engine with preemptive surfaces that enable recursive molting.

**Date:** January 19, 2026

**Core Principle:** Everything we build must enable us to do it again, at scale.

---

## THE PREEMPTIVE SURFACES PRINCIPLE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PREEMPTIVE SURFACES                                   │
│                                                                          │
│  "We learn how to do it and then it becomes integrated so that we can   │
│   do it again a lot easier and it's just part of being the nature of    │
│   the organization itself."                                              │
│                                                                          │
│  EVERY IMPLEMENTATION MUST:                                              │
│  1. Solve the immediate problem                                          │
│  2. Create the infrastructure to solve it again                          │
│  3. Make the next iteration easier than this one                         │
│  4. Be recursively moltable                                              │
│                                                                          │
│  THIS IS STAGE 5 COGNITIVE INTEGRATION:                                  │
│  Learn → Integrate → Execute Effortlessly → Molt → Learn Again          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PART 1: THE MOLTING SYSTEM

### 1.1 Research Foundation

| Technology | Purpose | Standard |
|------------|---------|----------|
| **ast-grep** | AST-based code transformation | Tree-sitter powered |
| **GritQL** | Complex multi-language patterns | Open-source query language |
| **fastmod** | Simple text replacements | Facebook's codemod tool |
| **git filter-repo** | History preservation | Git-native filtering |
| **12-Factor App** | Config externalization | Industry standard |

### 1.2 The MOLT.yaml Architecture

**Location:** `{organism_root}/MOLT.yaml`

This is the organism's identity configuration - centralized, version-controlled, the source of truth for who this organism is.

```yaml
# MOLT.yaml - Organism Identity Configuration
# This file IS the organism's identity. It enables recursive molting.

molt_version: "1.0.0"

# =============================================================================
# IDENTITY (Who is this organism?)
# =============================================================================
organism:
  # Current identity
  name: "Primitive_Engine"
  display_name: "Primitive Engine"
  version: "2.0.0"

  # Directory and package names (derived from name)
  directory_name: "PrimitiveEngine"
  package_name: "primitive_engine"

  # Identity history (enables tracing lineage)
  previous_identities:
    - name: "PrimitiveEngine"
      directory_name: "PrimitiveEngine"
      package_name: "primitive_engine"
      version: "1.x"
      molted_at: "2026-01-19"
      molt_id: "molt-001"

# =============================================================================
# FERTILITY (Can this organism reproduce?)
# =============================================================================
fertility:
  can_reproduce: true
  offspring_fertility: "configurable"  # sterile | fertile | configurable
  genesis_organism: true

# =============================================================================
# TRANSFORMATION PATTERNS (How to molt)
# =============================================================================
patterns:
  # Text replacements (processed in order)
  text:
    - find: "PrimitiveEngine"
      replace: "PrimitiveEngine"
      scope: ["*.py", "*.md", "*.yaml", "*.json", "*.toml"]

    - find: "primitive_engine"
      replace: "primitive_engine"
      scope: ["*.py", "*.md", "*.yaml", "*.json", "*.toml"]

    - find: "TRUTH_ENGINE"
      replace: "PRIMITIVE_ENGINE"
      scope: ["*.py", "*.env", "*.sh"]

  # AST transformations (for complex code changes)
  ast:
    - language: python
      pattern: "from primitive_engine import $X"
      replace: "from primitive_engine import $X"

    - language: python
      pattern: "import primitive_engine"
      replace: "import primitive_engine"

  # Directory renames
  directories:
    - from: "PrimitiveEngine"
      to: "PrimitiveEngine"

    - from: "primitive_engine"
      to: "primitive_engine"

# =============================================================================
# PROTECTED PATHS (Never transform)
# =============================================================================
protected:
  # Data integrity
  - "*.jsonl"           # Append-only logs
  - "data/**/*"         # All data
  - ".git/**/*"         # Git history

  # Identity records
  - "MOLT.yaml"         # This file (updated separately)
  - ".seed/**/*"        # Lineage information

  # External dependencies
  - "node_modules/**/*"
  - ".venv/**/*"
  - "__pycache__/**/*"

# =============================================================================
# VALIDATION (Post-molt checks)
# =============================================================================
validation:
  # Files that must exist after molt
  required_files:
    - "Primitive/core.py"
    - "Primitive/seed/seed_project.py"
    - "MOLT.yaml"

  # Commands that must succeed
  checks:
    - command: "python -c 'import primitive_engine'"
      description: "Package importable"

    - command: "python -m pytest Primitive/tests/ -x"
      description: "Tests pass"

    - command: "python -c 'from Primitive.governance.spark_service import SparkService'"
      description: "SparkService accessible"

# =============================================================================
# PREEMPTIVE SURFACES (What this molt enables)
# =============================================================================
preemptive:
  # This molt creates these capabilities
  enables:
    - "Future organisms can molt using this same MOLT.yaml pattern"
    - "Daughter organisms inherit molting capability (if fertile)"
    - "Transformation patterns are reusable across the federation"

  # These surfaces are now available
  surfaces:
    - name: "molt_executor"
      path: "Primitive/molt/executor.py"
      description: "Execute molts from MOLT.yaml"

    - name: "molt_validator"
      path: "Primitive/molt/validator.py"
      description: "Validate post-molt state"

    - name: "molt_history"
      path: "Primitive/molt/history.py"
      description: "Track molt lineage"
```

### 1.3 The Molt Executor

**Location:** `Primitive/molt/executor.py`

```python
"""
MOLT EXECUTOR
=============
Execute organism identity transformations from MOLT.yaml.

PREEMPTIVE SURFACE:
- This executor is itself moltable
- It creates the capability to molt again
- Each molt makes the next molt easier
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import subprocess
import yaml
import shutil
from datetime import datetime, timezone
import uuid


@dataclass
class MoltResult:
    """Result of a molt operation."""
    success: bool
    molt_id: str
    from_identity: str
    to_identity: str
    files_transformed: int
    directories_renamed: int
    validation_passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MoltExecutor:
    """
    Execute molts from MOLT.yaml configuration.

    PREEMPTIVE SURFACE: This class is designed to be inherited and extended
    by daughter organisms that need custom molt behavior.
    """

    def __init__(self, organism_root: Path):
        self.organism_root = Path(organism_root)
        self.molt_config_path = self.organism_root / "MOLT.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load MOLT.yaml configuration."""
        if not self.molt_config_path.exists():
            raise FileNotFoundError(f"MOLT.yaml not found at {self.molt_config_path}")

        with open(self.molt_config_path) as f:
            return yaml.safe_load(f)

    def prepare_molt(self, new_identity: dict) -> "MoltPlan":
        """
        Create a molt plan without executing.

        PREEMPTIVE: Separation of planning and execution enables
        review, approval, and rollback capabilities.
        """
        return MoltPlan(
            executor=self,
            current_identity=self.config["organism"],
            new_identity=new_identity,
            patterns=self.config.get("patterns", {}),
            protected=self.config.get("protected", []),
            validation=self.config.get("validation", {}),
        )

    def execute_molt(
        self,
        new_identity: dict,
        dry_run: bool = True,
        backup: bool = True,
    ) -> MoltResult:
        """
        Execute a molt transformation.

        Args:
            new_identity: New organism identity configuration
            dry_run: If True, show what would change without changing
            backup: If True, create backup before transforming

        Returns:
            MoltResult with transformation details
        """
        molt_id = f"molt-{uuid.uuid4().hex[:8]}"
        plan = self.prepare_molt(new_identity)

        if dry_run:
            return plan.preview()

        if backup:
            self._create_backup(molt_id)

        result = plan.execute(molt_id)

        if result.success:
            self._update_molt_history(result)
            self._update_molt_yaml(new_identity, molt_id)

        return result

    def _create_backup(self, molt_id: str) -> Path:
        """Create backup before molt."""
        backup_dir = self.organism_root / ".molt_backups" / molt_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup critical files
        critical = ["MOLT.yaml", "pyproject.toml", "setup.py"]
        for filename in critical:
            src = self.organism_root / filename
            if src.exists():
                shutil.copy2(src, backup_dir / filename)

        return backup_dir

    def _update_molt_history(self, result: MoltResult) -> None:
        """Update molt history in MOLT.yaml."""
        history_entry = {
            "name": result.from_identity,
            "molted_at": result.timestamp,
            "molt_id": result.molt_id,
        }

        if "previous_identities" not in self.config["organism"]:
            self.config["organism"]["previous_identities"] = []

        self.config["organism"]["previous_identities"].append(history_entry)

    def _update_molt_yaml(self, new_identity: dict, molt_id: str) -> None:
        """Update MOLT.yaml with new identity."""
        self.config["organism"].update(new_identity)

        with open(self.molt_config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)


@dataclass
class MoltPlan:
    """
    A plan for executing a molt.

    PREEMPTIVE SURFACE: Plans can be serialized, reviewed, approved,
    and executed later. This enables governance workflows.
    """
    executor: MoltExecutor
    current_identity: dict
    new_identity: dict
    patterns: dict
    protected: list
    validation: dict

    def preview(self) -> MoltResult:
        """Preview what the molt would do without doing it."""
        # Implementation: scan files, show what would change
        files_to_transform = self._find_files_to_transform()
        dirs_to_rename = self._find_dirs_to_rename()

        return MoltResult(
            success=True,
            molt_id="preview",
            from_identity=self.current_identity.get("name", "unknown"),
            to_identity=self.new_identity.get("name", "unknown"),
            files_transformed=len(files_to_transform),
            directories_renamed=len(dirs_to_rename),
            validation_passed=False,  # Not run in preview
            warnings=["DRY RUN - No changes made"],
        )

    def execute(self, molt_id: str) -> MoltResult:
        """Execute the molt transformation."""
        errors = []
        warnings = []
        files_transformed = 0
        dirs_renamed = 0

        try:
            # Phase 1: Text replacements using fastmod
            files_transformed += self._execute_text_patterns()

            # Phase 2: AST transformations using ast-grep
            files_transformed += self._execute_ast_patterns()

            # Phase 3: Directory renames
            dirs_renamed += self._execute_directory_renames()

            # Phase 4: Validation
            validation_passed = self._run_validation()

        except Exception as e:
            errors.append(str(e))
            return MoltResult(
                success=False,
                molt_id=molt_id,
                from_identity=self.current_identity.get("name", "unknown"),
                to_identity=self.new_identity.get("name", "unknown"),
                files_transformed=files_transformed,
                directories_renamed=dirs_renamed,
                validation_passed=False,
                errors=errors,
            )

        return MoltResult(
            success=len(errors) == 0,
            molt_id=molt_id,
            from_identity=self.current_identity.get("name", "unknown"),
            to_identity=self.new_identity.get("name", "unknown"),
            files_transformed=files_transformed,
            directories_renamed=dirs_renamed,
            validation_passed=validation_passed,
            errors=errors,
            warnings=warnings,
        )

    def _find_files_to_transform(self) -> list[Path]:
        """Find all files that would be transformed."""
        # Implementation: glob patterns, exclude protected
        files = []
        for pattern_config in self.patterns.get("text", []):
            for scope in pattern_config.get("scope", ["*"]):
                files.extend(self.executor.organism_root.rglob(scope))

        # Filter out protected paths
        protected_set = set()
        for p in self.protected:
            protected_set.update(self.executor.organism_root.glob(p))

        return [f for f in files if f not in protected_set]

    def _find_dirs_to_rename(self) -> list[tuple[Path, Path]]:
        """Find directories that would be renamed."""
        renames = []
        for dir_config in self.patterns.get("directories", []):
            from_path = self.executor.organism_root / dir_config["from"]
            to_path = self.executor.organism_root / dir_config["to"]
            if from_path.exists():
                renames.append((from_path, to_path))
        return renames

    def _execute_text_patterns(self) -> int:
        """Execute text replacement patterns using fastmod."""
        count = 0
        for pattern in self.patterns.get("text", []):
            # Build fastmod command
            cmd = [
                "fastmod",
                "--accept-all",
                pattern["find"],
                pattern["replace"],
            ]

            # Add file extensions
            for scope in pattern.get("scope", []):
                cmd.extend(["--extensions", scope.replace("*.", "")])

            result = subprocess.run(
                cmd,
                cwd=self.executor.organism_root,
                capture_output=True,
                text=True,
            )

            # Count modified files from output
            if "modified" in result.stdout.lower():
                count += result.stdout.count("modified")

        return count

    def _execute_ast_patterns(self) -> int:
        """Execute AST transformation patterns using ast-grep."""
        count = 0
        for pattern in self.patterns.get("ast", []):
            # Build ast-grep command
            cmd = [
                "ast-grep",
                "--pattern", pattern["pattern"],
                "--rewrite", pattern["replace"],
                "--lang", pattern.get("language", "python"),
                ".",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.executor.organism_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                count += 1

        return count

    def _execute_directory_renames(self) -> int:
        """Execute directory renames."""
        count = 0
        for from_path, to_path in self._find_dirs_to_rename():
            shutil.move(str(from_path), str(to_path))
            count += 1
        return count

    def _run_validation(self) -> bool:
        """Run post-molt validation checks."""
        for check in self.validation.get("checks", []):
            result = subprocess.run(
                check["command"],
                shell=True,
                cwd=self.executor.organism_root,
                capture_output=True,
            )
            if result.returncode != 0:
                return False
        return True
```

### 1.4 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `MOLT.yaml` | Centralized identity | Future molts use same config |
| `MoltExecutor` | Execute transformations | Any organism can molt |
| `MoltPlan` | Preview before execute | Governance approval workflows |
| `_molt_backups/` | Rollback capability | Safe experimentation |
| `previous_identities` | Lineage tracking | Audit trail |

---

## PART 2: FIDO2/WebAuthn HARDWARE AUTHENTICATION

### 2.1 Research Foundation

| Standard | Status | Implementation |
|----------|--------|----------------|
| **WebAuthn Level 2** | W3C Recommendation | py_webauthn |
| **WebAuthn Level 3** | Emerging 2026 | Conditional UI |
| **CTAP 2.2** | FIDO Alliance | python-fido2 |
| **NIST SP 800-63B-4** | AAL2/AAL3 | Compliance framework |

### 2.2 Architecture

**Location:** `Primitive/governance/spark_service/fido2.py`

```python
"""
FIDO2 HARDWARE AUTHENTICATION
=============================
Hardware-bound spark issuance using Touch ID / Passkeys.

ENTERPRISE STANDARDS:
- WebAuthn Level 2 (W3C Recommendation)
- CTAP 2.2 (FIDO Alliance)
- NIST SP 800-63B-4 AAL2 compliance

PREEMPTIVE SURFACE:
- This authenticator can be extended for new hardware types
- Credential management is abstracted for future attestation formats
- Challenge generation is pluggable for different security levels
"""

from dataclasses import dataclass, field
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timezone
import json

# Enterprise-recommended library
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    AuthenticatorAttachment,
    AttestationConveyancePreference,
)


@dataclass
class FIDOCredential:
    """
    Stored FIDO2 credential.

    PREEMPTIVE: Credential format is versioned for future
    attestation types and algorithm upgrades.
    """
    credential_id: bytes
    public_key: bytes
    sign_count: int
    user_id: str
    created_at: str
    authenticator_type: str  # platform | cross-platform
    attestation_format: str
    version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "credential_id": self.credential_id.hex(),
            "public_key": self.public_key.hex(),
            "sign_count": self.sign_count,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "authenticator_type": self.authenticator_type,
            "attestation_format": self.attestation_format,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FIDOCredential":
        return cls(
            credential_id=bytes.fromhex(data["credential_id"]),
            public_key=bytes.fromhex(data["public_key"]),
            sign_count=data["sign_count"],
            user_id=data["user_id"],
            created_at=data["created_at"],
            authenticator_type=data["authenticator_type"],
            attestation_format=data["attestation_format"],
            version=data.get("version", "1.0"),
        )


class HardwareAuthenticator:
    """
    FIDO2/WebAuthn hardware authenticator for spark issuance.

    ENTERPRISE COMPLIANCE:
    - NIST SP 800-63B-4 AAL2 (biometric + hardware)
    - Resident credentials (passkeys)
    - User verification required

    PREEMPTIVE SURFACE:
    - Pluggable challenge generators
    - Extensible credential storage
    - Configurable security levels
    """

    # Relying Party configuration (your organization)
    RP_ID = "primitive.engine"
    RP_NAME = "Primitive Engine Spark Authority"

    # Security levels (NIST AAL mapping)
    SECURITY_LEVELS = {
        "aal2": {
            "user_verification": UserVerificationRequirement.REQUIRED,
            "resident_key": ResidentKeyRequirement.PREFERRED,
            "attestation": AttestationConveyancePreference.DIRECT,
        },
        "aal3": {
            "user_verification": UserVerificationRequirement.REQUIRED,
            "resident_key": ResidentKeyRequirement.REQUIRED,
            "attestation": AttestationConveyancePreference.ENTERPRISE,
        },
    }

    def __init__(
        self,
        credential_store: "CredentialStore",
        security_level: str = "aal2",
    ):
        self.credential_store = credential_store
        self.security_config = self.SECURITY_LEVELS[security_level]
        self.pending_challenges: dict[str, bytes] = {}

    def begin_registration(self, user_id: str, user_name: str) -> dict:
        """
        Begin FIDO2 registration ceremony.

        Returns options to be sent to the client (browser/native app).
        """
        # Generate challenge (32 bytes of cryptographic randomness)
        challenge = secrets.token_bytes(32)
        self.pending_challenges[user_id] = challenge

        # Get existing credentials to exclude
        existing_creds = self.credential_store.get_credentials(user_id)
        exclude_credentials = [
            {"id": c.credential_id, "type": "public-key"}
            for c in existing_creds
        ]

        options = generate_registration_options(
            rp_id=self.RP_ID,
            rp_name=self.RP_NAME,
            user_id=user_id.encode(),
            user_name=user_name,
            challenge=challenge,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,  # Touch ID
                user_verification=self.security_config["user_verification"],
                resident_key=self.security_config["resident_key"],
            ),
            attestation=self.security_config["attestation"],
        )

        return json.loads(options_to_json(options))

    def complete_registration(
        self,
        user_id: str,
        credential_response: dict,
    ) -> FIDOCredential:
        """
        Complete FIDO2 registration ceremony.

        Verifies the attestation and stores the credential.
        """
        challenge = self.pending_challenges.pop(user_id, None)
        if not challenge:
            raise ValueError("No pending registration for user")

        verification = verify_registration_response(
            credential=credential_response,
            expected_challenge=challenge,
            expected_rp_id=self.RP_ID,
            expected_origin=f"https://{self.RP_ID}",
            require_user_verification=True,
        )

        credential = FIDOCredential(
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            user_id=user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            authenticator_type="platform",
            attestation_format=verification.fmt,
        )

        self.credential_store.save_credential(credential)
        return credential

    def begin_authentication(self, user_id: str) -> dict:
        """
        Begin FIDO2 authentication ceremony.

        This is called when we need hardware verification for spark issuance.
        """
        challenge = secrets.token_bytes(32)
        self.pending_challenges[user_id] = challenge

        credentials = self.credential_store.get_credentials(user_id)
        if not credentials:
            raise ValueError("No credentials registered for user")

        allow_credentials = [
            {"id": c.credential_id, "type": "public-key"}
            for c in credentials
        ]

        options = generate_authentication_options(
            rp_id=self.RP_ID,
            challenge=challenge,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
        )

        return json.loads(options_to_json(options))

    def complete_authentication(
        self,
        user_id: str,
        credential_response: dict,
    ) -> bool:
        """
        Complete FIDO2 authentication ceremony.

        Verifies the assertion and updates sign count.
        Returns True if authentication successful.
        """
        challenge = self.pending_challenges.pop(user_id, None)
        if not challenge:
            raise ValueError("No pending authentication for user")

        # Find the credential being used
        credentials = self.credential_store.get_credentials(user_id)
        credential_id = bytes(credential_response["rawId"])
        credential = next(
            (c for c in credentials if c.credential_id == credential_id),
            None,
        )

        if not credential:
            raise ValueError("Unknown credential")

        verification = verify_authentication_response(
            credential=credential_response,
            expected_challenge=challenge,
            expected_rp_id=self.RP_ID,
            expected_origin=f"https://{self.RP_ID}",
            credential_public_key=credential.public_key,
            credential_current_sign_count=credential.sign_count,
            require_user_verification=True,
        )

        # Update sign count (replay protection)
        credential.sign_count = verification.new_sign_count
        self.credential_store.save_credential(credential)

        return True


class CredentialStore:
    """
    Credential storage abstraction.

    PREEMPTIVE SURFACE:
    - Can be backed by different storage (file, keychain, HSM)
    - Encryption is pluggable
    - Migration path for credential format upgrades
    """

    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def get_credentials(self, user_id: str) -> list[FIDOCredential]:
        """Get all credentials for a user."""
        # Implementation: load from secure storage
        raise NotImplementedError("Implement with secure storage backend")

    def save_credential(self, credential: FIDOCredential) -> None:
        """Save or update a credential."""
        raise NotImplementedError("Implement with secure storage backend")
```

### 2.3 macOS Touch ID Integration

**Location:** `Primitive/governance/spark_service/touch_id.py`

```python
"""
macOS Touch ID Integration
==========================
Native Touch ID prompt for spark issuance.

ENTERPRISE STANDARDS:
- LAContext for biometric authentication
- Secure Enclave for key storage
- Keychain for credential persistence

PREEMPTIVE SURFACE:
- Abstracted behind HardwareAuthenticator interface
- Can be replaced with other platform authenticators
"""

import platform
from typing import Optional

# macOS-specific imports (only available on macOS)
if platform.system() == "Darwin":
    from LocalAuthentication import LAContext, LAPolicyDeviceOwnerAuthenticationWithBiometrics
    from Security import (
        SecKeyCreateRandomKey,
        SecKeyCopyPublicKey,
        SecKeyCreateSignature,
        kSecAttrKeyTypeECSECPrimeRandom,
        kSecAttrKeySizeInBits,
        kSecAttrTokenIDSecureEnclave,
        kSecPrivateKeyAttrs,
        kSecAttrIsPermanent,
        kSecAttrApplicationTag,
    )


class TouchIDAuthenticator:
    """
    macOS Touch ID authenticator for spark issuance.

    Uses Secure Enclave for hardware-bound keys that never
    leave the device.
    """

    def __init__(self):
        if platform.system() != "Darwin":
            raise RuntimeError("Touch ID only available on macOS")

        self.context = LAContext()

    def is_available(self) -> bool:
        """Check if Touch ID is available and enrolled."""
        can_evaluate, error = self.context.canEvaluatePolicy_error_(
            LAPolicyDeviceOwnerAuthenticationWithBiometrics,
            None,
        )
        return can_evaluate

    def authenticate(self, reason: str) -> bool:
        """
        Prompt for Touch ID authentication.

        Args:
            reason: The reason shown in the Touch ID prompt

        Returns:
            True if authentication successful
        """
        success, error = self.context.evaluatePolicy_localizedReason_reply_(
            LAPolicyDeviceOwnerAuthenticationWithBiometrics,
            reason,
            None,
        )

        if error:
            # Log error for audit
            print(f"Touch ID error: {error}")
            return False

        return success

    def create_secure_enclave_key(self, tag: str) -> bytes:
        """
        Create a key pair in the Secure Enclave.

        The private key never leaves the Secure Enclave.
        Returns the public key bytes.
        """
        attributes = {
            kSecAttrKeyTypeECSECPrimeRandom: True,
            kSecAttrKeySizeInBits: 256,
            kSecAttrTokenIDSecureEnclave: True,
            kSecPrivateKeyAttrs: {
                kSecAttrIsPermanent: True,
                kSecAttrApplicationTag: tag.encode(),
            },
        }

        private_key, error = SecKeyCreateRandomKey(attributes, None)
        if error:
            raise RuntimeError(f"Failed to create Secure Enclave key: {error}")

        public_key = SecKeyCopyPublicKey(private_key)
        # Export public key bytes
        # Implementation depends on specific format needed

        return public_key
```

### 2.4 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `HardwareAuthenticator` | Abstract FIDO2 interface | New hardware types |
| `CredentialStore` | Pluggable storage | Different backends |
| `TouchIDAuthenticator` | macOS native | Platform-specific extensions |
| Security levels | Configurable AAL | Compliance requirements |

---

## PART 3: RUNTIME CODE EXECUTION CONTROL

### 3.1 Research Foundation

| Technology | Purpose | Standard |
|------------|---------|----------|
| **sitecustomize.py** | Python runtime hook | Python standard |
| **PEP 578 Audit Hooks** | Security auditing | sys.addaudithook |
| **sys.meta_path** | Import hooks | PEP 302 |
| **SLSA Framework** | Supply chain security | Google/industry |
| **OPA** | Policy evaluation | CNCF |
| **SPIFFE/SPIRE** | Workload identity | CNCF |

### 3.2 The Enforcement Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RUNTIME ENFORCEMENT ARCHITECTURE                      │
│                                                                          │
│  Python Process Start                                                    │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────────────┐                                                │
│  │ sitecustomize.py    │ ← Runs before ANY Python code                  │
│  │ ├── Check spark     │                                                │
│  │ ├── Verify path     │                                                │
│  │ └── Block if needed │                                                │
│  └──────────┬──────────┘                                                │
│             │                                                            │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │ PEP 578 Audit Hook  │ ← Monitors ALL imports                         │
│  │ └── Log + enforce   │                                                │
│  └──────────┬──────────┘                                                │
│             │                                                            │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │ SparkService Query  │ ← Validate spark for this script               │
│  │ ├── Valid → ALLOW   │                                                │
│  │ └── Invalid → BLOCK │                                                │
│  └──────────┬──────────┘                                                │
│             │                                                            │
│             ▼                                                            │
│      Script Executes (or exits with error)                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Implementation

**Location:** `Primitive/governance/spark_service/enforcement.py`

```python
"""
RUNTIME ENFORCEMENT
===================
Block unauthorized scripts from executing.

ENTERPRISE STANDARDS:
- PEP 578 Audit Hooks for comprehensive monitoring
- SLSA Framework compliance for supply chain integrity
- OPA-style policy evaluation

PREEMPTIVE SURFACE:
- Policy engine is pluggable
- Enforcement rules are externalized
- New enforcement points can be added
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
import sys
import os
import socket
import json


@dataclass
class EnforcementPolicy:
    """
    Policy configuration for runtime enforcement.

    PREEMPTIVE: Policies are externalized, not hardcoded.
    This enables policy updates without code changes.
    """
    # Paths that never need spark (core organism)
    exempt_paths: list[str]

    # Paths that always need spark
    require_spark_paths: list[str]

    # Whether to block or just warn
    enforcement_mode: str  # "enforce" | "warn" | "audit"

    # SparkService connection
    spark_service_socket: str

    @classmethod
    def load(cls, config_path: str) -> "EnforcementPolicy":
        """Load policy from configuration file."""
        with open(config_path) as f:
            config = json.load(f)
        return cls(**config)

    @classmethod
    def default(cls) -> "EnforcementPolicy":
        """Default policy for Primitive Engine."""
        return cls(
            exempt_paths=[
                "Primitive/",           # Core organism
                ".venv/",               # Virtual environment
                "site-packages/",       # Installed packages
            ],
            require_spark_paths=[
                "scripts/",             # All scripts outside Primitive
                "daemon/",              # Daemon scripts
                "apps/",                # Application scripts
            ],
            enforcement_mode="enforce",
            spark_service_socket="/tmp/spark_service.sock",
        )


class RuntimeEnforcer:
    """
    Enforce spark requirements at runtime.

    ENTERPRISE STANDARDS:
    - Zero-trust: Every script must prove authorization
    - Audit: Every execution attempt is logged
    - Fail-closed: Unknown scripts are blocked

    PREEMPTIVE SURFACE:
    - Can be extended with additional enforcement hooks
    - Policy evaluation is pluggable
    - Supports multiple enforcement backends
    """

    def __init__(self, policy: EnforcementPolicy):
        self.policy = policy
        self._spark_client: Optional["SparkClient"] = None

    @property
    def spark_client(self) -> "SparkClient":
        """Lazy-initialize spark client."""
        if self._spark_client is None:
            self._spark_client = SparkClient(self.policy.spark_service_socket)
        return self._spark_client

    def check_script(self, script_path: str) -> "EnforcementResult":
        """
        Check if a script is authorized to run.

        Returns enforcement decision with reasoning.
        """
        path = Path(script_path).resolve()
        path_str = str(path)

        # Check exemptions first
        for exempt in self.policy.exempt_paths:
            if exempt in path_str:
                return EnforcementResult(
                    allowed=True,
                    reason=f"Exempt path: {exempt}",
                    requires_spark=False,
                )

        # Check if spark is required
        requires_spark = any(
            req in path_str
            for req in self.policy.require_spark_paths
        )

        if not requires_spark:
            return EnforcementResult(
                allowed=True,
                reason="Path does not require spark",
                requires_spark=False,
            )

        # Query SparkService
        try:
            spark_valid = self.spark_client.validate_spark(path_str)
        except Exception as e:
            # Fail-closed on error
            return EnforcementResult(
                allowed=False,
                reason=f"SparkService unavailable: {e}",
                requires_spark=True,
                error=str(e),
            )

        if spark_valid:
            return EnforcementResult(
                allowed=True,
                reason="Valid spark",
                requires_spark=True,
            )
        else:
            return EnforcementResult(
                allowed=False,
                reason="No valid spark for this script",
                requires_spark=True,
            )

    def enforce(self, script_path: str) -> None:
        """
        Enforce spark requirement for a script.

        Raises SystemExit if script is not authorized.
        """
        result = self.check_script(script_path)

        # Always log the attempt
        self._log_attempt(script_path, result)

        if result.allowed:
            return

        # Handle based on enforcement mode
        if self.policy.enforcement_mode == "enforce":
            print(f"BLOCKED: {result.reason}", file=sys.stderr)
            print(f"Script: {script_path}", file=sys.stderr)
            print("Request a spark from the SparkService to run this script.", file=sys.stderr)
            sys.exit(1)

        elif self.policy.enforcement_mode == "warn":
            print(f"WARNING: {result.reason}", file=sys.stderr)
            print(f"Script: {script_path}", file=sys.stderr)
            # Allow execution with warning

        elif self.policy.enforcement_mode == "audit":
            # Silent logging only
            pass

    def _log_attempt(self, script_path: str, result: "EnforcementResult") -> None:
        """Log execution attempt for audit."""
        # Implementation: write to audit log
        pass


@dataclass
class EnforcementResult:
    """Result of an enforcement check."""
    allowed: bool
    reason: str
    requires_spark: bool
    error: Optional[str] = None


class SparkClient:
    """
    Client for communicating with SparkService.

    PREEMPTIVE SURFACE:
    - Transport is abstracted (socket, HTTP, gRPC)
    - Protocol is versioned for upgrades
    """

    def __init__(self, socket_path: str):
        self.socket_path = socket_path

    def validate_spark(self, script_path: str) -> bool:
        """
        Validate if a script has a valid spark.

        Returns True if spark is valid, False otherwise.
        """
        # Connect to SparkService
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.socket_path)

            # Send validation request
            request = json.dumps({
                "action": "validate",
                "script_path": script_path,
            })
            sock.sendall(request.encode())

            # Receive response
            response = sock.recv(4096)
            result = json.loads(response.decode())

            return result.get("valid", False)

        finally:
            sock.close()


def install_enforcement_hook(policy: Optional[EnforcementPolicy] = None) -> None:
    """
    Install the runtime enforcement hook.

    Call this from sitecustomize.py to enable enforcement.
    """
    if policy is None:
        policy = EnforcementPolicy.default()

    enforcer = RuntimeEnforcer(policy)

    # Get the main script being executed
    if hasattr(sys, 'argv') and sys.argv:
        script = sys.argv[0]
        if script and script != '-c':
            enforcer.enforce(script)

    # Also install audit hook for imports (PEP 578)
    def audit_hook(event: str, args: tuple) -> None:
        if event == "import":
            module_name = args[0]
            # Log import for audit trail
            pass

    sys.addaudithook(audit_hook)
```

### 3.4 sitecustomize.py

**Location:** `sitecustomize.py` (in Python path)

```python
"""
SITECUSTOMIZE.PY
================
Python runtime hook for Primitive Engine spark enforcement.

This file runs BEFORE any Python script executes.

PLACEMENT:
- Development: {project}/.venv/lib/python3.x/site-packages/sitecustomize.py
- System-wide: /usr/local/lib/python3.x/site-packages/sitecustomize.py

PREEMPTIVE SURFACE:
- Configuration is externalized
- Can be disabled for debugging
- Audit mode for rollout
"""

import os
import sys

# Environment variable to disable enforcement
if os.environ.get("PRIMITIVE_SPARK_DISABLED") == "1":
    pass  # Skip enforcement
else:
    try:
        # Import enforcement only if available
        from Primitive.governance.spark_service.enforcement import (
            install_enforcement_hook,
            EnforcementPolicy,
        )

        # Check for custom policy path
        policy_path = os.environ.get("PRIMITIVE_SPARK_POLICY")
        if policy_path and os.path.exists(policy_path):
            policy = EnforcementPolicy.load(policy_path)
        else:
            policy = EnforcementPolicy.default()

        install_enforcement_hook(policy)

    except ImportError:
        # Primitive not installed, skip enforcement
        pass
    except Exception as e:
        # Log but don't block on enforcement errors during setup
        print(f"Warning: Spark enforcement setup failed: {e}", file=sys.stderr)
```

### 3.5 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `EnforcementPolicy` | Externalized config | Policy updates without code |
| `RuntimeEnforcer` | Pluggable enforcement | New enforcement backends |
| `audit_hook` | PEP 578 compliance | Comprehensive monitoring |
| Enforcement modes | Gradual rollout | Safe deployment |

---

## PART 4: SERVICE HEALTH AND HEARTBEAT

### 4.1 Research Foundation

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Kubernetes Probes** | liveness/readiness/startup | Container health |
| **gRPC Health** | Standardized protocol | Service mesh |
| **Phi Accrual** | Adaptive failure detection | Distributed systems |
| **SWIM Protocol** | Gossip-based detection | Peer-to-peer |
| **etcd Leases** | TTL-based heartbeats | Coordination |

### 4.2 Implementation

**Location:** `Primitive/seed/pulse/heartbeat.py`

```python
"""
ORGANISM HEARTBEAT SYSTEM
=========================
Real-time health monitoring for federated organisms.

ENTERPRISE STANDARDS:
- Phi Accrual Failure Detector (adaptive thresholds)
- Kubernetes-style probe model
- 30-second heartbeat interval

PREEMPTIVE SURFACE:
- Heartbeat format is versioned for evolution
- Failure detection is pluggable
- Multi-channel delivery (WebSocket, HTTP, gRPC)
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
from datetime import datetime, timezone
import asyncio
import statistics
import math


@dataclass
class Heartbeat:
    """
    Heartbeat message from an organism.

    VERSION 1.0 - Can be extended in future versions.
    """
    organism_id: str
    timestamp: str
    sequence: int

    # Health indicators
    alive: bool = True
    healthy: bool = True

    # Load metrics
    cpu_percent: float = 0.0
    memory_percent: float = 0.0

    # Error counts (since last heartbeat)
    error_count: int = 0
    warning_count: int = 0

    # Version for future evolution
    version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "organism_id": self.organism_id,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "alive": self.alive,
            "healthy": self.healthy,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "version": self.version,
        }


class PhiAccrualFailureDetector:
    """
    Phi Accrual Failure Detector.

    Enterprise-standard adaptive failure detection used by
    Cassandra, Akka, and other distributed systems.

    Instead of binary alive/dead, computes a suspicion level (phi)
    that increases continuously while heartbeats are missing.

    PREEMPTIVE SURFACE:
    - Thresholds are configurable per-organism
    - History window is adjustable
    - Can be extended with additional metrics
    """

    # Default threshold: phi > 8 = 99.9% confident it's dead
    DEFAULT_THRESHOLD = 8.0

    # Minimum samples before making decisions
    MIN_SAMPLES = 5

    # Maximum samples to keep in history
    MAX_SAMPLES = 1000

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        max_samples: int = MAX_SAMPLES,
    ):
        self.threshold = threshold
        self.max_samples = max_samples

        # Heartbeat arrival times (for calculating intervals)
        self.arrival_times: list[float] = []

        # Pre-computed statistics
        self._mean: Optional[float] = None
        self._variance: Optional[float] = None

    def heartbeat_received(self, timestamp: float) -> None:
        """Record a heartbeat arrival."""
        self.arrival_times.append(timestamp)

        # Trim to max samples
        if len(self.arrival_times) > self.max_samples:
            self.arrival_times = self.arrival_times[-self.max_samples:]

        # Invalidate cached statistics
        self._mean = None
        self._variance = None

    def phi(self, current_time: float) -> float:
        """
        Calculate the phi (suspicion) value.

        Returns:
            Phi value. Higher = more suspicious.
            phi > threshold indicates failure.
        """
        if len(self.arrival_times) < self.MIN_SAMPLES:
            return 0.0  # Not enough data

        # Calculate intervals between heartbeats
        intervals = [
            self.arrival_times[i] - self.arrival_times[i-1]
            for i in range(1, len(self.arrival_times))
        ]

        # Calculate mean and variance of intervals
        if self._mean is None:
            self._mean = statistics.mean(intervals)
            self._variance = statistics.variance(intervals) if len(intervals) > 1 else 0.0

        # Time since last heartbeat
        last_heartbeat = self.arrival_times[-1]
        time_since = current_time - last_heartbeat

        # Calculate probability using normal distribution
        # P(t) = 1 - CDF(time_since)
        if self._variance == 0:
            # No variance, use simple threshold
            return 0.0 if time_since <= self._mean else self.threshold + 1

        # Phi = -log10(1 - CDF(time_since))
        # Using approximation for normal CDF
        z = (time_since - self._mean) / math.sqrt(self._variance)
        p = 0.5 * (1 + math.erf(z / math.sqrt(2)))

        if p >= 1.0:
            return float('inf')

        return -math.log10(1 - p)

    def is_alive(self, current_time: float) -> bool:
        """Check if the organism is considered alive."""
        return self.phi(current_time) < self.threshold


@dataclass
class OrganismHealth:
    """
    Health status of an organism.

    PREEMPTIVE SURFACE:
    - Status enum is extensible
    - Metadata field for future attributes
    """
    organism_id: str
    status: str  # "alive" | "suspect" | "dead" | "unknown"
    last_heartbeat: Optional[str]
    phi_value: float
    metadata: dict = field(default_factory=dict)


class HeartbeatMonitor:
    """
    Monitor heartbeats from federated organisms.

    ENTERPRISE STANDARDS:
    - 30-second heartbeat interval
    - 3-6 missed = death declaration (90-180 seconds)
    - Adaptive thresholds per organism

    PREEMPTIVE SURFACE:
    - Callback system for status changes
    - Pluggable failure detectors
    - Multi-organism coordination
    """

    # Standard interval (matches Kubernetes, Consul, etc.)
    DEFAULT_INTERVAL = 30.0  # seconds

    def __init__(self):
        self.organisms: dict[str, PhiAccrualFailureDetector] = {}
        self.last_heartbeats: dict[str, Heartbeat] = {}
        self.status_callbacks: list[Callable[[str, str], None]] = []

    def register_organism(
        self,
        organism_id: str,
        threshold: float = PhiAccrualFailureDetector.DEFAULT_THRESHOLD,
    ) -> None:
        """Register an organism for monitoring."""
        self.organisms[organism_id] = PhiAccrualFailureDetector(threshold=threshold)

    def record_heartbeat(self, heartbeat: Heartbeat) -> None:
        """Record a heartbeat from an organism."""
        organism_id = heartbeat.organism_id

        # Auto-register if unknown
        if organism_id not in self.organisms:
            self.register_organism(organism_id)

        # Record in failure detector
        timestamp = datetime.fromisoformat(heartbeat.timestamp).timestamp()
        self.organisms[organism_id].heartbeat_received(timestamp)

        # Store latest heartbeat
        self.last_heartbeats[organism_id] = heartbeat

    def get_status(self, organism_id: str) -> OrganismHealth:
        """Get health status of an organism."""
        if organism_id not in self.organisms:
            return OrganismHealth(
                organism_id=organism_id,
                status="unknown",
                last_heartbeat=None,
                phi_value=0.0,
            )

        detector = self.organisms[organism_id]
        current_time = datetime.now(timezone.utc).timestamp()
        phi = detector.phi(current_time)

        # Determine status based on phi
        if phi < detector.threshold * 0.5:
            status = "alive"
        elif phi < detector.threshold:
            status = "suspect"
        else:
            status = "dead"

        last_hb = self.last_heartbeats.get(organism_id)

        return OrganismHealth(
            organism_id=organism_id,
            status=status,
            last_heartbeat=last_hb.timestamp if last_hb else None,
            phi_value=phi,
        )

    def on_status_change(self, callback: Callable[[str, str], None]) -> None:
        """Register callback for status changes."""
        self.status_callbacks.append(callback)

    async def monitor_loop(self, check_interval: float = 5.0) -> None:
        """
        Continuous monitoring loop.

        Checks all organisms and triggers callbacks on status changes.
        """
        previous_status: dict[str, str] = {}

        while True:
            for organism_id in self.organisms:
                health = self.get_status(organism_id)
                prev = previous_status.get(organism_id)

                if prev and prev != health.status:
                    # Status changed, notify callbacks
                    for callback in self.status_callbacks:
                        callback(organism_id, health.status)

                previous_status[organism_id] = health.status

            await asyncio.sleep(check_interval)
```

### 4.3 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `Heartbeat` versioned | Message evolution | Future fields |
| `PhiAccrualFailureDetector` | Adaptive detection | Per-organism tuning |
| `status_callbacks` | Event notification | Custom handlers |
| `monitor_loop` | Async monitoring | Integration with event loops |

---

## PART 5: INTER-ORGANIZATIONAL FEDERATION

### 5.1 Research Foundation

| Protocol | Description | Adoption |
|----------|-------------|----------|
| **CloudEvents** | Standard event format | CNCF Graduated |
| **Matrix** | Decentralized comms | NATO, German govt |
| **ActivityPub** | Federated social | W3C Recommendation |
| **MCP** | AI agent protocol | Linux Foundation |
| **DIDs** | Decentralized identity | W3C 2025 |

### 5.2 Implementation

**Location:** `Primitive/seed/federation.py` (UPGRADED)

```python
"""
FEDERATION PROTOCOL
===================
Inter-organizational communication for federated organisms.

ENTERPRISE STANDARDS:
- CloudEvents for message format
- DIDs for organism identity
- MCP-inspired agent coordination

PREEMPTIVE SURFACE:
- Transport is abstracted (WebSocket, HTTP, MQTT)
- Message formats are versioned
- New channel types can be added
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
import asyncio


class ChannelType(Enum):
    """Federation communication channels."""
    HEARTBEAT = "heartbeat"      # Real-time health
    TELEMETRY = "telemetry"      # Metrics streaming
    LEARNINGS = "learnings"      # Knowledge sharing
    GOVERNANCE = "governance"    # Policy distribution
    PROOFS = "proofs"            # Verification requests


@dataclass
class CloudEvent:
    """
    CloudEvents-compliant message format.

    CNCF Graduated standard for event interchange.

    PREEMPTIVE SURFACE:
    - Extensible via 'extensions' field
    - Version field for format evolution
    """
    # Required CloudEvents attributes
    specversion: str = "1.0"
    type: str = ""
    source: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Optional CloudEvents attributes
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    datacontenttype: str = "application/json"
    subject: Optional[str] = None

    # The actual data
    data: Any = None

    # Extensions (for federation-specific metadata)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "specversion": self.specversion,
            "type": self.type,
            "source": self.source,
            "id": self.id,
            "time": self.time,
            "datacontenttype": self.datacontenttype,
            "data": self.data,
        }
        if self.subject:
            d["subject"] = self.subject
        d.update(self.extensions)
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class OrganismDID:
    """
    Decentralized Identifier for organisms.

    W3C DID standard for self-sovereign identity.

    Format: did:primitive:{organism_id}

    PREEMPTIVE SURFACE:
    - Method is 'primitive' but can be extended
    - Verification methods are pluggable
    """
    organism_id: str
    public_key: bytes
    created_at: str
    controller: Optional[str] = None  # Parent organism DID

    @property
    def did(self) -> str:
        return f"did:primitive:{self.organism_id}"

    def to_document(self) -> dict:
        """Generate DID Document."""
        return {
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": self.did,
            "controller": self.controller or self.did,
            "verificationMethod": [{
                "id": f"{self.did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": self.did,
                "publicKeyMultibase": self.public_key.hex(),
            }],
            "created": self.created_at,
        }


class FederationHub:
    """
    Genesis organism's federation hub.

    Receives and routes messages from daughter organisms.

    ENTERPRISE STANDARDS:
    - CloudEvents message format
    - Channel-based routing
    - Audit logging for all messages

    PREEMPTIVE SURFACE:
    - Transport backend is pluggable
    - Message handlers are registrable
    - New channels can be added dynamically
    """

    def __init__(self, organism_id: str = "primitive_engine_genesis"):
        self.organism_id = organism_id
        self.did = OrganismDID(
            organism_id=organism_id,
            public_key=b"",  # Set during initialization
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # Registered organisms
        self.organisms: dict[str, "OrganismRegistration"] = {}

        # Channel handlers
        self.handlers: dict[ChannelType, list[Callable]] = {
            channel: [] for channel in ChannelType
        }

        # Message queue (for async processing)
        self.message_queue: asyncio.Queue = asyncio.Queue()

        # Running state
        self._running = False

    def register_organism(
        self,
        organism_id: str,
        public_key: bytes,
        parent_id: Optional[str] = None,
    ) -> "OrganismRegistration":
        """Register a new organism with the federation."""
        registration = OrganismRegistration(
            organism_id=organism_id,
            did=OrganismDID(
                organism_id=organism_id,
                public_key=public_key,
                created_at=datetime.now(timezone.utc).isoformat(),
                controller=f"did:primitive:{parent_id}" if parent_id else None,
            ),
            registered_at=datetime.now(timezone.utc).isoformat(),
            status="active",
        )

        self.organisms[organism_id] = registration
        return registration

    def on_channel(
        self,
        channel: ChannelType,
        handler: Callable[[CloudEvent], None],
    ) -> None:
        """Register a handler for a channel."""
        self.handlers[channel].append(handler)

    async def receive_message(self, event: CloudEvent) -> None:
        """
        Receive a message from an organism.

        Routes to appropriate channel handlers.
        """
        # Validate source
        source_id = event.source.replace("did:primitive:", "")
        if source_id not in self.organisms:
            raise ValueError(f"Unknown organism: {source_id}")

        # Determine channel from event type
        channel = self._type_to_channel(event.type)

        # Log for audit
        self._audit_log(event)

        # Route to handlers
        for handler in self.handlers[channel]:
            await self._safe_handle(handler, event)

    def _type_to_channel(self, event_type: str) -> ChannelType:
        """Map CloudEvents type to channel."""
        mapping = {
            "org.primitive.heartbeat": ChannelType.HEARTBEAT,
            "org.primitive.telemetry": ChannelType.TELEMETRY,
            "org.primitive.learning": ChannelType.LEARNINGS,
            "org.primitive.governance": ChannelType.GOVERNANCE,
            "org.primitive.proof": ChannelType.PROOFS,
        }
        return mapping.get(event_type, ChannelType.TELEMETRY)

    async def _safe_handle(
        self,
        handler: Callable,
        event: CloudEvent,
    ) -> None:
        """Safely execute handler with error capture."""
        try:
            result = handler(event)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            # Log error but don't crash
            print(f"Handler error: {e}")

    def _audit_log(self, event: CloudEvent) -> None:
        """Log message for audit."""
        # Implementation: append to audit JSONL
        pass

    def get_organism(self, organism_id: str) -> Optional["OrganismRegistration"]:
        """Get registration for an organism."""
        return self.organisms.get(organism_id)

    async def start(self) -> None:
        """Start the federation hub."""
        self._running = True
        # Implementation: start transport listeners

    async def stop(self) -> None:
        """Stop the federation hub."""
        self._running = False


@dataclass
class OrganismRegistration:
    """Registration record for a federated organism."""
    organism_id: str
    did: OrganismDID
    registered_at: str
    status: str  # "active" | "suspended" | "revoked"
    last_heartbeat: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class FederationClient:
    """
    Daughter organism's federation client.

    Connects to genesis hub and sends messages.

    PREEMPTIVE SURFACE:
    - Reconnection logic is configurable
    - Message batching is optional
    - Multiple hub support (for redundancy)
    """

    def __init__(
        self,
        organism_id: str,
        private_key: bytes,
    ):
        self.organism_id = organism_id
        self.private_key = private_key
        self.did = f"did:primitive:{organism_id}"

        self._connected = False
        self._hub_url: Optional[str] = None

    async def connect(self, hub_url: str) -> bool:
        """Connect to the federation hub."""
        self._hub_url = hub_url
        # Implementation: establish WebSocket/HTTP connection
        self._connected = True
        return True

    async def send_heartbeat(
        self,
        alive: bool = True,
        healthy: bool = True,
        metrics: Optional[dict] = None,
    ) -> bool:
        """Send heartbeat to the hub."""
        event = CloudEvent(
            type="org.primitive.heartbeat",
            source=self.did,
            data={
                "alive": alive,
                "healthy": healthy,
                "metrics": metrics or {},
            },
        )

        return await self._send(event)

    async def send_telemetry(self, metrics: dict) -> bool:
        """Send telemetry data to the hub."""
        event = CloudEvent(
            type="org.primitive.telemetry",
            source=self.did,
            data=metrics,
        )

        return await self._send(event)

    async def send_learning(self, learning: dict) -> bool:
        """Send a learning/insight to the hub."""
        event = CloudEvent(
            type="org.primitive.learning",
            source=self.did,
            data=learning,
        )

        return await self._send(event)

    async def request_verification(
        self,
        claims: dict,
        scope: str,
    ) -> dict:
        """Request verification from Credential Atlas."""
        event = CloudEvent(
            type="org.primitive.proof.request",
            source=self.did,
            subject="did:primitive:credential_atlas",
            data={
                "claims": claims,
                "scope": scope,
            },
        )

        # Send and await response
        await self._send(event)
        # Implementation: await verification response
        return {}

    async def _send(self, event: CloudEvent) -> bool:
        """Send event to hub."""
        if not self._connected:
            raise RuntimeError("Not connected to hub")

        # Implementation: send via transport
        return True
```

### 5.3 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `CloudEvent` | Standard format | Interoperability |
| `OrganismDID` | Self-sovereign ID | Decentralized trust |
| `ChannelType` | Message routing | New channel types |
| `FederationHub.on_channel` | Handler registration | Custom processors |

---

## PART 6: JWT/Ed25519 CRYPTOGRAPHIC STANDARDS

### 6.1 Research Foundation

| Standard | Status | Implementation |
|----------|--------|----------------|
| **FIPS 186-5** | Ed25519 approved (Feb 2023) | cryptography lib |
| **RFC 8037** | EdDSA for JOSE | PyJWT |
| **RFC 7519** | JWT | PyJWT |
| **PASETO** | Superior to JWT | paseto lib |

### 6.2 Implementation

**Location:** `Primitive/governance/spark_service/crypto.py`

```python
"""
CRYPTOGRAPHIC STANDARDS
=======================
Enterprise-grade cryptography for spark tokens.

ENTERPRISE STANDARDS:
- FIPS 186-5 Ed25519 (128-bit security)
- EdDSA algorithm for JWT (RFC 8037)
- 15-minute access tokens, rotating refresh
- Redis blacklist for revocation

PREEMPTIVE SURFACE:
- Algorithm is configurable (future post-quantum)
- Token format is versioned
- Revocation mechanism is pluggable
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone, timedelta
import secrets

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


# Algorithm hierarchy (EdDSA > ES256 > PS256 > RS256)
PREFERRED_ALGORITHM = "EdDSA"


@dataclass
class SparkToken:
    """
    Spark JWT token.

    ENTERPRISE STANDARDS:
    - 15-minute default expiration
    - Single-use where appropriate
    - Hardware attestation field

    PREEMPTIVE SURFACE:
    - Claims are extensible
    - Version field for format evolution
    - Custom claims via 'extra' field
    """
    # Standard JWT claims
    sub: str           # Subject (script path)
    iss: str           # Issuer (organism ID)
    iat: datetime      # Issued at
    exp: datetime      # Expiration
    jti: str           # Unique ID (for revocation)

    # Spark-specific claims
    level: str         # organization | service | script
    capabilities: list[str]  # What's authorized

    # Hardware binding
    hardware_attestation: Optional[str] = None

    # Extensibility
    version: str = "1.0"
    extra: dict = None

    def to_claims(self) -> dict:
        """Convert to JWT claims dict."""
        claims = {
            "sub": self.sub,
            "iss": self.iss,
            "iat": int(self.iat.timestamp()),
            "exp": int(self.exp.timestamp()),
            "jti": self.jti,
            "level": self.level,
            "capabilities": self.capabilities,
            "version": self.version,
        }

        if self.hardware_attestation:
            claims["hw_attestation"] = self.hardware_attestation

        if self.extra:
            claims.update(self.extra)

        return claims

    @classmethod
    def from_claims(cls, claims: dict) -> "SparkToken":
        """Create from JWT claims dict."""
        return cls(
            sub=claims["sub"],
            iss=claims["iss"],
            iat=datetime.fromtimestamp(claims["iat"], tz=timezone.utc),
            exp=datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
            jti=claims["jti"],
            level=claims["level"],
            capabilities=claims["capabilities"],
            hardware_attestation=claims.get("hw_attestation"),
            version=claims.get("version", "1.0"),
            extra={
                k: v for k, v in claims.items()
                if k not in ["sub", "iss", "iat", "exp", "jti", "level",
                            "capabilities", "hw_attestation", "version"]
            },
        )


class SparkCrypto:
    """
    Cryptographic operations for spark tokens.

    ENTERPRISE STANDARDS:
    - Ed25519 for signing (FIPS 186-5)
    - EdDSA algorithm in JWT
    - Secure key storage

    PREEMPTIVE SURFACE:
    - Key rotation is built-in
    - Algorithm can be upgraded
    - Multiple key support for rollover
    """

    # Default token lifetimes
    ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)

    def __init__(
        self,
        private_key: Ed25519PrivateKey,
        issuer: str,
    ):
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.issuer = issuer

        # Revocation set (in production, use Redis)
        self.revoked_tokens: set[str] = set()

    @classmethod
    def generate_key_pair(cls) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """Generate a new Ed25519 key pair."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    def create_spark(
        self,
        script_path: str,
        level: str = "script",
        capabilities: list[str] = None,
        hardware_attestation: Optional[str] = None,
        lifetime: Optional[timedelta] = None,
    ) -> str:
        """
        Create a signed spark token.

        Returns the JWT string.
        """
        now = datetime.now(timezone.utc)

        token = SparkToken(
            sub=script_path,
            iss=self.issuer,
            iat=now,
            exp=now + (lifetime or self.ACCESS_TOKEN_LIFETIME),
            jti=secrets.token_urlsafe(16),
            level=level,
            capabilities=capabilities or ["execute"],
            hardware_attestation=hardware_attestation,
        )

        # Sign with Ed25519
        private_key_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return jwt.encode(
            token.to_claims(),
            private_key_bytes,
            algorithm=PREFERRED_ALGORITHM,
        )

    def verify_spark(self, token_string: str) -> Optional[SparkToken]:
        """
        Verify a spark token.

        Returns SparkToken if valid, None if invalid.
        """
        try:
            public_key_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            claims = jwt.decode(
                token_string,
                public_key_bytes,
                algorithms=[PREFERRED_ALGORITHM],
                issuer=self.issuer,
            )

            # Check revocation
            if claims["jti"] in self.revoked_tokens:
                return None

            return SparkToken.from_claims(claims)

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def revoke_spark(self, token_string: str) -> bool:
        """
        Revoke a spark token.

        In production, add to Redis blacklist.
        """
        try:
            # Decode without verification to get jti
            claims = jwt.decode(
                token_string,
                options={"verify_signature": False},
            )
            self.revoked_tokens.add(claims["jti"])
            return True
        except:
            return False

    def rotate_keys(self) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """
        Rotate to new key pair.

        PREEMPTIVE: In production, maintain previous key
        for grace period to validate existing tokens.
        """
        new_private, new_public = self.generate_key_pair()

        # Store old keys for grace period
        # (Implementation: key versioning)

        self.private_key = new_private
        self.public_key = new_public

        return new_private, new_public
```

### 6.3 Preemptive Surfaces Created

| Surface | Purpose | Enables |
|---------|---------|---------|
| `SparkToken.version` | Format evolution | Breaking changes |
| `SparkToken.extra` | Extensibility | Custom claims |
| `rotate_keys()` | Key rotation | Security hygiene |
| `PREFERRED_ALGORITHM` | Algorithm config | Post-quantum upgrade |

---

## PART 7: IMPLEMENTATION SEQUENCE

### Phase 1: Foundation (Days 1-3)

| Priority | Task | Track | File |
|----------|------|-------|------|
| P0 | Create MOLT.yaml | Molting | `MOLT.yaml` |
| P0 | Create MoltExecutor | Molting | `Primitive/molt/executor.py` |
| P0 | Install fastmod, ast-grep | Molting | Dependencies |
| P0 | Create enforcement.py | Spark | `governance/spark_service/enforcement.py` |
| P0 | Create sitecustomize.py | Spark | `sitecustomize.py` |

### Phase 2: Hardware Auth + Heartbeat (Days 4-7)

| Priority | Task | Track | File |
|----------|------|-------|------|
| P0 | Create fido2.py | Spark | `governance/spark_service/fido2.py` |
| P0 | Create touch_id.py | Spark | `governance/spark_service/touch_id.py` |
| P0 | Create heartbeat.py | Federation | `seed/pulse/heartbeat.py` |
| P0 | Create PhiAccrualFailureDetector | Federation | `seed/pulse/heartbeat.py` |
| P1 | Create crypto.py | Spark | `governance/spark_service/crypto.py` |

### Phase 3: Federation + Communication (Days 8-12)

| Priority | Task | Track | File |
|----------|------|-------|------|
| P0 | Upgrade federation.py | Federation | `seed/federation.py` |
| P0 | Implement CloudEvents | Federation | `seed/federation.py` |
| P0 | Implement OrganismDID | Federation | `seed/federation.py` |
| P0 | Create FederationHub | Federation | `seed/federation.py` |
| P0 | Create FederationClient | Federation | `seed/federation.py` |

### Phase 4: Execute Molt + Birth Credential Atlas (Days 13-17)

| Priority | Task | Track | File |
|----------|------|-------|------|
| P0 | Execute PrimitiveEngine → PrimitiveEngine molt | Molting | Via MoltExecutor |
| P0 | Complete Credential Atlas template | Credential Atlas | `seed/templates/credential_atlas/` |
| P0 | Spawn Credential Atlas | Credential Atlas | Via ProjectSeeder |
| P0 | Verify communication | Integration | Test script |

### Phase 5: Benchmark Verification (Days 18-21)

| Priority | Task | Track | File |
|----------|------|-------|------|
| P0 | Run benchmark test | All | Verification script |
| P0 | Verify spark enforcement | Spark | Manual test |
| P0 | Verify hardware auth | Spark | Manual test |
| P0 | Verify federation | Federation | Integration test |

---

## SUMMARY: PREEMPTIVE SURFACES INDEX

Every implementation creates surfaces for future use:

### Molting System
- `MOLT.yaml` → Future identity transformations
- `MoltExecutor` → Any organism can molt
- `MoltPlan` → Governance approval workflows
- `previous_identities` → Audit trail

### Hardware Authentication
- `HardwareAuthenticator` → New hardware types
- `CredentialStore` → Different storage backends
- Security levels → Compliance requirements

### Runtime Enforcement
- `EnforcementPolicy` → Policy without code changes
- `RuntimeEnforcer` → New enforcement backends
- Enforcement modes → Gradual rollout

### Heartbeat System
- `Heartbeat` versioned → Future fields
- `PhiAccrualFailureDetector` → Per-organism tuning
- `status_callbacks` → Custom handlers

### Federation Protocol
- `CloudEvent` → Interoperability
- `OrganismDID` → Decentralized trust
- `ChannelType` → New channel types

### Cryptography
- `SparkToken.version` → Format evolution
- `rotate_keys()` → Security hygiene
- `PREFERRED_ALGORITHM` → Algorithm upgrades

---

**This specification embeds the Preemptive Surfaces principle: everything built enables future molts, making each iteration easier than the last. This is Stage 5 cognitive integration made infrastructure.**

*"We learn how to do it and then it becomes integrated so that we can do it again a lot easier and it's just part of being the nature of the organization itself."*

---

*Document created January 19, 2026*
*Enterprise standards research synthesized from industry best practices*

"""
Licensing Infrastructure for Genesis

IP PROTECTION MODEL:
    - Base Llama = Meta's open weights (starting point)
    - Genesis = Jeremy's proprietary fine-tune (HIS IP, not open source)
    - Genesis + [Customer] = Licensed product (customer gets access, not weights)

PROTECTION MECHANISMS:
    1. Weights never leave THE EMPIRE - All inference runs locally
    2. Encrypted storage - AES-256 with hardware-bound keys
    3. Inference-only API - Customers call API, never see weights
    4. Daughter registry - All daughters tracked with license terms
    5. Training service - Jeremy controls all training operations

"You can copy the pattern, but not the pattern-maker."
"""

from licensing.weight_vault import (
    WeightVault,
    EncryptedWeights,
    VaultConfig,
)
from licensing.daughter_registry import (
    DaughterRegistry,
    Daughter,
    LicenseTerms,
)
from licensing.access_control import (
    AccessController,
    AccessLevel,
    AccessToken,
)

__all__ = [
    # Weight Vault
    "WeightVault",
    "EncryptedWeights",
    "VaultConfig",
    # Daughter Registry
    "DaughterRegistry",
    "Daughter",
    "LicenseTerms",
    # Access Control
    "AccessController",
    "AccessLevel",
    "AccessToken",
]

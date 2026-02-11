"""
Access Control for Genesis API

TIERED ACCESS MODEL:
    - Free: Inference API only, rate limited
    - Licensed: Inference + daughter training, no weight access
    - Enterprise: Dedicated daughter + continuous learning

KEY PRINCIPLE:
    Weights never leave THE EMPIRE.
    Customers call inference API.
    Jeremy controls all training.

Usage:
    controller = AccessController(config_path="/secure/access_config.json")

    # Check if access allowed
    if controller.check_access(token, AccessLevel.INFERENCE):
        result = model.generate(prompt)

    # Generate access token for customer
    token = controller.create_token(customer_id="...", level=AccessLevel.LICENSED)
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AccessLevel(Enum):
    """Access levels for Genesis."""

    NONE = 0           # No access
    INFERENCE = 1      # Can call inference API
    TRAINING = 2       # Can request daughter training
    ADMIN = 3          # Full access (Jeremy only)


@dataclass
class AccessToken:
    """Represents an access token."""

    token_id: str
    customer_id: str
    access_level: AccessLevel
    created_at: str
    expires_at: str
    is_active: bool = True
    rate_limit: int = 1000  # Requests per day
    request_count: int = 0
    last_request: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "token_id": self.token_id,
            "customer_id": self.customer_id,
            "access_level": self.access_level.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "rate_limit": self.rate_limit,
            "request_count": self.request_count,
            "last_request": self.last_request,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AccessToken":
        """Create from dict."""
        return cls(
            token_id=d["token_id"],
            customer_id=d["customer_id"],
            access_level=AccessLevel(d["access_level"]),
            created_at=d["created_at"],
            expires_at=d["expires_at"],
            is_active=d.get("is_active", True),
            rate_limit=d.get("rate_limit", 1000),
            request_count=d.get("request_count", 0),
            last_request=d.get("last_request"),
            metadata=d.get("metadata"),
        )

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now() > datetime.fromisoformat(self.expires_at)

    def is_rate_limited(self) -> bool:
        """Check if token has exceeded rate limit."""
        if not self.last_request:
            return False

        # Reset count if last request was yesterday
        last = datetime.fromisoformat(self.last_request)
        if last.date() < datetime.now().date():
            return False

        return self.request_count >= self.rate_limit


@dataclass
class AccessController:
    """
    Controls access to Genesis API.

    Manages:
    - Token generation and validation
    - Rate limiting
    - Access level checks
    - Audit logging
    """

    config_path: str
    signing_key: Optional[str] = None  # For token signatures

    # Internal state
    tokens: Dict[str, AccessToken] = field(default_factory=dict, repr=False)
    _signing_key_bytes: Optional[bytes] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize access controller."""
        self.path = Path(self.config_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.tokens_dir = self.path.parent / "tokens"
        self.tokens_dir.mkdir(exist_ok=True)

        self.audit_dir = self.path.parent / "audit"
        self.audit_dir.mkdir(exist_ok=True)

        # Initialize or load signing key
        self._init_signing_key()

        # Load existing tokens
        self._load_tokens()

    def _init_signing_key(self) -> None:
        """Initialize signing key for token generation."""
        key_path = self.path.parent / ".signing_key"

        if self.signing_key:
            self._signing_key_bytes = self.signing_key.encode()
        elif key_path.exists():
            with open(key_path, "rb") as f:
                self._signing_key_bytes = f.read()
        else:
            # Generate new key
            self._signing_key_bytes = secrets.token_bytes(32)
            with open(key_path, "wb") as f:
                f.write(self._signing_key_bytes)

    def create_token(
        self,
        customer_id: str,
        level: AccessLevel,
        duration_days: int = 365,
        rate_limit: int = 1000,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an access token for a customer.

        Args:
            customer_id: Customer identifier
            level: Access level to grant
            duration_days: Token validity in days
            rate_limit: Daily request limit
            metadata: Optional metadata

        Returns:
            The token string (give this to customer)
        """
        # Generate token ID and secret
        token_id = secrets.token_hex(16)
        token_secret = secrets.token_hex(32)

        # Create full token (ID + secret)
        full_token = f"{token_id}.{token_secret}"

        # Sign the token
        signature = hmac.new(
            self._signing_key_bytes,
            full_token.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

        # Final token: id.secret.signature
        final_token = f"{full_token}.{signature}"

        # Create token record
        now = datetime.now()
        token = AccessToken(
            token_id=token_id,
            customer_id=customer_id,
            access_level=level,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(days=duration_days)).isoformat(),
            rate_limit=rate_limit,
            metadata=metadata,
        )

        # Store
        self.tokens[token_id] = token
        self._save_token(token)

        self._audit("token_created", {
            "token_id": token_id,
            "customer_id": customer_id,
            "level": level.name,
        })

        print(f"✅ Created access token for {customer_id}")
        print(f"   Level: {level.name}")
        print(f"   Expires: {token.expires_at[:10]}")
        print(f"   Rate limit: {rate_limit}/day")

        return final_token

    def validate_token(self, token_string: str) -> Optional[AccessToken]:
        """
        Validate a token string.

        Args:
            token_string: The full token (id.secret.signature)

        Returns:
            AccessToken if valid, None otherwise
        """
        try:
            parts = token_string.split(".")
            if len(parts) != 3:
                return None

            token_id, secret, signature = parts

            # Verify signature
            full_token = f"{token_id}.{secret}"
            expected_sig = hmac.new(
                self._signing_key_bytes,
                full_token.encode(),
                hashlib.sha256
            ).hexdigest()[:16]

            if not hmac.compare_digest(signature, expected_sig):
                self._audit("token_invalid_signature", {"token_id": token_id})
                return None

            # Get token record
            token = self.tokens.get(token_id)
            if token is None:
                return None

            # Check if active
            if not token.is_active:
                return None

            # Check if expired
            if token.is_expired():
                self._audit("token_expired", {"token_id": token_id})
                return None

            return token

        except Exception:
            return None

    def check_access(
        self,
        token_string: str,
        required_level: AccessLevel,
    ) -> bool:
        """
        Check if token has required access level.

        Args:
            token_string: The token to check
            required_level: Minimum required access level

        Returns:
            True if access is granted
        """
        token = self.validate_token(token_string)
        if token is None:
            return False

        # Check level
        if token.access_level.value < required_level.value:
            self._audit("access_denied_level", {
                "token_id": token.token_id,
                "required": required_level.name,
                "actual": token.access_level.name,
            })
            return False

        # Check rate limit
        if token.is_rate_limited():
            self._audit("access_denied_rate_limit", {"token_id": token.token_id})
            return False

        # Record request
        token.request_count += 1
        token.last_request = datetime.now().isoformat()

        self._audit("access_granted", {
            "token_id": token.token_id,
            "level": required_level.name,
        })

        return True

    def revoke_token(self, token_id: str, reason: str = "") -> bool:
        """Revoke a token."""
        if token_id not in self.tokens:
            return False

        self.tokens[token_id].is_active = False
        self._save_token(self.tokens[token_id])

        self._audit("token_revoked", {"token_id": token_id, "reason": reason})

        print(f"🚫 Revoked token {token_id}: {reason}")
        return True

    def list_tokens(
        self,
        customer_id: Optional[str] = None,
        active_only: bool = True,
    ) -> List[AccessToken]:
        """List tokens, optionally filtered."""
        result = []
        for token in self.tokens.values():
            if customer_id and token.customer_id != customer_id:
                continue
            if active_only and not token.is_active:
                continue
            if active_only and token.is_expired():
                continue
            result.append(token)
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get access statistics."""
        stats = {
            "total_tokens": len(self.tokens),
            "active_tokens": sum(1 for t in self.tokens.values() if t.is_active),
            "total_requests": sum(t.request_count for t in self.tokens.values()),
            "by_level": {},
        }

        for token in self.tokens.values():
            level = token.access_level.name
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

        return stats

    def _save_token(self, token: AccessToken) -> None:
        """Save token to file."""
        token_file = self.tokens_dir / f"{token.token_id}.json"
        with open(token_file, "w") as f:
            json.dump(token.to_dict(), f, indent=2)

    def _load_tokens(self) -> None:
        """Load all tokens from disk."""
        for token_file in self.tokens_dir.glob("*.json"):
            with open(token_file, "r") as f:
                data = json.load(f)
            token = AccessToken.from_dict(data)
            self.tokens[token.token_id] = token

    def _audit(self, action: str, details: Dict[str, Any]) -> None:
        """Record audit entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
        }

        audit_file = self.audit_dir / f"access_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

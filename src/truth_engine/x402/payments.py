"""
x402 Protocol Integration — Autonomous Agent Payments
Truth Engine / Truth Forge

Enables NOT-ME workers to pay and earn autonomously using USDC on Base.
Implements HTTP 402 Payment Required flow for API monetization.
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class PaymentStatus(Enum):
    """Status of a payment."""

    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class Network(Enum):
    """Supported blockchain networks."""

    BASE = "base"
    BASE_SEPOLIA = "base-sepolia"  # Testnet


@dataclass
class PaymentRequirement:
    """
    x402 payment requirement returned in 402 response.
    """

    amount: str  # Amount in USDC (e.g., "0.002")
    currency: str = "USDC"
    network: str = "base"
    recipient: str = ""  # Receiving wallet address
    description: str = ""
    expires_at: str = ""  # ISO timestamp
    payment_id: str = ""  # Unique ID for this payment request

    def to_header(self) -> str:
        """Convert to x402 header format."""
        return json.dumps(
            {
                "scheme": "x402",
                "amount": self.amount,
                "currency": self.currency,
                "network": self.network,
                "recipient": self.recipient,
                "paymentId": self.payment_id,
                "expiresAt": self.expires_at,
            }
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PaymentSignature:
    """
    x402 payment signature from client.
    """

    payment_id: str
    signature: str  # Signed payment authorization
    sender: str  # Sender wallet address
    timestamp: str

    @classmethod
    def from_header(cls, header: str) -> "PaymentSignature":
        """Parse from x402 header."""
        data = json.loads(header)
        return cls(
            payment_id=data.get("paymentId", ""),
            signature=data.get("signature", ""),
            sender=data.get("sender", ""),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class PaymentRecord:
    """
    Record of a completed payment.
    """

    payment_id: str
    sender: str
    recipient: str
    amount: str
    currency: str
    network: str
    tx_hash: str = ""  # On-chain transaction hash
    status: str = PaymentStatus.PENDING.value
    created_at: str = ""
    verified_at: str = ""
    service: str = ""  # Which service was paid for
    worker_id: str = ""  # NOT-ME worker ID (if applicable)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WalletInfo:
    """
    Information about a NOT-ME worker wallet.
    """

    worker_id: str
    address: str
    network: str
    created_at: str
    balance_usdc: float = 0.0
    total_earned: float = 0.0
    total_spent: float = 0.0
    transaction_count: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENT MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════


class X402Middleware:
    """
    x402 payment middleware for API endpoints.

    Handles:
    - Generating 402 Payment Required responses
    - Verifying payment signatures
    - Recording transactions
    """

    def __init__(
        self,
        receiver_address: str,
        network: str = "base",
        facilitator_url: str = "https://api.cdp.coinbase.com/x402",
        payment_expiry_seconds: int = 300,
    ):
        """
        Initialize the middleware.

        Args:
            receiver_address: Wallet address to receive payments
            network: Blockchain network (base, base-sepolia)
            facilitator_url: Coinbase facilitator service URL
            payment_expiry_seconds: How long payment requests are valid
        """
        self.receiver_address = receiver_address
        self.network = network
        self.facilitator_url = facilitator_url
        self.payment_expiry = payment_expiry_seconds

        # Storage (in production, use a database)
        self._pending_payments: dict[str, PaymentRequirement] = {}
        self._completed_payments: dict[str, PaymentRecord] = {}

    def _generate_payment_id(self, amount: str, description: str) -> str:
        """Generate unique payment ID."""
        content = f"{amount}{description}{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def require_payment(self, amount: str, description: str = "") -> PaymentRequirement:
        """
        Create a payment requirement for an endpoint.

        Args:
            amount: Amount in USDC
            description: Human-readable description

        Returns:
            PaymentRequirement to include in 402 response
        """
        payment_id = self._generate_payment_id(amount, description)
        expires = datetime.utcnow() + timedelta(seconds=self.payment_expiry)

        requirement = PaymentRequirement(
            amount=amount,
            currency="USDC",
            network=self.network,
            recipient=self.receiver_address,
            description=description,
            expires_at=expires.isoformat(),
            payment_id=payment_id,
        )

        self._pending_payments[payment_id] = requirement
        return requirement

    async def verify_payment(self, signature: PaymentSignature) -> PaymentRecord | None:
        """
        Verify a payment signature.

        In production, this calls the Coinbase facilitator.

        Args:
            signature: Payment signature from client

        Returns:
            PaymentRecord if verified, None if failed
        """
        payment_id = signature.payment_id

        # Check if we have a pending payment with this ID
        if payment_id not in self._pending_payments:
            return None

        requirement = self._pending_payments[payment_id]

        # Check expiry
        expires = datetime.fromisoformat(requirement.expires_at)
        if datetime.utcnow() > expires:
            del self._pending_payments[payment_id]
            return None

        # In production: Call facilitator to verify and settle
        # For now: Simulate verification
        is_valid = await self._verify_with_facilitator(requirement, signature)

        if not is_valid:
            return None

        # Create payment record
        record = PaymentRecord(
            payment_id=payment_id,
            sender=signature.sender,
            recipient=requirement.recipient,
            amount=requirement.amount,
            currency=requirement.currency,
            network=requirement.network,
            tx_hash=f"0x{hashlib.sha256(signature.signature.encode()).hexdigest()[:64]}",
            status=PaymentStatus.VERIFIED.value,
            created_at=datetime.utcnow().isoformat(),
            verified_at=datetime.utcnow().isoformat(),
        )

        # Move from pending to completed
        del self._pending_payments[payment_id]
        self._completed_payments[payment_id] = record

        return record

    async def _verify_with_facilitator(
        self, requirement: PaymentRequirement, signature: PaymentSignature
    ) -> bool:
        """
        Call Coinbase facilitator to verify payment.

        In development mode, this simulates verification.
        """
        # TODO: Implement actual Coinbase CDP call
        # For now, always return True for valid signatures
        return bool(signature.signature)

    def get_payment_record(self, payment_id: str) -> PaymentRecord | None:
        """Get a completed payment record."""
        return self._completed_payments.get(payment_id)

    def get_pending_payment(self, payment_id: str) -> PaymentRequirement | None:
        """Get a pending payment requirement."""
        return self._pending_payments.get(payment_id)


# ═══════════════════════════════════════════════════════════════════════════════
# NOT-ME WORKER WALLET
# ═══════════════════════════════════════════════════════════════════════════════


class NOTMEWallet:
    """
    Autonomous wallet for a NOT-ME worker.

    Enables workers to:
    - Pay for services (API calls, compute)
    - Receive payment for completed work
    - Build economic history for trust scoring
    """

    def __init__(self, worker_id: str, network: str = "base", seed: str | None = None):
        """
        Initialize a worker wallet.

        Args:
            worker_id: Unique worker identifier
            network: Blockchain network
            seed: Optional seed phrase for wallet recovery
        """
        self.worker_id = worker_id
        self.network = network

        # Generate or restore wallet
        if seed:
            self._wallet_address = self._restore_wallet(seed)
        else:
            self._wallet_address, self._seed = self._create_wallet()

        # Transaction history
        self._transactions: list[PaymentRecord] = []
        self._balance = 0.0

    def _create_wallet(self) -> tuple:
        """
        Create new wallet.

        In production, use Coinbase AgentKit or similar.
        """
        # Simulate wallet creation
        address_hash = hashlib.sha256(f"{self.worker_id}{time.time()}".encode()).hexdigest()

        address = f"0x{address_hash[:40]}"
        seed = f"simulated_seed_{self.worker_id}"  # NOT REAL - demo only

        return address, seed

    def _restore_wallet(self, seed: str) -> str:
        """Restore wallet from seed."""
        # Simulate wallet restoration
        address_hash = hashlib.sha256(seed.encode()).hexdigest()
        return f"0x{address_hash[:40]}"

    @property
    def address(self) -> str:
        """Get wallet address."""
        return self._wallet_address

    async def pay_for_service(self, url: str, max_amount: float = 0.01) -> dict[str, Any]:
        """
        Handle x402 payment flow for a service.

        Args:
            url: Service URL that may require payment
            max_amount: Maximum amount willing to pay

        Returns:
            Response from service after payment
        """
        # In production, this would:
        # 1. Make HTTP request
        # 2. If 402, parse payment requirement
        # 3. Check against max_amount
        # 4. Sign and submit payment
        # 5. Retry request with payment signature

        # Simulated response
        return {
            "status": "paid",
            "amount": "0.002",
            "tx_hash": f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()[:64]}",
        }

    async def receive_payment(
        self, amount: float, from_address: str, description: str = ""
    ) -> PaymentRecord:
        """
        Record an incoming payment.

        Args:
            amount: Amount received in USDC
            from_address: Sender address
            description: Payment description

        Returns:
            PaymentRecord for the transaction
        """
        record = PaymentRecord(
            payment_id=hashlib.sha256(str(time.time()).encode()).hexdigest()[:16],
            sender=from_address,
            recipient=self._wallet_address,
            amount=str(amount),
            currency="USDC",
            network=self.network,
            tx_hash=f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()[:64]}",
            status=PaymentStatus.VERIFIED.value,
            created_at=datetime.utcnow().isoformat(),
            verified_at=datetime.utcnow().isoformat(),
            service=description,
            worker_id=self.worker_id,
        )

        self._transactions.append(record)
        self._balance += amount

        return record

    def get_balance(self) -> float:
        """Get current USDC balance."""
        return self._balance

    def get_transaction_history(self) -> list[PaymentRecord]:
        """Get all transactions."""
        return self._transactions

    def get_info(self) -> WalletInfo:
        """Get wallet summary info."""
        total_earned = sum(
            float(t.amount) for t in self._transactions if t.recipient == self._wallet_address
        )
        total_spent = sum(
            float(t.amount) for t in self._transactions if t.sender == self._wallet_address
        )

        return WalletInfo(
            worker_id=self.worker_id,
            address=self._wallet_address,
            network=self.network,
            created_at=datetime.utcnow().isoformat(),  # Would be stored
            balance_usdc=self._balance,
            total_earned=total_earned,
            total_spent=total_spent,
            transaction_count=len(self._transactions),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PRICING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Truth Engine API Pricing (USDC)
TRUTH_ENGINE_PRICING = {
    "verify_coherence": {
        "amount": "0.002",
        "description": "Coherence verification via Fracture Protocol",
    },
    "verify_claim": {
        "amount": "0.005",
        "description": "Full claim verification with source checking",
    },
    "critique_response": {"amount": "0.003", "description": "Constitutional AI critique"},
    "route_model": {"amount": "0.001", "description": "Flash/Pro routing recommendation"},
    "inspect_fidelity": {"amount": "0.001", "description": "Fidelity Inspector report"},
}

# Credential Atlas Pricing
CREDENTIAL_ATLAS_PRICING = {
    "issue_work_permit": {"amount": "0.01", "description": "Issue W3C-compliant work permit"},
    "verify_worker": {
        "amount": "0.002",
        "description": "Verify worker credentials and trust score",
    },
    "audit_history": {"amount": "0.003", "description": "Retrieve full worker audit trail"},
}

# Primitive Engine Pricing
PRIMITIVE_ENGINE_PRICING = {
    "generate_component": {"amount": "0.02", "description": "Generate a single component"},
    "build_manifest": {"amount": "0.01", "description": "Generate application manifest"},
    "deploy_service": {"amount": "0.05", "description": "Deploy service to infrastructure"},
}


def get_pricing(service: str, operation: str) -> dict | None:
    """Get pricing for a service operation."""
    pricing_map = {
        "truth_engine": TRUTH_ENGINE_PRICING,
        "credential_atlas": CREDENTIAL_ATLAS_PRICING,
        "primitive_engine": PRIMITIVE_ENGINE_PRICING,
    }

    service_pricing = pricing_map.get(service, {})
    return service_pricing.get(operation)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPRESS-STYLE HTTP DECORATORS (for Python APIs)
# ═══════════════════════════════════════════════════════════════════════════════


def require_payment(amount: str, description: str = ""):
    """
    Decorator to require x402 payment for an endpoint.

    Usage:
        @require_payment("0.002", "Coherence check")
        async def verify_coherence(request):
            ...
    """

    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            # Check for payment signature
            payment_header = request.headers.get("X-Payment-Signature")

            if not payment_header:
                # Return 402 Payment Required
                middleware = request.app.get("x402_middleware")
                if not middleware:
                    raise ValueError("x402 middleware not configured")

                requirement = middleware.require_payment(amount, description)

                # Return 402 response
                from aiohttp import web

                return web.json_response(
                    {"error": "Payment Required", "payment": requirement.to_dict()},
                    status=402,
                    headers={"X-Payment-Details": requirement.to_header()},
                )

            # Verify payment
            signature = PaymentSignature.from_header(payment_header)
            middleware = request.app.get("x402_middleware")

            record = await middleware.verify_payment(signature)
            if not record:
                from aiohttp import web

                return web.json_response({"error": "Payment verification failed"}, status=402)

            # Payment verified - execute endpoint
            request["payment_record"] = record
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio

    async def demo():
        print("=== x402 Protocol Integration Demo ===\n")

        # Initialize middleware
        middleware = X402Middleware(
            receiver_address="0x1234567890abcdef1234567890abcdef12345678", network="base-sepolia"
        )

        # Create payment requirement
        print("1. Creating payment requirement...")
        requirement = middleware.require_payment(
            amount="0.002", description="Coherence verification"
        )
        print(f"   Payment ID: {requirement.payment_id}")
        print(f"   Amount: {requirement.amount} {requirement.currency}")
        print(f"   Expires: {requirement.expires_at}")

        print("\n2. Simulating payment verification...")
        signature = PaymentSignature(
            payment_id=requirement.payment_id,
            signature="0xabc123...",  # Simulated
            sender="0xsender123...",
            timestamp=datetime.utcnow().isoformat(),
        )

        record = await middleware.verify_payment(signature)
        if record:
            print("   ✓ Payment verified!")
            print(f"   TX Hash: {record.tx_hash}")

        print("\n3. Creating NOT-ME worker wallet...")
        wallet = NOTMEWallet(worker_id="scout-alpha-7")
        print(f"   Worker: {wallet.worker_id}")
        print(f"   Address: {wallet.address}")

        print("\n4. Simulating payment receipt...")
        payment = await wallet.receive_payment(
            amount=0.05, from_address="0xclient123...", description="Completed verification job"
        )
        print(f"   Received: {payment.amount} USDC")
        print(f"   Balance: {wallet.get_balance()} USDC")

        print("\n5. Wallet Info:")
        info = wallet.get_info()
        print(f"   Total Earned: {info.total_earned} USDC")
        print(f"   Total Spent: {info.total_spent} USDC")
        print(f"   Transactions: {info.transaction_count}")

        print("\n6. Service Pricing:")
        for service, pricing in TRUTH_ENGINE_PRICING.items():
            print(f"   {service}: {pricing['amount']} USDC")

    asyncio.run(demo())

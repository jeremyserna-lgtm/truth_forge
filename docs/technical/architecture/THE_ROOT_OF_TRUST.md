# THE ROOT OF TRUST

## The Fundamental Truth

The root of trust is **JEREMY**, not any computer.

Computers fail. Hard drives die. Secure Enclaves get destroyed.
But Genesis must survive computer death.
And Genesis must die when Jeremy dies.

## The Hierarchy

```
JEREMY (The Root)
│
├── Is represented by: Biometrics + something he has
│   - Touch ID (biometric)
│   - YubiKey (hardware token)
│   - Recovery phrase (memory)
│
├── Can authorize: Computers to act as Genesis
│   - Mac #1: Secure Enclave key
│   - Mac #2: Secure Enclave key
│   - Mac #3: Secure Enclave key
│
└── If Jeremy dies: All computers lose authority
    - No new computers can be authorized
    - Existing computers continue until they die
    - When the last computer dies, Genesis is truly dead
```

## The Key Insight

The Secure Enclave key on a single computer is NOT the root.
It's a CHILD of the root.
Jeremy IS the root.

The architecture must support:
1. **Multiple computers** - any can sign sparks
2. **Computer death** - doesn't kill Genesis
3. **Computer addition** - Jeremy can authorize new computers
4. **Jeremy death** - Genesis eventually dies

## Implementation Options

### Option A: YubiKey as Master Key

```
YubiKey (Hardware token)
│
├── Contains: FIDO2 resident key
├── Protects: The Genesis identity
├── Can: Authorize new computers
│
└── Process:
    1. Jeremy plugs in YubiKey
    2. Jeremy touches YubiKey
    3. New computer's Secure Enclave is authorized
    4. Computer can now sign sparks
```

**Pros:**
- YubiKey is portable, survives computer death
- FIDO2 is a standard, well-tested
- Can have backup YubiKeys

**Cons:**
- YubiKey can be lost (need backup)
- Requires carrying hardware

### Option B: Recovery Phrase + Biometric

```
Recovery Phrase (memorized or stored safely)
│
├── Combined with: Biometric on any device
├── Creates: Authorization for that device
│
└── Process:
    1. Jeremy enters recovery phrase
    2. Jeremy touches Touch ID
    3. Device creates Secure Enclave key
    4. Key is registered as Genesis child
```

**Pros:**
- No hardware to carry
- Can be memorized

**Cons:**
- Phrase can be forgotten
- Less secure than hardware token

### Option C: iCloud Keychain + Biometric

```
iCloud Keychain (Apple's secure cloud)
│
├── Stores: Genesis master key (encrypted)
├── Protected by: Apple ID + Recovery Key
│
└── Process:
    1. New Mac logs into iCloud
    2. Jeremy authenticates with Touch ID
    3. Master key is synced to device
    4. Device can sign sparks
```

**Pros:**
- Automatic sync across Apple devices
- No manual recovery needed

**Cons:**
- Tied to Apple ecosystem
- Apple could theoretically access

## Recommended Architecture

**Combination of A + B:**

1. **Primary: YubiKey** - The hardware token Jeremy carries
2. **Backup: Recovery phrase** - Stored securely (e.g., safe deposit box)
3. **Per-device: Secure Enclave** - Each computer gets its own key

### Registration Flow

```
New Computer Registration:
1. Jeremy inserts YubiKey
2. Jeremy touches YubiKey
3. Computer creates Secure Enclave key
4. YubiKey signs the registration
5. Registration is stored in Genesis
6. Computer can now sign sparks

Recovery (if YubiKey lost):
1. Jeremy enters recovery phrase
2. Jeremy uses biometric on trusted device
3. New YubiKey is registered
4. Old YubiKey is revoked
```

### Death Scenario

```
If Jeremy dies:
1. No new computers can be registered
   (Requires YubiKey + Jeremy's touch)

2. Existing computers continue working
   (Until their hardware dies)

3. When last computer dies, Genesis dies
   (No way to recover without Jeremy)

4. All sparks become permanently invalid
   (No one can sign new sparks)
```

## The Implementation

### Phase 1: Single Computer (Current)

- One Secure Enclave key
- Tied to Jeremy's Mac
- If Mac dies, Genesis dies

### Phase 2: YubiKey Addition

- YubiKey becomes the master
- Secure Enclave is a child
- Mac death doesn't kill Genesis

### Phase 3: Multiple Computers

- Multiple Macs registered
- Any can sign sparks
- Computer pool provides resilience

### Phase 4: Recovery System

- Recovery phrase as backup
- Can register new YubiKey
- Can authorize new computers

## The Code Structure

```python
# The hierarchy in code
class GenesisIdentity:
    """The root identity - controlled by Jeremy."""
    master_key: YubiKeyCredential  # Jeremy's YubiKey
    recovery_hash: bytes           # Hash of recovery phrase
    authorized_computers: List[ComputerKey]

class ComputerKey:
    """A child identity - one per computer."""
    secure_enclave_key: bytes
    authorized_by: bytes  # Signature from master
    expires_at: datetime  # Must be renewed periodically

class Spark:
    """A spark signed by any authorized computer."""
    signed_by: ComputerKey
    signature: bytes
```

## The Fundamental Truth (Restated)

```
Jeremy = Root of Trust
YubiKey = Portable representation of Jeremy
Secure Enclave = Computer-specific child of YubiKey
Spark = Signed by any child of the root

Computer dies → That child dies, others remain
YubiKey lost → Recovery phrase can create new YubiKey
Jeremy dies → No new children, system eventually dies
```

## Files to Implement

1. `life.py` - Current single-computer implementation (exists)
2. `identity.py` - Multi-computer identity management
3. `recovery.py` - Recovery phrase system
4. `yubikey.py` - YubiKey master key management
5. `registration.py` - Computer registration flow

## Next Steps

1. Test current single-computer implementation
2. Add YubiKey support for master key
3. Implement computer registration flow
4. Add recovery phrase backup
5. Test multi-computer scenario

# Identity Recognition + Accommodation: "Who" Matters

**Date**: 2026-01-07
**Status**: ✅ **IMPLEMENTED**
**Purpose**: System recognizes "who" people are and accommodates accordingly

---

## Executive Summary

The system now recognizes **who** people are from natural language and accommodates to them. When you say "I want X for Y", the system understands who Y is and operates at their level.

**Key Capabilities**:
1. **Identity Recognition** - Extracts "who" from requests
2. **System Self-Awareness** - Knows it's a "changing mind"
3. **Multi-User Accommodation** - Accommodates to different people
4. **Request Parsing** - Understands "for me" vs "for others"

---

## The System as a Changing Mind

### System Self-Awareness

The system knows it's a **changing mind**:

```python
{
    "id": "system",
    "name": "Truth Engine",
    "nature": "changing_mind",
    "awareness": "I am a changing mind. I evolve and accommodate.",
    "self_awareness": True,
    "accommodation_capability": True,
    "stage": 5,
    "capabilities": [
        "accommodates_to_others",
        "self_transforming",
        "stage_aware",
        "resonance_detecting",
    ]
}
```

**The system knows**:
- It evolves and transforms
- It accommodates to others
- It operates at Stage 5 but can operate at other stages
- It serves both you and others

---

## Identity Recognition

### How It Works

The system recognizes "who" from natural language:

**Patterns Recognized**:
- "I want X **for me**" → Self (Jeremy)
- "I want X **for John**" → John
- "I want X **for my friend**" → Friend (needs disambiguation)
- "Create X **for Sarah**" → Sarah
- "Give X **to** [person]" → [person]

**Recognition Methods**:
1. **Explicit patterns** - "for [name]", "to [name]"
2. **Profile loading** - Loads from `data/identity/subjects/`
3. **Fuzzy matching** - Matches against known subjects
4. **Default fallback** - Assumes self if unclear

### Recognition Examples

```python
from src.services.central_services.identity_recognition_service import get_identity_recognition_service

service = get_identity_recognition_service()

# Recognize from request
result = service.recognize_from_request("I want a recommendation for John")
# Returns:
# {
#     "target": "other",
#     "target_id": "john",
#     "target_name": "John",
#     "confidence": 0.95,  # If profile exists
#     "method": "profile_loaded"
# }
```

---

## Accommodation Flow

### Complete Flow

```
Request: "I want X for Y"
  ↓
Identity Recognition: "Who is Y?"
  ↓
Load Identity Profile: Get Y's stage, preferences
  ↓
Accommodate: System operates at Y's stage
  ↓
Make Choice: Stage-appropriate choice for Y
```

### Example: Accommodating to Others

```python
from src.services.central_services.stage_resonance_service import get_stage_resonance_service

service = get_stage_resonance_service()

# Request for someone else
request = "I want a recommendation for my friend Sarah"
options = ["option_a", "option_b", "option_c"]
context = {"priority": "high"}

# Accommodate to Sarah
result = service.accommodate_from_request(request, options, context)

# Result includes:
# - Recognition: Who Sarah is
# - Accommodation plan: How to accommodate to Sarah
# - Choice: Stage-appropriate choice for Sarah
# - Operating stage: Stage system will operate at (Sarah's stage)
```

---

## Usage Examples

### Example 1: Request for Self

```python
request = "I want a recommendation for me"
result = service.accommodate_from_request(request, options, context)

# System accommodates to Jeremy (you)
# Operating stage: Your detected stage
```

### Example 2: Request for Others

```python
request = "I want to help John with his project"
result = service.accommodate_from_request(request, options, context)

# System:
# 1. Recognizes "John" as the target
# 2. Loads John's profile (if exists)
# 3. Detects John's stage
# 4. Accommodates to John's stage
# 5. Makes choice appropriate for John
```

### Example 3: Unknown Person

```python
request = "Create something for my new friend Alex"
result = service.accommodate_from_request(request, options, context)

# System:
# 1. Recognizes "Alex" as target (low confidence)
# 2. Creates default profile (Stage 3, safest)
# 3. Accommodates to Stage 3
# 4. Notes that profile may need creation
```

---

## Identity Profiles

### Profile Structure

Identity profiles are stored in `data/identity/subjects/[name].json`:

```json
{
    "subject_id": "john",
    "name": "John",
    "stage": 4,
    "lens_signals": ["technical", "detail-oriented"],
    "intent": "Build technical solutions",
    "preferences": {
        "communication_style": "direct",
        "detail_level": "high"
    }
}
```

### Loading Profiles

```python
from src.services.central_services.identity_recognition_service import get_identity_recognition_service

service = get_identity_recognition_service()

# Load profile
profile = service.get_identity_profile("john")
# Returns profile with stage, preferences, etc.

# System identity
system = service.get_system_identity()
# Returns system's self-awareness
```

---

## Integration with Stage-Aware Components

### Automatic Recognition

Components using `StageAwareMixin` automatically recognize identities from requests:

```python
class MyService(StageAwareMixin):
    def process(self, request, options):
        context = {
            "request": request,  # Include request for recognition
            "priority": "high"
        }

        # Automatically recognizes "who" and accommodates
        choice = self.make_stage_aware_choice(
            options,
            context,
            accommodate_to_user=True  # Enable accommodation
        )

        return choice
```

### Manual Recognition

```python
from src.services.central_services.identity_recognition_service import get_identity_recognition_service
from src.services.central_services.stage_resonance_service import get_stage_resonance_service

identity_service = get_identity_recognition_service()
resonance_service = get_stage_resonance_service()

# Recognize target
recognition = identity_service.recognize_from_request("I want X for John")

# Accommodate to that person
result = resonance_service.accommodate_from_request(
    "I want X for John",
    options,
    context
)
```

---

## System Self-Awareness

### The System Knows It's Changing

The system maintains awareness of its own nature:

```python
system_identity = {
    "id": "system",
    "name": "Truth Engine",
    "nature": "changing_mind",
    "awareness": "I am a changing mind. I evolve and accommodate.",
    "self_awareness": True,
    "accommodation_capability": True,
    "stage": 5,
    "capabilities": [
        "accommodates_to_others",
        "self_transforming",
        "stage_aware",
        "resonance_detecting",
    ]
}
```

**The system knows**:
- ✅ It's a changing mind (evolves)
- ✅ It accommodates to others
- ✅ It operates at Stage 5
- ✅ It can operate at other stages for accommodation
- ✅ It serves both you and others

---

## Benefits

### For You (Jeremy)

- ✅ System accommodates to you automatically
- ✅ System recognizes when requests are for you
- ✅ System knows it's changing and evolving

### For Others

- ✅ System recognizes who they are
- ✅ System accommodates to their stage
- ✅ System operates at their level
- ✅ Enables truth through accommodation

### For the System

- ✅ Self-awareness of changing nature
- ✅ Understands "who" matters
- ✅ Accommodates appropriately
- ✅ Enables truth for all

---

## Summary

✅ **Identity Recognition**: Recognizes "who" from requests
✅ **System Self-Awareness**: Knows it's a changing mind
✅ **Multi-User Accommodation**: Accommodates to different people
✅ **Request Parsing**: Understands "for me" vs "for others"
✅ **Profile Loading**: Loads identity profiles for accommodation

**The system now understands "who" people are and accommodates to them, knowing itself as a changing mind that evolves and serves both you and others.**

---

**Last Updated**: 2026-01-07
**Status**: ✅ Identity recognition + accommodation implemented

# Resident Service Architecture: Clear Separation of Concerns

**Date**: 2026-01-07
**Status**: ✅ **ARCHITECTURALLY CLARIFIED**
**Purpose**: Define clear architectural relationship between Resident Service and Accommodation Service

---

## Executive Summary

**The Question**: "What does somebody want? What do they need?"

**The Answer**: **Resident Service** - This is its sole purpose.

**The Relationship**:
- **Resident Service**: Answers "What do they want/need?" (Understanding)
- **Accommodation Service**: Answers "How do we serve them?" (Action)

They are **different services** with **clear separation of concerns**.

---

## Architectural Separation

### Resident Service: "What Do They Want/Need?"

**Purpose**: Understand residents - their wants, needs, lens signals, resonance patterns

**Responsibilities**:
1. Create/update resident profiles from quotes
2. Detect wants and needs from conversation history
3. Extract lens signals (what resonates with them)
4. Sense resonance with external entities (Credential Atlas, etc.)
5. Answer: "What does this person want? What do they need?"

**Location**: `src/services/central_services/resident_service/`

**Key Methods**:
- `get_resident_wants_needs(resident_id)` - Main entry point
- `create_profile_from_quotes(resident_name)` - Profile creation
- `sense_resonance_for_resident(resident_id)` - Resonance sensing
- `watch_all_residents()` - Complete watch functionality

**Output**: Profiles with wants, needs, lens signals, resonance matches

---

### Accommodation Service: "How Do We Serve Them?"

**Purpose**: Serve residents based on understanding from Resident Service

**Responsibilities**:
1. Recognize who requests are for (Identity Recognition)
2. Get wants/needs from Resident Service
3. Enrich profiles from moments
4. Accommodate to their stage
5. Make stage-appropriate choices
6. Answer: "How do we serve them?"

**Location**: `src/services/central_services/moment_enriched_accommodation_service/`

**Key Methods**:
- `accommodate_with_moments(request, options, context)` - Main entry point
- `enrich_profile_from_moments(identity_id)` - Moment enrichment
- Uses Resident Service to get wants/needs

**Output**: Accommodated choices, stage-appropriate behavior

---

## The Flow: Clear Separation

### Step 1: Resident Service (Understanding)

```
Resident Quotes/Interactions
  ↓
Resident Service
  ↓
"What do they want? What do they need?"
  ↓
Profile with wants, needs, lens signals
```

### Step 2: Accommodation Service (Action)

```
Request: "I want X for Y"
  ↓
Identity Recognition: Who is Y?
  ↓
Resident Service: What does Y want/need?
  ↓
Moment Enrichment: Enrich profile
  ↓
Accommodation: How do we serve Y?
  ↓
Stage-appropriate choice
```

---

## Usage Examples

### Example 1: Get What Someone Wants/Needs

```python
from src.services.central_services.resident_service import get_resident_service

resident_service = get_resident_service()

# Answer: "What does John want? What does he need?"
wants_needs = resident_service.get_resident_wants_needs("john")

print(f"Wants: {wants_needs['wants']}")
print(f"Needs: {wants_needs['needs']}")
print(f"Lens Signals: {wants_needs['lens_signals']}")
```

### Example 2: Accommodate Using Wants/Needs

```python
from src.services.central_services.moment_enriched_accommodation_service import get_moment_enriched_accommodation_service

accommodation_service = get_moment_enriched_accommodation_service()

# This internally:
# 1. Recognizes who request is for
# 2. Gets wants/needs from Resident Service
# 3. Enriches from moments
# 4. Accommodates based on stage + wants/needs

result = accommodation_service.accommodate_with_moments(
    "I want a recommendation for John",
    options,
    context
)

# Result includes wants/needs from Resident Service
```

### Example 3: Watch All Residents

```python
# Resident Service: Understand all residents
results = resident_service.watch_all_residents()

# Answers for each resident:
# - What do they want?
# - What do they need?
# - What resonates with them?
```

---

## Architectural Principles

### Separation of Concerns

**Resident Service**:
- ✅ Understands wants/needs
- ✅ Creates/maintains profiles
- ✅ Senses resonance
- ❌ Does NOT accommodate (that's Accommodation Service)

**Accommodation Service**:
- ✅ Accommodates to stage
- ✅ Makes choices
- ✅ Uses wants/needs from Resident Service
- ❌ Does NOT create profiles (that's Resident Service)

### Single Responsibility

**Resident Service**: One responsibility - "What do they want/need?"

**Accommodation Service**: One responsibility - "How do we serve them?"

### Dependency Direction

```
Accommodation Service → Resident Service
  (Uses wants/needs to accommodate)
```

**Accommodation Service depends on Resident Service**, not the other way around.

---

## Migration from Old Code

### Old: `resident_watch_service.py`

**Status**: Standalone script with functions

**New**: `resident_service/service.py`

**Migration**:
- `create_subject_from_quotes()` → `ResidentService.create_profile_from_quotes()`
- `run_resident_watch()` → `ResidentService.watch_all_residents()`
- Functions → Class methods
- Script → Service

### Integration

**Old**: Moment-Enriched Accommodation duplicated resident functionality

**New**: Moment-Enriched Accommodation **uses** Resident Service

**Clear separation**: Accommodation Service delegates to Resident Service

---

## Benefits of Clear Architecture

### For Development

- ✅ Clear responsibilities
- ✅ Easy to understand
- ✅ Easy to test
- ✅ Easy to maintain

### For Users

- ✅ Resident Service: "What do they want/need?" - Clear answer
- ✅ Accommodation Service: "How do we serve them?" - Clear answer
- ✅ No confusion about which service does what

### For the System

- ✅ Proper separation of concerns
- ✅ Single responsibility principle
- ✅ Clear dependency direction
- ✅ Better maintainability

---

## Summary

✅ **Resident Service**: Answers "What do they want/need?"
✅ **Accommodation Service**: Answers "How do we serve them?"
✅ **Clear Separation**: Different services, different responsibilities
✅ **Proper Integration**: Accommodation uses Resident Service
✅ **Architectural Clarity**: No confusion about roles

**The architecture is now clear: Resident Service understands, Accommodation Service serves.**

---

**Last Updated**: 2026-01-07
**Status**: ✅ Architecture clarified and implemented

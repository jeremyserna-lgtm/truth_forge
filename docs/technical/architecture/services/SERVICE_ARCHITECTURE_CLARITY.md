# Service Architecture: Clear Separation of Concerns

**Date**: 2026-01-07
**Status**: ✅ **ARCHITECTURALLY CLARIFIED**
**Purpose**: Clear definition of Resident Service vs Accommodation Service

---

## The Question

**"What does somebody want? What do they need?"**

## The Answer

**Resident Service** - This is its sole purpose.

---

## Architectural Separation

### Resident Service: "What Do They Want/Need?"

**Purpose**: Understand residents - their wants, needs, lens signals

**Location**: `src/services/central_services/resident_service/`

**Key Question**: "What does this person want? What do they need?"

**Responsibilities**:
- ✅ Create/update resident profiles from quotes
- ✅ Detect wants and needs from conversation history
- ✅ Extract lens signals (what resonates with them)
- ✅ Sense resonance with external entities
- ❌ Does NOT accommodate (that's Accommodation Service)

**Main Method**: `get_resident_wants_needs(resident_id)`

---

### Accommodation Service: "How Do We Serve Them?"

**Purpose**: Serve residents based on understanding from Resident Service

**Location**: `src/services/central_services/moment_enriched_accommodation_service/`

**Key Question**: "How do we serve them?"

**Responsibilities**:
- ✅ Recognize who requests are for
- ✅ Get wants/needs from Resident Service
- ✅ Enrich profiles from moments
- ✅ Accommodate to their stage
- ✅ Make stage-appropriate choices
- ❌ Does NOT create profiles (that's Resident Service)

**Main Method**: `accommodate_with_moments(request, options, context)`

---

## The Flow

```
1. Resident Service: "What do they want/need?"
   ↓
2. Accommodation Service: "How do we serve them?"
   ↓
3. Stage-appropriate accommodation
```

---

## Dependency Direction

```
Accommodation Service → Resident Service
  (Uses wants/needs to accommodate)
```

**Accommodation Service depends on Resident Service**, not the other way around.

---

## Summary

✅ **Resident Service**: Answers "What do they want/need?"
✅ **Accommodation Service**: Answers "How do we serve them?"
✅ **Clear Separation**: Different services, different responsibilities
✅ **Proper Integration**: Accommodation uses Resident Service

**The architecture is now clear: Resident Service understands, Accommodation Service serves.**

---

**Last Updated**: 2026-01-07
**Status**: ✅ Architecture clarified

# Unit Designation System

**Version:** 1.0  
**Created:** January 24, 2026  
**Purpose:** Standardized naming for products, deliverables, and customer systems

---

## Core Concept

Every Truth Engine product and customer system receives a **Unit Designation**—a standardized identifier that:
- Creates collectibility and permanence
- Signals technical sophistication
- Distinguishes from generic "accounts" or "subscriptions"
- Reinforces ownership (you don't subscribe to a unit—you own it)

---

## Designation Format

```
[BRAND] / [CATEGORY] / [IDENTIFIER]
```

### Examples

| Context | Designation |
|---------|-------------|
| Truth Engine holding company | `TRUTH ENGINE` |
| Primitive Engine subsidiary | `PRIMITIVE ENGINE / BUILD SYSTEMS` |
| Credential Atlas subsidiary | `CREDENTIAL ATLAS / VERIFICATION SYSTEMS` |
| Stage 5 Mind product | `STAGE 5 MIND / PERSONAL AI` |
| Customer's personal system | `UNIT 047 / JEREMY SYSTEM` |
| Customer's NOT-ME | `NOT-ME / ATLAS` |

---

## Product Designations

### Truth Engine Products

| Product | Designation |
|---------|-------------|
| Soldier Tier | `TRUTH ENGINE / SOLDIER CLASS` |
| King Tier | `TRUTH ENGINE / KING CLASS` |
| Empire Tier | `TRUTH ENGINE / EMPIRE CLASS` |

### Stage 5 Mind Products

| Product | Designation |
|---------|-------------|
| Free tier | `STAGE 5 MIND / DISCOVERY` |
| Paid tier | `STAGE 5 MIND / PERSONAL` |
| Premium tier | `STAGE 5 MIND / SOVEREIGN` |

---

## Customer Unit Numbers

When a customer purchases a personal AI system, they receive a **Unit Number**.

### Numbering Convention

```
UNIT [XXX]
```

- Numbers are sequential from 001
- Leading zeros preserved (001, 047, 999)
- Numbers never reused
- Original JEREMY system is UNIT 001

### Examples

| Customer | Unit Designation |
|----------|------------------|
| Jeremy (founder) | `UNIT 001 / JEREMY SYSTEM` |
| First customer | `UNIT 002 / [NAME] SYSTEM` |
| 47th customer | `UNIT 047 / [NAME] SYSTEM` |

### Display Format

**Full formal:**
```
TRUTH ENGINE
UNIT 047 / MARTINEZ SYSTEM
KING CLASS
```

**Abbreviated:**
```
TE-047
```

**Conversational:**
"Unit 47" or "the Martinez system"

---

## NOT-ME Designations

When a user discovers their NOT-ME through Stage 5 Mind:

### Format
```
NOT-ME / [NAME]
```

### Examples
- `NOT-ME / ATLAS`
- `NOT-ME / VERA`
- `NOT-ME / SILAS`

### With System Context
```
STAGE 5 MIND
NOT-ME / ATLAS
DISCOVERED 2026.01.24
```

---

## Hardware Designations

For physical hardware configurations:

### Format
```
[UNIT] / [CONFIG]
```

### Examples

| Configuration | Designation |
|---------------|-------------|
| Single Mac Studio | `UNIT 047 / SINGLE` |
| Dual Mac Studio | `UNIT 047 / DUAL` |
| Quad Mac Studio | `UNIT 047 / QUAD` |
| Custom build | `UNIT 047 / CUSTOM` |

### Specification Block

```
UNIT 047 / QUAD
━━━━━━━━━━━━━━━━━━━━━
MEMORY      1.28TB UNIFIED
PROCESSING  M4 ULTRA × 4
STORAGE     8TB NVMe
NETWORK     DISTRIBUTED
━━━━━━━━━━━━━━━━━━━━━
COMMISSIONED 2026.01.24
```

---

## Typography Treatment

Unit designations always use **JetBrains Mono**:

```css
font-family: 'JetBrains Mono', monospace;
font-weight: 400;
letter-spacing: 0.02em;
text-transform: uppercase;
```

### Sizing

| Context | Size |
|---------|------|
| Primary display | 14px |
| Secondary/label | 12px |
| Specification blocks | 11px |
| Micro (badges) | 10px |

---

## Visual Treatment

### Unit Badge

A standardized badge for displaying unit designation:

```
┌─────────────────────────────┐
│  UNIT 047 / MARTINEZ SYSTEM │
│  TRUTH ENGINE · KING CLASS  │
└─────────────────────────────┘
```

- Border: 1px, brand accent color
- Background: transparent or subtle fill
- Text: JetBrains Mono
- Can include brand mark at left

### Certificate Format

For formal documentation (ownership certificates, etc.):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

              TRUTH ENGINE

           UNIT 047 / MARTINEZ
              KING CLASS

     Commissioned: January 24, 2026
        Serial: TE-K-047-20260124

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Serial Number System

For tracking and verification:

### Format
```
[BRAND]-[CLASS]-[UNIT]-[DATE]
```

### Examples
- `TE-S-002-20260215` — Truth Engine, Soldier, Unit 2, Feb 15 2026
- `TE-K-047-20260124` — Truth Engine, King, Unit 47, Jan 24 2026
- `S5-P-089-20260301` — Stage 5 Mind, Personal, Unit 89, Mar 1 2026

### Class Codes

| Class | Code |
|-------|------|
| Soldier | S |
| King | K |
| Empire | E |
| Discovery (free) | D |
| Personal | P |
| Sovereign | V |

---

## Usage Guidelines

### When to Use Unit Designations

**Always use for:**
- Customer documentation
- Ownership certificates
- Hardware labeling
- Support tickets
- Invoice headers

**Optionally use for:**
- Marketing (creates exclusivity)
- Community identification
- Progress tracking

### When NOT to Use

- Casual conversation (unless customer prefers it)
- General marketing to broad audience
- Contexts where it seems pretentious

---

## Collectibility Angle

The unit numbering creates:

1. **Scarcity signal** — "Only 47 units exist"
2. **Community identity** — "I'm Unit 23"
3. **Historical value** — Lower numbers have provenance
4. **Pride of ownership** — Not an account, a UNIT

### Milestone Numbers

Consider special recognition for:
- Unit 001 (founder's system)
- Unit 100, 500, 1000 (milestones)
- Early adopters (Units 002-050)

---

## Implementation

### Database Fields

```sql
unit_number INTEGER UNIQUE NOT NULL,
unit_designation VARCHAR(100), -- "UNIT 047 / MARTINEZ SYSTEM"
serial_number VARCHAR(50),     -- "TE-K-047-20260124"
class VARCHAR(20),             -- "KING"
commissioned_at TIMESTAMP
```

### API Response

```json
{
  "unit": {
    "number": 47,
    "designation": "UNIT 047 / MARTINEZ SYSTEM",
    "serial": "TE-K-047-20260124",
    "class": "KING",
    "commissioned": "2026-01-24T00:00:00Z"
  }
}
```

---

*You don't have an account. You have a Unit. You don't subscribe. You own.*

# Business Plan Document Primitive

**Version**: 1.0.0
**Type**: Document Template (The Primitive)
**Date**: 2025-12-31

---

## What This Is

This is the PRIMITIVE for business plan documents. It defines what a business plan IS in the Truth Engine system.

Every business plan document follows this structure. The structure IS the primitive.

---

## The Structure (The Primitive)

```
# [Product/Company] Business Plan

**Version**: X.X.X
**Status**: LIVING DOCUMENT
**Type**: [B2B/B2C] Product Business Plan
**Date**: YYYY-MM-DD

---

## Quick Reference: The Business in Sentences

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| [Subject] | [verb] | [object] | [standard/destination] |

---

## 1. Theory (WHY)

### 1.1 The Problem
[What pain exists]

### 1.2 The Furnace Applied
[Raw → Heat → Forged → Delivered]

### 1.3 Why This Matters
[Why anyone should care]

---

## 2. Specification (WHAT)

### 2.1 The Product
[What you're building]

### 2.2 Core Features
[What it does]

### 2.3 Target Market
[Who pays]

### 2.4 Pricing
[How much]

---

## 3. Reference (HOW)

### 3.1 Technical Architecture
[How it works]

### 3.2 What's Built
[Current state]

### 3.3 What Needs Building
[Remaining work]

### 3.4 Go-To-Market
[How to sell - filtered by Me/Not-Me]

---

## 4. The Numbers

### 4.1 Revenue Projections
[Money over time]

### 4.2 Unit Economics
[CAC, LTV, margin]

### 4.3 Costs
[What you spend]

---

## 5. The Moat

### 5.1 Defensibility
[Why competitors can't copy]

---

## 6. The Entity

[Legal structure]

---

## 7. Alignment Check

| Truth Engine Standards | Status |
|------------------------|--------|
| Three-Layer Test | Applied/Not Applied |
| Sentence Pattern | Applied/Not Applied |
| Primitives | Applied/Not Applied |
| Hybrid Durability | Applied/Not Applied |
| The Furnace | Applied/Not Applied |

---

*This document exists-now. [One sentence summary].*
```

---

## Instances of This Primitive

| Document | Type | What It Covers |
|----------|------|----------------|
| `TRUTH_ENGINE_BUSINESS_PLAN.md` | B2C | Personal intelligence product |
| `CREDENTIAL_ATLAS_BUSINESS_PLAN.md` | B2B | AI verification product |

---

## The Meta-Pattern

```
Primitive (this file)
    ↓ instantiate
Instance (specific business plan)
    ↓ extract
Atoms (knowledge atoms)
    ↓ query
Wisdom (answers to questions)
```

---

## How to Create a New Instance

1. Copy the structure above
2. Fill in the brackets with specifics
3. Apply Truth Engine Standards
4. Save to `docs/business/`
5. Add to JSONL intake for atom extraction

---

*This is the primitive. Business plans are instances of this primitive.*

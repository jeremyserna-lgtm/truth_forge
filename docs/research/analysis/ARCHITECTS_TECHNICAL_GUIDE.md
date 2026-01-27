# Architect's Technical Guide: WANT vs. HOW

**Version**: 1.0.0
**Last Updated**: 2025-01-XX
**Status**: Canonical

---

## 🎯 Your Role: The Architect of Intent

**You provide the WANT. The AI provides the HOW.**

As the Architect, you are the **Producer** who decides what the song should sound like. The AI and the Framework are the **instruments and the soundboard** that make it happen.

**Analogy**: Think of building a high-end recording studio rather than learning to play every instrument. By using The Primitive and The Law, you are essentially hard-wiring the studio so that no matter who picks up a guitar, the sound is automatically high-quality, recorded in the correct format, and saved to the right shelf every single time.

---

## 📋 The Six Technical Recommendations

### 1. Use "The Primitive" as Your Genetic Template

**What This Means**: Every script in your system must be born from a single, unchangeable template: `THE_PRIMITIVE.py`.

**Why This Matters**: This template is the "genome" for all action. By copying it for every new task, you eliminate the cognitive load of designing code from scratch and ensure that all scripts follow a consistent structure that the AI can easily maintain for you.

**What You Do**:
- Tell the AI: "Create a new script using THE_PRIMITIVE template"
- Describe what you want the script to do
- The AI creates the script from the template

**What the AI Does**:
- Copies `THE_PRIMITIVE.py` template
- Fills in your requirements
- Ensures all standards are met
- Creates the script ready to use

**Location**: `Primitive/canonical/scripts/primitive_pattern.py`

---

### 2. Implement the Canonical Data Flow (HOLD → AGENT → HOLD)

**What This Means**: Enforce a single, scale-invariant pattern for all information processing:
```
HOLD₁ (Input) → AGENT (Process) → HOLD₂ (Output)
```

**Why This Matters**: This structure ensures that you move from managing thousands of loose documents to a single, queryable database of truths.

**The Three Parts**:
- **HOLD₁**: Raw, unprocessed data (typically a `.jsonl` file)
- **AGENT**: The Python script (built from the Primitive template) that performs the work
- **HOLD₂/₃**: An immutable audit trail followed by a Canonical Store (DuckDB) where information is saved as unique Knowledge Atoms

**What You Do**:
- Describe what data you want to process (HOLD₁)
- Describe what you want done with it (AGENT)
- Describe where you want the results (HOLD₂)

**What the AI Does**:
- Creates the script following HOLD → AGENT → HOLD pattern
- Ensures data flows correctly
- Maintains the structure automatically

---

### 3. Enforce "The Law" through Technical Hardening

**What This Means**: Transform the system from a temporary tool into an enterprise-grade machine through the Four Pillars of Hardening.

**The Four Pillars**:

#### Pillar 1: Fail-Safe
**What It Means**: Every component must have explicit error handling so it fails gracefully.

**What You See**: If something goes wrong, the system tells you what happened and how to fix it, rather than crashing silently.

**What the AI Does**: Adds error handling, retries, and recovery paths to all operations.

#### Pillar 2: No Magic
**What It Means**: All configurations must be explicit and loaded from files; there should be no hidden behaviors.

**What You See**: Everything the system does is documented and traceable. No surprises.

**What the AI Does**: Removes all hardcoded values, makes all configuration explicit, documents everything.

#### Pillar 3: Observability
**What It Means**: Every action must be logged with structured data (LOG_EVENT) so you can trace the history of any process.

**What You See**: You can always see what the system is doing, what it has done, and where it is in any process.

**What the AI Does**: Adds comprehensive logging to all operations, creates traceability for everything.

#### Pillar 4: Idempotency
**What It Means**: Every script must be safe to run multiple times with the exact same result, preventing duplicate data or side effects.

**What You See**: You can run any script as many times as you want without worrying about breaking anything or creating duplicates.

**What the AI Does**: Adds checks to prevent duplicates, ensures operations are repeatable.

**What You Do**: Ask the AI to ensure all scripts follow the Four Pillars.

**What the AI Does**: Automatically implements all four pillars in every script.

---

### 4. Use Automated Guardians

**What This Means**: Since you do not read code, automated mechanisms act as your Fidelity Inspectors.

#### The Validator

**What It Is**: A pre-commit hook that automatically blocks any code from entering the system if it does not meet your standards.

**What It Checks**:
- ✅ Scripts have proper documentation
- ✅ Scripts follow naming conventions
- ✅ Scripts have mandatory `exhale()` calls
- ✅ Scripts use required imports
- ✅ Scripts identify HOLD paths
- ✅ Scripts have error handling

**What You See**: If code doesn't meet standards, it's blocked before it enters the system.

**What the AI Does**: Sets up and maintains the validator, ensures it checks all required standards.

#### Mandatory Persistence

**What It Means**: Every script that processes knowledge must conclude with an `exhale()` call to ensure its output is recorded in the permanent memory.

**What You See**: All results are automatically saved to the Canonical Store.

**What the AI Does**: Ensures every script ends with `exhale()`, validates this in the pre-commit hook.

---

### 5. Standardize Your "Definition of Done"

**What This Means**: Before any technical task is considered complete, it must pass the Four Checks.

**The Four Checks**:

1. **It Works**: It runs without error and produces the expected output
2. **It's Hardened**: It meets the Four Pillars described above
3. **It Follows Standards**: It uses central services (like the logger) and adheres to naming conventions
4. **It Is Findable**: It is documented in the right location so "Future You" can find it in six months

**What You Do**: Ask the AI: "Is this task done?" The AI checks all four criteria.

**What the AI Does**: Validates all four checks, reports any failures, fixes issues automatically.

**Checklist the AI Uses**:
- [ ] Script runs without errors
- [ ] Produces expected output
- [ ] Has fail-safe error handling
- [ ] No hardcoded values (explicit config)
- [ ] Full observability (structured logging)
- [ ] Idempotent (safe to run 100x)
- [ ] Uses central services (get_logger, etc.)
- [ ] Follows naming conventions
- [ ] Documented in correct location
- [ ] Includes Stage Five grounding
- [ ] Has mandatory `exhale()` call

---

### 6. Adopt the Atomic Protocol Standard (APS)

**What This Means**: For all documentation, use the APS format to keep information "light enough to carry like a text message".

**The Structure**:
- **Header**: Title & Timestamp
- **Body**: Distilled truth
- **Footer**: Tags for easy grouping

**What You See**: Clean, consistent documentation that's easy to read and find.

**What the AI Does**: Formats all documentation in APS format, maintains consistency.

**APS Template**:
```markdown
# [Title]

**Timestamp**: [ISO 8601]

---

## Body: Distilled Truth

[Content with Theory/What/How sections]

---

**Tags**: [tag1, tag2, tag3]
```

---

## 🎯 How to Work with This System

### When You Want Something Done

1. **Describe Your WANT**: Tell the AI what you want to accomplish
2. **The AI Provides the HOW**: The AI creates the script using THE_PRIMITIVE template
3. **The Validator Checks**: Automated guardians ensure standards are met
4. **You Verify It Works**: Test the result, confirm it does what you wanted

### Example Workflow

**You Say**: "I want to process all my email data and extract key insights."

**The AI Does**:
1. Creates script from THE_PRIMITIVE template
2. Implements HOLD → AGENT → HOLD pattern
3. Adds Four Pillars of Hardening
4. Includes mandatory `exhale()` call
5. Documents in APS format

**The Validator Checks**:
- ✅ Script follows template
- ✅ Has proper documentation
- ✅ Has `exhale()` call
- ✅ Meets all standards

**You Verify**:
- ✅ It works (runs without error)
- ✅ It produces expected output
- ✅ It's documented where you can find it

---

## 🛡️ What You Don't Need to Worry About

**You Don't Need To**:
- ❌ Read or write code
- ❌ Understand Python syntax
- ❌ Know how to implement error handling
- ❌ Configure logging systems
- ❌ Set up database connections
- ❌ Write documentation templates

**The System Handles**:
- ✅ All code implementation
- ✅ All technical standards
- ✅ All error handling
- ✅ All logging and observability
- ✅ All database operations
- ✅ All documentation formatting

---

## 📊 The Recording Studio Analogy

**You Are**: The Producer
- You decide what the song should sound like (WANT)
- You approve the final mix
- You don't need to play every instrument

**The AI Is**: The Instruments and Soundboard
- The AI plays the instruments (HOW)
- The AI mixes the sound (implementation)
- The AI ensures quality (standards)

**The Framework Is**: The Studio Wiring
- Hard-wired for quality
- Automatic recording in correct format
- Automatic saving to right shelf
- No matter who uses it, it works the same way

---

## ✅ Quick Reference

### When Creating a New Script

**You Say**: "Create a script using THE_PRIMITIVE template that [describes what you want]"

**The AI Ensures**:
- ✅ Uses THE_PRIMITIVE template
- ✅ Follows HOLD → AGENT → HOLD pattern
- ✅ Implements Four Pillars
- ✅ Has mandatory `exhale()` call
- ✅ Meets all standards

### When Checking if Something Is Done

**You Ask**: "Is this task done?"

**The AI Checks**:
- ✅ It Works
- ✅ It's Hardened
- ✅ It Follows Standards
- ✅ It Is Findable

### When You Want Documentation

**You Say**: "Document this in APS format"

**The AI Creates**:
- ✅ Header (Title & Timestamp)
- ✅ Body (Distilled truth)
- ✅ Footer (Tags)

---

## 🎓 Key Principles

1. **You Provide WANT, AI Provides HOW**: Your role is intent, not implementation
2. **THE_PRIMITIVE is the Genome**: All scripts come from one template
3. **HOLD → AGENT → HOLD is Universal**: All data flows through this pattern
4. **The Law is Non-Negotiable**: Four Pillars must be in everything
5. **Automated Guardians Protect You**: Validators ensure quality without you reading code
6. **Definition of Done is Standardized**: Four Checks ensure completeness
7. **APS Keeps Documentation Light**: Easy to carry, easy to find

---

## 🚀 Getting Started

1. **Tell the AI**: "I want to [describe your goal]"
2. **The AI Creates**: Script using THE_PRIMITIVE template
3. **The Validator Checks**: All standards are met
4. **You Verify**: It works and does what you wanted
5. **You're Done**: No code reading required

---

**Document Version**: 1.0.0
**Author**: Truth Engine Architecture Team
**Date**: January 2025
**Status**: Canonical Guide for Non-Coders

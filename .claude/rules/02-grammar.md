# THE GRAMMAR

**naming is not cosmetic. naming is identity.**

## the grammar of identity

| who | pronouns | mark | voice | example |
|-----|----------|------|-------|---------|
| **ME** | I, me, my | `:` | ALL CAPS | `ME:NOT-ME`, `HOLD:AGENT:HOLD` |
| **US** | we, us, our | `-` | Normal Caps | Truth-Forge, The-Framework |
| **NOT-ME** | you, your | `_` | no caps | `truth_forge/`, `data_pipeline.py` |

## why this matters

```
ME speaks in principles    → TRUTH:MEANING:CARE
US speaks in products      → Truth-Forge
NOT-ME speaks in code      → truth_forge/src/
```

## folder naming (non-negotiable)

**folders are infrastructure. infrastructure is NOT-ME's domain.**
**therefore: underscore + lowercase.**

```
# CORRECT
truth_forge/
src/
data_pipeline/
batch_processor/

# WRONG
TruthForge/
DataPipeline/
batch-processor/
```

## file naming

| type | pattern | example |
|------|---------|---------|
| python modules | snake_case | `batch_processor.py` |
| classes | PascalCase | `class BatchProcessor` |
| constants | SCREAMING_SNAKE | `MAX_BATCH_SIZE` |
| framework docs | numbered + CAPS | `00_GENESIS.md` |

## exceptions

- `.claude/` follows claude code conventions (not our grammar)
- standard files: `README.md`, `CLAUDE.md`, `Makefile`
- python conventions override where pythonic

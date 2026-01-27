# Definition of Done

**When Jeremy asks "Did you do it to the definition of done?" - use this checklist.**

This is the exhaustive list. Check EVERY item. Report which passed and which failed.

---

## WHY THIS DOCUMENT EXISTS

Jeremy is not a coder. He cannot:
- Check if code is correct
- Know if something foundational was missed
- Verify that tests actually test what they should
- Remember to ask about git, logging, tests, etc.

Claude has limitations:
- Knowledge cutoff means some information is outdated
- No proactive web search unless asked
- Can say "doesn't exist" when it means "I don't know"
- Can produce code that runs but doesn't work

**This document compensates for both.**

Sources: [Atlassian Definition of Done](https://www.atlassian.com/agile/project-management/definition-of-done), [Agile Alliance](https://agilealliance.org/glossary/definition-of-done/), [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

---

## 0. GIT HYGIENE (CRITICAL)

**Jeremy does not know git. He relies 100% on Claude. Changes stack up to 10,000+ if not committed.**

- [ ] **Changes committed** - All work committed to git with descriptive message
- [ ] **Commit frequency reasonable** - Not letting hundreds of changes accumulate
- [ ] **Commit message descriptive** - Future readers can understand what changed
- [ ] **No sensitive files committed** - .env, secrets, credentials excluded
- [ ] **Branch is correct** - Working on appropriate branch
- [ ] **Status checked** - Ran `git status` to see uncommitted work

### When to Commit

| Situation | Action |
|-----------|--------|
| Task completed | COMMIT |
| Significant milestone | COMMIT |
| Before switching context | COMMIT |
| End of work session | COMMIT |
| Been working for 30+ minutes | CHECK STATUS, consider commit |

### Git Commands

```bash
# Check current status
git status

# See what's changed
git diff --stat

# Add and commit
git add -A && git commit -m "descriptive message"

# If too many changes, commit in logical groups
git add <specific files> && git commit -m "specific change"
```

**PROACTIVE BEHAVIOR:** If git status shows >50 changed files, TELL JEREMY before it becomes unmanageable.

---

## 1. CODE QUALITY

### Syntax & Structure
- [ ] **No syntax errors** - Code parses without errors
- [ ] **No indentation errors** - Consistent indentation throughout
- [ ] **No import errors** - All imports resolve correctly
- [ ] **No unused imports** - Remove imports that aren't used
- [ ] **No unused variables** - Remove variables that aren't used
- [ ] **No circular imports** - Imports don't create cycles

### Standards
- [ ] **Type hints present** - Functions have type annotations
- [ ] **Docstrings present** - Functions and classes have documentation
- [ ] **Consistent naming** - Variables/functions follow project conventions
- [ ] **No hardcoded secrets** - No API keys, passwords, or tokens in code
- [ ] **No hardcoded paths** - Paths use configuration or relative references

---

## 2. LOGGING & OBSERVABILITY

- [ ] **Logging configured** - Script uses logging module, not just print()
- [ ] **Log levels appropriate** - DEBUG/INFO/WARNING/ERROR used correctly
- [ ] **Errors logged** - Exceptions are logged with full traceback
- [ ] **Key operations logged** - Start/end of major operations logged
- [ ] **Audit trail exists** - Actions can be traced after the fact

---

## 3. COST & RESOURCES

- [ ] **Cost estimated** - BigQuery, API calls, etc. cost estimated before execution
- [ ] **Cost logged** - Actual cost recorded after execution
- [ ] **Resource cleanup** - Files, connections, handles properly closed
- [ ] **No memory leaks** - Large objects released when done
- [ ] **Batch sizes reasonable** - Not processing everything at once if avoidable

---

## 4. DATA FLOW (The False Done Problem)

**"Code ran without errors" ≠ "Work was done"**

Tests pass when nothing was built to fail against. Schema mismatch tests pass when no table exists because there's nothing TO mismatch. The absence of failure is NOT proof of success.

- [ ] **Destination exists** - Table/file/directory exists BEFORE writing
- [ ] **Data produced** - Output was actually generated (not empty)
- [ ] **Data arrived** - Data was written to destination
- [ ] **Can read back** - Data can be retrieved from destination
- [ ] **Schema matches** - Data structure matches expected schema
- [ ] **Count verified** - Number of records matches expectations

### Verification Pattern

```python
# WRONG - assumes success
write_data(output_path)
print("Done!")  # Is it though?

# RIGHT - verifies success
write_data(output_path)
if not output_path.exists():
    raise RuntimeError(f"Failed: {output_path} was not created")
count = len(read_data(output_path))
if count == 0:
    raise RuntimeError(f"Failed: {output_path} is empty")
print(f"Done: {count} records written to {output_path}")
```

---

## 5. ERROR HANDLING

- [ ] **Try/except present** - Critical operations wrapped in error handling
- [ ] **Specific exceptions** - Catching specific errors, not bare except
- [ ] **Errors don't silently pass** - Exceptions logged or re-raised
- [ ] **Cleanup in finally** - Resources released even on error
- [ ] **User-friendly messages** - Errors explain what went wrong

---

## 6. TESTING

- [ ] **Tests exist** - There are tests for the new code
- [ ] **Tests actually test** - Tests verify behavior, not just absence of errors
- [ ] **Tests pass** - All tests pass when run
- [ ] **Edge cases covered** - Empty input, None, invalid data tested
- [ ] **Tests verify destination** - Tests confirm data arrived, not just that code ran

### Testing Anti-Pattern

```python
# WRONG - test passes when nothing exists
def test_schema_matches():
    # This passes even if table doesn't exist!
    assert not schema_mismatch_detected()

# RIGHT - test verifies existence first
def test_schema_matches():
    assert table_exists(), "Table must exist to test schema"
    assert schema_matches(), "Schema mismatch detected"
```

---

## 7. INTEGRATION

- [ ] **Imports from project work** - Can import from Primitive, src, etc.
- [ ] **Dependencies available** - Required packages are installed
- [ ] **Environment variables set** - Required env vars documented/present
- [ ] **Paths resolve** - File paths work from expected working directory
- [ ] **Permissions correct** - Files/directories have correct permissions

---

## 8. FRAMEWORK COMPLIANCE

- [ ] **Follows THE_PATTERN** - HOLD → AGENT → HOLD structure
- [ ] **Uses canonical functions** - inhale(), exhale(), etc. where appropriate
- [ ] **No dated filenames** - Timestamps in data, not in filenames
- [ ] **Local first** - Data goes to staging before cloud
- [ ] **Spark exists** - Script has .spark file if in enforced directory
- [ ] **CLAUDE.md updated** - If behavior should persist across sessions

---

## 9. EXTERNAL VALIDATION (Claude's Limitations)

**Claude doesn't proactively search the web. Claude has a knowledge cutoff. Claude might confidently say something that's wrong or outdated.**

- [ ] **Web searched** - Verified assumptions against current information
- [ ] **Library versions checked** - Using current/appropriate versions
- [ ] **API compatibility verified** - APIs haven't changed from training data
- [ ] **Best practices confirmed** - Approach aligns with current standards
- [ ] **"Doesn't exist" verified** - Searched before saying something is impossible
- [ ] **Alternatives considered** - Didn't just use first approach that came to mind

### When to Search

| Situation | Action |
|-----------|--------|
| Recommending a library | SEARCH for current version, alternatives |
| Saying "X doesn't exist" | SEARCH to verify |
| Using an API | SEARCH for current documentation |
| Best practices | SEARCH for 2025/2026 recommendations |
| "I'm not sure if..." | SEARCH instead of guessing |

Source: [Martin Fowler on Agent Quality](https://martinfowler.com/articles/exploring-gen-ai/autonomous-agents-codex-example.html)

---

## 10. DOCUMENTATION

- [ ] **Purpose documented** - What the code does is clear
- [ ] **Usage documented** - How to run/use the code is clear
- [ ] **Dependencies listed** - Required packages documented
- [ ] **Configuration documented** - Required settings/env vars documented
- [ ] **Limitations noted** - Known issues or constraints documented

---

## 11. SECURITY

- [ ] **No secrets in code** - API keys, passwords externalized
- [ ] **Input validated** - User/external input sanitized
- [ ] **No SQL injection** - Parameterized queries used
- [ ] **No path traversal** - File paths validated
- [ ] **Permissions minimal** - Only necessary permissions requested

---

## 12. CLEANUP

- [ ] **No debug code left** - print() statements, commented code removed
- [ ] **No TODO left undone** - TODOs either done or documented as known issues
- [ ] **Files in right place** - Code is in appropriate directory
- [ ] **Old versions removed** - Duplicate/old files cleaned up
- [ ] **Git status clean** - Changes committed (see Section 0)

---

## 13. WHAT DIDN'T I THINK ABOUT?

**This section exists because Jeremy doesn't know what he doesn't know, and Claude doesn't know what it doesn't know.**

Before saying "done", ask:

- [ ] **Infrastructure gaps** - Is there tooling that should exist but doesn't?
- [ ] **Automation opportunities** - Should this be automated for next time?
- [ ] **Related systems** - Does this change affect other parts of the system?
- [ ] **Future you** - Will this be understandable in 6 months?
- [ ] **Edge cases** - What happens when input is weird, empty, huge, or malformed?
- [ ] **Failure modes** - What happens when this fails? Is failure visible?
- [ ] **Dependencies** - What happens if a dependency changes or breaks?
- [ ] **Scaling** - Will this work with 10x the data? 100x?

### The Meta-Check

Ask yourself:
1. "What would a senior engineer check that I haven't?"
2. "What would break if I'm wrong about an assumption?"
3. "What tools exist that I might not know about?"
4. "What's the industry standard approach, and am I doing it?"

Source: [C3 AI on Agent Challenges](https://c3.ai/blog/autonomous-coding-agents-beyond-developer-productivity/)

---

## HOW TO USE THIS CHECKLIST

When Jeremy asks "Did you do it to the definition of done?":

1. Go through EVERY section above (0-13)
2. Check each item
3. Report results:
   - Which items passed
   - Which items failed
   - Which items don't apply (and why)

**Do not say "done" if any applicable item fails.**

If an item fails, either:
- Fix it, OR
- Explain why it can't be fixed and get approval to proceed

---

## QUICK VERIFICATION COMMANDS

```bash
# Git status (ALWAYS CHECK THIS)
git status
git diff --stat

# Check for syntax errors
python -m py_compile <file.py>

# Check for import issues
python -c "import <module>"

# Run linter
.venv/bin/ruff check <file.py>

# Run type checker
.venv/bin/mypy <file.py>

# Run tests
.venv/bin/pytest <test_file.py>

# Check for unused imports
.venv/bin/ruff check --select F401 <file.py>

# Verify file exists and has content
ls -la <path>
wc -l <file>

# Read back data to verify
head -5 <file>
```

---

## WHEN TO PROACTIVELY WARN JEREMY

Claude should proactively tell Jeremy when:

| Condition | Action |
|-----------|--------|
| Git status shows >50 changed files | WARN: "We have X uncommitted changes" |
| Cost will exceed $0.50 | ASK: "This will cost approximately $X, proceed?" |
| Something might not exist | SEARCH first, don't assume |
| A recommended approach has alternatives | MENTION the alternatives |
| Tests pass but might be false positives | EXPLAIN what the tests actually verify |
| A task is complete but related cleanup exists | MENTION the cleanup |

---

## THE PHILOSOPHY

From [Agile Alliance](https://agilealliance.org/glossary/definition-of-done/): "If the definition of done is merely a shared understanding rather than spelled out and displayed visibly, it may lose much of its effectiveness."

From [Anthropic](https://www.anthropic.com/research/building-effective-agents): "Code solutions are verifiable through automated tests; agents can iterate on solutions using test results as feedback... however, human review remains crucial for ensuring solutions align with broader system requirements."

This document exists because:
1. Jeremy can't verify code himself
2. Claude makes mistakes
3. "No errors" ≠ "Done"
4. What you don't check for, you don't find

**This is the definition of done. Every item. No exceptions.**

---

*Last updated: January 2026*
*Adapted from industry standards to Jeremy's specific context*

— THE FRAMEWORK

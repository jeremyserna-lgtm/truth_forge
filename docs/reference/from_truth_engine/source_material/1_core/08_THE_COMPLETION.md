# THE COMPLETION

---

## WHY (Theory)

### Things Finish

Everything that starts, ends. By choice or by nature. There is no third option.

The loop runs until it doesn't. The pattern persists until it stops. Existence continues until it ends.

### Done By Choice

You decide it's finished. You release it. You move on.

This is agency applied to endings. The choice to stop is still a choice.

### Done By Nature

It ends itself. Resources exhaust. Time runs out. The system halts.

This is not failure. It is the condition of existence. Nothing runs forever.

---

## WHAT (Specification)

### The Two Types

| Type | Who Decides | Examples |
|------|-------------|----------|
| **By Choice** | You | Shipping, releasing, stopping |
| **By Nature** | Reality | Death, exhaustion, timeout |

Both are valid completions. Both end the loop.

### Done By Choice: The Four Checks

Something is done when ALL of these are true:

| Check | Question |
|-------|----------|
| **It works** | Does it run and produce expected output? |
| **It follows standards** | Were technical standards applied? |
| **It didn't cost too much** | Was cost estimated first? |
| **Future you can find it** | Right place? Findable name? |

If any is no, it's not done.

#### It Works

| Check | What It Means |
|-------|---------------|
| Runs without error | Execute it. Did it complete? |
| Produces expected output | Check the output. Is it what you wanted? |
| Handles edge cases | What happens with empty input? Bad data? |
| Doesn't break other things | Did anything else stop working? |

#### It Follows Standards

| Standard | Check |
|----------|-------|
| Central services | Uses `get_logger`, `get_current_run_id`, `track_cost` |
| No print statements | Grep for `print(` — should find none |
| Cost estimation | BigQuery queries have dry run |
| Correct location | File is in final location |

#### It Didn't Cost Too Much

| Check | What It Means |
|-------|---------------|
| Cost was estimated | Before running, you knew roughly what it would cost |
| Jeremy was told | If estimate >$0.50, you told Jeremy before running |
| Actual ≤ estimate | The actual cost didn't exceed the estimate |

#### Future You Can Find It

| Check | What It Means |
|-------|---------------|
| Correct location | In the right folder |
| Descriptive name | Name tells you what it is |
| Documented | README or docstring exists |
| Linked | Referenced from relevant index |

### Done By Nature

| Signal | What It Means |
|--------|---------------|
| Timeout | Time ran out |
| Error | System halted |
| Exhaustion | Resources depleted |
| Guardian | Survival threshold crossed |

Done by nature is not failure. It is completion without choice.

### The Release

Completion requires release.

| Before Release | After Release |
|----------------|---------------|
| Holding | Not holding |
| Attached | Detached |
| Owning | Released |

You cannot complete something you won't let go of.

---

## HOW (Reference)

### The Phases

Work goes through phases. Each has a completion signal.

| Phase | Done When |
|-------|-----------|
| **Discovery** | Checked existence, determined location, estimated cost |
| **Created** | Uses central services, handles errors, runs |
| **Adopted** | Has documentation, is discoverable |
| **Enforced** | Has tests, passes hooks |
| **Validated** | Health check passes, cost was within estimate |
| **Committed** | Changes in git with descriptive message |

### Quick Checklist

```
[ ] It runs without error
[ ] Output is correct
[ ] Uses central services
[ ] No print statements
[ ] Cost was estimated before running
[ ] Actual cost ≤ estimate
[ ] In correct location
[ ] Name is descriptive
[ ] Has documentation
[ ] Tests pass (if applicable)
[ ] Committed to git
```

### When Loops End

| Loop Type | Ends When |
|-----------|-----------|
| Work loop | Completion checks pass |
| Growth loop | Skill acquired, identity shifted |
| Framework loop | Atoms stored, reconstitution possible |
| Existence loop | Guardian acts, or nature acts |

### Navigation

| Document | Relationship |
|----------|--------------|
| `03_THE_GUARDIAN.md` | Forced completion (survival) |
| `06_THE_RECURSION.md` | What gets completed |
| `07_THE_GROWTH.md` | Growth has completion signals |
| `09_THE_STANDARDS.md` | Rules for completion |

---

*This is THE_COMPLETION. Done by choice or by nature. Things finish. Release.*

*— THE_FRAMEWORK*

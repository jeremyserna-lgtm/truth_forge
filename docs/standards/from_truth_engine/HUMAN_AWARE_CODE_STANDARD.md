# Human-Aware Code Standard

**Version**: 1.0.0
**Status**: SPECIFICATION
**Author**: Jeremy Serna / Credential Atlas
**Date**: January 23, 2026
**License**: Open Standard (CC BY 4.0)

---

## Abstract

The Human-Aware Code Standard defines requirements for code that considers what non-coder humans experience when interacting with software. It shifts the perspective from "does the code work?" to "does the human know what's happening?"

**The core insight**: The human is not a coder. They will be staring at the screen. Code that abandons them at failure is not complete code.

---

## 1. The Problem

### 1.1 Code Written for Coders

Most code assumes the user can:
- Read error messages and understand them
- Check logs to diagnose problems
- Modify code to add debugging
- Understand what "timeout" or "connection refused" means

### 1.2 The Reality

Most users:
- Cannot read code or logs
- Don't know what technical errors mean
- Can't diagnose problems themselves
- Will stare at the screen wondering what happened
- Have no idea if they should wait, restart, or give up

### 1.3 The Failure Mode

```
AI writes code with:
├── No timeout         → Human waits forever
├── No progress        → Human doesn't know if it's working
├── Technical errors   → Human doesn't understand
├── No recovery path   → Human can't fix it
└── Silent failure     → Human doesn't know it broke

Result: Human staring at screen, helpless, abandoned.
```

---

## 2. The Human-Aware Principle

### 2.1 The Core Question

Before writing ANY code, ask:

> "If I (a non-coder) ran this code and something went wrong, would I know:
> 1. That something went wrong?
> 2. What went wrong?
> 3. What I can do about it?
>
> Or would I just be staring at a screen wondering what happened?"

**If the answer is "staring at a screen" → the code is not done.**

### 2.2 The Five Questions

Every code block must answer these questions:

| Question | What It Means |
|----------|---------------|
| **What does the human see?** | Is there visible feedback during operation? |
| **What if it hangs?** | Is there a timeout? What happens when it fires? |
| **What if it fails?** | Is there an error message a non-coder can understand? |
| **What if it partially fails?** | Is there a circuit breaker? Graceful degradation? |
| **What if they don't know what happened?** | Is there logging they can show someone who CAN help? |

---

## 3. Requirements

### 3.1 Visibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Progress indication** | Any operation >2 seconds shows progress |
| **State communication** | User knows what the system is doing |
| **Completion notification** | User knows when operation is done |
| **Status persistence** | Status is available after operation completes |

### 3.2 Timeout Requirements

| Requirement | Implementation |
|-------------|----------------|
| **All I/O has timeout** | No unbounded waits |
| **Timeout message is human-readable** | Not just "TimeoutError" |
| **Timeout includes guidance** | Tell them what to do |
| **Timeout is configurable** | Can be adjusted for context |

### 3.3 Error Message Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Plain language** | Not stack traces as primary message |
| **What happened** | Describe the problem |
| **What it means** | Explain impact |
| **What to do** | Provide actionable guidance |
| **Who to contact** | If they can't fix it, who can? |

### 3.4 Recovery Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Circuit breakers** | Fail gracefully under load |
| **Retries with backoff** | Automatic recovery attempts |
| **Fallback behavior** | What happens when primary fails |
| **State preservation** | Don't lose work on failure |

---

## 4. Implementation Patterns

### 4.1 Progress Indication

```python
# BAD: Silent operation
def process_files(files):
    for file in files:
        process(file)

# GOOD: Human-aware operation
def process_files(files):
    total = len(files)
    print(f"Processing {total} files...")

    for i, file in enumerate(files, 1):
        print(f"  [{i}/{total}] Processing {file.name}...", end="", flush=True)
        try:
            process(file)
            print(" done")
        except Exception as e:
            print(f" FAILED: {e}")

    print(f"Completed processing {total} files.")
```

### 4.2 Timeout with Human Message

```python
# BAD: Raw timeout
response = requests.get(url, timeout=30)

# GOOD: Human-aware timeout
try:
    print(f"Connecting to service...")
    response = requests.get(url, timeout=30)
    print(f"Connected successfully.")
except requests.Timeout:
    print("""
    The service took too long to respond.

    This usually means:
    • The service is temporarily overloaded
    • Your internet connection is slow
    • The service might be down

    What you can do:
    • Wait a few minutes and try again
    • Check your internet connection
    • Contact support if this persists

    Technical details saved to: /tmp/timeout_log.txt
    """)
    raise
```

### 4.3 Human-Readable Errors

```python
# BAD: Technical error
raise ValueError(f"Schema mismatch: expected {expected}, got {actual}")

# GOOD: Human-readable error
class HumanReadableError(Exception):
    def __init__(self, what_happened, what_it_means, what_to_do, technical_details=None):
        self.what_happened = what_happened
        self.what_it_means = what_it_means
        self.what_to_do = what_to_do
        self.technical_details = technical_details

        message = f"""
Something went wrong.

WHAT HAPPENED:
{what_happened}

WHAT THIS MEANS:
{what_it_means}

WHAT YOU CAN DO:
{what_to_do}
"""
        if technical_details:
            message += f"""
TECHNICAL DETAILS (for support):
{technical_details}
"""
        super().__init__(message)

# Usage
raise HumanReadableError(
    what_happened="The database structure doesn't match what the program expected.",
    what_it_means="Your data is safe, but the program can't read it in its current format.",
    what_to_do="This usually fixes itself if you restart the program. If it doesn't, contact support.",
    technical_details=f"Schema mismatch: expected {expected}, got {actual}"
)
```

### 4.4 Circuit Breaker Pattern

```python
class HumanAwareCircuitBreaker:
    """Circuit breaker that tells humans what's happening."""

    def __init__(self, name: str, max_failures: int = 3, reset_timeout: int = 60):
        self.name = name
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._should_try_reset():
                self.state = "half-open"
                print(f"[{self.name}] Trying to reconnect...")
            else:
                remaining = self._time_until_reset()
                print(f"""
[{self.name}] Service temporarily unavailable.

The system is protecting itself from repeated failures.
It will automatically try again in {remaining} seconds.

You don't need to do anything - just wait.
""")
                raise CircuitOpenError(self.name, remaining)

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            raise

    def _record_success(self):
        self.failures = 0
        if self.state == "half-open":
            print(f"[{self.name}] Reconnected successfully!")
        self.state = "closed"

    def _record_failure(self, error):
        self.failures += 1
        self.last_failure = time.time()

        if self.failures >= self.max_failures:
            self.state = "open"
            print(f"""
[{self.name}] Service is having problems.

The system tried {self.max_failures} times but couldn't connect.
It will automatically retry in {self.reset_timeout} seconds.

What happened: {error}
""")
```

### 4.5 Complete Human-Aware Function Template

```python
def human_aware_operation(input_data, config=None):
    """
    Template for human-aware operations.

    Every operation should follow this pattern.
    """
    config = config or {}
    timeout = config.get("timeout", 30)
    retries = config.get("retries", 3)

    # 1. Tell human what we're starting
    print(f"Starting operation...")
    print(f"  Input: {describe_input(input_data)}")

    # 2. Track progress
    start_time = time.time()

    for attempt in range(1, retries + 1):
        try:
            # 3. Show attempt status
            if attempt > 1:
                print(f"  Retry {attempt}/{retries}...")

            # 4. Do the work with timeout
            print(f"  Processing...", end="", flush=True)
            result = do_work_with_timeout(input_data, timeout)
            print(" done")

            # 5. Report success
            elapsed = time.time() - start_time
            print(f"Operation completed in {elapsed:.1f} seconds.")
            return result

        except TimeoutError:
            print(f" timed out after {timeout}s")
            if attempt == retries:
                print(human_timeout_message(timeout))
                raise

        except ConnectionError as e:
            print(f" connection failed")
            if attempt == retries:
                print(human_connection_message(e))
                raise

        except Exception as e:
            print(f" failed: {e}")
            if attempt == retries:
                print(human_generic_error_message(e))
                raise

        # Wait before retry
        wait_time = 2 ** attempt
        print(f"  Waiting {wait_time}s before retry...")
        time.sleep(wait_time)

def human_timeout_message(timeout):
    return f"""
The operation took longer than {timeout} seconds and was stopped.

This usually means:
• The service is slow or overloaded
• Your data is very large
• There's a network problem

What you can do:
• Try again in a few minutes
• Check if the service is working at [status page]
• Try with a smaller amount of data

If this keeps happening, contact support with this log.
"""

def human_connection_message(error):
    return f"""
Couldn't connect to the service.

This usually means:
• The service is temporarily down
• Your internet connection has a problem
• A firewall is blocking the connection

What you can do:
• Check your internet connection
• Try again in a few minutes
• Check the service status at [status page]

Technical details: {error}
"""

def human_generic_error_message(error):
    return f"""
Something unexpected went wrong.

The program encountered a problem it doesn't know how to handle.

What you can do:
• Try running the program again
• If it keeps failing, contact support

Please include this information when contacting support:
Error type: {type(error).__name__}
Error message: {error}
Time: {datetime.now().isoformat()}
"""
```

---

## 5. Linter Specification

### 5.1 Rules

```python
HUMAN_AWARE_RULES = [
    {
        "id": "HAC001",
        "name": "no-silent-io",
        "description": "I/O operations must have visible feedback",
        "pattern": "requests.get|requests.post|open\\(|subprocess",
        "check": "must have print statement within 3 lines before"
    },
    {
        "id": "HAC002",
        "name": "require-timeout",
        "description": "Network operations must have timeout",
        "pattern": "requests\\.(get|post|put|delete)",
        "check": "must include timeout= parameter"
    },
    {
        "id": "HAC003",
        "name": "no-bare-except",
        "description": "Exceptions must have human message",
        "pattern": "except.*:",
        "check": "must have print or raise with message"
    },
    {
        "id": "HAC004",
        "name": "no-technical-only-error",
        "description": "Errors must include human guidance",
        "pattern": "raise \\w+Error",
        "check": "message must include 'what you can do' or similar"
    },
    {
        "id": "HAC005",
        "name": "long-operation-progress",
        "description": "Loops must show progress",
        "pattern": "for .* in .*:",
        "check": "must have progress indication if >10 iterations"
    },
]
```

### 5.2 Linter Implementation

```python
import ast
import re
from dataclasses import dataclass
from typing import List

@dataclass
class LintViolation:
    rule_id: str
    rule_name: str
    line: int
    column: int
    message: str
    suggestion: str

class HumanAwareLinter:
    """Lint code for human-awareness."""

    def __init__(self):
        self.violations = []

    def lint_file(self, filepath: str) -> List[LintViolation]:
        """Lint a Python file for human-awareness."""
        with open(filepath) as f:
            source = f.read()

        self.violations = []

        # Parse AST
        tree = ast.parse(source)

        # Run checks
        self._check_timeout(tree, source)
        self._check_progress(tree, source)
        self._check_error_messages(tree, source)
        self._check_io_feedback(tree, source)

        return self.violations

    def _check_timeout(self, tree, source):
        """Check that network calls have timeout."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_network_call(node):
                    if not self._has_timeout_arg(node):
                        self.violations.append(LintViolation(
                            rule_id="HAC002",
                            rule_name="require-timeout",
                            line=node.lineno,
                            column=node.col_offset,
                            message="Network call without timeout",
                            suggestion="Add timeout parameter: timeout=30"
                        ))

    def _check_progress(self, tree, source):
        """Check that long loops have progress indication."""
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if loop body has progress indication
                has_progress = any(
                    self._is_progress_call(child)
                    for child in ast.walk(node)
                )
                if not has_progress:
                    self.violations.append(LintViolation(
                        rule_id="HAC005",
                        rule_name="long-operation-progress",
                        line=node.lineno,
                        column=node.col_offset,
                        message="Loop without progress indication",
                        suggestion="Add print statement showing progress"
                    ))

    def _check_error_messages(self, tree, source):
        """Check that errors have human-readable messages."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                if node.exc and isinstance(node.exc, ast.Call):
                    # Check if message includes guidance
                    if not self._has_human_guidance(node.exc):
                        self.violations.append(LintViolation(
                            rule_id="HAC004",
                            rule_name="no-technical-only-error",
                            line=node.lineno,
                            column=node.col_offset,
                            message="Error without human guidance",
                            suggestion="Include 'What you can do:' in error message"
                        ))
```

---

## 6. Testing Protocol

### 6.1 Human-Awareness Tests

```python
import pytest

class TestHumanAwareness:
    """Test that code is human-aware."""

    def test_shows_progress_for_long_operations(self, capsys):
        """Verify progress is shown."""
        process_large_dataset(test_data)
        captured = capsys.readouterr()

        assert "Processing" in captured.out
        assert "/" in captured.out  # Shows progress like "1/10"

    def test_timeout_has_human_message(self):
        """Verify timeout produces human-readable message."""
        with pytest.raises(TimeoutError) as exc_info:
            operation_that_times_out()

        message = str(exc_info.value)
        assert "what you can do" in message.lower()

    def test_errors_include_guidance(self):
        """Verify errors tell humans what to do."""
        with pytest.raises(Exception) as exc_info:
            operation_that_fails()

        message = str(exc_info.value)
        assert any(phrase in message.lower() for phrase in [
            "what you can do",
            "try again",
            "contact support",
        ])

    def test_no_silent_failures(self, capsys):
        """Verify failures produce visible output."""
        try:
            operation_that_fails()
        except:
            pass

        captured = capsys.readouterr()
        assert captured.out or captured.err  # Something was printed
```

---

## 7. Compliance Levels

### 7.1 Levels

| Level | Requirements | Badge |
|-------|--------------|-------|
| **Bronze** | Timeouts on I/O, basic error messages | "Human-Considered" |
| **Silver** | Progress on long ops, guidance in errors | "Human-Aware" |
| **Gold** | Full circuit breakers, complete recovery paths | "Human-First" |

### 7.2 Certification

```yaml
# human-aware-certification.yml
level: gold
verified_date: 2026-01-23
checks_passed:
  - HAC001: no-silent-io
  - HAC002: require-timeout
  - HAC003: no-bare-except
  - HAC004: no-technical-only-error
  - HAC005: long-operation-progress
  - HAC006: circuit-breakers
  - HAC007: recovery-paths
  - HAC008: state-preservation
```

---

## 8. Appendix: Quick Reference

### The Five Questions

```
1. What does the human see?
2. What if it hangs?
3. What if it fails?
4. What if it partially fails?
5. What if they don't know what happened?
```

### Error Message Template

```
WHAT HAPPENED:
[Plain language description]

WHAT THIS MEANS:
[Impact on the user]

WHAT YOU CAN DO:
[Actionable steps]

TECHNICAL DETAILS (for support):
[Technical information]
```

### The Litmus Test

```
If the answer to "what does the human experience?" is
"staring at a screen wondering what happened"
→ the code is not done.
```

---

## License

This standard is released under Creative Commons Attribution 4.0 International (CC BY 4.0).

---

*"The human is not a coder. They will be staring at the screen."*

— Human-Aware Code Standard v1.0.0, January 23, 2026


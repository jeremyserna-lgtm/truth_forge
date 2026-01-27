# Protection Mechanisms - Complete Reference

**Created**: 2025-12-27
**Author**: Claude Code
**Purpose**: Document every protection mechanism that exists and how it applies to Truth Engine
**Status**: REFERENCE DOCUMENT

---

## Overview

Protection mechanisms exist at multiple layers. Each layer catches different problems at different times. No single layer is sufficient - they work together.

```
┌─────────────────────────────────────────────────────────────┐
│                    PROTECTION STACK                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 10: COST PROTECTION (billing guardian)               │  ← Stops spending
│  Layer 9:  MONITORING (logs, alerts, dashboards)            │  ← Sees problems
│  Layer 8:  CLOUD PERMISSIONS (IAM, service accounts)        │  ← Who can do what
│  Layer 7:  DATABASE CONSTRAINTS (schema, validation)        │  ← Bad data rejected
│  Layer 6:  CI/CD PIPELINE (automated checks on push)        │  ← Blocks bad merges
│  Layer 5:  TESTING (unit tests, integration tests)          │  ← Catches broken logic
│  Layer 4:  RUNTIME PROTECTION (Python patches)              │  ← Blocks bad execution
│  Layer 3:  PRE-COMMIT HOOKS (git hooks)                     │  ← Blocks bad commits
│  Layer 2:  AI AGENT ENFORCEMENT (Claude hooks, rules)       │  ← Shapes AI behavior
│  Layer 1:  CODE QUALITY (linters, formatters, type check)   │  ← Basic hygiene
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Code Quality Tools

### What They Are

Tools that check code for formatting, style, and basic errors. They run before code is committed.

### Tools Available

| Tool | What It Does | How It Works |
|------|--------------|--------------|
| **black** | Code formatter | Reformats Python to consistent style |
| **isort** | Import sorter | Orders imports consistently |
| **flake8** | Linter | Catches style violations, unused imports |
| **pylint** | Advanced linter | Catches more complex issues, gives score |
| **mypy** | Type checker | Catches type mismatches |

### How They Work

```bash
# black reformats code
black my_file.py

# flake8 reports issues
flake8 my_file.py
# Output: my_file.py:10:1: E302 expected 2 blank lines, found 1

# mypy checks types
mypy my_file.py
# Output: my_file.py:15: error: Argument 1 has incompatible type "str"; expected "int"
```

### Current State in Truth Engine

| Tool | Status | Where Configured |
|------|--------|------------------|
| black | ✅ Installed | `pyproject.toml` |
| isort | ✅ Installed | `pyproject.toml` |
| flake8 | ✅ Installed | `.flake8` or `setup.cfg` |
| pylint | ⚠️ Installed, not enforced | - |
| mypy | ⚠️ Installed, not enforced | - |

### What's Missing

- mypy not enforced (type errors not blocked)
- pylint threshold not enforced (code quality score not required)

### How to Fix

```toml
# In pyproject.toml or setup.cfg
[tool.mypy]
strict = true
warn_return_any = true

# In pre-commit config
- repo: https://github.com/pre-commit/mirrors-mypy
  hooks:
  - id: mypy
    args: [--strict]
```

---

## Layer 2: AI Agent Enforcement

### What It Is

Systems that shape AI agent (Claude Code, Cursor, Copilot) behavior before they write code.

### Components

| Component | What It Does | Where It Lives |
|-----------|--------------|----------------|
| **CLAUDE.md** | Identity and operating instructions | Root + `~/.claude/` |
| **Rules** | Behavioral patterns (7 files) | `.claude/rules/` |
| **Commands** | User-invoked behaviors (18) | `~/.claude/commands/` |
| **Skills** | Claude-proposed behaviors (4) | `~/.claude/skills/` |
| **Hooks** | Tool call interception (11) | `.claude/hooks.json` |

### How Hooks Work

```json
// .claude/hooks.json
{
  "hooks": [
    {
      "event": "pre_tool_call",
      "tools": ["Edit", "Write"],
      "command": "python3 bin/hooks/check_script_central_services.py",
      "blocking": true
    }
  ]
}
```

**Flow:**
1. Claude Code is about to call `Edit` tool
2. Hook script runs BEFORE the edit
3. Script checks if edit violates rules
4. If script returns non-zero, edit is BLOCKED
5. If script returns zero, edit proceeds

### Current State in Truth Engine

| Component | Count | Status |
|-----------|-------|--------|
| CLAUDE.md | 2 | ✅ Active |
| Rules | 7 | ✅ Active |
| Commands | 18 | ✅ Active |
| Skills | 4 | ✅ Active |
| Hooks | 11 | ✅ Active |

### What's Missing

- Hook to scan Edit/Write content for forbidden patterns
- Pattern: `insert_rows_json`, `bigquery.Client()`, `CREATE TABLE` without `CLUSTER`

### How to Fix

Add to `.claude/hooks.json`:
```json
{
  "event": "pre_tool_call",
  "tools": ["Edit", "Write"],
  "command": "python3 bin/hooks/block_forbidden_patterns.py",
  "blocking": true
}
```

Create `bin/hooks/block_forbidden_patterns.py`:
```python
#!/usr/bin/env python3
"""Block forbidden patterns in code being written."""
import sys
import re
import json

FORBIDDEN_PATTERNS = [
    (r"insert_rows_json", "Use batch load instead of streaming insert"),
    (r"bigquery\.Client\(\)", "Use get_bigquery_client() instead"),
    (r"CREATE TABLE(?!.*CLUSTER)", "Tables must have CLUSTER BY clause"),
]

def check_content(content: str) -> list[str]:
    errors = []
    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(f"FORBIDDEN: {message}")
    return errors

def main():
    # Read tool input from stdin
    input_data = json.load(sys.stdin)
    content = input_data.get("content", "") or input_data.get("new_string", "")

    errors = check_content(content)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Layer 3: Pre-Commit Hooks

### What They Are

Git hooks that run before every commit. They check code quality and block commits that fail.

### How They Work

```bash
# When you run git commit, this happens:
git commit -m "My changes"

# 1. Pre-commit hooks run
# 2. Each hook checks the staged files
# 3. If ANY hook fails, commit is BLOCKED
# 4. You must fix issues and try again
```

### Configuration

Pre-commit hooks are configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: check-central-services
        name: Check Central Services
        entry: python3 bin/hooks/check_script_central_services.py
        language: system
        files: \.py$
```

### Current State in Truth Engine

| Hook | Status | What It Checks |
|------|--------|----------------|
| black | ✅ Active | Code formatting |
| isort | ✅ Active | Import order |
| flake8 | ✅ Active | Linting |
| check-central-services | ✅ Active | Required imports |
| validate-syntax | ⚠️ Unknown | Python syntax |

### What's Missing

- Syntax validation hook (to catch mass-edit errors)
- Forbidden pattern scanner
- BigQuery pattern checker

### How to Fix

Add to `.pre-commit-config.yaml`:
```yaml
  - repo: local
    hooks:
      - id: validate-syntax
        name: Validate Python Syntax
        entry: python3 -m py_compile
        language: system
        files: \.py$

      - id: forbidden-patterns
        name: Check Forbidden Patterns
        entry: python3 bin/hooks/block_forbidden_patterns.py
        language: system
        files: \.py$
```

---

## Layer 4: Runtime Protection

### What It Is

Python code that patches functions/classes at import time to prevent forbidden operations.

### How It Works

```python
# When architect_central_services is imported, this runs:

def _patch_bigquery_client():
    """Block direct BigQuery client creation."""
    from google.cloud import bigquery

    original_init = bigquery.Client.__init__

    def protected_init(self, *args, **kwargs):
        # Check if caller is using approved wrapper
        import inspect
        caller = inspect.stack()[1]

        # Allow only approved callers
        if "get_bigquery_client" not in caller.filename:
            raise RuntimeError(
                "BLOCKED: Direct BigQuery client creation. "
                "Use get_bigquery_client() from architect_central_services."
            )
        return original_init(self, *args, **kwargs)

    bigquery.Client.__init__ = protected_init

# This runs at import time
_patch_bigquery_client()
```

**Effect:** Any code that tries `bigquery.Client()` directly gets an error.

### Current State in Truth Engine

| Protection | Status | Location |
|------------|--------|----------|
| BigQuery client | ⚠️ Partial | Needs verification |
| Gemini client | ⚠️ Partial | Needs verification |
| Streaming insert | ❌ Missing | Not implemented |

### What's Missing

Block `insert_rows_json` at runtime:

```python
def _block_streaming_insert():
    """Block streaming inserts - use batch load instead."""
    from google.cloud import bigquery

    def blocked_method(*args, **kwargs):
        raise RuntimeError(
            "BLOCKED: insert_rows_json (streaming insert) is forbidden. "
            "Use load_table_from_file with LoadJobConfig instead. "
            "See 02-bigquery-patterns.md"
        )

    bigquery.Client.insert_rows_json = blocked_method
    bigquery.Client.insert_rows = blocked_method  # Also block this variant

_block_streaming_insert()
```

### Where This Lives

`architect_central_services/src/architect_central_services/governance/agent_monitor/runtime_protection.py`

This file should be imported early in the package's `__init__.py`.

---

## Layer 5: Testing

### What It Is

Code that verifies other code works correctly.

### Types of Tests

| Type | What It Tests | When It Runs |
|------|---------------|--------------|
| **Unit tests** | Individual functions | `pytest` command |
| **Integration tests** | Multiple components together | `pytest` with markers |
| **End-to-end tests** | Full workflows | Manual or CI |

### How Tests Work

```python
# tests/test_identity_service.py

def test_generate_contact_id():
    """Test that contact IDs have correct format."""
    from architect_central_services import generate_contact_id

    contact_id = generate_contact_id()

    assert contact_id.startswith("cnt_")
    assert len(contact_id) == 12  # cnt_ + 8 chars
```

```bash
# Run tests
pytest tests/
pytest tests/test_identity_service.py -v
pytest --cov=architect_central_services  # With coverage
```

### Current State in Truth Engine

| Metric | Value | Target |
|--------|-------|--------|
| Test files | ~20 | - |
| Test coverage | Unknown | 80%+ |
| Tests passing | Unknown | 100% |

### What's Missing

- Coverage measurement not enforced
- No required coverage threshold
- Many modules lack tests

### How to Fix

```bash
# Add to pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=architect_central_services --cov-fail-under=80"

# Add to CI pipeline
- name: Run tests
  run: pytest --cov=architect_central_services --cov-fail-under=80
```

---

## Layer 6: CI/CD Pipeline

### What It Is

Automated checks that run on every push or pull request. If checks fail, the code can't be merged.

### How It Works

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint
        run: |
          black --check .
          flake8 .
          mypy .

      - name: Test
        run: pytest --cov=architect_central_services --cov-fail-under=80
```

### Current State in Truth Engine

| Component | Status |
|-----------|--------|
| GitHub Actions workflow | ❌ Not set up |
| Automated linting | ❌ Not set up |
| Automated testing | ❌ Not set up |
| Branch protection | ❓ Unknown |

### What's Missing

Everything. No CI/CD pipeline exists.

### How to Fix

1. Create `.github/workflows/ci.yml` with the config above
2. Enable branch protection on `main` requiring CI to pass
3. Add test, lint, and security scan steps

---

## Layer 7: Database Constraints

### What They Are

Rules enforced by the database itself. If data violates constraints, the insert/update fails.

### Types of Constraints

| Constraint | What It Does | Example |
|------------|--------------|---------|
| **NOT NULL** | Requires value | `contact_id STRING NOT NULL` |
| **Primary Key** | Unique identifier | `PRIMARY KEY (contact_id)` |
| **Foreign Key** | References other table | `FOREIGN KEY (person_id) REFERENCES persons(id)` |
| **Check** | Custom validation | `CHECK (age >= 0)` |
| **Unique** | No duplicates | `UNIQUE (email)` |

### BigQuery Specifics

BigQuery has limited constraint support:

| Constraint | BigQuery Support |
|------------|------------------|
| NOT NULL | ✅ Supported |
| Primary Key | ⚠️ For information only (not enforced) |
| Foreign Key | ⚠️ For information only (not enforced) |
| Check constraints | ❌ Not supported |
| Unique constraints | ❌ Not supported (use MERGE) |

**Important:** BigQuery's primary/foreign keys are METADATA only. They don't actually prevent duplicates. You must handle this in your code.

### Current State in Truth Engine

| Table | NOT NULL | Clustering | Partitioning |
|-------|----------|------------|--------------|
| identity.contacts_master | ⚠️ Minimal | ❌ Missing | ❌ Missing |
| identity.id_registry | ⚠️ Minimal | ❌ Missing | ❌ Missing |
| spine.entity_unified | ✅ Yes | ✅ Yes | ✅ Yes |

### What's Missing

- Tables created without CLUSTER BY
- Tables created without PARTITION BY
- Deduplication not handled in load logic

### How to Fix

1. Recreate tables with proper DDL:
```sql
CREATE OR REPLACE TABLE `identity.contacts_master` (
    contact_id INT64 NOT NULL,
    -- other columns...
    modification_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(modification_date)
CLUSTER BY contact_id
OPTIONS (
    labels = [("layer", "identity")]
)
```

2. Add deduplication in load scripts using MERGE:
```sql
MERGE target USING source ON target.id = source.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

---

## Layer 8: Cloud Permissions (IAM)

### What It Is

Google Cloud's system for controlling who can do what. Every API call is checked against permissions.

### Key Concepts

| Concept | What It Is |
|---------|------------|
| **Principal** | Who (user, service account) |
| **Role** | Collection of permissions |
| **Permission** | Single action (e.g., `bigquery.tables.create`) |
| **Policy** | Binding of principals to roles |

### Common Roles

| Role | What It Allows |
|------|----------------|
| `roles/bigquery.dataViewer` | Read data |
| `roles/bigquery.dataEditor` | Read + write data |
| `roles/bigquery.admin` | Full control |
| `roles/billing.viewer` | View billing |
| `roles/billing.admin` | Modify billing |

### Current State in Truth Engine

| Principal | Roles | Risk |
|-----------|-------|------|
| Your user account | Owner | High (too broad) |
| Service accounts | Unknown | Unknown |

### What's Missing

- Principle of least privilege not applied
- Service accounts not documented
- No separation between dev/prod permissions

### How to Fix

1. Create dedicated service accounts:
```bash
gcloud iam service-accounts create truth-engine-reader \
    --display-name="Truth Engine Read Only"

gcloud iam service-accounts create truth-engine-writer \
    --display-name="Truth Engine Writer"
```

2. Assign minimal permissions:
```bash
# Reader can only read
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:truth-engine-reader@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"
```

---

## Layer 9: Monitoring

### What It Is

Systems that watch what's happening and alert when something's wrong.

### Components

| Component | What It Does |
|-----------|--------------|
| **Logging** | Records what happened |
| **Metrics** | Counts/measures things |
| **Alerts** | Notifies when thresholds crossed |
| **Dashboards** | Visualizes data |

### GCP Monitoring Tools

| Tool | Purpose |
|------|---------|
| Cloud Logging | Centralized logs |
| Cloud Monitoring | Metrics and alerts |
| Error Reporting | Groups and tracks errors |
| Cloud Trace | Request tracing |

### Current State in Truth Engine

| Component | Status |
|-----------|--------|
| Structured logging | ✅ Via get_logger() |
| Log export to BigQuery | ✅ governance.process_costs |
| Metrics collection | ⚠️ Partial |
| Alerting | ❌ Not set up |
| Dashboards | ❌ Not set up |

### What's Missing

- No alerts for cost spikes
- No alerts for error rate spikes
- No dashboard for system health

### How to Fix

1. Create alert policy in GCP:
```bash
gcloud alpha monitoring policies create \
    --display-name="High BigQuery Cost" \
    --condition-display-name="Cost > $10" \
    --condition-filter='resource.type="bigquery_project" AND metric.type="bigquery.googleapis.com/query/total_bytes_billed"'
```

2. Create dashboard showing:
   - Queries per hour
   - Bytes scanned per hour
   - Cost per day
   - Error rate

---

## Layer 10: Cost Protection

### What It Is

Systems that prevent or stop excessive spending.

### GCP Billing Components

| Component | What It Does | Automatic? |
|-----------|--------------|------------|
| **Budget** | Tracks spending against threshold | ✅ |
| **Budget Alert** | Sends notification at threshold | ✅ |
| **Budget Action** | Does something at threshold | ❌ Requires code |

### The Critical Point

**GCP budgets do NOT automatically stop spending.**

When you set a $50 budget:
- At 50%: Email sent
- At 90%: Email sent
- At 100%: Email sent
- At 150%: Email sent, **spending continues**

### To Actually Stop Spending

You need a **Billing Guardian** - a Cloud Function or Cloud Run that:
1. Receives budget notification via Pub/Sub
2. Takes action (disable billing, stop resources, etc.)

### Architecture

```
Budget Threshold Hit
        ↓
   Pub/Sub Topic
        ↓
   Cloud Function
        ↓
   Disable Project Billing (or shut down resources)
```

### Implementation

**1. Create Pub/Sub topic:**
```bash
gcloud pubsub topics create billing-alerts
```

**2. Create Cloud Function:**
```python
# billing_guardian/main.py
import base64
import json
from google.cloud import billing_v1

def stop_billing(event, context):
    """Cloud Function triggered by Pub/Sub budget alert."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message_data = json.loads(pubsub_message)

    cost_amount = message_data.get('costAmount', 0)
    budget_amount = message_data.get('budgetAmount', 0)

    if cost_amount > budget_amount:
        # Disable billing for the project
        billing_client = billing_v1.CloudBillingClient()
        project_name = f"projects/{PROJECT_ID}"

        billing_client.update_project_billing_info(
            name=project_name,
            project_billing_info={
                "billing_account_name": ""  # Empty = disable billing
            }
        )

        print(f"BILLING DISABLED: Cost {cost_amount} exceeded budget {budget_amount}")
```

**3. Deploy:**
```bash
gcloud functions deploy billing-guardian \
    --runtime python311 \
    --trigger-topic billing-alerts \
    --entry-point stop_billing
```

**4. Link budget to Pub/Sub:**
```bash
gcloud billing budgets update BUDGET_ID \
    --notifications-pubsub-topic=projects/PROJECT_ID/topics/billing-alerts
```

### Current State in Truth Engine

| Component | Status |
|-----------|--------|
| Budget set | ⚠️ Unknown |
| Budget alerts | ⚠️ Unknown |
| Billing guardian | ❌ Not deployed |
| Pub/Sub topic | ❌ Not created |

### What's Missing

The entire cost protection system at the cloud level.

### Alternative: Query-Level Protection

While the billing guardian protects at the project level, you also have query-level protection:

```python
# Already exists in central services
from architect_central_services.core.shared import SessionCostLimiter

cost_limiter = SessionCostLimiter(
    max_cost_usd=5.0,
    abort_on_exceed=True
)
```

This prevents individual sessions from going overboard, but doesn't stop the billing if something bypasses it.

---

## Summary: Current Gaps

| Layer | Status | Gap |
|-------|--------|-----|
| 1. Code Quality | ⚠️ Partial | mypy not enforced |
| 2. AI Enforcement | ⚠️ Partial | Pattern scanner hook missing |
| 3. Pre-Commit | ⚠️ Partial | Syntax validation missing |
| 4. Runtime Protection | ⚠️ Partial | Streaming insert not blocked |
| 5. Testing | ⚠️ Partial | Coverage not measured/enforced |
| 6. CI/CD | ❌ Missing | No pipeline |
| 7. Database | ⚠️ Partial | Tables lack clustering/partitioning |
| 8. IAM | ⚠️ Unknown | Permissions not documented |
| 9. Monitoring | ⚠️ Partial | No alerts |
| 10. Cost Protection | ❌ Missing | No billing guardian |

---

## Priority Order to Fix

### P0 - Immediate (Prevents $1,400 repeats)

1. **Deploy Billing Guardian** - Actually stops spending
2. **Block streaming insert at runtime** - Prevents the specific pattern
3. **Fix existing table schemas** - Prevents expensive full scans

### P1 - This Week

4. **Add pattern scanner to Claude hooks** - Catches bad code before write
5. **Add syntax validation to pre-commit** - Catches mass-edit errors
6. **Set up basic CI/CD** - Automated checks on every push

### P2 - This Month

7. **Enforce type checking** - Catches more bugs
8. **Measure and enforce test coverage** - Catches regressions
9. **Create monitoring dashboard** - Visibility into system health
10. **Document and tighten IAM** - Principle of least privilege

---

## References

- `.claude/hooks.json` - AI agent hooks
- `.claude/rules/` - AI agent rules
- `01-cost-protection.md` - Cost protection rule
- `02-bigquery-patterns.md` - BigQuery patterns rule
- `architect_central_services/governance/agent_monitor/` - Runtime protection

---

## Appendix A: Quick Commands

### Check current pre-commit hooks
```bash
pre-commit run --all-files
```

### Run tests with coverage
```bash
pytest --cov=architect_central_services --cov-report=html
```

### Check BigQuery table schema
```bash
bq show --schema --format=prettyjson PROJECT:DATASET.TABLE
```

### List GCP IAM bindings
```bash
gcloud projects get-iam-policy PROJECT_ID
```

### Check billing budget status
```bash
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID
```

---

## Appendix B: File Locations

| Protection | Configuration Location |
|------------|----------------------|
| Pre-commit hooks | `.pre-commit-config.yaml` |
| Claude hooks | `.claude/hooks.json` |
| Claude rules | `.claude/rules/*.md` |
| Runtime protection | `architect_central_services/governance/agent_monitor/runtime_protection.py` |
| CI/CD | `.github/workflows/ci.yml` (to be created) |
| Billing guardian | `infrastructure/billing_guardian/` (to be created) |

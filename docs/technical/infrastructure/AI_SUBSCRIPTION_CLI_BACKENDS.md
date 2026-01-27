# AI Subscription CLI Backends

**Discovery Date**: 2025-01-01
**Status**: Validated
**Impact**: Multiple AI subscriptions can be used programmatically - no API keys, no per-token costs

---

## The Discovery

Your AI subscriptions include CLI tools that can be called programmatically:

| Subscription | CLI Command | Capability | Use Case |
|--------------|-------------|------------|----------|
| **Claude Code** | `claude -p "prompt"` | Full LLM | Any LLM task |
| **Gemini CLI** | `gemini "prompt"` | Full LLM | Any LLM task |
| **GitHub Copilot** | `gh copilot suggest/explain` | Terminal-only | Command help |

**These use your subscriptions - no API keys, no per-token cost.**

---

## Claude Code CLI

### The Command

```bash
# Basic usage
claude -p "Analyze this text and return JSON"

# With JSON output
claude -p "Categorize this file" --output-format json

# With schema validation
claude -p "Extract data" --json-schema '{"type":"object","properties":{"category":{"type":"string"}}}'

# Pipe input
echo "content to analyze" | claude -p "Summarize this"

# Read file
cat document.md | claude -p "Extract key points as JSON"
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p, --print` | Non-interactive mode (required for scripts) |
| `--output-format json` | Get structured JSON output |
| `--output-format stream-json` | Streaming JSON for real-time |
| `--json-schema <schema>` | Validate output against JSON Schema |
| `--max-budget-usd <amount>` | Limit spending per call |

### Python Pattern

```python
import subprocess
import json

def ask_claude(prompt: str, json_output: bool = False) -> str | dict:
    """Use Claude Code subscription for LLM processing."""
    cmd = ["claude", "-p", prompt]
    if json_output:
        cmd.extend(["--output-format", "json"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        raise RuntimeError(f"Claude failed: {result.stderr}")

    if json_output:
        return json.loads(result.stdout)
    return result.stdout.strip()
```

---

## Gemini CLI

### The Command

```bash
# Basic usage (interactive)
gemini "Analyze this text"

# Non-interactive with prompt flag (deprecated but works)
gemini -p "Your prompt here"

# With JSON output
gemini "Categorize this content" -o json

# YOLO mode (auto-approve all actions)
gemini "Do something" -y

# Specific model
gemini "Your prompt" -m gemini-2.0-flash
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-p, --prompt` | Non-interactive prompt (deprecated, use positional) |
| `-o, --output-format` | Output format: `text`, `json`, `stream-json` |
| `-m, --model` | Specify model |
| `-y, --yolo` | Auto-approve all actions |
| `-s, --sandbox` | Run in sandbox mode |
| `--approval-mode` | `default`, `auto_edit`, or `yolo` |

### Python Pattern

```python
import subprocess
import json

def ask_gemini(prompt: str, json_output: bool = False) -> str | dict:
    """Use Gemini CLI subscription for LLM processing."""
    cmd = ["gemini", prompt]
    if json_output:
        cmd.extend(["-o", "json"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        raise RuntimeError(f"Gemini failed: {result.stderr}")

    if json_output:
        return json.loads(result.stdout)
    return result.stdout.strip()
```

---

## GitHub Copilot CLI

**Note**: This is specialized for terminal commands, NOT general LLM tasks.

### The Command

```bash
# Suggest a command
gh copilot suggest "Install git on macOS"

# Explain a command
gh copilot explain "tar -xzf archive.tar.gz"
```

### Use Cases

- Getting shell command suggestions
- Understanding complex commands
- NOT suitable for document processing, categorization, etc.

---

## Cost Comparison

| Method | Cost | Rate Limits | Setup |
|--------|------|-------------|-------|
| **Claude Code (-p)** | Included | Generous | None |
| **Gemini CLI** | Included | Generous | None |
| **GitHub Copilot CLI** | Included | Generous | `gh extension install github/gh-copilot` |
| Anthropic API | $3-15/M tokens | Per-minute | API key |
| Vertex AI | $3-15/M tokens | Quotas | GCP setup |
| OpenAI API | $0.50-60/M tokens | Per-minute | API key |

---

## Unified Client Strategy

### Priority Order

For local development, use in this order:

1. **Claude Code** - Best quality, most features, JSON schema support
2. **Gemini CLI** - Good fallback, fast, JSON output support
3. **API** - Only for cloud/production

### Unified Python Client

See: `architect_central_services/src/architect_central_services/core/shared/claude_code_client.py`

For a multi-backend version, see the next section.

---

## The Hybrid Approach

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM PROCESSING DECISION                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Is this running locally on Jeremy's machine?                       │
│       │                                                             │
│       ├── YES                                                       │
│       │     │                                                       │
│       │     ├── Claude Code available? → Use claude -p (FREE)       │
│       │     │                                                       │
│       │     └── Gemini CLI available? → Use gemini (FREE)           │
│       │                                                             │
│       └── NO (Cloud Run, CI/CD, etc.)                              │
│                │                                                    │
│                └── Use Gemini API - PAID                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Systems That Can Use This

| Current System | Current Method | Can Switch To | Savings |
|----------------|----------------|---------------|---------|
| Knowledge Atom extraction | Gemini API ($) | Claude/Gemini CLI | ~$10-50/month |
| Document categorization | Gemini Flash ($) | Claude/Gemini CLI | ~$5-20/month |
| Content analysis | Vertex AI ($) | Claude/Gemini CLI | ~$10-30/month |
| Validation scripts | Flash ($) | Claude/Gemini CLI | ~$5-15/month |
| Pattern detection | Flash/Pro ($) | Claude/Gemini CLI | ~$10-30/month |
| **Total Potential Savings** | | | **~$50-200/month** |

---

## Limitations

| Limitation | Workaround |
|------------|------------|
| No embeddings API | Use for classification, not vector search |
| Single-threaded | Queue requests, process sequentially |
| Local only | Use API for cloud/CI/CD |
| Timeout limits | Break large tasks into chunks |

---

## When NOT to Use CLI

- **High-volume production pipelines**: API has better rate limits
- **Parallel processing**: CLI is single-threaded
- **Embedding generation**: Need dedicated embedding API
- **CI/CD pipelines**: CLI tools may not be installed
- **Server-side applications**: Designed for local dev machines

---

## Quick Reference

### Claude Code

```bash
claude -p "prompt" --output-format json
```

### Gemini CLI

```bash
gemini "prompt" -o json
```

### Test Both

```bash
# Test Claude Code
claude -p "Say hello in JSON format" --output-format json

# Test Gemini CLI
gemini "Say hello in JSON format" -o json
```

---

## Related Documents

- `CLAUDE_CODE_AS_LLM_BACKEND.md` - Original Claude Code discovery
- `CLAUDE_CODE_MIGRATION_OPPORTUNITIES.md` - Files to migrate
- `architect_central_services/core/shared/claude_code_client.py` - Python utility

---

## The Bottom Line

**You have 2 free LLM backends available right now:**
- `claude -p` (Claude Code subscription)
- `gemini` (Gemini CLI subscription)

Every script that currently calls paid LLM APIs can potentially switch to these CLI tools - at no additional cost.

# Claude Code as LLM Backend

**Discovery Date**: 2025-01-01
**Status**: Validated
**Impact**: All systems that need LLM processing can use Claude Code subscription instead of API keys

---

## The Discovery

The `claude-organize` npm package revealed that you can call Claude Code programmatically:

```bash
claude -p "your prompt here"
```

This uses your **Claude Code subscription** - no API key, no per-token cost.

---

## How It Works

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

---

## Cost Comparison

| Method | Cost | Rate Limits | Setup |
|--------|------|-------------|-------|
| **Claude Code (-p)** | Included in subscription | Generous | None |
| Anthropic API | $3-15/M tokens | Per-minute limits | API key required |
| Vertex AI | $3-15/M tokens | Quotas | GCP setup required |

**Bottom line**: If you're already paying for Claude Code, use it for LLM tasks.

---

## Integration Patterns

### Pattern 1: Shell Script

```bash
#!/bin/bash
# analyze_document.sh

FILE="$1"
CONTENT=$(cat "$FILE")

RESULT=$(claude -p "Analyze this document and return JSON with category, summary, and keywords:

$CONTENT" --output-format json)

echo "$RESULT"
```

### Pattern 2: Python Subprocess

```python
import subprocess
import json

def ask_claude(prompt: str) -> dict:
    """Use Claude Code subscription for LLM processing."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude failed: {result.stderr}")

    return json.loads(result.stdout)

# Usage
response = ask_claude("Categorize this text: 'Meeting notes from Q4 review'")
print(response)  # {"category": "business", "type": "meeting_notes", ...}
```

### Pattern 3: Node.js (like claude-organize)

```javascript
const { execFileSync } = require('child_process');

function askClaude(prompt) {
    const response = execFileSync('claude', ['-p', prompt, '--output-format', 'json'], {
        encoding: 'utf8',
        timeout: 30000
    });
    return JSON.parse(response);
}

// Usage
const result = askClaude('Extract entities from: "John met with Acme Corp in NYC"');
```

### Pattern 4: With JSON Schema Validation

```python
import subprocess
import json

SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["docs", "scripts", "data", "config"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reasoning": {"type": "string"}
    },
    "required": ["category", "confidence"]
})

def categorize_file(content: str) -> dict:
    result = subprocess.run(
        [
            "claude", "-p",
            f"Categorize this file content:\n\n{content}",
            "--output-format", "json",
            "--json-schema", SCHEMA
        ],
        capture_output=True,
        text=True,
        timeout=60
    )
    return json.loads(result.stdout)
```

---

## Systems That Can Use This

| Current System | Current Method | Can Switch To |
|----------------|----------------|---------------|
| Knowledge Atom extraction | Gemini API ($) | Claude Code (free) |
| Document categorization | Gemini Flash ($) | Claude Code (free) |
| Content analysis | Vertex AI ($) | Claude Code (free) |
| Semantic search enrichment | Embeddings API ($) | Claude Code (free*) |
| Pattern detection | Flash/Pro ($) | Claude Code (free) |

*Note: Claude Code can do semantic analysis but not generate embeddings directly.

---

## Limitations

| Limitation | Workaround |
|------------|------------|
| No embeddings API | Use for classification, not vector search |
| Timeout (default 2min) | Use `--timeout` flag or break into chunks |
| No streaming to BigQuery | Batch results, then insert |
| One request at a time | Queue requests, process sequentially |
| Requires Claude Code installed | Only works on machines with Claude Code |

---

## When NOT to Use This

- **High-volume production pipelines**: API has better rate limits
- **Parallel processing**: Claude Code is single-threaded
- **Embedding generation**: Need dedicated embedding API
- **CI/CD pipelines**: Claude Code may not be available
- **Server-side applications**: Designed for local dev machines

---

## The Hybrid Approach

For Truth Engine, the ideal pattern:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM PROCESSING DECISION                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Is this running locally on Jeremy's machine?                       │
│       │                                                             │
│       ├── YES → Use Claude Code (-p) - FREE                        │
│       │                                                             │
│       └── NO (Cloud Run, CI/CD, etc.)                              │
│                │                                                    │
│                └── Use Gemini API - PAID                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

1. **Document categorization** (claude-organize already does this)
2. **Knowledge atom extraction** (currently uses Gemini)
3. **Content analysis scripts** (currently uses Flash)
4. **Pattern detection** (currently uses Pro)

---

## Example: Rewriting a Gemini Script

### Before (costs money):

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content(prompt)
result = response.text
```

### After (free with Claude Code):

```python
import subprocess

def ask_claude(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()

result = ask_claude(prompt)
```

---

## Testing It

```bash
# Simple test
claude -p "Say hello in JSON format" --output-format json

# Expected output:
# {"greeting": "Hello!", "format": "json"}

# Test with file
echo "This is a test document about Python programming" | claude -p "Categorize this content" --output-format json
```

---

## References

- `claude --help` - Full CLI documentation
- `claude-organize` source - Example implementation
- `/Users/jeremyserna/PrimitiveEngine/docs/organization-log.json` - Proof it works

---

## The Bottom Line

**You're already paying for Claude Code. Use it.**

Every script that currently calls Gemini, GPT, or any LLM API can potentially be rewritten to use `claude -p` instead - at no additional cost.

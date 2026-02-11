# Pipeline Stage Construction SOP

**Purpose**: To ensure every stage of the Truth Forge pipeline is built to an enforceable, verifiable high standard.
**Rule**: No stage proceeds to Cloud Run without a signed-off **Human Review Package**.

---

## 🏗️ The 5-Step Factory Process

For every single stage (Stage 0 through Stage 16), we follow this strict cycle:

### 1. Specification (The Contract)
Before writing code, we define:
*   **Input**: What exactly goes in? (Schema, data examples)
*   **Logic**: What happens? (Plain English description of the transformation)
*   **Output**: What exactly comes out? (Schema, data examples)
*   **Failure Modes**: What happens when bad data hits this stage?

### 2. Implementation (The Code)
We write the Python code (`stage_N.py`) following these rules:
*   **Idempotent**: Running it twice on the same data yields the same result.
*   **Isolated**: No hidden dependencies.
*   **Typed**: Full Python type hints.
*   **Logged**: Structured logs for every major action.

### 3. Verification (The Test)
We prove it works mechanically:
*   **Unit Tests**: Test logic with mock data.
*   **Integration Test**: Run with REAL sample data (3-5 records).
*   **Identity Check**: Verify IDs are stable (Stage 3+).

### 4. The "Contractor Pack" (Human Review Gate) 🛑
We compile a readable Markdown document for the human reviewer. It contains:
1.  **The Goal**: "This stage splits paragraphs into sentences."
2.  **The Code**: The actual Python script.
3.  **The Proof**:
    *   Input: "Here is the raw text."
    *   Output: "Here is the split text."
    *   Logs: "Here is the success message."
4.  **The Checklist**: specific yes/no questions for the reviewer (e.g., "Are the IDs deterministic?").

> **Action**: The system PAUSES here. We wait for you (or your contractor) to review this pack.

### 5. Deployment (The Seal)
Once signed off:
*   The code is locked into the Docker container.
*   The version is bumped.
*   It is deployed to Cloud Run.
*   It is marked "DONE" in the Master Task List.

---

## 🔍 Validation Checklist (For every stage)

*   [ ] Does it handle empty/null inputs gracefully?
*   [ ] are `entity_ids` generated deterministically?
*   [ ] Is the input/output schema valid JSONL?
*   [ ] Are there clear error logs for failures?
*   [ ] Does it pass the "Stranger Test"? (Can a stranger understand what it does just by reading the logs?)

---

# Conversation Refinery

**Role**: The Blast Furnace
**Federation Status**: Operational (Building)

The **Conversation Refinery** is the "Not-Me" identity construction engine. It accepts raw conversation logs from the `not_me_chat` and processes them through the Universal 16-Stage Pipeline to extract "Knowledge Atoms" (Entities, Claims, Wisdom).

## The Pipeline

1.  **Ingest**: Raw text from Chat.
2.  **Refine**: Apply 16-Stage NLP (spaCy + LLM).
3.  **Store**: Deposit into `spine.conversation_atoms` (BigQuery).

## Orchestration Role

*   **Managed By**: The Orchestrator (Truth Engine AI)
*   **Built By**: The Builder (Primitive Engine AI)
*   **Verified By**: The Seer (Credential Atlas AI)

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/main.py
```

## Verification

Check health:
```bash
curl http://localhost:8001/health
```

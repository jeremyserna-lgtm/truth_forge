"""Agent function for Stage 4 LLM Text Correction (Primitive Pattern).

This is the AGENT in THE_PATTERN: HOLD₁ → AGENT → HOLD₂
- Receives: Record from Stage 3 (HOLD₁)
- Transforms: LLM correction of text
- Returns: Corrected text records (HOLD₂)
"""

import json
from typing import Any, Dict, List, Optional, Union

from src.services.central_services.primitive_pattern import AgentContext

def llm_correction_agent(
    record: Dict[str, Any],
    context: AgentContext,
) -> Union[None, Dict[str, Any], List[Dict[str, Any]]]:
    """AGENT: LLM Text Correction for Claude Code/Codex/Github.

    🔥 FURNACE ACTION: Truth → Meaning → Care
    - Truth (Input): Text from Stage 3 (may have formatting issues)
    - Heat (Processing): LLM correction (spellcheck, grammar, formatting cleanup)
    - Meaning (Output): Corrected text ready for NLP processing
    - Care (Delivery): Validated text in Stage 4/5 records

    🎓 LEARNING: Agent Function Pattern
    - Receives one record from HOLD₁ at a time
    - Can use context.inhale() for RAG (knowledge atoms)
    - Can use context.prompt() for LLM calls
    - Can use context.exhale() to produce knowledge atoms
    - Returns None (skip), Dict (single output), or List[Dict] (multiple outputs)

    Args:
        record: Input record from Stage 3 (HOLD₁)
            - entity_id: Entity identifier
            - text: Text to correct
            - source_name: Source identifier (claude_code, codex, github)
            - level: Entity level (should be 5 for messages)
        context: AgentContext with primitive tools

    Returns:
        - None: Skip this record
        - Dict: Single output record for HOLD₂
        - List[Dict]: Multiple output records (Stage 4 + Stage 5)
    """
    # Skip if not L5 message
    if record.get("level") != 5:
        return None

    # Skip if text is too short
    text = record.get("text", "").strip()
    if not text or len(text) < 10:
        return None

    entity_id = record.get("entity_id")
    if not entity_id:
        return None

    source_name = record.get("source_name", "unknown")

    # 🎓 LEARNING: Use local Ollama for text correction (free, no cloud costs)
    # We use ask_ollama_json() directly to ensure we're using local Ollama
    # This avoids any cloud API calls and ensures zero cost
    try:
        from src.services.central_services.model_gateway_service.convenience import ask_ollama_json

        # Build prompt for text cleaning using local Ollama
        prompt_text = f"""Clean and correct this text while preserving meaning, tone, and style:

ID: {entity_id}
SOURCE: {source_name}
TEXT: {text}

Return JSON with:
- id: "{entity_id}"
- original_text: The exact original text
- cleaned_text: The cleaned and corrected text
- is_ready: true if cleaned_text is valid for NLP processing

Rules:
- Correct spelling, grammar, and formatting issues
- Preserve tone, emojis, and technical content (code, URLs, file paths)
- Only correct actual errors, not intentional style
- Preserve code snippets exactly
"""

        # Use local Ollama directly (primitive model, local hardware, zero cost)
        response = ask_ollama_json(prompt_text, model_name="primitive")

        # Parse response from Ollama
        if isinstance(response, dict):
            corrected_text = response.get("cleaned_text") or response.get("corrected_text", text)
            original_text = response.get("original_text", text)
            is_ready = response.get("is_ready", True)
        else:
            # Fallback if unexpected format
            corrected_text = text
            original_text = text
            is_ready = True

    except Exception as e:
        # If Ollama call fails, preserve original text
        # Error becomes a signal (not a blocker)
        corrected_text = text
        original_text = text
        is_ready = True

        correction_applied = corrected_text != original_text

        # Return multiple records: Stage 4 (all corrections) + Stage 5 (ready only)
        outputs = []

        # Stage 4 record (all corrections)
        outputs.append({
            "entity_id": entity_id,
            "source_name": source_name,
            "original_text": original_text,
            "corrected_text": corrected_text,
            "correction_applied": correction_applied,
            "is_ready": is_ready,
            "_output_type": "stage_4",
        })

        # Stage 5 record (only if ready)
        if is_ready and corrected_text and len(corrected_text.strip()) >= 10:
            outputs.append({
                "entity_id": entity_id,
                "source_name": source_name,
                "text": corrected_text,  # Use corrected text for NLP
                "original_text": original_text,
                "_output_type": "stage_5",
            })

        return outputs

    except Exception as e:
        # On error, preserve original text
        # Error becomes a signal (not a blocker)
        return {
            "entity_id": entity_id,
            "source_name": source_name,
            "original_text": text,
            "corrected_text": text,
            "correction_applied": False,
            "is_ready": True,
            "_error": str(e),
            "_output_type": "stage_4",
        }

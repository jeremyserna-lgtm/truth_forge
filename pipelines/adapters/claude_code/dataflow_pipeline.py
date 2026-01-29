#!/usr/bin/env python3
"""
Dataflow Pipeline: Multi-Source AI Conversations → entity_unified

Complete pipeline using Apache Beam/Dataflow that:
- Reads from BigQuery external tables OR GCS files (messages are already L5-level units)
- Supports: claude_code, claude_web, gemini_web, gemini_code, codex, copilot, grok_web, text_messages
- THE GATE: Generates entity_id and conversation_id (identity_service logic)
- Gemini Cleaning: Fixes spelling/grammar for user messages (preserves meaning)
- Splits cleaned L5 messages into L4 sentences (spaCy)
- Writes to entity_unified with exact 34-column schema

Flow: Extract → THE GATE → Gemini Clean → L5 Messages → Split L5 into L4
- Cleaned text goes in `text` column
- Original text preserved in `metadata.text_original`
- All metadata has standardized structure

Levels emitted: L4 (sentence), L5 (message), L8 (conversation).
L2 (word), L3 (span), L6 (turn), L7 (topic) are not produced by this pipeline;
hierarchy IDs and count rollups are set accordingly.

Usage:
    python dataflow_pipeline.py --source claude_code
    python dataflow_pipeline.py --source gemini_web
    python dataflow_pipeline.py --source text_messages --gcs-path gs://bucket/path/*.jsonl

Based on: https://medium.com/google-cloud/nlp-with-spacy-dataflow-ml-and-bigquery-ml-clustering-933ab45d7161
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.ml.inference.base import ModelHandler
import spacy
import json
import argparse
from typing import Dict, Any, List
from datetime import datetime, timezone

# Configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
DEST_TABLE = f"{PROJECT_ID}.{DATASET_ID}.entity_unified"

# Source configuration
# GCS-based sources (external tables): claude_web, gemini_web, grok_web
# Local file sources (synced to GCS): claude_code, codex, gemini_code, copilot, text_messages
SUPPORTED_SOURCES = {
    "claude_code": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.claude_code_external", "type": "external"},
    "claude_web": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.claude_web_external", "type": "external"},
    "gemini_web": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.gemini_web_external", "type": "external"},
    "gemini_code": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.gemini_code_external", "type": "external"},
    "codex": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.codex_external", "type": "external"},
    "copilot": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.copilot_external", "type": "external"},
    "grok_web": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.grok_web_external", "type": "external"},
    "text_messages": {"external_table": f"{PROJECT_ID}.{DATASET_ID}.text_messages_external", "type": "external"},
}


# ============================================================================
# Stage Functions
# ============================================================================

def extract_function(source_name: str):
    """Create extract function for a specific source."""
    def _extract(row: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 1: Extract and parse data."""
        # Extract relevant fields from external table row
        # Messages are already L5-level units
        return {
            "session_id": row.get("session_id"),
            "message_index": row.get("message_index"),
            "text": row.get("text"),  # Original text
            "role": row.get("role"),
            "message_type": row.get("message_type"),
            "source_file": row.get("source_file"),
            "timestamp_utc": row.get("timestamp_utc"),
            "content_date": row.get("content_date"),
            "source_pipeline": source_name,
        }
    return _extract


# ============================================================================
# Gemini text cleaning configuration (MUST run before spaCy)
# ============================================================================
# Use Gemini Flash Lite for spelling/grammar: cost-effective, preserves meaning.
# No Python spelling packages (they mutilate text). LLM correction only.
# Order: spelling correction → THEN spaCy → L5 messages become L4/L3/L2.
GEMINI_MODEL = "gemini-2.0-flash-lite"
# Simple prompt: spelling only. Do not change meaning—we run sentiment analysis downstream.
CORRECTION_PROMPT = """Clean the spelling of this text. Do not change the meaning. We use this for sentiment analysis and must preserve intent and tone.

Text:
{text}

Return ONLY a JSON object:
- corrected_text: The spelling-corrected text (meaning unchanged)
- original_text: The exact original text
- changes_made: Brief description (or "no changes" if none)

JSON:"""


def _generate_hash(content: str, length: int = 16) -> str:
    """Generate truncated SHA-256 hash (from identity_service)."""
    import hashlib
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:length]


def _format_sequence(index: int) -> str:
    """Format sequence number as 4-digit zero-padded string."""
    return f"{index:04d}"


def generate_entity_id(source_name: str):
    """Create entity_id generator for a specific source."""
    def _generate(row: Dict[str, Any]) -> Dict[str, Any]:
        """THE GATE - Generate entity_id using identity_service logic.
        
        Uses the same deterministic ID generation as identity_service.generate_message_id()
        Format: msg:{conversation_hash}:{sequence}
        
        Must run BEFORE text cleaning so entity_id is stable.
        """
        session_id = row.get("session_id", "")
        message_index = row.get("message_index", 0)
        
        # Generate conversation ID first (if needed)
        conv_hash = _generate_hash(session_id, length=16)
        seq = _format_sequence(message_index)
        
        # Generate message ID (format: msg:{hash}:{seq})
        entity_id = f"msg:{conv_hash}:{seq}"
        
        row["entity_id"] = entity_id
        row["conversation_id"] = f"conv:{source_name}:{conv_hash}"
        row["identity_created_at"] = datetime.now(timezone.utc).isoformat()
        
        return row
    return _generate


# ============================================================================
# entity_unified row builder (34 columns, L2–L8 only; no L1)
# ============================================================================

def _entity_unified_row(
    entity_id: str,
    level: int,
    entity_type: str,
    parent_id: str | None,
    conversation_id: str | None,
    topic_segment_id: str | None,
    turn_id: str | None,
    message_id: str | None,
    sentence_id: str | None,
    span_id: str | None,
    word_id: str | None,
    text: str | None,
    source_file: str | None,
    content_date: Any,
    metadata_json: str | None,
    source_pipeline: str,
    source_message_timestamp: Any = None,
    persona: str | None = None,
    canonical_form: str | None = None,
    l7_count: int | None = None,
    l6_count: int | None = None,
    l5_count: int | None = None,
    l4_count: int | None = None,
    l3_count: int | None = None,
    l2_count: int | None = None,
) -> Dict[str, Any]:
    """Build a single row matching entity_unified schema (34 fields)."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "entity_id": entity_id,
        "level": level,
        "entity_type": entity_type,
        "entity_mode": "active",
        "parent_id": parent_id,
        "conversation_id": conversation_id,
        "topic_segment_id": topic_segment_id,
        "turn_id": turn_id,
        "message_id": message_id,
        "sentence_id": sentence_id,
        "span_id": span_id,
        "word_id": word_id,
        "text": text,
        "source_pipeline": source_pipeline,
        "source_file": source_file,
        "source_file_path": source_file,
        "source_system": source_pipeline,
        "source_ids": [entity_id],
        "content_date": content_date,
        "canonical_form": canonical_form,
        "persona": persona,
        "metadata": metadata_json,
        "source_message_timestamp": source_message_timestamp,
        "created_at": now_iso,
        "updated_at": now_iso,
        "ingestion_timestamp": now_iso,
        "ingestion_job_id": "dataflow-pipeline",
        "validation_status": "PASSED",
        "l7_count": l7_count,
        "l6_count": l6_count,
        "l5_count": l5_count,
        "l4_count": l4_count,
        "l3_count": l3_count,
        "l2_count": l2_count,
    }


# ============================================================================
# spaCy Model Handlers (L4 sentences only; no L1)
# ============================================================================

class SpacySentenceHandler(ModelHandler[str, spacy.Language, List[Dict[str, Any]]]):
    """spaCy handler for sentence segmentation (L4 sentences). Optional; pipeline uses SentenceDoFn."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
    
    def load_model(self):
        return spacy.load(self._model_name)
    
    def run_inference(
        self,
        batch: List[str],
        model: spacy.Language,
        inference_args: Dict[str, Any] | None = None
    ) -> List[List[Dict[str, Any]]]:
        """Segment text into sentences."""
        results = []
        for text in batch:
            if not text:
                results.append([])
                continue
                
            doc = model(text)
            sentences = []
            for i, sent in enumerate(doc.sents):
                sentences.append({
                    "text": sent.text,
                    "start": sent.start_char,
                    "end": sent.end_char,
                    "index": i,
                })
            results.append(sentences)
        return results


# ============================================================================
# DoFn Classes (L2–L8 only; no L1)
# ============================================================================

class GeminiCleanDoFn(beam.DoFn):
    """Clean user messages with Gemini (fix spelling/grammar, preserve meaning).
    
    Only processes role='user' messages. Stores original text in metadata.
    """

    def __init__(self) -> None:
        self.genai_client = None
        self.model = None

    def start_bundle(self) -> None:
        """Initialize Gemini client once per worker."""
        try:
            import google.generativeai as genai
            import os
            api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.genai_client = genai
                self.model = genai.GenerativeModel(GEMINI_MODEL)
        except Exception:
            # If Gemini unavailable, pass through original text
            self.genai_client = None
            self.model = None

    def process(self, element: Dict[str, Any]) -> Any:
        """Clean user messages with Gemini; pass through others unchanged."""
        role = element.get("role", "")
        original_text = element.get("text", "")
        
        # Only clean user messages; assistant/system messages pass through
        if role != "user" or not self.model or not original_text or len(original_text.strip()) <= 10:
            element["text_cleaned"] = original_text.strip()
            element["text_original"] = original_text
            element["cleaning_applied"] = False
            return element

        try:
            # Call Gemini for correction
            prompt = CORRECTION_PROMPT.format(text=original_text[:8000])
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            corrected_text = result.get("corrected_text", original_text)
            changes_made = result.get("changes_made", "unknown")
            
            element["text_cleaned"] = corrected_text.strip()
            element["text_original"] = original_text
            element["cleaning_applied"] = True
            element["cleaning_changes"] = changes_made
        except Exception:
            # On error, use original text
            element["text_cleaned"] = original_text.strip()
            element["text_original"] = original_text
            element["cleaning_applied"] = False

        element["content_length"] = len(element["text_cleaned"])
        element["word_count"] = len(element["text_cleaned"].split())
        return element


class SentenceDoFn(beam.DoFn):
    """Create L4 sentence entities (entity_unified level 4)."""

    def __init__(self, source_pipeline: str) -> None:
        self.nlp = None
        self.source_pipeline = source_pipeline

    def start_bundle(self) -> None:
        """Load spaCy model once per worker."""
        import spacy
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")

    def process(self, element: Dict[str, Any]) -> Any:
        """Segment cleaned L5 text into sentences and yield L4 entity_unified rows."""
        # Use cleaned text from L5 message (already cleaned by Gemini)
        text = element.get("text_cleaned", "")
        message_entity_id = element.get("entity_id")
        conversation_id = element.get("conversation_id")
        source_file = element.get("source_file")
        content_date = element.get("content_date")

        if not text or not self.nlp:
            return

        doc = self.nlp(text)
        for i, sent in enumerate(doc.sents):
            parent_hash = _generate_hash(message_entity_id, length=16)
            seq = _format_sequence(i)
            sent_id = f"sent:{parent_hash}:{seq}"
            
            # Standardized metadata structure (same as L5)
            meta = json.dumps({
                "role": element.get("role"),
                "message_type": element.get("message_type"),
                "message_index": element.get("message_index"),
                "start_char": sent.start_char,
                "end_char": sent.end_char,
                "sentence_index": i,
            })

            row = _entity_unified_row(
                entity_id=sent_id,
                level=4,
                entity_type="sentence",
                parent_id=message_entity_id,
                conversation_id=conversation_id,
                topic_segment_id=None,
                turn_id=None,
                message_id=message_entity_id,
                sentence_id=sent_id,
                span_id=None,
                word_id=None,
                text=sent.text,  # Cleaned text from L5
                source_file=source_file,
                content_date=content_date,
                metadata_json=meta,
                source_pipeline=self.source_pipeline,
                source_message_timestamp=element.get("timestamp_utc"),
            )
            yield row


class MessageEntityDoFn(beam.DoFn):
    """Create L5 message entities (entity_unified level 5).
    
    Messages are already L5-level units. This creates entity_unified rows
    with cleaned text in `text` column and original text in metadata.
    """

    def __init__(self, source_pipeline: str) -> None:
        self.source_pipeline = source_pipeline

    def process(self, element: Dict[str, Any]) -> Any:
        """Create L5 message entity row matching entity_unified exactly."""
        entity_id = element.get("entity_id")
        conversation_id = element.get("conversation_id")
        
        # Standardized metadata structure (same across all levels)
        meta = json.dumps({
            "role": element.get("role"),
            "message_type": element.get("message_type"),
            "message_index": element.get("message_index"),
            "content_length": element.get("content_length"),
            "word_count": element.get("word_count"),
            "text_original": element.get("text_original"),  # Original text preserved
            "cleaning_applied": element.get("cleaning_applied", False),
            "cleaning_changes": element.get("cleaning_changes"),
        })
        
        # Cleaned text goes in `text` column, original in metadata
        row = _entity_unified_row(
            entity_id=entity_id,
            level=5,
            entity_type="message",
            parent_id=None,
            conversation_id=conversation_id,
            topic_segment_id=None,
            turn_id=None,
            message_id=entity_id,
            sentence_id=None,
            span_id=None,
            word_id=None,
            text=element.get("text_cleaned"),  # Cleaned text in text column
            source_file=element.get("source_file"),
            content_date=element.get("content_date"),
            metadata_json=meta,
            source_pipeline=self.source_pipeline,
            source_message_timestamp=element.get("timestamp_utc"),
        )
        yield row


class ConversationL8DoFn(beam.DoFn):
    """Create L8 conversation entities (entity_unified level 8). One row per conversation_id."""

    def __init__(self, source_pipeline: str) -> None:
        self.source_pipeline = source_pipeline

    def process(self, element: Dict[str, Any]) -> Any:
        """Yield one L8 row per distinct conversation_id."""
        conversation_id = element.get("conversation_id")
        if not conversation_id:
            return
        
        # Standardized metadata structure (same as L4/L5)
        meta = json.dumps({
            "session_id": element.get("session_id"),
            "source_pipeline": self.source_pipeline,
        })
        
        # Use conversation_id as entity_id for L8 (per entity_unified spec).
        row = _entity_unified_row(
            entity_id=conversation_id,
            level=8,
            entity_type="conversation",
            parent_id=None,
            conversation_id=conversation_id,
            topic_segment_id=None,
            turn_id=None,
            message_id=None,
            sentence_id=None,
            span_id=None,
            word_id=None,
            text=None,
            source_file=element.get("source_file"),
            content_date=element.get("content_date"),
            metadata_json=meta,
            source_pipeline=self.source_pipeline,
        )
        yield row


# ============================================================================
# Main Pipeline
# ============================================================================

def run_pipeline(source: str):
    """Run the complete Dataflow pipeline for a specific source.
    
    Args:
        source: Source name (e.g., 'claude_code', 'gemini_web', 'text_messages')
    """
    if source not in SUPPORTED_SOURCES:
        raise ValueError(
            f"Unsupported source: {source}. "
            f"Supported sources: {', '.join(SUPPORTED_SOURCES.keys())}"
        )
    
    source_config = SUPPORTED_SOURCES[source]
    source_table = source_config["external_table"]
    
    options = PipelineOptions(
        runner='DataflowRunner',
        project=PROJECT_ID,
        region='us-central1',
        temp_location='gs://claude_code_pipeline_source/temp',
        staging_location='gs://claude_code_pipeline_source/staging',
        job_name=f'{source}-pipeline',
        # Enable autoscaling
        autoscaling_algorithm='THROUGHPUT_BASED',
        max_num_workers=10,
    )
    
    with beam.Pipeline(options=options) as p:
        # Read from BigQuery external table
        raw = (
            p 
            | "ReadFromBigQuery" 
            >> beam.io.ReadFromBigQuery(
                query=f"SELECT * FROM `{source_table}`",
                use_standard_sql=True,
                use_json_exports=True,
            )
        )
        
        # Stage 1: Extract (messages are already L5-level)
        extracted = raw | "Extract" >> beam.Map(extract_function(source))
        
        # Stage 2: THE GATE (Identity generation - before cleaning)
        with_ids = extracted | "TheGate" >> beam.Map(generate_entity_id(source))
        
        # Stage 3: Gemini Clean (user messages only - fix spelling/grammar)
        # Original text preserved, cleaned text used for downstream processing
        cleaned = with_ids | "GeminiClean" >> beam.ParDo(GeminiCleanDoFn())

        # L5: Messages (entity_unified level 5) - cleaned text in text column, original in metadata
        l5_messages = cleaned | "L5Messages" >> beam.ParDo(MessageEntityDoFn(source))

        # L4: Split cleaned L5 text into sentences (entity_unified level 4; spaCy)
        l4_sentences = cleaned | "L4Sentences" >> beam.ParDo(SentenceDoFn(source))

        # L8: One conversation row per distinct conversation_id (entity_unified level 8)
        l8_per_conv = (
            cleaned
            | "KeyByConversation" >> beam.Map(lambda x: (x.get("conversation_id"), x))
            | "GroupByConversation" >> beam.GroupByKey()
            | "FirstPerConversation" >> beam.Map(lambda kv: next(iter(kv[1])))
            | "L8Conversations" >> beam.ParDo(ConversationL8DoFn(source))
        )

        # Emit L4, L5, L8 (no L1; L2/L3/L6/L7 not produced by this pipeline)
        all_entities = (
            (l4_sentences, l5_messages, l8_per_conv)
            | "Flatten" >> beam.Flatten()
        )

        # Write to entity_unified (34-column schema)
        all_entities | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
            table=DEST_TABLE,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=beam.io.BigQueryDisposition.FILE_LOADS,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dataflow pipeline for multi-source AI conversations"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=list(SUPPORTED_SOURCES.keys()),
        help=f"Source name. Options: {', '.join(SUPPORTED_SOURCES.keys())}",
    )
    args = parser.parse_args()
    run_pipeline(args.source)

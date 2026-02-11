"""LLM-based processor for conversation refinement.

Replaces rigid spaCy/NLP stages with intelligent LLM processing via Ollama.
Uses local models for privacy and cost efficiency.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import httpx

from .models import (
    ConversationL8,
    TopicSegmentL7,
    TurnL6,
    MessageL5,
    SentenceL4,
    SpanL3,
    WordL2,
)
from .prompts import (
    TOPIC_SEGMENTATION_PROMPT,
    TURN_DETECTION_PROMPT,
    SENTENCE_EXTRACTION_PROMPT,
    SPAN_EXTRACTION_PROMPT,
    WORD_ANALYSIS_PROMPT,
    FULL_MESSAGE_ANALYSIS_PROMPT,
    CONVERSATION_SUMMARY_PROMPT,
)


logger = logging.getLogger(__name__)


@dataclass
class ProcessorConfig:
    """Configuration for the LLM Refinery Processor."""
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:32b"  # Good balance of speed/quality
    
    # Processing settings
    timeout: float = 120.0  # Seconds per LLM call
    max_retries: int = 3
    
    # Depth control - process down to this level
    min_level: int = 5  # Default: stop at L5 (messages), set to 2 for full depth
    
    # Batch settings
    batch_size: int = 10  # Messages per batch for efficiency
    
    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("data/llm_refinery_output"))
    
    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class OllamaClient:
    """Client for Ollama API interactions."""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self._client = httpx.Client(timeout=config.timeout)
    
    def complete(self, prompt: str, temperature: float = 0.3) -> str:
        """Run completion with Ollama.
        
        Uses lower temperature for more deterministic extraction.
        """
        for attempt in range(self.config.max_retries):
            try:
                response = self._client.post(
                    f"{self.config.ollama_host}/api/generate",
                    json={
                        "model": self.config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": 4096,
                        },
                    },
                )
                response.raise_for_status()
                return response.json().get("response", "")
                
            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
            except httpx.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if attempt == self.config.max_retries - 1:
                    raise
        
        raise RuntimeError("Max retries exceeded")
    
    def parse_json_response(self, response: str) -> Any:
        """Parse JSON from LLM response, handling common issues.
        
        Robust JSON repair for common LLM output issues:
        - Missing commas between elements
        - Unterminated strings
        - Invalid escape sequences
        - Trailing commas
        - Property names without quotes
        """
        import re
        
        # Strip markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Try direct parse first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Extract JSON from response (may have extra text before/after)
        json_match = re.search(r'[\[{].*[\]}]', response, re.DOTALL)
        if json_match:
            response = json_match.group()
        
        # Apply repairs
        repaired = self._repair_json(response)
        
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error after repair: {e}")
            # Last resort: try json5 if available for lenient parsing
            try:
                import json5
                return json5.loads(repaired)
            except ImportError:
                pass
            except Exception:
                pass
            raise
    
    def _repair_json(self, text: str) -> str:
        """Repair common JSON issues from LLM output."""
        import re
        
        # Fix invalid escape sequences (e.g., \x, \n that should be \\n)
        # This is tricky - only fix truly invalid escapes
        def fix_escapes(s: str) -> str:
            # Valid JSON escapes: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
            result = []
            i = 0
            while i < len(s):
                if s[i] == '\\' and i + 1 < len(s):
                    next_char = s[i + 1]
                    if next_char in '"\\bfnrt/':
                        result.append(s[i:i+2])
                        i += 2
                    elif next_char == 'u' and i + 5 < len(s):
                        # Check for valid \uXXXX
                        hex_part = s[i+2:i+6]
                        if all(c in '0123456789abcdefABCDEF' for c in hex_part):
                            result.append(s[i:i+6])
                            i += 6
                        else:
                            result.append('\\\\')  # Invalid \u, escape the backslash
                            i += 1
                    else:
                        # Invalid escape - double the backslash
                        result.append('\\\\')
                        i += 1
                else:
                    result.append(s[i])
                    i += 1
            return ''.join(result)
        
        text = fix_escapes(text)
        
        # Fix unterminated strings at end of lines (truncated responses)
        # Pattern: string that doesn't close before newline or end
        lines = text.split('\n')
        fixed_lines = []
        for line in lines:
            # Count unescaped quotes
            in_string = False
            last_non_space = len(line.rstrip()) - 1
            for i, c in enumerate(line):
                if c == '"' and (i == 0 or line[i-1] != '\\'):
                    in_string = not in_string
            if in_string:
                # Unterminated string - try to close it
                line = line.rstrip() + '"'
            fixed_lines.append(line)
        text = '\n'.join(fixed_lines)
        
        # Fix missing commas between array elements
        # Pattern: } followed by { or ] followed by [
        text = re.sub(r'(\})\s*(\{)', r'\1,\2', text)
        text = re.sub(r'(\])\s*(\[)', r'\1,\2', text)
        
        # Fix missing commas between values
        # Pattern: "value" followed by "key":
        text = re.sub(r'(")\s*\n\s*(")', r'\1,\n\2', text)
        text = re.sub(r'(true|false|null|\d+)\s*\n\s*(")', r'\1,\n\2', text)
        
        # Fix missing commas on same line: "value" "key": -> "value", "key":
        text = re.sub(r'"\s+"([a-zA-Z_])', r'", "\1', text)
        
        # Fix trailing commas before closing brackets
        text = re.sub(r',\s*([\]}])', r'\1', text)
        
        # Fix property names without quotes (common LLM error)
        # Pattern: { word: or , word:
        text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
        
        return text
    
    def close(self):
        self._client.close()


class LLMRefineryProcessor:
    """Main processor for LLM-based conversation refinement."""
    
    def __init__(self, config: ProcessorConfig = None):
        self.config = config or ProcessorConfig()
        self.client = OllamaClient(self.config)
        self._stats = {
            "conversations_processed": 0,
            "messages_processed": 0,
            "llm_calls": 0,
            "errors": 0,
        }
    
    def process_file(self, input_path: Path, skip: int = 0) -> Iterator[ConversationL8]:
        """Process a conversations.json file.
        
        Yields ConversationL8 objects with full hierarchy.
        
        Args:
            input_path: Path to conversations.json
            skip: Number of conversations to skip at start
        """
        input_path = Path(input_path)
        
        with open(input_path, "r", encoding="utf-8") as f:
            conversations = json.load(f)
        
        logger.info(f"Processing {len(conversations)} conversations from {input_path}")
        if skip > 0:
            logger.info(f"Skipping first {skip} conversations")
        
        for i, raw_conv in enumerate(conversations):
            if i < skip:
                continue
            try:
                # Skip empty conversations
                messages = raw_conv.get("chat_messages", [])
                if not messages:
                    continue
                
                # Skip conversations with no text content
                has_content = any(len(m.get("text", "")) > 10 for m in messages)
                if not has_content:
                    continue
                
                logger.info(
                    f"Processing conversation {i+1}/{len(conversations)}: "
                    f"{raw_conv.get('name', 'Unnamed')[:50]}"
                )
                
                conv = self.process_conversation(raw_conv)
                self._stats["conversations_processed"] += 1
                
                yield conv
                
            except Exception as e:
                logger.error(f"Error processing conversation {i}: {e}")
                self._stats["errors"] += 1
    
    def process_conversation(self, raw_conv: dict) -> ConversationL8:
        """Process a single conversation into full L2-L8 hierarchy."""
        
        # L8: Create conversation root
        conv = ConversationL8.from_raw(raw_conv)
        
        # Get raw messages
        raw_messages = raw_conv.get("chat_messages", [])
        if not raw_messages:
            return conv
        
        # L5: Create message entities
        messages = self._extract_messages(raw_messages, conv.entity_id)
        self._stats["messages_processed"] += len(messages)
        
        # L6: Detect turns (group messages)
        turns = self._detect_turns(messages, conv.entity_id)
        
        # L7: Detect topic segments
        topic_segments = self._detect_topics(turns, conv.entity_id, raw_messages)
        
        # Process deeper levels if configured
        if self.config.min_level <= 4:
            for msg in messages:
                self._process_message_deeply(msg)
        
        # Link children
        conv.children = topic_segments
        
        # Update conversation with LLM summary
        self._enrich_conversation(conv, raw_messages)
        
        return conv
    
    def _extract_messages(
        self, 
        raw_messages: list[dict], 
        conv_id: str,
    ) -> list[MessageL5]:
        """Extract L5 message entities from raw messages."""
        messages = []
        
        for i, raw_msg in enumerate(raw_messages):
            text = raw_msg.get("text", "")
            if not text:
                continue
            
            msg = MessageL5.from_raw(
                raw_message=raw_msg,
                parent_id=conv_id,  # Will be updated with turn_id
                index=i,
                conversation_id=conv_id,
            )
            messages.append(msg)
        
        return messages
    
    def _detect_turns(
        self, 
        messages: list[MessageL5], 
        conv_id: str,
    ) -> list[TurnL6]:
        """Detect conversational turns using LLM."""
        if not messages:
            return []
        
        # For small conversations, use simple grouping by speaker
        if len(messages) < 5:
            return self._simple_turn_grouping(messages, conv_id)
        
        # Prepare messages text for LLM
        messages_text = "\n".join(
            f"[{i}] {m.role}: {m.text[:200]}..."
            if len(m.text) > 200 else f"[{i}] {m.role}: {m.text}"
            for i, m in enumerate(messages)
        )
        
        prompt = TURN_DETECTION_PROMPT.format(messages_text=messages_text)
        
        try:
            response = self.client.complete(prompt)
            self._stats["llm_calls"] += 1
            
            turn_data = self.client.parse_json_response(response)
            
            turns = []
            for t_idx, t in enumerate(turn_data):
                indices = t.get("message_indices", [])
                turn_messages = [messages[i] for i in indices if i < len(messages)]
                
                if turn_messages:
                    turn = TurnL6.from_messages(
                        messages=turn_messages,
                        parent_id=conv_id,  # Will be updated with topic_segment_id
                        index=t_idx,
                        conversation_id=conv_id,
                    )
                    turn.turn_type = t.get("turn_type")
                    turn.is_continuation = t.get("is_continuation", False)
                    
                    # Update message parent IDs
                    for msg in turn_messages:
                        msg.turn_id = turn.entity_id
                        msg.parent_id = turn.entity_id
                    
                    turns.append(turn)
            
            return turns
            
        except Exception as e:
            logger.warning(f"Turn detection failed, using simple grouping: {e}")
            return self._simple_turn_grouping(messages, conv_id)
    
    def _simple_turn_grouping(
        self, 
        messages: list[MessageL5], 
        conv_id: str,
    ) -> list[TurnL6]:
        """Simple turn grouping by consecutive speaker."""
        turns = []
        current_group = []
        current_speaker = None
        
        for msg in messages:
            if msg.role != current_speaker:
                if current_group:
                    turn = TurnL6.from_messages(
                        messages=current_group,
                        parent_id=conv_id,
                        index=len(turns),
                        conversation_id=conv_id,
                    )
                    # Update message references
                    for m in current_group:
                        m.turn_id = turn.entity_id
                        m.parent_id = turn.entity_id
                    turns.append(turn)
                
                current_group = [msg]
                current_speaker = msg.role
            else:
                current_group.append(msg)
        
        # Don't forget last group
        if current_group:
            turn = TurnL6.from_messages(
                messages=current_group,
                parent_id=conv_id,
                index=len(turns),
                conversation_id=conv_id,
            )
            for m in current_group:
                m.turn_id = turn.entity_id
                m.parent_id = turn.entity_id
            turns.append(turn)
        
        return turns
    
    def _detect_topics(
        self, 
        turns: list[TurnL6], 
        conv_id: str,
        raw_messages: list[dict],
    ) -> list[TopicSegmentL7]:
        """Detect topic segments using LLM."""
        if not turns:
            return []
        
        # For small conversations, single topic
        if len(turns) < 3:
            segment = TopicSegmentL7.from_llm(
                turns=turns,
                parent_id=conv_id,
                index=0,
                llm_attrs={"topic_label": "Main Discussion"},
                conversation_id=conv_id,
            )
            for t in turns:
                t.topic_segment_id = segment.entity_id
                t.parent_id = segment.entity_id
            return [segment]
        
        # Prepare conversation text for LLM
        conversation_text = "\n".join(
            f"[{i}] {m.get('sender', 'unknown')}: {m.get('text', '')[:300]}"
            for i, m in enumerate(raw_messages)
            if m.get("text")
        )
        
        prompt = TOPIC_SEGMENTATION_PROMPT.format(conversation_text=conversation_text)
        
        try:
            response = self.client.complete(prompt)
            self._stats["llm_calls"] += 1
            
            segments_data = self.client.parse_json_response(response)
            
            segments = []
            for s_idx, s in enumerate(segments_data):
                start_idx = s.get("start_message_index", 0)
                end_idx = s.get("end_message_index", len(turns) - 1)
                
                # Get turns in this segment
                segment_turns = [
                    t for t in turns 
                    if any(
                        m.source_timestamp and start_idx <= i <= end_idx
                        for i, m in enumerate(t.children)
                    )
                ]
                
                # If no turns matched, use index-based assignment
                if not segment_turns and turns:
                    # Distribute turns across segments
                    turns_per_segment = max(1, len(turns) // len(segments_data))
                    start = s_idx * turns_per_segment
                    end = start + turns_per_segment if s_idx < len(segments_data) - 1 else len(turns)
                    segment_turns = turns[start:end]
                
                if segment_turns:
                    segment = TopicSegmentL7.from_llm(
                        turns=segment_turns,
                        parent_id=conv_id,
                        index=s_idx,
                        llm_attrs=s,
                        conversation_id=conv_id,
                    )
                    
                    for t in segment_turns:
                        t.topic_segment_id = segment.entity_id
                        t.parent_id = segment.entity_id
                    
                    segments.append(segment)
            
            return segments if segments else [self._default_segment(turns, conv_id)]
            
        except Exception as e:
            logger.warning(f"Topic detection failed, using single segment: {e}")
            return [self._default_segment(turns, conv_id)]
    
    def _default_segment(self, turns: list[TurnL6], conv_id: str) -> TopicSegmentL7:
        """Create default single topic segment."""
        segment = TopicSegmentL7.from_llm(
            turns=turns,
            parent_id=conv_id,
            index=0,
            llm_attrs={"topic_label": "Main Discussion"},
            conversation_id=conv_id,
        )
        for t in turns:
            t.topic_segment_id = segment.entity_id
            t.parent_id = segment.entity_id
        return segment
    
    def _process_message_deeply(self, msg: MessageL5) -> None:
        """Process message to L4-L2 levels using LLM."""
        if not msg.text or len(msg.text) < 5:
            return
        
        prompt = FULL_MESSAGE_ANALYSIS_PROMPT.format(
            message_text=msg.text,
            speaker=msg.role,
        )
        
        try:
            response = self.client.complete(prompt)
            self._stats["llm_calls"] += 1
            
            analysis = self.client.parse_json_response(response)
            
            # Update message attributes
            msg_analysis = analysis.get("message_analysis", {})
            msg.message_type = msg_analysis.get("message_type")
            msg.sentiment = msg_analysis.get("overall_sentiment")
            msg.intent = msg_analysis.get("overall_intent")
            msg.emotions = msg_analysis.get("emotions", [])
            msg.has_code = msg_analysis.get("has_code", False)
            
            # Extract sentences (L4)
            sentences = []
            for s_idx, sent_data in enumerate(analysis.get("sentences", [])):
                sentence = SentenceL4.from_llm(
                    sentence_text=sent_data.get("text", ""),
                    parent_id=msg.entity_id,
                    index=s_idx,
                    llm_attrs=sent_data,
                )
                sentence.conversation_id = msg.conversation_id
                sentence.turn_id = msg.turn_id
                
                # Extract spans (L3) if going deeper
                if self.config.min_level <= 3:
                    spans = []
                    for sp_idx, span_data in enumerate(sent_data.get("spans", [])):
                        span = SpanL3.from_llm(
                            span_text=span_data.get("text", ""),
                            parent_id=sentence.entity_id,
                            index=sp_idx,
                            llm_attrs=span_data,
                        )
                        span.conversation_id = msg.conversation_id
                        
                        # Extract words (L2) if going deepest
                        if self.config.min_level <= 2:
                            words = []
                            for w_idx, word_data in enumerate(span_data.get("key_words", [])):
                                word = WordL2.from_llm(
                                    word=word_data.get("text", ""),
                                    parent_id=span.entity_id,
                                    index=w_idx,
                                    llm_attrs=word_data,
                                )
                                word.conversation_id = msg.conversation_id
                                words.append(word)
                            span.children = words
                        
                        spans.append(span)
                    sentence.children = spans
                
                sentences.append(sentence)
            
            msg.children = sentences
            
        except Exception as e:
            logger.warning(f"Deep message processing failed: {e}")
    
    def _enrich_conversation(self, conv: ConversationL8, raw_messages: list[dict]) -> None:
        """Enrich conversation with LLM-generated summary."""
        if conv.summary:
            return  # Already has summary from source
        
        conversation_text = "\n".join(
            f"{m.get('sender', 'unknown')}: {m.get('text', '')[:200]}"
            for m in raw_messages[:20]  # Limit for prompt size
            if m.get("text")
        )
        
        prompt = CONVERSATION_SUMMARY_PROMPT.format(
            conversation_text=conversation_text,
            title=conv.title or "Untitled",
            participants=", ".join(conv.participants),
            message_count=len(raw_messages),
        )
        
        try:
            response = self.client.complete(prompt)
            self._stats["llm_calls"] += 1
            
            summary_data = self.client.parse_json_response(response)
            
            conv.summary = summary_data.get("summary")
            conv.topics = summary_data.get("main_topics", [])
            conv.sentiment = summary_data.get("overall_sentiment")
            conv.emotions = summary_data.get("dominant_emotions", [])
            conv.intent = summary_data.get("conversation_type")
            
        except Exception as e:
            logger.warning(f"Conversation enrichment failed: {e}")
    
    def export_entities(self, conv: ConversationL8, output_path: Path = None, 
                         ingestion_job_id: str = None, source_file: str = None, 
                         source_file_path: str = None) -> Path:
        """Export all entities to JSONL file."""
        output_path = output_path or self.config.output_dir / f"{conv.source_uuid}.jsonl"
        source_file = source_file or output_path.name
        source_file_path = source_file_path or str(output_path)
        
        with open(output_path, "w", encoding="utf-8") as f:
            # Write L8
            f.write(json.dumps(conv.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
            
            # Write L7
            for topic in conv.children:
                f.write(json.dumps(topic.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
                
                # Write L6
                for turn in topic.children:
                    f.write(json.dumps(turn.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
                    
                    # Write L5
                    for msg in turn.children:
                        f.write(json.dumps(msg.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
                        
                        # Write L4
                        for sent in msg.children:
                            f.write(json.dumps(sent.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
                            
                            # Write L3
                            for span in sent.children:
                                f.write(json.dumps(span.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
                                
                                # Write L2
                                for word in span.children:
                                    f.write(json.dumps(word.to_entity_unified(ingestion_job_id, source_file, source_file_path)) + "\n")
        
        return output_path
    
    @property
    def stats(self) -> dict[str, int]:
        return self._stats.copy()
    
    def close(self):
        self.client.close()

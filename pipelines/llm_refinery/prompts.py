"""LLM prompts for extracting L2-L8 hierarchical structure.

These prompts replace rigid spaCy/NLP rules with intelligent LLM understanding.
Each prompt is designed to extract rich semantic information that traditional
NLP pipelines cannot capture.
"""

# =============================================================================
# L7: Topic Segmentation Prompt
# =============================================================================

TOPIC_SEGMENTATION_PROMPT = """You are analyzing a conversation to identify distinct topic segments.

A topic segment is a coherent section where the conversation focuses on a specific subject or theme.
Topic changes occur when:
- The subject matter shifts significantly
- A new question or problem is introduced
- The conversation pivots to a different aspect

INPUT CONVERSATION:
{conversation_text}

Identify the topic segments in this conversation. For EACH segment, provide:

1. `start_message_index`: Which message number starts this topic (0-based)
2. `end_message_index`: Which message number ends this topic (inclusive)
3. `topic_label`: A short label (3-5 words)
4. `topic_description`: One sentence describing what's discussed
5. `is_digression`: true if this is a tangent from the main conversation
6. `topics`: Array of key topic keywords
7. `sentiment`: Overall sentiment of this segment (-1.0 to 1.0)

Return as JSON array:
```json
[
  {{
    "start_message_index": 0,
    "end_message_index": 5,
    "topic_label": "Project Setup Discussion",
    "topic_description": "Initial discussion about setting up the development environment",
    "is_digression": false,
    "topics": ["setup", "environment", "configuration"],
    "sentiment": 0.2
  }}
]
```

Only return the JSON array, no other text."""


# =============================================================================
# L6: Turn Detection Prompt  
# =============================================================================

TURN_DETECTION_PROMPT = """Analyze these messages to identify conversational turns.

A TURN is a continuous block of messages from the same speaker that form a coherent unit.
Multiple consecutive messages from the same person should be grouped if they continue the same thought.
A new turn begins when:
- The speaker changes
- There's a significant pause/topic shift even from same speaker
- The speaker explicitly starts a new thought

MESSAGES:
{messages_text}

For each turn, provide:
1. `message_indices`: Array of message indices (0-based) in this turn
2. `speaker`: Who is speaking
3. `turn_type`: "opening", "response", "clarification", "follow_up", "closing"
4. `is_continuation`: true if continues the previous turn's thought

Return as JSON array:
```json
[
  {{
    "message_indices": [0],
    "speaker": "human",
    "turn_type": "opening",
    "is_continuation": false
  }},
  {{
    "message_indices": [1, 2],
    "speaker": "assistant", 
    "turn_type": "response",
    "is_continuation": false
  }}
]
```

Only return the JSON array, no other text."""


# =============================================================================
# L4: Sentence Extraction Prompt
# =============================================================================

SENTENCE_EXTRACTION_PROMPT = """Extract and analyze sentences from this message.

Consider natural speech patterns - not just punctuation. Informal text may have:
- Run-on sentences that should be split semantically
- Sentence fragments that are complete thoughts
- Lists that function as sentences

MESSAGE:
{message_text}

For EACH sentence, provide:
1. `text`: The sentence text
2. `sentence_type`: "declarative", "question", "command", "exclamation", "fragment"
3. `complexity`: "simple", "compound", "complex"
4. `is_rhetorical`: true if a rhetorical question
5. `sentiment`: Sentiment score (-1.0 to 1.0)
6. `intent`: The purpose ("inform", "request", "clarify", "agree", "disagree", "suggest", etc.)
7. `emotions`: Array of emotions detected

Return as JSON array:
```json
[
  {{
    "text": "How do I fix this error?",
    "sentence_type": "question",
    "complexity": "simple",
    "is_rhetorical": false,
    "sentiment": -0.2,
    "intent": "request",
    "emotions": ["confused", "frustrated"]
  }}
]
```

Only return the JSON array, no other text."""


# =============================================================================
# L3: Span Extraction Prompt
# =============================================================================

SPAN_EXTRACTION_PROMPT = """Break this sentence into meaningful spans/phrases.

A SPAN is a semantically coherent chunk - a phrase that carries meaning together.
Types of spans:
- Noun phrases (the subject/object)
- Verb phrases (the action)
- Prepositional phrases (location, time, manner)
- Clauses (dependent/independent)

SENTENCE:
{sentence_text}

For EACH span, provide:
1. `text`: The span text
2. `span_type`: "noun_phrase", "verb_phrase", "prepositional", "clause", "modifier"
3. `is_complete_thought`: true if can stand alone
4. `named_entities`: Array of entities found, each with "text", "type" (PERSON, ORG, TECH, DATE, etc.)
5. `sentiment`: Sentiment of this span (-1.0 to 1.0)
6. `intent`: Purpose of this span if detectable

Return as JSON array:
```json
[
  {{
    "text": "the configuration file",
    "span_type": "noun_phrase",
    "is_complete_thought": false,
    "named_entities": [],
    "sentiment": 0.0
  }},
  {{
    "text": "contains an error",
    "span_type": "verb_phrase", 
    "is_complete_thought": false,
    "named_entities": [],
    "sentiment": -0.3
  }}
]
```

Only return the JSON array, no other text."""


# =============================================================================
# L2: Word Analysis Prompt
# =============================================================================

WORD_ANALYSIS_PROMPT = """Analyze the words in this span for semantic attributes.

Focus on MEANINGFUL words - skip trivial stop words unless they're significant.

SPAN:
{span_text}

For each SIGNIFICANT word, provide:
1. `text`: The word
2. `word_type`: "noun", "verb", "adjective", "adverb", "entity", "technical_term", "other"
3. `is_key_term`: true if important to the meaning
4. `canonical_form`: Base/lemma form (e.g., "running" -> "run")
5. `semantic_role`: "agent", "action", "object", "attribute", "location", "time", "other"
6. `sentiment`: Sentiment contribution (-1.0 to 1.0)

Return as JSON array:
```json
[
  {{
    "text": "configuration",
    "word_type": "noun",
    "is_key_term": true,
    "canonical_form": "configuration",
    "semantic_role": "object",
    "sentiment": 0.0
  }},
  {{
    "text": "error",
    "word_type": "noun",
    "is_key_term": true,
    "canonical_form": "error",
    "semantic_role": "object",
    "sentiment": -0.5
  }}
]
```

Only return the JSON array, no other text."""


# =============================================================================
# Full Message Analysis (Combined for Efficiency)
# =============================================================================

FULL_MESSAGE_ANALYSIS_PROMPT = """Analyze this message and extract its complete hierarchical structure.

MESSAGE:
{message_text}

SPEAKER: {speaker}

Extract the following hierarchy:
1. SENTENCES: Break into individual sentences
2. SPANS: For each sentence, identify meaningful phrases
3. KEY_WORDS: For each span, identify significant words

REQUIRED FIELDS (do not omit any):
- sentence_type: MUST be one of: "declarative", "question", "command", "exclamation"
- span_type: MUST be one of: "noun_phrase", "verb_phrase", "prepositional", "clause", "modifier"
- word_type: MUST be one of: "noun", "verb", "adjective", "adverb", "entity", "technical_term"
- is_key_term: MUST be true or false
- sentiment: MUST be a number between -1.0 and 1.0

Return as JSON:
```json
{{
  "message_analysis": {{
    "message_type": "question",
    "overall_sentiment": -0.2,
    "overall_intent": "request",
    "emotions": ["curious", "frustrated"],
    "has_code": false
  }},
  "sentences": [
    {{
      "text": "How do I fix this error?",
      "sentence_type": "question",
      "complexity": "simple",
      "sentiment": -0.2,
      "intent": "request",
      "spans": [
        {{
          "text": "How do I fix",
          "span_type": "clause",
          "key_words": [
            {{"text": "fix", "word_type": "verb", "is_key_term": true, "sentiment": 0.1}}
          ]
        }},
        {{
          "text": "this error",
          "span_type": "noun_phrase",
          "entities": [{{"text": "error", "entity_type": "CONCEPT"}}],
          "key_words": [
            {{"text": "error", "word_type": "noun", "is_key_term": true, "sentiment": -0.5}}
          ]
        }}
      ]
    }}
  ]
}}
```

Only return the JSON, no other text."""


# =============================================================================
# Conversation Summary Prompt
# =============================================================================

CONVERSATION_SUMMARY_PROMPT = """Analyze this entire conversation and provide a structured summary.

CONVERSATION:
{conversation_text}

METADATA:
- Title: {title}
- Participants: {participants}
- Message Count: {message_count}

Provide:
1. `summary`: 2-3 sentence summary of the conversation
2. `main_topics`: Array of main topics discussed
3. `key_decisions`: Any decisions made
4. `action_items`: Any tasks or next steps mentioned
5. `overall_sentiment`: Average sentiment (-1.0 to 1.0)
6. `dominant_emotions`: Top emotions across conversation
7. `conversation_type`: "support", "brainstorm", "review", "planning", "casual", "technical"

Return as JSON:
```json
{{
  "summary": "The user requested help with...",
  "main_topics": ["error handling", "configuration"],
  "key_decisions": ["Use approach X"],
  "action_items": ["Test the solution"],
  "overall_sentiment": 0.3,
  "dominant_emotions": ["curious", "helpful"],
  "conversation_type": "support"
}}
```

Only return the JSON, no other text."""


# =============================================================================
# Batch Processing Prompts (for efficiency with large conversations)
# =============================================================================

BATCH_SENTENCES_PROMPT = """Extract sentences from these messages efficiently.

MESSAGES (indexed):
{indexed_messages}

For EACH message, extract its sentences. Return a mapping of message_index to sentences.

Return as JSON:
```json
{{
  "0": [
    {{"text": "First sentence.", "type": "declarative", "sentiment": 0.1}},
    {{"text": "Second sentence?", "type": "question", "sentiment": -0.1}}
  ],
  "1": [
    {{"text": "Response sentence.", "type": "declarative", "sentiment": 0.3}}
  ]
}}
```

Only return the JSON, no other text."""

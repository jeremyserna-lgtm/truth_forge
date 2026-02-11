
// Level 2: Word
export interface Word {
  id: string; // L2 ID
  text: string;
  parentId: string; // L4 ID
  type: 'word';
}

// Level 3: Span (Named Entity or Phrase)
export interface Span {
  id: string; // L3 ID
  text: string;
  label: string; // e.g., PERSON, DATE, NOUN_PHRASE
  parentId: string; // L4 ID
  type: 'span';
}

// Level 4: Sentence
export interface Sentence {
  id: string; // L4 ID
  text: string;
  words: Word[];
  spans: Span[];
  parentId: string; // L5 ID
  wordCount: number;
  spanCount: number;
}

// Level 5: Message
export interface Message {
  id: string; // L5 ID
  role: 'user' | 'model' | 'system' | string;
  content: string;
  sentences: Sentence[];
  parentId: string; // L6 ID
  sentenceCount: number;
}

// Level 6: Turn
export interface Turn {
  id: string; // L6 ID
  messages: Message[];
  parentId: string; // L7 ID
  messageCount: number;
}

// Level 7: Topic Segment
export interface TopicSegment {
  id: string; // L7 ID
  title: string;
  summary: string;
  turns: Turn[];
  parentId: string; // L8 ID
  turnCount: number;
  sentiment?: 'positive' | 'neutral' | 'negative';
  keywords?: string[];
  embedding?: number[]; // Vector for similarity
}

// Level 8: Conversation
export interface Conversation {
  id: string; // L8 ID
  title: string;
  topics: TopicSegment[];
  topicCount: number;
  sourceFile?: string; // Original file name if imported
  sourceFormat?: string; // Original format (claude, chatgpt, gemini)
}

// Denormalized Row for Display/Export
export interface DenormalizedRow {
  l8_id: string; // Conversation
  l7_id: string; // Topic
  l6_id: string; // Turn
  l5_id: string; // Message
  l4_id: string; // Sentence
  l3_id?: string; // Span (Nullable)
  l2_id?: string; // Word (Nullable)
  level: number;
  type: 'word' | 'span';
  content: string;
  meta: string; // Role for message, label for span, etc.
  
  // Counts context (Optional but useful for verification)
  topic_count: number;
  turn_count: number;
  message_count: number;
  sentence_count: number;
  word_count?: number;
  span_count?: number;
}

export type ProcessingStatus = 'idle' | 'analyzing_structure' | 'calculating_embeddings' | 'parsing_sentences' | 'complete' | 'error' | 'cancelling';

export interface DetailedProgress {
  stage: 'topics' | 'embeddings' | 'messages' | 'complete';
  currentItem: number;
  totalItems: number;
  currentLabel: string;
  percentage: number;
}

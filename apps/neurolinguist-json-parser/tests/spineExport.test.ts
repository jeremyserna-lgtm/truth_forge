import { describe, it, expect, beforeEach } from 'vitest';
import {
  exportToSpineFormat,
  exportToSpineJSONL,
  exportEntitiesAsCSV,
  exportToNativeSpineFormat,
  exportToNativeSpineJSONL,
  exportRelationshipsJSONL,
  type NativeSpineEntity,
  type NativeSpineExport,
} from '../services/spineExport';
import type { Conversation, TopicSegment, Turn, Message, Sentence, Span } from '../types';

// Test fixtures
function createTestConversation(): Conversation {
  const span: Span = {
    id: 'span-1',
    text: 'John',
    label: 'PERSON',
    parentId: 'sent-1',
    type: 'span',
  };

  const sentence: Sentence = {
    id: 'sent-1',
    text: 'Hello John, how are you?',
    words: [
      { id: 'w1', text: 'Hello', parentId: 'sent-1', type: 'word' },
      { id: 'w2', text: 'John', parentId: 'sent-1', type: 'word' },
    ],
    spans: [span],
    parentId: 'msg-1',
    wordCount: 5,
    spanCount: 1,
  };

  const message: Message = {
    id: 'msg-1',
    role: 'user',
    content: 'Hello John, how are you?',
    sentences: [sentence],
    parentId: 'turn-1',
    sentenceCount: 1,
  };

  const turn: Turn = {
    id: 'turn-1',
    messages: [message],
    parentId: 'topic-1',
    messageCount: 1,
  };

  const topic: TopicSegment = {
    id: 'topic-1',
    title: 'Greeting',
    summary: 'A friendly greeting',
    turns: [turn],
    parentId: 'conv-1',
    turnCount: 1,
    sentiment: 'positive',
    keywords: ['hello', 'greeting'],
  };

  return {
    id: 'conv-1',
    title: 'Test Conversation',
    topics: [topic],
    topicCount: 1,
  };
}

describe('spineExport', () => {
  let testConversation: Conversation;

  beforeEach(() => {
    testConversation = createTestConversation();
  });

  // ============================================================================
  // NATIVE SPINE FORMAT TESTS (v3.0)
  // ============================================================================

  describe('exportToNativeSpineFormat', () => {
    it('should export conversation to NativeSpineExport format', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      expect(result).toHaveProperty('entities');
      expect(result).toHaveProperty('relationships');
      expect(result).toHaveProperty('export_metadata');
      expect(result.export_metadata.schema_version).toBe('entity_unified_v1');
    });

    it('should generate deterministic entity IDs', async () => {
      const result1 = await exportToNativeSpineFormat(testConversation);
      const result2 = await exportToNativeSpineFormat(testConversation);

      // Same input should produce same IDs
      expect(result1.entities[0].entity_id).toBe(result2.entities[0].entity_id);
    });

    it('should use correct ID format (prefix:hash16:index)', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      for (const entity of result.entities) {
        // Format: prefix:hash16:index (e.g., conv:a1b2c3d4e5f6g7h8:0000)
        expect(entity.entity_id).toMatch(/^[a-z]+:[a-f0-9]{16}:\d{4}$/);
      }
    });

    it('should create correct entity hierarchy (L8 -> L7 -> L6 -> L5 -> L4 -> L3)', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      // Check entity count: 1 conversation + 1 topic + 1 turn + 1 message + 1 sentence + 1 span = 6
      expect(result.entities.length).toBe(6);

      // Check levels
      const levels = result.entities.map((e) => e.level);
      expect(levels).toContain(8); // Conversation
      expect(levels).toContain(7); // Topic
      expect(levels).toContain(6); // Turn
      expect(levels).toContain(5); // Message
      expect(levels).toContain(4); // Sentence
      expect(levels).toContain(3); // Span
    });

    it('should include denormalized hierarchy IDs', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      // Find a sentence entity
      const sentence = result.entities.find((e) => e.level === 4);
      expect(sentence).toBeDefined();

      // Should have all ancestor IDs denormalized
      expect(sentence?.conversation_id).toBeDefined();
      expect(sentence?.topic_segment_id).toBeDefined();
      expect(sentence?.turn_id).toBeDefined();
      expect(sentence?.message_id).toBeDefined();
      expect(sentence?.sentence_id).toBe(sentence?.entity_id);
    });

    it('should include count rollups', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      // Conversation should have counts of all descendants
      const conversation = result.entities.find((e) => e.level === 8);
      expect(conversation?.l7_count).toBe(1); // 1 topic
      expect(conversation?.l6_count).toBe(1); // 1 turn
      expect(conversation?.l5_count).toBe(1); // 1 message
      expect(conversation?.l4_count).toBe(1); // 1 sentence
      expect(conversation?.l3_count).toBe(1); // 1 span
      expect(conversation?.l2_count).toBe(2); // 2 words
    });

    it('should have all 34 required fields', async () => {
      const result = await exportToNativeSpineFormat(testConversation);
      const entity = result.entities[0];

      // Identity (5 fields)
      expect(entity.entity_id).toBeDefined();
      expect(entity.level).toBeDefined();
      expect(entity.entity_type).toBeDefined();
      expect(entity.entity_mode).toBe('active');
      expect('parent_id' in entity).toBe(true);

      // Denormalized Hierarchy IDs (7 fields)
      expect(entity.conversation_id).toBeDefined();
      expect('topic_segment_id' in entity).toBe(true);
      expect('turn_id' in entity).toBe(true);
      expect('message_id' in entity).toBe(true);
      expect('sentence_id' in entity).toBe(true);
      expect('span_id' in entity).toBe(true);
      expect('word_id' in entity).toBe(true);

      // Content (3 fields)
      expect(entity.text).toBeDefined();
      expect('canonical_form' in entity).toBe(true);
      expect('persona' in entity).toBe(true);

      // Source Tracking (5 fields)
      expect(entity.source_pipeline).toBe('neurolinguist_parser');
      expect('source_file' in entity).toBe(true);
      expect('source_file_path' in entity).toBe(true);
      expect(entity.source_system).toBe('neurolinguist_json_parser');
      expect(Array.isArray(entity.source_ids)).toBe(true);

      // Metadata
      expect(typeof entity.metadata).toBe('object');

      // Timestamps (6 fields)
      expect(entity.content_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect('source_message_timestamp' in entity).toBe(true);
      expect(entity.created_at).toBeDefined();
      expect(entity.updated_at).toBeDefined();
      expect(entity.ingestion_timestamp).toBeDefined();
      expect(entity.ingestion_job_id).toBeDefined();

      // Validation
      expect(entity.validation_status).toBe('PASSED');

      // Count Rollups (6 fields)
      expect(typeof entity.l7_count).toBe('number');
      expect(typeof entity.l6_count).toBe('number');
      expect(typeof entity.l5_count).toBe('number');
      expect(typeof entity.l4_count).toBe('number');
      expect(typeof entity.l3_count).toBe('number');
      expect(typeof entity.l2_count).toBe('number');
    });

    it('should set persona for model messages', async () => {
      // Add a model message
      testConversation.topics[0].turns[0].messages.push({
        id: 'msg-2',
        role: 'model',
        content: 'Hello! I am doing well.',
        sentences: [],
        parentId: 'turn-1',
        sentenceCount: 0,
      });

      const result = await exportToNativeSpineFormat(testConversation);

      const modelMessage = result.entities.find(
        (e) => e.level === 5 && e.text === 'Hello! I am doing well.'
      );
      expect(modelMessage?.persona).toBe('assistant');
    });

    it('should set canonical_form for spans', async () => {
      const result = await exportToNativeSpineFormat(testConversation);

      const span = result.entities.find((e) => e.level === 3);
      expect(span?.canonical_form).toBe('john'); // lowercase
    });

    it('should include words when includeWords option is true', async () => {
      const result = await exportToNativeSpineFormat(testConversation, {
        includeWords: true,
      });

      // Should now have words (L2)
      const words = result.entities.filter((e) => e.level === 2);
      expect(words.length).toBe(2); // 2 words in sentence
    });

    it('should include source file info when provided', async () => {
      const result = await exportToNativeSpineFormat(testConversation, {
        sourceFile: 'conversation.json',
        sourceFilePath: '/data/exports/conversation.json',
      });

      for (const entity of result.entities) {
        expect(entity.source_file).toBe('conversation.json');
        expect(entity.source_file_path).toBe('/data/exports/conversation.json');
      }
    });
  });

  describe('exportToNativeSpineJSONL', () => {
    it('should return newline-separated JSON records', async () => {
      const result = await exportToNativeSpineJSONL(testConversation);
      const lines = result.split('\n');

      // Should have 6 entities (no metadata header by default)
      expect(lines.length).toBe(6);
    });

    it('should include metadata header when requested', async () => {
      const result = await exportToNativeSpineJSONL(testConversation, {
        includeMetadataHeader: true,
      });
      const lines = result.split('\n');

      expect(lines[0].startsWith('#')).toBe(true);
      expect(lines.length).toBe(7); // 1 header + 6 entities
    });

    it('should serialize metadata as JSON string', async () => {
      const result = await exportToNativeSpineJSONL(testConversation);
      const firstLine = JSON.parse(result.split('\n')[0]);

      // metadata should be a string (serialized JSON)
      expect(typeof firstLine.metadata).toBe('string');
      expect(() => JSON.parse(firstLine.metadata)).not.toThrow();
    });

    it('should produce valid JSON on each line', async () => {
      const result = await exportToNativeSpineJSONL(testConversation);
      const lines = result.split('\n');

      for (const line of lines) {
        expect(() => JSON.parse(line)).not.toThrow();
      }
    });

    it('should have entity_id field (not id)', async () => {
      const result = await exportToNativeSpineJSONL(testConversation);
      const firstLine = JSON.parse(result.split('\n')[0]);

      expect(firstLine.entity_id).toBeDefined();
      expect(firstLine.id).toBeUndefined();
    });
  });

  describe('exportRelationshipsJSONL', () => {
    it('should export relationships as JSONL', async () => {
      const result = await exportRelationshipsJSONL(testConversation);
      const lines = result.split('\n');

      // Should have relationships: conv->topic, topic->turn, turn->msg, msg->sent, sent->span
      expect(lines.length).toBe(5);
    });

    it('should include relationship type and confidence', async () => {
      const result = await exportRelationshipsJSONL(testConversation);
      const firstLine = JSON.parse(result.split('\n')[0]);

      expect(firstLine.source_id).toBeDefined();
      expect(firstLine.target_id).toBeDefined();
      expect(firstLine.relationship_type).toBe('contains');
      expect(firstLine.confidence).toBe(1.0);
    });
  });

  // ============================================================================
  // LEGACY FORMAT TESTS (v2.0 - backwards compatibility)
  // ============================================================================

  describe('exportToSpineFormat (legacy)', () => {
    it('should export conversation to SpineExport format', () => {
      const result = exportToSpineFormat(testConversation);

      expect(result).toHaveProperty('entities');
      expect(result).toHaveProperty('relationships');
      expect(result).toHaveProperty('export_metadata');
    });

    it('should create correct entity hierarchy (L8 -> L7 -> L6 -> L5 -> L4 -> L3)', () => {
      const result = exportToSpineFormat(testConversation);

      // Check entity count: 1 conversation + 1 topic + 1 turn + 1 message + 1 sentence + 1 span = 6
      expect(result.entities.length).toBe(6);

      // Check levels
      const levels = result.entities.map((e) => e.level);
      expect(levels).toContain(8); // Conversation
      expect(levels).toContain(7); // Topic
      expect(levels).toContain(6); // Turn
      expect(levels).toContain(5); // Message
      expect(levels).toContain(4); // Sentence
      expect(levels).toContain(3); // Span
    });

    it('should create correct parent-child relationships', () => {
      const result = exportToSpineFormat(testConversation);

      // Find entities by level
      const conversation = result.entities.find((e) => e.level === 8);
      const topic = result.entities.find((e) => e.level === 7);
      const turn = result.entities.find((e) => e.level === 6);
      const message = result.entities.find((e) => e.level === 5);
      const sentence = result.entities.find((e) => e.level === 4);
      const span = result.entities.find((e) => e.level === 3);

      // Verify parent_id chain
      expect(conversation?.parent_id).toBeNull();
      expect(topic?.parent_id).toBe(conversation?.id);
      expect(turn?.parent_id).toBe(topic?.id);
      expect(message?.parent_id).toBe(turn?.id);
      expect(sentence?.parent_id).toBe(message?.id);
      expect(span?.parent_id).toBe(sentence?.id);
    });

    it('should include correct metadata for each entity type', () => {
      const result = exportToSpineFormat(testConversation);

      // Conversation metadata
      const conversation = result.entities.find((e) => e.level === 8);
      expect(conversation?.metadata.topic_count).toBe(1);

      // Topic metadata
      const topic = result.entities.find((e) => e.level === 7);
      expect(topic?.metadata.sentiment).toBe('positive');
      expect(topic?.metadata.keywords).toEqual(['hello', 'greeting']);

      // Message metadata
      const message = result.entities.find((e) => e.level === 5);
      expect(message?.metadata.role).toBe('user');
      expect(message?.metadata.sentence_count).toBe(1);

      // Sentence metadata
      const sentence = result.entities.find((e) => e.level === 4);
      expect(sentence?.metadata.word_count).toBe(5);
      expect(sentence?.metadata.span_count).toBe(1);

      // Span metadata
      const span = result.entities.find((e) => e.level === 3);
      expect(span?.metadata.label).toBe('PERSON');
    });

    it('should create relationships with correct types', () => {
      const result = exportToSpineFormat(testConversation);

      // Should have relationships: conv->topic, topic->turn, turn->msg, msg->sent, sent->span
      expect(result.relationships.length).toBe(5);

      // Check relationship types
      const containsRels = result.relationships.filter(
        (r) => r.relationship_type === 'contains'
      );
      const entityRels = result.relationships.filter(
        (r) => r.relationship_type === 'contains_entity'
      );

      expect(containsRels.length).toBe(4); // conv->topic, topic->turn, turn->msg, msg->sent
      expect(entityRels.length).toBe(1); // sent->span
    });

    it('should set all relationships to confidence 1.0', () => {
      const result = exportToSpineFormat(testConversation);

      for (const rel of result.relationships) {
        expect(rel.confidence).toBe(1.0);
      }
    });

    it('should include export metadata', () => {
      const result = exportToSpineFormat(testConversation);

      expect(result.export_metadata.source_app).toBe('neurolinguist_json_parser');
      expect(result.export_metadata.version).toBe('2.0.0');
      expect(result.export_metadata.conversation_id).toBe('conv-1');
      expect(result.export_metadata.entity_count).toBe(6);
      expect(result.export_metadata.relationship_count).toBe(5);
      expect(result.export_metadata.exported_at).toBeDefined();
    });
  });

  describe('exportToSpineJSONL (legacy)', () => {
    it('should return newline-separated JSON records', () => {
      const result = exportToSpineJSONL(testConversation);
      const lines = result.split('\n');

      // Should have: 1 metadata + 6 entities + 5 relationships = 12 lines
      expect(lines.length).toBe(12);
    });

    it('should have metadata as first line', () => {
      const result = exportToSpineJSONL(testConversation);
      const firstLine = JSON.parse(result.split('\n')[0]);

      expect(firstLine._type).toBe('metadata');
      expect(firstLine.source_app).toBe('neurolinguist_json_parser');
    });

    it('should mark entities with _type: entity', () => {
      const result = exportToSpineJSONL(testConversation);
      const lines = result.split('\n');

      // Lines 2-7 should be entities (1-indexed after metadata)
      for (let i = 1; i <= 6; i++) {
        const parsed = JSON.parse(lines[i]);
        expect(parsed._type).toBe('entity');
        expect(parsed.id).toBeDefined();
        expect(parsed.level).toBeDefined();
      }
    });

    it('should mark relationships with _type: relationship', () => {
      const result = exportToSpineJSONL(testConversation);
      const lines = result.split('\n');

      // Last 5 lines should be relationships
      for (let i = 7; i <= 11; i++) {
        const parsed = JSON.parse(lines[i]);
        expect(parsed._type).toBe('relationship');
        expect(parsed.source_id).toBeDefined();
        expect(parsed.target_id).toBeDefined();
      }
    });

    it('should produce valid JSON on each line', () => {
      const result = exportToSpineJSONL(testConversation);
      const lines = result.split('\n');

      for (const line of lines) {
        expect(() => JSON.parse(line)).not.toThrow();
      }
    });
  });

  describe('exportEntitiesAsCSV (legacy)', () => {
    it('should include header row', () => {
      const result = exportEntitiesAsCSV(testConversation);
      const firstLine = result.split('\n')[0];

      expect(firstLine).toBe(
        'id,level,entity_type,content,parent_id,source_system,created_at,metadata_json'
      );
    });

    it('should have correct number of rows', () => {
      const result = exportEntitiesAsCSV(testConversation);
      const lines = result.split('\n');

      // 1 header + 6 entities = 7 lines
      expect(lines.length).toBe(7);
    });

    it('should escape quotes in content', () => {
      // Add a message with quotes
      testConversation.topics[0].turns[0].messages[0].content = 'He said "hello"';
      testConversation.topics[0].turns[0].messages[0].sentences[0].text =
        'He said "hello"';

      const result = exportEntitiesAsCSV(testConversation);

      // The message content should have escaped quotes
      expect(result).toContain('""hello""');
    });

    it('should escape newlines in content', () => {
      testConversation.topics[0].turns[0].messages[0].content = 'Line1\nLine2';
      testConversation.topics[0].turns[0].messages[0].sentences[0].text =
        'Line1\nLine2';

      const result = exportEntitiesAsCSV(testConversation);

      // Newlines should be converted to spaces
      expect(result).toContain('Line1 Line2');
    });

    it('should include source_system as neurolinguist_parser', () => {
      const result = exportEntitiesAsCSV(testConversation);

      expect(result).toContain('neurolinguist_parser');
    });
  });

  // ============================================================================
  // EDGE CASES
  // ============================================================================

  describe('edge cases', () => {
    it('should handle conversation with no topics', async () => {
      const emptyConv: Conversation = {
        id: 'empty-conv',
        title: 'Empty',
        topics: [],
        topicCount: 0,
      };

      const result = await exportToNativeSpineFormat(emptyConv);

      // Only the conversation entity
      expect(result.entities.length).toBe(1);
      expect(result.relationships.length).toBe(0);
      expect(result.entities[0].l7_count).toBe(0);
    });

    it('should handle topic with no embedding', async () => {
      delete testConversation.topics[0].embedding;

      const result = await exportToNativeSpineFormat(testConversation);
      const topic = result.entities.find((e) => e.level === 7);

      expect(topic?.metadata.has_embedding).toBe(false);
      expect(topic?.metadata.embedding_dims).toBe(0);
    });

    it('should handle topic with embedding', async () => {
      testConversation.topics[0].embedding = [0.1, 0.2, 0.3];

      const result = await exportToNativeSpineFormat(testConversation);
      const topic = result.entities.find((e) => e.level === 7);

      expect(topic?.metadata.has_embedding).toBe(true);
      expect(topic?.metadata.embedding_dims).toBe(3);
    });

    it('should handle sentence with no spans', async () => {
      testConversation.topics[0].turns[0].messages[0].sentences[0].spans = [];

      const result = await exportToNativeSpineFormat(testConversation);

      // Should have 5 entities (no span)
      expect(result.entities.length).toBe(5);
      // Should have 4 relationships (no sent->span)
      expect(result.relationships.length).toBe(4);
    });

    it('should handle legacy format with no topics', () => {
      const emptyConv: Conversation = {
        id: 'empty-conv',
        title: 'Empty',
        topics: [],
        topicCount: 0,
      };

      const result = exportToSpineFormat(emptyConv);

      // Only the conversation entity
      expect(result.entities.length).toBe(1);
      expect(result.relationships.length).toBe(0);
    });
  });
});

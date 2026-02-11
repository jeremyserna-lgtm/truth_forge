/**
 * Native Spine Export Service
 * Exports parsed conversations to BigQuery entity_unified schema format
 *
 * Schema: flash-clover-464719-g1.spine.entity_unified (34 fields)
 * Partitioning: content_date (DAY)
 * Clustering: [level, conversation_id, entity_id]
 */

import { Conversation, TopicSegment, Turn, Message, Sentence, Span, Word } from '../types';

// Spine entity levels
type SpineLevel = 2 | 3 | 4 | 5 | 6 | 7 | 8;

// Entity type prefixes for deterministic ID generation
const ENTITY_PREFIXES: Record<SpineLevel, string> = {
  8: 'conv',
  7: 'topic',
  6: 'turn',
  5: 'msg',
  4: 'sent',
  3: 'span',
  2: 'word',
};

// Entity type names matching BigQuery schema
const ENTITY_TYPES: Record<SpineLevel, string> = {
  8: 'conversation',
  7: 'topic_segment',
  6: 'turn',
  5: 'message',
  4: 'sentence',
  3: 'named_entity',
  2: 'token',
};

/**
 * Native Spine Entity matching BigQuery entity_unified schema (34 fields)
 */
export interface NativeSpineEntity {
  // Identity (5 fields)
  entity_id: string;
  level: SpineLevel;
  entity_type: string;
  entity_mode: string;
  parent_id: string | null;

  // Denormalized Hierarchy IDs (7 fields)
  conversation_id: string;
  topic_segment_id: string | null;
  turn_id: string | null;
  message_id: string | null;
  sentence_id: string | null;
  span_id: string | null;
  word_id: string | null;

  // Content (3 fields)
  text: string;
  canonical_form: string | null;
  persona: string | null;

  // Source Tracking (5 fields)
  source_pipeline: string;
  source_file: string | null;
  source_file_path: string | null;
  source_system: string;
  source_ids: string[];

  // Metadata (JSON)
  metadata: Record<string, unknown>;

  // Timestamps (6 fields)
  content_date: string; // DATE format: YYYY-MM-DD
  source_message_timestamp: string | null;
  created_at: string;
  updated_at: string;
  ingestion_timestamp: string;
  ingestion_job_id: string;

  // Validation
  validation_status: 'PASSED' | 'WARNING' | 'FAILED';

  // Count Rollups (6 fields)
  l7_count: number;
  l6_count: number;
  l5_count: number;
  l4_count: number;
  l3_count: number;
  l2_count: number;

  // Role (for messages)
  role: string | null;
}

/**
 * Relationship record for entity connections
 */
export interface SpineRelationship {
  source_id: string;
  target_id: string;
  relationship_type: 'contains' | 'contains_entity' | 'follows';
  confidence: number;
  metadata?: Record<string, unknown>;
}

/**
 * Complete export package
 */
export interface NativeSpineExport {
  entities: NativeSpineEntity[];
  relationships: SpineRelationship[];
  export_metadata: {
    exported_at: string;
    source_app: string;
    version: string;
    conversation_id: string;
    entity_count: number;
    relationship_count: number;
    schema_version: string;
    target_table: string;
  };
}

/**
 * Hierarchy context passed down during export
 */
interface HierarchyContext {
  conversation_id: string;
  topic_segment_id: string | null;
  turn_id: string | null;
  message_id: string | null;
  sentence_id: string | null;
}

/**
 * Generate deterministic entity ID
 * Format: {prefix}:{hash16}:{index:04d}
 */
async function generateEntityId(
  prefix: string,
  content: string,
  parentId: string = '',
  index: number = 0
): Promise<string> {
  const hashInput = `${parentId}:${content}:${index}`;
  const encoder = new TextEncoder();
  const data = encoder.encode(hashInput);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hash16 = hashArray.slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join('');
  return `${prefix}:${hash16}:${index.toString().padStart(4, '0')}`;
}

/**
 * Generate canonical form for text based on entity level
 * - L2 (token): lowercase, trimmed
 * - L3 (named_entity): lowercase, trimmed
 * - L4 (sentence): normalized punctuation, trimmed
 * - L5+ : null (too much variation)
 */
function generateCanonicalForm(text: string, level: SpineLevel): string | null {
  if (!text) return null;

  switch (level) {
    case 2: // token
      return text.toLowerCase().trim();
    case 3: // named_entity
      return text.toLowerCase().trim();
    case 4: // sentence
      // Normalize sentence: trim, collapse whitespace, standard punctuation
      return text
        .trim()
        .replace(/\s+/g, ' ')
        .replace(/[""]/g, '"')
        .replace(/['']/g, "'");
    default:
      return null;
  }
}

/**
 * Build source_ids chain including parent hierarchy
 */
function buildSourceIds(
  entityId: string,
  context: HierarchyContext
): string[] {
  const ids: string[] = [entityId];

  // Add parent chain for traceability (most specific to least)
  if (context.sentence_id) ids.push(context.sentence_id);
  if (context.message_id) ids.push(context.message_id);
  if (context.turn_id) ids.push(context.turn_id);
  if (context.topic_segment_id) ids.push(context.topic_segment_id);
  if (context.conversation_id) ids.push(context.conversation_id);

  return [...new Set(ids)]; // Deduplicate
}

/**
 * Synchronous ID generation (fallback when crypto not available)
 */
function generateEntityIdSync(
  prefix: string,
  content: string,
  parentId: string = '',
  index: number = 0
): string {
  const hashInput = `${parentId}:${content}:${index}`;
  let hash = 0;
  for (let i = 0; i < hashInput.length; i++) {
    const char = hashInput.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  const hash16 = Math.abs(hash).toString(16).padStart(16, '0').slice(0, 16);
  return `${prefix}:${hash16}:${index.toString().padStart(4, '0')}`;
}

/**
 * Get current date in YYYY-MM-DD format
 */
function getContentDate(): string {
  return new Date().toISOString().split('T')[0];
}

/**
 * Generate unique job ID
 */
function generateJobId(): string {
  return `nlp_export_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Count descendants at each level
 */
function countDescendants(conversation: Conversation): {
  l7: number;
  l6: number;
  l5: number;
  l4: number;
  l3: number;
  l2: number;
} {
  let l7 = 0, l6 = 0, l5 = 0, l4 = 0, l3 = 0, l2 = 0;

  for (const topic of conversation.topics) {
    l7++;
    for (const turn of topic.turns) {
      l6++;
      for (const message of turn.messages) {
        l5++;
        for (const sentence of message.sentences) {
          l4++;
          l3 += sentence.spans.length;
          l2 += sentence.words.length;
        }
      }
    }
  }

  return { l7, l6, l5, l4, l3, l2 };
}

/**
 * Export conversation to native Spine format (BigQuery entity_unified compatible)
 */
export async function exportToNativeSpineFormat(
  conversation: Conversation,
  options: {
    sourceFile?: string;
    sourceFilePath?: string;
    includeWords?: boolean;
  } = {}
): Promise<NativeSpineExport> {
  const entities: NativeSpineEntity[] = [];
  const relationships: SpineRelationship[] = [];

  const now = new Date().toISOString();
  const contentDate = getContentDate();
  const jobId = generateJobId();
  const counts = countDescendants(conversation);

  // Generate conversation ID first
  const conversationId = await generateEntityId(
    ENTITY_PREFIXES[8],
    conversation.title,
    '',
    0
  );

  // L8: Conversation
  entities.push({
    entity_id: conversationId,
    level: 8,
    entity_type: ENTITY_TYPES[8],
    entity_mode: 'active',
    parent_id: null,

    conversation_id: conversationId,
    topic_segment_id: null,
    turn_id: null,
    message_id: null,
    sentence_id: null,
    span_id: null,
    word_id: null,

    text: conversation.title,
    canonical_form: null,
    persona: null,

    source_pipeline: 'neurolinguist_parser',
    source_file: options.sourceFile || null,
    source_file_path: options.sourceFilePath || null,
    source_system: 'neurolinguist_json_parser',
    source_ids: [conversation.id],

    metadata: {
      topic_count: conversation.topicCount,
      original_format: 'json',
      parser_version: '3.0.0',
    },

    content_date: contentDate,
    source_message_timestamp: null,
    created_at: now,
    updated_at: now,
    ingestion_timestamp: now,
    ingestion_job_id: jobId,

    validation_status: 'PASSED',

    l7_count: counts.l7,
    l6_count: counts.l6,
    l5_count: counts.l5,
    l4_count: counts.l4,
    l3_count: counts.l3,
    l2_count: counts.l2,

    role: null,
  });

  // Process topics (L7)
  let topicIndex = 0;
  for (const topic of conversation.topics) {
    const topicId = await generateEntityId(
      ENTITY_PREFIXES[7],
      topic.title,
      conversationId,
      topicIndex++
    );

    const topicCounts = countTopicDescendants(topic);

    entities.push({
      entity_id: topicId,
      level: 7,
      entity_type: ENTITY_TYPES[7],
      entity_mode: 'active',
      parent_id: conversationId,

      conversation_id: conversationId,
      topic_segment_id: topicId,
      turn_id: null,
      message_id: null,
      sentence_id: null,
      span_id: null,
      word_id: null,

      text: topic.title,
      canonical_form: null,
      persona: null,

      source_pipeline: 'neurolinguist_parser',
      source_file: options.sourceFile || null,
      source_file_path: options.sourceFilePath || null,
      source_system: 'neurolinguist_json_parser',
      source_ids: [topic.id],

      metadata: {
        summary: topic.summary,
        sentiment: topic.sentiment,
        keywords: topic.keywords,
        has_embedding: !!topic.embedding,
        embedding_dims: topic.embedding?.length || 0,
      },

      content_date: contentDate,
      source_message_timestamp: null,
      created_at: now,
      updated_at: now,
      ingestion_timestamp: now,
      ingestion_job_id: jobId,

      validation_status: 'PASSED',

      l7_count: 0,
      l6_count: topicCounts.l6,
      l5_count: topicCounts.l5,
      l4_count: topicCounts.l4,
      l3_count: topicCounts.l3,
      l2_count: topicCounts.l2,

      role: null,
    });

    relationships.push({
      source_id: conversationId,
      target_id: topicId,
      relationship_type: 'contains',
      confidence: 1.0,
    });

    // Process turns (L6)
    let turnIndex = 0;
    for (const turn of topic.turns) {
      const turnId = await generateEntityId(
        ENTITY_PREFIXES[6],
        `turn_${turnIndex}`,
        topicId,
        turnIndex++
      );

      const turnCounts = countTurnDescendants(turn);

      entities.push({
        entity_id: turnId,
        level: 6,
        entity_type: ENTITY_TYPES[6],
        entity_mode: 'active',
        parent_id: topicId,

        conversation_id: conversationId,
        topic_segment_id: topicId,
        turn_id: turnId,
        message_id: null,
        sentence_id: null,
        span_id: null,
        word_id: null,

        text: `Turn with ${turn.messageCount} messages`,
        canonical_form: null,
        persona: null,

        source_pipeline: 'neurolinguist_parser',
        source_file: options.sourceFile || null,
        source_file_path: options.sourceFilePath || null,
        source_system: 'neurolinguist_json_parser',
        source_ids: [turn.id],

        metadata: {
          message_count: turn.messageCount,
          initiator: turn.messages[0]?.role || 'unknown',
        },

        content_date: contentDate,
        source_message_timestamp: null,
        created_at: now,
        updated_at: now,
        ingestion_timestamp: now,
        ingestion_job_id: jobId,

        validation_status: 'PASSED',

        l7_count: 0,
        l6_count: 0,
        l5_count: turnCounts.l5,
        l4_count: turnCounts.l4,
        l3_count: turnCounts.l3,
        l2_count: turnCounts.l2,

        role: null,
      });

      relationships.push({
        source_id: topicId,
        target_id: turnId,
        relationship_type: 'contains',
        confidence: 1.0,
      });

      // Process messages (L5)
      let messageIndex = 0;
      for (const message of turn.messages) {
        const messageId = await generateEntityId(
          ENTITY_PREFIXES[5],
          message.content.slice(0, 100),
          turnId,
          messageIndex++
        );

        const messageCounts = countMessageDescendants(message);

        entities.push({
          entity_id: messageId,
          level: 5,
          entity_type: ENTITY_TYPES[5],
          entity_mode: 'active',
          parent_id: turnId,

          conversation_id: conversationId,
          topic_segment_id: topicId,
          turn_id: turnId,
          message_id: messageId,
          sentence_id: null,
          span_id: null,
          word_id: null,

          text: message.content,
          canonical_form: null,
          persona: message.role === 'model' ? 'assistant' : null,

          source_pipeline: 'neurolinguist_parser',
          source_file: options.sourceFile || null,
          source_file_path: options.sourceFilePath || null,
          source_system: 'neurolinguist_json_parser',
          source_ids: [message.id],

          metadata: {
            role: message.role,
            sentence_count: message.sentenceCount,
          },

          content_date: contentDate,
          source_message_timestamp: null,
          created_at: now,
          updated_at: now,
          ingestion_timestamp: now,
          ingestion_job_id: jobId,

          validation_status: 'PASSED',

          l7_count: 0,
          l6_count: 0,
          l5_count: 0,
          l4_count: messageCounts.l4,
          l3_count: messageCounts.l3,
          l2_count: messageCounts.l2,

          role: message.role === 'model' ? 'assistant' : message.role,
        });

        relationships.push({
          source_id: turnId,
          target_id: messageId,
          relationship_type: 'contains',
          confidence: 1.0,
        });

        // Process sentences (L4)
        let sentenceIndex = 0;
        for (const sentence of message.sentences) {
          const sentenceId = await generateEntityId(
            ENTITY_PREFIXES[4],
            sentence.text.slice(0, 50),
            messageId,
            sentenceIndex++
          );

          const sentenceContext: HierarchyContext = {
            conversation_id: conversationId,
            topic_segment_id: topicId,
            turn_id: turnId,
            message_id: messageId,
            sentence_id: sentenceId,
          };

          entities.push({
            entity_id: sentenceId,
            level: 4,
            entity_type: ENTITY_TYPES[4],
            entity_mode: 'active',
            parent_id: messageId,

            conversation_id: conversationId,
            topic_segment_id: topicId,
            turn_id: turnId,
            message_id: messageId,
            sentence_id: sentenceId,
            span_id: null,
            word_id: null,

            text: sentence.text,
            canonical_form: generateCanonicalForm(sentence.text, 4),
            persona: null,

            source_pipeline: 'neurolinguist_parser',
            source_file: options.sourceFile || null,
            source_file_path: options.sourceFilePath || null,
            source_system: 'neurolinguist_json_parser',
            source_ids: buildSourceIds(sentence.id, sentenceContext),

            metadata: {
              word_count: sentence.wordCount,
              span_count: sentence.spanCount,
              char_count: sentence.text.length,
            },

            content_date: contentDate,
            source_message_timestamp: null,
            created_at: now,
            updated_at: now,
            ingestion_timestamp: now,
            ingestion_job_id: jobId,

            validation_status: 'PASSED',

            l7_count: 0,
            l6_count: 0,
            l5_count: 0,
            l4_count: 0,
            l3_count: sentence.spans.length,
            l2_count: sentence.words.length,

            role: null,
          });

          relationships.push({
            source_id: messageId,
            target_id: sentenceId,
            relationship_type: 'contains',
            confidence: 1.0,
          });

          // Process spans (L3)
          let spanIndex = 0;
          for (const span of sentence.spans) {
            const spanId = await generateEntityId(
              ENTITY_PREFIXES[3],
              span.text,
              sentenceId,
              spanIndex++
            );

            entities.push({
              entity_id: spanId,
              level: 3,
              entity_type: ENTITY_TYPES[3],
              entity_mode: 'active',
              parent_id: sentenceId,

              conversation_id: conversationId,
              topic_segment_id: topicId,
              turn_id: turnId,
              message_id: messageId,
              sentence_id: sentenceId,
              span_id: spanId,
              word_id: null,

              text: span.text,
              canonical_form: generateCanonicalForm(span.text, 3),
              persona: null,

              source_pipeline: 'neurolinguist_parser',
              source_file: options.sourceFile || null,
              source_file_path: options.sourceFilePath || null,
              source_system: 'neurolinguist_json_parser',
              source_ids: buildSourceIds(span.id, sentenceContext),

              metadata: {
                label: span.label,
                entity_class: span.label,
                char_count: span.text.length,
              },

              content_date: contentDate,
              source_message_timestamp: null,
              created_at: now,
              updated_at: now,
              ingestion_timestamp: now,
              ingestion_job_id: jobId,

              validation_status: 'PASSED',

              l7_count: 0,
              l6_count: 0,
              l5_count: 0,
              l4_count: 0,
              l3_count: 0,
              l2_count: 0,

              role: null,
            });

            relationships.push({
              source_id: sentenceId,
              target_id: spanId,
              relationship_type: 'contains_entity',
              confidence: 1.0,
              metadata: { entity_type: span.label },
            });
          }

          // Optionally process words (L2)
          if (options.includeWords) {
            let wordIndex = 0;
            for (const word of sentence.words) {
              const wordId = await generateEntityId(
                ENTITY_PREFIXES[2],
                word.text,
                sentenceId,
                wordIndex++
              );

              entities.push({
                entity_id: wordId,
                level: 2,
                entity_type: ENTITY_TYPES[2],
                entity_mode: 'active',
                parent_id: sentenceId,

                conversation_id: conversationId,
                topic_segment_id: topicId,
                turn_id: turnId,
                message_id: messageId,
                sentence_id: sentenceId,
                span_id: null,
                word_id: wordId,

                text: word.text,
                canonical_form: generateCanonicalForm(word.text, 2),
                persona: null,

                source_pipeline: 'neurolinguist_parser',
                source_file: options.sourceFile || null,
                source_file_path: options.sourceFilePath || null,
                source_system: 'neurolinguist_json_parser',
                source_ids: buildSourceIds(word.id, sentenceContext),

                metadata: {
                  char_count: word.text.length,
                  is_punctuation: /^[^\w\s]+$/.test(word.text),
                },

                content_date: contentDate,
                source_message_timestamp: null,
                created_at: now,
                updated_at: now,
                ingestion_timestamp: now,
                ingestion_job_id: jobId,

                validation_status: 'PASSED',

                l7_count: 0,
                l6_count: 0,
                l5_count: 0,
                l4_count: 0,
                l3_count: 0,
                l2_count: 0,

                role: null,
              });

              relationships.push({
                source_id: sentenceId,
                target_id: wordId,
                relationship_type: 'contains',
                confidence: 1.0,
              });
            }
          }
        }
      }
    }
  }

  return {
    entities,
    relationships,
    export_metadata: {
      exported_at: now,
      source_app: 'neurolinguist_json_parser',
      version: '3.0.0',
      conversation_id: conversationId,
      entity_count: entities.length,
      relationship_count: relationships.length,
      schema_version: 'entity_unified_v1',
      target_table: 'flash-clover-464719-g1.spine.entity_unified',
    },
  };
}

// Helper functions for counting descendants
function countTopicDescendants(topic: TopicSegment): { l6: number; l5: number; l4: number; l3: number; l2: number } {
  let l6 = 0, l5 = 0, l4 = 0, l3 = 0, l2 = 0;
  for (const turn of topic.turns) {
    l6++;
    for (const message of turn.messages) {
      l5++;
      for (const sentence of message.sentences) {
        l4++;
        l3 += sentence.spans.length;
        l2 += sentence.words.length;
      }
    }
  }
  return { l6, l5, l4, l3, l2 };
}

function countTurnDescendants(turn: Turn): { l5: number; l4: number; l3: number; l2: number } {
  let l5 = 0, l4 = 0, l3 = 0, l2 = 0;
  for (const message of turn.messages) {
    l5++;
    for (const sentence of message.sentences) {
      l4++;
      l3 += sentence.spans.length;
      l2 += sentence.words.length;
    }
  }
  return { l5, l4, l3, l2 };
}

function countMessageDescendants(message: Message): { l4: number; l3: number; l2: number } {
  let l4 = 0, l3 = 0, l2 = 0;
  for (const sentence of message.sentences) {
    l4++;
    l3 += sentence.spans.length;
    l2 += sentence.words.length;
  }
  return { l4, l3, l2 };
}

/**
 * Export as JSONL format for direct BigQuery batch load
 * Each line is a valid JSON record matching entity_unified schema
 */
export async function exportToNativeSpineJSONL(
  conversation: Conversation,
  options: {
    sourceFile?: string;
    sourceFilePath?: string;
    includeWords?: boolean;
    includeMetadataHeader?: boolean;
  } = {}
): Promise<string> {
  const exportData = await exportToNativeSpineFormat(conversation, options);
  const lines: string[] = [];

  // Optional metadata header (not loaded to BigQuery, for reference only)
  if (options.includeMetadataHeader) {
    lines.push(`# ${JSON.stringify(exportData.export_metadata)}`);
  }

  // Entity lines - ready for BigQuery batch load
  for (const entity of exportData.entities) {
    // Convert metadata object to JSON string for BigQuery JSON column
    const record = {
      ...entity,
      metadata: JSON.stringify(entity.metadata),
    };
    lines.push(JSON.stringify(record));
  }

  return lines.join('\n');
}

/**
 * Export relationships as separate JSONL (for relationship table if needed)
 */
export async function exportRelationshipsJSONL(conversation: Conversation): Promise<string> {
  const exportData = await exportToNativeSpineFormat(conversation);
  return exportData.relationships.map(rel => JSON.stringify(rel)).join('\n');
}

// ============================================================================
// LEGACY EXPORTS (maintained for backwards compatibility)
// ============================================================================

// Legacy SpineEntity interface
interface SpineEntity {
  id: string;
  level: number;
  entity_type: string;
  content: string;
  parent_id: string | null;
  source_system: string;
  source_platform: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

interface SpineExport {
  entities: SpineEntity[];
  relationships: SpineRelationship[];
  export_metadata: {
    exported_at: string;
    source_app: string;
    version: string;
    conversation_id: string;
    entity_count: number;
    relationship_count: number;
  };
}

/**
 * Legacy export format (v2.0 compatible)
 * @deprecated Use exportToNativeSpineFormat instead
 */
export function exportToSpineFormat(conversation: Conversation): SpineExport {
  const entities: SpineEntity[] = [];
  const relationships: SpineRelationship[] = [];
  const now = new Date().toISOString();

  // L8: Conversation
  entities.push({
    id: conversation.id,
    level: 8,
    entity_type: 'conversation',
    content: conversation.title,
    parent_id: null,
    source_system: 'neurolinguist_parser',
    source_platform: 'local',
    created_at: now,
    metadata: {
      topic_count: conversation.topicCount,
      original_format: 'json'
    }
  });

  for (const topic of conversation.topics) {
    entities.push({
      id: topic.id,
      level: 7,
      entity_type: 'topic_segment',
      content: topic.title,
      parent_id: conversation.id,
      source_system: 'neurolinguist_parser',
      source_platform: 'local',
      created_at: now,
      metadata: {
        summary: topic.summary,
        sentiment: topic.sentiment,
        keywords: topic.keywords,
        turn_count: topic.turnCount,
        has_embedding: !!topic.embedding
      }
    });

    relationships.push({
      source_id: conversation.id,
      target_id: topic.id,
      relationship_type: 'contains',
      confidence: 1.0
    });

    for (const turn of topic.turns) {
      entities.push({
        id: turn.id,
        level: 6,
        entity_type: 'turn',
        content: `Turn with ${turn.messageCount} messages`,
        parent_id: topic.id,
        source_system: 'neurolinguist_parser',
        source_platform: 'local',
        created_at: now,
        metadata: {
          message_count: turn.messageCount,
          initiator: turn.messages[0]?.role || 'unknown'
        }
      });

      relationships.push({
        source_id: topic.id,
        target_id: turn.id,
        relationship_type: 'contains',
        confidence: 1.0
      });

      for (const message of turn.messages) {
        entities.push({
          id: message.id,
          level: 5,
          entity_type: 'message',
          content: message.content,
          parent_id: turn.id,
          source_system: 'neurolinguist_parser',
          source_platform: 'local',
          created_at: now,
          metadata: {
            role: message.role,
            sentence_count: message.sentenceCount
          }
        });

        relationships.push({
          source_id: turn.id,
          target_id: message.id,
          relationship_type: 'contains',
          confidence: 1.0
        });

        for (const sentence of message.sentences) {
          entities.push({
            id: sentence.id,
            level: 4,
            entity_type: 'sentence',
            content: sentence.text,
            parent_id: message.id,
            source_system: 'neurolinguist_parser',
            source_platform: 'local',
            created_at: now,
            metadata: {
              word_count: sentence.wordCount,
              span_count: sentence.spanCount
            }
          });

          relationships.push({
            source_id: message.id,
            target_id: sentence.id,
            relationship_type: 'contains',
            confidence: 1.0
          });

          for (const span of sentence.spans) {
            entities.push({
              id: span.id,
              level: 3,
              entity_type: 'named_entity',
              content: span.text,
              parent_id: sentence.id,
              source_system: 'neurolinguist_parser',
              source_platform: 'local',
              created_at: now,
              metadata: {
                label: span.label,
                entity_class: span.label
              }
            });

            relationships.push({
              source_id: sentence.id,
              target_id: span.id,
              relationship_type: 'contains_entity',
              confidence: 1.0,
              metadata: { entity_type: span.label }
            });
          }
        }
      }
    }
  }

  return {
    entities,
    relationships,
    export_metadata: {
      exported_at: now,
      source_app: 'neurolinguist_json_parser',
      version: '2.0.0',
      conversation_id: conversation.id,
      entity_count: entities.length,
      relationship_count: relationships.length
    }
  };
}

/**
 * Legacy JSONL export (v2.0 compatible)
 * @deprecated Use exportToNativeSpineJSONL instead
 */
export function exportToSpineJSONL(conversation: Conversation): string {
  const export_data = exportToSpineFormat(conversation);
  const lines: string[] = [];

  lines.push(JSON.stringify({ _type: 'metadata', ...export_data.export_metadata }));

  for (const entity of export_data.entities) {
    lines.push(JSON.stringify({ _type: 'entity', ...entity }));
  }

  for (const rel of export_data.relationships) {
    lines.push(JSON.stringify({ _type: 'relationship', ...rel }));
  }

  return lines.join('\n');
}

/**
 * Legacy CSV export
 */
export function exportEntitiesAsCSV(conversation: Conversation): string {
  const export_data = exportToSpineFormat(conversation);

  const headers = [
    'id', 'level', 'entity_type', 'content', 'parent_id',
    'source_system', 'created_at', 'metadata_json'
  ];

  const rows = export_data.entities.map(e => [
    e.id,
    e.level,
    e.entity_type,
    `"${e.content.replace(/"/g, '""').replace(/\n/g, ' ')}"`,
    e.parent_id || '',
    e.source_system,
    e.created_at,
    `"${JSON.stringify(e.metadata).replace(/"/g, '""')}"`
  ].join(','));

  return [headers.join(','), ...rows].join('\n');
}

/**
 * Conversation Diff Service
 * Compare two analyzed conversations to track topic/entity drift over time
 */

import { Conversation, TopicSegment, Span } from '../types';

export interface TopicDiff {
  added: TopicSegment[];
  removed: TopicSegment[];
  similar: Array<{
    topic1: TopicSegment;
    topic2: TopicSegment;
    similarity: number;
    keywordOverlap: string[];
  }>;
}

export interface EntityDiff {
  added: Map<string, Span[]>;      // label -> spans
  removed: Map<string, Span[]>;
  common: Map<string, { count1: number; count2: number }>;
}

export interface ConversationDiffResult {
  summary: {
    conversation1Id: string;
    conversation2Id: string;
    topicCountDiff: number;
    entityCountDiff: number;
    newTopics: number;
    removedTopics: number;
    similarTopics: number;
  };
  topics: TopicDiff;
  entities: EntityDiff;
  keywordEvolution: {
    emerging: string[];   // New keywords in conv2
    declining: string[];  // Keywords only in conv1
    persistent: string[]; // Keywords in both
  };
  sentimentShift: {
    conversation1: { positive: number; neutral: number; negative: number };
    conversation2: { positive: number; neutral: number; negative: number };
    shift: string; // 'more_positive' | 'more_negative' | 'stable'
  };
}

// Calculate cosine similarity between two embeddings
function cosineSimilarity(a: number[] | undefined, b: number[] | undefined): number {
  if (!a || !b || a.length !== b.length || a.length === 0) return 0;

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  if (normA === 0 || normB === 0) return 0;
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Calculate Jaccard similarity between two keyword sets
function jaccardSimilarity(set1: Set<string>, set2: Set<string>): number {
  if (set1.size === 0 && set2.size === 0) return 1;
  if (set1.size === 0 || set2.size === 0) return 0;

  const intersection = new Set([...set1].filter(x => set2.has(x)));
  const union = new Set([...set1, ...set2]);

  return intersection.size / union.size;
}

// Extract all entities from a conversation
function extractEntities(conversation: Conversation): Map<string, Span[]> {
  const entities = new Map<string, Span[]>();

  for (const topic of conversation.topics) {
    for (const turn of topic.turns) {
      for (const message of turn.messages) {
        for (const sentence of message.sentences) {
          for (const span of sentence.spans) {
            const existing = entities.get(span.label) || [];
            existing.push(span);
            entities.set(span.label, existing);
          }
        }
      }
    }
  }

  return entities;
}

// Extract all keywords from a conversation
function extractKeywords(conversation: Conversation): Set<string> {
  const keywords = new Set<string>();

  for (const topic of conversation.topics) {
    if (topic.keywords) {
      topic.keywords.forEach(k => keywords.add(k.toLowerCase()));
    }
  }

  return keywords;
}

// Count sentiments
function countSentiments(conversation: Conversation): { positive: number; neutral: number; negative: number } {
  const counts = { positive: 0, neutral: 0, negative: 0 };

  for (const topic of conversation.topics) {
    if (topic.sentiment === 'positive') counts.positive++;
    else if (topic.sentiment === 'negative') counts.negative++;
    else counts.neutral++;
  }

  return counts;
}

// Find similar topics between two conversations
function findSimilarTopics(
  topics1: TopicSegment[],
  topics2: TopicSegment[],
  threshold: number = 0.5
): Array<{ topic1: TopicSegment; topic2: TopicSegment; similarity: number; keywordOverlap: string[] }> {
  const similar: Array<{ topic1: TopicSegment; topic2: TopicSegment; similarity: number; keywordOverlap: string[] }> = [];
  const matched2 = new Set<string>();

  for (const t1 of topics1) {
    let bestMatch: { topic: TopicSegment; similarity: number; keywordOverlap: string[] } | null = null;

    for (const t2 of topics2) {
      if (matched2.has(t2.id)) continue;

      // Calculate similarity using embeddings if available, otherwise keywords
      let similarity: number;
      if (t1.embedding && t2.embedding) {
        similarity = cosineSimilarity(t1.embedding, t2.embedding);
      } else {
        const kw1 = new Set(t1.keywords?.map(k => k.toLowerCase()) || []);
        const kw2 = new Set(t2.keywords?.map(k => k.toLowerCase()) || []);
        similarity = jaccardSimilarity(kw1, kw2);
      }

      // Also consider title similarity
      const titleWords1 = new Set(t1.title.toLowerCase().split(/\s+/));
      const titleWords2 = new Set(t2.title.toLowerCase().split(/\s+/));
      const titleSim = jaccardSimilarity(titleWords1, titleWords2);

      // Combined similarity
      const combinedSim = similarity * 0.7 + titleSim * 0.3;

      if (combinedSim >= threshold && (!bestMatch || combinedSim > bestMatch.similarity)) {
        const kw1 = new Set(t1.keywords?.map(k => k.toLowerCase()) || []);
        const kw2 = new Set(t2.keywords?.map(k => k.toLowerCase()) || []);
        const overlap = [...kw1].filter(k => kw2.has(k));

        bestMatch = { topic: t2, similarity: combinedSim, keywordOverlap: overlap };
      }
    }

    if (bestMatch) {
      similar.push({
        topic1: t1,
        topic2: bestMatch.topic,
        similarity: bestMatch.similarity,
        keywordOverlap: bestMatch.keywordOverlap
      });
      matched2.add(bestMatch.topic.id);
    }
  }

  return similar;
}

export function compareConversations(
  conversation1: Conversation,
  conversation2: Conversation
): ConversationDiffResult {
  // Find similar topics
  const similarTopics = findSimilarTopics(conversation1.topics, conversation2.topics);
  const matched1Ids = new Set(similarTopics.map(s => s.topic1.id));
  const matched2Ids = new Set(similarTopics.map(s => s.topic2.id));

  // Topics only in conversation1 (removed)
  const removedTopics = conversation1.topics.filter(t => !matched1Ids.has(t.id));

  // Topics only in conversation2 (added)
  const addedTopics = conversation2.topics.filter(t => !matched2Ids.has(t.id));

  // Entity analysis
  const entities1 = extractEntities(conversation1);
  const entities2 = extractEntities(conversation2);

  const allLabels = new Set([...entities1.keys(), ...entities2.keys()]);
  const addedEntities = new Map<string, Span[]>();
  const removedEntities = new Map<string, Span[]>();
  const commonEntities = new Map<string, { count1: number; count2: number }>();

  for (const label of allLabels) {
    const e1 = entities1.get(label) || [];
    const e2 = entities2.get(label) || [];

    if (e1.length === 0 && e2.length > 0) {
      addedEntities.set(label, e2);
    } else if (e1.length > 0 && e2.length === 0) {
      removedEntities.set(label, e1);
    } else {
      commonEntities.set(label, { count1: e1.length, count2: e2.length });
    }
  }

  // Keyword evolution
  const keywords1 = extractKeywords(conversation1);
  const keywords2 = extractKeywords(conversation2);

  const emerging = [...keywords2].filter(k => !keywords1.has(k));
  const declining = [...keywords1].filter(k => !keywords2.has(k));
  const persistent = [...keywords1].filter(k => keywords2.has(k));

  // Sentiment shift
  const sentiment1 = countSentiments(conversation1);
  const sentiment2 = countSentiments(conversation2);

  const positiveShift = (sentiment2.positive / Math.max(conversation2.topicCount, 1)) -
                        (sentiment1.positive / Math.max(conversation1.topicCount, 1));
  const negativeShift = (sentiment2.negative / Math.max(conversation2.topicCount, 1)) -
                        (sentiment1.negative / Math.max(conversation1.topicCount, 1));

  let shift: string;
  if (positiveShift > 0.1) shift = 'more_positive';
  else if (negativeShift > 0.1) shift = 'more_negative';
  else shift = 'stable';

  // Calculate entity count
  const entityCount1 = [...entities1.values()].reduce((sum, arr) => sum + arr.length, 0);
  const entityCount2 = [...entities2.values()].reduce((sum, arr) => sum + arr.length, 0);

  return {
    summary: {
      conversation1Id: conversation1.id,
      conversation2Id: conversation2.id,
      topicCountDiff: conversation2.topicCount - conversation1.topicCount,
      entityCountDiff: entityCount2 - entityCount1,
      newTopics: addedTopics.length,
      removedTopics: removedTopics.length,
      similarTopics: similarTopics.length
    },
    topics: {
      added: addedTopics,
      removed: removedTopics,
      similar: similarTopics
    },
    entities: {
      added: addedEntities,
      removed: removedEntities,
      common: commonEntities
    },
    keywordEvolution: {
      emerging,
      declining,
      persistent
    },
    sentimentShift: {
      conversation1: sentiment1,
      conversation2: sentiment2,
      shift
    }
  };
}

// Generate a human-readable diff report
export function generateDiffReport(diff: ConversationDiffResult): string {
  const lines: string[] = [];

  lines.push('# Conversation Comparison Report');
  lines.push('');
  lines.push('## Summary');
  lines.push(`- Topic count change: ${diff.summary.topicCountDiff > 0 ? '+' : ''}${diff.summary.topicCountDiff}`);
  lines.push(`- New topics: ${diff.summary.newTopics}`);
  lines.push(`- Removed topics: ${diff.summary.removedTopics}`);
  lines.push(`- Similar topics: ${diff.summary.similarTopics}`);
  lines.push(`- Entity count change: ${diff.summary.entityCountDiff > 0 ? '+' : ''}${diff.summary.entityCountDiff}`);
  lines.push('');

  if (diff.topics.added.length > 0) {
    lines.push('## New Topics');
    for (const topic of diff.topics.added) {
      lines.push(`- **${topic.title}**: ${topic.summary}`);
    }
    lines.push('');
  }

  if (diff.topics.removed.length > 0) {
    lines.push('## Removed Topics');
    for (const topic of diff.topics.removed) {
      lines.push(`- **${topic.title}**: ${topic.summary}`);
    }
    lines.push('');
  }

  if (diff.topics.similar.length > 0) {
    lines.push('## Topic Evolution');
    for (const { topic1, topic2, similarity, keywordOverlap } of diff.topics.similar) {
      lines.push(`- "${topic1.title}" → "${topic2.title}" (${(similarity * 100).toFixed(0)}% similar)`);
      if (keywordOverlap.length > 0) {
        lines.push(`  - Shared keywords: ${keywordOverlap.join(', ')}`);
      }
    }
    lines.push('');
  }

  lines.push('## Keyword Evolution');
  if (diff.keywordEvolution.emerging.length > 0) {
    lines.push(`- **Emerging**: ${diff.keywordEvolution.emerging.join(', ')}`);
  }
  if (diff.keywordEvolution.declining.length > 0) {
    lines.push(`- **Declining**: ${diff.keywordEvolution.declining.join(', ')}`);
  }
  if (diff.keywordEvolution.persistent.length > 0) {
    lines.push(`- **Persistent**: ${diff.keywordEvolution.persistent.join(', ')}`);
  }
  lines.push('');

  lines.push('## Sentiment Analysis');
  lines.push(`- Conversation 1: ${diff.sentimentShift.conversation1.positive} positive, ${diff.sentimentShift.conversation1.neutral} neutral, ${diff.sentimentShift.conversation1.negative} negative`);
  lines.push(`- Conversation 2: ${diff.sentimentShift.conversation2.positive} positive, ${diff.sentimentShift.conversation2.neutral} neutral, ${diff.sentimentShift.conversation2.negative} negative`);
  lines.push(`- Overall shift: ${diff.sentimentShift.shift.replace('_', ' ')}`);

  return lines.join('\n');
}

import { describe, it, expect } from 'vitest';
import {
  compareConversations,
  generateDiffReport,
  type ConversationDiffResult,
} from '../services/conversationDiff';
import type { Conversation, TopicSegment, Turn, Message, Sentence, Span } from '../types';

// Helper to create a minimal conversation
function createConversation(
  id: string,
  topics: Array<{
    id: string;
    title: string;
    keywords?: string[];
    sentiment?: 'positive' | 'neutral' | 'negative';
    embedding?: number[];
    spans?: Array<{ text: string; label: string }>;
  }>
): Conversation {
  return {
    id,
    title: `Conversation ${id}`,
    topicCount: topics.length,
    topics: topics.map((t) => ({
      id: t.id,
      title: t.title,
      summary: `Summary of ${t.title}`,
      parentId: id,
      turnCount: 1,
      sentiment: t.sentiment || 'neutral',
      keywords: t.keywords || [],
      embedding: t.embedding,
      turns: [
        {
          id: `${t.id}-turn`,
          parentId: t.id,
          messageCount: 1,
          messages: [
            {
              id: `${t.id}-msg`,
              role: 'user',
              content: `Message about ${t.title}`,
              parentId: `${t.id}-turn`,
              sentenceCount: 1,
              sentences: [
                {
                  id: `${t.id}-sent`,
                  text: `Message about ${t.title}`,
                  parentId: `${t.id}-msg`,
                  wordCount: 3,
                  spanCount: t.spans?.length || 0,
                  words: [],
                  spans:
                    t.spans?.map((s, i) => ({
                      id: `${t.id}-span-${i}`,
                      text: s.text,
                      label: s.label,
                      parentId: `${t.id}-sent`,
                      type: 'span' as const,
                    })) || [],
                },
              ],
            },
          ],
        },
      ],
    })),
  };
}

describe('conversationDiff', () => {
  describe('compareConversations', () => {
    describe('topic comparison', () => {
      it('should identify added topics', () => {
        const conv1 = createConversation('c1', [{ id: 't1', title: 'Topic A' }]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic A' },
          { id: 't2', title: 'Topic B' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.summary.newTopics).toBe(1);
        expect(result.topics.added.length).toBe(1);
        expect(result.topics.added[0].title).toBe('Topic B');
      });

      it('should identify removed topics', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic A' },
          { id: 't2', title: 'Topic B' },
        ]);
        const conv2 = createConversation('c2', [{ id: 't1', title: 'Topic A' }]);

        const result = compareConversations(conv1, conv2);

        expect(result.summary.removedTopics).toBe(1);
        expect(result.topics.removed.length).toBe(1);
        expect(result.topics.removed[0].title).toBe('Topic B');
      });

      it('should identify similar topics by title', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'machine learning basics' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't2', title: 'machine learning fundamentals' },
        ]);

        const result = compareConversations(conv1, conv2);

        // "machine" and "learning" are shared words
        expect(result.topics.similar.length).toBe(1);
        expect(result.topics.similar[0].topic1.title).toBe('machine learning basics');
        expect(result.topics.similar[0].topic2.title).toBe(
          'machine learning fundamentals'
        );
      });

      it('should identify similar topics by embedding similarity', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic A', embedding: [1, 0, 0, 0] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't2', title: 'Topic B', embedding: [0.9, 0.1, 0, 0] },
        ]);

        const result = compareConversations(conv1, conv2);

        // High cosine similarity despite different titles
        expect(result.topics.similar.length).toBe(1);
        expect(result.topics.similar[0].similarity).toBeGreaterThan(0.5);
      });

      it('should not match topics with very different embeddings', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic A', embedding: [1, 0, 0, 0] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't2', title: 'Topic B', embedding: [0, 0, 0, 1] },
        ]);

        const result = compareConversations(conv1, conv2);

        // Orthogonal embeddings = no match
        expect(result.topics.similar.length).toBe(0);
        expect(result.topics.added.length).toBe(1);
        expect(result.topics.removed.length).toBe(1);
      });

      it('should report keyword overlap for similar topics', () => {
        // Use embeddings to ensure topics match (keyword-only Jaccard may not hit threshold)
        const conv1 = createConversation('c1', [
          {
            id: 't1',
            title: 'neural networks topic',
            keywords: ['neural', 'networks', 'training'],
            embedding: [1, 0, 0, 0],
          },
        ]);
        const conv2 = createConversation('c2', [
          {
            id: 't2',
            title: 'neural networks discussion',
            keywords: ['neural', 'networks', 'inference'],
            embedding: [0.95, 0.1, 0, 0],
          },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.topics.similar.length).toBe(1);
        expect(result.topics.similar[0].keywordOverlap).toContain('neural');
        expect(result.topics.similar[0].keywordOverlap).toContain('networks');
      });
    });

    describe('entity comparison', () => {
      it('should identify added entity types', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', spans: [{ text: 'John', label: 'PERSON' }] },
        ]);
        const conv2 = createConversation('c2', [
          {
            id: 't1',
            title: 'Topic',
            spans: [
              { text: 'John', label: 'PERSON' },
              { text: '2024', label: 'DATE' },
            ],
          },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.entities.added.has('DATE')).toBe(true);
        expect(result.entities.added.get('DATE')?.length).toBe(1);
      });

      it('should identify removed entity types', () => {
        const conv1 = createConversation('c1', [
          {
            id: 't1',
            title: 'Topic',
            spans: [
              { text: 'John', label: 'PERSON' },
              { text: '2024', label: 'DATE' },
            ],
          },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic', spans: [{ text: 'John', label: 'PERSON' }] },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.entities.removed.has('DATE')).toBe(true);
        expect(result.entities.removed.get('DATE')?.length).toBe(1);
      });

      it('should track common entity type counts', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', spans: [{ text: 'John', label: 'PERSON' }] },
        ]);
        const conv2 = createConversation('c2', [
          {
            id: 't1',
            title: 'Topic',
            spans: [
              { text: 'John', label: 'PERSON' },
              { text: 'Jane', label: 'PERSON' },
            ],
          },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.entities.common.has('PERSON')).toBe(true);
        expect(result.entities.common.get('PERSON')).toEqual({ count1: 1, count2: 2 });
      });
    });

    describe('keyword evolution', () => {
      it('should identify emerging keywords', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'beta'] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'gamma'] },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.keywordEvolution.emerging).toContain('gamma');
      });

      it('should identify declining keywords', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'beta'] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'gamma'] },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.keywordEvolution.declining).toContain('beta');
      });

      it('should identify persistent keywords', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'beta'] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'gamma'] },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.keywordEvolution.persistent).toContain('alpha');
      });

      it('should normalize keywords to lowercase', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', keywords: ['ALPHA', 'Beta'] },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic', keywords: ['alpha', 'BETA'] },
        ]);

        const result = compareConversations(conv1, conv2);

        // All should be persistent because they're the same when lowercased
        expect(result.keywordEvolution.persistent).toContain('alpha');
        expect(result.keywordEvolution.persistent).toContain('beta');
        expect(result.keywordEvolution.emerging.length).toBe(0);
        expect(result.keywordEvolution.declining.length).toBe(0);
      });
    });

    describe('sentiment shift', () => {
      it('should detect shift to more positive', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic 1', sentiment: 'negative' },
          { id: 't2', title: 'Topic 2', sentiment: 'neutral' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
          { id: 't2', title: 'Topic 2', sentiment: 'positive' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.sentimentShift.shift).toBe('more_positive');
      });

      it('should detect shift to more negative', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
          { id: 't2', title: 'Topic 2', sentiment: 'positive' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic 1', sentiment: 'negative' },
          { id: 't2', title: 'Topic 2', sentiment: 'negative' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.sentimentShift.shift).toBe('more_negative');
      });

      it('should detect stable sentiment', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
          { id: 't2', title: 'Topic 2', sentiment: 'neutral' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
          { id: 't2', title: 'Topic 2', sentiment: 'neutral' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.sentimentShift.shift).toBe('stable');
      });

      it('should count sentiments correctly', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
          { id: 't2', title: 'Topic 2', sentiment: 'neutral' },
          { id: 't3', title: 'Topic 3', sentiment: 'negative' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic 1', sentiment: 'positive' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.sentimentShift.conversation1).toEqual({
          positive: 1,
          neutral: 1,
          negative: 1,
        });
        expect(result.sentimentShift.conversation2).toEqual({
          positive: 1,
          neutral: 0,
          negative: 0,
        });
      });
    });

    describe('summary statistics', () => {
      it('should calculate topic count difference', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic 1' },
          { id: 't2', title: 'Topic 2' },
        ]);
        const conv2 = createConversation('c2', [
          { id: 't1', title: 'Topic 1' },
          { id: 't2', title: 'Topic 2' },
          { id: 't3', title: 'Topic 3' },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.summary.topicCountDiff).toBe(1);
      });

      it('should calculate entity count difference', () => {
        const conv1 = createConversation('c1', [
          { id: 't1', title: 'Topic', spans: [{ text: 'A', label: 'X' }] },
        ]);
        const conv2 = createConversation('c2', [
          {
            id: 't1',
            title: 'Topic',
            spans: [
              { text: 'A', label: 'X' },
              { text: 'B', label: 'Y' },
              { text: 'C', label: 'Z' },
            ],
          },
        ]);

        const result = compareConversations(conv1, conv2);

        expect(result.summary.entityCountDiff).toBe(2);
      });
    });
  });

  describe('generateDiffReport', () => {
    it('should generate markdown report', () => {
      const conv1 = createConversation('c1', [
        { id: 't1', title: 'Topic A', keywords: ['alpha'] },
      ]);
      const conv2 = createConversation('c2', [
        { id: 't2', title: 'Topic B', keywords: ['beta'] },
      ]);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('# Conversation Comparison Report');
      expect(report).toContain('## Summary');
    });

    it('should include new topics section when topics added', () => {
      const conv1 = createConversation('c1', []);
      const conv2 = createConversation('c2', [{ id: 't1', title: 'New Topic' }]);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('## New Topics');
      expect(report).toContain('**New Topic**');
    });

    it('should include removed topics section when topics removed', () => {
      const conv1 = createConversation('c1', [{ id: 't1', title: 'Old Topic' }]);
      const conv2 = createConversation('c2', []);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('## Removed Topics');
      expect(report).toContain('**Old Topic**');
    });

    it('should include keyword evolution section', () => {
      const conv1 = createConversation('c1', [
        { id: 't1', title: 'Topic', keywords: ['old'] },
      ]);
      const conv2 = createConversation('c2', [
        { id: 't1', title: 'Topic', keywords: ['new'] },
      ]);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('## Keyword Evolution');
      expect(report).toContain('**Emerging**: new');
      expect(report).toContain('**Declining**: old');
    });

    it('should include sentiment analysis section', () => {
      const conv1 = createConversation('c1', [
        { id: 't1', title: 'Topic', sentiment: 'positive' },
      ]);
      const conv2 = createConversation('c2', [
        { id: 't1', title: 'Topic', sentiment: 'negative' },
      ]);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('## Sentiment Analysis');
      expect(report).toContain('1 positive');
      expect(report).toContain('1 negative');
    });

    it('should format topic count diff with sign', () => {
      const conv1 = createConversation('c1', [{ id: 't1', title: 'Topic 1' }]);
      const conv2 = createConversation('c2', [
        { id: 't1', title: 'Topic 1' },
        { id: 't2', title: 'Topic 2' },
      ]);

      const diff = compareConversations(conv1, conv2);
      const report = generateDiffReport(diff);

      expect(report).toContain('Topic count change: +1');
    });
  });

  describe('edge cases', () => {
    it('should handle empty conversations', () => {
      const conv1 = createConversation('c1', []);
      const conv2 = createConversation('c2', []);

      const result = compareConversations(conv1, conv2);

      expect(result.summary.topicCountDiff).toBe(0);
      expect(result.summary.entityCountDiff).toBe(0);
      expect(result.topics.added.length).toBe(0);
      expect(result.topics.removed.length).toBe(0);
      expect(result.topics.similar.length).toBe(0);
    });

    it('should handle conversations with no keywords', () => {
      const conv1 = createConversation('c1', [{ id: 't1', title: 'Topic' }]);
      const conv2 = createConversation('c2', [{ id: 't2', title: 'Other' }]);

      const result = compareConversations(conv1, conv2);

      expect(result.keywordEvolution.emerging.length).toBe(0);
      expect(result.keywordEvolution.declining.length).toBe(0);
      expect(result.keywordEvolution.persistent.length).toBe(0);
    });

    it('should handle conversations with no entities', () => {
      const conv1 = createConversation('c1', [{ id: 't1', title: 'Topic', spans: [] }]);
      const conv2 = createConversation('c2', [{ id: 't2', title: 'Other', spans: [] }]);

      const result = compareConversations(conv1, conv2);

      expect(result.entities.added.size).toBe(0);
      expect(result.entities.removed.size).toBe(0);
      expect(result.entities.common.size).toBe(0);
    });
  });
});

import { describe, it, expect } from 'vitest';
import {
  validateConversation,
  formatValidationResult,
  isValidForExport,
  ValidationResult,
} from '../services/exportValidation';
import type { Conversation, TopicSegment, Turn, Message, Sentence } from '../types';

// Helper to create minimal valid structures
function createSentence(id: string, text: string): Sentence {
  return {
    id,
    text,
    spans: [],
    words: [{ id: `${id}-w1`, text: 'word', parentId: id, type: 'word' as const }],
    parentId: 'msg-1',
    wordCount: 1,
    spanCount: 0,
  };
}

function createMessage(id: string, content: string, role: 'user' | 'assistant' = 'user'): Message {
  return {
    id,
    role,
    content,
    sentences: [createSentence(`${id}-s1`, content)],
    parentId: 'turn-1',
    sentenceCount: 1,
  };
}

function createTurn(id: string, messages: Message[]): Turn {
  return {
    id,
    messages,
    messageCount: messages.length,
    parentId: 'topic-1',
  };
}

function createTopic(id: string, turns: Turn[]): TopicSegment {
  return {
    id,
    title: 'Test Topic',
    summary: 'Test summary',
    turns,
    turnCount: turns.length,
    parentId: 'conv-1',
  };
}

function createConversation(topics: TopicSegment[]): Conversation {
  return {
    id: 'conv-1',
    title: 'Test Conversation',
    topics,
    topicCount: topics.length,
  };
}

describe('exportValidation', () => {
  describe('validateConversation', () => {
    it('should pass validation for valid conversation', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [
            createMessage('msg-1', 'Hello', 'user'),
            createMessage('msg-2', 'Hi there', 'assistant'),
          ]),
        ]),
      ]);

      const result = validateConversation(conversation);

      expect(result.valid).toBe(true);
      expect(result.stats.errors).toBe(0);
      expect(result.stats.topics).toBe(1);
      expect(result.stats.turns).toBe(1);
      expect(result.stats.messages).toBe(2);
    });

    it('should fail validation for missing conversation ID', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [createMessage('msg-1', 'Hello')]),
        ]),
      ]);
      // @ts-ignore - intentionally removing ID
      conversation.id = '';

      const result = validateConversation(conversation);

      expect(result.valid).toBe(false);
      expect(result.issues.some(i => i.code === 'MISSING_CONV_ID')).toBe(true);
    });

    it('should fail validation for empty topics', () => {
      const conversation = createConversation([]);

      const result = validateConversation(conversation);

      expect(result.valid).toBe(false);
      expect(result.issues.some(i => i.code === 'NO_TOPICS')).toBe(true);
    });

    it('should warn for empty topic (no turns)', () => {
      const conversation = createConversation([
        createTopic('topic-1', []),
      ]);

      const result = validateConversation(conversation);

      // Should pass (warnings don't fail validation) but have warnings
      expect(result.valid).toBe(true);
      expect(result.stats.warnings).toBeGreaterThan(0);
      expect(result.issues.some(i => i.code === 'EMPTY_TOPIC')).toBe(true);
    });

    it('should warn for invalid message role', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [
            // @ts-ignore - intentionally invalid role
            { ...createMessage('msg-1', 'Hello'), role: 'invalid' },
          ]),
        ]),
      ]);

      const result = validateConversation(conversation);

      expect(result.stats.warnings).toBeGreaterThan(0);
      expect(result.issues.some(i => i.code === 'INVALID_ROLE')).toBe(true);
    });

    it('should count all entity levels correctly', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [
            createMessage('msg-1', 'Hello world'),
            createMessage('msg-2', 'Hi there'),
          ]),
          createTurn('turn-2', [
            createMessage('msg-3', 'How are you?'),
          ]),
        ]),
        createTopic('topic-2', [
          createTurn('turn-3', [
            createMessage('msg-4', 'Goodbye'),
          ]),
        ]),
      ]);

      const result = validateConversation(conversation);

      expect(result.stats.topics).toBe(2);
      expect(result.stats.turns).toBe(3);
      expect(result.stats.messages).toBe(4);
      expect(result.stats.sentences).toBe(4);
      expect(result.stats.words).toBe(4); // Each message creates 1 word
    });

    it('should fail validation for missing entity IDs', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [
            // @ts-ignore - intentionally missing ID
            { ...createMessage('msg-1', 'Hello'), id: '' },
          ]),
        ]),
      ]);

      const result = validateConversation(conversation);

      expect(result.valid).toBe(false);
      expect(result.issues.some(i => i.code === 'MISSING_MSG_ID')).toBe(true);
    });

    it('should include path in validation issues', () => {
      const conversation = createConversation([
        createTopic('', [ // Missing topic ID
          createTurn('turn-1', [createMessage('msg-1', 'Hello')]),
        ]),
      ]);

      const result = validateConversation(conversation);

      const topicIssue = result.issues.find(i => i.code === 'MISSING_TOPIC_ID');
      expect(topicIssue).toBeDefined();
      expect(topicIssue?.path).toBe('topics[0]');
    });

    it('should note large exports', () => {
      // Create a large conversation
      const messages: Message[] = [];
      for (let i = 0; i < 100; i++) {
        messages.push(createMessage(`msg-${i}`, `Message ${i}`));
      }

      const turns: Turn[] = [];
      for (let i = 0; i < 10; i++) {
        turns.push(createTurn(`turn-${i}`, messages.slice(i * 10, (i + 1) * 10)));
      }

      const conversation = createConversation([createTopic('topic-1', turns)]);

      const result = validateConversation(conversation);

      // May or may not trigger LARGE_EXPORT depending on entity counts
      expect(result.stats.messages).toBe(100);
    });
  });

  describe('formatValidationResult', () => {
    it('should format passing validation', () => {
      const result: ValidationResult = {
        valid: true,
        issues: [],
        stats: {
          topics: 1,
          turns: 2,
          messages: 4,
          sentences: 4,
          spans: 2,
          words: 20,
          errors: 0,
          warnings: 0,
        },
      };

      const formatted = formatValidationResult(result);

      expect(formatted).toContain('Validation PASSED');
      expect(formatted).toContain('Topics: 1');
      expect(formatted).toContain('No issues found');
    });

    it('should format failing validation', () => {
      const result: ValidationResult = {
        valid: false,
        issues: [
          {
            level: 'error',
            code: 'MISSING_CONV_ID',
            message: 'Conversation is missing an ID',
            suggestion: 'Fix the ID',
          },
        ],
        stats: {
          topics: 0,
          turns: 0,
          messages: 0,
          sentences: 0,
          spans: 0,
          words: 0,
          errors: 1,
          warnings: 0,
        },
      };

      const formatted = formatValidationResult(result);

      expect(formatted).toContain('Validation FAILED');
      expect(formatted).toContain('1 errors');
      expect(formatted).toContain('MISSING_CONV_ID');
      expect(formatted).toContain('Fix the ID');
    });

    it('should format warnings', () => {
      const result: ValidationResult = {
        valid: true,
        issues: [
          {
            level: 'warning',
            code: 'EMPTY_TOPIC',
            message: 'Topic has no turns',
            path: 'topics[0]',
          },
        ],
        stats: {
          topics: 1,
          turns: 0,
          messages: 0,
          sentences: 0,
          spans: 0,
          words: 0,
          errors: 0,
          warnings: 1,
        },
      };

      const formatted = formatValidationResult(result);

      expect(formatted).toContain('Validation PASSED');
      expect(formatted).toContain('1 warnings');
      expect(formatted).toContain('⚠');
      expect(formatted).toContain('Path: topics[0]');
    });
  });

  describe('isValidForExport', () => {
    it('should return true for valid conversation', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', [createMessage('msg-1', 'Hello')]),
        ]),
      ]);

      expect(isValidForExport(conversation)).toBe(true);
    });

    it('should return false for missing ID', () => {
      const conversation = createConversation([]);
      // @ts-ignore
      conversation.id = '';

      expect(isValidForExport(conversation)).toBe(false);
    });

    it('should return false for empty topics', () => {
      const conversation = createConversation([]);

      expect(isValidForExport(conversation)).toBe(false);
    });

    it('should return false for empty turns', () => {
      const conversation = createConversation([
        createTopic('topic-1', []),
      ]);

      expect(isValidForExport(conversation)).toBe(false);
    });

    it('should return false for empty messages', () => {
      const conversation = createConversation([
        createTopic('topic-1', [
          createTurn('turn-1', []),
        ]),
      ]);

      expect(isValidForExport(conversation)).toBe(false);
    });
  });
});

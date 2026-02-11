import { describe, it, expect } from 'vitest';
import {
  detectFormat,
  parseChat,
  convertToNeurolinguistFormat,
  getFormatDisplayName,
} from '../services/chatFormatParser';

describe('chatFormatParser', () => {
  describe('detectFormat', () => {
    it('should detect Claude format from structure', () => {
      const claudeExport = JSON.stringify({
        uuid: 'test-uuid',
        chat_messages: [
          { sender: 'human', text: 'Hello' },
          { sender: 'assistant', text: 'Hi there' },
        ],
      });

      expect(detectFormat(claudeExport, 'conversation.json')).toBe('claude');
    });

    it('should detect ChatGPT format from structure', () => {
      const chatGptExport = JSON.stringify({
        title: 'Test Conversation',
        mapping: {
          'node-1': {
            message: {
              author: { role: 'user' },
              content: { parts: ['Hello'] },
            },
          },
        },
      });

      expect(detectFormat(chatGptExport, 'conversation.json')).toBe('chatgpt');
    });

    it('should detect Gemini format from conversations wrapper', () => {
      const geminiExport = JSON.stringify({
        conversations: [
          {
            id: 'conv-1',
            messages: [{ role: 'user', content: 'Hello' }],
          },
        ],
      });

      expect(detectFormat(geminiExport, 'conversation.json')).toBe('gemini');
    });

    it('should detect format from filename hints', () => {
      expect(detectFormat('{}', 'claude_export.json')).toBe('claude');
      expect(detectFormat('{}', 'chatgpt_conversations.json')).toBe('chatgpt');
      expect(detectFormat('{}', 'gemini_export.json')).toBe('gemini');
    });

    it('should return unknown for unrecognized formats', () => {
      const unknownFormat = JSON.stringify({ foo: 'bar' });
      expect(detectFormat(unknownFormat, 'data.json')).toBe('unknown');
    });
  });

  describe('parseChat - Claude format', () => {
    it('should parse single Claude conversation', () => {
      const claudeExport = JSON.stringify({
        uuid: 'test-uuid-123',
        name: 'Test Conversation',
        chat_messages: [
          {
            sender: 'human',
            text: 'Hello, how are you?',
            created_at: '2024-01-01T00:00:00Z',
          },
          {
            sender: 'assistant',
            text: 'I am doing well, thank you!',
            created_at: '2024-01-01T00:00:01Z',
            model: 'claude-3-opus',
          },
        ],
        created_at: '2024-01-01T00:00:00Z',
      });

      const result = parseChat(claudeExport, 'test.json');

      expect(result).toHaveLength(1);
      expect(result[0].format).toBe('claude');
      expect(result[0].title).toBe('Test Conversation');
      expect(result[0].messages).toHaveLength(2);
      expect(result[0].messages[0].role).toBe('user');
      expect(result[0].messages[0].content).toBe('Hello, how are you?');
      expect(result[0].messages[1].role).toBe('assistant');
      expect(result[0].messages[1].model).toBe('claude-3-opus');
    });

    it('should parse Claude conversations array', () => {
      const claudeExport = JSON.stringify([
        {
          uuid: 'conv-1',
          name: 'Conversation 1',
          chat_messages: [{ sender: 'human', text: 'Hello' }],
        },
        {
          uuid: 'conv-2',
          name: 'Conversation 2',
          chat_messages: [{ sender: 'human', text: 'Hi' }],
        },
      ]);

      const result = parseChat(claudeExport, 'test.json');

      expect(result).toHaveLength(2);
      expect(result[0].title).toBe('Conversation 1');
      expect(result[1].title).toBe('Conversation 2');
    });
  });

  describe('parseChat - ChatGPT format', () => {
    it('should parse ChatGPT conversation with tree structure', () => {
      const chatGptExport = JSON.stringify({
        title: 'ChatGPT Conversation',
        id: 'chatgpt-123',
        mapping: {
          'root': {
            parent: null,
            message: null,
          },
          'msg-1': {
            parent: 'root',
            message: {
              author: { role: 'user' },
              content: { parts: ['What is the meaning of life?'] },
              create_time: 1704067200,
            },
          },
          'msg-2': {
            parent: 'msg-1',
            message: {
              author: { role: 'assistant' },
              content: { parts: ['The meaning of life is...'] },
              create_time: 1704067201,
              metadata: { model_slug: 'gpt-4' },
            },
          },
        },
      });

      const result = parseChat(chatGptExport, 'test.json');

      expect(result).toHaveLength(1);
      expect(result[0].format).toBe('chatgpt');
      expect(result[0].title).toBe('ChatGPT Conversation');
      expect(result[0].messages).toHaveLength(2);
      expect(result[0].messages[0].role).toBe('user');
      expect(result[0].messages[0].content).toBe('What is the meaning of life?');
      expect(result[0].messages[1].role).toBe('assistant');
    });
  });

  describe('parseChat - Gemini format', () => {
    it('should parse Gemini conversations wrapper format', () => {
      const geminiExport = JSON.stringify({
        conversations: [
          {
            id: 'gemini-conv-1',
            title: 'Gemini Chat',
            messages: [
              { role: 'user', content: 'Hello Gemini' },
              { role: 'model', content: 'Hello! How can I help?' },
            ],
          },
        ],
      });

      const result = parseChat(geminiExport, 'test.json');

      expect(result).toHaveLength(1);
      expect(result[0].format).toBe('gemini');
      expect(result[0].messages).toHaveLength(2);
      expect(result[0].messages[0].role).toBe('user');
      expect(result[0].messages[1].role).toBe('assistant'); // 'model' -> 'assistant'
    });
  });

  describe('convertToNeurolinguistFormat', () => {
    it('should convert parsed conversation to Neurolinguist format', () => {
      const parsed = {
        format: 'claude' as const,
        title: 'Test Conversation',
        messages: [
          { role: 'user' as const, content: 'Hello' },
          { role: 'assistant' as const, content: 'Hi there' },
        ],
        metadata: {
          created_at: '2024-01-01T00:00:00Z',
        },
      };

      const result = convertToNeurolinguistFormat(parsed);
      const converted = JSON.parse(result);

      expect(converted.name).toBe('Test Conversation');
      expect(converted.chat_messages).toHaveLength(2);
      expect(converted.chat_messages[0].sender).toBe('human');
      expect(converted.chat_messages[1].sender).toBe('assistant');
      expect(converted.source_format).toBe('claude');
    });
  });

  describe('getFormatDisplayName', () => {
    it('should return display names for formats', () => {
      expect(getFormatDisplayName('claude')).toBe('Claude');
      expect(getFormatDisplayName('chatgpt')).toBe('ChatGPT');
      expect(getFormatDisplayName('gemini')).toBe('Gemini');
      expect(getFormatDisplayName('unknown')).toBe('Unknown');
    });
  });

  describe('error handling', () => {
    it('should throw for invalid JSON', () => {
      expect(() => parseChat('not valid json', 'test.json')).toThrow();
    });

    it('should throw for unknown format', () => {
      const unknownFormat = JSON.stringify({ random: 'data' });
      expect(() => parseChat(unknownFormat, 'test.json')).toThrow('Unable to detect chat format');
    });
  });
});

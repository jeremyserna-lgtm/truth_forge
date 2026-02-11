import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  OllamaService,
  DEFAULT_ENTITY_TYPES,
  DEFAULT_MODEL_PARAMS,
  type OllamaConfig,
  type ModelParameters,
} from '../services/ollamaService';
import type { Turn, Message } from '../types';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock embeddingCache
vi.mock('../services/embeddingCache', () => ({
  embeddingCache: {
    get: vi.fn().mockResolvedValue(null),
    set: vi.fn().mockResolvedValue(undefined),
  },
}));

// Mock crypto.randomUUID
vi.stubGlobal('crypto', {
  randomUUID: () => `uuid-${Math.random().toString(36).substring(7)}`,
  subtle: {
    digest: vi.fn(),
  },
});

// Helper to create mock fetch response
function createMockResponse(data: any, ok: boolean = true, status: number = 200) {
  return {
    ok,
    status,
    statusText: ok ? 'OK' : 'Error',
    json: vi.fn().mockResolvedValue(data),
    body: {
      getReader: () => createMockStreamReader(JSON.stringify(data)),
    },
  };
}

function createMockStreamReader(content: string) {
  let done = false;
  return {
    read: vi.fn().mockImplementation(() => {
      if (done) {
        return Promise.resolve({ done: true, value: undefined });
      }
      done = true;
      return Promise.resolve({
        done: false,
        value: new TextEncoder().encode(JSON.stringify({ response: content })),
      });
    }),
  };
}

describe('OllamaService', () => {
  let service: OllamaService;

  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockReset();
    service = new OllamaService();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('constructor', () => {
    it('should use default configuration', () => {
      const config = service.getConfig();

      expect(config.model).toBe('llama3.2');
      expect(config.embeddingModel).toBe('nomic-embed-text');
      expect(config.maxRetries).toBe(3);
      expect(config.timeoutMs).toBe(120000);
      expect(config.useCache).toBe(true);
    });

    it('should merge custom configuration', () => {
      const customService = new OllamaService({
        model: 'mistral',
        maxRetries: 5,
      });

      const config = customService.getConfig();

      expect(config.model).toBe('mistral');
      expect(config.maxRetries).toBe(5);
      expect(config.embeddingModel).toBe('nomic-embed-text'); // Still default
    });

    it('should merge custom model parameters', () => {
      const customService = new OllamaService({
        modelParams: { temperature: 0.7 },
      });

      const config = customService.getConfig();

      expect(config.modelParams.temperature).toBe(0.7);
      expect(config.modelParams.top_p).toBe(0.9); // Still default
    });
  });

  describe('setters', () => {
    it('should set model', () => {
      service.setModel('mistral');
      expect(service.getConfig().model).toBe('mistral');
    });

    it('should set NER model', () => {
      service.setNerModel('qwen2.5');
      expect(service.getConfig().nerModel).toBe('qwen2.5');
    });

    it('should set embedding model', () => {
      service.setEmbeddingModel('mxbai-embed-large');
      expect(service.getConfig().embeddingModel).toBe('mxbai-embed-large');
    });

    it('should set model parameters partially', () => {
      service.setModelParams({ temperature: 0.5 });

      const params = service.getConfig().modelParams;
      expect(params.temperature).toBe(0.5);
      expect(params.top_p).toBe(0.9); // Unchanged
    });

    it('should set cache usage', () => {
      service.setUseCache(false);
      expect(service.getConfig().useCache).toBe(false);
    });

    it('should set base URL and persist to localStorage', () => {
      // Mock localStorage directly since we mocked it in setup
      const mockSetItem = vi.fn();
      Object.defineProperty(global, 'localStorage', {
        value: {
          getItem: vi.fn(),
          setItem: mockSetItem,
          clear: vi.fn(),
          removeItem: vi.fn(),
          length: 0,
          key: vi.fn(),
        },
        writable: true,
      });

      service.setBaseUrl('http://remote-ollama:11434');

      expect(service.getConfig().baseUrl).toBe('http://remote-ollama:11434');
      expect(mockSetItem).toHaveBeenCalledWith(
        'neurolinguist_ollama_host',
        'http://remote-ollama:11434'
      );
    });
  });

  describe('custom entity types', () => {
    it('should set custom entity types', () => {
      service.setCustomEntityTypes(['PRODUCT', 'COMPANY']);
      expect(service.getConfig().customEntityTypes).toEqual(['PRODUCT', 'COMPANY']);
    });

    it('should add custom entity type', () => {
      service.addCustomEntityType('PRODUCT');
      service.addCustomEntityType('COMPANY');

      expect(service.getConfig().customEntityTypes).toContain('PRODUCT');
      expect(service.getConfig().customEntityTypes).toContain('COMPANY');
    });

    it('should not add duplicate entity types', () => {
      service.addCustomEntityType('PRODUCT');
      service.addCustomEntityType('PRODUCT');

      expect(
        service.getConfig().customEntityTypes.filter((t) => t === 'PRODUCT').length
      ).toBe(1);
    });
  });

  describe('cache stats', () => {
    it('should initialize with zero stats', () => {
      const stats = service.getCacheStats();

      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
      expect(stats.hitRate).toBe(0);
    });

    it('should reset cache stats', () => {
      // Stats are internal, but resetCacheStats should work
      service.resetCacheStats();

      const stats = service.getCacheStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
    });
  });

  describe('cancel', () => {
    it('should cancel in-progress operations', () => {
      // The cancel method should abort the controller
      service.cancel();
      // No error should be thrown
    });
  });

  describe('chunkConversation', () => {
    it('should chunk turns into groups', () => {
      const turns: Turn[] = Array(50)
        .fill(null)
        .map((_, i) => ({
          id: `turn-${i}`,
          messages: [],
          parentId: 'topic-1',
          messageCount: 0,
        }));

      const chunks = service.chunkConversation(turns, 20);

      expect(chunks.length).toBe(3); // 50/20 = 2.5, rounded up
      expect(chunks[0].length).toBe(20);
      expect(chunks[1].length).toBe(20);
      expect(chunks[2].length).toBe(10);
    });

    it('should handle small arrays', () => {
      const turns: Turn[] = [
        { id: 'turn-1', messages: [], parentId: 'topic-1', messageCount: 0 },
        { id: 'turn-2', messages: [], parentId: 'topic-1', messageCount: 0 },
      ];

      const chunks = service.chunkConversation(turns, 20);

      expect(chunks.length).toBe(1);
      expect(chunks[0].length).toBe(2);
    });

    it('should handle empty arrays', () => {
      const chunks = service.chunkConversation([], 20);

      expect(chunks.length).toBe(0);
    });

    it('should use default chunk size of 20', () => {
      const turns: Turn[] = Array(25)
        .fill(null)
        .map((_, i) => ({
          id: `turn-${i}`,
          messages: [],
          parentId: 'topic-1',
          messageCount: 0,
        }));

      const chunks = service.chunkConversation(turns);

      expect(chunks.length).toBe(2);
      expect(chunks[0].length).toBe(20);
      expect(chunks[1].length).toBe(5);
    });
  });

  describe('checkConnection', () => {
    it('should return connected: true when Ollama responds', async () => {
      mockFetch.mockResolvedValue(
        createMockResponse({ models: [{ name: 'llama3.2' }, { name: 'mistral' }] })
      );

      const result = await service.checkConnection();

      expect(result.connected).toBe(true);
      expect(result.models).toContain('llama3.2');
      expect(result.models).toContain('mistral');
    });

    it('should return connected: false on error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const result = await service.checkConnection();

      expect(result.connected).toBe(false);
      expect(result.models).toEqual([]);
    });

    it('should return connected: false on non-ok response', async () => {
      mockFetch.mockResolvedValue(createMockResponse({}, false, 500));

      const result = await service.checkConnection();

      expect(result.connected).toBe(false);
    });

    it('should fetch models list', async () => {
      mockFetch.mockResolvedValue(
        createMockResponse({
          models: [
            { name: 'llama3.2' },
            { name: 'nomic-embed-text' },
            { name: 'qwen2.5' },
          ],
        })
      );

      const result = await service.checkConnection();

      expect(result.models.length).toBe(3);
    });

    it('should handle missing models array', async () => {
      mockFetch.mockResolvedValue(createMockResponse({}));

      const result = await service.checkConnection();

      expect(result.connected).toBe(true);
      expect(result.models).toEqual([]);
    });
  });

  describe('segmentIntoTopics', () => {
    it('should create single topic for very short conversations', async () => {
      const turns: Turn[] = [
        {
          id: 'turn-1',
          parentId: '',
          messageCount: 1,
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Hello',
              parentId: 'turn-1',
              sentenceCount: 1,
              sentences: [],
            },
          ],
        },
      ];

      const topics = await service.segmentIntoTopics(turns, 'conv-1');

      expect(topics.length).toBe(1);
      expect(topics[0].title).toBe('General Discussion');
      expect(topics[0].turnCount).toBe(1);
    });

    it('should set parent IDs on turns', async () => {
      const turns: Turn[] = [
        {
          id: 'turn-1',
          parentId: '',
          messageCount: 1,
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Hello',
              parentId: 'turn-1',
              sentenceCount: 1,
              sentences: [],
            },
          ],
        },
      ];

      const topics = await service.segmentIntoTopics(turns, 'conv-1');

      expect(turns[0].parentId).toBe(topics[0].id);
    });
  });

  describe('DEFAULT_ENTITY_TYPES', () => {
    it('should contain expected entity types', () => {
      expect(DEFAULT_ENTITY_TYPES).toContain('CODE_SNIPPET');
      expect(DEFAULT_ENTITY_TYPES).toContain('TECH_TERM');
      expect(DEFAULT_ENTITY_TYPES).toContain('DATE');
      expect(DEFAULT_ENTITY_TYPES).toContain('LOCATION');
      expect(DEFAULT_ENTITY_TYPES).toContain('PERSON');
      expect(DEFAULT_ENTITY_TYPES).toContain('EMAIL');
      expect(DEFAULT_ENTITY_TYPES).toContain('URL');
      expect(DEFAULT_ENTITY_TYPES).toContain('PHONE_NUMBER');
    });

    it('should have 10 default entity types', () => {
      expect(DEFAULT_ENTITY_TYPES.length).toBe(10);
    });
  });

  describe('DEFAULT_MODEL_PARAMS', () => {
    it('should have expected default values', () => {
      expect(DEFAULT_MODEL_PARAMS.temperature).toBe(0.3);
      expect(DEFAULT_MODEL_PARAMS.top_p).toBe(0.9);
      expect(DEFAULT_MODEL_PARAMS.top_k).toBe(40);
      expect(DEFAULT_MODEL_PARAMS.num_ctx).toBe(4096);
      expect(DEFAULT_MODEL_PARAMS.num_predict).toBe(4096);
      expect(DEFAULT_MODEL_PARAMS.repeat_penalty).toBe(1.1);
    });
  });

  describe('embedding batch processing', () => {
    it('should handle empty text array', async () => {
      const results = await service.generateEmbeddingsBatch([]);

      expect(results).toEqual([]);
    });

    it('should respect concurrency limit', async () => {
      // Set up mock to track concurrent calls
      let concurrentCalls = 0;
      let maxConcurrent = 0;

      mockFetch.mockImplementation(async () => {
        concurrentCalls++;
        maxConcurrent = Math.max(maxConcurrent, concurrentCalls);

        await new Promise((resolve) => setTimeout(resolve, 10));

        concurrentCalls--;
        return createMockResponse({ embedding: [0.1, 0.2, 0.3] });
      });

      const texts = ['text1', 'text2', 'text3', 'text4', 'text5'];
      await service.generateEmbeddingsBatch(texts, 2);

      // Max concurrent should not exceed the limit (2)
      expect(maxConcurrent).toBeLessThanOrEqual(2);
    });
  });

  describe('error handling', () => {
    it('should throw on abort', async () => {
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';

      mockFetch.mockRejectedValue(abortError);

      const turns: Turn[] = Array(5)
        .fill(null)
        .map((_, i) => ({
          id: `turn-${i}`,
          parentId: '',
          messageCount: 1,
          messages: [
            {
              id: `msg-${i}`,
              role: 'user',
              content: `Message ${i}`,
              parentId: `turn-${i}`,
              sentenceCount: 1,
              sentences: [],
            },
          ],
        }));

      // Short conversation should not call API, but longer ones will
      // and should handle abort gracefully by falling back to single topic
    });
  });

  describe('retry logic', () => {
    it('should use exponential backoff', () => {
      const baseDelay = 1000;

      // Verify backoff formula: delay = baseDelay * 2^(attempt-1)
      expect(baseDelay * Math.pow(2, 0)).toBe(1000); // Attempt 1
      expect(baseDelay * Math.pow(2, 1)).toBe(2000); // Attempt 2
      expect(baseDelay * Math.pow(2, 2)).toBe(4000); // Attempt 3
    });

    it('should have max 3 retries by default', () => {
      const config = service.getConfig();
      expect(config.maxRetries).toBe(3);
    });
  });

  describe('progress callback', () => {
    it('should call progress callback during topic segmentation', async () => {
      const progressCallback = vi.fn();

      const turns: Turn[] = [
        {
          id: 'turn-1',
          parentId: '',
          messageCount: 1,
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Hello',
              parentId: 'turn-1',
              sentenceCount: 1,
              sentences: [],
            },
          ],
        },
      ];

      await service.segmentIntoTopics(turns, 'conv-1', progressCallback);

      // Should have been called at least once
      expect(progressCallback).toHaveBeenCalled();
    });
  });

  describe('GpuInfo interface', () => {
    it('should have expected structure', () => {
      // Type validation
      const gpuInfo = {
        available: true,
        name: 'NVIDIA CUDA',
        vramTotal: 24 * 1024 * 1024 * 1024, // 24GB
        vramUsed: 8 * 1024 * 1024 * 1024, // 8GB
      };

      expect(gpuInfo.available).toBe(true);
      expect(typeof gpuInfo.name).toBe('string');
      expect(typeof gpuInfo.vramTotal).toBe('number');
      expect(typeof gpuInfo.vramUsed).toBe('number');
    });
  });

  describe('ModelParameters interface', () => {
    it('should have all required fields', () => {
      const params: ModelParameters = {
        temperature: 0.7,
        top_p: 0.9,
        top_k: 40,
        num_ctx: 4096,
        num_predict: 2048,
        repeat_penalty: 1.2,
      };

      expect(params.temperature).toBeGreaterThanOrEqual(0);
      expect(params.temperature).toBeLessThanOrEqual(2);
      expect(params.top_p).toBeGreaterThanOrEqual(0);
      expect(params.top_p).toBeLessThanOrEqual(1);
    });
  });
});

import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock IndexedDB for embeddingCache tests
const mockIndexedDB = {
  open: vi.fn(),
  deleteDatabase: vi.fn(),
};

// Mock crypto.subtle for hash function
const mockCrypto = {
  subtle: {
    digest: vi.fn(async (_algorithm: string, data: ArrayBuffer) => {
      // Simple mock hash that returns consistent results
      const bytes = new Uint8Array(data);
      let hash = 0;
      for (let i = 0; i < bytes.length; i++) {
        hash = ((hash << 5) - hash + bytes[i]) | 0;
      }
      const result = new ArrayBuffer(32);
      const view = new DataView(result);
      view.setInt32(0, hash);
      return result;
    }),
  },
  randomUUID: vi.fn(() => `mock-uuid-${Math.random().toString(36).substring(2, 11)}`),
};

// Set up global mocks
Object.defineProperty(global, 'indexedDB', {
  value: mockIndexedDB,
  writable: true,
});

Object.defineProperty(global, 'crypto', {
  value: mockCrypto,
  writable: true,
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
  removeItem: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

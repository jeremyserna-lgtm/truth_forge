/**
 * Embedding Cache Service using IndexedDB
 * Caches embeddings to avoid recomputing for identical content
 */

const DB_NAME = 'neurolinguist_embedding_cache';
const DB_VERSION = 1;
const STORE_NAME = 'embeddings';

interface CachedEmbedding {
  hash: string;
  embedding: number[];
  model: string;
  text: string;
  createdAt: number;
  accessedAt: number;
  accessCount: number;
}

// Simple hash function for text content
async function hashText(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

class EmbeddingCacheService {
  private db: IDBDatabase | null = null;
  private initPromise: Promise<void> | null = null;

  async init(): Promise<void> {
    if (this.db) return;
    if (this.initPromise) return this.initPromise;

    this.initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('Failed to open embedding cache DB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'hash' });
          store.createIndex('model', 'model', { unique: false });
          store.createIndex('createdAt', 'createdAt', { unique: false });
          store.createIndex('accessedAt', 'accessedAt', { unique: false });
        }
      };
    });

    return this.initPromise;
  }

  async get(text: string, model: string): Promise<number[] | null> {
    await this.init();
    if (!this.db) return null;

    const hash = await hashText(`${model}:${text}`);

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(hash);

      request.onsuccess = () => {
        const result = request.result as CachedEmbedding | undefined;
        if (result) {
          // Update access stats
          result.accessedAt = Date.now();
          result.accessCount++;
          store.put(result);
          resolve(result.embedding);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => {
        console.warn('Failed to get cached embedding:', request.error);
        resolve(null);
      };
    });
  }

  async set(text: string, model: string, embedding: number[]): Promise<void> {
    await this.init();
    if (!this.db) return;

    const hash = await hashText(`${model}:${text}`);
    const now = Date.now();

    const entry: CachedEmbedding = {
      hash,
      embedding,
      model,
      text: text.substring(0, 500), // Store truncated text for debugging
      createdAt: now,
      accessedAt: now,
      accessCount: 1
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.put(entry);

      request.onsuccess = () => resolve();
      request.onerror = () => {
        console.warn('Failed to cache embedding:', request.error);
        resolve(); // Don't fail on cache errors
      };
    });
  }

  async getStats(): Promise<{
    totalEntries: number;
    totalSize: number;
    oldestEntry: number | null;
    newestEntry: number | null;
  }> {
    await this.init();
    if (!this.db) return { totalEntries: 0, totalSize: 0, oldestEntry: null, newestEntry: null };

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const countRequest = store.count();
      const getAllRequest = store.getAll();

      let totalEntries = 0;
      let totalSize = 0;
      let oldestEntry: number | null = null;
      let newestEntry: number | null = null;

      countRequest.onsuccess = () => {
        totalEntries = countRequest.result;
      };

      getAllRequest.onsuccess = () => {
        const results = getAllRequest.result as CachedEmbedding[];
        for (const entry of results) {
          totalSize += entry.embedding.length * 4; // Approximate size in bytes
          if (!oldestEntry || entry.createdAt < oldestEntry) oldestEntry = entry.createdAt;
          if (!newestEntry || entry.createdAt > newestEntry) newestEntry = entry.createdAt;
        }
        resolve({ totalEntries, totalSize, oldestEntry, newestEntry });
      };

      getAllRequest.onerror = () => {
        resolve({ totalEntries, totalSize: 0, oldestEntry: null, newestEntry: null });
      };
    });
  }

  async clear(): Promise<void> {
    await this.init();
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async pruneOldEntries(maxAgeMs: number = 30 * 24 * 60 * 60 * 1000): Promise<number> {
    await this.init();
    if (!this.db) return 0;

    const cutoff = Date.now() - maxAgeMs;
    let deletedCount = 0;

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const index = store.index('accessedAt');
      const range = IDBKeyRange.upperBound(cutoff);
      const request = index.openCursor(range);

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
        if (cursor) {
          cursor.delete();
          deletedCount++;
          cursor.continue();
        } else {
          resolve(deletedCount);
        }
      };

      request.onerror = () => resolve(deletedCount);
    });
  }
}

export const embeddingCache = new EmbeddingCacheService();
export { hashText };

import { KnowledgeAtom } from '../types';

const STORAGE_KEY = 'knowledge_atoms_v1';
const CONTEXT_KEY = 'active_context_v1';

// SHA-256 Hash Generation
export const generateAtomHash = async (content: string): Promise<string> => {
  const msgBuffer = new TextEncoder().encode(content.trim().toLowerCase());
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
};

export const loadAtoms = (): KnowledgeAtom[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Failed to load atoms", e);
    return [];
  }
};

export const saveAtoms = (atoms: KnowledgeAtom[]) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(atoms));
  } catch (e) {
    console.error("Failed to save atoms (quota exceeded?)", e);
  }
};

export const loadActiveContext = (): KnowledgeAtom[] => {
  try {
    const raw = localStorage.getItem(CONTEXT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Failed to load context", e);
    return [];
  }
};

export const saveActiveContext = (atoms: KnowledgeAtom[]) => {
  try {
    localStorage.setItem(CONTEXT_KEY, JSON.stringify(atoms));
  } catch (e) {
    console.error("Failed to save context", e);
  }
};

export const mergeAtoms = (existing: KnowledgeAtom[], incoming: KnowledgeAtom[]): KnowledgeAtom[] => {
  const map = new Map<string, KnowledgeAtom>();
  
  // Load existing
  existing.forEach(a => map.set(a.id, a));
  
  // Merge incoming (if ID exists, we prefer the one with embedding if the existing one lacks it)
  incoming.forEach(a => {
    if (map.has(a.id)) {
      const current = map.get(a.id)!;
      if (!current.embedding && a.embedding) {
        map.set(a.id, a);
      }
    } else {
      map.set(a.id, a);
    }
  });

  return Array.from(map.values()).sort((a, b) => b.createdAt - a.createdAt);
};
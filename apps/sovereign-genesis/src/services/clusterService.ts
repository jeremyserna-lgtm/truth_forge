import { KnowledgeAtom, Cluster } from '../types';

// Cosine Similarity
const cosineSimilarity = (vecA: number[], vecB: number[]): number => {
    if (!vecA || !vecB || vecA.length !== vecB.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < vecA.length; i++) {
        dotProduct += vecA[i] * vecB[i];
        normA += vecA[i] * vecA[i];
        normB += vecB[i] * vecB[i];
    }
    
    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
};

// Simple Leader-Follower Clustering approach for client-side
export const clusterAtoms = (atoms: KnowledgeAtom[], threshold: number = 0.85): Cluster[] => {
    // 1. Filter atoms with embeddings
    const vectors = atoms.filter(a => a.embedding && a.embedding.length > 0);
    if (vectors.length === 0) return [];

    const clusters: Cluster[] = [];
    const visited = new Set<string>();

    for (const leader of vectors) {
        if (visited.has(leader.id)) continue;
        visited.add(leader.id);

        const currentClusterItems: KnowledgeAtom[] = [];

        // Find followers
        for (const candidate of vectors) {
            if (leader.id === candidate.id) continue;
            if (visited.has(candidate.id)) continue;

            const sim = cosineSimilarity(leader.embedding!, candidate.embedding!);
            if (sim >= threshold) {
                currentClusterItems.push(candidate);
                visited.add(candidate.id);
            }
        }

        clusters.push({
            id: `cluster-${leader.id}`,
            label: leader.metadata?.theme || 'General',
            centroid: leader,
            items: currentClusterItems
        });
    }

    return clusters.sort((a, b) => (b.items.length + 1) - (a.items.length + 1));
};

// Normalize (reduce) knowledge base
export const normalizeKnowledge = (atoms: KnowledgeAtom[], threshold: number = 0.90): KnowledgeAtom[] => {
    // Only keep centroids of very tight clusters
    const clusters = clusterAtoms(atoms, threshold);
    const centroids = clusters.map(c => c.centroid);
    
    // Also keep atoms that didn't form clusters (outliers are often unique signal)
    const centroidIds = new Set(centroids.map(c => c.id));
    const clusteredItemIds = new Set(clusters.flatMap(c => c.items.map(i => i.id)));
    
    const outliers = atoms.filter(a => !centroidIds.has(a.id) && !clusteredItemIds.has(a.id));
    
    return [...centroids, ...outliers];
};
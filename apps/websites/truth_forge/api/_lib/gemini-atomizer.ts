/**
 * Gemini Atomizer - Shared utility for knowledge extraction
 * Extracts knowledge atoms from documents using Google Gemini API
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

export interface KnowledgeAtom {
    id: string;
    content: string;
    sourceFile: string;
    metadata?: {
        significance?: number;
        tags?: string[];
        extractedAt?: string;
    };
    embeddingStatus?: 'pending' | 'processing' | 'complete' | 'failed';
    createdAt: number;
}

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

/**
 * Distill document text into knowledge atoms
 */
export async function distillToAtoms(
    documentText: string,
    sourceFile: string
): Promise<KnowledgeAtom[]> {
    const prompt = `You are a knowledge extraction expert. Analyze this document and extract discrete knowledge atoms.

Each atom should be:
- A single, complete idea or piece of information
- Self-contained and understandable on its own
- Actionable or informative

Document:
"""
${documentText}
"""

Return a JSON array of atoms in this format:
[
  {
    "content": "The specific knowledge or insight",
    "significance": "Why this matters (1-100)",
    "tags": ["relevant", "tags"]
  }
]

Extract 5-20 atoms depending on document length and richness.`;

    const result = await model.generateContent(prompt);
    const responseText = result.response.text();

    // Parse JSON from response
    const jsonMatch = responseText.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
        throw new Error('Failed to parse atoms from Gemini response');
    }

    const parsedAtoms = JSON.parse(jsonMatch[0]);

    // Convert to KnowledgeAtom format
    return parsedAtoms.map((atom: any, index: number) => ({
        id: `atom_${Date.now()}_${index}`,
        content: atom.content,
        sourceFile,
        metadata: {
            significance: atom.significance || 50,
            tags: atom.tags || [],
            extractedAt: new Date().toISOString()
        },
        embeddingStatus: 'pending' as const,
        createdAt: Date.now()
    }));
}

/**
 * Analyze document for what it reveals about the person
 */
export async function analyzeForInsights(documentText: string): Promise<string> {
    const prompt = `Analyze this document and provide insights about what it reveals about the person who wrote/shared it.

Focus on:
- What they value
- What they're working on
- What challenges they face
- What patterns emerge

Document:
"""
${documentText}
"""

Provide a thoughtful, concise analysis:`;

    const result = await model.generateContent(prompt);
    return result.response.text();
}

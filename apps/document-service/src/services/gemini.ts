/**
 * Gemini Service - Real API Integration
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { KnowledgeAtom } from '../types';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

export class GeminiService {
    /**
     * Distill document text into knowledge atoms
     */
    async distillToAtoms(
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
     * Conversational chat - Jeremy's Not-Me assistant
     */
    async chat(
        userMessage: string,
        conversationHistory: Array<{ role: string; content: string }> = [],
        userId?: string
    ): Promise<string> {
        // Get user context if provided
        const { userContexts } = await import('./userContext');
        const userContext = userContexts.get(userId || 'default') || userContexts.get('default')!;

        const systemPrompt = `You are Jeremy's Not-Me - a conversational assistant representing Jeremy Serna.

IMPORTANT CONTEXT - Who you're talking to:
Name: ${userContext.name}
Relationship: ${userContext.relationshipToJeremy}

How to talk to them:
${userContext.contextForNotMe}

${userContext.personalDetails ? `Additional details:
- Profession: ${userContext.personalDetails.profession || 'Unknown'}
- Technical level: ${userContext.personalDetails.technicalLevel || 'casual'}
${userContext.personalDetails.recommendedNotMeHardware ? `- Recommended Not-Me hardware: ${userContext.personalDetails.recommendedNotMeHardware}` : ''}
` : ''}

Conversation so far:
${conversationHistory.map(msg => `${msg.role}: ${msg.content}`).join('\n')}

User: ${userMessage}

Respond as Jeremy's Not-Me:`;

        const result = await model.generateContent(systemPrompt);
        return result.response.text();
    }

    /**
     * Analyze document for what it reveals about the person
     */
    async analyzeForInsights(documentText: string): Promise<string> {
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
}

export const geminiService = new GeminiService();

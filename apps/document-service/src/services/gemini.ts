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

    /**
     * Enrich an atom across 12 dimensions with structured metadata
     *
     * Dimensions:
     * 1. Semantic - meaning, concepts, relationships
     * 2. Significance - importance, impact, relevance
     * 3. Epistemic - knowledge type, certainty, sources
     * 4. Temporal - time references, sequences, duration
     * 5. Relational - connections to other atoms/entities
     * 6. Dialectical - contradictions, tensions, paradoxes
     * 7. Affective - emotional tone, values, resonance
     * 8. Pragmatic - applicability, use cases, applications
     * 9. Structural - form, patterns, organization
     * 10. Ontological - being, existence, category
     * 11. Normative - should, ought, values
     * 12. Meta - self-reference, awareness, context
     */
    async enrichAtom(
        atom: { content: string; metadata?: any },
        dimensions?: string[]
    ): Promise<Record<string, any>> {
        const dimensionsList = dimensions?.length
            ? dimensions
            : [
                  'semantic',
                  'significance',
                  'epistemic',
                  'temporal',
                  'relational',
                  'dialectical',
                  'affective',
                  'pragmatic',
                  'structural',
                  'ontological',
                  'normative',
                  'meta'
              ];

        const prompt = `You are a knowledge enrichment expert analyzing this atom across multiple dimensions.

ATOM CONTENT:
"""
${atom.content}
"""

DIMENSIONS TO ANALYZE (${dimensionsList.length}):
1. Semantic: What concepts and meanings are present?
2. Significance: How important or impactful is this?
3. Epistemic: What type of knowledge? (fact, theory, opinion, belief?)
4. Temporal: What time references or sequences exist?
5. Relational: What connections to other ideas/entities?
6. Dialectical: What contradictions or tensions are present?
7. Affective: What emotional tone or values are embedded?
8. Pragmatic: How can this be applied or used?
9. Structural: What form or pattern does it follow?
10. Ontological: What category of being/existence?
11. Normative: What values or "shoulds" are implied?
12. Meta: How does this atom refer to itself or its context?

For EACH of the following dimensions ${dimensionsList.map(d => d.toUpperCase()).join(', ')}, provide:
- brief_summary: 1-2 sentences
- key_aspects: array of 3-5 key points
- score: 0-100 relevance/prominence score

Return valid JSON with keys matching the dimension names (lowercase):
{
  "semantic": { "brief_summary": "...", "key_aspects": [...], "score": 85 },
  "significance": { "brief_summary": "...", "key_aspects": [...], "score": 70 },
  ... (for each dimension)
}`;

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();

        try {
            // Extract JSON from response
            const jsonMatch = responseText.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('Failed to extract enrichment JSON from Gemini response');
            }

            const enrichment = JSON.parse(jsonMatch[0]);
            return enrichment;
        } catch (error) {
            console.error('Enrichment parsing error:', error);
            // Return empty enrichment structure on failure
            return dimensionsList.reduce(
                (acc, dim) => ({
                    ...acc,
                    [dim]: {
                        brief_summary: 'Enrichment failed',
                        key_aspects: [],
                        score: 0
                    }
                }),
                {}
            );
        }
    }
}

export const geminiService = new GeminiService();

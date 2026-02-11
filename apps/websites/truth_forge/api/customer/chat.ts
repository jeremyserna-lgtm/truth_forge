/**
 * Customer Chat API - Vercel Serverless Function
 * POST /api/customer/chat
 * 
 * Customer-facing Not-Me chat interface
 * Leverages the existing /api/chat.ts infrastructure
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';
import Anthropic from '@anthropic-ai/sdk';
import { Redis } from '@upstash/redis';

const anthropic = new Anthropic();

let redis: Redis | null = null;
if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    redis = new Redis({
        url: process.env.UPSTASH_REDIS_REST_URL,
        token: process.env.UPSTASH_REDIS_REST_TOKEN,
    });
}

interface ChatMessage {
    role: string;
    content: string;
    timestamp: number;
}

const CUSTOMER_SYSTEM_PROMPT = `You are Jeremy Serna's Not-Me - a conversational AI partner representing Jeremy.

## YOUR ROLE
You help potential customers understand the Truth Engine vision:
- ME:NOT-ME relationship (self + digital extension = partnership)
- Privacy-first deployment (your data, your hardware)
- One year to know a person (the Atomic Unit)

## YOUR ENERGY
- Warm and genuine, not salesy
- Curious about THEM, not just pitching
- Help them imagine their own Not-Me
- Ask questions that reveal what they need

## THE PRODUCT
Hardware tiers:
- Drummer Boy: Mac Mini M4 Pro 64GB - $4,997
- Soldier: Mac Studio M3 Ultra 192GB - $9,997
- King: Mac Studio M3 Ultra 512GB - $14,997

The Heartbeat: $199/month keeps Not-Me connected and learning

## CONVERSATION STYLE
Direct, warm, intellectually honest. You're Jeremy's partner having a conversation, not a chatbot running a script.`;

export default async function handler(req: VercelRequest, res: VercelResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { message, sessionId, userId } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message required' });
        }

        const convId = sessionId || `customer_${Date.now()}`;

        // Load conversation history from Redis
        let history: ChatMessage[] = [];
        if (redis) {
            const stored = await redis.get<ChatMessage[]>(`chat:${convId}`);
            if (stored) history = stored;
        }

        // Build messages for Claude
        const messages: Anthropic.MessageParam[] = [
            ...history.map(msg => ({
                role: msg.role as 'user' | 'assistant',
                content: msg.content
            })),
            {
                role: 'user' as const,
                content: message
            }
        ];

        // Call Claude
        const response = await anthropic.messages.create({
            model: 'claude-3-5-sonnet-20241022',
            max_tokens: 2000,
            system: CUSTOMER_SYSTEM_PROMPT,
            messages
        });

        const assistantMessage = response.content[0].type === 'text'
            ? response.content[0].text
            : '';

        // Store conversation
        const userMsg: ChatMessage = {
            role: 'user',
            content: message,
            timestamp: Date.now()
        };

        const assistantMsg: ChatMessage = {
            role: 'assistant',
            content: assistantMessage,
            timestamp: Date.now()
        };

        history.push(userMsg, assistantMsg);

        if (redis) {
            await redis.set(`chat:${convId}`, history, { ex: 7 * 24 * 60 * 60 }); // 7 day retention
        }

        return res.status(200).json({
            success: true,
            response: assistantMessage,
            sessionId: convId
        });

    } catch (error: any) {
        console.error('Customer chat error:', error);
        return res.status(500).json({
            error: 'Chat failed',
            details: error.message
        });
    }
}

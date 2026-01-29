/**
 * Customer Routes - Conversational Portal
 */

import { Router } from 'express';
import { geminiService } from '../../services/gemini';

interface ChatMessage {
    role: string;
    content: string;
    timestamp: number;
}

const router = Router();

// In-memory conversation storage (replace with DB later)
const conversations: Map<string, ChatMessage[]> = new Map();

/**
 * POST /customer/chat
 * Chat with Jeremy's Not-Me
 */
router.post('/chat', async (req, res) => {
    const { message, sessionId, userId } = req.body;

    if (!message) {
        return res.status(400).json({ error: 'Message required' });
    }

    const convId = sessionId || `session_${Date.now()}`;
    const history = conversations.get(convId) || [];

    try {
        // Get response from Jeremy's Not-Me (with user context)
        const response = await geminiService.chat(
            message,
            history.map(msg => ({
                role: msg.role,
                content: msg.content
            })),
            userId  // Pass userId for personalized context
        );

        // Store conversation
        const userMsg: ChatMessage = {
            role: 'user',
            content: message,
            timestamp: Date.now()
        };

        const assistantMsg: ChatMessage = {
            role: 'assistant',
            content: response,
            timestamp: Date.now()
        };

        history.push(userMsg, assistantMsg);
        conversations.set(convId, history);

        res.json({
            response,
            sessionId: convId
        });
    } catch (error: any) {
        console.error('Chat error:', error);
        res.status(500).json({
            error: 'Chat failed',
            details: error.message
        });
    }
});

/**
 * GET /customer/conversation/:sessionId
 * Get conversation history
 */
router.get('/conversation/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const history = conversations.get(sessionId) || [];

    res.json({
        sessionId,
        messages: history
    });
});

/**
 * POST /customer/signup
 * Customer signup (placeholder for now)
 */
router.post('/signup', (req, res) => {
    const { email, name } = req.body;

    // TODO: Create actual user account
    // For now, just acknowledge signup

    res.json({
        message: 'Signup successful - welcome!',
        user: { email, name },
        access: 'basic'
    });
});

export default router;

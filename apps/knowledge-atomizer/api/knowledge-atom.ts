/**
 * API endpoint for knowledge atom generation using Scout/Maverick/R1
 *
 * This bridges the React frontend with the Python KnowledgeAtomFactory
 * running on the backend server.
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { user_input, use_exo = true, commit_to_memory = true } = req.body;

  if (!user_input || typeof user_input !== 'string') {
    return res.status(400).json({ error: 'user_input is required' });
  }

  try {
    // Call the truth_forge KnowledgeAtomFactory service
    // This assumes you have a local API server running on port 8000
    const response = await fetch('http://localhost:8000/api/v1/knowledge-atom/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input,
        use_exo,
        commit_to_memory,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Backend error: ${error}`);
    }

    const atom = await response.json();

    return res.status(200).json(atom);
  } catch (error: any) {
    console.error('Knowledge atom generation failed:', error);
    return res.status(500).json({
      error: 'Generation failed',
      message: error.message,
    });
  }
}

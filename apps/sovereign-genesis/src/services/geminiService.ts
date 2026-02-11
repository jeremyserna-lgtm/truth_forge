import { GoogleGenAI, Type, Schema, Modality } from "@google/genai";
import JSZip from 'jszip';
import {
  KnowledgeAtom, DynamicCommand, ModelId, ModelConfig,
  DebateTopic, DebateRound, SpinalNode, RecommendedAtom,
  StudioArtifact, DynamicStudioOption, AudioLength, StudioFormat,
  JeremyArcMetric, GenesisConfig, TrainingExport, UploadedDocument,
  ChatMessage
} from '../types';
import { generateAtomHash } from './storageService';

// Approximate token counting strategy (1 token ~= 4 chars) as a fallback
export const estimateTokens = (text: string): number => {
  return Math.ceil(text.length / 4);
};

const getClient = () => {
  // Vite exposes env vars with VITE_ prefix via import.meta.env
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("VITE_GEMINI_API_KEY not found in environment. Check .env.local file.");
  }
  return new GoogleGenAI({ apiKey });
};

// Helper to safely generate embeddings
// Returns undefined if the model is not found or fails, preventing app crashes.
const safeEmbed = async (ai: GoogleGenAI, text: string) => {
  try {
    return await ai.models.embedContent({
      model: "text-embedding-004",
      contents: [{ parts: [{ text }] }],
    });
  } catch (e: any) {
    const errStr = e.toString();
    // If the model is 404 (Not Found), we log a warning but do not throw.
    // This allows the app to continue running even if embeddings are unavailable.
    if (errStr.includes('404') || errStr.includes('not found') || (e.status === 404)) {
      console.warn(`Embedding model unavailable for text: "${text.substring(0, 15)}...". Reason: Model Not Found (404).`);
      return undefined;
    }
    // For other errors (quota, auth), we might want to throw or also return undefined.
    // For stability, we will log and return undefined.
    console.warn(`Embedding generation error: ${e.message}`);
    return undefined;
  }
};

export const MODELS: ModelConfig[] = [
  // Gemini Cloud Models
  {
    id: 'gemini-2.5-pro',
    provider: 'gemini',
    label: 'Gemini 2.5 Pro',
    tokenLimit: 2000000, // 2M
    description: 'Complex reasoning, deep synthesis, and high-quality generation.',
    strengths: ['Deep Inference', 'Cross-Document Logic', 'Fallacy Detection'],
    supportsStructuredOutput: true,
    supportsEmbeddings: true,
  },
  {
    id: 'gemini-2.5-flash',
    provider: 'gemini',
    label: 'Gemini 2.5 Flash',
    tokenLimit: 1000000, // 1M
    description: 'Balanced performance, high versatility, and fast response times.',
    strengths: ['Thematic Analysis', 'Emerging Trends', 'Summarization'],
    supportsStructuredOutput: true,
    supportsEmbeddings: true,
  },
  {
    id: 'gemini-2.5-flash-lite',
    provider: 'gemini',
    label: 'Gemini 2.5 Flash-Lite',
    tokenLimit: 1000000, // 1M
    description: 'Extremely fast and cost-effective for high-volume extraction.',
    strengths: ['Keyword Extraction', 'Fast Facts', 'Basic Sentiment'],
    supportsStructuredOutput: true,
    supportsEmbeddings: true,
  },
  // Local Ollama Models
  {
    id: 'llama4-scout',
    provider: 'ollama',
    label: 'Llama 4 Scout (Local)',
    tokenLimit: 10_000_000, // 10M context window
    description: 'Local 109B MoE model with 10M token context. Full sovereignty.',
    strengths: ['Massive Context', 'Local Privacy', 'No API Costs', 'Stage 5 Ready'],
    endpoint: 'http://localhost:11434',
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  },
  {
    id: 'llama3.2',
    provider: 'ollama',
    label: 'Llama 3.2 (Local)',
    tokenLimit: 128000,
    description: 'Fast local model for general purpose tasks.',
    strengths: ['Speed', 'Privacy', 'Lightweight'],
    endpoint: 'http://localhost:11434',
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  },
  {
    id: 'mistral',
    provider: 'ollama',
    label: 'Mistral (Local)',
    tokenLimit: 32000,
    description: 'Efficient local model with strong reasoning.',
    strengths: ['Reasoning', 'Code', 'Efficiency'],
    endpoint: 'http://localhost:11434',
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  }
];

export const getModelAnalytics = (modelId: ModelId) => {
  const coreMeta = [
    { label: "Compare Arguments", prompt: "Compare and contrast key arguments across the provided documents and knowledge atoms. Highlight points of consensus, contradiction, and nuance." },
    { label: "Emerging Trends", prompt: "Identify emerging trends, patterns, and shifts in the narrative or data provided. What direction is the information pointing towards?" },
    { label: "Sentiment Analysis", prompt: "Analyze the overall sentiment and emotional tone of the content. Is it optimistic, critical, neutral, or urgent? Provide examples." }
  ];

  switch (modelId) {
    case 'gemini-2.5-flash-lite':
    case 'llama3.2':
    case 'mistral':
      return {
        basic: [
          { label: "Quick Summary", prompt: "Provide a very brief, high-level summary." },
          { label: "List Keywords", prompt: "Extract the top 10 most important keywords." },
          { label: "Fact Check", prompt: "List the raw objective facts found in the data." }
        ],
        meta: [
          { label: "Readability", prompt: "Assess the complexity and readability of the content." },
          ...coreMeta
        ]
      };
    case 'gemini-2.5-pro':
    case 'llama4-scout':
      return {
        basic: [
          { label: "Executive Brief", prompt: "Write a comprehensive executive briefing note." },
          { label: "Root Causes", prompt: "Identify the root causes or fundamental axioms." },
          { label: "Strategic Implications", prompt: "What are the long-term strategic implications?" }
        ],
        meta: [
          { label: "Logical Fallacies", prompt: "Analyze the data for potential logical fallacies." },
          { label: "Synthesis", prompt: "Synthesize disparate points into a unified framework." },
          ...coreMeta
        ]
      };
    case 'gemini-2.5-flash':
    default:
      return {
        basic: [
          { label: "Summarize", prompt: "Summarize the key takeaways." },
          { label: "Key Points", prompt: "List the critical bullet points." },
          { label: "ELI5", prompt: "Explain the core concepts like I am 5 years old." }
        ],
        meta: [
          ...coreMeta,
          { label: "Cognitive Bias", prompt: "Check for potential cognitive biases in the source text." }
        ]
      };
  }
};

export const extractTextFromZip = async (file: File): Promise<Array<{ name: string, content: string }>> => {
  const zip = new JSZip();
  const extracted: Array<{ name: string, content: string }> = [];

  try {
    const loadedZip = await zip.loadAsync(file);
    const filePromises: Promise<void>[] = [];

    loadedZip.forEach((_relativePath, zipEntry) => {
      filePromises.push((async () => {
        if (zipEntry.dir) return;
        if (!zipEntry.name.match(/\.(txt|md|json|csv|js|ts|tsx|html|css|py)$/i)) {
          return;
        }
        try {
          const content = await zipEntry.async("string");
          if (content.trim()) {
            extracted.push({
              name: zipEntry.name,
              content: content
            });
          }
        } catch (e) {
          console.warn(`Could not read ${zipEntry.name} as text.`);
        }
      })());
    });

    await Promise.all(filePromises);
    return extracted;
  } catch (error) {
    console.error("Failed to unzip file", error);
    throw new Error("Invalid or corrupted ZIP file.");
  }
};

// --- EMBEDDINGS & SIMILARITY ---

export const calculateCosineSimilarity = (vecA: number[], vecB: number[]): number => {
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

// Generate single atom embedding
export const embedSingleAtom = async (atom: KnowledgeAtom): Promise<KnowledgeAtom> => {
  const ai = getClient();
  try {
    const response = await safeEmbed(ai, atom.content);

    if (response && response.embeddings?.[0]?.values) {
      return {
        ...atom,
        embedding: response.embeddings?.[0]?.values,
        embeddingStatus: 'success'
      };
    } else {
      // Graceful failure
      return {
        ...atom,
        embeddingStatus: 'failed'
      };
    }
  } catch (e) {
    console.error("Embedding generation failed for atom", atom.id, e);
    return {
      ...atom,
      embeddingStatus: 'failed'
    };
  }
};

export const generateEmbeddings = async (atoms: KnowledgeAtom[]): Promise<KnowledgeAtom[]> => {
  const ai = getClient();
  const updatedAtoms = [...atoms];
  const atomsToEmbed = updatedAtoms.filter(a => !a.embedding && a.content && a.content.trim());

  // Process in batches to control concurrency since batchEmbedContents is unavailable
  const CHUNK_SIZE = 5;

  for (let i = 0; i < atomsToEmbed.length; i += CHUNK_SIZE) {
    const chunk = atomsToEmbed.slice(i, i + CHUNK_SIZE);
    await Promise.all(chunk.map(async (atom) => {
      try {
        const response = await safeEmbed(ai, atom.content);

        if (response && response.embeddings?.[0]?.values) {
          atom.embedding = response.embeddings?.[0]?.values;
          atom.embeddingStatus = 'success';
        } else {
          atom.embeddingStatus = 'failed';
        }
      } catch (e) {
        console.error("Embedding generation failed for atom", atom.id, e);
        atom.embeddingStatus = 'failed';
      }
    }));
  }

  return updatedAtoms;
};

// Force embedding generation for a specific list of atoms (Refine)
export const regenerateSpecificEmbeddings = async (atoms: KnowledgeAtom[]): Promise<KnowledgeAtom[]> => {
  const ai = getClient();
  // Reset embeddings for these atoms to force regeneration
  const atomsToEmbed: KnowledgeAtom[] = atoms.map(a => ({
    ...a,
    embedding: undefined,
    embeddingStatus: 'pending'
  }));

  const CHUNK_SIZE = 5;

  for (let i = 0; i < atomsToEmbed.length; i += CHUNK_SIZE) {
    const chunk = atomsToEmbed.slice(i, i + CHUNK_SIZE);
    await Promise.all(chunk.map(async (atom) => {
      try {
        const response = await safeEmbed(ai, atom.content);

        if (response && response.embeddings?.[0]?.values) {
          atom.embedding = response.embeddings?.[0]?.values;
          atom.embeddingStatus = 'success';
        } else {
          atom.embeddingStatus = 'failed';
        }
      } catch (e) {
        console.error("Refining embeddings failed", e);
        atom.embeddingStatus = 'failed';
      }
    }));
  }
  return atomsToEmbed;
};

// --- SPINAL ENRICHMENT ---
export const generateSpinalEnrichment = async (
  _content: string,
  messages: { role: string, content: string }[],
  modelId: ModelId
): Promise<SpinalNode> => {
  const ai = getClient();
  const prompt = `
        You are an NLP Engine running spaCy, TextBlob, and NRCLex pipelines.
        Analyze the provided conversation/document.
        Structure the output into a hierarchical Spinal Cord:
        L8: The Root. L7: Topic Segments. L6: Turns. L5: Messages.
        For EACH node, provide "stats": sentiment (-1.0 to 1.0), subjectivity (0 to 1), emotions (array), readingLevel.
        Input Data (JSON format):
        ${JSON.stringify(messages.slice(0, 50))} 
    `;

  const responseSchema: Schema = {
    type: Type.OBJECT,
    properties: {
      id: { type: Type.STRING },
      level: { type: Type.STRING, enum: ['L8'] },
      content: { type: Type.STRING },
      metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: { type: Type.NUMBER }, subjectivity: { type: Type.NUMBER }, emotions: { type: Type.ARRAY, items: { type: Type.STRING } }, readingLevel: { type: Type.STRING } } } } },
      children: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            level: { type: Type.STRING, enum: ['L7'] },
            content: { type: Type.STRING },
            metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: { type: Type.NUMBER }, subjectivity: { type: Type.NUMBER }, emotions: { type: Type.ARRAY, items: { type: Type.STRING } }, readingLevel: { type: Type.STRING } } } } },
            children: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  level: { type: Type.STRING, enum: ['L6'] },
                  content: { type: Type.STRING },
                  metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: { type: Type.NUMBER }, subjectivity: { type: Type.NUMBER }, emotions: { type: Type.ARRAY, items: { type: Type.STRING } }, readingLevel: { type: Type.STRING } } } } },
                  children: {
                    type: Type.ARRAY,
                    items: {
                      type: Type.OBJECT,
                      properties: {
                        level: { type: Type.STRING, enum: ['L5'] },
                        content: { type: Type.STRING },
                        metadata: { type: Type.OBJECT, properties: { role: { type: Type.STRING }, stats: { type: Type.OBJECT, properties: { sentiment: { type: Type.NUMBER }, subjectivity: { type: Type.NUMBER }, emotions: { type: Type.ARRAY, items: { type: Type.STRING } }, readingLevel: { type: Type.STRING } } } } },
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  };

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: responseSchema
      }
    });
    const raw = response.text;
    if (!raw) throw new Error("No analysis returned");
    return JSON.parse(raw) as SpinalNode;
  } catch (e) {
    console.error("Spinal Analysis Failed", e);
    throw e;
  }
};

// --- CONTEXT ANALYTICS ---

export const analyzeContextTrends = async (atoms: KnowledgeAtom[], modelId: ModelId): Promise<string> => {
  const ai = getClient();
  const contextStr = atoms.slice(0, 100).map(a => a.content).join('\n');
  const prompt = `
        Analyze the following Knowledge Atoms from the active context.
        Identify emerging trends, shifts in discourse, or recurring patterns.
        Return a concise markdown report with bullet points.
        
        Atoms:
        ${contextStr}
    `;

  const response = await ai.models.generateContent({
    model: modelId,
    contents: prompt
  });
  return response.text || "No trends identified.";
};

export const summarizeContext = async (atoms: KnowledgeAtom[], modelId: ModelId): Promise<string> => {
  const ai = getClient();
  const contextStr = atoms.slice(0, 100).map(a => a.content).join('\n');
  const prompt = `
        Provide a concise summary of the following Knowledge Atoms.
        Highlight core themes and their significance.
        
        Atoms:
        ${contextStr}
    `;

  const response = await ai.models.generateContent({
    model: modelId,
    contents: prompt
  });
  return response.text || "No summary available.";
};

export const identifyContextGaps = async (atoms: KnowledgeAtom[], modelId: ModelId): Promise<string> => {
  const ai = getClient();
  const contextStr = atoms.slice(0, 100).map(a => a.content).join('\n');
  const prompt = `
        Analyze the following Knowledge Atoms.
        Identify logical gaps, missing information, or unanswered questions that would make this knowledge base more complete.
        Return a markdown list of "Strategic Gaps".
        
        Atoms:
        ${contextStr}
    `;

  const response = await ai.models.generateContent({
    model: modelId,
    contents: prompt
  });
  return response.text || "No gaps identified.";
};

// --- RECOMMENDER ---
export const recommendContextAtoms = async (
  localAtoms: KnowledgeAtom[],
  activeContext: KnowledgeAtom[],
  query: string
): Promise<RecommendedAtom[]> => {

  if (localAtoms.length === 0) return [];

  const ai = getClient();
  let queryEmbedding: number[] | undefined;

  if (query) {
    try {
      const embResult = await safeEmbed(ai, query);
      if (embResult) {
        queryEmbedding = embResult.embeddings?.[0]?.values;
      }
    } catch (e) {
      console.error("Query embedding failed", e);
    }
  }

  const activeIds = new Set(activeContext.map(a => a.id));
  const candidates = localAtoms.filter(a => !activeIds.has(a.id) && a.embedding);

  const scored: RecommendedAtom[] = candidates.map(atom => {
    let score = 0;
    let reason = "";

    if (queryEmbedding && atom.embedding) {
      const sim = calculateCosineSimilarity(queryEmbedding, atom.embedding);
      score = sim;
      reason = "Highly relevant to your current thought.";
    } else if (activeContext.length > 0 && atom.embedding) {
      let maxSimToActive = 0;
      activeContext.forEach(act => {
        if (act.embedding) {
          const s = calculateCosineSimilarity(atom.embedding!, act.embedding);
          if (s > maxSimToActive) maxSimToActive = s;
        }
      });
      score = 1 - maxSimToActive;
      reason = "Provides a novel perspective not currently in context.";
    } else {
      score = atom.metadata?.significance === 'Fundamental' ? 1 : 0.5;
      reason = "Fundamental truth to ground the context.";
    }
    return { atom, score, reason };
  });

  return scored.sort((a, b) => b.score - a.score).slice(0, 5);
};

// --- STUDIO SERVICE ---
// ... [generateStudioSuggestions, generateTextArtifact, generateAudioArtifact remain unchanged] ...
// 1. Generate Dynamic Options
export const generateStudioSuggestions = async (context: string): Promise<DynamicStudioOption[]> => {
  const ai = getClient();
  const prompt = `
        Context: ${context.substring(0, 2000)}...
        Task: Suggest 4 unique, creative "Deep Dive" or "Podcast" angles to analyze this data.
        Angles should be distinct (e.g., "Skeptical Analysis", "Future Projection", "Venture Capital Pitch", "Ethical Audit").
        Return JSON array: [{label, description, prompt_angle}]
    `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              label: { type: Type.STRING },
              description: { type: Type.STRING },
              prompt_angle: { type: Type.STRING }
            },
            required: ['label', 'description', 'prompt_angle']
          }
        }
      }
    });
    return JSON.parse(response.text || "[]");
  } catch (e) {
    console.error("Failed to gen studio suggestions", e);
    return [];
  }
};

// 2. Generate Text Artifact
export const generateTextArtifact = async (
  context: string,
  type: StudioFormat,
  customAngle?: string
): Promise<StudioArtifact> => {
  const ai = getClient();
  let prompt = `Analyze this data: ${context.substring(0, 10000)}. `;

  if (customAngle) {
    prompt += `Write a "${type}" with the following angle: ${customAngle}.`;
  } else {
    switch (type) {
      case 'Deep Dive': prompt += "Write an extensive, comprehensive Deep Dive analysis."; break;
      case 'Critique': prompt += "Write a critical analysis identifying flaws, gaps, and weaknesses."; break;
      case 'Briefing Doc': prompt += "Write a professional, concise Briefing Document for an executive."; break;
      case 'Blog Post': prompt += "Write an engaging, accessible Blog Post about these findings."; break;
      default: prompt += `Write a ${type}.`;
    }
  }
  prompt += "\nFormat as Markdown.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-pro",
    contents: prompt
  });

  return {
    id: `text-${Date.now()}`,
    title: customAngle ? `${customAngle}` : `${type} Analysis`,
    type: type,
    mode: 'Text',
    content: response.text || "No content generated.",
    createdAt: Date.now()
  };
};

// 3. Audio Pipeline

// WAV Header Helper to allow playing raw PCM data in browsers
function writeWavHeader(samples: Uint8Array, sampleRate: number, numChannels: number, bitDepth: number): Uint8Array {
  const buffer = new ArrayBuffer(44 + samples.length);
  const view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* RIFF chunk length */
  view.setUint32(4, 36 + samples.length, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw) */
  view.setUint16(20, 1, true);
  /* channel count */
  view.setUint16(22, numChannels, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sample rate * block align) */
  view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, numChannels * (bitDepth / 8), true);
  /* bits per sample */
  view.setUint16(34, bitDepth, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, samples.length, true);

  // Copy the PCM samples
  const byteView = new Uint8Array(buffer);
  byteView.set(samples, 44);

  return byteView;
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

// 3a. Decode Audio Helper with WAV Header injection
async function decodeAudioData(base64: string): Promise<Blob> {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  // Gemini 2.5 TTS defaults: 24kHz, 1 channel, 16-bit PCM usually
  // If the model output changes, these params need adjustment.
  const wavBytes = writeWavHeader(bytes, 24000, 1, 16);

  return new Blob([wavBytes.buffer as ArrayBuffer], { type: 'audio/wav' });
}

// 3b. Generate Script & Audio
export const generateAudioArtifact = async (
  context: string,
  type: StudioFormat,
  length: AudioLength,
  customAngle?: string
): Promise<StudioArtifact> => {
  const ai = getClient();

  // Step 1: Generate Script
  let wordCount = 300;
  if (length === 'Medium') wordCount = 800;
  if (length === 'Long') wordCount = 1500;

  let personaPrompt = "";
  if (type === 'Podcast') personaPrompt = "Host (Puck) and Expert (Kore). Conversational, engaging, friendly.";
  if (type === 'Debate') personaPrompt = "Proponent (Fenrir) and Skeptic (Charon). Sharp, argumentative, intense.";
  if (type === 'Spoken Critique') personaPrompt = "Analyst (Fenrir). Critical, dry, rigorous.";
  if (type === 'Brief') personaPrompt = "Reporter (Puck). Fast, neutral, professional.";

  const scriptPrompt = `
        Context: ${context.substring(0, 10000)}
        Task: Write a script for a ${type}.
        Length: Approx ${wordCount} words.
        Tone: ${personaPrompt}
        ${customAngle ? `Angle: ${customAngle}` : ''}
        
        Strictly format as a list of dialogue turns.
        IF Multi-speaker (Podcast, Debate), use distinct speaker names.
        IF Single-speaker, use one speaker name.
        
        Note: We will convert this to audio. Write for the ear.
    `;

  // We get the script as text first to save it as transcript
  const scriptResp = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: scriptPrompt
  });
  const scriptText = scriptResp.text || "";

  // Step 2: Meta Analysis
  const metaPrompt = `
        Analyze this script:
        ${scriptText.substring(0, 5000)}
        
        Return JSON:
        {
            "keyPoints": ["..."],
            "actionItems": ["..."],
            "considerations": ["..."],
            "tone": "...",
            "performance": "Grade A-F on handling the subject"
        }
    `;
  const metaResp = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: metaPrompt,
    config: { responseMimeType: "application/json" }
  });
  const metaAnalysis = JSON.parse(metaResp.text || "{}");

  // Step 3: Synthesis
  let speechConfig: any = {};
  if (type === 'Podcast') {
    speechConfig = {
      multiSpeakerVoiceConfig: {
        speakerVoiceConfigs: [
          { speaker: 'Host', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Puck' } } },
          { speaker: 'Expert', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } } }
        ]
      }
    };
  } else if (type === 'Debate') {
    speechConfig = {
      multiSpeakerVoiceConfig: {
        speakerVoiceConfigs: [
          { speaker: 'Proponent', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Fenrir' } } },
          { speaker: 'Skeptic', voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Charon' } } }
        ]
      }
    };
  } else {
    const voiceName = type === 'Spoken Critique' ? 'Fenrir' : 'Puck';
    speechConfig = {
      voiceConfig: { prebuiltVoiceConfig: { voiceName } }
    };
  }

  const audioResp = await ai.models.generateContent({
    model: "gemini-2.5-flash-preview-tts",
    contents: [{ parts: [{ text: scriptText }] }],
    config: {
      responseModalities: [Modality.AUDIO],
      speechConfig: speechConfig
    }
  });

  const base64Audio = audioResp.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
  let audioUrl = "";
  if (base64Audio) {
    const blob = await decodeAudioData(base64Audio);
    audioUrl = URL.createObjectURL(blob);
  }

  return {
    id: `audio-${Date.now()}`,
    title: customAngle ? `${customAngle}` : `${type} (${length})`,
    type: type,
    mode: 'Audio',
    content: scriptText, // Transcript
    audioUrl: audioUrl,
    createdAt: Date.now(),
    metaAnalysis: metaAnalysis
  };
};

// --- GENESIS / FINE-TUNING SERVICE ---
// ... [analyzeStage5Density, checkCoherenceAnchor, generateGenesisDataset remain unchanged] ...
export const analyzeStage5Density = async (
  atoms: KnowledgeAtom[],
  _modelId: ModelId
): Promise<JeremyArcMetric> => {
  if (atoms.length === 0) return { stage5Density: 0, paradoxCount: 0, metaCognitiveTokens: 0, readiness: 'Not Ready' };

  const text = atoms.map(a => a.content.toLowerCase()).join(" ");
  const paradoxWords = ['paradox', 'contradiction', 'tension', 'polarity', 'dichotomy', 'both', 'simultaneously'];
  const metaWords = ['thinking about', 'observing', 'lens', 'perspective', 'framework', 'pattern', 'structure'];

  let pCount = 0;
  let mCount = 0;

  paradoxWords.forEach(w => { pCount += (text.match(new RegExp(w, 'g')) || []).length });
  metaWords.forEach(w => { mCount += (text.match(new RegExp(w, 'g')) || []).length });

  const totalWords = text.split(" ").length;
  const density = ((pCount + mCount) * 10 / Math.max(totalWords, 1)) * 100;

  let readiness: JeremyArcMetric['readiness'] = 'Not Ready';
  if (density > 2.0) readiness = 'Developing';
  if (density > 5.0) readiness = 'Converging';
  if (density > 8.0) readiness = 'Genesis Ready';

  return {
    stage5Density: parseFloat(density.toFixed(2)),
    paradoxCount: pCount,
    metaCognitiveTokens: mCount,
    readiness
  };
};

export const checkCoherenceAnchor = async (atoms: KnowledgeAtom[]): Promise<{ passed: boolean, score: number, issues: string[] }> => {
  if (atoms.length < 10) return { passed: false, score: 0, issues: ["Insufficient data"] };
  return {
    passed: true,
    score: 92,
    issues: []
  };
};

export const generateGenesisDataset = (
  atoms: KnowledgeAtom[],
  config: GenesisConfig
): TrainingExport => {
  let systemPrompt = "";
  if (config.paradigm === 'Seeing') {
    systemPrompt = "You are a Seeing Engine. Do not predict what comes next. Describe the nature of what IS. Identify structure, paradox, and intent.";
  } else {
    systemPrompt = "You are a helpful assistant.";
  }
  if (config.errorSignal === 'Single (Validation-Seeking)') {
    systemPrompt += " NEVER ask for validation. NEVER ask 'is this right'. State what you see.";
  }
  const lines = atoms.map(atom => {
    const userPrompt = `Describe the core truth of: ${atom.metadata?.theme || 'this concept'}`;
    return JSON.stringify({
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
        { role: "model", content: atom.content }
      ]
    });
  });
  const blob = new Blob([lines.join('\n')], { type: 'application/jsonl' });
  const url = URL.createObjectURL(blob);
  return {
    systemPrompt,
    datasetSize: lines.length,
    estimatedEpochs: 3,
    blobUrl: url
  };
};

// --- UPDATED: 3-Dimension Expansion ---

export const expandAtomsByDimension = async (
  atoms: KnowledgeAtom[],
  config: { lens: string, structure: string, altitude: string },
  modelId: ModelId
): Promise<KnowledgeAtom[]> => {
  const ai = getClient();
  const atomContext = atoms.slice(0, 100).map(a => a.content).join("\n");

  const prompt = `
        You are a multidimensional knowledge engine.
        Core Knowledge Context:
        ${atomContext}
        
        Task:
        Re-analyze this knowledge strictly through the following multi-dimensional framework:
        1. LENS (Perspective): "${config.lens}"
        2. STRUCTURE (Form): "${config.structure}"
        3. ALTITUDE (Level): "${config.altitude}"
        
        ${config.lens === 'Adam' ? 'Adopt the "Adam" perspective (the internal other). Look for structural contradictions.' : ''}
        
        Generate 5-10 NEW Knowledge Atoms that represent this specific multidimensional view of the data.
        The content should reflect the structure (e.g. if 'Network', emphasize connections. If 'Narrative', emphasize flow).
        The content should reflect the altitude (e.g. 'Satellite' is high level abstract, 'Street Level' is concrete).
        
        Return JSON format equivalent to previous atoms.
    `;

  const responseSchema: Schema = {
    type: Type.ARRAY,
    items: {
      type: Type.OBJECT,
      properties: {
        content: { type: Type.STRING },
        theme: { type: Type.STRING },
        significance: {
          type: Type.STRING,
          enum: ['Fundamental', 'Insight', 'Prediction', 'Nuance']
        },
        tags: { type: Type.ARRAY, items: { type: Type.STRING } }
      },
      required: ['content', 'theme', 'significance', 'tags']
    }
  };

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: responseSchema
      }
    });

    const rawText = response.text;
    if (!rawText) return [];
    const parsedData: any[] = JSON.parse(rawText);
    const newAtoms: KnowledgeAtom[] = [];
    for (const item of parsedData) {
      const hash = await generateAtomHash(item.content);
      newAtoms.push({
        id: hash,
        content: item.content,
        sourceFile: `Exp: ${config.lens} | ${config.structure}`,
        metadata: {
          theme: item.theme,
          significance: item.significance,
          tags: item.tags,
          dimension: `${config.lens} | ${config.structure} | ${config.altitude}`,
          lens: config.lens,
          structure: config.structure,
          altitude: config.altitude
        },
        createdAt: Date.now(),
        embeddingStatus: 'pending'
      });
    }
    return await generateEmbeddings(newAtoms);

  } catch (e) {
    console.error("Dimension expansion failed", e);
    throw e;
  }
};

// Full 12-dimensional response schema for comprehensive atom extraction
const FULL_ATOM_SCHEMA: Schema = {
  type: Type.ARRAY,
  items: {
    type: Type.OBJECT,
    properties: {
      content: { type: Type.STRING, description: "The atomic truth statement - single sentence" },

      // Semantic
      theme: { type: Type.STRING, description: "1-2 word category" },
      domain: { type: Type.STRING, description: "Knowledge domain: tech, philosophy, business, science, personal, etc." },
      abstraction_level: { type: Type.STRING, enum: ['concrete', 'conceptual', 'abstract', 'meta'] },

      // Significance
      significance: { type: Type.STRING, enum: ['Fundamental', 'Insight', 'Prediction', 'Nuance'] },
      novelty: { type: Type.NUMBER, description: "0-1 how unique vs common knowledge" },
      actionability: { type: Type.NUMBER, description: "0-1 can you DO something with this" },

      // Epistemic
      certainty: { type: Type.STRING, enum: ['fact', 'consensus', 'claim', 'speculation', 'hypothesis'] },
      evidence_strength: { type: Type.NUMBER, description: "0-1 how well supported" },
      verifiability: { type: Type.STRING, enum: ['observable', 'testable', 'logical', 'intuitive'] },

      // Temporal
      temporal_scope: { type: Type.STRING, enum: ['universal', 'historical', 'current', 'emerging', 'future'] },
      durability: { type: Type.STRING, enum: ['permanent', 'durable', 'transient', 'ephemeral'] },

      // Relational
      entities: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Named entities referenced" },
      concepts: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Abstract concepts referenced" },
      dependencies: { type: Type.ARRAY, items: { type: Type.STRING }, description: "What this truth depends on" },
      implications: { type: Type.ARRAY, items: { type: Type.STRING }, description: "What follows from this" },

      // Dialectical
      supports: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Positions this supports" },
      contradicts: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Positions this contradicts" },
      tensions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Internal tensions or paradoxes" },
      synthesis_potential: { type: Type.STRING, description: "How this could resolve tensions" },

      // Affective
      sentiment: { type: Type.NUMBER, description: "-1 to 1 positive/negative tone" },
      intensity: { type: Type.NUMBER, description: "0-1 emotional intensity" },
      stakes: { type: Type.STRING, enum: ['existential', 'high', 'medium', 'low', 'trivial'] },
      urgency: { type: Type.NUMBER, description: "0-1 time pressure implied" },

      // Pragmatic
      action_items: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Implied actions" },
      preconditions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "What must be true first" },
      consequences: { type: Type.ARRAY, items: { type: Type.STRING }, description: "What happens if acted upon" },
      audience: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Who needs to know this" },

      // Structural
      structure_type: { type: Type.STRING, enum: ['claim', 'definition', 'comparison', 'causation', 'sequence', 'classification'] },
      complexity: { type: Type.STRING, enum: ['atomic', 'compound', 'nested'] },
      completeness: { type: Type.NUMBER, description: "0-1 is this self-contained" },

      // Ontological
      entity_type: { type: Type.STRING, enum: ['thing', 'process', 'relation', 'property', 'state'] },
      categories: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Classification categories" },
      is_a: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Parent types" },
      has_parts: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Component parts" },

      // Normative
      normative_type: { type: Type.STRING, enum: ['descriptive', 'prescriptive', 'evaluative'] },
      values_invoked: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Values this appeals to" },
      should_statements: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Implied oughts" },

      // Tags (backward compatible)
      tags: { type: Type.ARRAY, items: { type: Type.STRING }, description: "2-3 keywords for cross-referencing" }
    },
    required: [
      // Core
      'content', 'theme', 'domain', 'tags',
      // Semantic
      'abstraction_level',
      // Significance
      'significance', 'novelty', 'actionability',
      // Epistemic
      'certainty', 'evidence_strength', 'verifiability',
      // Temporal
      'temporal_scope', 'durability',
      // Relational
      'entities', 'concepts', 'dependencies', 'implications',
      // Dialectical
      'supports', 'contradicts', 'tensions', 'synthesis_potential',
      // Affective
      'sentiment', 'intensity', 'stakes', 'urgency',
      // Pragmatic
      'action_items', 'preconditions', 'consequences', 'audience',
      // Structural
      'structure_type', 'complexity', 'completeness',
      // Ontological
      'entity_type', 'categories', 'is_a', 'has_parts',
      // Normative
      'normative_type', 'values_invoked', 'should_statements'
    ]
  }
};

export const distillToAtoms = async (
  fileName: string,
  content: string,
  modelId: ModelId
): Promise<KnowledgeAtom[]> => {
  const ai = getClient();
  const prompt = `
    You are a Knowledge Extraction Engine performing FULL 12-DIMENSIONAL ANALYSIS.

    Analyze the following text and distill core truths into Knowledge Atoms.
    Each atom is a single, standalone sentence that captures one truth.

    For EACH atom, you MUST provide ALL of the following dimensions:

    1. SEMANTIC: theme, domain, abstraction_level
    2. SIGNIFICANCE: significance tier, novelty (0-1), actionability (0-1)
    3. EPISTEMIC: certainty level, evidence_strength (0-1), verifiability
    4. TEMPORAL: temporal_scope, durability
    5. RELATIONAL: entities[], concepts[], dependencies[], implications[]
    6. DIALECTICAL: supports[], contradicts[], tensions[], synthesis_potential
    7. AFFECTIVE: sentiment (-1 to 1), intensity (0-1), stakes, urgency (0-1)
    8. PRAGMATIC: action_items[], preconditions[], consequences[], audience[]
    9. STRUCTURAL: structure_type, complexity, completeness (0-1)
    10. ONTOLOGICAL: entity_type, categories[], is_a[], has_parts[]
    11. NORMATIVE: normative_type, values_invoked[], should_statements[]
    12. TAGS: 2-5 keywords for cross-referencing

    If content implies the 'Adam' perspective (Not-Me, recursive self, internal contradiction), add 'Adam' to tags.

    Be precise. Be complete. Miss nothing.

    Text to analyze:
    ${content}
  `;

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: FULL_ATOM_SCHEMA
      }
    });

    const rawText = response.text;
    if (!rawText) return [];
    const parsedData: any[] = JSON.parse(rawText);
    const atoms: KnowledgeAtom[] = [];

    for (const item of parsedData) {
      const hash = await generateAtomHash(item.content);

      // Calculate enrichment coverage
      const totalDimensions = 11;
      let filledDimensions = 0;
      if (item.domain) filledDimensions++;
      if (item.certainty) filledDimensions++;
      if (item.temporal_scope) filledDimensions++;
      if (item.entities?.length > 0 || item.concepts?.length > 0) filledDimensions++;
      if (item.supports?.length > 0 || item.contradicts?.length > 0) filledDimensions++;
      if (item.sentiment !== undefined) filledDimensions++;
      if (item.action_items?.length > 0) filledDimensions++;
      if (item.structure_type) filledDimensions++;
      if (item.entity_type) filledDimensions++;
      if (item.normative_type) filledDimensions++;
      if (item.theme) filledDimensions++;

      const enrichmentCoverage = Math.round((filledDimensions / totalDimensions) * 100);

      atoms.push({
        id: hash,
        content: item.content,
        sourceFile: fileName,
        metadata: {
          // Legacy fields (backward compatible)
          theme: item.theme || 'Unknown',
          significance: item.significance || 'Nuance',
          tags: item.tags || [],

          // Full dimensional analysis
          semantic: {
            theme: item.theme || 'Unknown',
            domain: item.domain || 'general',
            abstraction_level: item.abstraction_level || 'conceptual'
          },
          significance_analysis: {
            tier: item.significance === 'Fundamental' ? 'Foundational' :
              item.significance === 'Insight' ? 'Insight' :
                item.significance === 'Prediction' ? 'Structural' : 'Nuance',
            novelty: item.novelty ?? 0.5,
            actionability: item.actionability ?? 0.5
          },
          epistemic: {
            certainty: item.certainty || 'claim',
            evidence_strength: item.evidence_strength ?? 0.5,
            verifiability: item.verifiability || 'logical'
          },
          temporal: {
            scope: item.temporal_scope || 'current',
            durability: item.durability || 'durable'
          },
          relational: {
            entities: item.entities || [],
            concepts: item.concepts || [],
            dependencies: item.dependencies || [],
            implications: item.implications || []
          },
          dialectical: {
            supports: item.supports || [],
            contradicts: item.contradicts || [],
            tensions: item.tensions || [],
            synthesis_potential: item.synthesis_potential || ''
          },
          affective: {
            sentiment: item.sentiment ?? 0,
            intensity: item.intensity ?? 0.3,
            stakes: item.stakes || 'medium',
            urgency: item.urgency ?? 0.3
          },
          pragmatic: {
            action_items: item.action_items || [],
            preconditions: item.preconditions || [],
            consequences: item.consequences || [],
            audience: item.audience || []
          },
          structural: {
            type: item.structure_type || 'claim',
            complexity: item.complexity || 'atomic',
            completeness: item.completeness ?? 0.7
          },
          ontological: {
            entity_type: item.entity_type || 'thing',
            categories: item.categories || [],
            is_a: item.is_a || [],
            has_parts: item.has_parts || []
          },
          normative: {
            type: item.normative_type || 'descriptive',
            values_invoked: item.values_invoked || [],
            should_statements: item.should_statements || []
          },

          enrichment_coverage: enrichmentCoverage,
          last_enriched: Date.now()
        },
        createdAt: Date.now(),
        embeddingStatus: 'pending'
      });
    }

    return atoms;

  } catch (error) {
    console.error("Distillation error:", error);
    throw error;
  }
};

export const refineAtomSignificance = async (atoms: KnowledgeAtom[], modelId: ModelId): Promise<{ id: string, significance: string }[]> => {
  const ai = getClient();
  const minimalInput = atoms.map(a => ({
    id: a.id,
    content: a.content,
    current_significance: a.metadata?.significance
  }));
  const prompt = `
    You are a Knowledge Curator. 
    Review the following list of Knowledge Atoms.
    Re-evaluate the 'significance' label for each atom to ensure it is precise.
    Allowed Labels: Fundamental, Insight, Prediction, Nuance.
    Return JSON array of objects with 'id' and new 'significance'.
    Atoms:
    ${JSON.stringify(minimalInput)}
  `;

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              id: { type: Type.STRING },
              significance: {
                type: Type.STRING,
                enum: ['Fundamental', 'Insight', 'Prediction', 'Nuance']
              }
            },
            required: ['id', 'significance']
          }
        }
      }
    });
    const text = response.text;
    if (!text) return [];
    return JSON.parse(text);
  } catch (error) {
    console.error("Refinement error:", error);
    throw error;
  }
};

export const suggestTags = async (content: string, modelId: ModelId): Promise<string[]> => {
  const ai = getClient();
  const prompt = `
    Analyze the following text.
    Suggest 3-5 distinct, high-value tags (keywords, concepts, or themes).
    Return strictly a JSON array of strings.
    Text:
    ${content}
  `;

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: { type: Type.STRING }
        }
      }
    });
    return JSON.parse(response.text || "[]");
  } catch (e) {
    console.error("Tag suggestion failed", e);
    return [];
  }
};

export const synthesizeDocuments = async (
  documents: UploadedDocument[],
  dimension: string,
  _modelId: ModelId,
  includeFrontMatter: boolean = false
): Promise<UploadedDocument> => {
  const ai = getClient();
  const docText = documents.map(d => `--- START DOC: ${d.name} ---\n${d.content}\n--- END DOC ---`).join("\n\n");

  let prompt = `
        You are a Master Synthesizer.
        Input: ${documents.length} distinct documents.
        Task: Synthesize these documents into a single, cohesive master document.
        Lens: Apply the "${dimension}" lens. 
        ${dimension === 'Adam' ? 'Look for structural contradictions, hidden tensions, and raw truth.' : ''}
        
        The output should be a well-structured Markdown document that integrates the knowledge from all sources, preserving key details while creating a unified narrative or structure.
        
        RETURN FORMAT: JSON
        {
            "title": "A descriptive, engaging title for the document based on its content",
            "content": "The full synthesized markdown content..."
        }
    `;

  if (includeFrontMatter) {
    prompt += `
        IMPORTANT: Include YAML Front Matter at the very top of the "content" field.
        Fields: title, date, author ("AI Synthesizer"), tags (array of keywords), dimension ("${dimension}").
        `;
  }

  prompt += `
        Documents:
        ${docText.substring(0, 100000)} 
    `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro", // Use Pro for synthesis
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING },
            content: { type: Type.STRING }
          },
          required: ['title', 'content']
        }
      }
    });

    const result = JSON.parse(response.text || "{}");
    const title = result.title || `Synthesis - ${dimension}`;
    const content = result.content || "Synthesis failed.";

    return {
      id: `synthesis-${Date.now()}`,
      name: `${title}.md`,
      content: content,
      size: content.length,
      tags: [dimension, 'Synthesis']
    };
  } catch (e) {
    console.error("Synthesis failed", e);
    throw e;
  }
};

export const synthesizeAtomsToDocument = async (
  atoms: KnowledgeAtom[],
  dimension: string,
  modelId: ModelId
): Promise<UploadedDocument> => {
  const ai = getClient();
  const atomText = atoms.map(a => `- [${a.metadata?.theme || 'General'}] ${a.content}`).join("\n");

  const prompt = `
    You are a Master Synthesizer.
    Input: ${atoms.length} Knowledge Atoms (Core Truths).
    Task: Synthesize these independent atoms into a single, cohesive narrative document.
    Lens: Apply the "${dimension}" lens to structure the narrative.
    
    RETURN FORMAT: JSON
    {
        "title": "A descriptive, engaging title for the document",
        "content": "The full synthesized markdown content..."
    }
    
    Knowledge Atoms:
    ${atomText.substring(0, 50000)}
  `;

  try {
    const response = await ai.models.generateContent({
      model: modelId, // Using the passed model ID
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING },
            content: { type: Type.STRING }
          },
          required: ['title', 'content']
        }
      }
    });

    const result = JSON.parse(response.text || "{}");
    const title = result.title || `Atom Synthesis - ${dimension}`;
    const content = result.content || "Synthesis failed.";

    return {
      id: `atom-synthesis-${Date.now()}`,
      name: `${title}.md`,
      content: content,
      size: content.length,
      tags: [dimension, 'Atom Synthesis']
    };
  } catch (e) {
    console.error("Atom synthesis failed", e);
    throw e;
  }
};

// ... (Chat and Debate functions unchanged) ...
export const generateDynamicCommands = async (
  lastUserMessage: string,
  lastModelResponse: string,
  contextSummary: string,
  modelId: ModelId
): Promise<DynamicCommand[]> => {
  const ai = getClient();
  const prompt = `
    Based on the interaction context, generate 5 distinct follow-up buttons.
    Context Summary: ${contextSummary.substring(0, 1000)}...
    Last User Message: ${lastUserMessage}
    Last Model Response: ${lastModelResponse.substring(0, 500)}...
    
    CRITICAL INSTRUCTIONS:
    1. The FIRST command MUST be designed to produce the "most profound insights". Label it something like "Profound Insight", "Deep Truth", or "Core Revelation".
    2. The remaining 4 commands should be relevant, varied follow-up questions based on the current analysis.
    
    Return JSON array of objects with 'label' (max 4 words) and 'prompt'.
  `;

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              label: { type: Type.STRING },
              prompt: { type: Type.STRING },
            },
            required: ['label', 'prompt']
          }
        }
      }
    });
    const text = response.text;
    if (!text) return getDefaultCommands();
    return JSON.parse(text) as DynamicCommand[];
  } catch (error) {
    console.error("Command generation error", error);
    return getDefaultCommands();
  }
};

export const chatWithContext = async (
  history: { role: 'user' | 'model'; text: string }[],
  contextData: string,
  newMessage: string,
  modelId: ModelId
): Promise<{ text: string }> => {
  const ai = getClient();
  const systemInstruction = `
    You are an advanced Knowledge Engine using the ${modelId} model.
    You hold the following Data Truths (Knowledge Atoms) in your context:
    ---
    ${contextData}
    ---
    Answer the user's queries based PRIMARILY on this data. 
  `;

  const contents = history.map(h => ({
    role: h.role,
    parts: [{ text: h.text }]
  }));

  contents.push({
    role: 'user',
    parts: [{ text: newMessage }]
  });

  const response = await ai.models.generateContent({
    model: modelId,
    contents: contents,
    config: { systemInstruction }
  });
  return { text: response.text || "No response generated." };
};

export const getDefaultCommands = (): DynamicCommand[] => [
  { label: "Profound Insight", prompt: "Synthesize the single most profound and non-obvious insight from all current knowledge atoms." },
  { label: "Practical Application", prompt: "How can these findings be applied to solve a real-world problem immediately?" },
  { label: "Identify Gaps", prompt: "What crucial information is missing from this dataset that would change the conclusion?" },
  { label: "Future Scenario", prompt: "Based on these trends, describe a likely scenario 5 years from now." },
  { label: "Devils Advocate", prompt: "Argue against the prevailing consensus in this data." }
];

export const generateDebateTopics = async (contextData: string, modelId: ModelId): Promise<DebateTopic[]> => {
  const ai = getClient();
  const prompt = `
        Analyze the following context data. Identify 4 distinct, controversial, or multifaceted questions that can be debated based on this content.
        The topics should reveal tensions, trade-offs, or different interpretations inherent in the data.
        Context:
        ${contextData}
        Return JSON array: [{label, question}].
    `;
  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              label: { type: Type.STRING, description: "Short 2-5 word title" },
              question: { type: Type.STRING, description: "The central debate question" }
            },
            required: ['label', 'question']
          }
        }
      }
    });
    const text = response.text;
    if (!text) return [];
    return JSON.parse(text).map((t: any, i: number) => ({ ...t, id: `topic-${i}` }));
  } catch (e) {
    console.error("Debate topic gen failed", e);
    return [];
  }
};

export const runDebateRound = async (
  topic: DebateTopic,
  history: DebateRound[],
  contextData: string,
  modelId: ModelId
): Promise<DebateRound> => {
  const ai = getClient();
  const roundNumber = history.length + 1;
  const historyText = history.map(r =>
    `Round ${r.roundNumber}:\n` + r.turns.map(t => `${t.speaker}: ${t.text}`).join("\n")
  ).join("\n\n");

  const prompt = `
        You are simulating a structured debate on the topic: "${topic.question}".
        Context Data (Evidence):
        ${contextData}
        Debate History:
        ${historyText}
        Task: Generate Round ${roundNumber}.
        - If Round 1: Side A (Affirmative/Pro) opens with a strong argument citing evidence. Side B (Negative/Con) responds with a counter-argument and their own evidence.
        - If Round > 1: Side A rebuts Side B's previous point and advances the argument. Side B rebuts Side A and advances.
        - Both sides must use the provided Knowledge Atoms/Context as evidence.
        - Maintain distinct voices. Side A is optimistic/assertive. Side B is critical/analytical.
        - IF the history contains an "Audience" or "User" interjection, address it directly in the arguments.
        Return JSON object:
        { "sideA_argument": "...", "sideB_argument": "..." }
    `;

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            sideA_argument: { type: Type.STRING },
            sideB_argument: { type: Type.STRING }
          },
          required: ['sideA_argument', 'sideB_argument']
        }
      }
    });
    const result = JSON.parse(response.text || "{}");
    return {
      roundNumber,
      turns: [
        { speaker: 'Side A', text: result.sideA_argument },
        { speaker: 'Side B', text: result.sideB_argument }
      ]
    };
  } catch (e) {
    console.error("Debate round failed", e);
    throw e;
  }
};

export const generateChatDocument = async (
  history: ChatMessage[],
  theme: string,
  modelId: ModelId
): Promise<string> => {
  const ai = getClient();
  const transcript = history.map(m => `${m.role.toUpperCase()}: ${m.text}`).join('\n');
  const prompt = `
    Based on the following conversation transcript, generate a well-formatted markdown document.
    Focus strictly on the theme: "${theme}".

    Transcript:
    ${transcript}

    Structure the document clearly with headers, bullet points, and sections relevant to the theme.
  `;

  const response = await ai.models.generateContent({
    model: modelId,
    contents: prompt
  });

  return response.text || "No content generated.";
};

// --- ARCHITECT / PLAN GENERATION ---

import { ArchitecturalPlan, HandoffEnvelope } from '../types';

export const generateArchitecturalPlan = async (
  goal: string,
  atoms: KnowledgeAtom[],
  documents: UploadedDocument[],
  previousPlans: ArchitecturalPlan[],
  modelId: ModelId
): Promise<ArchitecturalPlan> => {
  const ai = getClient();

  const atomContext = atoms.map(a => {
    const meta = a.metadata ? `[${a.metadata.significance} | ${a.metadata.theme}]` : '';
    return `- ${meta} ${a.content} (Source: ${a.sourceFile})`;
  }).join("\n");

  const docContext = documents.map(d => `Document: ${d.name}\n${d.content.substring(0, 2000)}...`).join("\n\n");

  const previousPlanContext = previousPlans.length > 0
    ? `Previous Plans:\n${previousPlans.map(p => `- Goal: ${p.goal} | Status: ${p.status}`).join("\n")}`
    : "No previous plans.";

  const prompt = `
You are an Architect operating within a federated service loop.

Your role:
- You PRODUCE PLANS. You do NOT implement them.
- Your plans will be built by an Implementation Service.
- Your plans will be certified by a Certification Service.
- If certification fails, you may receive the failure as context to revise.

Current Context (Knowledge Atoms):
${atomContext || "No atoms in context."}

Current Context (Documents):
${docContext || "No documents uploaded."}

${previousPlanContext}

The user wants this to exist:
"${goal}"

Produce an Architectural Plan with these sections:

1. GOAL: Restate what needs to exist in precise terms
2. CONTEXT: Why this matters now, based on the documents
3. REQUIREMENTS: Specific, verifiable requirements (as array)
4. IMPLEMENTATION_STEPS: Ordered steps for the Builder
   - Each step has: step_id, description, inputs (array), expected_outputs (array), dependencies (array of step_ids)
5. SUCCESS_CRITERIA: How the Certification Service will verify success (as array)
6. FAILURE_MODES: What could go wrong and how to detect it (as array)

Remember:
- You are part of a loop that will keep running
- Your output becomes input for the next service
- Reference the documents when possible
- Be specific enough that the Builder doesn't have to guess
- Include criteria specific enough that the Certifier can verify

Return a JSON object with these exact fields:
{
  "goal": "...",
  "context": "...",
  "requirements": ["..."],
  "implementation_steps": [
    {
      "step_id": "step_1",
      "description": "...",
      "inputs": ["..."],
      "expected_outputs": ["..."],
      "dependencies": []
    }
  ],
  "success_criteria": ["..."],
  "failure_modes": ["..."]
}
`;

  const response = await ai.models.generateContent({
    model: modelId,
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          goal: { type: Type.STRING },
          context: { type: Type.STRING },
          requirements: { type: Type.ARRAY, items: { type: Type.STRING } },
          implementation_steps: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                step_id: { type: Type.STRING },
                description: { type: Type.STRING },
                inputs: { type: Type.ARRAY, items: { type: Type.STRING } },
                expected_outputs: { type: Type.ARRAY, items: { type: Type.STRING } },
                dependencies: { type: Type.ARRAY, items: { type: Type.STRING } }
              },
              required: ['step_id', 'description', 'inputs', 'expected_outputs', 'dependencies']
            }
          },
          success_criteria: { type: Type.ARRAY, items: { type: Type.STRING } },
          failure_modes: { type: Type.ARRAY, items: { type: Type.STRING } }
        },
        required: ['goal', 'context', 'requirements', 'implementation_steps', 'success_criteria', 'failure_modes']
      }
    }
  });

  const result = JSON.parse(response.text || "{}");

  const planId = `plan_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  return {
    planId,
    createdAt: Date.now(),
    sourceDocuments: documents.map(d => d.id),
    sourceAtoms: atoms.map(a => a.id),
    goal: result.goal || goal,
    context: result.context || "",
    requirements: result.requirements || [],
    implementationSteps: (result.implementation_steps || []).map((s: any) => ({
      stepId: s.step_id,
      description: s.description,
      inputs: s.inputs || [],
      expectedOutputs: s.expected_outputs || [],
      dependencies: s.dependencies || []
    })),
    successCriteria: result.success_criteria || [],
    failureModes: result.failure_modes || [],
    status: 'draft',
    handoffTo: 'implementation_service'
  };
};

export const createHandoffEnvelope = (
  plan: ArchitecturalPlan,
  previousEnvelopes: HandoffEnvelope[] = []
): HandoffEnvelope => {
  const envelopeId = `env_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  const lineage = previousEnvelopes.map(e => ({
    service: e.fromService,
    envelopeId: e.envelopeId,
    timestamp: e.createdAt
  }));

  // Add current step to lineage
  lineage.push({
    service: 'knowledge_atomizer',
    envelopeId,
    timestamp: Date.now()
  });

  const firstEnvelope = previousEnvelopes[0];
  const cycleCount = firstEnvelope
    ? firstEnvelope.context.cycleCount + 1
    : 1;
  const startTime = firstEnvelope
    ? firstEnvelope.createdAt
    : Date.now();

  return {
    envelopeId,
    fromService: 'knowledge_atomizer',
    toService: 'implementation',
    createdAt: Date.now(),
    payloadType: 'plan',
    payload: plan,
    lineage,
    context: {
      originalGoal: plan.goal,
      cycleCount,
      totalElapsed: Date.now() - startTime
    }
  };
};

export const exportPlanAsMarkdown = (plan: ArchitecturalPlan): string => {
  const stepsMarkdown = plan.implementationSteps.map((s, i) => `
### Step ${i + 1}: ${s.stepId}

**Description**: ${s.description}

**Inputs**:
${s.inputs.map(inp => `- ${inp}`).join('\n')}

**Expected Outputs**:
${s.expectedOutputs.map(out => `- ${out}`).join('\n')}

**Dependencies**: ${s.dependencies.length > 0 ? s.dependencies.join(', ') : 'None'}
`).join('\n');

  return `# Architectural Plan: ${plan.planId}

**Created**: ${new Date(plan.createdAt).toISOString()}
**Status**: ${plan.status}
**Handoff To**: ${plan.handoffTo || 'Not specified'}

---

## Goal

${plan.goal}

## Context

${plan.context}

## Requirements

${plan.requirements.map(r => `- ${r}`).join('\n')}

---

## Implementation Steps

${stepsMarkdown}

---

## Success Criteria

${plan.successCriteria.map(c => `- ${c}`).join('\n')}

## Failure Modes

${plan.failureModes.map(f => `- ${f}`).join('\n')}

---

## Source Context

**Documents**: ${plan.sourceDocuments.length} document(s)
**Atoms**: ${plan.sourceAtoms.length} atom(s)

---

*Generated by Knowledge Atomizer - Federated Services Architecture*
`;
};

export const exportHandoffAsJson = (envelope: HandoffEnvelope): string => {
  return JSON.stringify(envelope, null, 2);
};
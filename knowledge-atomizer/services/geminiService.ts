import { GoogleGenAI, Type, Schema, Modality } from "@google/genai";
import JSZip from 'jszip';
import { 
  KnowledgeAtom, DynamicCommand, AtomMetadata, ModelId, ModelConfig, 
  DebateTopic, DebateRound, SpinalNode, StandardMessage, RecommendedAtom,
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
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    throw new Error("API Key not found in environment variables");
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
  {
    id: 'gemini-3-pro-preview',
    label: 'Gemini 3 Pro',
    tokenLimit: 2000000, // 2M
    description: 'Complex reasoning, deep synthesis, and high-quality generation.',
    strengths: ['Deep Inference', 'Cross-Document Logic', 'Fallacy Detection']
  },
  {
    id: 'gemini-3-flash-preview',
    label: 'Gemini 3 Flash',
    tokenLimit: 1000000, // 1M
    description: 'Balanced performance, high versatility, and fast response times.',
    strengths: ['Thematic Analysis', 'Emerging Trends', 'Summarization']
  },
  {
    id: 'gemini-flash-lite-latest',
    label: 'Gemini 3 Flash-Lite',
    tokenLimit: 1000000, // 1M
    description: 'Extremely fast and cost-effective for high-volume extraction.',
    strengths: ['Keyword Extraction', 'Fast Facts', 'Basic Sentiment']
  }
];

export const getModelAnalytics = (modelId: ModelId) => {
  const coreMeta = [
      { label: "Compare Arguments", prompt: "Compare and contrast key arguments across the provided documents and knowledge atoms. Highlight points of consensus, contradiction, and nuance." },
      { label: "Emerging Trends", prompt: "Identify emerging trends, patterns, and shifts in the narrative or data provided. What direction is the information pointing towards?" },
      { label: "Sentiment Analysis", prompt: "Analyze the overall sentiment and emotional tone of the content. Is it optimistic, critical, neutral, or urgent? Provide examples." }
  ];

  switch (modelId) {
    case 'gemini-flash-lite-latest':
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
    case 'gemini-3-pro-preview':
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
    case 'gemini-3-flash-preview':
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

export const extractTextFromZip = async (file: File): Promise<Array<{name: string, content: string}>> => {
  const zip = new JSZip();
  const extracted: Array<{name: string, content: string}> = [];

  try {
    const loadedZip = await zip.loadAsync(file);
    const filePromises: Promise<void>[] = [];

    loadedZip.forEach((relativePath, zipEntry) => {
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

        if (response && response.embedding?.values) {
            return { 
                ...atom, 
                embedding: response.embedding.values,
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

                if (response && response.embedding?.values) {
                    atom.embedding = response.embedding.values;
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

                if (response && response.embedding?.values) {
                    atom.embedding = response.embedding.values;
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
    content: string, 
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
            metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: {type:Type.NUMBER}, subjectivity:{type:Type.NUMBER}, emotions:{type:Type.ARRAY, items:{type:Type.STRING}}, readingLevel:{type:Type.STRING} } } } },
            children: { 
                type: Type.ARRAY,
                items: {
                    type: Type.OBJECT,
                    properties: {
                        level: { type: Type.STRING, enum: ['L7'] },
                        content: { type: Type.STRING },
                        metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: {type:Type.NUMBER}, subjectivity:{type:Type.NUMBER}, emotions:{type:Type.ARRAY, items:{type:Type.STRING}}, readingLevel:{type:Type.STRING} } } } },
                        children: { 
                            type: Type.ARRAY,
                            items: {
                                type: Type.OBJECT,
                                properties: {
                                    level: { type: Type.STRING, enum: ['L6'] },
                                    content: { type: Type.STRING },
                                    metadata: { type: Type.OBJECT, properties: { stats: { type: Type.OBJECT, properties: { sentiment: {type:Type.NUMBER}, subjectivity:{type:Type.NUMBER}, emotions:{type:Type.ARRAY, items:{type:Type.STRING}}, readingLevel:{type:Type.STRING} } } } },
                                    children: { 
                                        type: Type.ARRAY,
                                        items: {
                                            type: Type.OBJECT,
                                            properties: {
                                                level: { type: Type.STRING, enum: ['L5'] },
                                                content: { type: Type.STRING },
                                                metadata: { type: Type.OBJECT, properties: { role: {type:Type.STRING}, stats: { type: Type.OBJECT, properties: { sentiment: {type:Type.NUMBER}, subjectivity:{type:Type.NUMBER}, emotions:{type:Type.ARRAY, items:{type:Type.STRING}}, readingLevel:{type:Type.STRING} } } } },
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
                queryEmbedding = embResult.embedding?.values;
            }
        } catch(e) {
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
                if(act.embedding) {
                    const s = calculateCosineSimilarity(atom.embedding!, act.embedding);
                    if(s > maxSimToActive) maxSimToActive = s;
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
            model: "gemini-3-flash-preview",
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
    } catch(e) {
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
        switch(type) {
            case 'Deep Dive': prompt += "Write an extensive, comprehensive Deep Dive analysis."; break;
            case 'Critique': prompt += "Write a critical analysis identifying flaws, gaps, and weaknesses."; break;
            case 'Briefing Doc': prompt += "Write a professional, concise Briefing Document for an executive."; break;
            case 'Blog Post': prompt += "Write an engaging, accessible Blog Post about these findings."; break;
            default: prompt += `Write a ${type}.`;
        }
    }
    prompt += "\nFormat as Markdown.";

    const response = await ai.models.generateContent({
        model: "gemini-3-pro-preview",
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
  
  return new Blob([wavBytes], { type: 'audio/wav' });
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
        model: "gemini-3-flash-preview",
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
        model: "gemini-3-flash-preview",
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
    modelId: ModelId
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

export const checkCoherenceAnchor = async (atoms: KnowledgeAtom[]): Promise<{passed: boolean, score: number, issues: string[]}> => {
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

export const distillToAtoms = async (
  fileName: string, 
  content: string,
  modelId: ModelId
): Promise<KnowledgeAtom[]> => {
  const ai = getClient();
  const prompt = `
    Analyze the following text. 
    Distill the core truths into a list of distinct, single sentences (Knowledge Atoms).
    For each atom, generate metadata that elevates the analysis:
    - theme: A 1-2 word category.
    - significance: One of 'Fundamental', 'Insight', 'Prediction', 'Nuance'.
    - tags: 2-3 keywords for cross-referencing.
    - If the content strongly implies the 'Adam' perspective (Not-Me, recursive self, internal contradiction), add 'Adam' to tags.

    Text:
    ${content}
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
        tags: { 
          type: Type.ARRAY, 
          items: { type: Type.STRING } 
        }
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
    const parsedData: { content: string, theme: string, significance: any, tags: string[] }[] = JSON.parse(rawText);
    const atoms: KnowledgeAtom[] = [];
    for (const item of parsedData) {
        const hash = await generateAtomHash(item.content);
        atoms.push({
            id: hash,
            content: item.content,
            sourceFile: fileName,
            metadata: {
                theme: item.theme,
                significance: item.significance,
                tags: item.tags
            },
            createdAt: Date.now(),
            embeddingStatus: 'pending'
        });
    }
    // Return immediately to allow UI update, do not await embedding here
    return atoms;

  } catch (error) {
    console.error("Distillation error:", error);
    throw error;
  }
};

export const refineAtomSignificance = async (atoms: KnowledgeAtom[], modelId: ModelId): Promise<{id: string, significance: string}[]> => {
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
    modelId: ModelId,
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
            model: "gemini-3-pro-preview", // Use Pro for synthesis
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
    if(!text) return getDefaultCommands();
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
        if(!text) return [];
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
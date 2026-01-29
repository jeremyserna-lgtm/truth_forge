
import { StandardMessage, StructureAnalysis, StructureCandidate, ImportConfig } from '../types';
import _ from 'lodash'; 

// --- STRUCTURAL ANALYSIS ---

export const analyzeJsonStructure = async (file: File): Promise<StructureAnalysis> => {
    const text = await file.text();
    const json = JSON.parse(text);
    const candidates: StructureCandidate[] = [];

    // Recursive traverser to find arrays or significant objects
    const traverse = (obj: any, path: string, depth: number) => {
        if (depth > 3) return; // Limit depth for performance

        if (Array.isArray(obj)) {
            candidates.push({
                path: path || 'root',
                type: 'Array',
                count: obj.length,
                sampleKeys: obj.length > 0 && typeof obj[0] === 'object' ? Object.keys(obj[0]) : [],
                depth
            });
            // Analyze the first item to see if it contains nested structures
            if (obj.length > 0 && typeof obj[0] === 'object') {
                traverse(obj[0], path ? `${path}[]` : 'root[]', depth + 1);
            }
        } else if (typeof obj === 'object' && obj !== null) {
            const keys = Object.keys(obj);
            // Heuristic: Objects with many keys might be maps (like ChatGPT 'mapping')
            if (keys.length > 20) {
                 candidates.push({
                    path: path || 'root',
                    type: 'Object',
                    count: keys.length,
                    sampleKeys: keys.slice(0, 5),
                    depth
                });
            }
            
            // Continue traversal for specific known patterns or generally
            keys.slice(0, 3).forEach(key => {
                 traverse(obj[key], path ? `${path}.${key}` : key, depth + 1);
            });
        }
    };

    traverse(json, 'root', 0); // Start with explicit root

    // Add a virtual "Single Document" candidate
    candidates.unshift({
        path: 'SINGLE_DOC_MODE',
        type: 'Object',
        count: 1,
        sampleKeys: [],
        depth: 0
    });

    return { candidates, rawJson: json };
};

// --- EXTRACTION ENGINE ---

export const processStructuredImport = (analysis: StructureAnalysis, config: ImportConfig): StandardMessage[][] => {
    const { rawJson } = analysis;
    const conversations: StandardMessage[][] = [];

    // Robust generic getter
    const getByPath = (obj: any, path: string): any => {
        if (!path || path === 'root') return obj;
        
        // Clean path: remove 'root.' or 'root' prefix if present
        let parts = path.split('.').filter(p => p !== 'root' && p !== '');
        
        let current = obj;
        for (const part of parts) {
            if (current === undefined || current === null) return undefined;
            
            // Handle array notation in path (e.g. "items[]") - strictly for schema pathing, 
            // usually we don't traverse INTO array unless iterating.
            // But if the path is direct to a property, we assume object traversal.
            // If we encounter 'part[]', it usually implies we should be inside an array map, 
            // but here we are doing direct access. We'll strip [] for direct access attempts.
            const cleanPart = part.replace('[]', '');
            current = current[cleanPart];
        }
        return current;
    };

    // CASE 1: Single Document / Flat
    if (config.l8Path === 'SINGLE_DOC_MODE') {
        // If L5 is root/array, just return that as one convo
        if (Array.isArray(rawJson)) {
            conversations.push(normalizeMessages(rawJson));
        } else {
             // Try to find the array based on l5Path
             let msgs = getByPath(rawJson, config.l5Path);
             
             if (msgs && typeof msgs === 'object' && !Array.isArray(msgs)) {
                 // Handle ChatGPT 'mapping' object
                 msgs = Object.values(msgs);
             }
             if (Array.isArray(msgs)) {
                 conversations.push(normalizeMessages(msgs));
             } else {
                 // Fallback: entire file is text
                 conversations.push([{ role: 'user', content: JSON.stringify(rawJson).substring(0, 5000) }]);
             }
        }
        return conversations;
    }

    // CASE 2: Structured Array (L8)
    let l8Node = getByPath(rawJson, config.l8Path);

    if (!Array.isArray(l8Node)) {
        console.warn("L8 Node is not an array, treating as single item");
        l8Node = [l8Node];
    }

    l8Node.forEach((convo: any) => {
        // Find L5 relative to convo
        let l5Node = convo;
        
        if (config.l5Path) {
             // Calculate Relative Path
             // L8 Path: root.conversations
             // L5 Path: root.conversations[].messages
             // Relative: messages
             
             // Logic: Remove the L8 path prefix + '[]' from the L5 path
             let relativePath = config.l5Path;
             
             // Escape dots for regex
             const l8Pattern = config.l8Path.replace(/\./g, '\\.');
             // Regex to match "L8Path" optionally followed by "[]" or "."
             const prefixRegex = new RegExp(`^${l8Pattern}(\\[\\])?\\.?`);
             
             relativePath = relativePath.replace(prefixRegex, '');
             
             if (relativePath) {
                 l5Node = getByPath(convo, relativePath);
             }
        }

        let rawMessages: any[] = [];
        if (Array.isArray(l5Node)) {
            rawMessages = l5Node;
        } else if (typeof l5Node === 'object' && l5Node !== null) {
            // Likely a Map (ChatGPT style)
            rawMessages = Object.values(l5Node);
        }

        if (rawMessages.length > 0) {
            conversations.push(normalizeMessages(rawMessages));
        }
    });

    return conversations;
};

// Heuristic Normalizer to convert any JSON object to StandardMessage
const normalizeMessages = (raw: any[]): StandardMessage[] => {
    return raw.map((item): StandardMessage => {
        // 1. ChatGPT Mapping structure
        if (item.message) {
            const m = item.message;
            if (m.content && m.content.parts) {
                return {
                    role: (m.author.role === 'assistant' ? 'model' : 'user') as 'user' | 'model',
                    content: m.content.parts.join('\n'),
                    timestamp: m.create_time
                };
            }
        }

        // 2. Claude / Simple
        const role = item.role || item.sender || item.author || 'user';
        const content = item.content || item.text || item.message || '';
        const ts = item.created_at || item.timestamp || item.create_time || 0;

        return {
            role: ((role === 'model' || role === 'assistant' || role === 'bot') ? 'model' : 'user') as 'user' | 'model',
            content: typeof content === 'string' ? content : JSON.stringify(content),
            timestamp: typeof ts === 'string' ? Date.parse(ts) : ts
        };
    })
    .filter(m => m.content.trim() !== '')
    .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
};

export const parseChatExport = async (file: File): Promise<StandardMessage[]> => {
    const analysis = await analyzeJsonStructure(file);
    let l8 = 'root';
    let l5 = '';
    
    const chatGptCand = analysis.candidates.find(c => c.path.includes('mapping'));
    if (chatGptCand) {
        l5 = chatGptCand.path;
    }
    
    const claudeCand = analysis.candidates.find(c => c.path.includes('chat_messages'));
    if (claudeCand) {
        l5 = claudeCand.path;
    }

    const convos = processStructuredImport(analysis, { l8Path: l8, l5Path: l5 });
    return convos.flat();
};

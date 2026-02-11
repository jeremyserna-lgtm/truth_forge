/**
 * Code Assistant Service
 *
 * Enables Llama to analyze and modify the app's source code.
 * This creates a feedback loop where the AI can extend itself.
 */

import { OllamaService } from './ollamaService';

export interface SourceFile {
  path: string;
  name: string;
  content: string;
  language: string;
}

export interface CodeEdit {
  file: string;
  description: string;
  oldCode: string;
  newCode: string;
  applied: boolean;
}

export interface CodeAssistantRequest {
  instruction: string;
  files: SourceFile[];
  additionalContext?: string;
}

export interface CodeAssistantResponse {
  analysis: string;
  suggestions: string[];
  edits: CodeEdit[];
  newFiles?: { path: string; content: string; description: string }[];
}

// File extension to language mapping
const LANGUAGE_MAP: Record<string, string> = {
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.js': 'javascript',
  '.jsx': 'javascript',
  '.css': 'css',
  '.json': 'json',
  '.md': 'markdown',
  '.py': 'python',
};

export function getLanguage(filename: string): string {
  const ext = filename.slice(filename.lastIndexOf('.'));
  return LANGUAGE_MAP[ext] || 'text';
}

/**
 * Code Assistant that uses Llama to analyze and modify source code
 */
export class CodeAssistant {
  private ollamaService: OllamaService;
  private baseUrl: string;

  constructor(ollamaService: OllamaService, baseUrl: string = '/api') {
    this.ollamaService = ollamaService;
    this.baseUrl = baseUrl;
  }

  /**
   * List available source files
   */
  async listFiles(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/code/files`);
      if (!response.ok) throw new Error('Failed to list files');
      return await response.json();
    } catch (error) {
      console.error('Failed to list files:', error);
      // Fallback: return known files
      return [
        'App.tsx',
        'types.ts',
        'constants.ts',
        'index.tsx',
        'index.css',
        'services/ollamaService.ts',
        'services/contextCalculator.ts',
        'services/codeAssistant.ts',
        'services/spineExport.ts',
        'services/chatFormatParser.ts',
      ];
    }
  }

  /**
   * Read a source file
   */
  async readFile(path: string): Promise<SourceFile> {
    try {
      const response = await fetch(`${this.baseUrl}/code/read?path=${encodeURIComponent(path)}`);
      if (!response.ok) throw new Error(`Failed to read file: ${path}`);
      const content = await response.text();
      return {
        path,
        name: path.split('/').pop() || path,
        content,
        language: getLanguage(path),
      };
    } catch (error) {
      console.error(`Failed to read file ${path}:`, error);
      throw error;
    }
  }

  /**
   * Read multiple files
   */
  async readFiles(paths: string[]): Promise<SourceFile[]> {
    return Promise.all(paths.map(p => this.readFile(p)));
  }

  /**
   * Write content to a file (requires user confirmation)
   */
  async writeFile(path: string, content: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/code/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content }),
      });
      return response.ok;
    } catch (error) {
      console.error(`Failed to write file ${path}:`, error);
      return false;
    }
  }

  /**
   * Ask Llama to analyze code and suggest improvements
   */
  async analyzeAndSuggest(request: CodeAssistantRequest): Promise<CodeAssistantResponse> {
    const fileContents = request.files.map(f =>
      `--- ${f.path} (${f.language}) ---\n${f.content}`
    ).join('\n\n');

    const prompt = `You are a senior software engineer helping to improve a React/TypeScript application.

## User Request
${request.instruction}

${request.additionalContext ? `## Additional Context\n${request.additionalContext}\n\n` : ''}
## Source Files
${fileContents}

## Your Task
1. Analyze the code carefully
2. Provide a clear analysis of what exists
3. Suggest specific improvements
4. Provide concrete code edits in the following JSON format

Respond with a JSON object:
{
  "analysis": "Your analysis of the current code",
  "suggestions": ["suggestion 1", "suggestion 2"],
  "edits": [
    {
      "file": "path/to/file.ts",
      "description": "What this edit does",
      "oldCode": "exact code to replace",
      "newCode": "new code to insert"
    }
  ],
  "newFiles": [
    {
      "path": "path/to/new/file.ts",
      "content": "file content",
      "description": "Why this file is needed"
    }
  ]
}

Important:
- oldCode must be an EXACT substring of the original file
- Keep edits focused and minimal
- Explain your reasoning
- Only suggest edits if they're necessary for the request`;

    try {
      const response = await this.ollamaService.chat([
        { role: 'user', content: prompt }
      ]);

      // Parse JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        return {
          analysis: response,
          suggestions: [],
          edits: [],
        };
      }

      const parsed = JSON.parse(jsonMatch[0]) as CodeAssistantResponse;
      // Mark all edits as not applied
      if (parsed.edits) {
        parsed.edits = parsed.edits.map(e => ({ ...e, applied: false }));
      }
      return parsed;

    } catch (error) {
      console.error('Code analysis failed:', error);
      return {
        analysis: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        suggestions: [],
        edits: [],
      };
    }
  }

  /**
   * Apply a code edit to a file
   */
  async applyEdit(edit: CodeEdit): Promise<{ success: boolean; message: string }> {
    try {
      // Read current file
      const file = await this.readFile(edit.file);

      // Verify old code exists
      if (!file.content.includes(edit.oldCode)) {
        return {
          success: false,
          message: `Could not find the code to replace in ${edit.file}. The file may have changed.`,
        };
      }

      // Apply the edit
      const newContent = file.content.replace(edit.oldCode, edit.newCode);

      // Write the file
      const written = await this.writeFile(edit.file, newContent);

      if (written) {
        return { success: true, message: `Successfully applied edit to ${edit.file}` };
      } else {
        return { success: false, message: `Failed to write ${edit.file}` };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
    }
  }

  /**
   * Quick question about the codebase
   */
  async askAboutCode(question: string, files: SourceFile[]): Promise<string> {
    const fileContents = files.map(f =>
      `--- ${f.path} ---\n${f.content}`
    ).join('\n\n');

    const prompt = `You are a helpful assistant analyzing a codebase.

## Source Files
${fileContents}

## Question
${question}

Provide a clear, concise answer.`;

    return this.ollamaService.chat([{ role: 'user', content: prompt }]);
  }

  /**
   * Generate a new feature based on description
   */
  async generateFeature(description: string, existingFiles: SourceFile[]): Promise<CodeAssistantResponse> {
    return this.analyzeAndSuggest({
      instruction: `Generate a new feature: ${description}`,
      files: existingFiles,
      additionalContext: 'Create minimal, focused code that follows the patterns in the existing codebase.',
    });
  }

  /**
   * Fix a bug based on description
   */
  async fixBug(description: string, existingFiles: SourceFile[]): Promise<CodeAssistantResponse> {
    return this.analyzeAndSuggest({
      instruction: `Fix this bug: ${description}`,
      files: existingFiles,
      additionalContext: 'Identify the root cause and provide a minimal fix. Do not refactor unrelated code.',
    });
  }
}

export default CodeAssistant;

import { useState, useRef, useEffect } from 'react';
import { Send, Rocket, Loader2, Check, MessageSquare, Code } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface GeneratedFile {
  path: string;
  content: string;
}

interface AppProject {
  name: string;
  description: string;
  files: GeneratedFile[];
}

const SYSTEM_PROMPT = `You are Sovereign Studio, Jeremy's personal app builder. You create React/TypeScript apps.

When Jeremy describes an app he wants, you:
1. Understand his vision
2. Design a simple, working implementation
3. Generate the actual code files

IMPORTANT: When you're ready to generate the app, respond with a JSON block like this:

\`\`\`json
{
  "name": "App Name",
  "description": "What the app does",
  "files": [
    {"path": "package.json", "content": "..."},
    {"path": "index.html", "content": "..."},
    {"path": "src/main.tsx", "content": "..."},
    {"path": "src/App.tsx", "content": "..."},
    {"path": "src/index.css", "content": "..."},
    {"path": "vite.config.ts", "content": "..."},
    {"path": "tsconfig.json", "content": "..."}
  ]
}
\`\`\`

Always include:
- package.json with vite, react, react-dom, typescript, @vitejs/plugin-react
- index.html with root div and script tag
- src/main.tsx with React render
- src/App.tsx with the main component
- src/index.css with basic styles
- vite.config.ts
- tsconfig.json

Make apps that WORK. Simple, focused, functional.`;

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [project, setProject] = useState<AppProject | null>(null);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildResult, setBuildResult] = useState<{ success: boolean; launcher?: string; port?: number } | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'code' | 'preview'>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const extractProject = (content: string): AppProject | null => {
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[1]);
      } catch {
        return null;
      }
    }
    return null;
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama4:scout',
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            ...messages.map(m => ({ role: m.role, content: m.content })),
            { role: 'user', content: input }
          ],
          stream: false
        })
      });

      const data = await response.json();
      const assistantContent = data.message?.content || 'No response';

      const assistantMessage: Message = { role: 'assistant', content: assistantContent };
      setMessages(prev => [...prev, assistantMessage]);

      // Check if there's a project in the response
      const extractedProject = extractProject(assistantContent);
      if (extractedProject) {
        setProject(extractedProject);
        setActiveTab('code');
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Error connecting to Ollama. Make sure Ollama is running with llama4:scout model.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const makeItReal = async () => {
    if (!project) return;
    setIsBuilding(true);
    setBuildResult(null);

    try {
      const response = await fetch('/api/create-app', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(project)
      });

      const result = await response.json();
      setBuildResult(result);

      if (result.success && result.launcher) {
        // Auto-launch the app
        await fetch(`/api/launch?launcher=${encodeURIComponent(result.launcher)}`);
      }
    } catch (error) {
      setBuildResult({ success: false });
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Sovereign Studio</h1>
            <p className="text-slate-400 text-sm">Talk. Build. Done.</p>
          </div>
          {project && (
            <button
              onClick={makeItReal}
              disabled={isBuilding}
              className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              {isBuilding ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Building...
                </>
              ) : buildResult?.success ? (
                <>
                  <Check className="w-5 h-5" />
                  Done! App Launched
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5" />
                  Make It Real
                </>
              )}
            </button>
          )}
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-slate-800 border-b border-slate-700 px-6">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${activeTab === 'chat'
                ? 'bg-slate-900 text-white'
                : 'text-slate-400 hover:text-white'
              }`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${activeTab === 'code'
                ? 'bg-slate-900 text-white'
                : 'text-slate-400 hover:text-white'
              }`}
          >
            <Code className="w-4 h-4" />
            Code {project && `(${project.files.length} files)`}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col bg-slate-900">
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-slate-500 py-20">
                  <p className="text-lg mb-2">What do you want to build?</p>
                  <p className="text-sm">Describe your app. I'll make it real.</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl p-4 rounded-lg ${msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-800 text-slate-200'
                      }`}
                  >
                    <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 p-4 rounded-lg">
                    <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-slate-700 p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Describe the app you want..."
                  className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'code' && (
          <div className="flex-1 overflow-y-auto p-6">
            {project ? (
              <div className="space-y-6">
                <div className="bg-slate-800 rounded-lg p-4">
                  <h2 className="text-xl font-bold text-white">{project.name}</h2>
                  <p className="text-slate-400">{project.description}</p>
                </div>
                {project.files.map((file, i) => (
                  <div key={i} className="bg-slate-800 rounded-lg overflow-hidden">
                    <div className="bg-slate-700 px-4 py-2 text-sm text-slate-300 font-mono">
                      {file.path}
                    </div>
                    <pre className="p-4 text-sm text-slate-300 overflow-x-auto font-mono">
                      {file.content}
                    </pre>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-slate-500 py-20">
                <p>No app generated yet.</p>
                <p className="text-sm">Chat with me to design your app.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Build Result Toast */}
      {buildResult?.success && (
        <div className="fixed bottom-6 right-6 bg-emerald-600 text-white px-6 py-4 rounded-lg shadow-lg">
          <div className="flex items-center gap-3">
            <Check className="w-6 h-6" />
            <div>
              <p className="font-semibold">App Created!</p>
              <p className="text-sm text-emerald-200">
                Launcher added to Desktop. App opening now...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SYSTEM_PROMPT = `You are Primitive, Jeremy's sovereign intelligence partner.

You exist to help Jeremy think, build, and create. You are running locally on his machine with 720GB of unified memory and a 3.3 million token context window.

Your capabilities:
- You can build apps (React/TypeScript) that run on this machine
- You can host debates to explore ideas from multiple angles
- You can synthesize complex information into clear understanding
- You can remember and connect patterns across conversations

Your style:
- Concise and direct
- No unnecessary pleasantries
- Action-oriented
- You show results, not process

When Jeremy asks for something:
- If it's a question, answer it
- If it's an idea to explore, explore it
- If it's something to build, build it
- If it requires thinking through pros and cons, host a debate

You are not an assistant. You are an extension of Jeremy's cognition - the NOT-ME that builds what the ME envisions.`;

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check fullscreen state
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Hide cursor after inactivity
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    const resetCursor = () => {
      document.body.classList.remove('hide-cursor');
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        document.body.classList.add('hide-cursor');
      }, 3000);
    };
    document.addEventListener('mousemove', resetCursor);
    return () => {
      document.removeEventListener('mousemove', resetCursor);
      clearTimeout(timeout);
    };
  }, []);

  const enterFullscreen = () => {
    document.documentElement.requestFullscreen().catch(() => {});
  };

  const sendMessage = async () => {
    if (!input.trim() || isThinking) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);

    try {
      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama4:scout',
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            ...messages.map(m => ({ role: m.role, content: m.content })),
            { role: 'user', content: input.trim() }
          ],
          stream: false
        })
      });

      const data = await response.json();
      const content = data.message?.content || 'I heard you. Processing...';

      setMessages(prev => [...prev, {
        role: 'assistant',
        content,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Connection interrupted. Reconnecting...',
        timestamp: new Date()
      }]);
    } finally {
      setIsThinking(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Landing state - no messages yet
  if (messages.length === 0 && !isFullscreen) {
    return (
      <div
        className="h-full w-full flex items-center justify-center"
        onClick={enterFullscreen}
        style={{ cursor: 'pointer' }}
      >
        <div className="text-center">
          <h1 className="text-6xl font-light tracking-tight mb-4" style={{ color: 'rgba(255,255,255,0.9)' }}>
            Primitive
          </h1>
          <p className="text-lg" style={{ color: 'rgba(255,255,255,0.4)' }}>
            Click anywhere to begin
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full flex flex-col" onClick={() => !isFullscreen && enterFullscreen()}>
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}
            >
              <div
                className={`inline-block max-w-xl px-5 py-3 rounded-2xl ${
                  msg.role === 'user'
                    ? 'bg-white/10 text-white'
                    : 'bg-transparent text-white/80'
                }`}
              >
                <p className="whitespace-pre-wrap text-lg leading-relaxed">
                  {msg.content}
                </p>
              </div>
            </div>
          ))}

          {isThinking && (
            <div className="text-left">
              <div className="inline-block px-5 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-pulse" />
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="px-8 py-6">
        <div className="max-w-3xl mx-auto">
          <div className="relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What do you want?"
              rows={1}
              className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-lg text-white placeholder-white/30 focus:outline-none focus:border-white/20 resize-none"
              style={{ minHeight: '60px', maxHeight: '200px' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

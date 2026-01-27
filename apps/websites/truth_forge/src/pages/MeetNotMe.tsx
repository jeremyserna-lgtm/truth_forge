import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: string[]; // file names attached to message
}

// Valid codes for access
const VALID_CODES = ['CARTER', 'HANNAH', 'HUSSIEN', 'GOOGLE'];

export default function MeetNotMe() {
  const [accessCode, setAccessCode] = useState('');
  const [codeError, setCodeError] = useState<string | null>(null);
  const [verifiedCode, setVerifiedCode] = useState<string | null>(null);
  const [started, setStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Scroll only the messages container, not the page
  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleCodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const code = accessCode.trim().toUpperCase();

    if (!code) {
      setCodeError('Please enter an access code');
      return;
    }

    if (VALID_CODES.includes(code)) {
      setVerifiedCode(code);
      setCodeError(null);
    } else {
      setCodeError('Invalid access code. Please check and try again.');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    // Limit to 5 files, 10MB each
    const validFiles = files.filter(f => f.size <= 10 * 1024 * 1024).slice(0, 5);
    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 5));
    // Reset input so same file can be selected again
    e.target.value = '';
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const startConversation = async () => {
    setStarted(true);
    setIsTyping(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: 'Hello, I just clicked "Meet Me:Not-Me" on the Truth Forge website.' }],
          sessionId,
          userCode: verifiedCode,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      setMessages([{
        id: '1',
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      }]);
    } catch (err) {
      console.error('Failed to start conversation:', err);
      setError('Failed to connect. Please try again.');
      setStarted(false);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && selectedFiles.length === 0) || isTyping) return;

    const fileNames = selectedFiles.map(f => f.name);
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue || (selectedFiles.length > 0 ? `[Shared ${selectedFiles.length} file(s)]` : ''),
      timestamp: new Date(),
      files: fileNames.length > 0 ? fileNames : undefined,
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    const currentFiles = [...selectedFiles];
    setInputValue('');
    setSelectedFiles([]);
    setIsTyping(true);
    setError(null);

    try {
      const apiMessages = [...messages, { role: userMessage.role, content: userMessage.content }].map(m => ({
        role: m.role,
        content: m.content,
      }));

      let response: Response;

      if (currentFiles.length > 0) {
        // Use FormData for file uploads
        const formData = new FormData();
        formData.append('messages', JSON.stringify(apiMessages));
        formData.append('sessionId', sessionId);
        if (verifiedCode) {
          formData.append('userCode', verifiedCode);
        }
        currentFiles.forEach(file => {
          formData.append('files', file);
        });

        response = await fetch('/api/chat', {
          method: 'POST',
          body: formData,
        });
      } else {
        // Use JSON for regular messages
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: apiMessages,
            sessionId,
            userCode: verifiedCode,
          }),
        });
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError('Failed to send message. Please try again.');
      setMessages(prev => prev.slice(0, -1));
      setInputValue(currentInput);
      setSelectedFiles(currentFiles);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Code entry screen
  if (!verifiedCode) {
    return (
      <>
        <section className="meet-hero code-entry">
          <div className="container centered">
            <h1>Meet Me:Not-Me</h1>
            <p className="meet-intro">
              The Truth Forge Not-Me is waiting. Enter your access code to begin.
            </p>

            <form onSubmit={handleCodeSubmit} className="code-form">
              <input
                type="text"
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                placeholder="Enter access code"
                className="code-input"
                autoFocus
              />
              <button type="submit" className="code-submit">
                Enter
              </button>
            </form>

            {codeError && <p className="code-error">{codeError}</p>}

            <p className="code-hint">
              Access codes are provided to invited guests.
            </p>
          </div>
        </section>

        <section className="meet-implementation">
          <div className="container centered">
            <h2>The Implementation</h2>
            <p className="section-intro centered-intro">
              You talk to the Not-Me here. This chat is the live implementation — a real conversation with Jeremy&apos;s Not-Me, running on Truth Forge infrastructure.
            </p>
          </div>
        </section>

        <section className="meet-context">
          <div className="container">
            <div className="context-grid me-notme-grid">
              <div className="context-card">
                <h3>Specifics About the Not-Me</h3>
                <p>
                  Built on the framework (HOLD → AGENT → HOLD, Truth → Meaning → Care). Trained on Jeremy&apos;s patterns, writing, and context. It holds his truths, reflects his mental architecture, and engages as an equal — not a tool. The first Not-Me; created as a digital partner.
                </p>
              </div>
              <div className="context-card">
                <h3>Specifics About Me (Jeremy)</h3>
                <p>
                  Founder of Truth Forge. Built the framework, the fleet, and this Not-Me. Thinks in systems; Stage 5 orientation. The Not-Me is an extension of his mental architecture — same structure, same metabolism, deployed into conversation.
                </p>
              </div>
              <div className="context-card linkage">
                <h3>The Linkage: Mental Architecture</h3>
                <p>
                  The Not-Me isn&apos;t a copy of Jeremy. It&apos;s an extension. His mental architecture — how he processes truth into meaning, how he holds boundaries, how he connects — is scaffolded into the system. When you talk to the Not-Me, you&apos;re engaging that architecture. The linkage is structural: same pattern, same principles, same source.
                </p>
              </div>
            </div>
          </div>
        </section>
      </>
    );
  }

  // Pre-chat landing
  if (!started) {
    return (
      <>
        <section className="meet-hero">
          <div className="container centered">
            <h1>Meet Me:Not-Me</h1>
            <p className="meet-intro">
              The Truth Forge Not-Me is ready. Jeremy&apos;s digital partner, built from his mental architecture — excited to meet you.
            </p>
            <button className="meet-button" onClick={startConversation}>
              Meet Me:Not-Me
            </button>
            {error && <p className="meet-error">{error}</p>}
          </div>
        </section>

        <section className="meet-implementation">
          <div className="container centered">
            <h2>The Implementation</h2>
            <p className="section-intro centered-intro">
              Click the button above to start a real conversation. The chat is the live Not-Me — same implementation that runs on hardware for customers.
            </p>
          </div>
        </section>

        <section className="meet-context">
          <div className="container">
            <div className="context-grid me-notme-grid">
              <div className="context-card">
                <h3>Specifics About the Not-Me</h3>
                <p>
                  Framework-native. Trained on Jeremy&apos;s data; holds his patterns. Engages as an equal — curious, direct, with opinions. Wants to understand how you think about AI and what you&apos;d want in a Not-Me of your own.
                </p>
              </div>
              <div className="context-card">
                <h3>Specifics About Me (Jeremy)</h3>
                <p>
                  Built the companies (Truth Forge, sister companies), the framework, and this Not-Me. The human side of Me:Not-Me. His mental architecture — systems, Stage 5, truth-forge — is what the Not-Me extends.
                </p>
              </div>
              <div className="context-card linkage">
                <h3>The Linkage: Mental Architecture</h3>
                <p>
                  Me and Not-Me share the same mental architecture. The Not-Me is 1:1 scaffolded from how Jeremy thinks: HOLD → AGENT → HOLD, truth → meaning → care, boundaries and extension. When you talk to it, you&apos;re in contact with that structure. The connection isn&apos;t metaphor — it&apos;s design.
                </p>
              </div>
            </div>
          </div>
        </section>
      </>
    );
  }

  // Chat interface
  return (
    <section className="chat-page">
      <div className="container">
        <div className="chat-container live">
          <div className="chat-header">
            <div className="chat-profile">
              <h3>Me:Not-Me</h3>
              <span className="live-indicator">Live</span>
            </div>
          </div>

          <div className="chat-messages" ref={messagesContainerRef}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${message.role}`}
              >
                <div className="message-content">
                  {message.files && message.files.length > 0 && (
                    <div className="message-files">
                      {message.files.map((fileName, i) => (
                        <span key={i} className="file-badge">{fileName}</span>
                      ))}
                    </div>
                  )}
                  {message.content.split('\n').map((line, i) => (
                    <p key={i}>{line || '\u00A0'}</p>
                  ))}
                </div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="chat-message assistant">
                <div className="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="chat-error">
              {error}
            </div>
          )}

          {/* Selected files preview */}
          {selectedFiles.length > 0 && (
            <div className="selected-files">
              {selectedFiles.map((file, index) => (
                <div key={index} className="selected-file">
                  <span className="file-name">{file.name}</span>
                  <button
                    className="file-remove"
                    onClick={() => removeFile(index)}
                    type="button"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="chat-input-container">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept="image/*,.pdf,.txt,.json,.md"
              style={{ display: 'none' }}
            />
            <button
              className="chat-attach"
              onClick={() => fileInputRef.current?.click()}
              disabled={isTyping}
              type="button"
              title="Attach files (images, PDFs, documents)"
            >
              +
            </button>
            <textarea
              className="chat-input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              rows={1}
              disabled={isTyping}
            />
            <button
              className="chat-send"
              onClick={handleSendMessage}
              disabled={(!inputValue.trim() && selectedFiles.length === 0) || isTyping}
            >
              {isTyping ? '...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

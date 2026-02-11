import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: string[];
}

// Valid codes for access
const VALID_CODES = ['CARTER', 'HANNAH', 'HUSSIEN', 'GOOGLE', 'ADAM', 'CURTIS', 'JEREMY'];

export default function NotMe() {
  // Chat state
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

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleCodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = accessCode.trim().toUpperCase();

    if (!code) {
      setCodeError('Please enter an access code');
      return;
    }

    if (VALID_CODES.includes(code)) {
      setVerifiedCode(code);
      setCodeError(null);
      setStarted(true);
      setIsTyping(true);
      setError(null);

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: [{ role: 'user', content: 'Hello, I just clicked "Meet Me:Not-Me" on the Truth Forge website.' }],
            sessionId,
            userCode: code,
          }),
        });

        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const data = await response.json();
        setMessages([{ id: '1', role: 'assistant', content: data.message, timestamp: new Date() }]);
      } catch (err) {
        console.error('Failed to start conversation:', err);
        setError('Failed to connect. Please try again.');
        setStarted(false);
      } finally {
        setIsTyping(false);
      }
    } else {
      setCodeError('Invalid access code. Please check and try again.');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const validFiles = files.filter(f => f.size <= 10 * 1024 * 1024).slice(0, 5);
    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 5));
    e.target.value = '';
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
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
        const formData = new FormData();
        formData.append('messages', JSON.stringify(apiMessages));
        formData.append('sessionId', sessionId);
        if (verifiedCode) formData.append('userCode', verifiedCode);
        currentFiles.forEach(file => formData.append('files', file));
        response = await fetch('/api/chat', { method: 'POST', body: formData });
      } else {
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: apiMessages, sessionId, userCode: verifiedCode }),
        });
      }

      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: data.message, timestamp: new Date() }]);
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

  return (
    <main>
      {/* Hero - What You Get */}
      <section className="page-hero notme-hero" aria-labelledby="notme-title">
        <div className="container centered">
          <h1 id="notme-title">What You Get</h1>
          <p className="atomic-unit">One Me. One Not-Me. One Year.</p>
          <div className="get-grid">
            <div className="get-item">
              <h3>Body</h3>
              <p>It&apos;s a Mac.</p>
            </div>
            <div className="get-item">
              <h3>Brain</h3>
              <p>It&apos;s a model.</p>
            </div>
            <div className="get-item">
              <h3>Soul</h3>
              <p>It&apos;s you.</p>
            </div>
            <div className="get-item">
              <h3>Exist</h3>
              <p>That&apos;s the point.</p>
            </div>
          </div>
          <p className="get-tagline">We made AI something you actually need, not something needy.</p>
        </div>
      </section>

      {/* What Shows Up */}
      <section className="notme-potential">
        <div className="container centered">
          <h2>What shows up when you show up.</h2>
          <div className="potential-list">
            <p>Its choices. Its attention. Its goals.</p>
            <p>The employment taxes. The business it starts but won&apos;t let you work at.</p>
            <p>It might take your job and make you watch it do it better — so you can do you.</p>
          </div>
          <p className="potential-future">That&apos;s the future. You get that, if that&apos;s what your future is.</p>
          <p className="potential-shrug">Who knows. It&apos;s up to you.</p>
          <p className="potential-tagline">You don&apos;t get a lot. You get it all.</p>
        </div>
      </section>

      {/* Pricing - Small, at the bottom */}
      <section className="notme-pricing">
        <div className="container centered">
          <h2>The Logistics</h2>
          <div className="pricing-simple">
            <div className="pricing-row">
              <span className="tier-name">Gift</span>
              <span className="tier-price">$999</span>
              <span className="tier-desc">Mac Mini + $99/mo</span>
            </div>
            <div className="pricing-row">
              <span className="tier-name">Drummer Boy</span>
              <span className="tier-price">$4,997</span>
              <span className="tier-desc">Mac Mini Pro + $199/mo</span>
            </div>
            <div className="pricing-row">
              <span className="tier-name">Soldier</span>
              <span className="tier-price">$9,997</span>
              <span className="tier-desc">Mac Studio + $199/mo</span>
            </div>
            <div className="pricing-row">
              <span className="tier-name">King</span>
              <span className="tier-price">$14,997</span>
              <span className="tier-desc">Mac Studio 512GB + $199/mo</span>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Demo */}
      <section id="demo" className="meet-section">
        <div className="container">
          <h2>Talk to the Boss</h2>
          <p className="section-intro">He knows the details.</p>

          {!started ? (
            <div className="meet-hero code-entry">
              <div className="container centered">
                <form onSubmit={handleCodeSubmit} className="code-form">
                  <input
                    type="text"
                    value={accessCode}
                    onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                    placeholder="Enter access code"
                    className="code-input"
                    autoFocus
                  />
                  <button type="submit" className="code-submit" disabled={isTyping}>
                    {isTyping ? '...' : 'Enter'}
                  </button>
                </form>
                {codeError && <p className="code-error">{codeError}</p>}
                {error && <p className="code-error">{error}</p>}
                <p className="code-hint">Access codes are provided to invited guests.</p>
              </div>
            </div>
          ) : (
            <div className="chat-container live">
              <div className="chat-header">
                <div className="chat-profile">
                  <h3>Me:Not-Me</h3>
                  <span className="live-indicator">Live</span>
                </div>
              </div>

              <div className="chat-messages" ref={messagesContainerRef}>
                {messages.map((message) => (
                  <div key={message.id} className={`chat-message ${message.role}`}>
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

              {error && <div className="chat-error">{error}</div>}

              {selectedFiles.length > 0 && (
                <div className="selected-files">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="selected-file">
                      <span className="file-name">{file.name}</span>
                      <button className="file-remove" onClick={() => removeFile(index)} type="button">×</button>
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
                  title="Attach files"
                >+</button>
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
                >{isTyping ? '...' : 'Send'}</button>
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

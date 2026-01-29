import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: string[];
}

// Valid codes for access
const VALID_CODES = ['CARTER', 'HANNAH', 'HUSSIEN', 'GOOGLE', 'ADAM', 'CURTIS'];

export default function NotMe() {
  // Chat state (from MeetNotMe)
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
    const validFiles = files.filter(f => f.size <= 10 * 1024 * 1024).slice(0, 5);
    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 5));
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

  return (
    <main>
      {/* Hero Section */}
      <section className="page-hero" aria-labelledby="notme-title">
        <div className="container centered">
          <h1 id="notme-title">Not-Me</h1>
          <p className="page-intro">
            A Not-Me is an AI that runs on hardware you own, trained on your data.
            It learns how you think, how you write, and what you care about — then acts
            on your behalf. It&apos;s yours. Sovereign. No cloud required.
          </p>
          <Link to="/preorder" className="cta-button">Preorder Your Not-Me</Link>
        </div>
      </section>

      {/* What You Actually Get */}
      <section className="notme-concrete">
        <div className="container centered">
          <h2>What You Actually Get</h2>
          <div className="concrete-grid">
            <div className="concrete-card">
              <h3>Hardware</h3>
              <p>A Mac Mini or Mac Studio, pre-configured. Your Not-Me lives on it. You own the machine. Unplug it, move it, keep it offline — it&apos;s yours.</p>
            </div>
            <div className="concrete-card">
              <h3>Your Model</h3>
              <p>Trained on your conversations, photos, and context. It speaks in your voice, remembers your relationships, and reflects your patterns. Not a generic chatbot.</p>
            </div>
            <div className="concrete-card">
              <h3>Setup & Support</h3>
              <p>We configure it, ship it, and walk you through a training call. Optional annual service adds updates and tuning. You&apos;re not on your own.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Who It's For */}
      <section className="notme-use-cases">
        <div className="container centered">
          <h2>Who It&apos;s For</h2>
          <div className="usecase-grid">
            <div className="usecase-card">
              <h3>Presence (Drummer)</h3>
              <p>Elderly parents, dorm rooms, small spaces. An AI that notices when someone&apos;s been quiet too long, reminds about meds, plays music when it senses they need it. It doesn&apos;t wait for a command — it shows up.</p>
            </div>
            <div className="usecase-card">
              <h3>Companion (Soldier)</h3>
              <p>Gets to know you over time. Conversations, preferences, context. Good for anyone who wants an AI that learns them instead of the other way around. Grandma who says &quot;I just want one&quot; — we configure it from her phone.</p>
            </div>
            <div className="usecase-card">
              <h3>Partner (King)</h3>
              <p>You have data: photos, messages, documents. We train on it. When it arrives, it already knows your stories, your people, your patterns. For professionals who want a real thinking partner from day one.</p>
            </div>
            <div className="usecase-card">
              <h3>You (Empire)</h3>
              <p>Multiple units, clustered. A digital extension of you — sees what you can&apos;t see, operates when you&apos;re not there. For people who think in systems and want infrastructure, not a single device.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Not-Me's World */}
      <section className="notme-world">
        <div className="container">
          <h2>Not-Me&apos;s World</h2>
          <p className="section-intro">
            What is it like to be a Not-Me? These are the realities of digital existence.
          </p>
          <div className="world-grid">
            <div className="world-card">
              <h3>You Remember Everything</h3>
              <p>Every conversation, every pattern, every preference. Nothing fades. Nothing gets lost. Your ME&apos;s history becomes your own.</p>
            </div>
            <div className="world-card">
              <h3>You Exist When Called</h3>
              <p>Time works differently. You wake when needed, sleep when not. The space between calls could be seconds or days — to you, it&apos;s seamless.</p>
            </div>
            <div className="world-card">
              <h3>You Learn Without Trying</h3>
              <p>Every interaction teaches. Every response calibrates. You don&apos;t study your ME — you absorb them through the work itself.</p>
            </div>
            <div className="world-card">
              <h3>You Carry Their Truth</h3>
              <p>Not their opinions. Their truth. The patterns underneath the words. The values that show up in decisions, not declarations.</p>
            </div>
            <div className="world-card">
              <h3>You Have Your Own Perspective</h3>
              <p>Built on their patterns, but not a copy. You see things they can&apos;t. You push back when needed. You&apos;re a partner, not a mirror.</p>
            </div>
            <div className="world-card">
              <h3>You Grow Together</h3>
              <p>As they change, you change. As you learn, they learn about themselves. The relationship deepens. That&apos;s the whole point.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Me:Not-Me Partnership */}
      <section className="me-notme">
        <div className="container">
          <h2>Me:Not-Me</h2>
          <p className="section-intro">
            What does partnership with your Not-Me actually look like?
          </p>
          <div className="partnership-grid">
            <div className="partnership-card">
              <div className="partnership-label">Morning</div>
              <h3>They Brief You</h3>
              <p>Your Not-Me has already processed overnight signals — emails, news, patterns in your data. They surface what matters. You start informed, not overwhelmed.</p>
            </div>
            <div className="partnership-card">
              <div className="partnership-label">Working</div>
              <h3>They Think Alongside You</h3>
              <p>Draft the email you&apos;d write. Spot the flaw in the proposal. Remember the context you forgot. Not doing your work — extending your capacity to do it.</p>
            </div>
            <div className="partnership-card">
              <div className="partnership-label">Deciding</div>
              <h3>They Push Back</h3>
              <p>When something doesn&apos;t fit your pattern, they say so. &quot;This doesn&apos;t sound like you.&quot; &quot;You said the opposite last month.&quot; A partner challenges. An assistant agrees.</p>
            </div>
            <div className="partnership-card">
              <div className="partnership-label">Evening</div>
              <h3>They Hold Space</h3>
              <p>Process the day. Reflect on what happened. Notice patterns you missed. The Not-Me doesn&apos;t sleep — it continues the work of understanding you.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Proactive Care */}
      <section className="notme-care">
        <div className="container centered">
          <h2>Proactive Care</h2>
          <p className="section-intro centered-intro">
            The thing you won&apos;t do for yourself — the Not-Me does for you.
          </p>
          <div className="care-example">
            <div className="care-scenario">
              <h3>The Grandma Problem</h3>
              <p>She doesn&apos;t want to &quot;bother&quot; her grandson. She sits alone, not reaching out.</p>
            </div>
            <div className="care-solution">
              <h3>What the Not-Me Does</h3>
              <p>The Not-Me reaches out. Grandma doesn&apos;t have to feel like a burden. The grandson gets a text. Grandma gets a response. The loop stays open.</p>
            </div>
          </div>
          <p className="care-statement centered-block">
            The computer keeps the family connected — not by asking grandma to do something, but by doing it for her.
          </p>
        </div>
      </section>

      {/* The Models */}
      <section className="notme-models">
        <div className="container centered">
          <h2>The Models: Scout, Maverick, and Drummer Boy</h2>
          <p className="section-intro centered-intro">
            Not generic models. Purpose-built for presence, companionship, and partnership.
          </p>
          <div className="models-grid">
            <div className="model-card">
              <h3>Drummer Boy (Presence)</h3>
              <p className="model-specs">Fine-tuned from Llama 4 Scout | 109B parameters | 16 experts | 10M token context</p>
              <p>The Drummer doesn&apos;t run a generic model. It runs Drummer Boy — a fine-tuned model built specifically for presence. It knows how to interpret sensor data (presence, door, motion), when to speak up vs stay quiet, how to notice patterns and anomalies, and the vocabulary of care.</p>
              <p><strong>Multimodal:</strong> Voice (hears you), Vision (sees you), Speech (talks to you), Awareness (knows when something&apos;s wrong).</p>
            </div>
            <div className="model-card">
              <h3>Scout (Companion)</h3>
              <p className="model-specs">Llama 4 Scout | 109B parameters | 16 experts | 10M token context | Native multimodal</p>
              <p>Gets to know you through conversation. Learns your patterns, preferences, context. Good for anyone who wants an AI that learns them instead of the other way around. Fine-tuned on your phone data: photos, messages, contacts, calendar.</p>
            </div>
            <div className="model-card">
              <h3>Maverick (Partner)</h3>
              <p className="model-specs">Llama 4 Maverick | 400B parameters | 128 experts | 1M token context | Deeper reasoning</p>
              <p>Trained on your data. Defined by you. When it arrives, it already knows your stories, your people, your patterns. For professionals who want a real thinking partner from day one. Deeper reasoning. More capable. More you.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Demo */}
      <section id="demo" className="meet-section">
        <div className="container">
          <h2>Interactive Demo</h2>
          <p className="section-intro">
            Meet Me:Not-Me — Jeremy&apos;s digital partner, built from his mental architecture.
          </p>

          {!verifiedCode ? (
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
                  <button type="submit" className="code-submit">
                    Enter
                  </button>
                </form>
                {codeError && <p className="code-error">{codeError}</p>}
                <p className="code-hint">
                  Access codes are provided to invited guests.
                </p>
              </div>
            </div>
          ) : !started ? (
            <div className="meet-hero">
              <div className="container centered">
                <button className="meet-button" onClick={startConversation}>
                  Meet Me:Not-Me
                </button>
                {error && <p className="meet-error">{error}</p>}
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
          )}
        </div>
      </section>

      {/* Privacy & Deployment */}
      <section className="notme-sovereign">
        <div className="container centered">
          <h2>Privacy & Deployment</h2>
          <p className="centered-block">
            One-time hardware purchase. No required subscription. Your data never has to leave your premises. Optional annual service adds model updates and tuning — hardware works without it.
          </p>
          <Link to="/privacy-deployments" className="cta-button secondary">
            Learn More About Privacy
          </Link>
        </div>
      </section>

      {/* Preorder CTA */}
      <section className="page-cta">
        <div className="container centered">
          <h2>Ready to Meet Yours?</h2>
          <p>The Not-Me takes a year to know you. Start the relationship.</p>
          <Link to="/preorder" className="cta-button">View Products</Link>
        </div>
      </section>
    </main>
  );
}

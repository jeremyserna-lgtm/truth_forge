/**
 * Chat Page for Primitive Engine
 *
 * THE BUILDER - Custom Engagement
 * Chat interface for initial conversations about custom builds.
 */

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

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
          messages: [{ role: 'user', content: 'I want to discuss a custom build.' }],
          sessionId,
          context: 'primitive_engine',
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
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsTyping(true);
    setError(null);

    try {
      const apiMessages = [...messages, { role: userMessage.role, content: userMessage.content }].map(m => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: apiMessages,
          sessionId,
          context: 'primitive_engine',
        }),
      });

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
    <div className="page chat-page">
      <section className="chat-hero">
        <h1>Let's Talk</h1>
        <p>Describe what you're trying to build. We'll figure out if we can help.</p>
      </section>

      <section className="chat-section">
        {!started ? (
          <div className="chat-start">
            <div className="start-content">
              <h2>Start the Conversation</h2>
              <p>
                We build custom systems. Data pipelines, AI integration,
                automation, whatever you need. This conversation helps us
                understand what you're trying to do.
              </p>
              <p>
                No commitment. Just a conversation to see if we're a fit.
              </p>
              <button
                onClick={startConversation}
                className="cta-button"
                disabled={isTyping}
              >
                {isTyping ? 'Starting...' : 'Begin'}
              </button>
              {error && <p className="error-message">{error}</p>}
            </div>
          </div>
        ) : (
          <div className="chat-container">
            <div className="chat-header">
              <div className="chat-profile">
                <h3>Primitive Engine</h3>
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

            <div className="chat-input-container">
              <textarea
                className="chat-input"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe what you're trying to build..."
                rows={1}
                disabled={isTyping}
              />
              <button
                className="chat-send"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
              >
                {isTyping ? '...' : 'Send'}
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { sendChatMessage } from '../lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: string[];
}

type AuthMode = 'login' | 'register' | 'forgot' | 'reset';

export default function Login() {
  const { user, profile, portalStats, loading, isConfigured, signIn, signUp, signOut, resetPassword, updatePassword, updatePortalStats } = useAuth();

  // Auth form state
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [showResetSent, setShowResetSent] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetSuccess, setResetSuccess] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [chatStarted, setChatStarted] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Local stats (synced with Supabase)
  const [localStats, setLocalStats] = useState({
    documentsShared: portalStats?.documentsShared || 0,
    conversations: portalStats?.conversations || 0,
    timeInvested: portalStats?.timeInvested || 'Not yet started',
    depthAchieved: portalStats?.depthAchieved || 'Surface level'
  });

  // Sync local stats with portalStats from context
  useEffect(() => {
    if (portalStats) {
      setLocalStats({
        documentsShared: portalStats.documentsShared,
        conversations: portalStats.conversations,
        timeInvested: portalStats.timeInvested,
        depthAchieved: portalStats.depthAchieved
      });
    }
  }, [portalStats]);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Check for password reset URL parameter
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reset') === 'true') {
      setAuthMode('reset');
    }
  }, []);

  // Start chat when user is authenticated
  useEffect(() => {
    if (user && profile && !chatStarted && !loading) {
      startChat();
    }
  }, [user, profile, loading]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setShowEmailConfirmation(false);
    setShowResetSent(false);
    setAuthLoading(true);

    try {
      if (authMode === 'register') {
        if (!firstName.trim() || !lastName.trim()) {
          setAuthError('Please enter your first and last name');
          setAuthLoading(false);
          return;
        }
        const displayName = `${firstName.trim()} ${lastName.trim()}`;
        const { error, needsEmailConfirmation } = await signUp(email, password, displayName, firstName.trim(), lastName.trim());
        if (error) {
          setAuthError(error.message);
        } else if (needsEmailConfirmation) {
          setShowEmailConfirmation(true);
        }
      } else if (authMode === 'forgot') {
        const { error } = await resetPassword(email);
        if (error) {
          setAuthError(error.message);
        } else {
          setShowResetSent(true);
        }
      } else if (authMode === 'reset') {
        if (newPassword !== confirmPassword) {
          setAuthError('Passwords do not match');
          setAuthLoading(false);
          return;
        }
        if (newPassword.length < 6) {
          setAuthError('Password must be at least 6 characters');
          setAuthLoading(false);
          return;
        }
        const { error } = await updatePassword(newPassword);
        if (error) {
          setAuthError(error.message);
        } else {
          setResetSuccess(true);
          // Clear URL params
          window.history.replaceState({}, '', window.location.pathname);
        }
      } else {
        const { error } = await signIn(email, password);
        if (error) {
          setAuthError(error.message);
        }
      }
    } catch (err) {
      console.error('Auth error:', err);
      setAuthError('An unexpected error occurred');
    } finally {
      setAuthLoading(false);
    }
  };

  const startChat = async () => {
    if (!profile) return;

    setChatStarted(true);
    setIsTyping(true);
    setError(null);

    try {
      const data = await sendChatMessage(
        [{ role: 'user', content: 'Hello, I just logged in to my Not-Me portal.' }],
        sessionId,
        profile.user_code
      );

      if (data.error) {
        throw new Error(data.error);
      }

      setMessages([{
        id: '1',
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      }]);

      // Log if using edge function
      if (data.edgeFunction) {
        console.log(`Chat via Edge Function (${data.duration}ms)`);
      }
    } catch (err) {
      console.error('Failed to start conversation:', err);
      setError('Failed to connect. Please try again.');
    } finally {
      setIsTyping(false);
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
    if ((!inputValue.trim() && selectedFiles.length === 0) || isTyping || !profile) return;

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

    // Update stats
    const newStats = {
      ...localStats,
      conversations: localStats.conversations + 1,
      timeInvested: 'Active session',
      depthAchieved: localStats.conversations > 5 ? 'Building understanding' : 'Getting started',
      documentsShared: localStats.documentsShared + currentFiles.length
    };
    setLocalStats(newStats);
    await updatePortalStats(newStats);

    try {
      const apiMessages = [...messages, { role: userMessage.role, content: userMessage.content }].map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }));

      // Use unified API client (supports both Vercel and Edge Functions)
      const data = await sendChatMessage(
        apiMessages,
        sessionId,
        profile.user_code,
        currentFiles.length > 0 ? currentFiles : undefined
      );

      if (data.error) {
        throw new Error(data.error);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Log if using edge function
      if (data.edgeFunction) {
        console.log(`Chat via Edge Function (${data.duration}ms)`);
      }
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

  // Loading state
  if (loading) {
    return (
      <main className="portal-page">
        <section className="portal-entry">
          <div className="container centered">
            <div className="loading-spinner">Loading...</div>
          </div>
        </section>
      </main>
    );
  }

  // AUTH SCREEN (Login/Register/Forgot/Reset)
  if (!user) {
    // Show email confirmation message
    if (showEmailConfirmation) {
      return (
        <main className="portal-page">
          <section className="portal-entry">
            <div className="container centered">
              <h1>Check Your Email</h1>
              <div className="email-confirmation-message">
                <p className="portal-intro">
                  We've sent a confirmation link to <strong>{email}</strong>
                </p>
                <p>Click the link in your email to activate your account and access your Not-Me portal.</p>
                <button
                  type="button"
                  className="auth-submit"
                  onClick={() => {
                    setShowEmailConfirmation(false);
                    setAuthMode('login');
                  }}
                  style={{ marginTop: '2rem' }}
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          </section>
        </main>
      );
    }

    // Show password reset email sent message
    if (showResetSent) {
      return (
        <main className="portal-page">
          <section className="portal-entry">
            <div className="container centered">
              <h1>Check Your Email</h1>
              <div className="email-confirmation-message">
                <p className="portal-intro">
                  We've sent a password reset link to <strong>{email}</strong>
                </p>
                <p>Click the link in your email to reset your password.</p>
                <button
                  type="button"
                  className="auth-submit"
                  onClick={() => {
                    setShowResetSent(false);
                    setAuthMode('login');
                  }}
                  style={{ marginTop: '2rem' }}
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          </section>
        </main>
      );
    }

    // Show password reset success
    if (resetSuccess) {
      return (
        <main className="portal-page">
          <section className="portal-entry">
            <div className="container centered">
              <h1>Password Updated</h1>
              <div className="email-confirmation-message">
                <p className="portal-intro">
                  Your password has been successfully updated.
                </p>
                <button
                  type="button"
                  className="auth-submit"
                  onClick={() => {
                    setResetSuccess(false);
                    setAuthMode('login');
                  }}
                  style={{ marginTop: '2rem' }}
                >
                  Sign In
                </button>
              </div>
            </div>
          </section>
        </main>
      );
    }

    return (
      <main className="portal-page">
        <section className="portal-entry">
          <div className="container centered">
            <h1>Your Portal</h1>
            <p className="portal-intro">
              {authMode === 'login' && 'Sign in to connect with your Not-Me.'}
              {authMode === 'register' && 'Create an account to begin your journey.'}
              {authMode === 'forgot' && 'Enter your email to reset your password.'}
              {authMode === 'reset' && 'Enter your new password.'}
            </p>

            {!isConfigured && (
              <div className="auth-warning">
                <p>Authentication is not configured. Please set up Supabase environment variables.</p>
              </div>
            )}

            <form onSubmit={handleAuthSubmit} className="auth-form">
              {authMode === 'register' && (
                <>
                  <div className="form-field">
                    <label htmlFor="firstName">First Name</label>
                    <input
                      id="firstName"
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="Your first name"
                      required
                      disabled={authLoading || !isConfigured}
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="lastName">Last Name</label>
                    <input
                      id="lastName"
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      placeholder="Your last name"
                      required
                      disabled={authLoading || !isConfigured}
                    />
                  </div>
                </>
              )}

              {(authMode === 'login' || authMode === 'register' || authMode === 'forgot') && (
                <div className="form-field">
                  <label htmlFor="email">Email</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                    disabled={authLoading || !isConfigured}
                  />
                </div>
              )}

              {(authMode === 'login' || authMode === 'register') && (
                <div className="form-field">
                  <label htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Your password"
                    required
                    minLength={6}
                    disabled={authLoading || !isConfigured}
                  />
                </div>
              )}

              {authMode === 'reset' && (
                <>
                  <div className="form-field">
                    <label htmlFor="newPassword">New Password</label>
                    <input
                      id="newPassword"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password"
                      required
                      minLength={6}
                      disabled={authLoading || !isConfigured}
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                      id="confirmPassword"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                      required
                      minLength={6}
                      disabled={authLoading || !isConfigured}
                    />
                  </div>
                </>
              )}

              {authError && <p className="auth-error">{authError}</p>}

              <button type="submit" className="auth-submit" disabled={authLoading || !isConfigured}>
                {authLoading ? 'Please wait...' :
                  authMode === 'login' ? 'Sign In' :
                  authMode === 'register' ? 'Create Account' :
                  authMode === 'forgot' ? 'Send Reset Link' :
                  'Update Password'}
              </button>
            </form>

            <div className="auth-switch">
              {authMode === 'login' && (
                <>
                  <p>
                    Don&apos;t have an account?{' '}
                    <button type="button" onClick={() => setAuthMode('register')}>
                      Create one
                    </button>
                  </p>
                  <p>
                    <button type="button" onClick={() => setAuthMode('forgot')}>
                      Forgot your password?
                    </button>
                  </p>
                </>
              )}
              {authMode === 'register' && (
                <p>
                  Already have an account?{' '}
                  <button type="button" onClick={() => setAuthMode('login')}>
                    Sign in
                  </button>
                </p>
              )}
              {(authMode === 'forgot' || authMode === 'reset') && (
                <p>
                  <button type="button" onClick={() => setAuthMode('login')}>
                    Back to Sign In
                  </button>
                </p>
              )}
            </div>
          </div>
        </section>
      </main>
    );
  }

  // FULL PORTAL EXPERIENCE (authenticated)
  return (
    <main className="portal-page">
      <section className="portal-header">
        <div className="container centered">
          <h1 className="portal-welcome">Hey {profile?.display_name || 'Friend'}</h1>
          <p className="portal-subtitle">ME:NOT-ME - Your identity, extended.</p>
          <button className="sign-out-btn" onClick={signOut}>Sign Out</button>
        </div>
      </section>

      {/* TWO-COLUMN PROFILE: ME / NOT-ME */}
      <section className="portal-profiles">
        <div className="container">
          <div className="profile-grid">
            {/* LEFT: What the ME provides */}
            <div className="profile-card me">
              <h2>What You&apos;ve Given</h2>

              <div className="profile-field">
                <label>Documents Shared</label>
                <div className={localStats.documentsShared > 0 ? 'value' : 'placeholder'}>
                  {localStats.documentsShared > 0
                    ? `${localStats.documentsShared} document${localStats.documentsShared > 1 ? 's' : ''} uploaded`
                    : '0 documents uploaded - waiting for you to begin'}
                </div>
              </div>

              <div className="profile-field">
                <label>Conversations</label>
                <div className={localStats.conversations > 0 ? 'value' : 'placeholder'}>
                  {localStats.conversations > 0
                    ? `${localStats.conversations} exchange${localStats.conversations > 1 ? 's' : ''}`
                    : 'Start chatting to reveal yourself'}
                </div>
              </div>

              <div className="profile-field">
                <label>Time Invested</label>
                <div className={localStats.timeInvested !== 'Not yet started' ? 'value' : 'placeholder'}>
                  {localStats.timeInvested}
                </div>
              </div>

              <div className="profile-field">
                <label>Depth Achieved</label>
                <div className={localStats.depthAchieved !== 'Surface level' ? 'value' : 'placeholder'}>
                  {localStats.depthAchieved}
                </div>
              </div>
            </div>

            {/* RIGHT: What the NOT-ME builds */}
            <div className="profile-card not-me">
              <h2>What Emerges From You</h2>

              <div className="profile-field">
                <label>Your Not-Me&apos;s Understanding</label>
                <div className="emerging">[Grows as you share...]</div>
              </div>

              <div className="profile-field">
                <label>Coherence State</label>
                <div className="emerging">[Tracked over time...]</div>
              </div>

              <div className="profile-field">
                <label>Purpose Direction</label>
                <div className="emerging">[Emerges from patterns...]</div>
              </div>

              <div className="profile-field">
                <label>Your Twin&apos;s Perspective</label>
                <div className="emerging">[The one who sees you clearly...]</div>
              </div>

              <div className="profile-explanation">
                <strong>This space fills itself.</strong><br />
                Your Not-Me grows here - from what you share, from your conversations, from your journey.
                You can&apos;t fill this directly. But you create the conditions for it to emerge.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CHAT SECTION */}
      <section className="portal-chat">
        <div className="container">
          <div className="chat-container portal live">
            <div className="chat-header">
              <div className="chat-profile">
                <h3>Chat with Your Not-Me</h3>
                <span className="live-indicator">Live</span>
              </div>
            </div>

            <div className="chat-messages" ref={messagesContainerRef}>
              {messages.length === 0 && !isTyping && (
                <div className="chat-empty">
                  Start a conversation - your Not-Me is listening...
                </div>
              )}
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
                placeholder="Ask about identity, purpose, or what this all means..."
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
    </main>
  );
}

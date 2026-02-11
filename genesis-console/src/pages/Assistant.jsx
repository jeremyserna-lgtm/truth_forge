import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { getJson, postJson } from '../api';

function cardStyle() {
    return {
        background: 'var(--genesis-surface)',
        border: '1px solid var(--genesis-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--gap-lg)',
    };
}

function inputStyle() {
    return {
        width: '100%',
        padding: '10px 12px',
        background: 'var(--genesis-bg)',
        border: '1px solid var(--genesis-border)',
        borderRadius: 'var(--radius-sm)',
        color: '#e5e7eb',
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        outline: 'none',
    };
}

function buttonStyle(kind = 'primary') {
    const base = {
        padding: '8px 12px',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--genesis-border)',
        fontSize: 10,
        fontFamily: 'var(--font-mono)',
        letterSpacing: 1,
        cursor: 'pointer',
    };

    if (kind === 'danger') {
        return {
            ...base,
            background: 'rgba(239,68,68,0.12)',
            color: '#ef4444',
            border: '1px solid rgba(239,68,68,0.25)',
        };
    }

    if (kind === 'success') {
        return {
            ...base,
            background: 'rgba(16,185,129,0.12)',
            color: '#10b981',
            border: '1px solid rgba(16,185,129,0.25)',
        };
    }

    return {
        ...base,
        background: 'rgba(59,130,246,0.12)',
        color: '#60a5fa',
        border: '1px solid rgba(59,130,246,0.25)',
    };
}

function parseRouteParam(search) {
    try {
        const params = new URLSearchParams(search || '');
        return params.get('route') || '/';
    } catch {
        return '/';
    }
}

function formatTime(isoString) {
    if (!isoString) return '--:--:--';
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return '--:--:--';
    return date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

const QUICK_PROMPTS = [
    'What does this page do and what should I click first?',
    'Explain all sections in plain language.',
    'What is not configured yet and how do I verify it?',
    'Give me a 3-step checklist to move forward right now.',
];

export default function AssistantPage({ ollamaStatus }) {
    const location = useLocation();
    const listRef = useRef(null);
    const recognitionRef = useRef(null);

    const [focusRoute, setFocusRoute] = useState(() => parseRouteParam(location.search));
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [model, setModel] = useState('');
    const [busy, setBusy] = useState(false);
    const [listening, setListening] = useState(false);
    const [voiceSupported, setVoiceSupported] = useState(false);
    const [status, setStatus] = useState('Ready.');

    const totalMessages = messages.length;
    const modelOptions = useMemo(
        () => (ollamaStatus.models || []).map((m) => m.name).filter(Boolean),
        [ollamaStatus.models],
    );

    const refreshHistory = useCallback(async () => {
        try {
            const data = await getJson('/api/assistant/history?limit=120');
            setMessages(data.messages || []);
            setStatus(`History synced (${data.total || 0} messages).`);
        } catch (error) {
            setStatus(`History sync failed: ${error.message}`);
        }
    }, []);

    useEffect(() => {
        void refreshHistory();
        const timer = setInterval(() => {
            void refreshHistory();
        }, 25000);
        return () => clearInterval(timer);
    }, [refreshHistory]);

    useEffect(() => {
        if (!listRef.current) return;
        listRef.current.scrollTop = listRef.current.scrollHeight;
    }, [messages]);

    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.onresult = (event) => {
            const transcript = String(event.results?.[0]?.[0]?.transcript || '').trim();
            if (!transcript) return;
            setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
            setStatus('Voice captured. You can send now.');
        };
        recognition.onend = () => {
            setListening(false);
        };
        recognition.onerror = (event) => {
            setListening(false);
            setStatus(`Voice input failed: ${event.error}`);
        };

        recognitionRef.current = recognition;
        setVoiceSupported(true);

        return () => {
            try {
                recognition.stop();
            } catch {
                // no-op
            }
            recognitionRef.current = null;
        };
    }, []);

    useEffect(() => {
        setFocusRoute(parseRouteParam(location.search));
    }, [location.search]);

    const sendMessage = useCallback(async () => {
        const text = input.trim();
        if (!text || busy) return;

        setBusy(true);
        setStatus('Querying local assistant...');
        setInput('');
        try {
            const result = await postJson('/api/assistant/chat', {
                message: text,
                route: focusRoute || '/',
                model: model || undefined,
                snapshot: {
                    ui_route: '/chat',
                    focus_route: focusRoute || '/',
                    ollama_connected: Boolean(ollamaStatus.connected),
                    available_models: modelOptions,
                    timestamp: new Date().toISOString(),
                },
            });

            if (!result.ok) {
                throw new Error(result.error || 'assistant_request_failed');
            }

            await refreshHistory();
            if (result.degraded) {
                setStatus('Assistant replied in degraded mode. Check Ollama status.');
            } else if (result.offline) {
                setStatus('Assistant offline fallback used. Load a local model.');
            } else {
                setStatus(`Assistant replied via ${result.message?.model || 'model'}.`);
            }
        } catch (error) {
            setStatus(`Assistant request failed: ${error.message}`);
        } finally {
            setBusy(false);
        }
    }, [busy, focusRoute, input, model, modelOptions, ollamaStatus.connected, refreshHistory]);

    const handleVoiceToggle = useCallback(() => {
        const recognition = recognitionRef.current;
        if (!recognition) return;

        if (listening) {
            recognition.stop();
            setListening(false);
            setStatus('Voice input stopped.');
            return;
        }

        try {
            recognition.start();
            setListening(true);
            setStatus('Listening...');
        } catch (error) {
            setListening(false);
            setStatus(`Voice input could not start: ${error.message}`);
        }
    }, [listening]);

    const handleQuickPrompt = useCallback((prompt) => {
        setInput(prompt);
    }, []);

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>ASSISTANT</h1>
                <p>Ask Genesis Monitor what anything means, what to click, and what to fix next. Voice input is available when supported.</p>
            </div>

            <div className="grid-4">
                <div className="stat-card" title="Total assistant messages stored on this machine">
                    <span className="stat-label">CHAT MESSAGES</span>
                    <span className="stat-value" style={{ color: '#3b82f6' }}>{totalMessages}</span>
                    <span className="stat-sub">persistent local history</span>
                </div>
                <div className="stat-card" title="Whether Ollama is currently reachable by the assistant">
                    <span className="stat-label">LOCAL MODEL STATUS</span>
                    <span className="stat-value" style={{ color: ollamaStatus.connected ? '#10b981' : '#ef4444', fontSize: 18 }}>
                        {ollamaStatus.connected ? 'CONNECTED' : 'OFFLINE'}
                    </span>
                    <span className="stat-sub">Ollama backend</span>
                </div>
                <div className="stat-card" title="The route the assistant should explain and operate against">
                    <span className="stat-label">FOCUS ROUTE</span>
                    <span className="stat-value" style={{ color: '#f59e0b', fontSize: 18 }}>
                        {focusRoute}
                    </span>
                    <span className="stat-sub">context target</span>
                </div>
                <div className="stat-card" title="Browser support for speech-to-text controls">
                    <span className="stat-label">VOICE INPUT</span>
                    <span className="stat-value" style={{ color: voiceSupported ? '#10b981' : '#6b7280', fontSize: 18 }}>
                        {voiceSupported ? 'READY' : 'UNAVAILABLE'}
                    </span>
                    <span className="stat-sub">Web Speech API</span>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--gap-lg)' }}>
                <div style={cardStyle()}>
                    <div className="card-header">
                        <span>GENESIS MONITOR CHAT</span>
                        <span className="badge">{busy ? 'THINKING' : 'IDLE'}</span>
                    </div>

                    <div
                        ref={listRef}
                        style={{
                            height: 360,
                            overflow: 'auto',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 8,
                            marginBottom: 10,
                            paddingRight: 4,
                        }}
                    >
                        {messages.length === 0 && (
                            <div style={{
                                padding: 14,
                                background: 'var(--genesis-bg)',
                                border: '1px solid var(--genesis-border)',
                                borderRadius: 8,
                                color: '#9ca3af',
                                fontSize: 12,
                                lineHeight: 1.5,
                            }}
                            >
                                No assistant history yet. Ask: "What does the Pipeline page do?"
                            </div>
                        )}

                        {messages.map((message) => {
                            const isAssistant = message.role === 'assistant';
                            return (
                                <div
                                    key={message.id}
                                    style={{
                                        padding: '10px 12px',
                                        background: isAssistant ? 'rgba(59,130,246,0.08)' : 'rgba(17,24,39,0.95)',
                                        border: `1px solid ${isAssistant ? 'rgba(59,130,246,0.22)' : 'var(--genesis-border)'}`,
                                        borderRadius: 8,
                                    }}
                                    title={`${isAssistant ? 'Assistant' : 'User'} message`}
                                >
                                    <div style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        marginBottom: 6,
                                        gap: 10,
                                        fontFamily: 'var(--font-mono)',
                                        fontSize: 10,
                                    }}
                                    >
                                        <span style={{ color: isAssistant ? '#60a5fa' : '#9ca3af' }}>
                                            {isAssistant ? 'ASSISTANT' : 'YOU'}
                                        </span>
                                        <span style={{ color: '#6b7280' }}>
                                            {formatTime(message.created_at || message._ts)}
                                        </span>
                                    </div>
                                    <div style={{ color: '#e5e7eb', lineHeight: 1.55, fontSize: 12, whiteSpace: 'pre-wrap' }}>
                                        {message.content}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 190px', gap: 8, marginBottom: 8 }}>
                        <input
                            type="text"
                            value={focusRoute}
                            onChange={(event) => setFocusRoute(event.target.value || '/')}
                            style={inputStyle()}
                            placeholder="/pipeline"
                            title="Tell assistant what route/screen to explain"
                        />
                        <select
                            value={model}
                            onChange={(event) => setModel(event.target.value)}
                            style={inputStyle()}
                            title="Optional: force a specific local model"
                        >
                            <option value="">Auto model</option>
                            {modelOptions.map((option) => (
                                <option key={option} value={option}>{option}</option>
                            ))}
                        </select>
                    </div>

                    <textarea
                        rows={4}
                        style={{ ...inputStyle(), resize: 'vertical' }}
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        placeholder="Ask for plain-language explanation, click-paths, or troubleshooting..."
                        title="Type your question to Genesis Monitor"
                    />

                    <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
                        <button
                            type="button"
                            onClick={() => void sendMessage()}
                            style={buttonStyle('success')}
                            disabled={busy || input.trim().length === 0}
                            title="Send this message to the assistant"
                        >
                            SEND
                        </button>
                        <button
                            type="button"
                            onClick={handleVoiceToggle}
                            style={buttonStyle(listening ? 'danger' : 'primary')}
                            disabled={!voiceSupported || busy}
                            title="Start/stop speech-to-text"
                        >
                            {listening ? 'STOP MIC' : 'VOICE INPUT'}
                        </button>
                        <button
                            type="button"
                            onClick={() => {
                                setInput('');
                                setStatus('Draft cleared.');
                            }}
                            style={buttonStyle('primary')}
                            disabled={busy}
                            title="Clear current draft text"
                        >
                            CLEAR DRAFT
                        </button>
                        <button
                            type="button"
                            onClick={() => void refreshHistory()}
                            style={buttonStyle('primary')}
                            disabled={busy}
                            title="Reload assistant message history from disk"
                        >
                            REFRESH HISTORY
                        </button>
                    </div>
                </div>

                <div style={{ ...cardStyle(), display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <div className="card-header">QUICK PROMPTS</div>
                    {QUICK_PROMPTS.map((prompt) => (
                        <button
                            key={prompt}
                            type="button"
                            style={{
                                ...buttonStyle(),
                                textAlign: 'left',
                                lineHeight: 1.5,
                                whiteSpace: 'normal',
                            }}
                            onClick={() => handleQuickPrompt(prompt)}
                            title="Load this prompt into the message box"
                        >
                            {prompt}
                        </button>
                    ))}

                    <div style={{
                        marginTop: 6,
                        padding: 10,
                        borderRadius: 8,
                        background: 'var(--genesis-bg)',
                        border: '1px solid var(--genesis-border)',
                        fontSize: 10,
                        color: '#9ca3af',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: 1.6,
                    }}
                    >
                        <div style={{ color: '#6b7280', marginBottom: 6 }}>STATUS</div>
                        {status}
                    </div>

                    <div style={{
                        padding: 10,
                        borderRadius: 8,
                        background: 'rgba(16,185,129,0.08)',
                        border: '1px solid rgba(16,185,129,0.25)',
                        fontSize: 10,
                        color: '#a7f3d0',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: 1.6,
                    }}
                    >
                        Tip: set `focus route` to `/pipeline`, `/knowledge`, `/models`, or another screen and ask for exact click paths.
                    </div>
                </div>
            </div>
        </div>
    );
}

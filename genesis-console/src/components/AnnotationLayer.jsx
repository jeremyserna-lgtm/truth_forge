import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { getJson, postJson } from '../api';

const TYPE_COLORS = {
    feedback: '#60a5fa',
    question: '#f59e0b',
    issue: '#ef4444',
};

function clamp01(value) {
    if (!Number.isFinite(value)) return 0.5;
    if (value < 0) return 0;
    if (value > 1) return 1;
    return value;
}

export default function AnnotationLayer({ containerRef }) {
    const location = useLocation();
    const route = location.pathname;

    const [enabled, setEnabled] = useState(false);
    const [statusFilter, setStatusFilter] = useState('open');
    const [annotations, setAnnotations] = useState([]);
    const [message, setMessage] = useState('');
    const [selectedId, setSelectedId] = useState(null);
    const [busy, setBusy] = useState(false);

    const [composer, setComposer] = useState(null);
    const [draftType, setDraftType] = useState('feedback');
    const [draftMessage, setDraftMessage] = useState('');
    const [draftAnchorText, setDraftAnchorText] = useState('');

    const selected = useMemo(
        () => annotations.find((annotation) => annotation.id === selectedId) || null,
        [annotations, selectedId],
    );

    const refresh = useCallback(async () => {
        try {
            const query = new URLSearchParams({
                route,
                status: statusFilter,
                limit: '300',
            });
            const response = await getJson(`/api/annotations?${query.toString()}`);
            setAnnotations(response.annotations || []);
        } catch (error) {
            setMessage(`Annotation refresh failed: ${error.message}`);
        }
    }, [route, statusFilter]);

    useEffect(() => {
        void refresh();
        const interval = setInterval(() => {
            void refresh();
        }, 15000);
        return () => clearInterval(interval);
    }, [refresh]);

    useEffect(() => {
        setSelectedId(null);
        setComposer(null);
    }, [route]);

    const handleCreateAnnotation = async () => {
        if (!composer) return;
        const text = draftMessage.trim();
        if (!text) {
            setMessage('Annotation text required.');
            return;
        }
        setBusy(true);
        try {
            const annotation = await postJson('/api/annotations', {
                route,
                x: composer.x,
                y: composer.y,
                annotation_type: draftType,
                message: text,
                anchor_text: draftAnchorText || null,
                context: {
                    route,
                    user_agent: navigator.userAgent,
                },
            });
            setDraftMessage('');
            setDraftAnchorText('');
            setComposer(null);
            setSelectedId(annotation.id);
            setMessage('Annotation saved.');
            await refresh();
        } catch (error) {
            setMessage(`Create annotation failed: ${error.message}`);
        } finally {
            setBusy(false);
        }
    };

    const updateStatus = async (annotationId, status) => {
        setBusy(true);
        try {
            const annotation = await postJson(`/api/annotations/${encodeURIComponent(annotationId)}/status`, {
                status,
            });
            setSelectedId(annotation.id);
            setMessage(`Annotation status updated to ${status}.`);
            await refresh();
        } catch (error) {
            setMessage(`Status update failed: ${error.message}`);
        } finally {
            setBusy(false);
        }
    };

    const openComposerAtClick = (event) => {
        if (!enabled) return;
        if (!containerRef?.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return;

        const x = clamp01((event.clientX - rect.left) / rect.width);
        const y = clamp01((event.clientY - rect.top) / rect.height);
        const selection = window.getSelection?.()?.toString?.() || '';
        setDraftAnchorText(selection.slice(0, 240));
        setComposer({ x, y });
        setSelectedId(null);
    };

    return (
        <div className="annotation-root">
            <div className="annotation-toolbar">
                <button
                    type="button"
                    onClick={() => setEnabled((value) => !value)}
                    className={`annotation-btn ${enabled ? 'active' : ''}`}
                    title={enabled ? 'Annotation mode is ON. Click anywhere to add a marker.' : 'Enable annotation mode'}
                >
                    {enabled ? 'Annotating' : 'Annotate'}
                </button>
                <select
                    value={statusFilter}
                    onChange={(event) => setStatusFilter(event.target.value)}
                    className="annotation-filter"
                    title="Filter annotation markers by workflow status"
                >
                    <option value="open">Open</option>
                    <option value="resolved">Resolved</option>
                    <option value="all">All</option>
                </select>
                <button type="button" onClick={() => void refresh()} className="annotation-btn" title="Reload annotations from storage">
                    Refresh
                </button>
            </div>

            <div
                className={`annotation-overlay ${enabled ? 'capture' : ''}`}
                onClick={openComposerAtClick}
                role="presentation"
            >
                {annotations.map((annotation, index) => (
                    <button
                        key={annotation.id}
                        type="button"
                        className={`annotation-marker ${selectedId === annotation.id ? 'selected' : ''}`}
                        style={{
                            left: `${annotation.x * 100}%`,
                            top: `${annotation.y * 100}%`,
                            borderColor: TYPE_COLORS[annotation.annotation_type] || '#60a5fa',
                        }}
                        title={`${annotation.annotation_type}: ${annotation.message}`}
                        onClick={(event) => {
                            event.stopPropagation();
                            setSelectedId(annotation.id);
                            setComposer(null);
                        }}
                    >
                        <span>{index + 1}</span>
                    </button>
                ))}

                {composer && (
                    <div
                        className="annotation-composer"
                        style={{
                            left: `${composer.x * 100}%`,
                            top: `${composer.y * 100}%`,
                        }}
                        onClick={(event) => event.stopPropagation()}
                        role="presentation"
                    >
                        <div className="annotation-composer-header">NEW ANNOTATION</div>
                        <select
                            value={draftType}
                            onChange={(event) => setDraftType(event.target.value)}
                            className="annotation-input"
                            title="Choose what kind of annotation you are creating"
                        >
                            <option value="feedback">Feedback</option>
                            <option value="question">Question</option>
                            <option value="issue">Issue</option>
                        </select>
                        <textarea
                            rows={4}
                            value={draftMessage}
                            onChange={(event) => setDraftMessage(event.target.value)}
                            placeholder="Ask your question or leave feedback for this exact spot..."
                            className="annotation-input annotation-textarea"
                            title="Describe feedback, ask a question, or report an issue for this exact location"
                        />
                        {draftAnchorText && (
                            <div className="annotation-anchor">Selected text: {draftAnchorText}</div>
                        )}
                        <div className="annotation-actions">
                            <button
                                type="button"
                                onClick={() => setComposer(null)}
                                className="annotation-btn"
                                disabled={busy}
                                title="Close the annotation composer"
                            >
                                Cancel
                            </button>
                            <button
                                type="button"
                                onClick={() => void handleCreateAnnotation()}
                                className="annotation-btn active"
                                disabled={busy}
                                title="Save this annotation"
                            >
                                Save
                            </button>
                        </div>
                    </div>
                )}

                {selected && (
                    <div className="annotation-detail" onClick={(event) => event.stopPropagation()} role="presentation">
                        <div className="annotation-composer-header">ANNOTATION</div>
                        <div className="annotation-meta">
                            type: <b>{selected.annotation_type}</b> | status: <b>{selected.status}</b>
                        </div>
                        <div className="annotation-message">{selected.message}</div>
                        {selected.anchor_text && (
                            <div className="annotation-anchor">Selected text: {selected.anchor_text}</div>
                        )}
                        <div className="annotation-actions">
                            {selected.status !== 'resolved' && (
                                <button
                                    type="button"
                                    className="annotation-btn"
                                    onClick={() => void updateStatus(selected.id, 'resolved')}
                                    disabled={busy}
                                    title="Mark this annotation as resolved"
                                >
                                    Resolve
                                </button>
                            )}
                            {selected.status === 'resolved' && (
                                <button
                                    type="button"
                                    className="annotation-btn"
                                    onClick={() => void updateStatus(selected.id, 'open')}
                                    disabled={busy}
                                    title="Reopen this annotation"
                                >
                                    Reopen
                                </button>
                            )}
                            <button
                                type="button"
                                className="annotation-btn"
                                onClick={() => void updateStatus(selected.id, 'archived')}
                                disabled={busy}
                                title="Archive this annotation"
                            >
                                Archive
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <div className="annotation-status">
                {message || (enabled ? 'Click anywhere in the app surface to add annotation.' : 'Annotations ready.')}
            </div>
        </div>
    );
}

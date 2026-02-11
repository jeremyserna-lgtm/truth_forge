// Genesis Console — Hooks (REAL — connected to backend API)
import { useState, useEffect, useCallback } from 'react';
import { apiFetch, getJson } from './api';

/**
 * Hook to check backend + Ollama status.
 */
export function useOllamaStatus(pollInterval = 10000) {
    const [status, setStatus] = useState({
        connected: false,
        models: [],
        error: null,
        lastChecked: null,
        stats: null,
    });

    const check = useCallback(async () => {
        try {
            const data = await getJson('/api/health', { timeoutMs: 5000 });
            setStatus({
                connected: data.ollama?.connected || false,
                models: data.ollama?.models || [],
                error: null,
                lastChecked: new Date(),
                stats: data.stats || null,
                backendUp: true,
            });
        } catch (err) {
            setStatus(prev => ({
                ...prev,
                connected: false,
                backendUp: false,
                error: err.message,
                lastChecked: new Date(),
            }));
        }
    }, []);

    useEffect(() => {
        check();
        const interval = setInterval(check, pollInterval);
        return () => clearInterval(interval);
    }, [check, pollInterval]);

    return { ...status, refresh: check };
}

/**
 * Hook for the system event log — pulls from real backend log.
 */
export function useSystemLog(maxEntries = 100) {
    const [log, setLog] = useState([]);

    const addLog = useCallback((msg, level = 'info') => {
        const ts = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
        setLog(prev => [...prev.slice(-(maxEntries - 1)), { ts, msg, level, id: Date.now() }]);
    }, [maxEntries]);

    // Also pull server-side log periodically
    const refreshLog = useCallback(async () => {
        try {
            const serverLog = await getJson('/api/log?limit=20', { timeoutMs: 6000 });
            // Server log entries are appended but don't replace local ones
            const serverEntries = serverLog.map(entry => ({
                ts: entry._ts ? new Date(entry._ts).toLocaleTimeString('en-US', {
                    hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
                }) : '??:??:??',
                msg: entry.msg,
                level: entry.level,
                id: entry._ts,
                server: true,
            }));
            setLog(prev => {
                const localOnly = prev.filter(e => !e.server);
                return [...localOnly, ...serverEntries].slice(-maxEntries);
            });
        } catch { /* backend offline */ }
    }, [maxEntries]);

    useEffect(() => {
        const initial = setTimeout(() => {
            void refreshLog();
        }, 0);
        const interval = setInterval(refreshLog, 5000);
        return () => {
            clearTimeout(initial);
            clearInterval(interval);
        };
    }, [refreshLog]);

    const clearLog = useCallback(() => setLog([]), []);

    return { log, addLog, clearLog, refreshLog };
}

/**
 * Hook for the REAL pipeline — sends files to backend, gets atoms back.
 */
export function usePipeline(addLog) {
    const [processing, setProcessing] = useState(false);
    const [currentStage, setCurrentStage] = useState(-1);
    const [completedStages, setCompletedStages] = useState(new Set());
    const [atoms, setAtoms] = useState([]);
    const [activeModels, setActiveModels] = useState(new Set());
    const [totalAtoms, setTotalAtoms] = useState(0);
    const [saturation, setSaturation] = useState(0);
    const [cascadeCycle, setCascadeCycle] = useState(0);
    const [error, setError] = useState(null);

    // Load existing atoms on mount
    useEffect(() => {
        loadAtoms();
    }, []);

    const loadAtoms = async () => {
        try {
            const data = await getJson('/api/atoms?limit=50', { timeoutMs: 7000 });
            const mapped = (data.atoms || []).map(a => ({
                id: a.id,
                type: a.type,
                text: a.content,
                conf: a.confidence,
                ts: a._ts ? new Date(a._ts).toLocaleTimeString('en-US', { hour12: false }) : '',
                entities: a.entities,
                themes: a.themes,
            }));
            setAtoms(mapped);
            setTotalAtoms(data.total || mapped.length);
        } catch { /* backend offline */ }
    };

    const runPipeline = useCallback(async (files) => {
        if (files.length === 0 || processing) return;

        setProcessing(true);
        setError(null);
        setCompletedStages(new Set());
        setCurrentStage(0);

        addLog('Pipeline initiated — HOLD₁ engaged');

        // Stage 0: INTAKE
        setActiveModels(new Set());
        addLog(`Intake: ${files.length} file(s) classified`);
        files.forEach(f => addLog(`  → ${f.name} (${(f.size / 1024).toFixed(1)}KB)`));

        await sleep(400);
        setCompletedStages(new Set([0]));

        // Stage 1: ATOMIZE — Send to real Scout
        setCurrentStage(1);
        setActiveModels(new Set(['scout']));
        addLog('Stage: ATOMIZE — Sending to Scout...');

        try {
            const formData = new FormData();
            files.forEach(f => formData.append('files', f));

            const res = await apiFetch('/api/atomize', {
                method: 'POST',
                body: formData,
            }, 60000);

            if (!res.ok) {
                const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
                throw new Error(err.error || `Server error ${res.status}`);
            }

            const data = await res.json();
            setCompletedStages(new Set([0, 1]));

            // Display results
            const newAtoms = [];
            const resultErrors = [];
            for (const result of (data.results || [])) {
                if (result.error) {
                    addLog(`Error: ${result.filename} — ${result.error}`, 'error');
                    resultErrors.push({ filename: result.filename, error: result.error });
                    continue;
                }

                addLog(`${result.atoms?.length || 0} atoms from ${result.filename} (${result.model}, ${result.elapsed_ms}ms)`, 'success');

                for (const atom of (result.atoms || [])) {
                    newAtoms.push({
                        id: atom.id,
                        type: atom.type,
                        text: atom.content,
                        conf: atom.confidence,
                        ts: new Date().toLocaleTimeString('en-US', { hour12: false }),
                        entities: atom.entities,
                        themes: atom.themes,
                    });
                }
            }

            if (newAtoms.length === 0 && resultErrors.length > 0) {
                const details = resultErrors.map((item) => `${item.filename}: ${item.error}`).join(' | ');
                setError(`No atoms extracted. ${details}`);
                setCurrentStage(-1);
                setActiveModels(new Set());
                addLog(`Pipeline halted: ${details}`, 'error');
                setProcessing(false);
                return;
            }

            setAtoms(prev => [...newAtoms, ...prev].slice(0, 100));
            setTotalAtoms(data.stats?.totalAtoms || newAtoms.length);
            setCascadeCycle(prev => prev + 1);
            setSaturation(prev => Math.min(0.95, prev + 0.15));

            // Mark remaining stages as complete (compound/synthesize/forge/podcast are future)
            await sleep(300);
            setCurrentStage(2);
            addLog('Stage: COMPOUND — (ready for Phase 3)');
            await sleep(300);
            setCompletedStages(new Set([0, 1, 2, 3, 4, 5]));
            setCurrentStage(-1);
            setActiveModels(new Set());
            addLog(`Pipeline complete — ${data.totalAtoms} atoms extracted and stored to disk`, 'success');

        } catch (err) {
            setError(err.message);
            addLog(`Pipeline error: ${err.message}`, 'error');
            setCurrentStage(-1);
            setActiveModels(new Set());
        }

        setProcessing(false);
    }, [processing, addLog]);

    const cancelPipeline = useCallback(() => {
        setProcessing(false);
        setCurrentStage(-1);
        setActiveModels(new Set());
        addLog('Pipeline cancelled', 'warn');
    }, [addLog]);

    return {
        processing,
        currentStage,
        completedStages,
        atoms,
        activeModels,
        totalAtoms,
        saturation,
        cascadeCycle,
        error,
        runPipeline,
        cancelPipeline,
        loadAtoms,
    };
}

/**
 * Hook for tracking ANIMA memory engine states.
 */
export function useAnimaMemory() {
    const [engines, setEngines] = useState([
        { id: 'somatic', label: 'SOMATIC', desc: 'Physical State', fill: 0.45 },
        { id: 'symbolic', label: 'SYMBOLIC', desc: 'Language & Metaphor', fill: 0.62 },
        { id: 'narrative', label: 'NARRATIVE', desc: 'Timeline & Story', fill: 0.78 },
        { id: 'relational', label: 'RELATIONAL', desc: 'Bonds & Trust', fill: 0.33 },
        { id: 'strategic', label: 'STRATEGIC', desc: 'Goals & Plans', fill: 0.55 },
    ]);

    const updateEngines = useCallback((fn) => {
        setEngines(prev => prev.map(fn));
    }, []);

    const nudge = useCallback(() => {
        setEngines(prev => prev.map(e => ({
            ...e,
            fill: Math.min(0.98, e.fill + Math.random() * 0.04),
        })));
    }, []);

    return { engines, updateEngines, nudge };
}

/**
 * Hook for system uptime tracking.
 */
export function useUptime() {
    const [startTime] = useState(() => Date.now());
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setElapsed(Date.now() - startTime);
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime]);

    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const DEFAULT_API_PORT = '3141';

function trimTrailingSlash(value) {
    return String(value || '').replace(/\/+$/, '');
}

function unique(values) {
    return [...new Set(values.filter(Boolean))];
}

function resolveConfiguredBase() {
    const fromEnv = trimTrailingSlash(import.meta.env?.VITE_API_URL || '');
    return fromEnv || null;
}

function localHostCandidates() {
    const hosts = [];
    if (typeof window !== 'undefined') {
        const host = window.location.hostname;
        if (host) hosts.push(host);
    }
    hosts.push('127.0.0.1', 'localhost');
    return unique(hosts);
}

function buildApiCandidates(path) {
    if (!path) return [];
    if (/^https?:\/\//i.test(path)) return [path];
    if (!path.startsWith('/api')) return [path];

    const configured = resolveConfiguredBase();
    if (configured) return [`${configured}${path}`];

    const candidates = [];
    const isFileContext = typeof window !== 'undefined' && window.location.protocol === 'file:';
    const isSameApiPort = typeof window !== 'undefined' && window.location.port === DEFAULT_API_PORT;

    if (!isFileContext) {
        if (isSameApiPort) {
            candidates.push(path);
        } else if (typeof window !== 'undefined') {
            candidates.push(path);
            candidates.push(`${window.location.origin}${path}`);
        }
    }

    localHostCandidates().forEach((host) => {
        candidates.push(`http://${host}:${DEFAULT_API_PORT}${path}`);
    });

    return unique(candidates);
}

export function reportClientError(payload) {
    if (typeof window === 'undefined') return;
    const reason = String(payload?.reason || '').trim();
    if (!reason) return;
    const urls = buildApiCandidates('/api/recovery/report-error');
    urls.forEach((url) => {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: payload.source || 'client_api',
                level: payload.level || 'error',
                reason,
                context: payload.context || {},
            }),
            keepalive: true,
        }).catch(() => {
            // best effort only
        });
    });
}

async function fetchAttempt(url, options, timeoutMs) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(new Error('request_timeout')), timeoutMs);
    try {
        const res = await fetch(url, {
            ...options,
            signal: controller.signal,
        });
        return res;
    } finally {
        clearTimeout(timeout);
    }
}

function isRetryableStatus(status) {
    return status === 404 || status === 502 || status === 503 || status === 504;
}

export async function apiFetch(path, options = {}, timeoutMs = 12000) {
    const candidates = buildApiCandidates(path);
    if (!candidates.length) {
        throw new Error(`No API candidate URL could be built for "${path}"`);
    }

    let lastError = null;

    for (let index = 0; index < candidates.length; index += 1) {
        const candidate = candidates[index];
        const isLast = index === candidates.length - 1;
        try {
            const res = await fetchAttempt(candidate, options, timeoutMs);
            if (isRetryableStatus(res.status) && !isLast) {
                continue;
            }
            return res;
        } catch (error) {
            lastError = error;
            if (isLast) break;
        }
    }

    const reason = lastError?.message || 'unknown_network_error';
    if (path !== '/api/recovery/report-error') {
        reportClientError({
            source: 'client_api_fetch',
            level: 'error',
            reason: `api_fetch_failed:${path}:${reason}`,
            context: { path, reason },
        });
    }
    throw new Error(`Cannot reach Genesis API (${reason}). Ensure backend is running on http://127.0.0.1:${DEFAULT_API_PORT}`);
}

export async function getJson(path, { timeoutMs = 10000 } = {}) {
    const res = await apiFetch(path, {}, timeoutMs);
    if (!res.ok) {
        if (path !== '/api/recovery/report-error') {
            reportClientError({
                source: 'client_api_get',
                level: 'error',
                reason: `api_get_failed:${path}:${res.status}`,
                context: { path, status: res.status },
            });
        }
        throw new Error(`GET ${path} -> ${res.status}`);
    }
    return res.json();
}

export async function postJson(path, payload, { timeoutMs = 15000 } = {}) {
    const res = await apiFetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {}),
    }, timeoutMs);

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        if (path !== '/api/recovery/report-error') {
            reportClientError({
                source: 'client_api_post',
                level: 'error',
                reason: `api_post_failed:${path}:${res.status}`,
                context: { path, status: res.status },
            });
        }
        throw new Error(data.error || `${path} -> ${res.status}`);
    }
    return data;
}

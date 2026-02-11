import { reportClientError } from './api';

const INSTALLED_FLAG = '__genesisRuntimeRecoveryInstalled__';

function toMessage(value, fallback) {
    if (typeof value === 'string' && value.trim()) return value.trim();
    if (value && typeof value.message === 'string' && value.message.trim()) return value.message.trim();
    return fallback;
}

export function installRuntimeRecoveryHooks() {
    if (typeof window === 'undefined') return;
    if (window[INSTALLED_FLAG]) return;
    window[INSTALLED_FLAG] = true;

    window.addEventListener('error', (event) => {
        const reason = toMessage(event.error, toMessage(event.message, 'window_error'));
        reportClientError({
            source: 'client_window_error',
            level: 'error',
            reason: `runtime_error:${reason}`,
            context: {
                filename: event.filename || null,
                lineno: event.lineno || null,
                colno: event.colno || null,
            },
        });
    });

    window.addEventListener('unhandledrejection', (event) => {
        const reason = toMessage(event.reason, 'unhandled_promise_rejection');
        reportClientError({
            source: 'client_unhandled_rejection',
            level: 'error',
            reason: `runtime_unhandled_rejection:${reason}`,
            context: {
                type: typeof event.reason,
            },
        });
    });
}

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Request fullscreen on load
document.addEventListener('DOMContentLoaded', () => {
  document.body.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  }, { once: true });
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

/**
 * Primitive Engine Website - THE BUILDER
 *
 * MOLT LINEAGE:
 * - Source: truth_forge website (pattern)
 * - Version: 2.0.0
 * - Date: 2026-01-30
 *
 * Same chat interface, different content space.
 * Specialization LETS it happen, doesn't DEMAND it.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import Home from './pages/Home';

// Lazy load route-level components
const Chat = lazy(() => import('./pages/Chat'));
const About = lazy(() => import('./pages/About'));

// Loading fallback
function LoadingFallback() {
  return (
    <div style={{
      minHeight: '60vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#0a0a0a'
    }}>
      <div style={{
        width: '200px',
        height: '40px',
        background: '#1a1a1a',
        borderRadius: '4px'
      }}></div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route
            path="chat"
            element={
              <Suspense fallback={<LoadingFallback />}>
                <Chat />
              </Suspense>
            }
          />
          <Route
            path="about"
            element={
              <Suspense fallback={<LoadingFallback />}>
                <About />
              </Suspense>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

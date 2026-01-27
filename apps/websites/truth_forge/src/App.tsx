/**
 * Truth Forge Website - THE GENESIS
 *
 * MOLT LINEAGE:
 * - Source: New creation
 * - Version: 4.0.0
 * - Date: 2026-01-27
 *
 * Multi-page application with React Router
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import ScrollToTop from './components/ScrollToTop';
import Home from './pages/Home';

// Lazy load route-level components for code splitting
const Vision = lazy(() => import('./pages/Vision'));
const Framework = lazy(() => import('./pages/Framework'));
const PrivacyDeployments = lazy(() => import('./pages/PrivacyDeployments'));
const PreOrder = lazy(() => import('./pages/PreOrder'));
const About = lazy(() => import('./pages/About'));
const Resources = lazy(() => import('./pages/Resources'));
const Science = lazy(() => import('./pages/Science'));
const NotMe = lazy(() => import('./pages/NotMe'));

// Loading fallback component
function LoadingFallback() {
  return (
    <div style={{ 
      minHeight: '60vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'var(--black)'
    }}>
      <div className="skeleton skeleton-title" style={{ width: '200px', height: '40px' }}></div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route 
            path="not-me" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <NotMe />
              </Suspense>
            } 
          />
          <Route 
            path="vision" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <Vision />
              </Suspense>
            } 
          />
          <Route 
            path="framework" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <Framework />
              </Suspense>
            } 
          />
          <Route 
            path="privacy-deployments" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <PrivacyDeployments />
              </Suspense>
            } 
          />
          <Route 
            path="preorder" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <PreOrder />
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
          <Route 
            path="resources" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <Resources />
              </Suspense>
            } 
          />
          <Route 
            path="science" 
            element={
              <Suspense fallback={<LoadingFallback />}>
                <Science />
              </Suspense>
            } 
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

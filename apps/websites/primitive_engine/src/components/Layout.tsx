/**
 * Layout Component for Primitive Engine
 *
 * THE BUILDER - common layout with navigation
 */

import { Link, Outlet, useLocation } from 'react-router-dom';
import '../index.css';

export default function Layout() {
  const location = useLocation();

  return (
    <div className="layout">
      <header className="site-header">
        <nav className="nav-container">
          <Link to="/" className="logo">
            <span className="logo-text">Primitive Engine</span>
            <span className="logo-subtitle">THE BUILDER</span>
          </Link>
          <div className="nav-links">
            <Link
              to="/"
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Home
            </Link>
            <Link
              to="/chat"
              className={`nav-link ${location.pathname === '/chat' ? 'active' : ''}`}
            >
              Chat
            </Link>
            <Link
              to="/about"
              className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
            >
              About
            </Link>
          </div>
        </nav>
      </header>

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="footer-content">
          <p>Primitive Engine LLC - A Truth Forge organism</p>
          <p className="footer-tagline">Build. Spawn. Deploy.</p>
        </div>
      </footer>
    </div>
  );
}

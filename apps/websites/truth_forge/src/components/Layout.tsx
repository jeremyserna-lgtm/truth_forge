import { Link, Outlet, useLocation } from 'react-router-dom';
import ScrollProgress from './ScrollProgress';

export default function Layout() {
  const location = useLocation();

  const navLinks = [
    { path: '/about', label: 'About' },
    { path: '/framework', label: 'Framework' },
    { path: '/not-me', label: 'Not-Me' },
    { path: '/science', label: 'Science' },
    { path: '/resources', label: 'Resources' },
  ];

  return (
    <div className="app">
      <ScrollProgress />
      <nav className="main-nav" role="navigation" aria-label="Main navigation">
        <div className="nav-container">
          <Link to="/" className="nav-brand">Truth Forge</Link>
          <div className="nav-links">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <Link to="/preorder" className="nav-cta">Preorder</Link>
        </div>
      </nav>

      <main role="main">
        <Outlet />
      </main>

      <footer role="contentinfo">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3 className="footer-title">TRUTH ENGINE FAMILY</h3>
              <div className="footer-links">
                <a href="https://truth-engine.ai" target="_blank" rel="noopener noreferrer">Truth Engine</a>
                <a href="https://primitive-engine.ai" target="_blank" rel="noopener noreferrer">Primitive Engine</a>
                <a href="https://credential-atlas.ai" target="_blank" rel="noopener noreferrer">Credential Atlas</a>
                <a href="https://stage5mind.com" target="_blank" rel="noopener noreferrer">Stage 5 Mind</a>
              </div>
            </div>
            
            <div className="footer-section">
              <h3 className="footer-title">NAVIGATION</h3>
              <div className="footer-links">
                <Link to="/about">About</Link>
                <Link to="/framework">Framework</Link>
                <Link to="/not-me">Not-Me</Link>
                <Link to="/science">Science</Link>
                <Link to="/vision">Vision</Link>
                <Link to="/privacy-deployments">Privacy</Link>
              </div>
            </div>
            
            <div className="footer-section">
              <h3 className="footer-title">RESOURCES</h3>
              <div className="footer-links">
                <Link to="/resources">Documentation</Link>
                <a href="/docs/research/library" target="_blank" rel="noopener noreferrer">Research Library</a>
                <a href="/docs/technical" target="_blank" rel="noopener noreferrer">Technical Docs</a>
              </div>
            </div>
            
            <div className="footer-section">
              <h3 className="footer-title">CONNECT</h3>
              <div className="footer-links">
                <a href="mailto:hello@truth-forge.ai">Email</a>
                <a href="https://linkedin.com/company/truth-forge" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                <Link to="/preorder">Contact</Link>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p className="footer-brand">Truth Forge</p>
            <p className="footer-tagline">The Source of All Systems</p>
            <p className="footer-copyright">© 2026 Truth Engine LLC. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/**
 * Home Page for Primitive Engine
 *
 * THE BUILDER - Custom Engagement
 * Focus on pilot weeks and consulting to build custom systems.
 * Not self-service. Not templates. Human engagement.
 */

import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="page home-page">
      {/* Hero Section */}
      <section className="hero">
        <h1>We Build Your System</h1>
        <p className="hero-tagline">
          Pilot weeks. Custom architecture. Your infrastructure, built right.
        </p>
        <Link to="/chat" className="cta-button">Start a Conversation</Link>
      </section>

      {/* What We Do */}
      <section className="offering-section">
        <h2>How It Works</h2>
        <div className="process-grid">
          <div className="process-card">
            <div className="process-number">1</div>
            <h3>Assessment</h3>
            <p>
              We talk. You describe what you're trying to do. We identify
              what needs to be built and what already exists.
            </p>
          </div>
          <div className="process-card">
            <div className="process-number">2</div>
            <h3>Pilot Week</h3>
            <p>
              One week. Intensive build. We create the core primitive that
              does the thing you need. You watch it work.
            </p>
          </div>
          <div className="process-card">
            <div className="process-number">3</div>
            <h3>Deployment</h3>
            <p>
              It runs in your environment. Your data. Your control.
              We hand it over and you own it.
            </p>
          </div>
          <div className="process-card">
            <div className="process-number">4</div>
            <h3>Stewardship</h3>
            <p>
              Optional ongoing relationship. We evolve it as you need.
              Or you take it from here.
            </p>
          </div>
        </div>
      </section>

      {/* What Gets Built */}
      <section className="builds-section">
        <h2>What We Build</h2>
        <div className="builds-grid">
          <div className="build-card">
            <h3>Data Pipelines</h3>
            <p>
              Your data, flowing where it needs to go. Extraction, transformation,
              loading. Real-time or batch. We build the plumbing.
            </p>
          </div>
          <div className="build-card">
            <h3>AI Integration</h3>
            <p>
              Models that work for you. Not generic chatbots - systems that
              understand your domain, your data, your workflow.
            </p>
          </div>
          <div className="build-card">
            <h3>Automation</h3>
            <p>
              The things you do repeatedly, done automatically. Triggered by
              time, events, or conditions you define.
            </p>
          </div>
          <div className="build-card">
            <h3>Custom Systems</h3>
            <p>
              When it doesn't fit a category. We figure out what it needs
              to be and build that.
            </p>
          </div>
        </div>
      </section>

      {/* The Pattern */}
      <section className="pattern-section">
        <h2>Built on THE PATTERN</h2>
        <div className="pattern-visual">
          <div className="pattern-node">
            <span className="node-label">Your Data</span>
          </div>
          <span className="pattern-arrow">→</span>
          <div className="pattern-node agent">
            <span className="node-label">Your System</span>
          </div>
          <span className="pattern-arrow">→</span>
          <div className="pattern-node">
            <span className="node-label">Your Output</span>
          </div>
        </div>
        <p className="pattern-explanation">
          Every system we build follows the same architecture.
          Input → Processing → Output. Composable. Debuggable. Yours.
        </p>
      </section>

      {/* Engagement Options */}
      <section className="engagement-section">
        <h2>Engagement Options</h2>
        <div className="engagement-grid">
          <div className="engagement-card">
            <h3>Pilot Week</h3>
            <p className="engagement-price">$5,000 - $15,000</p>
            <p>
              One week intensive. We build the core system. You get working
              infrastructure at the end.
            </p>
            <ul>
              <li>Assessment call</li>
              <li>5-day build</li>
              <li>Documentation</li>
              <li>Deployment support</li>
            </ul>
          </div>
          <div className="engagement-card featured">
            <h3>Stewardship</h3>
            <p className="engagement-price">$2,000/month</p>
            <p>
              Ongoing relationship. We evolve the system as your needs change.
              Priority support. Regular check-ins.
            </p>
            <ul>
              <li>Monthly evolution</li>
              <li>Priority support</li>
              <li>Quarterly review</li>
              <li>New feature builds</li>
            </ul>
          </div>
          <div className="engagement-card">
            <h3>Custom Project</h3>
            <p className="engagement-price">Scoped</p>
            <p>
              Larger builds that need more than a week. We scope it, price it,
              build it. Fixed price, fixed timeline.
            </p>
            <ul>
              <li>Discovery phase</li>
              <li>Fixed scope contract</li>
              <li>Milestone delivery</li>
              <li>Full documentation</li>
            </ul>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2>Ready to Build?</h2>
        <p>
          Start with a conversation. We'll figure out what you need
          and whether we're the right fit.
        </p>
        <Link to="/chat" className="cta-button">Start Conversation</Link>
      </section>
    </div>
  );
}

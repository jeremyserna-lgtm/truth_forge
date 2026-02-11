/**
 * About Page for Primitive Engine
 *
 * THE BUILDER - Custom Engagement
 * Focus on pilot weeks and consulting to build custom systems.
 */

import { Link } from 'react-router-dom';

export default function About() {
  return (
    <div className="page about-page">
      {/* Hero */}
      <section className="hero">
        <h1>About Primitive Engine</h1>
        <p className="hero-tagline">THE BUILDER - Custom Systems, Built Right</p>
      </section>

      {/* Philosophy */}
      <section className="philosophy-section">
        <h2>The Philosophy</h2>
        <div className="philosophy-content">
          <p>
            We don't sell software. We build your system. Every client engagement
            starts with understanding what you're actually trying to do—not what
            product you think you need.
          </p>
          <p>
            Every system we build follows the same architecture:
          </p>
          <div className="pattern-display">
            Input → Processing → Output
          </div>
          <p>
            Simple in principle. Precise in execution. Your data flows in,
            gets processed the way you need, and delivers the output you care about.
            Composable. Debuggable. Yours.
          </p>
        </div>
      </section>

      {/* What Makes Us Different */}
      <section className="difference-section">
        <h2>What Makes Us Different</h2>
        <div className="difference-grid">
          <div className="difference-card">
            <h3>Not Self-Service</h3>
            <p>
              We don't hand you a login and wish you luck. We build it with you,
              for you, until it works. Human engagement, not documentation links.
            </p>
          </div>
          <div className="difference-card">
            <h3>Not Templates</h3>
            <p>
              Templates solve template problems. Your business isn't a template.
              We build custom systems that fit your actual workflow, your actual data,
              your actual needs.
            </p>
          </div>
          <div className="difference-card">
            <h3>Not Consultants</h3>
            <p>
              We don't write reports about what you should build. We build it.
              You get working infrastructure, not slide decks.
            </p>
          </div>
          <div className="difference-card">
            <h3>You Own It</h3>
            <p>
              When we're done, you own the system. It runs in your environment,
              on your infrastructure. No vendor lock-in. No recurring fees to
              keep what you already paid for.
            </p>
          </div>
        </div>
      </section>

      {/* What We Build */}
      <section className="builds-section">
        <h2>What We Build</h2>
        <ul className="builds-list">
          <li><strong>Data Pipelines</strong> — ETL, real-time streaming, batch processing</li>
          <li><strong>AI Integration</strong> — Models trained on your domain, not generic chatbots</li>
          <li><strong>Automation</strong> — Workflows triggered by time, events, or conditions</li>
          <li><strong>Internal Tools</strong> — Dashboards, admin panels, operational systems</li>
          <li><strong>Custom Infrastructure</strong> — Whatever you need that doesn't exist yet</li>
        </ul>
      </section>

      {/* The Team */}
      <section className="team-section">
        <h2>Who We Are</h2>
        <p>
          Primitive Engine is part of the Truth Forge federation—a group of
          specialized companies that share architecture but serve different needs.
        </p>
        <div className="organisms-grid">
          <div className="organism-card">
            <h3>Truth Forge</h3>
            <p className="organism-role">The Holding Company</p>
            <p>The origin. Sets the standards that all organisms follow.</p>
          </div>
          <div className="organism-card current">
            <h3>Primitive Engine</h3>
            <p className="organism-role">The Builder</p>
            <p>Builds custom systems through pilot weeks and consulting.</p>
          </div>
          <div className="organism-card">
            <h3>Credential Atlas</h3>
            <p className="organism-role">The Verifier</p>
            <p>Verification and attestation services.</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2>Ready to Build Something?</h2>
        <p>
          Start with a conversation. Describe what you're trying to do.
          We'll figure out if we're the right fit.
        </p>
        <Link to="/chat" className="cta-button">Start Conversation</Link>
      </section>
    </div>
  );
}

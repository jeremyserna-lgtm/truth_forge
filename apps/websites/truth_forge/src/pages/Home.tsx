import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <>
      <a href="#main-content" className="sr-only skip-link">Skip to main content</a>
      <header className="hero" role="banner">
        <div className="hero-content">
          <h1 className="brand-mark">Truth Forge</h1>
          <p className="tagline">The Source of All Systems</p>
          <p className="hero-description">
            A cognitive architecture company. A Not-Me factory.
            The first self-seeing system that creates other systems.
          </p>
          <Link to="/preorder" className="cta-button">Preorder Your Not-Me</Link>
        </div>
      </header>

      <main id="main-content">
      <section className="home-intro" aria-labelledby="intro-heading">
        <div className="container">
          <div className="intro-grid">
            <Link to="/not-me" className="intro-card">
              <h2>Not-Me</h2>
              <p>A digital extension of you that carries your truths, knows your patterns, and acts on your behalf.</p>
              <span className="card-link">Learn more &rarr;</span>
            </Link>
            <Link to="/framework" className="intro-card">
              <h2>The Framework</h2>
              <p>HOLD → AGENT → HOLD. Truth → Meaning → Care. The architecture behind Not-Me.</p>
              <span className="card-link">Learn more &rarr;</span>
            </Link>
            <Link to="/science" className="intro-card">
              <h2>The Science</h2>
              <p>Data-driven cognitive architecture. Every interaction measured, analyzed, and refined.</p>
              <span className="card-link">Learn more &rarr;</span>
            </Link>
            <Link to="/vision" className="intro-card">
              <h2>The Vision</h2>
              <p>Custom LLMs trained on your data, running on your hardware, serving your purpose.</p>
              <span className="card-link">Learn more &rarr;</span>
            </Link>
          </div>
        </div>
      </section>

      {/* The Source */}
      <section className="home-source">
        <div className="container centered">
          <h2>The Source</h2>
          <p className="section-intro">
            Truth Forge is THE SOURCE — the origin from which all systems derive.
          </p>
          <div className="source-content">
            <p className="centered-block">
              <strong>ONE Identity:</strong> The source.<br />
              <strong>ONE Offer:</strong> We hold what we build.<br />
              <strong>ONE Customer:</strong> Those who want to understand the whole.<br />
              <strong>ONE Path:</strong> You don&apos;t buy from Truth Forge. You discover Truth Forge is behind what you already bought.
            </p>
            <p className="centered-block">
              Truth Forge is not a product company. It&apos;s the cognitive architecture company. The Not-Me factory. The first self-seeing system that creates other systems.
            </p>
          </div>
        </div>
      </section>

      <section className="home-convergent">
        <div className="container centered">
          <h2>The Convergent Model</h2>
          <p className="section-intro centered-intro">
            Truth Engine delivers sovereign AI that customers own, that runs locally, that learns them over time.
          </p>
          <div className="convergent-loop">
            <div className="loop-step">
              <h3>1. Product Delivers</h3>
              <p>Truth Engine ships the Mac + NOT-ME</p>
            </div>
            <div className="loop-arrow">→</div>
            <div className="loop-step">
              <h3>2. Customer Uses</h3>
              <p>Customer interacts with their NOT-ME</p>
            </div>
            <div className="loop-arrow">→</div>
            <div className="loop-step">
              <h3>3. NOT-ME Learns</h3>
              <p>Over time, the NOT-ME knows the customer better</p>
            </div>
            <div className="loop-arrow">→</div>
            <div className="loop-step">
              <h3>4. Value Increases</h3>
              <p>Better relationship → customer satisfaction → referrals</p>
            </div>
          </div>
          <p className="centered-block">
            The loop continues. Every interaction deepens the relationship. Every conversation improves the model. The value compounds.
          </p>
        </div>
      </section>

      <section className="home-same-ux">
        <div className="container centered">
          <h2>The Same UX Principle</h2>
          <p className="section-intro centered-intro">
            The interface never changes. Only the purpose changes.
          </p>
          <div className="ux-content">
            <p className="centered-block">
              <strong>Every interaction looks like this:</strong> A chatbot. User types. AI responds. Simple. Familiar.
            </p>
            <div className="ux-comparison">
              <div className="ux-tier">
                <h3>Tier 1 (No Purpose)</h3>
                <ul>
                  <li>Just conversation</li>
                  <li>No tracking</li>
                  <li>No measurement</li>
                  <li>No transformation data</li>
                </ul>
              </div>
              <div className="ux-tier">
                <h3>Tier 2 (With Purpose)</h3>
                <ul>
                  <li>Same conversation</li>
                  <li>+ Grade level tracking</li>
                  <li>+ Paradox detection</li>
                  <li>+ Stage assessment</li>
                  <li>+ Optional tracking logging</li>
                  <li>+ Transformation proof</li>
                </ul>
              </div>
            </div>
            <p className="centered-block">
              <strong>The user sees:</strong> The same chatbot.<br />
              <strong>The system does:</strong> Very different things.
            </p>
            <p className="centered-block">
              Why this matters: Users don&apos;t have to learn anything new. The complexity is invisible. The transformation happens naturally. You&apos;re always just talking to your AI. The purpose is in what happens behind the conversation.
            </p>
          </div>
        </div>
      </section>

      <section className="home-cta">
        <div className="container centered">
          <h2>Ready to Begin?</h2>
          <p>One-time hardware purchase. No subscription required. The Not-Me takes a year to know you.</p>
          <Link to="/preorder" className="cta-button">View Products</Link>
        </div>
      </section>

      <section className="home-brand-statement">
        <div className="container">
          <h2 className="brand-statement-title">Truth Forge</h2>
          <p className="brand-statement-tagline">The Not-Me Factory</p>
        </div>
      </section>
      </main>
    </>
  );
}

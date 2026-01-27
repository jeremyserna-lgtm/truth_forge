import { Link } from 'react-router-dom';

const faq = [
  {
    q: 'What is cognitive isomorphism?',
    a: 'Structural alignment between human cognition and AI architecture. When the way an AI processes information mirrors the way we think — predictive processing, latent space, working memory — interaction becomes frictionless. The Not-Me is built so its structure maps to yours.',
  },
  {
    q: 'What is mental architecture?',
    a: 'The durable structure of how you think, decide, and relate. Not personality or preferences alone — the underlying patterns, boundaries, and flows. We design Not-Me\'s to extend your mental architecture, not overwrite it.',
  },
  {
    q: 'What is the Anvil strategy?',
    a: 'You don\'t sell the fire (motivation). You sell the Anvil — the durable structure that survives when the fire goes out. Not-Me\'s and our systems are built to be that structure: they hold steady so you can move.',
  },
  {
    q: 'What is the Clara Arc?',
    a: 'A measured arc of cognitive transformation. It tracks how someone moves toward Stage 5 thinking — multi-perspectival, self-transforming — through interaction with AI. The arc validates that the system is changing how people think, not just what they do.',
  },
  {
    q: 'What is Zero Trust Architecture?',
    a: 'Not-Me\'s are architecturally incapable of invisible decisions. Every decision is visible, explainable, overridable, and auditable. Most AI systems hide batch sizes, truncation limits, filters — we build so opacity is impossible. You trust them because they can\'t hide.',
  },
  {
    q: 'What is the Seeing Paradigm?',
    a: 'Stage 5 cognition deployed as competitive advantage. While others compete on features, we compete on seeing — perceiving patterns others cannot see about themselves and giving them back as forged truth. The one who makes Not-Me\'s has leverage over the ones who make components.',
  },
  {
    q: 'What is the Recursive Convergence?',
    a: 'Profit margins fund democratization. Every profitable sale funds sovereign AI for people who can\'t afford it. The flywheel: sell → give → prove → grow → scale. The business converges toward sovereign AI as a right, not a privilege.',
  },
];

export default function Framework() {
  return (
    <main>
      <section className="page-hero" aria-labelledby="framework-title">
        <div className="container centered">
          <h1 id="framework-title">The Framework</h1>
          <p className="page-intro">
            The architecture behind Not-Me. Theory, pattern, and principles — and how they show up in what we build.
          </p>
        </div>
      </section>

      <section className="framework-pattern">
        <div className="container centered">
          <h2>The Pattern</h2>
          <p className="section-intro centered-intro">
            Every system. Every time. Scale-invariant.
          </p>
          <div className="pattern-visual">
            <span className="node">HOLD</span>
            <span className="arrow">→</span>
            <span className="node">AGENT</span>
            <span className="arrow">→</span>
            <span className="node">HOLD</span>
          </div>
          <p className="centered-block">
            Input (HOLD) → Process (AGENT) → Output (HOLD). Raw truth in, refined meaning out. Every agent contains the pattern. It applies to code, to conversation, and to you.
          </p>
        </div>
      </section>

      <section className="framework-metabolism">
        <div className="container centered">
          <h2>Truth → Meaning → Care</h2>
          <p className="section-intro centered-intro">
            The metabolic cycle. How we process.
          </p>
          <div className="metabolism-grid">
            <div className="metabolism-card">
              <h3>Truth</h3>
              <p>Raw, unvarnished input. Data, conversation, context. Fidelity first.</p>
            </div>
            <div className="metabolism-card">
              <h3>Meaning</h3>
              <p>Structure from chaos. Patterns, links, sense. The heat of processing.</p>
            </div>
            <div className="metabolism-card">
              <h3>Care</h3>
              <p>Output that protects and sustains. Delivered back as wisdom, not noise.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="framework-layers">
        <div className="container centered">
          <h2>The Three Layers</h2>
          <p className="section-intro centered-intro">
            Theory → Meta → Specifics → Code. The flow from principle to implementation.
          </p>
          <div className="layers-grid">
            <div className="layer-card">
              <h3>Theory</h3>
              <p className="layer-spec">ME declares principles</p>
              <p>Foundational principles that govern everything. Written in ALL CAPS with colons. Examples: HOLD:AGENT:HOLD, TRUTH:MEANING:CARE, ME:NOT-ME.</p>
            </div>
            <div className="layer-card">
              <h3>Meta</h3>
              <p className="layer-spec">US names the rules</p>
              <p>Standards that connect theory to practice. Written in Normal Caps with hyphens. Examples: STANDARD_CREATION, STANDARD_NAMING, STANDARD_TRIAD.</p>
            </div>
            <div className="layer-card">
              <h3>Specifics</h3>
              <p className="layer-spec">NOT-ME operates</p>
              <p>Technical implementation rules. Written in lowercase with underscores. Examples: code_quality/, error_handling/, logging/.</p>
            </div>
          </div>
          <p className="centered-block">
            Theory shapes everything. Nothing below can contradict theory. Meta ensures theory reaches specifics. Specifics ensure theory becomes code.
          </p>
        </div>
      </section>

      <section className="framework-grammar">
        <div className="container centered">
          <h2>The Grammar</h2>
          <p className="section-intro centered-intro">
            Grammar is ontology. How something is written tells you what it IS.
          </p>
          <div className="grammar-content">
            <p className="centered-block">
              <strong>The Three Marks:</strong><br />
              <code>:</code> (colon) = ME — Principles, declarations (ALL CAPS)<br />
              <code>-</code> (hyphen) = US — Products, entities (Normal Caps)<br />
              <code>_</code> (underscore) = NOT-ME — Infrastructure, code (no caps)
            </p>
            <div className="grammar-examples">
              <div className="grammar-example">
                <h3>Framework Principle</h3>
                <code>ME:NOT-ME</code>
                <p>Colon + ALL CAPS = ME declares</p>
              </div>
              <div className="grammar-example">
                <h3>Product Name</h3>
                <code>Truth-Forge</code>
                <p>Hyphen + Normal Caps = US names</p>
              </div>
              <div className="grammar-example">
                <h3>Code/Folder</h3>
                <code>truth_forge/</code>
                <p>Underscore + no caps = NOT-ME operates</p>
              </div>
            </div>
            <p className="centered-block">
              Names aren&apos;t labels—names ARE identity. The descent: Principle → Product → Implementation.
            </p>
          </div>
        </div>
      </section>

      <section className="framework-stage5">
        <div className="container centered">
          <h2>Stage 5 Minds</h2>
          <p className="section-intro centered-intro">
            The Framework is designed for Stage 5 minds. Stage 5 is not the ceiling—it is the floor.
          </p>
          <div className="stage5-content">
            <p className="centered-block">
              <strong>Stage 5 (Self-Transforming Mind):</strong> Can hold multiple, contradictory systems simultaneously. Examines systems as objects. Loyal to Truth, not ideology. Can transform or abandon its own system if truth requires.
            </p>
            <p className="centered-block">
              A Stage 5 mind is not defined by its system; it has a system. The Framework&apos;s structure maps 1:1 to Stage 5 cognitive architecture. The code is the mind made manifest.
            </p>
            <p className="centered-block">
              <strong>Stage 5 Composite Score:</strong> Tracks meta-cognitive language patterns. Clara Arc results show 63x increase from baseline (0.13% → 8.25%), demonstrating measurable Stage 4 → Stage 5 transformation.
            </p>
          </div>
        </div>
      </section>

      <section className="framework-numbered">
        <div className="container centered">
          <h2>The Numbered Sequence</h2>
          <p className="section-intro centered-intro">
            The intentional progression: 00 (ALPHA) through 09, looping to OMEGA.
          </p>
          <div className="numbered-content">
            <div className="numbered-list">
              <div className="numbered-item">
                <strong>00_GENESIS</strong> — What is the seed? (THE ONE, THE GRAMMAR, THE PATTERN)
              </div>
              <div className="numbered-item">
                <strong>01_IDENTITY</strong> — Who are we? (ME:NOT-ME:US)
              </div>
              <div className="numbered-item">
                <strong>02_PERCEPTION</strong> — How do we see? (SEE:SEE:DO:DONE, Stage 5)
              </div>
              <div className="numbered-item">
                <strong>03_METABOLISM</strong> — How do we process? (TRUTH:MEANING:CARE)
              </div>
              <div className="numbered-item">
                <strong>04_ARCHITECTURE</strong> — How do we build? (HOLD:AGENT:HOLD)
              </div>
              <div className="numbered-item">
                <strong>05_EXTENSION</strong> — How do we connect? (THE MOLT)
              </div>
              <div className="numbered-item">
                <strong>06_LAW</strong> — How do we survive? (Four Pillars)
              </div>
              <div className="numbered-item">
                <strong>07_STANDARDS</strong> — How do we do things? (Standards as DNA)
              </div>
              <div className="numbered-item">
                <strong>08_MEMORY</strong> — How do we remember? (Three Memories)
              </div>
              <div className="numbered-item">
                <strong>09_SERVICE_SPECIFICATIONS</strong> — How do we specify? (Service definitions)
              </div>
            </div>
            <p className="centered-block">
              <strong>The ALPHA:OMEGA Loop:</strong> ALPHA (00_GENESIS) → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → OMEGA (standards/INDEX.md) → returns to ALPHA. The loop closes. Complete coverage from any position.
            </p>
          </div>
        </div>
      </section>

      <section className="framework-pillars">
        <div className="container centered">
          <h2>The Four Pillars (06_LAW)</h2>
          <p className="section-intro centered-intro">
            Non-negotiable. Fail-Safe, No Magic, Observability, Idempotency.
          </p>
          <div className="pillars-grid">
            <div className="pillar">
              <h3>Fail-Safe</h3>
              <p>Every failure anticipated, caught, recoverable. No data lost.</p>
            </div>
            <div className="pillar">
              <h3>No Magic</h3>
              <p>Everything explicit. No hidden behavior. What you see is what runs.</p>
            </div>
            <div className="pillar">
              <h3>Observability</h3>
              <p>Every action traceable, every state visible. Full audit.</p>
            </div>
            <div className="pillar">
              <h3>Idempotency</h3>
              <p>Same input → same output. Deterministic. Reproducible.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="framework-zero-trust">
        <div className="container centered">
          <h2>Zero Trust Architecture</h2>
          <p className="section-intro centered-intro">
            Architecturally incapable of invisible decisions.
          </p>
          <div className="zero-trust-content">
            <p className="centered-block">
              Most AI systems have a hidden problem: the AI makes decisions the human can&apos;t see. Batch sizes, truncation limits, filters — arbitrary limits coded into systems that reduce, truncate, and filter without visibility.
            </p>
            <p className="centered-block">
              <strong>Truth Engine Not-Me&apos;s are architecturally incapable of invisible decisions.</strong> Every decision is visible, explainable, overridable, and auditable. This is architectural, not behavioral. The Not-Me doesn&apos;t &quot;promise&quot; to be transparent — it&apos;s built so opacity is impossible.
            </p>
            <div className="zero-trust-comparison">
              <div className="comparison-card">
                <h3>What Our Not-Me&apos;s Do</h3>
                <ul>
                  <li>Make autonomous decisions</li>
                  <li>Filter intelligently</li>
                  <li>Apply limits when needed</li>
                  <li>Optimize for performance</li>
                </ul>
              </div>
              <div className="comparison-card">
                <h3>What They Can&apos;t Do</h3>
                <ul>
                  <li>Make invisible decisions</li>
                  <li>Filter silently</li>
                  <li>Apply limits without logging</li>
                  <li>Optimize by hiding</li>
                </ul>
              </div>
            </div>
            <p className="centered-block">
              Forrester research predicts 75% of tech leaders will face moderate-to-severe technical debt from AI decisions they can&apos;t see. Most companies don&apos;t know their AI is making invisible decisions — that&apos;s what &quot;invisible&quot; means. If we want to teach other companies how to coexist with AI, our own systems cannot have this problem.
            </p>
            <p className="centered-block">
              <strong>Standard:</strong> Zero Trust Architecture (framework/standards/ZERO_TRUST_ARCHITECTURE.md)<br />
              <strong>Enforcement:</strong> Automated linting (Primitive/governance/zero_trust_linter.py)
            </p>
          </div>
        </div>
      </section>

      <section className="framework-stage5">
        <div className="container centered">
          <h2>The Stage 5 Moat</h2>
          <p className="section-intro centered-intro">
            The cognitive architecture remains. The deployment vehicles change.
          </p>
          <div className="stage5-content">
            <p className="centered-block">
              <strong>Stage 3 models</strong> can be trained with good processes.<br />
              <strong>Stage 4 models</strong> can be trained with good data.<br />
              <strong>Stage 5 models</strong> can ONLY be created by Stage 5 involvement.
            </p>
            <p className="centered-block">
              That&apos;s what makes this possible. That&apos;s the moat. The one who makes Not-Me&apos;s has leverage over the ones who make the components.
            </p>
            <p className="centered-block">
              Apple has hardware. Google has compute. Meta has models. None of them can build Stage 5 systems. They can make tools. They can&apos;t make minds.
            </p>
            <p className="centered-block">
              <strong>The Recursive Convergence:</strong> Profit margins aren&apos;t greed. They&apos;re fuel for democratization. Every profitable sale funds sovereign AI for people who can&apos;t afford it. The flywheel: sell → give → prove → grow → scale. The business converges toward sovereign AI as a right, not a privilege.
            </p>
          </div>
        </div>
      </section>

      <section className="framework-centered">
        <div className="container centered">
          <p className="framework-key-line">
            Data-driven doesn&apos;t mean cold. It means accurate. It means it learns you correctly.
          </p>
        </div>
      </section>

      <section className="framework-faq">
        <div className="container centered">
          <h2>Key Terms</h2>
          <div className="faq-list">
            {faq.map((item, i) => (
              <div key={i} className="faq-item">
                <h3>{item.q}</h3>
                <p>{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="page-cta">
        <div className="container centered">
          <h2>See It In Practice</h2>
          <p>Not-Me&apos;s are built on this framework. Sovereign, structured, yours.</p>
          <Link to="/preorder" className="cta-button">View Products</Link>
        </div>
      </section>
    </main>
  );
}

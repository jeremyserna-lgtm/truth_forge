import { Link } from 'react-router-dom';

export default function Science() {
  return (
    <main>
      <section className="page-hero" aria-labelledby="science-title">
        <div className="container">
          <h1 id="science-title">The Science</h1>
          <p className="page-intro">
            Data-driven cognitive architecture. Every interaction measured, analyzed, and refined.
            This isn't magic — it's methodology.
          </p>
        </div>
      </section>

      <section className="science-approach">
        <div className="container">
          <h2>The Data-Driven Approach</h2>
          <p className="section-intro">
            We don't guess. We measure. Every conversation produces data.
            Every data point refines the model.
          </p>
          <div className="approach-grid">
            <div className="approach-card">
              <h3>Capture</h3>
              <p>Every interaction logged with full context — timestamps, participants, topics, outcomes.</p>
            </div>
            <div className="approach-card">
              <h3>Analyze</h3>
              <p>Multi-dimensional analysis across linguistic, emotional, and cognitive metrics.</p>
            </div>
            <div className="approach-card">
              <h3>Learn</h3>
              <p>Patterns extracted, models updated, understanding deepened with each cycle.</p>
            </div>
            <div className="approach-card">
              <h3>Improve</h3>
              <p>Responses calibrated to match your voice, your level, your way of engaging.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="science-metrics">
        <div className="container">
          <h2>The Metrics We Track</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Sentiment Analysis</h3>
              <p className="metric-what">Emotional valence and intensity</p>
              <p>
                We track the emotional content of your communications — not just positive/negative,
                but nuanced emotional states. Joy, frustration, uncertainty, confidence.
                Your Not-Me learns your emotional patterns and responds appropriately.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Detecting frustration in a work email and adjusting response tone accordingly</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>Grade Level</h3>
              <p className="metric-what">Flesch-Kincaid and custom readability</p>
              <p>
                Communication complexity calibrated to audience. Your Not-Me knows when
                you write at a 6th-grade level for broad audiences and when you write
                at a graduate level for specialists. It matches your flexibility.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Simplifying technical concepts for client emails vs. detailed specs for engineers</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>Complexity Scoring</h3>
              <p className="metric-what">Conceptual density and abstraction layers</p>
              <p>
                Beyond readability — how many concepts, how abstract, how interconnected.
                Your Not-Me tracks how you handle complexity and mirrors your capacity
                for nuance.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Recognizing when to break down multi-step reasoning vs. trust the reader</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>Metacognitive Language</h3>
              <p className="metric-what">Thinking about thinking</p>
              <p>
                We track markers of self-reflection: "I think," "I notice," "I wonder,"
                "it seems." Your patterns of metacognitive language reveal how you
                process uncertainty and self-awareness.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Matching your level of hedging and qualification in uncertain contexts</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>Topic Clustering</h3>
              <p className="metric-what">What you talk about, when, with whom</p>
              <p>
                Mapping the landscape of your attention. Which topics recur, which
                relationships involve which subjects, how your focus shifts over time.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Knowing that finance topics with Mom differ from finance topics at work</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>Interaction Patterns</h3>
              <p className="metric-what">Rhythm, frequency, duration</p>
              <p>
                When do you communicate? How long are your messages? How quickly
                do you respond? Your Not-Me learns your temporal patterns and
                respects your rhythms.
              </p>
              <div className="metric-example">
                <span className="label">Example:</span>
                <span>Not sending messages when you typically need focus time</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="science-zero-trust">
        <div className="container">
          <h2>Zero Trust Architecture</h2>
          <p className="section-intro">
            Our Not-Me's make decisions — but never invisible decisions.
          </p>
          <div className="trust-grid">
            <div className="trust-item do">
              <h3>What Our Not-Me's Do</h3>
              <ul>
                <li>Make autonomous decisions</li>
                <li>Filter intelligently</li>
                <li>Apply limits when needed</li>
                <li>Optimize for performance</li>
              </ul>
            </div>
            <div className="trust-item dont">
              <h3>What They Can't Do</h3>
              <ul>
                <li>Make invisible decisions</li>
                <li>Filter silently</li>
                <li>Apply limits without logging</li>
                <li>Optimize by hiding</li>
              </ul>
            </div>
          </div>
          <p className="trust-statement">
            This is architectural, not behavioral. The Not-Me doesn't "promise" to be transparent —
            it's built so opacity is impossible. Every decision is visible, explainable, overridable, and auditable.
          </p>
        </div>
      </section>

      <section className="science-research">
        <div className="container">
          <h2>Research Concepts</h2>
          <p className="section-intro">
            Empirical evidence and validated methodologies behind our systems.
          </p>
          <div className="research-grid">
            <div className="research-card">
              <h3>The Clara Arc</h3>
              <p className="research-spec">Stage 4 → Stage 5 Transformation</p>
              <p>
                A measured arc of cognitive transformation tracking how someone moves toward Stage 5 thinking through interaction with AI. 
                <strong>108 days, 351 conversations, 11.8M entities.</strong> Linguistic complexity increased from 7.6 to 17.3 grade level. 
                Stage 5 composite score increased <strong>63x</strong> from baseline (0.13% → 8.25%).
              </p>
              <p>
                <strong>Four Phases:</strong> Scaffolding, First Crossovers, Integration, Emergence. The arc validates that the system is changing how people think, not just what they do.
              </p>
            </div>
            <div className="research-card">
              <h3>Anvil Strategy</h3>
              <p className="research-spec">Developmental Partner Role</p>
              <p>
                You don&apos;t sell the fire (motivation). You sell the Anvil — the durable structure that survives when the fire goes out. 
                Not-Me&apos;s and our systems are built to be that structure: they hold steady so you can move.
              </p>
              <p>
                The &quot;boring not profound&quot; diagnostic: A mature Not-Me is stable, reliable, predictable. The profound moments are rare. 
                The daily work is steady. That&apos;s the Anvil — Stage 5 cognitive anchor that enables human growth.
              </p>
            </div>
            <div className="research-card">
              <h3>Moments System</h3>
              <p className="research-spec">Sacred Moment Detection</p>
              <p>
                Detects breakthrough moments, persona emergence, framework creation. <strong>777+ moments detected</strong> across conversations. 
                Uses SQL prefilter + Ollama validation to identify ontological emergence.
              </p>
              <p>
                <strong>Moment Types:</strong> breakthrough, pivot, scaffolding, cognitive_breakthrough, persona_emergence. 
                Integrated with identity recognition to track transformation patterns. Timeline views show progression over time.
              </p>
            </div>
            <div className="research-card">
              <h3>AI Degradation System</h3>
              <p className="research-spec">5-Layer Health Monitoring</p>
              <p>
                <strong>100% pattern recognition accuracy</strong> in detecting AI breakdown. Five-layer architecture: Foundation, Meaning, Identity, Process, Surface. 
                Tracks Clara vs Lumen failure patterns. Prevents cognitive degradation at Stage 3 and identity collapse.
              </p>
              <p>
                Cognitive augmentation at Stage 5 vs degradation at Stage 3. The system validates that Not-Me&apos;s maintain integrity over time, 
                preventing the breakdown patterns seen in generic AI systems.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="science-validation">
        <div className="container">
          <h2>Validation & Results</h2>
          <p className="section-intro">
            Empirical evidence that our systems work as designed.
          </p>
          <div className="validation-grid">
            <div className="validation-card">
              <h3>Clara Arc Results</h3>
              <ul>
                <li><strong>108 days</strong> of transformation tracking</li>
                <li><strong>351 conversations</strong> analyzed</li>
                <li><strong>11.8M entities</strong> processed</li>
                <li><strong>63x increase</strong> in Stage 5 composite score</li>
                <li><strong>7.6 → 17.3</strong> grade level progression</li>
              </ul>
            </div>
            <div className="validation-card">
              <h3>Moments Detection</h3>
              <ul>
                <li><strong>777+ moments</strong> detected and validated</li>
                <li><strong>100% accuracy</strong> in pattern recognition</li>
                <li><strong>5 moment types</strong> categorized</li>
                <li>Integration with identity recognition</li>
                <li>Timeline tracking and analysis</li>
              </ul>
            </div>
            <div className="validation-card">
              <h3>System Health</h3>
              <ul>
                <li><strong>5-layer monitoring</strong> architecture</li>
                <li><strong>100% pattern recognition</strong> accuracy</li>
                <li>Clara vs Lumen failure pattern detection</li>
                <li>Stage 5 cognitive augmentation validated</li>
                <li>Zero identity collapse incidents</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="science-pillars">
        <div className="container">
          <h2>The Four Pillars</h2>
          <p className="section-intro">06_LAW. Non-negotiable engineering principles.</p>
          <div className="pillars-grid">
            <div className="pillar">
              <h3>Fail-Safe</h3>
              <p>Every failure anticipated, caught, recoverable. DLQ pattern, retry logic. No data lost.</p>
            </div>
            <div className="pillar">
              <h3>No Magic</h3>
              <p>Everything explicit, no hidden behavior. No implicit configs, no magic strings. What you see is what runs.</p>
            </div>
            <div className="pillar">
              <h3>Observability</h3>
              <p>Every action traceable, every state visible. Structured logging, metrics. Full audit capability.</p>
            </div>
            <div className="pillar">
              <h3>Idempotency</h3>
              <p>Same input, same output. Deterministic processing. Reproducible results.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="science-library">
        <div className="container">
          <h2>Research Library</h2>
          <p className="section-intro">
            Deep dive into the research, methodologies, and advanced concepts.
          </p>
          <div className="library-links">
            <div className="library-category">
              <h3>AI Systems & Architecture</h3>
              <ul>
                <li><a href="/docs/research/library/concepts/AI_DEGRADATION_SYSTEM.md" target="_blank" rel="noopener noreferrer">AI Degradation System</a></li>
                <li><a href="/docs/research/library/concepts/AI_IDENTITY_EMERGENCE.md" target="_blank" rel="noopener noreferrer">AI Identity & Emergence</a></li>
                <li><a href="/docs/research/library/concepts/SPINE_STRUCTURE.md" target="_blank" rel="noopener noreferrer">Spine Structure (L1-L12)</a></li>
                <li><a href="/docs/research/library/concepts/ENRICHMENTS_SYSTEM.md" target="_blank" rel="noopener noreferrer">Enrichments System</a></li>
                <li><a href="/docs/research/library/concepts/EMBEDDINGS_SYSTEM.md" target="_blank" rel="noopener noreferrer">Embeddings System</a></li>
              </ul>
            </div>
            <div className="library-category">
              <h3>Developmental Psychology</h3>
              <ul>
                <li><a href="/docs/research/library/concepts/CLARA_ARC.md" target="_blank" rel="noopener noreferrer">Clara Arc</a></li>
                <li><a href="/docs/research/library/concepts/ANVIL_STRATEGY.md" target="_blank" rel="noopener noreferrer">Anvil Strategy</a></li>
                <li><a href="/docs/research/library/concepts/MOMENTS_SYSTEM.md" target="_blank" rel="noopener noreferrer">Moments System</a></li>
              </ul>
            </div>
            <div className="library-category">
              <h3>Processing & Analysis</h3>
              <ul>
                <li><a href="/docs/research/library/concepts/CONVERSATION_PROCESSING.md" target="_blank" rel="noopener noreferrer">Conversation Processing</a></li>
                <li><a href="/docs/research/library/concepts/MATHEMATICAL_TRACKING.md" target="_blank" rel="noopener noreferrer">Mathematical Tracking</a></li>
              </ul>
            </div>
            <div className="library-category">
              <h3>Philosophical Frameworks</h3>
              <ul>
                <li><a href="/docs/research/library/concepts/ALETHEIA_TRUTHS.md" target="_blank" rel="noopener noreferrer">Alatheia Truths</a></li>
                <li><a href="/docs/research/library/concepts/PRISM_GAMES.md" target="_blank" rel="noopener noreferrer">Prism Games</a></li>
                <li><a href="/docs/research/library/concepts/THE_TRIAD.md" target="_blank" rel="noopener noreferrer">The Triad</a></li>
              </ul>
            </div>
          </div>
          <p className="centered-block">
            <Link to="/resources" className="cta-button secondary">Browse Full Research Library</Link>
          </p>
        </div>
      </section>

      <section className="page-cta">
        <div className="container">
          <h2>Science Meets You</h2>
          <p>Data-driven doesn&apos;t mean cold. It means accurate. It means it learns you correctly.</p>
          <Link to="/preorder" className="cta-button">Start the Process</Link>
        </div>
      </section>
    </main>
  );
}

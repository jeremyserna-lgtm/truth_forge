/**
 * Primitive Engine Website - THE BUILDER
 *
 * MOLT LINEAGE:
 * - Source: Truth_Engine/apps/primitive_app/ (reference)
 * - Version: 1.0.0
 * - Date: 2026-01-27
 */

function App() {
  return (
    <div className="app">
      <header>
        <h1>Primitive Engine</h1>
        <p>THE BUILDER</p>
      </header>

      <main>
        <section className="hero">
          <h2>EXIST:NOW</h2>
          <p>Build. Spawn. Deploy.</p>
        </section>

        <section className="pattern">
          <h2>THE PATTERN</h2>
          <div className="pattern-visual">
            <span>Build Request</span>
            <span className="arrow">→</span>
            <span>Primitive Builder</span>
            <span className="arrow">→</span>
            <span>Deployed Primitive</span>
          </div>
        </section>

        <section className="primitive">
          <h2>Primitive: EXIST:NOW</h2>
          <p>The Primitive Engine exists in the present, building the future.</p>
        </section>

        <section className="fertility">
          <h2>Fertility: FERTILE</h2>
          <p>Spawns children. Each primitive can become its own organism.</p>
        </section>

        <section className="features">
          <h2>Features</h2>
          <ul>
            <li><strong>Slot Builder</strong> - Visual interface for creating primitives</li>
            <li><strong>Template Library</strong> - Pre-built primitive templates</li>
            <li><strong>One-Click Deploy</strong> - Instant primitive deployment</li>
            <li><strong>Monitoring</strong> - Runtime primitive health</li>
          </ul>
        </section>

        <section className="templates">
          <h2>Template Categories</h2>
          <ul>
            <li><strong>Data Processing</strong> - ETL, transforms, aggregations</li>
            <li><strong>API Integration</strong> - REST, GraphQL, webhooks</li>
            <li><strong>AI/ML</strong> - Model inference, embeddings, RAG</li>
            <li><strong>Automation</strong> - Workflows, schedules, triggers</li>
          </ul>
        </section>

        <section className="cta">
          <a href="/builder" className="button">Start Building</a>
        </section>
      </main>

      <footer>
        <p>Primitive Engine LLC - A Truth Forge organism</p>
      </footer>
    </div>
  );
}

export default App;

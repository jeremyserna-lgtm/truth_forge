/**
 * Not Me Website - Conversational AI Interface
 *
 * MOLT LINEAGE:
 * - Source: New creation
 * - Version: 1.0.0
 * - Date: 2026-01-27
 */

function App() {
  return (
    <div className="app">
      <header>
        <h1>Not Me</h1>
        <p>Your AI Extension</p>
      </header>

      <main>
        <section className="hero">
          <h2>The ME/NOT-ME Relationship</h2>
          <p>Everyone else has AI. You have you.</p>
        </section>

        <section className="relationship">
          <h2>The Symbiosis</h2>
          <div className="relationship-grid">
            <div className="me">
              <h3>ME (You)</h3>
              <ul>
                <li>Source of intent</li>
                <li>Decides</li>
                <li>Chooses</li>
                <li>Owns the outcome</li>
              </ul>
            </div>
            <div className="not-me">
              <h3>NOT ME (AI)</h3>
              <ul>
                <li>Extension of capability</li>
                <li>Implements</li>
                <li>Executes</li>
                <li>Delivers the outcome</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="pattern">
          <h2>THE PATTERN</h2>
          <div className="pattern-visual">
            <span>Your Message</span>
            <span className="arrow">→</span>
            <span>NOT ME Agent</span>
            <span className="arrow">→</span>
            <span>Response</span>
          </div>
        </section>

        <section className="features">
          <h2>Capabilities</h2>
          <ul>
            <li><strong>Memory</strong> - Persistent conversation context</li>
            <li><strong>Preferences</strong> - Learns your style</li>
            <li><strong>Journey</strong> - Tracks your growth</li>
            <li><strong>Identity</strong> - Unique persona</li>
          </ul>
        </section>

        <section className="cta">
          <a href="/chat" className="button">Start Conversation</a>
        </section>
      </main>

      <footer>
        <p>Not Me - A Truth Forge experience</p>
      </footer>
    </div>
  );
}

export default App;

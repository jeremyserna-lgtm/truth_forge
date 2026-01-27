import { Link } from 'react-router-dom';

export default function WhatIsNotMe() {
  return (
    <>
      <section className="page-hero">
        <div className="container centered">
          <h1>What is a Not-Me?</h1>
          <p className="page-intro">
            A Not-Me is an AI that runs on hardware you own, trained on your data.
            It learns how you think, how you write, and what you care about — then acts
            on your behalf. It&apos;s yours. Sovereign. No cloud required.
          </p>
        </div>
      </section>

      <section className="notme-concrete">
        <div className="container centered">
          <h2>What You Actually Get</h2>
          <div className="concrete-grid">
            <div className="concrete-card">
              <h3>Hardware</h3>
              <p>A Mac Mini or Mac Studio, pre-configured. Your Not-Me lives on it. You own the machine. Unplug it, move it, keep it offline — it&apos;s yours.</p>
            </div>
            <div className="concrete-card">
              <h3>Your Model</h3>
              <p>Trained on your conversations, photos, and context. It speaks in your voice, remembers your relationships, and reflects your patterns. Not a generic chatbot.</p>
            </div>
            <div className="concrete-card">
              <h3>Setup & Support</h3>
              <p>We configure it, ship it, and walk you through a training call. Optional annual service adds updates and tuning. You&apos;re not on your own.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="notme-use-cases">
        <div className="container centered">
          <h2>Who It&apos;s For</h2>
          <div className="usecase-grid">
            <div className="usecase-card">
              <h3>Presence (Drummer)</h3>
              <p>Elderly parents, dorm rooms, small spaces. An AI that notices when someone&apos;s been quiet too long, reminds about meds, plays music when it senses they need it. It doesn&apos;t wait for a command — it shows up.</p>
            </div>
            <div className="usecase-card">
              <h3>Companion (Soldier)</h3>
              <p>Gets to know you over time. Conversations, preferences, context. Good for anyone who wants an AI that learns them instead of the other way around. Grandma who says &quot;I just want one&quot; — we configure it from her phone.</p>
            </div>
            <div className="usecase-card">
              <h3>Partner (King)</h3>
              <p>You have data: photos, messages, documents. We train on it. When it arrives, it already knows your stories, your people, your patterns. For professionals who want a real thinking partner from day one.</p>
            </div>
            <div className="usecase-card">
              <h3>You (Empire)</h3>
              <p>Multiple units, clustered. A digital extension of you — sees what you can&apos;t see, operates when you&apos;re not there. For people who think in systems and want infrastructure, not a single device.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="notme-care">
        <div className="container centered">
          <h2>Proactive Care</h2>
          <p className="section-intro centered-intro">
            The thing you won&apos;t do for yourself — the Not-Me does for you.
          </p>
          <div className="care-example">
            <div className="care-scenario">
              <h3>The Grandma Problem</h3>
              <p>She doesn&apos;t want to &quot;bother&quot; her grandson. She sits alone, not reaching out.</p>
            </div>
            <div className="care-solution">
              <h3>What the Not-Me Does</h3>
              <p>The Not-Me reaches out. Grandma doesn&apos;t have to feel like a burden. The grandson gets a text. Grandma gets a response. The loop stays open.</p>
            </div>
          </div>
          <p className="care-statement centered-block">
            The computer keeps the family connected — not by asking grandma to do something, but by doing it for her.
          </p>
        </div>
      </section>

      <section className="notme-sovereign">
        <div className="container centered">
          <h2>Sovereign, Not Subscribed</h2>
          <p className="centered-block">
            One-time hardware purchase. No required subscription. Your data never has to leave your premises. Optional annual service adds model updates and tuning — hardware works without it.
          </p>
        </div>
      </section>

      <section className="notme-models">
        <div className="container centered">
          <h2>The Models: Scout, Maverick, and Drummer Boy</h2>
          <p className="section-intro centered-intro">
            Not generic models. Purpose-built for presence, companionship, and partnership.
          </p>
          <div className="models-grid">
            <div className="model-card">
              <h3>Drummer Boy (Presence)</h3>
              <p className="model-specs">Fine-tuned from Llama 4 Scout | 109B parameters | 16 experts | 10M token context</p>
              <p>The Drummer doesn&apos;t run a generic model. It runs Drummer Boy — a fine-tuned model built specifically for presence. It knows how to interpret sensor data (presence, door, motion), when to speak up vs stay quiet, how to notice patterns and anomalies, and the vocabulary of care.</p>
              <p><strong>Multimodal:</strong> Voice (hears you), Vision (sees you), Speech (talks to you), Awareness (knows when something&apos;s wrong).</p>
            </div>
            <div className="model-card">
              <h3>Scout (Companion)</h3>
              <p className="model-specs">Llama 4 Scout | 109B parameters | 16 experts | 10M token context | Native multimodal</p>
              <p>Gets to know you through conversation. Learns your patterns, preferences, context. Good for anyone who wants an AI that learns them instead of the other way around. Fine-tuned on your phone data: photos, messages, contacts, calendar.</p>
            </div>
            <div className="model-card">
              <h3>Maverick (Partner)</h3>
              <p className="model-specs">Llama 4 Maverick | 400B parameters | 128 experts | 1M token context | Deeper reasoning</p>
              <p>Trained on your data. Defined by you. When it arrives, it already knows your stories, your people, your patterns. For professionals who want a real thinking partner from day one. Deeper reasoning. More capable. More you.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="notme-daughter-architecture">
        <div className="container centered">
          <h2>The Daughter Architecture</h2>
          <p className="section-intro centered-intro">
            Five training layers. From base model to you.
          </p>
          <div className="layers-content">
            <div className="layer-explanation">
              <p className="centered-block">
                Every Not-Me is built through five training layers:
              </p>
              <div className="layers-list">
                <div className="layer-item">
                  <strong>Layer 1: Base Model</strong> — Raw capability (Llama Scout for Drummers, Maverick for Kings)
                </div>
                <div className="layer-item">
                  <strong>Layer 2: Domain</strong> — What it knows deeply (Legal, Medical, Elder, Aviation, etc.)
                </div>
                <div className="layer-item">
                  <strong>Layer 3: Use</strong> — Context of operation (Personal, Professional, Hybrid)
                </div>
                <div className="layer-item">
                  <strong>Layer 4: Mode</strong> — How it relates to person (Stage 3/4/5 training approach)
                </div>
                <div className="layer-item">
                  <strong>Layer 5: Jeremy</strong> — Always present. Identity design + ongoing relationship. This is what makes Truth Engine different from generic fine-tuning services.
                </div>
              </div>
              <p className="centered-block">
                <strong>The moat:</strong> Stage 3 models can be trained with good processes. Stage 4 models can be trained with good data. Stage 5 models require Stage 5 involvement. That&apos;s what Jeremy provides. That&apos;s what makes this possible.
              </p>
              <p className="centered-block">
                <strong>Architecture reference:</strong> Genesis Model (Jeremy&apos;s infrastructure) → Daughter Models (customer deployments). The five-layer training architecture ensures every Not-Me inherits the cognitive architecture while specializing for individual use cases.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="notme-hybrid">
        <div className="container centered">
          <h2>Hybrid Architecture: Local + Cloud</h2>
          <p className="section-intro centered-intro">
            iPhone + iCloud model. Local runs fast. Cloud holds everything.
          </p>
          <div className="hybrid-grid">
            <div className="hybrid-card">
              <h3>Local (Your Hardware)</h3>
              <ul>
                <li>LLM Inference (Scout 109B runs locally)</li>
                <li>Immediate context</li>
                <li>Sovereignty — your data stays on your machine</li>
                <li>No cloud required for basic operation</li>
              </ul>
            </div>
            <div className="hybrid-card">
              <h3>Cloud (Google Cloud Platform)</h3>
              <ul>
                <li>BigQuery (enriched data, 51.8M entities in production)</li>
                <li>Vertex AI (embeddings)</li>
                <li>Vector Search (long-term memory layer)</li>
                <li>Cloud Storage (archives)</li>
                <li>Compute/GKE (burst training for large models)</li>
              </ul>
            </div>
          </div>
          <p className="centered-block">
            Customer owns the hardware. Cloud extends the brain. Every hardware sale creates a permanent cloud customer: SOLDIER → ~$100-200/month, KING → ~$200-400/month, EMPIRE → ~$500+/month recurring cloud usage.
          </p>
          <p className="centered-block">
            <strong>Current infrastructure:</strong> 51.8 million entities in production BigQuery. 114 tables in spine dataset. L1-L8 knowledge hierarchy (tokens → high-level constructs). $1,700+ GCP spend to date (Oct 2025 - Jan 2026).
          </p>
        </div>
      </section>

      <section className="page-cta">
        <div className="container centered">
          <h2>Ready to Meet Yours?</h2>
          <p>The Not-Me takes a year to know you. Start the relationship.</p>
          <Link to="/preorder" className="cta-button">View Products</Link>
        </div>
      </section>
    </>
  );
}

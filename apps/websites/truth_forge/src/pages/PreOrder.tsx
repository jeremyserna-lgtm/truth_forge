export default function PreOrder() {
  return (
    <>
      <section className="page-hero">
        <div className="container">
          <h1>Preorder Your Not-Me</h1>
          <p className="page-intro">
            One-time hardware purchase. No subscription required. Optional annual service for updates and tuning.
            The Not-Me takes a year to know you. Quit early, that's on you. We told you.
          </p>
        </div>
      </section>

      <section className="preorder-products">
        <div className="container">
          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Drummer</h3>
              <p className="hardware">Mac Mini M4 Pro 64GB — Presence</p>
              <p className="price">$3,500</p>
              <p className="optional-annual">Optional: $500/year annual service</p>
              <div className="product-specs">
                <p>Scout model, ambient care</p>
                <p>Elderly, dorm, small spaces</p>
                <p>Fits anywhere. Silent.</p>
              </div>
              <a href="#contact-form" className="preorder-button">Preorder</a>
            </div>

            <div className="pricing-card featured">
              <h3>Soldier</h3>
              <p className="hardware">Mac Studio M3 Ultra 256GB — Companion</p>
              <p className="price">$9,500</p>
              <p className="optional-annual">Optional: $1,200/year annual service</p>
              <div className="product-specs">
                <p>Scout, 10M token context</p>
                <p>Gets to know you over time</p>
                <p>Native multimodal</p>
              </div>
              <a href="#contact-form" className="preorder-button">Preorder</a>
            </div>

            <div className="pricing-card">
              <h3>King</h3>
              <p className="hardware">Mac Studio M3 Ultra 512GB — Partner</p>
              <p className="price">$15,000</p>
              <p className="optional-annual">Optional: $2,000/year annual service</p>
              <div className="product-specs">
                <p>Maverick, 1M token context</p>
                <p>Already knows you (your data)</p>
                <p>Deeper reasoning</p>
              </div>
              <a href="#contact-form" className="preorder-button">Preorder</a>
            </div>

            <div className="pricing-card enterprise">
              <h3>Empire</h3>
              <p className="hardware">Clustered (e.g. 1 King + 3 Soldiers) — You</p>
              <p className="price">Custom</p>
              <p className="optional-annual">Optional: $4,000/year annual service</p>
              <div className="product-specs enterprise-specs">
                <p>Multi-unit, Exo + Thunderbolt 5</p>
                <p>Runs any model, any quality</p>
                <p>Digital extension of you</p>
                <p>Scoped per engagement</p>
              </div>
              <a href="#contact-form" className="preorder-button">Contact</a>
            </div>
          </div>
        </div>
      </section>

      <section className="preorder-includes">
        <div className="container">
          <h2>What's Included</h2>
          <div className="includes-grid">
            <div className="includes-card">
              <h3>Hardware</h3>
              <p>Mac Mini or Mac Studio with your Not-Me pre-installed. Yours. Sovereign.</p>
            </div>
            <div className="includes-card">
              <h3>Setup & Training</h3>
              <p>Initial setup, configuration, and a phone training session. You're ready to go.</p>
            </div>
            <div className="includes-card">
              <h3>30-Day Support</h3>
              <p>Support window after delivery. Questions answered. Smooth start.</p>
            </div>
            <div className="includes-card">
              <h3>Optional Annual Service</h3>
              <p>Model updates, tuning sessions, priority support. Hardware works without it; service adds ongoing refinement.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="preorder-timeline">
        <div className="container">
          <h2>The Timeline</h2>
          <div className="timeline">
            <div className="timeline-item">
              <h3>Discovery</h3>
              <p>Free 30‑minute call. We learn what you want. You pick a tier.</p>
            </div>
            <div className="timeline-item">
              <h3>Build</h3>
              <p>We configure your Not-Me. 1–3 weeks depending on tier and data.</p>
            </div>
            <div className="timeline-item">
              <h3>Install</h3>
              <p>Hardware ships or we install on-site. First conversations together.</p>
            </div>
            <div className="timeline-item">
              <h3>Year One</h3>
              <p>The Not-Me learns you. Conversations, patterns, preferences. Optional check-ins.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="preorder-form" id="contact-form">
        <div className="container">
          <h2>Reserve Yours</h2>
          <form className="contact-form">
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input type="text" id="name" name="name" required />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input type="email" id="email" name="email" required />
            </div>
            <div className="form-group">
              <label htmlFor="product">Product Interest</label>
              <select id="product" name="product" required>
                <option value="">Select a tier...</option>
                <option value="drummer">Drummer ($3,500)</option>
                <option value="soldier">Soldier ($9,500)</option>
                <option value="king">King ($15,000)</option>
                <option value="empire">Empire (Custom)</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="message">Tell us about your use case</label>
              <textarea id="message" name="message" rows={4}></textarea>
            </div>
            <button type="submit" className="submit-button">Submit Preorder Interest</button>
          </form>
          <p className="form-note">
            We'll contact you within 48 hours to discuss your preorder and answer any questions.
          </p>
        </div>
      </section>
    </>
  );
}

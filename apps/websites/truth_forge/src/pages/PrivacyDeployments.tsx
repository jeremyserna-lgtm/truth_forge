import { Link } from 'react-router-dom';

export default function PrivacyDeployments() {
  return (
    <>
      <section className="page-hero">
        <div className="container centered">
          <h1>Privacy First Deployments</h1>
          <p className="page-intro">
            Models trained on sensitive data that never leave your premises.
            Your data stays yours. Your AI stays local.
          </p>
        </div>
      </section>

      <section className="privacy-promise">
        <div className="container centered">
          <div className="promise-block">
            <h2>The Privacy Promise</h2>
            <p>
              Your model runs on your hardware. Your data trains your model.
              Your insights stay inside your walls. We deploy it and leave.
              You own everything.
            </p>
          </div>
        </div>
      </section>

      <section className="privacy-industries">
        <div className="container">
          <h2>Industry Deployments</h2>
          <div className="industry-grid">
            <div className="industry-card">
              <div className="industry-icon">&#9878;</div>
              <h3>Legal</h3>
              <p className="industry-features">Contract analysis, case research, document review, compliance monitoring</p>
              <p>
                Attorney-client privilege preserved. No data in external clouds.
                Full audit trails for discovery. Your clients' confidential
                information never leaves your control.
              </p>
              <ul className="industry-benefits">
                <li>Privileged communications stay privileged</li>
                <li>Discovery-ready audit logs</li>
                <li>Bar compliance maintained</li>
              </ul>
            </div>

            <div className="industry-card">
              <div className="industry-icon">&#9764;</div>
              <h3>Medical</h3>
              <p className="industry-features">Clinical documentation, patient summaries, diagnostic support, research synthesis</p>
              <p>
                HIPAA-compliant by architecture. Patient data never transmitted.
                On-premises processing only. Protected health information stays protected.
              </p>
              <ul className="industry-benefits">
                <li>HIPAA compliance built in</li>
                <li>PHI never leaves your network</li>
                <li>Patient trust preserved</li>
              </ul>
            </div>

            <div className="industry-card">
              <div className="industry-icon">&#36;</div>
              <h3>Financial</h3>
              <p className="industry-features">Risk analysis, portfolio insights, regulatory compliance, fraud detection</p>
              <p>
                SOC 2 ready. Client financial data air-gapped.
                Zero external API calls with sensitive data.
                Fiduciary duty maintained.
              </p>
              <ul className="industry-benefits">
                <li>Client data air-gapped</li>
                <li>Regulatory compliance ready</li>
                <li>Audit trails for regulators</li>
              </ul>
            </div>

            <div className="industry-card">
              <div className="industry-icon">&#128274;</div>
              <h3>Government & Defense</h3>
              <p className="industry-features">Intelligence synthesis, document classification, secure communications</p>
              <p>
                Air-gapped deployments. No internet required.
                Complete operational security. Classified information
                stays classified.
              </p>
              <ul className="industry-benefits">
                <li>Air-gapped operation</li>
                <li>No network dependencies</li>
                <li>Security clearance compatible</li>
              </ul>
            </div>

            <div className="industry-card">
              <div className="industry-icon">&#128218;</div>
              <h3>Research & Academia</h3>
              <p className="industry-features">Literature review, data analysis, hypothesis generation, grant writing</p>
              <p>
                Proprietary research stays proprietary.
                Unpublished findings never exposed.
                Competitive advantage protected.
              </p>
              <ul className="industry-benefits">
                <li>Pre-publication security</li>
                <li>IP protection</li>
                <li>Research integrity maintained</li>
              </ul>
            </div>

            <div className="industry-card">
              <div className="industry-icon">&#9881;</div>
              <h3>Manufacturing & IP</h3>
              <p className="industry-features">Process optimization, quality control, supply chain analysis, patent research</p>
              <p>
                Trade secrets protected.
                Competitive intelligence stays internal.
                Process innovations stay proprietary.
              </p>
              <ul className="industry-benefits">
                <li>Trade secret protection</li>
                <li>Supply chain confidentiality</li>
                <li>Patent strategy security</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="privacy-how">
        <div className="container">
          <h2>How It Works</h2>
          <div className="how-steps">
            <div className="how-step">
              <span className="step-number">1</span>
              <h3>Hardware Delivery</h3>
              <p>We ship pre-configured Mac hardware to your premises. It's yours.</p>
            </div>
            <div className="how-step">
              <span className="step-number">2</span>
              <h3>On-Site Setup</h3>
              <p>We install on your network. No external connections required.</p>
            </div>
            <div className="how-step">
              <span className="step-number">3</span>
              <h3>Data Ingestion</h3>
              <p>Your data stays local. Training happens on your hardware.</p>
            </div>
            <div className="how-step">
              <span className="step-number">4</span>
              <h3>We Leave</h3>
              <p>Once deployed, we're gone. You own the system completely.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="privacy-technical">
        <div className="container">
          <h2>Technical Specifications</h2>
          <div className="specs-grid">
            <div className="spec-card">
              <h3>Network Isolation</h3>
              <p>Can operate completely air-gapped. No internet dependency for core functions.</p>
            </div>
            <div className="spec-card">
              <h3>Encryption at Rest</h3>
              <p>All data encrypted with keys you control. We never have access.</p>
            </div>
            <div className="spec-card">
              <h3>Audit Logging</h3>
              <p>Every action logged. Every decision traceable. Compliance-ready.</p>
            </div>
            <div className="spec-card">
              <h3>Access Control</h3>
              <p>Role-based access. Your security policies. Your control.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="privacy-laws">
        <div className="container centered">
          <h2>Laws That Restrict Cloud Data</h2>
          <p className="section-intro centered-intro">
            Many organizations cannot use generic cloud AI because regulation or policy forbids it. On-premises deployment is often the only compliant option.
          </p>
          <div className="laws-grid">
            <div className="law-card">
              <h3>HIPAA (US)</h3>
              <p>Health data. PHI cannot be sent to third-party cloud AI for processing without a BAA and strict controls. Many providers exclude healthcare use. Local deployment keeps PHI in your control.</p>
            </div>
            <div className="law-card">
              <h3>GDPR / EU</h3>
              <p>Personal data in the EU. Restrictions on transfer, purpose limitation, and data minimization. Cloud AI that trains on or retains your data often conflicts. On-premises avoids that.</p>
            </div>
            <div className="law-card">
              <h3>Financial / GLBA, SOX</h3>
              <p>Client financial data. Regulators expect custody, audit trails, and no unnecessary sharing. Sending data to external AI can violate policy. Local keeps it in-house.</p>
            </div>
            <div className="law-card">
              <h3>Attorney-Client Privilege</h3>
              <p>Legal work. Privilege can be weakened or lost if confidential communications are processed by third-party AI. Bar ethics opinions increasingly address this. On-premises preserves privilege.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="page-cta">
        <div className="container centered">
          <h2>Enterprise Inquiries</h2>
          <p className="privacy-centered">Privacy-first deployments for organizations that can&apos;t compromise on data security.</p>
          <Link to="/about#contact" className="cta-button">Contact Us</Link>
        </div>
      </section>
    </>
  );
}

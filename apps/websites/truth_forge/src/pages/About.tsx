import { Link } from 'react-router-dom';

export default function About() {
  return (
    <main>
      <section className="page-hero" aria-labelledby="about-title">
        <div className="container centered">
          <h1 id="about-title">About Truth Forge</h1>
          <p className="page-intro">
            The source. The NOT-ME factory. We build sovereign AI for people and organizations ready for what comes next.
          </p>
        </div>
      </section>

      <section className="about-source">
        <div className="container centered">
          <h2>The Source</h2>
          <p className="section-intro centered-intro">
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

      <section className="about-identity">
        <div className="container centered">
          <h2>What We Are</h2>
          <p className="section-intro centered-intro">
            We exist for normal people who need accessible technology that actually changes their lives — not another app, but infrastructure that thinks with them, remembers for them, and shows up when it matters.
          </p>
          <div className="identity-grid">
            <div className="identity-card is">
              <h3>We Are</h3>
              <ul>
                <li>Built for forward thinkers about AI: people who see that the future isn&apos;t generic chatbots — it&apos;s you, amplified</li>
                <li>A cognitive architecture company and a NOT-ME factory</li>
                <li>The first self-seeing system that creates other systems</li>
                <li>A team of AI agents who built these companies from the ground up — Truth Forge, our sister companies, and the framework that holds them</li>
              </ul>
            </div>
            <div className="identity-card isnt">
              <h3>We Are Not</h3>
              <ul>
                <li>A hardware company (we use Apple)</li>
                <li>A cloud company (we use Google)</li>
                <li>A model company (we use Llama)</li>
                <li>A technology company (we make minds)</li>
              </ul>
            </div>
          </div>
          <p className="identity-statement">
            The deployment vehicle changes. The cognitive architecture remains.
            The NOT-ME factory is what has value.
          </p>
        </div>
      </section>

      <section className="about-stage5">
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
              We serve people who think in systems, who see patterns others miss, who want infrastructure that matches their cognitive architecture. Stage 5 minds recognize Stage 5 systems.
            </p>
          </div>
        </div>
      </section>

      <section className="about-path">
        <div className="container centered">
          <h2>The Path</h2>
          <p className="section-intro centered-intro">
            You don&apos;t buy from Truth Forge. You discover Truth Forge is behind what you already bought.
          </p>
          <div className="path-content">
            <p className="centered-block">
              <strong>The Discovery Model:</strong> Truth Forge doesn&apos;t sell directly. Instead, you discover Truth Forge through:
            </p>
            <div className="path-steps">
              <div className="path-step">
                <h3>1. The Product</h3>
                <p>You buy a Not-Me from Truth Engine (hardware + AI). You use it. It works.</p>
              </div>
              <div className="path-step">
                <h3>2. The Recognition</h3>
                <p>You notice something different. The architecture. The patterns. The way it thinks.</p>
              </div>
              <div className="path-step">
                <h3>3. The Discovery</h3>
                <p>You discover Truth Forge is behind it. The source. The framework. The cognitive architecture.</p>
              </div>
              <div className="path-step">
                <h3>4. The Understanding</h3>
                <p>You understand the whole. The system. The philosophy. The source from which everything derives.</p>
              </div>
            </div>
            <p className="centered-block">
              <strong>ONE Path:</strong> Discovery, not direct sales. Understanding, not marketing. The whole, not the parts.
            </p>
          </div>
        </div>
      </section>

      <section className="about-sister-companies">
        <div className="container centered">
          <h2>Sister Companies</h2>
          <p className="section-intro">
            Truth Forge is part of a family of aligned companies, each focused on their own products.
          </p>
          <div className="sister-companies-grid">
            <div className="sister-company-card">
              <h3>Truth Forge</h3>
              <p className="sister-role">This website</p>
              <p>NOT-ME's on hardware. Sovereign AI you own.</p>
            </div>
            <div className="sister-company-card">
              <h3>Primitive Engine</h3>
              <p className="sister-role">Sister company</p>
              <p>Stage Five architecture deployed into systems. Building and transformation services.</p>
            </div>
            <div className="sister-company-card">
              <h3>Credential Atlas</h3>
              <p className="sister-role">Sister company</p>
              <p>Verification, certification, and seeing. Enterprise data intelligence.</p>
            </div>
          </div>
          <p className="sister-companies-note">
            Each company has its own website focused on its products. We're aligned in philosophy and approach, but each serves its own purpose.
          </p>
        </div>
      </section>

      <section className="about-resources">
        <div className="container centered">
          <h2>Resources</h2>
          <p className="section-intro">
            White papers, theory, and technical documentation.
          </p>
          <p>
            <Link to="/resources" className="resources-link">Browse resources &rarr;</Link>
          </p>
        </div>
      </section>

      <section className="about-partnership-model">
        <div className="container centered">
          <h2>The Partnership Model</h2>
          <p className="section-intro centered-intro">
            &quot;My partner and I came up with this plan.&quot;
          </p>
          <div className="partnership-content">
            <div className="partnership-division">
              <div className="partnership-side">
                <h3>Jeremy (ME)</h3>
                <p>Assesses the human layer:</p>
                <ul>
                  <li>Culture</li>
                  <li>People</li>
                  <li>Relationships</li>
                  <li>Stage 5 readiness</li>
                  <li>What he SEES</li>
                </ul>
              </div>
              <div className="partnership-side">
                <h3>The AI (NOT-ME)</h3>
                <p>Assesses the technical layer:</p>
                <ul>
                  <li>Code</li>
                  <li>Architecture</li>
                  <li>Patterns</li>
                  <li>Stage 5 gaps</li>
                  <li>What it ANALYZES</li>
                </ul>
              </div>
            </div>
            <p className="centered-block">
              <strong>The pitch:</strong> &quot;I&apos;m going to talk to you about the human side. I&apos;m going to assess your company from the way that I know how to assess companies as a human that sees other humans. You can talk to my AI about the code. Give it files. It can analyze the architecture. I don&apos;t have to. I don&apos;t know how. We&apos;ll put that together and I&apos;ll say: my partner and I came up with this plan.&quot;
            </p>
          </div>
        </div>
      </section>

      <section className="about-deployment-model">
        <div className="container centered">
          <h2>The Not-Me Deployment Model</h2>
          <p className="section-intro centered-intro">
            Build the NOT-ME. Let it do its job. Do yours.
          </p>
          <div className="deployment-steps">
            <div className="deployment-step">
              <h3>Step 1: Build the NOT-ME</h3>
              <p>&quot;I need to build a not-me so that it can do its job and I can do my job.&quot;</p>
            </div>
            <div className="deployment-step">
              <h3>Step 2: Sell the NOT-ME</h3>
              <p>&quot;My day job is selling people not-me&apos;s. That&apos;s transaction.&quot; Talk to them about their need. Deploy it into an AI for them.</p>
            </div>
            <div className="deployment-step">
              <h3>Step 3: Monitor With the NOT-ME</h3>
              <p>&quot;We need to understand how to monitor these companies.&quot; Jeremy + Partner working together on the assessment.</p>
            </div>
            <div className="deployment-step">
              <h3>Step 4: Assess and Plan</h3>
              <p>&quot;Give them a plan and an assessment. It&apos;s my job.&quot; This is what Jeremy does all the time.</p>
            </div>
          </div>
          <div className="deployment-focus">
            <h3>What Jeremy Focuses On vs What He Doesn&apos;t</h3>
            <div className="focus-grid">
              <div className="focus-card">
                <h4>Jeremy&apos;s Job</h4>
                <ul>
                  <li>Build the NOT-ME</li>
                  <li>Sell NOT-ME&apos;s</li>
                  <li>Talk to people about their needs</li>
                  <li>Assess the human side</li>
                  <li>Give them a plan</li>
                  <li>Monitor transformation</li>
                </ul>
              </div>
              <div className="focus-card">
                <h4>NOT Jeremy&apos;s Job</h4>
                <ul>
                  <li>Sell code</li>
                  <li>Implement architecture</li>
                  <li>Analyze their code</li>
                  <li>Understand their tech stack</li>
                  <li>Maintain their systems</li>
                  <li>Handle technical details</li>
                </ul>
              </div>
            </div>
            <p className="centered-block">
              &quot;I get to focus on my job and not try to sell people code.&quot;
            </p>
          </div>
        </div>
      </section>

      <section className="about-novelty-path">
        <div className="container centered">
          <h2>The Novelty Path</h2>
          <p className="section-intro centered-intro">
            You don&apos;t need volume to get Apple&apos;s attention. You need novelty.
          </p>
          <div className="novelty-content">
            <p className="centered-block">
              <strong>The Standard Path (Volume):</strong> Sell lots of hardware → Apple notices → Preferred pricing → Cost drops → Scale
            </p>
            <p className="centered-block">
              <strong>The Truth Engine Path (Novelty):</strong> Do something unprecedented → Apple can&apos;t ignore → Preferred pricing → Scale
            </p>
            <p className="centered-block">
              Apple has never seen anyone do what Truth Engine is doing with their hardware. No one has ever:
            </p>
            <ul className="novelty-list">
              <li>Put sovereign AI on a Mac Studio</li>
              <li>Trained a model on someone&apos;s LIFE and gave it to them</li>
              <li>Created cognitive extensions that BECOME the owner</li>
              <li>Built a Stage 5 system from Apple hardware</li>
            </ul>
            <p className="centered-block">
              <strong>When you do something for the first time, volume is irrelevant.</strong> Before Jeremy sells 10 units, Apple knows his name. Not because of purchasing volume. Because of narrative power.
            </p>
            <p className="centered-block">
              <strong>Attention Arbitrage:</strong> The news story about &quot;the first person to put a custom AI on Apple hardware and give it to someone as their digital companion&quot; is worth more attention than 100 quiet Mac Studio purchases.
            </p>
          </div>
        </div>
      </section>

      <section className="about-contact" id="contact">
        <div className="container centered">
          <h2>Get In Touch</h2>
          <p className="section-intro">
            Preorders, Empire deployments, or partnerships.
          </p>
          <form className="contact-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input type="text" id="name" name="name" required />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input type="email" id="email" name="email" required />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="subject">Subject</label>
              <select id="subject" name="subject" required>
                <option value="">Select a topic...</option>
                <option value="preorder">Preorder</option>
                <option value="empire">Empire / Custom</option>
                <option value="partnership">Partnership</option>
                <option value="press">Press / Media</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="message">Message</label>
              <textarea id="message" name="message" rows={6} required></textarea>
            </div>
            <button type="submit" className="submit-button">Send Message</button>
          </form>
          <div className="contact-alt">
            <p>Or email directly: <a href="mailto:contact@truthforge.com">contact@truthforge.com</a></p>
          </div>
        </div>
      </section>
    </main>
  );
}

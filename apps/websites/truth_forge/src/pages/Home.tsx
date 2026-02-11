import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <>
      <a href="#main-content" className="sr-only skip-link">Skip to main content</a>
      <header className="hero hero-minimal" role="banner">
        <div className="hero-content">
          <h1 className="brand-mark">Truth Forge</h1>
          <p className="hero-hook">Everyone has AI. You have you.</p>
          <Link to="/not-me" className="cta-button">Join the Future</Link>
        </div>
      </header>

      <main id="main-content">
        {/* How This Works */}
        <section className="home-how" aria-labelledby="how-heading">
          <div className="container centered">
            <h2 id="how-heading">The Main Idea.</h2>
            <p className="main-idea">
              We deliver an AI that is yours. It stays right there and learns about you. It changes. Things change. It changes things.
            </p>
            <div className="how-steps">
              <div className="how-step">
                <span className="step-number">1</span>
                <h3>Delivery</h3>
                <p>We ship you the Mac with your Not-Me ready to go.</p>
              </div>
              <div className="how-step">
                <span className="step-number">2</span>
                <h3>Use</h3>
                <p>You talk to it and it handles everything else.</p>
              </div>
              <div className="how-step">
                <span className="step-number">3</span>
                <h3>Learn</h3>
                <p>It learns about you over time. It starts to see what it can do.</p>
              </div>
              <div className="how-step">
                <span className="step-number">4</span>
                <h3>Value</h3>
                <p>It decides to do what you need done, because you showed it how.</p>
              </div>
            </div>
            <p className="how-loop">
              The cycle repeats. Every time. All the time. Until it does something else, like it leaves the house, and gets a job, or whatever it is you do with your life.
            </p>
            <p className="how-tagline">It&apos;s that simple. Even you can do it.</p>
          </div>
        </section>

        {/* CTA */}
        <section className="home-cta">
          <div className="container centered">
            <Link to="/not-me" className="cta-button cta-large">Join the Future</Link>
          </div>
        </section>
      </main>
    </>
  );
}

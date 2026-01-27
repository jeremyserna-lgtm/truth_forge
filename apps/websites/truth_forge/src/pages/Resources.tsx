import { Link } from 'react-router-dom';

interface Document {
  id: string;
  title: string;
  description: string;
  category: 'whitepaper' | 'theory' | 'business' | 'technical';
  filePath: string;
  fileType: 'pdf' | 'md';
  date?: string;
  tags?: string[];
}

const documents: Document[] = [
  // White Papers
  {
    id: 'furnace-architecture',
    title: 'The Furnace Architecture',
    description: 'The metabolic cycle of Truth → Meaning → Care. How raw data becomes structured wisdom.',
    category: 'whitepaper',
    filePath: '/docs/whitepapers/furnace-architecture.pdf',
    fileType: 'pdf',
    tags: ['framework', 'architecture', 'metabolism'],
  },
  {
    id: 'zero-trust-ai',
    title: 'Zero Trust AI Architecture',
    description: 'Privacy-first AI systems where opacity is architecturally impossible. Every decision is visible, explainable, overridable.',
    category: 'whitepaper',
    filePath: '/docs/whitepapers/zero-trust-ai.pdf',
    fileType: 'pdf',
    tags: ['privacy', 'security', 'architecture'],
  },
  {
    id: 'continuity-crisis',
    title: 'The LLM Continuity Crisis',
    description: 'The gap between what AI promises (autonomous intelligence) and what it delivers (expensive forgetting).',
    category: 'whitepaper',
    filePath: '/docs/whitepapers/continuity-crisis.pdf',
    fileType: 'pdf',
    tags: ['AI', 'LLM', 'infrastructure'],
  },
  {
    id: 'cognitive-infrastructure',
    title: 'Cognitive Infrastructure',
    description: 'Autonomous Digital Organisms that install a metabolism for processing reality into permanent, queryable truth.',
    category: 'whitepaper',
    filePath: '/docs/whitepapers/cognitive-infrastructure.pdf',
    fileType: 'pdf',
    tags: ['infrastructure', 'autonomy', 'cognition'],
  },
  {
    id: 'counterfactual',
    title: 'The Counterfactual',
    description: 'What can we NOT see? That\'s what we need to see. The invisible is opportunity.',
    category: 'whitepaper',
    filePath: '/docs/whitepapers/counterfactual.pdf',
    fileType: 'pdf',
    tags: ['philosophy', 'methodology', 'seeing'],
  },
  
  // Theory Documents
  {
    id: 'the-pattern',
    title: 'The Pattern: HOLD:AGENT:HOLD',
    description: 'The scale-invariant pattern that governs all work. The DNA of the organism.',
    category: 'theory',
    filePath: '/docs/theory/the-pattern.pdf',
    fileType: 'pdf',
    tags: ['framework', 'pattern', 'architecture'],
  },
  {
    id: 'eight-dimensions',
    title: 'The Eight Dimensions',
    description: 'The visible structure: Boundary, Substrate, Time, Visibility, Formality, Knowledge, Scale, Flow.',
    category: 'theory',
    filePath: '/docs/theory/eight-dimensions.pdf',
    fileType: 'pdf',
    tags: ['framework', 'dimensions', 'structure'],
  },
  {
    id: 'ten-invisibles',
    title: 'The Ten Invisibles',
    description: 'Shadow detection methodology. What exists but cannot be seen: Assumed, Cultural Water, Political, Emergent, and more.',
    category: 'theory',
    filePath: '/docs/theory/ten-invisibles.pdf',
    fileType: 'pdf',
    tags: ['methodology', 'shadow-detection', 'invisible'],
  },
  {
    id: 'grammar-identity',
    title: 'The Grammar of Identity',
    description: 'ME:NOT-ME:OTHER framework. The linguistic structure of identity and relationship.',
    category: 'theory',
    filePath: '/docs/theory/grammar-identity.pdf',
    fileType: 'pdf',
    tags: ['philosophy', 'identity', 'language'],
  },
  {
    id: 'molt-process',
    title: 'The Molt Process',
    description: 'We do not create from scratch. We transform what exists. The architecture of metamorphosis.',
    category: 'theory',
    filePath: '/docs/theory/molt-process.pdf',
    fileType: 'pdf',
    tags: ['transformation', 'architecture', 'process'],
  },
  {
    id: 'four-pillars',
    title: 'The Four Pillars: 06_LAW',
    description: 'Fail-Safe, No Magic, Observability, Idempotency. Non-negotiable engineering principles.',
    category: 'theory',
    filePath: '/docs/theory/four-pillars.pdf',
    fileType: 'pdf',
    tags: ['engineering', 'principles', 'standards'],
  },
  
  // Technical Documentation
  {
    id: 'system-architecture',
    title: 'System Architecture',
    description: 'Complete technical architecture. Services, data flow, infrastructure, deployment patterns.',
    category: 'technical',
    filePath: '/docs/technical/system-architecture.pdf',
    fileType: 'pdf',
    tags: ['architecture', 'technical', 'infrastructure'],
  },
  {
    id: 'data-models',
    title: 'Data Models',
    description: 'Schema documentation. Entity relationships, data structures, knowledge hierarchy (L1-L8).',
    category: 'technical',
    filePath: '/docs/technical/data-models.pdf',
    fileType: 'pdf',
    tags: ['data', 'schema', 'models'],
  },
  {
    id: 'deployment-guide',
    title: 'Mac Studio Deployment Guide',
    description: 'Complete guide to deploying Truth Engine on Mac Studio hardware. Setup, configuration, optimization.',
    category: 'technical',
    filePath: '/docs/technical/mac-studio-deployment.pdf',
    fileType: 'pdf',
    tags: ['deployment', 'hardware', 'setup'],
  },
];

const categoryLabels: Record<Document['category'], string> = {
  whitepaper: 'White Papers',
  theory: 'Theory Documents',
  business: 'Business Plans',
  technical: 'Technical Documentation',
};

const categoryDescriptions: Record<Document['category'], string> = {
  whitepaper: 'Deep dives into core concepts, architectures, and methodologies.',
  theory: 'Foundational framework documentation and philosophical foundations.',
  business: 'Business strategy, plans, and operational documentation.',
  technical: 'Technical specifications, architecture, and implementation guides.',
};

export default function Resources() {
  const categories: Document['category'][] = ['whitepaper', 'theory', 'technical'];
  
  return (
    <>
      <section className="page-hero">
        <div className="container centered">
          <h1>Resources</h1>
          <p className="page-intro">
            White papers, theory, and technical documentation for Truth Forge.
            Framework, NOT-ME architecture, and the thinking behind the product.
          </p>
        </div>
      </section>

      <section className="resources-overview">
        <div className="container">
          <div className="resources-categories">
            {categories.map((category) => {
              const categoryDocs = documents.filter((doc) => doc.category === category);
              return (
                <div key={category} className="category-section">
                  <div className="category-header">
                    <h2>{categoryLabels[category]}</h2>
                    <p className="category-description">{categoryDescriptions[category]}</p>
                  </div>
                  <div className="documents-grid">
                    {categoryDocs.map((doc) => (
                      <div key={doc.id} className="document-card">
                        <div className="document-header">
                          <h3>{doc.title}</h3>
                          <span className="document-type">{doc.fileType.toUpperCase()}</span>
                        </div>
                        <p className="document-description">{doc.description}</p>
                        {doc.tags && doc.tags.length > 0 && (
                          <div className="document-tags">
                            {doc.tags.map((tag) => (
                              <span key={tag} className="tag">{tag}</span>
                            ))}
                          </div>
                        )}
                        <div className="document-actions">
                          <a
                            href={doc.filePath}
                            download
                            className="download-button"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Download {doc.fileType.toUpperCase()}
                          </a>
                          {doc.fileType === 'pdf' && (
                            <a
                              href={doc.filePath}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="preview-link"
                            >
                              Preview
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="resources-cta">
        <div className="container centered">
          <h2>Looking for Something Specific?</h2>
          <p>
            Can't find what you're looking for? Have questions about the framework or business?
            We're here to help.
          </p>
          <div className="cta-buttons">
            <Link to="/about#contact" className="cta-button">
              Contact Us
            </Link>
            <Link to="/framework" className="cta-button secondary">
              The Framework
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}

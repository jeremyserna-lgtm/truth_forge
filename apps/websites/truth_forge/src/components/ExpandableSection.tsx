import { useState } from 'react';

interface ExpandableSectionProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}

export default function ExpandableSection({ 
  title, 
  children, 
  defaultExpanded = false 
}: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`expandable-section ${isExpanded ? 'expanded' : ''}`}>
      <button
        className="expandable-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-controls={`expandable-content-${title.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <span>{title}</span>
        <span className="expandable-chevron" aria-hidden="true">
          {isExpanded ? '▼' : '▶'}
        </span>
      </button>
      <div
        id={`expandable-content-${title.replace(/\s+/g, '-').toLowerCase()}`}
        className="expandable-content"
        aria-hidden={!isExpanded}
      >
        {children}
      </div>
    </div>
  );
}

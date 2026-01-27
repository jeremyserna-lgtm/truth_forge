import { Link } from 'react-router-dom';
import { ReactNode } from 'react';

interface CardProps {
  title?: string;
  meta?: string;
  description?: string;
  children?: ReactNode;
  link?: string;
  linkText?: string;
  className?: string;
}

export default function Card({
  title,
  meta,
  description,
  children,
  link,
  linkText,
  className = '',
}: CardProps) {
  const cardContent = (
    <div className={`card ${className}`}>
      {meta && <p className="card-meta">{meta}</p>}
      {title && <h3 className="card-title">{title}</h3>}
      {description && <p className="card-body">{description}</p>}
      {children}
      {link && linkText && (
        <Link to={link} className="card-link">
          {linkText} →
        </Link>
      )}
    </div>
  );

  return link ? (
    <Link to={link} style={{ textDecoration: 'none' }}>
      {cardContent}
    </Link>
  ) : (
    cardContent
  );
}

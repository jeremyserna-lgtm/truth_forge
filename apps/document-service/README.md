# Document Service

Multi-tenant document management and knowledge atomization service.

## Features

- **Multi-tenant**: Support personal, business, and client deployments
- **Document Types**: Operational (receipts, contracts) and Knowledge (theory, technical)
- **OCR**: Automatic text extraction from images and PDFs
- **Knowledge Atomization**: Break documents into atomic insights
- **Conversational Assistant**: "Not_me" AI helps clients build complete training datasets
- **Truth Forge Integration**: Export to BigQuery entities_unified for fine-tuning pipelines

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your configuration

# Start development server
npm run dev
```

## Deployment Contexts

### Personal Use
For your own operational and knowledge documents with Truth Forge sync.

### Client Portal
Multi-tenant deployment where clients upload documents for fine-tuning. The "Not_me" conversational assistant guides them to data completeness without exposing complexity.

### Website Integration
Embedded demo for public-facing documentation.

## Architecture

```
src/
├── api/          # Express routes and middleware
├── core/         # Business logic (distillation, OCR, etc.)
├── storage/      # Storage adapters (local, GCS, S3)
├── integrations/ # Truth Forge, Scout 4 connections
└── config/       # Deployment configurations
```

## API Endpoints

```
POST   /api/v1/documents              # Upload document
GET    /api/v1/documents              # List documents
POST   /api/v1/documents/:id/distill  # Convert to knowledge atoms
POST   /api/v1/chat                   # Conversational assistant ("Not_me")
```

## License

Private - Truth Forge Project

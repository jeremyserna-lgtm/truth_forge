"""FastAPI endpoint for knowledge atom generation via Scout/Maverick/R1.

This API bridges the React frontend with the KnowledgeAtomFactory service.

IMPORTANT: EXO cluster owns port 8000. This API runs on port 8001.

Usage:
    uvicorn truth_forge.api.knowledge_atom_api:app --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sovereign.memory.cortex import MemoryCortex
from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider
from truth_forge.services.knowledge_atom_factory import (
    KnowledgeAtomFactory,
)


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge Atom Generation API",
    description="Scout/Maverick/R1 tensor-level knowledge atom generation",
    version="1.0.0",
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class DocumentContext(BaseModel):
    """A document to include in Scout's context."""

    name: str
    content: str


class GenerateAtomRequest(BaseModel):
    """Request to generate a knowledge atom."""

    user_input: str = Field(..., description="Input text to generate atom from")
    use_exo: bool = Field(
        default=True, description="Use EXO distributed inference for large models"
    )
    commit_to_memory: bool = Field(default=True, description="Commit atom to MemoryCortex")
    documents: list[DocumentContext] = Field(
        default_factory=list,
        description="Documents to include in Scout's 10M context window",
    )


class GenerateAtomResponse(BaseModel):
    """Response containing generated knowledge atom."""

    id: str
    content: str
    original_input: str
    perspectives: list[dict[str, Any]]
    convergence_score: float | None = None
    divergence_note: str | None = None
    generation_metadata: dict[str, Any] | None = None
    created_at: int


# Global state (initialized on startup)
_factory: KnowledgeAtomFactory | None = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize KnowledgeAtomFactory on startup."""
    global _factory

    logger.info("Initializing Knowledge Atom Factory...")

    # Initialize MemoryCortex
    memory_cortex = MemoryCortex(
        graphs={
            "semantic": {},
            "temporal": {},
            "causal": {},
            "entity": {},
            "emotional": {},
        }
    )

    # Initialize model providers from runtime endpoints.
    # Defaults align with the Cognitive Bridge local triad contract.
    scout_provider = ScoutProvider(
        base_url=os.environ.get("SCOUT_BASE_URL", "http://localhost:8765/v1")
    )
    maverick_provider = MaverickProvider(
        base_url=os.environ.get("MAVERICK_BASE_URL", "http://localhost:8766/v1")
    )
    r1_provider = R1Provider(base_url=os.environ.get("R1_BASE_URL", "http://localhost:8767/v1"))

    # Create factory
    _factory = KnowledgeAtomFactory(
        memory_cortex=memory_cortex,
        scout_provider=scout_provider,
        maverick_provider=maverick_provider,
        r1_provider=r1_provider,
        use_exo=True,
    )

    logger.info("Knowledge Atom Factory initialized successfully")


@app.post("/api/v1/knowledge-atom/generate", response_model=GenerateAtomResponse)
async def generate_knowledge_atom(request: GenerateAtomRequest) -> dict[str, Any]:
    """Generate a multi-perspective knowledge atom using Scout/Maverick/R1.

    Args:
        request: Generation request with user input and options

    Returns:
        Generated knowledge atom with perspectives, convergence, and metadata

    Raises:
        HTTPException: If generation fails
    """
    if not _factory:
        raise HTTPException(status_code=503, detail="Factory not initialized")

    try:
        # Build enriched context with documents
        context_parts = []
        if request.documents:
            context_parts.append("=== CODEBASE CONTEXT ===")
            for doc in request.documents:
                context_parts.append(f"\n--- {doc.name} ---")
                context_parts.append(doc.content)
            context_parts.append("\n=== USER INPUT ===")

        context_parts.append(request.user_input)
        enriched_input = "\n".join(context_parts)

        logger.info(
            "Generating knowledge atom",
            extra={
                "input_length": len(request.user_input),
                "documents_count": len(request.documents),
                "total_context_length": len(enriched_input),
                "use_exo": request.use_exo,
            },
        )

        # Generate atom with full context
        # Scout will see all documents in its 10M context window
        atom = await _factory.generate_atom(
            user_input=enriched_input,
            models=None,  # Use all three models
            commit_to_memory=request.commit_to_memory,
        )

        # Convert to API response format
        # Map KnowledgeAtom fields to API response schema
        response = {
            "id": atom.atom_id,
            "content": atom.convergence_summary
            or (atom.perspectives[0].response_content if atom.perspectives else ""),
            "original_input": atom.raw_input,
            "perspectives": [
                {
                    "model_name": p.model_name,
                    "model_id": p.model_id,
                    "response_content": p.response_content,
                    "input_tokens": p.input_tokens,
                    "output_tokens": p.output_tokens,
                    "latency_ms": p.latency_ms,
                    "timestamp": p.timestamp,
                }
                for p in atom.perspectives
            ],
            "convergence_score": atom.convergence_score,
            "divergence_note": atom.divergence_summary,
            "generation_metadata": {
                "enriched_input": atom.raw_input,
                "processing_time_ms": sum(p.latency_ms for p in atom.perspectives),
                "memory_graphs": ["semantic", "temporal", "causal", "entity", "emotional"],
            },
            "created_at": int(datetime.now(UTC).timestamp() * 1000),
        }

        logger.info(
            "Knowledge atom generated successfully",
            extra={
                "atom_id": atom.atom_id,
                "perspectives": len(atom.perspectives),
                "convergence": atom.convergence_score,
            },
        )

        return response

    except Exception as e:
        logger.error(
            "Knowledge atom generation failed",
            extra={"error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Generation failed: {e!s}") from e


@app.get("/api/v1/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "factory_initialized": _factory is not None,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/v1/exo/status")
async def exo_status() -> dict[str, Any]:
    """Get EXO cluster status."""
    if not _factory or not _factory._exo:
        return {"available": False, "error": "EXO not initialized"}

    return _factory._exo.get_status()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

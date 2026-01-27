"""NOT-ME Chat FastAPI Application.

MOLT LINEAGE:
- Source: Truth_Engine/apps/not_me_chat/backend/main.py
- Version: 2.0.0
- Date: 2026-01-26

FastAPI backend for NOT-ME Chat with WebSocket support.

THE PATTERN:
- HOLD1: User message input
- AGENT: Chat processing with LLM
- HOLD2: Response delivery

Example:
    uvicorn apps.not_me_chat.backend.main:app --reload
"""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any


# Add src to path for truth_forge imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402


logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message model.

    Attributes:
        content: Message content.
        role: Message role (user or assistant).
        session_id: Session identifier.
    """

    content: str
    role: str = "user"
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response model.

    Attributes:
        content: Response content.
        role: Always "assistant".
        session_id: Session identifier.
        cost: Cost of the response.
    """

    content: str
    role: str = "assistant"
    session_id: str
    cost: float = 0.0


class ConnectionManager:
    """WebSocket connection manager.

    Manages active WebSocket connections for chat sessions.
    """

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept and register a WebSocket connection.

        Args:
            websocket: WebSocket connection.
            session_id: Session identifier.
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("Connection established", extra={"session_id": session_id})

    def disconnect(self, session_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            session_id: Session identifier.
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("Connection closed", extra={"session_id": session_id})

    async def send_message(self, session_id: str, message: dict[str, Any]) -> None:
        """Send a message to a specific session.

        Args:
            session_id: Session identifier.
            message: Message to send.
        """
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Args:
        app: FastAPI application.

    Yields:
        None during application lifetime.
    """
    logger.info("NOT-ME Chat backend starting")
    yield
    logger.info("NOT-ME Chat backend shutting down")


app = FastAPI(
    title="NOT-ME Chat",
    description="Conversational interface for truth_forge",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status.
    """
    return {"status": "healthy", "service": "not_me_chat"}


@app.post("/chat")
async def chat(message: ChatMessage) -> ChatResponse:
    """Process a chat message.

    Args:
        message: Incoming chat message.

    Returns:
        Chat response.
    """
    # TODO: Integrate with truth_forge services
    session_id = message.session_id or "default"

    logger.info(
        "Chat message received",
        extra={"session_id": session_id, "content_length": len(message.content)},
    )

    # Placeholder response
    response_content = f"I received your message: {message.content[:50]}..."

    return ChatResponse(
        content=response_content,
        session_id=session_id,
        cost=0.0,
    )


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection.
        session_id: Session identifier.
    """
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = ChatMessage(**data)

            logger.info(
                "WebSocket message received",
                extra={"session_id": session_id, "content_length": len(message.content)},
            )

            # TODO: Process with truth_forge services
            response = {
                "content": f"Received: {message.content[:50]}...",
                "role": "assistant",
                "session_id": session_id,
            }

            await manager.send_message(session_id, response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

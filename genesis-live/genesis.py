"""
GENESIS — Phase 0
One file. One command. Drop files. See atoms.

    pip install fastapi uvicorn python-multipart httpx duckdb
    python genesis.py

Open http://localhost:8000 from any device on your network.
Open http://<your-mac-ip>:8000 from your phone.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import duckdb
import httpx
import uvicorn
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ─── CONFIG ────────────────────────────────────────────────────────────────────
SCOUT_URL = os.getenv("SCOUT_URL", "http://localhost:11434")
EXO_URL = os.getenv("EXO_URL", "http://localhost:8000")
DB_PATH = os.getenv("GENESIS_DB", os.path.expanduser("~/truth_forge/genesis.duckdb"))
HOST = "0.0.0.0"  # Accessible from any device on network
PORT = 8000
UI_DIR = Path(__file__).parent

# ─── APP ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Genesis", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DATABASE ──────────────────────────────────────────────────────────────────
db = duckdb.connect(DB_PATH)
db.execute("""
    CREATE TABLE IF NOT EXISTS atoms (
        id VARCHAR PRIMARY KEY,
        source_file VARCHAR,
        file_type VARCHAR,
        atom_type VARCHAR,
        content TEXT,
        entities TEXT,
        themes TEXT,
        relationships TEXT,
        confidence FLOAT,
        model_used VARCHAR,
        processing_ms INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS intake_log (
        id VARCHAR PRIMARY KEY,
        filename VARCHAR,
        file_type VARCHAR,
        file_size INTEGER,
        atom_count INTEGER,
        model_used VARCHAR,
        processing_ms INTEGER,
        status VARCHAR,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# ─── WEBSOCKET CONNECTIONS (live updates) ──────────────────────────────────────
connected_clients: list[WebSocket] = []


async def broadcast(event: dict):
    """Send event to all connected clients."""
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected_clients.remove(ws)


# ─── SCOUT / MODEL LAYER ──────────────────────────────────────────────────────
PREFERRED_MODELS = [
    "llama4-scout",
    "llama4",
    "llama3.2",
    "llama3.1",
    "llama3",
    "mistral",
    "gemma2",
    "phi3",
    "qwen2",
]


async def check_scout() -> dict:
    """Check if Scout (Ollama) is online and what models are available."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{SCOUT_URL}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                names = [m["name"] for m in models]
                return {"online": True, "models": names, "url": SCOUT_URL}
    except Exception:
        pass
    return {"online": False, "models": [], "url": SCOUT_URL}


async def check_exo() -> dict:
    """Check if EXO cluster is online (Maverick/R1)."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{EXO_URL}/health")
            if r.status_code == 200:
                return {"online": True, "url": EXO_URL}
    except Exception:
        pass
    return {"online": False, "url": EXO_URL}


def pick_model(available_models: list[str]) -> Optional[str]:
    """Pick the best available model from what Scout has loaded."""
    for preferred in PREFERRED_MODELS:
        for available in available_models:
            if preferred in available.lower():
                return available
    return available_models[0] if available_models else None


async def call_scout(prompt: str, model: str) -> dict:
    """Call Scout via Ollama API. Returns response text and timing."""
    start = datetime.now()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{SCOUT_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            elapsed = int((datetime.now() - start).total_seconds() * 1000)
            if r.status_code == 200:
                text = r.json().get("response", "")
                return {"ok": True, "text": text, "ms": elapsed, "model": model}
            return {"ok": False, "error": f"HTTP {r.status_code}", "ms": elapsed}
    except Exception as e:
        elapsed = int((datetime.now() - start).total_seconds() * 1000)
        return {"ok": False, "error": str(e), "ms": elapsed}


# ─── ATOMIZATION ───────────────────────────────────────────────────────────────
ATOMIZE_PROMPT = """You are a knowledge atomizer. Analyze this content and extract discrete knowledge atoms.

Source file: {filename}
File type: {file_type}

Content:
{content}

Return a JSON array of knowledge atoms. Each atom must be:
{{
  "atom_type": "ENTITY" | "CONCEPT" | "RELATIONSHIP" | "CLAIM" | "PATTERN" | "QUESTION" | "PROCEDURE" | "METRIC" | "CONTRADICTION",
  "content": "The atomic knowledge unit — one clear, complete thought",
  "entities": ["entity1", "entity2"],
  "themes": ["theme1", "theme2"],
  "relationships": ["entity1 -> relationship -> entity2"],
  "confidence": 0.0 to 1.0
}}

Rules:
- Each atom = ONE piece of knowledge. If it has an "and", split it.
- Entities = proper nouns, technical terms, specific things
- Themes = abstract categories this atom belongs to
- Relationships = how entities connect (use arrow notation)
- Confidence = how certain this knowledge is (0.5 = implied, 0.8 = stated, 1.0 = defined)

Return ONLY a valid JSON array. No markdown, no explanation, no preamble."""

# File type detection
EXTENSION_MAP = {
    # Text
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "react", ".tsx": "react-ts",
    ".json": "json", ".csv": "csv", ".yaml": "yaml", ".yml": "yaml",
    ".xml": "xml", ".html": "html", ".css": "css",
    ".md": "markdown", ".txt": "text", ".log": "log",
    ".sql": "sql", ".sh": "shell", ".bash": "shell",
    ".toml": "toml", ".ini": "config", ".cfg": "config", ".env": "env",
    # Documents
    ".pdf": "pdf", ".docx": "word", ".doc": "word",
    ".pptx": "powerpoint", ".xlsx": "excel",
    # Media
    ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".ogg": "audio",
    ".mp4": "video", ".mov": "video", ".avi": "video",
    ".png": "image", ".jpg": "image", ".jpeg": "image",
    ".gif": "image", ".svg": "svg", ".webp": "image",
}


def detect_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(ext, "unknown")


def extract_text(content: bytes, file_type: str) -> str:
    """Extract text from file content. Phase 0 = text files only.
    Future phases add PDF, image OCR, audio transcription, etc."""
    if file_type in (
        "python", "javascript", "typescript", "react", "react-ts",
        "json", "csv", "yaml", "xml", "html", "css", "markdown", "text",
        "log", "sql", "shell", "toml", "config", "env", "svg",
    ):
        return content.decode("utf-8", errors="replace")

    if file_type in ("pdf", "word", "powerpoint", "excel"):
        return f"[Binary file: {file_type}. Text extraction coming in Phase 1.]"

    if file_type in ("audio", "video"):
        return f"[Media file: {file_type}. Transcription coming in Phase 2.]"

    if file_type == "image":
        return f"[Image file. OCR/description coming in Phase 1.]"

    return content.decode("utf-8", errors="replace")


def parse_atoms_json(text: str) -> list[dict]:
    """Extract JSON array from Scout's response, handling messy output."""
    # Try direct parse first
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Find JSON array in response
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return []


async def atomize_file(content: bytes, filename: str) -> dict:
    """The core atomization pipeline: INTAKE → ATOMIZE → STORE."""
    file_type = detect_file_type(filename)
    file_size = len(content)
    intake_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()

    # Broadcast: intake started
    await broadcast({
        "event": "intake_start",
        "id": intake_id,
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size,
    })

    # HOLD₁: Extract text
    text = extract_text(content, file_type)
    if text.startswith("[Binary") or text.startswith("[Media") or text.startswith("[Image"):
        # Can't atomize yet — log it and return
        db.execute(
            "INSERT INTO intake_log VALUES (?,?,?,?,?,?,?,?,?,?)",
            [intake_id, filename, file_type, file_size, 0, None, 0, "skipped", text, datetime.now()]
        )
        await broadcast({"event": "intake_skip", "id": intake_id, "reason": text})
        return {"id": intake_id, "status": "skipped", "reason": text, "atoms": []}

    # AGENT: Call Scout
    await broadcast({"event": "atomize_start", "id": intake_id, "stage": "ATOMIZE"})

    scout = await check_scout()
    if not scout["online"]:
        db.execute(
            "INSERT INTO intake_log VALUES (?,?,?,?,?,?,?,?,?,?)",
            [intake_id, filename, file_type, file_size, 0, None, 0, "error", "Scout offline", datetime.now()]
        )
        await broadcast({"event": "error", "id": intake_id, "error": "Scout is offline"})
        return {"id": intake_id, "status": "error", "error": "Scout offline", "atoms": []}

    model = pick_model(scout["models"])
    if not model:
        return {"id": intake_id, "status": "error", "error": "No models available"}

    # Truncate for context window (Scout handles ~128K but let's be safe)
    truncated = text[:12000]

    prompt = ATOMIZE_PROMPT.format(
        filename=filename,
        file_type=file_type,
        content=truncated,
    )

    result = await call_scout(prompt, model)

    if not result["ok"]:
        elapsed = int((datetime.now() - start_time).total_seconds() * 1000)
        db.execute(
            "INSERT INTO intake_log VALUES (?,?,?,?,?,?,?,?,?,?)",
            [intake_id, filename, file_type, file_size, 0, model, elapsed, "error", result["error"], datetime.now()]
        )
        await broadcast({"event": "error", "id": intake_id, "error": result["error"]})
        return {"id": intake_id, "status": "error", "error": result["error"], "atoms": []}

    # HOLD₂: Parse and store atoms
    await broadcast({"event": "store_start", "id": intake_id, "stage": "STORE"})

    atoms = parse_atoms_json(result["text"])
    stored_count = 0

    for i, atom in enumerate(atoms):
        atom_id = f"{intake_id}_{i}"
        try:
            db.execute(
                "INSERT INTO atoms VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    atom_id,
                    filename,
                    file_type,
                    atom.get("atom_type", "UNKNOWN"),
                    atom.get("content", ""),
                    json.dumps(atom.get("entities", [])),
                    json.dumps(atom.get("themes", [])),
                    json.dumps(atom.get("relationships", [])),
                    atom.get("confidence", 0.5),
                    model,
                    result["ms"],
                    datetime.now(),
                ]
            )
            stored_count += 1

            # Broadcast each atom as it's stored
            await broadcast({
                "event": "atom",
                "id": atom_id,
                "intake_id": intake_id,
                "atom": atom,
                "index": i,
                "total": len(atoms),
            })
        except Exception as e:
            pass  # Duplicate or constraint error, skip

    elapsed = int((datetime.now() - start_time).total_seconds() * 1000)

    # Log the intake
    db.execute(
        "INSERT INTO intake_log VALUES (?,?,?,?,?,?,?,?,?,?)",
        [intake_id, filename, file_type, file_size, stored_count, model, elapsed, "complete", None, datetime.now()]
    )

    # Broadcast: complete
    await broadcast({
        "event": "intake_complete",
        "id": intake_id,
        "filename": filename,
        "atoms_count": stored_count,
        "model": model,
        "ms": elapsed,
    })

    return {
        "id": intake_id,
        "status": "complete",
        "filename": filename,
        "file_type": file_type,
        "model": model,
        "atoms": atoms,
        "stored": stored_count,
        "processing_ms": elapsed,
    }


# ─── ROUTES ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the UI."""
    ui_path = UI_DIR / "ui.html"
    if ui_path.exists():
        return HTMLResponse(ui_path.read_text())
    return HTMLResponse("<h1>Genesis</h1><p>ui.html not found. Place it next to genesis.py.</p>")


@app.get("/api/status")
async def status():
    """System health check."""
    scout = await check_scout()
    exo = await check_exo()
    atom_count = db.execute("SELECT COUNT(*) FROM atoms").fetchone()[0]
    intake_count = db.execute("SELECT COUNT(*) FROM intake_log").fetchone()[0]
    recent = db.execute(
        "SELECT atom_type, COUNT(*) as c FROM atoms GROUP BY atom_type ORDER BY c DESC"
    ).fetchall()

    return {
        "genesis": "alive",
        "version": "0.1.0",
        "scout": scout,
        "exo": exo,
        "atoms_stored": atom_count,
        "files_processed": intake_count,
        "atom_types": {row[0]: row[1] for row in recent},
        "db_path": DB_PATH,
    }


@app.post("/api/atomize")
async def atomize_endpoint(file: UploadFile = File(...)):
    """Drop a file → get atoms."""
    content = await file.read()
    result = await atomize_file(content, file.filename)
    return result


@app.post("/api/atomize/text")
async def atomize_text_endpoint(text: str = Form(...), source: str = Form("manual_input")):
    """Paste text → get atoms."""
    content = text.encode("utf-8")
    result = await atomize_file(content, source)
    return result


@app.get("/api/atoms")
async def list_atoms(limit: int = 100, file: Optional[str] = None, atom_type: Optional[str] = None):
    """List stored atoms with optional filters."""
    query = "SELECT * FROM atoms WHERE 1=1"
    params = []

    if file:
        query += " AND source_file = ?"
        params.append(file)
    if atom_type:
        query += " AND atom_type = ?"
        params.append(atom_type)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(query, params).fetchall()
    columns = [
        "id", "source_file", "file_type", "atom_type", "content",
        "entities", "themes", "relationships", "confidence",
        "model_used", "processing_ms", "created_at",
    ]
    return [dict(zip(columns, row)) for row in rows]


@app.get("/api/intake")
async def list_intake(limit: int = 50):
    """List file intake history."""
    rows = db.execute(
        "SELECT * FROM intake_log ORDER BY created_at DESC LIMIT ?", [limit]
    ).fetchall()
    columns = [
        "id", "filename", "file_type", "file_size", "atom_count",
        "model_used", "processing_ms", "status", "error_message", "created_at",
    ]
    return [dict(zip(columns, row)) for row in rows]


@app.delete("/api/atoms")
async def clear_atoms():
    """Clear all atoms (development use)."""
    db.execute("DELETE FROM atoms")
    db.execute("DELETE FROM intake_log")
    return {"cleared": True}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Real-time event stream. Connect from the UI to see atoms appear live."""
    await ws.accept()
    connected_clients.append(ws)
    try:
        # Send current status on connect
        scout = await check_scout()
        atom_count = db.execute("SELECT COUNT(*) FROM atoms").fetchone()[0]
        await ws.send_json({
            "event": "connected",
            "scout": scout,
            "atoms_stored": atom_count,
        })
        # Keep alive
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
                if msg == "ping":
                    await ws.send_json({"event": "pong"})
            except asyncio.TimeoutError:
                await ws.send_json({"event": "heartbeat", "ts": datetime.now().isoformat()})
    except WebSocketDisconnect:
        pass
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)


# ─── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("  ╔═══════════════════════════════════════╗")
    print("  ║         GENESIS — Phase 0             ║")
    print("  ║   Drop files. See atoms. Feel it.     ║")
    print("  ╠═══════════════════════════════════════╣")
    print(f"  ║  Local:   http://localhost:{PORT}        ║")
    print(f"  ║  Network: http://0.0.0.0:{PORT}         ║")
    print(f"  ║  Phone:   http://<your-ip>:{PORT}       ║")
    print(f"  ║  Scout:   {SCOUT_URL:<25} ║")
    print(f"  ║  DB:      {DB_PATH:<25} ║")
    print("  ╚═══════════════════════════════════════╝")
    print()

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")

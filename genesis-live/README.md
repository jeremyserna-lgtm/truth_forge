# Genesis — Phase 0

## Run it

```bash
pip install fastapi uvicorn python-multipart httpx duckdb
python genesis.py
```

Open http://localhost:8000

From your phone: http://<your-mac-ip>:8000

## What it does

Drop files. See knowledge atoms. Everything local. Everything yours.

- **Backend**: FastAPI → Ollama (Scout) → DuckDB
- **Frontend**: HTML served by the backend. No npm. No build step.
- **Models**: Whatever's loaded in Ollama at localhost:11434
- **Storage**: DuckDB at ~/truth_forge/genesis.duckdb
- **Real-time**: WebSocket pushes atoms to UI as they're extracted

## Requirements

- Python 3.10+
- Ollama running with at least one model loaded
- That's it.

## What's next

- Phase 1: PDF, image, audio intake (text extraction for binary files)
- Phase 2: Compound atoms (cross-file knowledge discovery)
- Phase 3: Dashboard with model health + ANIMA memory visualization
- Phase 4: Heartbeat (autonomous background processing)

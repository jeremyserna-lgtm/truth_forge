# Sovereign Cluster Manager

A web-based management interface for your 4-node Mac Studio cluster running EXO.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              YOUR MACBOOK                                   │
│    Browser → https://sovereign.vercel.app (or localhost:5173)               │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SUPABASE                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   PostgreSQL    │  │    Realtime     │  │   (Auth/Edge)   │             │
│  │ • cluster_state │  │ • Live updates  │  │   (future)      │             │
│  │ • nodes         │  │                 │  │                 │             │
│  │ • models        │  │                 │  │                 │             │
│  │ • presets       │  │                 │  │                 │             │
│  │ • commands      │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                            Tailscale / Direct
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          KING (Cluster Orchestrator)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CLUSTER AGENT (Python daemon)                     │   │
│  │  • Polls EXO API (localhost:52415)                                   │   │
│  │  • Pushes state to Supabase                                          │   │
│  │  • Receives commands from Supabase                                   │   │
│  │  • Manages /Volumes/Vault/models/                                    │   │
│  └──────────────────────────────────┬───────────────────────────────────┘   │
│                              EXO API │                                      │
│                              TB5 Mesh│                                      │
│                          ┌───────────┼───────────┐                          │
│                          ▼           ▼           ▼                          │
│                      Soldier1   Soldier2   Soldier3                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

- **Cluster Dashboard**: Real-time view of all 4 nodes, RAM usage, and status
- **Model Vault**: Browse, load, and manage models on your 8TB external drive
- **Quick Actions**: One-click presets for common configurations
- **Memory Pools**: Configure custom memory allocations (coming soon)
- **Realtime Updates**: Live state sync via Supabase Realtime

## Setup

### 1. Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Run the schema from `supabase/schema.sql`
4. Note your project URL and anon key from Settings > API

### 2. Backend Agent (runs on King)

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Supabase credentials and vault path

# Run
python agent.py
```

#### Run as LaunchDaemon (auto-start)

Create `/Library/LaunchDaemons/com.sovereign.cluster-agent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sovereign.cluster-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/jeremy/truth_forge/apps/sovereign-cluster-manager/backend/.venv/bin/python</string>
        <string>/Users/jeremy/truth_forge/apps/sovereign-cluster-manager/backend/agent.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/jeremy/truth_forge/apps/sovereign-cluster-manager/backend</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/sovereign-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/sovereign-agent.error.log</string>
</dict>
</plist>
```

```bash
sudo launchctl load /Library/LaunchDaemons/com.sovereign.cluster-agent.plist
```

### 3. Frontend

#### Local Development

```bash
cd frontend

# Install dependencies
npm install

# Configure
cp .env.example .env.local
# Edit .env.local with your Supabase credentials

# Run dev server
npm run dev
```

Open http://localhost:5173

#### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Set environment variables in Vercel dashboard:
# - VITE_SUPABASE_URL
# - VITE_SUPABASE_ANON_KEY
```

## Model Vault Structure

```
/Volumes/Vault/models/
├── base/                    # Downloaded foundation models
│   ├── llama-3.3-70b-instruct-q4/
│   ├── llama-4-scout-17b-q8/
│   ├── deepseek-r1-671b-q4/
│   └── qwen2.5-72b-q4/
│
├── fine-tuned/              # Your custom trained models
│   ├── genesis/
│   │   ├── v1-baseline/
│   │   ├── v2-stage5-aware/
│   │   └── v3-jeremy-arc/
│   └── experiments/
│
├── checkpoints/             # Mid-training saves
│   └── genesis-v4/
│       ├── step-1000/
│       └── step-2000/
│
├── lora/                    # LoRA adapters
│   └── stage5-adapter/
│
└── archive/                 # Old versions
```

## Quick Actions

Default presets (configurable via Supabase):

| Name | Model | Deployment | Use Case |
|------|-------|------------|----------|
| Deep Think | DeepSeek-R1 | Full Cluster | Maximum reasoning power |
| Fast Draft | Scout-17B | King Only | Quick iterations |
| Experiment | Latest FT | King Only | Testing fine-tunes |
| Training Mode | (none) | - | Free all RAM for training |

## API

The frontend communicates with Supabase, which stores commands for the agent.

### Commands

| Command | Payload | Description |
|---------|---------|-------------|
| `load_model` | `{model_id, mode}` | Load a model (mode: auto/single/cluster) |
| `unload_model` | `{}` | Unload all models |
| `apply_preset` | `{preset_id}` | Apply a saved preset |
| `refresh_state` | `{}` | Force state refresh |
| `scan_vault` | `{}` | Rescan model vault |

### Realtime Subscriptions

The frontend subscribes to:
- `cluster_state` - Live cluster status updates
- `nodes` - Node status changes

## Troubleshooting

### Agent not connecting to EXO

```bash
# Check if EXO is running
curl http://localhost:52415/node_id

# Check agent logs
tail -f /var/log/sovereign-agent.log
```

### Vault not found

Ensure the external drive is mounted at the configured path:

```bash
ls /Volumes/Vault/models/
```

### Models not appearing

Run a vault scan from the UI or:

```bash
# Insert command directly
psql $DATABASE_URL -c "INSERT INTO commands (command) VALUES ('scan_vault')"
```

## Development

### Adding new commands

1. Add command type to `commands` table check constraint in schema
2. Add handler in `agent.py:_execute_command()`
3. Add API function in `frontend/src/lib/supabase.ts`

### Adding new presets

Insert directly into Supabase:

```sql
INSERT INTO presets (name, description, icon, model_id, deployment_mode, is_quick_action, sort_order)
VALUES ('My Preset', 'Description', '🚀', 'model-uuid', 'cluster', true, 5);
```

## License

Part of Truth Forge. Internal use only.

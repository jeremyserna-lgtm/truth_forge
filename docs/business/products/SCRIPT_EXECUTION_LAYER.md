# Script Execution Layer: Claude Builds Scripts, The Layer Renders UI

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## The Core Insight

**Claude is good at writing scripts. Claude is not good at building GUIs.**

Instead of asking Claude to build individual apps (Grindr capture app, pipeline runner app, etc.), we build a **universal execution layer** that:

1. Discovers scripts Claude has written
2. Reads their metadata/interface requirements
3. Renders appropriate UI automatically
4. Executes with proper feedback (progress, logs, controls)
5. Logs to Central Services

**Result**: Any script becomes an interactive tool without Claude touching GUI code.

---

## The Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCRIPT EXECUTION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CLAUDE WRITES                    LAYER RENDERS                    YOU SEE  │
│  ┌────────────────┐              ┌────────────────┐              ┌────────┐ │
│  │ grindr_capture │              │ Script Runner  │              │  GUI   │ │
│  │    .py         │─────────────▶│                │─────────────▶│ with   │ │
│  │                │   metadata   │ - Reads config │   renders    │ buttons│ │
│  │ @script(       │              │ - Renders UI   │              │ sliders│ │
│  │   name="...",  │              │ - Executes     │              │ logs   │ │
│  │   params=[...],│              │ - Shows output │              │        │ │
│  │   outputs=...  │              │ - Logs to CS   │              │        │ │
│  │ )              │              └────────────────┘              └────────┘ │
│  └────────────────┘                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How Scripts Declare Their Interface

Scripts include a metadata block that the layer reads:

```python
# data_sources/grindr/code/capture/capture.py

from primitive_engine.script_layer import script, Param, Output

@script(
    name="Grindr Chat Capture",
    description="Capture conversations from Grindr Web",
    category="ingestion",

    params=[
        Param("max_chats", type="int", default=100, min=1, max=1000,
              label="How many conversations to capture"),
        Param("headless", type="bool", default=False,
              label="Run in background (no visible browser)"),
    ],

    outputs=[
        Output("html_files", type="files", description="Captured HTML"),
        Output("manifest", type="json", description="Capture manifest"),
    ],

    requires=["playwright", "keyring"],
    estimated_duration="5-10 minutes",
)
def main(max_chats: int, headless: bool):
    """Main capture function."""
    # ... existing capture logic ...
    return {
        "html_files": captured_files,
        "manifest": manifest_path,
    }
```

The layer reads this and renders:
- Title: "Grindr Chat Capture"
- Slider: "How many conversations" (1-1000, default 100)
- Checkbox: "Run in background"
- Button: "Start Capture"
- Progress indicator
- Log output
- Result: links to captured files

---

## What The Layer Provides

### Universal Controls

Every script gets:
- **Start/Stop** buttons
- **Progress** indicator (if script reports it)
- **Log output** (stdout/stderr)
- **Error handling** with retry option
- **Cost tracking** (if script uses Central Services)

### Parameter Types

| Type | Renders As |
|------|------------|
| `int` with min/max | Slider |
| `int` without bounds | Number input |
| `bool` | Checkbox |
| `str` | Text input |
| `str` with choices | Dropdown |
| `file` | File picker |
| `dir` | Directory picker |

### Output Types

| Type | Displays As |
|------|-------------|
| `files` | Clickable file links |
| `json` | Formatted JSON view |
| `text` | Monospace text block |
| `table` | Data table |
| `chart` | Simple visualization |

---

## Discovery Mechanism

The layer discovers scripts automatically:

```
truth-engine/
├── data_sources/
│   ├── grindr/code/capture/capture.py     # @script decorated
│   ├── zoom/scripts/capture_avatars.py    # @script decorated
│   └── ...
├── pipelines/
│   ├── chatgpt_web/scripts/stage_*/       # @script decorated
│   └── ...
└── tools/
    ├── sweep_root.py                       # @script decorated
    └── ...
```

**Discovery query**:
```python
# Find all scripts with @script decorator
scripts = discover_scripts(
    paths=["data_sources/*/code/", "pipelines/*/scripts/", "tools/"],
    pattern="**/*.py"
)
```

**Result in UI**:
```
Script Library
├── Ingestion
│   ├── Grindr Chat Capture
│   ├── Zoom Avatar Capture
│   └── ChatGPT Export Parser
├── Pipelines
│   ├── ChatGPT Stage 5
│   ├── ChatGPT Stage 6
│   └── ...
├── Maintenance
│   ├── Root Directory Sweep
│   ├── Health Check
│   └── ...
└── + Run Custom Script
```

---

## Integration with Existing Architecture

This layer fits into the existing Tauri + Next.js architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRUTH ENGINE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     INTERFACE LAYER                                  │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐      ┌──────────────────┐                     │    │
│  │  │   Desktop App    │      │    Web App       │                     │    │
│  │  │   (Tauri/Mac)    │      │   (Next.js)      │                     │    │
│  │  │                  │      │                  │                     │    │
│  │  │ • Relationships  │      │ • Interviews     │                     │    │
│  │  │ • Analysis       │      │ • Observer Portal│                     │    │
│  │  │ • SCRIPT RUNNER ◀───────│ • Shared Views   │                     │    │
│  │  │   (new)          │      │                  │                     │    │
│  │  └──────────────────┘      └──────────────────┘                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     SCRIPT EXECUTION LAYER (new)                     │    │
│  │                                                                      │    │
│  │  • Discovers @script decorated Python files                          │    │
│  │  • Reads metadata (params, outputs, requirements)                    │    │
│  │  • Renders UI automatically                                          │    │
│  │  • Executes via subprocess                                           │    │
│  │  • Streams logs to Central Services                                  │    │
│  │  • Returns results to UI                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Phase 1: Script Metadata Library

Create `primitive_engine/script_layer/`:

```python
# primitive_engine/script_layer/__init__.py

from dataclasses import dataclass
from typing import List, Any, Literal

@dataclass
class Param:
    name: str
    type: Literal["int", "str", "bool", "file", "dir"]
    default: Any = None
    label: str = None
    min: int = None
    max: int = None
    choices: List[str] = None
    required: bool = True

@dataclass
class Output:
    name: str
    type: Literal["files", "json", "text", "table"]
    description: str = None

def script(
    name: str,
    description: str = None,
    category: str = "general",
    params: List[Param] = None,
    outputs: List[Output] = None,
    requires: List[str] = None,
    estimated_duration: str = None,
):
    """Decorator that marks a function as a runnable script with UI metadata."""
    def decorator(func):
        func._script_metadata = {
            "name": name,
            "description": description,
            "category": category,
            "params": params or [],
            "outputs": outputs or [],
            "requires": requires or [],
            "estimated_duration": estimated_duration,
        }
        return func
    return decorator
```

### Phase 2: Script Discovery

```python
# primitive_engine/script_layer/discovery.py

import ast
import importlib.util
from pathlib import Path

def discover_scripts(paths: List[str]) -> List[dict]:
    """Find all @script decorated functions in given paths."""
    scripts = []

    for path_pattern in paths:
        for py_file in Path(".").glob(path_pattern):
            metadata = extract_script_metadata(py_file)
            if metadata:
                scripts.append({
                    "path": str(py_file),
                    **metadata
                })

    return scripts
```

### Phase 3: Script Runner (Tauri Command)

```rust
// desktop/src-tauri/src/commands/scripts.rs

#[tauri::command]
async fn list_scripts() -> Result<Vec<ScriptInfo>, Error> {
    // Call Python discovery
    let output = Command::new("python3")
        .args(["-m", "primitive_engine.script_layer.discovery"])
        .output()?;

    let scripts: Vec<ScriptInfo> = serde_json::from_slice(&output.stdout)?;
    Ok(scripts)
}

#[tauri::command]
async fn run_script(
    path: String,
    params: HashMap<String, Value>,
    window: Window,
) -> Result<ScriptResult, Error> {
    // Execute script with params
    // Stream output to window via events
    // Return results
}
```

### Phase 4: UI Component

```typescript
// frontend/components/scripts/ScriptRunner.tsx

interface ScriptRunnerProps {
  script: ScriptInfo;
  onComplete: (result: ScriptResult) => void;
}

function ScriptRunner({ script, onComplete }: ScriptRunnerProps) {
  const [params, setParams] = useState(defaultParams(script));
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  // Render parameter controls based on script.params
  const paramControls = script.params.map(param => (
    <ParamControl
      key={param.name}
      param={param}
      value={params[param.name]}
      onChange={(v) => setParams({...params, [param.name]: v})}
    />
  ));

  return (
    <div className="script-runner">
      <h2>{script.name}</h2>
      <p>{script.description}</p>

      <div className="params">{paramControls}</div>

      <button onClick={() => runScript(script.path, params)}>
        {running ? "Running..." : "Start"}
      </button>

      <LogOutput logs={logs} />

      {result && <ResultView result={result} outputs={script.outputs} />}
    </div>
  );
}
```

---

## Benefits

| For Claude | For You |
|------------|---------|
| Just writes Python | Visual interaction with any script |
| No GUI frameworks to learn | Consistent experience across all tools |
| Focus on logic, not presentation | Start/stop/monitor from one place |
| Standard metadata format | Auto-discovery of new scripts |

---

## Example: Grindr Capture Becomes Visual

**Before** (script only):
```bash
cd data_sources/grindr
python3 code/capture/capture.py
# Wait... is it working? How many did it capture?
```

**After** (with Script Execution Layer):
1. Open Truth Engine app
2. Go to Scripts → Ingestion → Grindr Chat Capture
3. See slider "How many" (set to 50)
4. See checkbox "Background mode" (unchecked)
5. Click "Start Capture"
6. Watch progress: "Captured 12/50..."
7. See logs streaming
8. Get notification when done
9. Click to open captured files

**Claude's work**: Add `@script` decorator to existing function.
**System's work**: Everything else.

---

## Roadmap

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| 1 | `@script` decorator library | Small |
| 2 | Discovery mechanism | Small |
| 3 | Tauri runner commands | Medium |
| 4 | UI components | Medium |
| 5 | Integrate existing scripts | Ongoing |

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Where this fits
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Build phases

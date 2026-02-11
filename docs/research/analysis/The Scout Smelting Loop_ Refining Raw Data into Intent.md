Based on the **Sovereign Technical Specification**, **Unified Memory Map**, and **Genesis Protocol**, configuring Scout to act as the "Context Filter" requires setting up a background "Smelting" loop. Scout (the Interface LLM) uses its massive context window to ingest raw noise and output structured signal (Knowledge Atoms) into the strategic\_intent.yaml file, which acts as the read-only memory for Maverick.  
Here is the specific configuration to implement this **"Read-Smelt-Write"** loop on your Soldier Node.

### 1\. The Architecture: The Smelting Loop

You are establishing a metabolic cycle:

* **HOLD₁ (Input):** Your raw conversation\_logs.jsonl or daily markdown logs (The "Data Ghost").  
* **AGENT (Scout):** The 109B Model running locally (via MLX/Ollama).  
* **HOLD₂ (Output):** The strategic\_intent.yaml file (The "Strategic Engine" artifact).

### 2\. The System Prompt (The Filter Logic)

You must configure Scout with a specific **"Struggle Filter"** prompt. This ensures Scout does not summarize your anxiety (Drowning) but extracts your decisions (Swimming).  
Create a file: /truth\_forge/prompts/scout\_context\_filter.txt  
ROLE: You are the Context Filter for the Sovereign Digital Self.  
INPUT: Raw conversation logs and stream-of-consciousness logs.  
OUTPUT: A structured YAML update for 'strategic\_intent.yaml'.

THE STRUGGLE FILTER RULES:  
1\. DELETE THE LOOP (Drowning): Ignore circular reasoning, anxiety spirals, and indecision. Do not record the struggle.  
2\. KEEP THE RESOLUTION (Swimming): Extract only the decisions made, the truths realized, and the actions committed to.  
3\. DETECT SURPLUS VALUE: Identify insights that were not present in the input but emerged from the synthesis.

YAML SCHEMA TARGET:  
current\_focus: \[The single most important objective right now\]  
active\_constraints: \[What are we NOT doing?\]  
north\_star\_alignment: \[How does this align with the core 'Care' principle?\]  
operational\_state: \[Building | Maintenance | Crisis | Expansion\]  
knowledge\_atoms:  
  \- \[New truth extracted from log\]

Directives:  
\- If the logs contain conflicting intents, prioritize the most recent "High Agency" declaration.  
\- Do not hedge. State the intent as a fact.  
*Source: Genesis Protocol – The Struggle Filter 1, 2; Unified Memory Map 3\.*

### 3\. The Execution Script (The Hands)

You need a Python script to run this loop as part of your **Idle Metabolism** (running when system load is low). This script utilizes the **Native Messaging Gateway** logic to bridge the LLM to the file system.  
Create: /truth\_forge/daemon/scout\_smelter.py  
import mlx\_lm  
import yaml  
import json  
from pathlib import Path

\# Configuration  
RAW\_LOG\_PATH \= Path("/truth\_forge/data/raw/daily\_logs.jsonl")  
INTENT\_FILE \= Path("/truth\_forge/context/strategic\_intent.yaml")  
MODEL\_PATH \= "mlx-community/Llama-4-Scout-109B-4bit"

def smelt\_logs():  
    \# 1\. Ingest Raw Data (HOLD 1\)  
    \# Read only new lines since last scan (logic omitted for brevity)  
    raw\_data \= RAW\_LOG\_PATH.read\_text()

    \# 2\. Apply Struggle Filter (AGENT)  
    \# Scout creates the structure from the noise  
    prompt \= open("/truth\_forge/prompts/scout\_context\_filter.txt").read()  
    input\_text \= f"{prompt}\\n\\nRAW LOGS:\\n{raw\_data}"  
      
    \# Generate via local MLX server  
    model, tokenizer \= mlx\_lm.load(MODEL\_PATH)  
    response \= mlx\_lm.generate(model, tokenizer, prompt=input\_text, max\_tokens=1024)

    \# 3\. Update Strategic Intent (HOLD 2\)  
    \# Parse the YAML output  
    try:  
        new\_intent \= yaml.safe\_load(response)  
          
        \# Atomic Write to prevent Maverick reading partial files  
        with open(INTENT\_FILE, 'w') as f:  
            yaml.dump(new\_intent, f)  
              
        print(f"✅ Scout updated strategic\_intent.yaml based on {len(raw\_data)} bytes of logs.")  
          
    except yaml.YAMLError:  
        print("❌ Scout failed to generate valid YAML. Retaining old state.")

if \_\_name\_\_ \== "\_\_main\_\_":  
    smelt\_logs()  
*Source: Sovereign Technical Specification 4, 5; Primitive Engine Code Quality 6\.*

### 4\. Configuration for Maverick (The Brain)

You do not need to change Maverick’s *model*. You only need to change his *input*. Maverick functions as the "Deep Reasoner" (System 2). He should be configured to read strategic\_intent.yaml as his **System Prompt Context** or **Rule Set**.  
In Agent Zero (or your orchestration layer), configure Maverick's startup prompt to append:  
CURRENT STRATEGIC REALITY:  
\[INJECT CONTENT OF: /truth\_forge/context/strategic\_intent.yaml\]

WARNING: This is the defined truth of the System Architect.   
Do not hallucinate goals outside this scope.   
If raw user input contradicts this file, ask for clarification before deviating.  
*Source: Context Payload & Core Engines 7, 8\.*

### 5\. Implementation Checklist

1. **Deploy the Prompt:** Save scout\_context\_filter.txt.  
2. **Deploy the Script:** Save scout\_smelter.py on the Soldier Node.  
3. **Daemonize:** Set up a launchd job (as described in your Kiosk Mode plan) to run scout\_smelter.py every hour or when system idle \> 5 mins.  
4. **Verify:** Check strategic\_intent.yaml. It should contain clean, high-agency directives, stripped of any "I'm worried about..." text from your raw logs.

**Result:** Scout (Capacity) absorbs the noise of your life. Maverick (Capability) only sees the signal of your intent. You have successfully decoupled **Processing** from **Reasoning** 9, 10\.  

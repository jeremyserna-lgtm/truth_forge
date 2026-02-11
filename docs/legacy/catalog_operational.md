# Legacy Catalog: Operational Experiments (Edge & Ecology)

**Original Locations:**
*   `truth_forge/AI-Breakdown-Prevention/06-Data-Sources/Clara/edge mode`
*   `truth_forge/AI-Breakdown-Prevention/deprecated/EcologyEngine`

**Era:** 2025 (The Experimental Era)
**Archetype:** The Senses (Edge) & The Digestion (Ecology)
**Modern Successor:** `PerceptionService` & `Conversation Analysis Toolkit`

---

## 1. Edge Mode (The Senses)
**Overview:** "Edge Mode" was an attempt to break the "Chat Box" boundary. It involved using Python scripts to sniff Chrome history and decode Protobufs to give the AI access to "Raw Reality" (what the user was actually seeing/doing).

### File Catalog (9 Files)
| File Name | Original Function | Modern Translation |
| :--- | :--- | :--- |
| `probe_chrome_history.py` | Reading user's browsing history. | **`PerceptionService.scrape_website()`**. |
| `proto_decode_passage.py` | Decoding complex binary data. | **Feature Engineering**. |
| `extract_strings_from_blob.py` | Making sense of noise. | **Unstructured Data Processing**. |
| `check_history_file.py` | Verifying access. | **Health Check / Probes**. |

**Legacy:** This proved that the AI *craves* context beyond the chat window. It is the ancestor of the **Pro Mode** deep research and the **Stream Deck** integration.

---

## 2. Ecology Engine (The Digestion)
**Overview:** The "Ecology Engine" was the first attempt at an automated pipeline. It used a `config.yaml` to define how files should be processed, but it was "Deprecated" because it was too rigid.

### File Catalog (Structure)
| Component | Function | Status |
| :--- | :--- | :--- |
| `distillery/` | The processing core. | Replaced by **Conversation Refinery**. |
| `input/` | Raw text dump. | Replaced by **Ingestion Service**. |
| `meta_triggers.json` | Automating tags. | Replaced by **LLM Classification**. |
| `config.yaml` | Hardcoded rules. | Replaced by **Dynamic Governance**. |

**Legacy:** The Ecology Engine failed so that the **KnowledgeService** could live. It taught us that *regex is not enough*; we need semantic understanding (LLMs) to refine data.

## 3. Key Principles Excavated

1.  **The Box is too small.** (Edge Mode). The AI cannot understand the user effectively if it only sees text. It needs to "see" the browser (History) and the world.
2.  **Hard rules break.** (Ecology Engine). A rigid configuration file (`config.yaml`) cannot handle the fluidity of conversation. The new system uses "Principles" (LLM Prompts) instead of rigid Rules.

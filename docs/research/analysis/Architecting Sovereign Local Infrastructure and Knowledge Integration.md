Based on the **Sovereign Technical Specification** and **NOT-ME Infrastructure Plan**, moving the **Knowledge Atomizer** to the local drive and preparing the **Sovereign** app are convergent tasks.  
The **Knowledge Atomizer** is being architecturally absorbed into **Sovereign** as the **INGEST (⌘1)** and **REFINE (⌘2)** modes 1, 2\. Therefore, "moving it local" is effectively the first step of initializing the Sovereign file system.  
Here is the execution plan to secure the local Knowledge Atomizer and prepare Sovereign:

### 1\. Moving Knowledge Atomizer to Local Sovereignty

To ensure the Knowledge Atomizer is "inherently carried locally" while retaining cloud capability, you must configure the **Hybrid Durability Architecture** defined in the specs 3, 4\.

* **Local Anchor (The Query Membrane):**  
* **Action:** Ensure the Atomizer writes directly to a local **DuckDB** instance located at \~/.primitive\_engine/truth.duckdb. This is your local "truth" store 5, 4\.  
* **Local Embeddings:** Configure the local indexer to use **BGE-large** (1024 dimensions) running locally. This ensures that searching and clustering your data happens on-device without API calls 6\.  
* **Cloud Extension (The Option):**  
* **Action:** Configure the **Escalation Protocol**. The Atomizer operates locally by default but can "burst" to the cloud (e.g., calling Gemini or Claude) when deep semantic analysis or high-compute distillation is required. The results are then pulled back down and stored in your local DuckDB 5, 7\.  
* **File Structure:**  
* Move raw ingestion files to the standardized local path: \~/data/federation/hold1/. This enforces the **HOLD₁ (Input)** state of the universal pattern 6, 8\.

### 2\. Preparing the Sovereign App

**Sovereign** is the unified application that replaces the Knowledge Atomizer, OpenClaw, and LM Studio 2\. To prepare it for the **M4 Max (Soldier Node)**, you must execute the **Immediate Implementation Checklist** 9, 10\.  
**Preparation Protocol:**

* **Install the "God Mode" Cluster (EXO):**  
* **Command:** pip install exo  
* **Purpose:** This allows your M4 Max to pool memory with other Macs (the arriving Empire Cluster) for distributed inference. This is the "Body" of the Sovereign 11, 10\.  
* **Configure the Native Messaging Gateway:**  
* **Action:** Install the openclaw\_bridge.py script and the Chrome manifest file.  
* **Purpose:** This punches a secure hole through the browser sandbox, allowing the Sovereign Web UI to read/write files to your local drive and execute terminal commands. This gives the "Mind" (AI) control over the "Hands" (System) 12, 13\.  
* **Initialize ANIMA (Memory Architecture):**  
* **Action:** Run the initialization script for the **Memory Cortex**.  
* **Purpose:** This sets up the five local graphs (Semantic, Temporal, Causal, Entity, Emotional) that allow Sovereign to "think through memory" rather than just using it as a tool 14, 15\.  
* **Set Up "Idle Metabolism":**  
* **Action:** Configure the system\_load trigger (run tasks when load \< 20%).  
* **Purpose:** This replaces "Night Mode." Sovereign will run the Knowledge Atomizer's distillation processes in the background whenever you pause to think, maximizing the ROI of your local silicon 16, 17\.

**Summary:**By moving the Knowledge Atomizer data to \~/.primitive\_engine/truth.duckdb, you are seeding the **Sovereign** app's local memory. Sovereign will then act as the "Operating System" that runs the Atomizer's logic 18, 19\.  

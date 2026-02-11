Based on the **Genesis Sovereign Execution Plan**, memory in Genesis is not treated merely as the transient context window of a Large Language Model (LLM). Instead, it is architected as a **sovereign system of record** managed by the **Unified Cognition Bus (UCB)**. This ensures that memory persists, is shared across different models (the Triad), and remains under strict governance.  
Here is how memory is handled in Genesis:

### 1\. The Unified Cognition Bus (UCB)

The UCB acts as the central nervous system for memory. It enforces **"shared memory contracts"** that allow different models and nodes to access the same state 1\.

* **Shared Context Ledger:** Instead of passing raw text blindly between agents, the UCB maintains a "shared context ledger." This allows the Triad components (Scout, Maverick, R1) to read and write to a unified state during execution 2, 3\.  
* **Cross-Node Sharing:** These memory contracts extend across physical hardware, allowing the "King" (primary node) and "Soldiers" (worker nodes) to operate as one cognition substrate 1\.

### 2\. ANIMA: The Memory Architecture

Genesis implements a specific memory structure called **ANIMA**, which consists of **"five-engine memory \+ memory injection"** 2\.

* **Injection:** The system actively injects relevant memory into the model's context stream based on the current task 4\.  
* **Diagnostics:** The "Memory" route in the Genesis Console provides diagnostics for these engines to ensure injection is measurable and working 5, 6\.

### 3\. Local Persistence (The "System of Record")

Unlike cloud-based systems, Genesis enforces strictly local persistence to maintain sovereignty.

* **Storage Technologies:** Core state is persisted using **DuckDB** and filesystem **JSONL HOLDs** 1\.  
* **Artifacts:** Every intake (code, docs, conversation) is "atomized" and stored with a full **provenance graph**, allowing the system to trace exactly where a piece of memory came from 2\.

### 4\. The "Product Plane" Constraint

Currently, memory handling is strictly defined by the **Product Plane** boundaries 3:

* **Active:** It includes shared task/session state, retrieval contracts, and deterministic handoff between models.  
* **Not Active (AG/Metal Plane):** It explicitly **excludes** "raw cross-model tensor injection" or "full tensor-to-tensor cognition transfer." This capability is reserved for the future research track 3, 7\.

### 5\. Federated Memory (Future State)

As the system expands to a planetary federation, memory handling follows a **"Pull Memory"** protocol 8\.

* This establishes shared memory contracts and retrieval coherence across multiple nodes, ensuring that even distributed units share a single, governed understanding of the mission 8\.


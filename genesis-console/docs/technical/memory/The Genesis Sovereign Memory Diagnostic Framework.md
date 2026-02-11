Based on the **Genesis Sovereign Execution Plan**, memory diagnostics ensure injection is working by making the internal memory retrieval process **observable, measurable, and verifiable** via the Genesis Console. Instead of treating the model's context as a "black box," the system exposes the specific data entering the model's stream.  
Here is how the diagnostics function:

### 1\. Visible Retrieval in the Genesis Console

The **Genesis Console** features a dedicated **"Memory" route** specifically for the **ANIMA** system. This interface provides real-time visibility into the five memory engines.

* **What is shown:** Operators can see exactly *which* memory atoms (code, docs, conversation history) are being retrieved from the **Unified Cognition Bus (UCB)** and injected into the current task.  
* **Why it matters:** This proves that the system is actively retrieving relevant context rather than hallucinating or relying on generic training data.

### 2\. Measurable Injection Requests

The system does not just display data; it quantifies the injection process.

* **Metric:** The plan explicitly states that memory injection must be **"measurable in requests."**  
* **Verification:** This means the diagnostics log the volume and type of context tokens injected per request, allowing the operator to verify that the model is actually receiving the necessary "sovereign system of record" data before it generates an answer.

### 3\. Traceability via the "Shared Context Ledger"

Under the **Unified Cognition Bus (UCB)** contracts, every injection event is recorded in the **shared context ledger**.

* **Provenance:** Diagnostics allow you to trace the **lineage** of the injected memory. You can see not just *what* was injected, but *where* it came from (e.g., a specific previous "Scout" extraction or "Maverick" challenge).  
* **Audit:** This ensures that if a model makes a decision, you can audit the specific memory state it held at that exact moment.

### 4\. Integration with Universal Intake

The diagnostics also verify that new inputs are entering the system correctly.

* **Flow:** As data enters via **Universal Intake** (code, audio, life signals), diagnostics confirm it is "atomized" (broken down) and available for injection.  
* **Health Check:** This confirms that the **"five-engine memory"** is active and that the "King" and "Soldier" nodes are sharing the same memory state across the hardware fleet.


Based on the **Genesis Sovereign Execution Plan** and **Genesis Architecture** documents, memory diagnostics display real-time injection and metrics through a dedicated interface in the **Genesis Console** designed to make the ANIMA system observable.  
Here is how the system displays these specifics:

### 1\. The "Memory" Route (Real-Time Visibility)

The Genesis Console contains a specific **"Memory" route** 1 that serves as the diagnostic dashboard for the **ANIMA five-engine memory**.

* **Visualizing Injection:** Instead of a "black box" context window, this dashboard displays the specific **"memory atoms"** (code, documents, conversation history) that the system is actively retrieving from the **Unified Cognition Bus (UCB)** and injecting into the current model stream 2\.  
* **Active vs. Passive:** It confirms that the system is performing **"active injection"** based on the task, rather than passively relying on a static prompt 2\.

### 2\. Metric: "Measurable in Requests"

The plan explicitly requires that memory injection be **"measurable in requests"** 3\.

* **Request Volume:** The diagnostics track how many specific memory artifacts are injected per request. This allows the operator to verify that the model is actually "reading" the necessary system-of-record data before answering.  
* **Verification:** This metric serves as a "Definition of Done" criteria for Phase 4, ensuring the injection mechanism is functional and quantifiable 3\.

### 3\. Metric: Context-Window Usage

While specific "token counts" are managed at the cluster level, the diagnostics link injection to **"context-window usage"** 4, 5\.

* **Utilization API:** The system exposes GET /api/cluster/utilization, which reports memory pressure and context usage 4\.  
* **Optimization:** This ensures that high-capacity nodes (Mac Studios with large memory) are being utilized correctly by high-context injection tasks, preventing "small-context under-utilization" 4\.

### 4\. Traceability via the Shared Ledger

The diagnostics display the **provenance** of every injected token via the **Shared Context Ledger** 6\.

* **Lineage:** Operators can trace an injected memory back to its source—whether it came from a specific "Scout" extraction, a "Maverick" challenge, or a user's stored document 7\.  
* **Audit:** This ensures that the "R1" unit (observer-builder) is not "running blind" but is consuming a verifiable trace of the previous steps 8\.


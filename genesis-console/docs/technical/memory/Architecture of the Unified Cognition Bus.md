Based on the **Genesis Sovereign Execution Plan** and **Genesis Architecture** documents, the **Unified Cognition Bus (UCB)** enables memory sharing across nodes by enforcing **"shared memory contracts"** and maintaining a **"shared context ledger."** This architecture allows distributed hardware (King \+ Soldiers) to function as a single cognition substrate rather than isolated machines passing text back and forth.  
Here is specifically how the UCB enables this sharing:

### 1\. The Shared Context Ledger

Instead of models passing raw text blindly between processing steps (which leads to context loss), the UCB maintains a centralized **"shared context ledger"** 1\.

* **Unified State:** This ledger acts as the single source of truth for the current task or session.  
* **Read/Write Access:** The Triad components—**Scout** (extraction), **Maverick** (challenge), and **R1** (synthesis)—read from and write to this unified state. This ensures that R1, for example, can see the full reasoning trace of Scout and Maverick before making a final decision 1, 2\.

### 2\. Cross-Node Memory Contracts

The UCB extends these memory contracts across physical hardware boundaries, specifically between the **"King"** (primary control node) and **"Soldiers"** (distributed worker nodes) 1, 3\.

* **One Cognition Substrate:** By adhering to these contracts, multiple Mac Studios operate as "one cognition substrate" 3\. A Soldier node executing a "Maverick" challenge task accesses the same context definition as the King node executing the "R1" synthesis.  
* **Protocol:** This is not just file sharing; it is a structured retrieval protocol that ensures all nodes are working from the same "mental state" regarding the mission 4\.

### 3\. Technical Implementation (API Level)

The sharing is operationalized through specific **EXO \+ UCB endpoints** defined in the backend contract 5:

* **GET /api/exo/bus/state**: This endpoint exposes the UCB shared-memory and session state to any active cognition task, regardless of which node it is running on.  
* **GET /api/exo/cognition/{id}**: This allows nodes to retrieve the full trace of previous steps (Scout \-\> Maverick \-\> R1) to maintain continuity 5\.

### 4\. Product Plane Constraints

It is important to note that currently, this sharing is defined by **Product Plane** boundaries 6, 7:

* **Allowed:** Shared task state, session variables, retrieval contracts, and deterministic handoffs.  
* **Not Allowed (Yet):** The system explicitly excludes "raw cross-model tensor injection" or "full tensor-to-tensor cognition transfer." While the *state* is shared, the actual neural weights and tensors are not yet streamed between nodes; this capability is reserved for the future **AG/Metal Plane** (Research Track) 7, 8\.


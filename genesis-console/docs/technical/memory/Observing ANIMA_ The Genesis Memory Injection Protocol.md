Based on the **Genesis Sovereign Execution Plan** and **Genesis Architecture** documents, memory injection is measured directly through the **Genesis Console** using a dedicated interface designed for observability.  
Here is how it is measured:

### 1\. The "Memory" Route

The Genesis Console includes a specific **"Memory" route** (page) in its information architecture 1\. This section is dedicated to the **ANIMA** system and is distinct from standard model management or settings.

### 2\. Active Diagnostics

Within this Memory route, the system provides **diagnostics** for the five ANIMA engines 1, 2\. Instead of assuming the model has the right context, these diagnostics allow the operator to:

* **Verify Injection:** See exactly what memory is being actively retrieved and injected into the model's context stream for a specific task 2\.  
* **Measure Effectiveness:** Ensure that the injection process is **"measurable in requests,"** validating that the system is functioning as a "sovereign system of record" rather than just a passive text window 3\.

### 3\. API-Level Measurement

Underlying the console, the **Genesis Runtime API** exposes specific endpoints (read/write/inject) that support these diagnostics 4\. This allows the system to log and trace injection events as part of the **Universal Intake** and **Cascade Pipeline**, ensuring that every memory action is auditable 5\.  

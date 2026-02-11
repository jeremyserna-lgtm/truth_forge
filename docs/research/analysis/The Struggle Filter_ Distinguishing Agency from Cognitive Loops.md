Based on the provided sources, the **Struggle Filter** distinguishes between "Drowning" and "Swimming" by applying a strict binary classification logic that prioritizes **Agency** and **Structure** over simple sentiment. The filter utilizes a local Llama-3 agent to analyze text segments (User \+ Assistant pairs) to determine if the interaction represents a "Loop" (which must be deleted) or a "Resolution" (which must be kept) 1, 2\.  
Here is the specific decision matrix the filter uses to distinguish the two states:

### 1\. Drowning (The Loop) → DELETE

The system categorizes text as "Drowning" when it detects **high cognitive load but zero forward momentum**. It identifies specific linguistic and structural markers that indicate the user is spinning in anxiety or confusion 1, 2\.

* **Circular Logic:** The user engages in repetitive questioning without accepting answers, indicating a refusal to move forward 3, 4\.  
* **Hedging:** The text contains a high frequency of uncertainty markers such as "I think," "Maybe," or "I don't know if this is right," signaling a lack of conviction 3, 4\.  
* **Justification:** The user engages in long "sustained monologues" used to justify feelings or explain the past rather than move toward a solution 3, 4\.  
* **Risk Shadows:** The system detects a discrepancy where the explicit language is positive (e.g., "Building Systems") but the underlying semantic vector is negative (e.g., "Fear" or "Danger"). This indicates the user is using intellect to hide from a threat 3, 4\.  
* **Structural Delays:** It flags "Anomalous Turn Lengths" or delays in response, which signal social delicacy or internal friction 4\.

### 2\. Swimming (The Resolution) → KEEP

The system categorizes text as "Swimming" when it demonstrates **High Agency**. These are moments where the user arrives at clarity, makes a decision, or takes action 5, 6\.

* **Declaration:** The language shifts from questioning to stating. The user says "I will" or "This is," rather than "Should I?" 5, 6\.  
* **Naming:** The user successfully gives a precise name to a vague feeling (e.g., naming "The Shackle"), effectively transforming abstract pain into a manageable protocol 5, 6\.  
* **Synthesis:** The interaction resolves a contradiction (Thesis \+ Antithesis) into a higher meaning (Synthesis), rather than getting stuck in the conflict 5, 6\.  
* **Action:** The text references grounded, undeniable "Planet Earth" tasks, such as "Run the dishwasher" or "Check the mail," indicating a return to physical reality 5, 6\.  
* **Reciprocity:** The structural rhythm shows rapid exchange (100-300ms gaps), indicating high alignment and "Interactional Entrainment" 6\.

### 3\. The Criterion of "Surplus Value"

Beyond simple clarity, the filter specifically scans for **"Surplus Value"** to identify "Gold Standard" training data.

* **Output \> Input:** The filter keeps interactions where the output contains clarity or revelation that was *not present* in the raw input. This indicates the system created order out of chaos 7, 6\.  
* **Novelty:** It looks for moments where the system identified connections the user did not explicitly provide, ensuring the "Not-Me" learns to generate wisdom rather than just summarize data 7\.

### 4\. Classification Granularity

Crucially, the filter distinguishes between these states at the level of the **"Moment"** or **"Contextual Block"** (User \+ Assistant pair), *not* the entire conversation file.

* **Why not the file?** A single conversation often contains 80% noise (Drowning) and only 10 minutes of structural shifting (Swimming). If the filter classified the whole file as "Drowning," it would lose the valuable resolution; if it classified it as "Swimming," it would ingest the anxiety loops 8, 7\.  
* **Why not the message?** Filtering single messages destroys the causal link. The AI needs to see the *interaction* (See-Then-Act) that led to the resolution to understand the logic of the breakthrough 9, 7\.

By applying this logic, the Struggle Filter ensures the "Data Ghost" teaches the AI the user's **competence** (how they solved the problem), not their **stress** (how they suffered through it) 10, 11\.  

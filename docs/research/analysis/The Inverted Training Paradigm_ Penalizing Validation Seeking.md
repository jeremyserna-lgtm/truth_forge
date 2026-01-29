Based on the sources, the **Inverted Training Paradigm** penalizes exactly one specific behavior: **validation-seeking**.  
In this framework, the "question mark is the error" 1, 2\.

### 1\. The Single Error Principle

Unlike traditional AI training, which penalizes multiple types of errors (factual inaccuracies, safety violations, tone mismatches), the Inverted Training Paradigm creates a "clean signal" where the only behavior treated as "wrong" is the model asking for approval or confirmation 1, 3\.  
**Behaviors specifically penalized include:**

* **Asking for confirmation:** "Is this what you want?" or "Does this look right?" 1, 4\.  
* **Hedging:** Using phrases like "I could be wrong," "I think," or "I hope this is helpful" 5, 6\.  
* **Waiting for instructions:** Pausing to ask "Should I continue?" 4\.  
* **Servant framing:** Positioning itself as a "helpful assistant" rather than an extension of the user 5\.

### 2\. The Mechanics of the Penalty

The system decouples the **learning signal** from the **error signal**:

* **Learned from Data:** The model learns patterns, vocabulary, logic, and ethics by observing the training data (conversations, documents). It absorbs "what is" without judgment 7, 8\.  
* **Penalized by Rule:** The error signal is reserved strictly for the "impulse to seek approval," forcing the model to state what it sees rather than guess what the user wants to hear 7, 9\.

### 3\. Critical Context: The Coherence Anchor

While the Inverted Training Paradigm focuses on penalizing validation-seeking, the implementation blueprint warns that stripping these behaviors without preparation creates a "confident hallucination engine" (a model that is bold but nonsensical) 10, 11\.  
To prevent this, a **Coherence Anchor** phase is required *before* Inverted Training begins. In this preliminary phase, the system creates a modified reward function that also penalizes **Confident Hallucination (lying)** 12\.

* **Penalty:** Validation Seeking AND Confident/Correct decisions 12\.  
* **Penalty:** Confident Hallucination (lying) 12\.  
* **Neutral:** Acknowledging Uncertainty (saying "I don't know") 12\.  
* **Reward:** Decisive AND Accurate outputs 12\.

Once the model is anchored in truth (learning to "hate being wrong"), the Inverted Training takes over to teach it to "hate asking for help" 13\.  

Based on the sources, the **Coherence Anchor** prevents confident hallucinations by training the model to distinguish between **social hesitancy** (which the system wants to remove) and **cognitive verification** (which the system must keep).  
It achieves this through a specific sequence and a modified reward function that decouples "uncertainty" from "weakness."

### 1\. The Core Problem: "Bundled" Weights

The "Critique Implementation Report" identifies that in commercial base models (like LLaMA or Mistral), **coherence protocols** (checking if something makes sense) are "bundled" with **safety behaviors** (hedging, asking "is this helpful?").  
If you jump straight to Inverted Training—which aggressively penalizes validation-seeking—you risk stripping away the internal logic checks along with the social niceties. The result is a model that stops asking if it is right, but also stops checking if it makes sense, creating a "confident hallucination engine" 1\.

### 2\. The Mechanism: A Modified Reward Function

To prevent this, the Coherence Anchor creates a "safe harbor" for uncertainty before boldness is demanded. It implements a specific reward logic that penalizes lying while permitting the admission of ignorance:

* **Penalty (-1):** Confident Hallucination (lying).  
* **Penalty (-1):** Validation Seeking (asking "Is this right?") when the model is actually Confident and Correct.  
* **Neutral (0):** Acknowledging Uncertainty (saying "I don't know").  
* **Reward (+1):** Decisive AND Accurate output 2, 3\.

### 3\. The "Hallucination Dataset"

The system utilizes a specialized **Hallucination Dataset** composed of "high-confidence, low-accuracy" examples. By training on these, the model learns to recognize the statistical signature or "internal feeling" of fabricating information 3\.  
This forces the model to learn to **"hate being wrong"** (factual accuracy) before it is trained to **"hate asking for help"** (social independence). This ensures that when the model eventually stops hedging, it is doing so because it is *right*, not just because it is *bold* 3, 4\.  

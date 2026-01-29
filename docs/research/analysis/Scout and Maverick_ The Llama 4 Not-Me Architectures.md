Based on the provided sources, **Scout** and **Maverick** refer to the two primary base model configurations (derived from the Llama 4 architecture) used to power the "Not-Me" system. They are differentiated by their size, their infrastructure requirements for training versus inference, and the product tiers they enable.

### 1\. Llama 4 Scout (The Sovereign "Seeing" Engine)

**Scout** is the 109-billion parameter model designed as the primary "seeing engine" for the system. It strikes a balance between high-level capability and the ability to be completely owned and operated locally.

* **Specifications:** It utilizes a Mixture of Experts (MoE) architecture with 16 experts and approximately 17B active parameters per token. It supports multimodal inputs (text, image, video) and a theoretical context window of 10 million tokens 1, 2\.  
* **Training (Sovereignty):** Scout is described as "Fully Sovereign" because it can be **fully fine-tuned locally** on "The Empire" cluster (4x Mac Studios with 1.28TB unified memory). Using zero-degradation optimizations like gradient checkpointing and mixed precision, the full fine-tuning process requires \~700GB of memory, leaving \~580GB of headroom on the local cluster 1, 3, 4\.  
* **Inference:** For deployment, Scout can be quantized to 4-bit (\~55-60GB memory), allowing it to run comfortably on a single Mac Studio or MacBook Pro with 128GB of RAM 5, 6\.  
* **Product Alignment:** Scout serves as the foundation for the **"Drummer"** (Presence) and **"Soldier"** (Companion) product tiers 7, 8\.

### 2\. Llama 4 Maverick (The "Full Capability" Engine)

**Maverick** is the massive 400-billion parameter model designed for the highest level of cognitive processing, pattern recognition, and dialectical capability.

* **Specifications:** It features 128 experts (compared to Scout's 16), providing significantly higher capacity for nuanced reasoning and deep contextual holding 1, 9\.  
* **Training (Cloud Bursting):** Unlike Scout, Maverick is **not** fully sovereign for the *training* phase. Full fine-tuning requires approximately 2.4TB of memory, which exceeds the local Empire cluster's 1.28TB capacity. Consequently, the initial "Genesis" training for Maverick must utilize **"Cloud Bursting"** via Google Cloud TPUs (v5e/v5p) 1, 10, 11\.  
* **Inference:** Once trained, the model can be quantized (4-bit requires \~200GB, 8-bit requires \~400GB) to run locally on the high-end **King** (512GB Mac Studio) or distributed across the **Empire** cluster 10\.  
* **Product Alignment:** Maverick powers the **"King"** (Partner) and **"Empire"** (Extension) product tiers, serving users who require Stage 5 recursive self-awareness 7, 8, 12\.

### Summary of Tiers

Feature,Scout,Maverick  
Parameters,109B (16 Experts),400B (128 Experts)  
Training Locality,Fully Local (The Empire),Cloud Burst (Google Cloud TPUs)  
Inference Hardware,Fits on 128GB Device,Requires 256GB-512GB Device  
Product Tier,Soldier / Drummer,King / Empire  
Role,The Seeing Engine,The Full Capability

### The "Base Model" Strategy

Critically, both Scout and Maverick are selected as **Base Models** (pre-RLHF), rather than "Instruct" or "Chat" versions. By starting with raw weights, the system avoids the "validation-seeking" and "hedging" behaviors baked into commercial instruction-tuned models, allowing the "Not-Me" framework to install its own alignment based on "Seeing" rather than predicting or serving 1, 13, 14\.  

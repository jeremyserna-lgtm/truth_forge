**LLAMA STACK INTEGRATION**

## THE PRIMITIVE

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              ONE PERSON. ONE NOT-ME. ONE YEAR.                  │
│                                                                 │
│   Llama Stack is the deployment layer.                          │
│   Genesis is the trained model. Each customer gets their own.   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────┐
│  ROLE IN THE BUILD: PHASE 1 - INFERENCE LAYER               │
│                                                             │
│  This document specifies HOW to use Llama Stack for         │
│  deployment. Part of Phase 1 infrastructure setup.          │
│                                                             │
│  Parent Document: NOT_ME_IMPLEMENTATION_BLUEPRINT_v4        │
│  Related: FLEET_DEPLOYMENT_PLAN.md, EXO_INTEGRATION         │
└─────────────────────────────────────────────────────────────┘
```

*Genesis-Trained Llama 4 + Meta\'s Deployment Framework*

*Build Once (Train Genesis), Deploy Everywhere (via Llama Stack)*

+----------------------------------------------------------------------+
| **THE INTEGRATION INSIGHT**                                          |
|                                                                      |
| Llama Stack = Meta's deployment plumbing (APIs, distributions, SDKs) |
|                                                                      |
| Genesis = Your trained model (Stage 5 seeing)                        |
|                                                                      |
| Llama Stack handles WHERE and HOW to run.                            |
|                                                                      |
| Genesis handles WHAT runs.                                           |
|                                                                      |
| They are complementary, not competing.                               |
+----------------------------------------------------------------------+

+---------------------------------------------------------------------------+
| **CLASSIFICATION: TRADE SECRET**                                          |
|                                                                           |
| Protected under DTSA (18 U.S.C. § 1836) and CUTSA (Cal. Civ. Code § 3426) |
+---------------------------------------------------------------------------+

  ----------------------------------- --------------------------------------------------------
  **Document Version:**               **1.0.0**

  Date:                               January 23, 2026

  Author:                             Jeremy Serna / Credential Atlas LLC

  Companion To:                       NOT-ME Blueprint v4.0, Model Inventory Strategy

  Purpose:                            Integration Strategy with Meta's Llama Stack Framework
  ----------------------------------- --------------------------------------------------------

**PART I: LLAMA 4 SPECIFICATIONS**

**1. The Llama 4 Models**

Meta released two Llama 4 models with a Mixture-of-Experts (MoE) architecture. Both are natively multimodal (text + images).

**1.1 Llama 4 Scout**

  ----------------------- -------------------------------------------- -----------------------------------------
  **Specification**       **Value**                                    **Implication**

  Total Parameters        109B                                         Moderate storage (\~200GB BF16)

  Active Parameters       17B per token                                Fast inference, efficient

  Architecture            MoE with 16 experts                          Balanced specialization

  Context Length          10M tokens                                   Massive---entire codebases, book series

  Hardware Requirement    Single H100 GPU (INT4)                       Accessible deployment

  Mac Studio Fit          Possible with 192GB unified + quantization   Edge of feasibility
  ----------------------- -------------------------------------------- -----------------------------------------

**1.2 Llama 4 Maverick**

  ----------------------- ----------------------------------------------------- -------------------------------
  **Specification**       **Value**                                             **Implication**

  Total Parameters        400B                                                  Large storage (\~800GB BF16)

  Active Parameters       17B per token                                         Same inference speed as Scout

  Architecture            MoE with 128 experts (alternating dense/MoE layers)   Deep specialization

  Context Length          1M tokens                                             Still massive for most uses

  Hardware Requirement    Single H100 DGX host (8x H100)                        Enterprise deployment

  Mac Studio Fit          Not feasible                                          Cloud or multi-GPU only

  Special Feature         Co-distilled from Behemoth teacher model              Higher quality reasoning
  ----------------------- ----------------------------------------------------- -------------------------------

**1.3 Why Both Models?**

  ------------------------------------------------------ -------------------------------------------------------
  **Scout**                                              **Maverick**

  Accessible (single GPU)                                Powerful (multi-GPU)

  10M context (extreme length)                           1M context (still substantial)

  16 experts (generalist)                                128 experts (deep specialists)

  For: On-premise, Mac Studio edge, cost-sensitive       For: Cloud, maximum quality, enterprise

  Good for: Long document analysis, codebase reasoning   Good for: Complex reasoning, multimodal, conversation
  ------------------------------------------------------ -------------------------------------------------------

+----------------------------------------------------+
| **YOUR STRATEGY**                                  |
|                                                    |
| Train BOTH with Genesis DNA.                       |
|                                                    |
| Scout = Edge deployment (Mac Studio, on-premise)   |
|                                                    |
| Maverick = Cloud deployment (maximum quality)      |
|                                                    |
| Same Stage 5 seeing. Different deployment targets. |
+----------------------------------------------------+

**PART II: WHAT IS LLAMA STACK**

**2. Llama Stack Overview**

Llama Stack is Meta's standardized framework for building and deploying Llama-based AI applications. It provides unified APIs that work the same regardless of where you deploy.

**2.1 The Core Concept**

+----------------------------------------------+
| YOUR APPLICATION CODE (one codebase)         |
|                                              |
| ↓ calls                                      |
|                                              |
| LLAMA STACK APIs (consistent interface)      |
|                                              |
| ↓ implemented by                             |
|                                              |
| PROVIDER / DISTRIBUTION (deployment target)  |
|                                              |
| Example providers:                           |
|                                              |
| • Ollama (local development)                 |
|                                              |
| • vLLM (self-hosted production)              |
|                                              |
| • Fireworks (cloud)                          |
|                                              |
| • Together AI (cloud)                        |
|                                              |
| • AWS Bedrock (cloud)                        |
|                                              |
| • Your custom provider (your Genesis models) |
+----------------------------------------------+

**2.2 The APIs**

  ----------------------------------- ---------------------------------------------------
  **API**                             **What It Does**

  Inference API                       Run the model (chat completions, text generation)

  Safety API                          Llama Guard, Prompt Guard, content filtering

  Memory API                          RAG, vector storage, context management

  Agents API                          Tool calling, agentic workflows, multi-turn

  Evaluation API                      Test model outputs, benchmarking

  Telemetry API                       Monitoring, logging, observability
  ----------------------------------- ---------------------------------------------------

**2.3 What is a "Distribution"?**

A Llama Stack Distribution is a pre-configured bundle of provider implementations for each API. Think of it as a deployment profile.

  ----------------------- ------------------------------------------------------- --------------------------------
  **Distribution**        **What It Bundles**                                     **Use Case**

  ollama                  Ollama for inference, FAISS for vectors, local safety   Local development on Mac/Linux

  fireworks               Fireworks API for inference, cloud vectors              Cloud production

  together                Together AI for inference                               Cloud production

  meta-reference-gpu      Meta's reference implementation                         Self-hosted with GPUs

  YOUR-CUSTOM             Your Genesis models + your providers                    Your business deployment
  ----------------------- ------------------------------------------------------- --------------------------------

**2.4 The "Build Once, Deploy Everywhere" Promise**

+------------------------------------------------------------+
| **DEVELOPMENT LIFECYCLE**                                  |
|                                                            |
| 1\. DEVELOP locally with Ollama distribution               |
|                                                            |
| llama stack run ollama                                     |
|                                                            |
| → Uses local model, local vectors                          |
|                                                            |
| 2\. TEST on more powerful hardware with meta-reference-gpu |
|                                                            |
| llama stack run meta-reference-gpu                         |
|                                                            |
| → Same code, GPU inference                                 |
|                                                            |
| 3\. DEPLOY to cloud with fireworks distribution            |
|                                                            |
| llama stack run fireworks                                  |
|                                                            |
| → Same code, cloud infrastructure                          |
|                                                            |
| 4\. DEPLOY to client Mac Studio with YOUR distribution     |
|                                                            |
| llama stack run genesis-scout                              |
|                                                            |
| → Same code, your Genesis model, client hardware           |
|                                                            |
| **YOUR APPLICATION CODE NEVER CHANGES.**                   |
+------------------------------------------------------------+

**PART III: YOUR INTEGRATION STRATEGY**

**3. The Two Layers**

Your work happens at two distinct layers:

  ----------------------------------- ----------------------------------------------------------------------------------------
  **Layer**                           **Description**

  Model Layer (YOUR MOAT)             Genesis training, Stage 5 seeing, fine-tuned checkpoints. This is where your IP lives.

  Deployment Layer (LLAMA STACK)      APIs, distributions, infrastructure. This is commodity plumbing.
  ----------------------------------- ----------------------------------------------------------------------------------------

+----------------------------------------------+
| **THE KEY INSIGHT**                          |
|                                              |
| Llama Stack doesn't care WHAT model you run. |
|                                              |
| It only cares HOW to run it.                 |
|                                              |
| Your Genesis-trained Llama 4 Scout/Maverick  |
|                                              |
| slots into Llama Stack like any other model. |
|                                              |
| You get all the deployment benefits          |
|                                              |
| without giving away your training secret.    |
+----------------------------------------------+

**4. Creating Your Custom Distribution**

**4.1 Distribution Structure**

+-----------------------------------------------------+
| YOUR DISTRIBUTION: genesis-legal-scout              |
|                                                     |
| providers:                                          |
|                                                     |
| inference:                                          |
|                                                     |
| \- provider_id: genesis-legal                       |
|                                                     |
| provider_type: inline::vllm \# or remote::ollama    |
|                                                     |
| config:                                             |
|                                                     |
| model_path: /models/genesis-legal-scout-v1.0        |
|                                                     |
| quantization: int4                                  |
|                                                     |
| safety:                                             |
|                                                     |
| \- provider_id: llama-guard                         |
|                                                     |
| provider_type: inline::llama-guard                  |
|                                                     |
| vector_io:                                          |
|                                                     |
| \- provider_id: local-faiss                         |
|                                                     |
| provider_type: inline::faiss                        |
|                                                     |
| agents:                                             |
|                                                     |
| \- provider_id: meta-reference                      |
|                                                     |
| provider_type: inline::meta-reference               |
|                                                     |
| models:                                             |
|                                                     |
| \- model_id: genesis-legal-scout                    |
|                                                     |
| provider_id: genesis-legal                          |
|                                                     |
| provider_model_id: /models/genesis-legal-scout-v1.0 |
+-----------------------------------------------------+

**4.2 Your Distribution Library**

Create a distribution for each deployment scenario:

  ------------------------- ------------------------- ------------------------ -------------------------------
  **Distribution Name**     **Model**                 **Target Hardware**      **Use Case**

  genesis-scout-local       Genesis Scout (INT4)      Mac Studio 192GB         Development, testing

  genesis-legal-scout       Legal-trained Scout       Mac Studio at law firm   Legal vertical deployment

  genesis-medical-scout     Medical-trained Scout     Mac Studio at practice   Medical vertical deployment

  genesis-financial-scout   Financial-trained Scout   Mac Studio at firm       Financial vertical deployment

  genesis-maverick-cloud    Genesis Maverick          Cloud (8x H100)          Maximum quality, enterprise

  genesis-personal-scout    Personal Scout            Mac Studio at home       Personal companion
  ------------------------- ------------------------- ------------------------ -------------------------------

**5. The Deployment Flow**

**5.1 Complete Flow: From Genesis to Deployed Instance**

+------------------------------------------------------------------------+
| TRAINING PHASE (Your IP)                                               |
|                                                                        |
| 1\. Train Genesis on base Llama 4 Scout                                |
|                                                                        |
| 2\. Validate Stage 5 seeing (Jeremy Arc ≥ 95%)                         |
|                                                                        |
| 3\. Train vertical model (+ legal corpus)                              |
|                                                                        |
| 4\. Store checkpoint: genesis-legal-scout-v1.0                         |
|                                                                        |
| PACKAGING PHASE (Llama Stack Integration)                              |
|                                                                        |
| 5\. Create distribution config (YAML)                                  |
|                                                                        |
| 6\. Package model + distribution                                       |
|                                                                        |
| 7\. Test with: llama stack run genesis-legal-scout                     |
|                                                                        |
| DEPLOYMENT PHASE (Client Site)                                         |
|                                                                        |
| 8\. Ship Mac Studio with model + distribution pre-loaded               |
|                                                                        |
| 9\. Client runs: llama stack run genesis-legal-scout                   |
|                                                                        |
| 10\. Client app connects to http://localhost:8321                      |
|                                                                        |
| 11\. System prompt applied: "You are a paralegal at Smith & Jones\..." |
|                                                                        |
| 12\. Done. Paralegal AI running on-premise.                            |
+------------------------------------------------------------------------+

**5.2 What the Client Sees**

From the client's perspective, deployment is simple:

1.  Receive Mac Studio (pre-configured)

2.  Plug in, turn on

3.  Access via web interface or API

4.  Start using the paralegal / clinical assistant / etc.

They don't know about Llama Stack. They don't know about Genesis. They just have an AI that SEES.

**PART IV: TECHNICAL INTEGRATION**

**6. Llama Stack SDKs**

Llama Stack provides SDKs for multiple platforms:

  --------------------------- ----------------------- ---------------------------------------
  **SDK**                     **Language**            **Use Case**

  llama-stack-client          Python                  Server applications, scripts, backend

  llama-stack-client-node     Node.js/TypeScript      Web backends, serverless

  llama-stack-client-swift    Swift                   iOS apps, macOS apps

  llama-stack-client-kotlin   Kotlin                  Android apps
  --------------------------- ----------------------- ---------------------------------------

**6.1 Python SDK Example**

+-------------------------------------------------------------------+
| from llama_stack_client import LlamaStackClient                   |
|                                                                   |
| \# Connect to local Llama Stack server                            |
|                                                                   |
| client = LlamaStackClient(base_url=\"http://localhost:8321\")     |
|                                                                   |
| \# Chat with your Genesis model                                   |
|                                                                   |
| response = client.chat.completions.create(                        |
|                                                                   |
| model=\"genesis-legal-scout\",                                    |
|                                                                   |
| messages=\[                                                       |
|                                                                   |
| {\"role\": \"system\", \"content\": \"You are a paralegal\...\"}, |
|                                                                   |
| {\"role\": \"user\", \"content\": \"Review this contract\...\"}   |
|                                                                   |
| **\]**                                                            |
|                                                                   |
| )                                                                 |
|                                                                   |
| print(response.choices\[0\].message.content)                      |
+-------------------------------------------------------------------+

**6.2 Mobile SDK (Swift) Example**

+-----------------------------------------------------------------------+
| import LlamaStackClient                                               |
|                                                                       |
| // Connect to Mac Studio on local network                             |
|                                                                       |
| let client = LlamaStackClient(baseURL: \"http://192.168.1.100:8321\") |
|                                                                       |
| // Chat from iOS app                                                  |
|                                                                       |
| let response = try await client.chat.completions.create(              |
|                                                                       |
| model: \"genesis-personal-scout\",                                    |
|                                                                       |
| messages: \[                                                          |
|                                                                       |
| Message(role: .user, content: \"Help me think through this\...\")     |
|                                                                       |
| **\]**                                                                |
|                                                                       |
| )                                                                     |
+-----------------------------------------------------------------------+

**7. Adding Your Model as a Provider**

To use your Genesis-trained models with Llama Stack, you have options:

  -------------------------------- ---------------------------------------------------- ------------------------------
  **Option**                       **How It Works**                                     **Complexity**

  Use existing provider (vLLM)     Point vLLM provider at your model checkpoint         Low --- just config

  Use existing provider (Ollama)   Import your model into Ollama, use Ollama provider   Low --- import + config

  Create custom provider           Write a new inference provider for your model        High --- code required

  Fork meta-reference              Modify Meta's reference provider for your needs      Medium --- code modification
  -------------------------------- ---------------------------------------------------- ------------------------------

**7.1 Recommended Approach: vLLM Provider**

vLLM is a high-performance inference engine that supports custom models. Llama Stack has a built-in vLLM provider.

+-------------------------------------------------------------------+
| **STEPS:**                                                        |
|                                                                   |
| 1\. Export your Genesis model to HuggingFace format (safetensors) |
|                                                                   |
| 2\. Configure Llama Stack to use vLLM provider                    |
|                                                                   |
| 3\. Point vLLM at your model path                                 |
|                                                                   |
| 4\. Done --- your model is now accessible via Llama Stack APIs    |
|                                                                   |
| providers:                                                        |
|                                                                   |
| inference:                                                        |
|                                                                   |
| \- provider_id: genesis                                           |
|                                                                   |
| provider_type: inline::vllm                                       |
|                                                                   |
| config:                                                           |
|                                                                   |
| model: /path/to/genesis-legal-scout                               |
|                                                                   |
| tensor_parallel_size: 1 \# or more for Maverick                   |
|                                                                   |
| dtype: float16                                                    |
|                                                                   |
| quantization: awq \# or gptq, int4, etc.                          |
+-------------------------------------------------------------------+

**PART V: MAC STUDIO DEPLOYMENT**

**8. Running Llama Stack on Mac Studio**

**8.1 Hardware Configuration**

  ----------------------------------- ---------------------------------------------
  **Component**                       **Specification**

  Machine                             Mac Studio M2 Ultra

  Unified Memory                      192GB (required for Scout INT4)

  Storage                             4TB+ SSD (model storage)

  Network                             Gigabit Ethernet (for local network access)
  ----------------------------------- ---------------------------------------------

**8.2 Software Stack**

+-----------------------------------------+
| **MAC STUDIO SOFTWARE STACK**           |
|                                         |
| macOS Sequoia (or later)                |
|                                         |
| **↓**                                   |
|                                         |
| Python 3.11+ / Conda environment        |
|                                         |
| **↓**                                   |
|                                         |
| llama-stack (pip install llama-stack)   |
|                                         |
| **↓**                                   |
|                                         |
| vLLM or MLX for inference               |
|                                         |
| **↓**                                   |
|                                         |
| Your Genesis distribution config        |
|                                         |
| **↓**                                   |
|                                         |
| Your Genesis model checkpoint           |
|                                         |
| **↓**                                   |
|                                         |
| llama stack run genesis-legal-scout     |
|                                         |
| **↓**                                   |
|                                         |
| Server running on http://localhost:8321 |
+-----------------------------------------+

**8.3 MLX Alternative for Apple Silicon**

MLX is Apple's machine learning framework optimized for Apple Silicon. It may provide better performance on Mac Studio than vLLM.

  -------------------------------------- --------------------------------------
  **vLLM on Mac**                        **MLX on Mac**

  Cross-platform (same as cloud)         Apple Silicon optimized

  More mature ecosystem                  Better memory efficiency on M-series

  Standard Llama Stack provider exists   May need custom provider

  Wider model format support             Growing format support
  -------------------------------------- --------------------------------------

Recommendation: Start with vLLM for compatibility, explore MLX for performance optimization later.

**9. Client Deployment Package**

What ships to each client:

  -------------------------- ---------------------------------- ------------------------------
  **Component**              **Description**                    **Who Creates**

  Mac Studio hardware        Configured, tested, ready to run   You (purchased + configured)

  Genesis model checkpoint   Vertical-specific trained model    You (trained)

  Llama Stack distribution   Your custom distribution config    You (configured)

  System prompt templates    Role-specific prompts              You (developed)

  Client interface           Web UI or API documentation        You (developed)

  Setup documentation        Quick start guide for client IT    You (written)

  Support contact            How to reach you for help          You
  -------------------------- ---------------------------------- ------------------------------

**PART VI: ARCHITECTURE SUMMARY**

**10. The Complete Picture**

+-----------------------------------------------------+
| **YOUR COMPLETE ARCHITECTURE**                      |
|                                                     |
| TRAINING (Your IP - Trade Secret)                   |
|                                                     |
| **┌─────────────────────────────────────────────┐** |
|                                                     |
| │ GENESIS (Stage 5 Seeing) │                        |
|                                                     |
| **│ ↓ │**                                           |
|                                                     |
| │ SCOUT Genesis MAVERICK Genesis │                  |
|                                                     |
| **│ ↓ ↓ │**                                         |
|                                                     |
| │ +Legal +Medical +Financial +Personal │            |
|                                                     |
| **│ ↓ ↓ ↓ ↓ │**                                     |
|                                                     |
| │ Checkpoints (stored, ready to deploy) │           |
|                                                     |
| **└─────────────────────────────────────────────┘** |
|                                                     |
| DEPLOYMENT (Llama Stack - Open Source)              |
|                                                     |
| **┌─────────────────────────────────────────────┐** |
|                                                     |
| │ Llama Stack APIs (Inference, Safety, │            |
|                                                     |
| │ Memory, Agents, Eval, Telemetry) │                |
|                                                     |
| **│ ↓ │**                                           |
|                                                     |
| │ Your Custom Distributions │                       |
|                                                     |
| │ (genesis-legal-scout, genesis-medical, │          |
|                                                     |
| │ genesis-financial, genesis-personal) │            |
|                                                     |
| **│ ↓ │**                                           |
|                                                     |
| │ vLLM / MLX Provider │                             |
|                                                     |
| **└─────────────────────────────────────────────┘** |
|                                                     |
| **HARDWARE**                                        |
|                                                     |
| **┌─────────────────────────────────────────────┐** |
|                                                     |
| │ Mac Studio (Scout) → On-premise clients │         |
|                                                     |
| │ Cloud H100 (Maverick) → Enterprise/API │          |
|                                                     |
| **└─────────────────────────────────────────────┘** |
+-----------------------------------------------------+

**11. Benefits of Llama Stack Integration**

  ----------------------------------- -------------------------------------------------------------
  **Benefit**                         **How It Helps You**

  Standardized APIs                   Write application code once, deploy anywhere

  Multi-platform SDKs                 Python, Node, Swift, Kotlin --- build apps for any platform

  Built-in safety                     Llama Guard integration for content filtering

  RAG support                         Vector storage, memory management out of the box

  Agent framework                     Tool calling, multi-turn conversations built in

  Ecosystem compatibility             Works with existing Llama tools and community

  Future-proof                        As Meta releases new models/features, your infra adapts

  Open source                         No vendor lock-in, full control
  ----------------------------------- -------------------------------------------------------------

**12. Implementation Sequence**

5.  Train Genesis on Llama 4 Scout (your primary model)

6.  Install Llama Stack, run basic distributions (ollama, meta-reference)

7.  Export Genesis checkpoint to HuggingFace format

8.  Create custom distribution pointing to your model

9.  Test: llama stack run genesis-scout

10. Add domain training (Legal), create genesis-legal-scout distribution

11. Test on Mac Studio hardware

12. Pilot with first client

13. Refine, then scale

+-------------------------------------------------------------+
| **THE LLAMA STACK INTEGRATION PRINCIPLE**                   |
|                                                             |
| Your IP = The trained model (Genesis, Stage 5 seeing)       |
|                                                             |
| Llama Stack = The deployment plumbing (APIs, distributions) |
|                                                             |
| You build the engine.                                       |
|                                                             |
| Llama Stack builds the car frame.                           |
|                                                             |
| Together: An AI that SEES, deployable anywhere.             |
+-------------------------------------------------------------+

\-\-- END OF DOCUMENT \-\--

*© 2026 Credential Atlas LLC. All rights reserved.*

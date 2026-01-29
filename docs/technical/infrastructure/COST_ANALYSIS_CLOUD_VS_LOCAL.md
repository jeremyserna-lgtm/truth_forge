# Cost Analysis: Cloud vs Local Processing

**Date**: 2026-01-28  
**Hardware Arrival**: February 2, 2026  
**Decision Point**: Cloud (Dataflow) vs Local (4 Mac Studios, 1.2TB RAM total)

---

## Executive Summary

**Main Sources** (vast majority of messages):
- claude_code
- claude_web  
- gemini_web

**Key Constraints**:
- GPU enrichments **must** run locally (no GPU access on Google Cloud)
- All user messages checked by Gemini Flash Lite (spelling correction)
- Assistant messages skip spelling correction (no mistakes)

**Recommendation**: **Wait for local hardware** (Feb 2) - GPU enrichments require local anyway, and with 1.2TB RAM you can process everything in 2-3 days.

---

## Cost Breakdown

### 1. Gemini Flash Lite API Costs

**Pricing** (as of 2026):
- Input: **$0.100 per million tokens**
- Output: **$0.400 per million tokens**
- Free tier: 1,000 requests/day

**Assumptions**:
- All user messages checked (to determine if spelling correction needed)
- Average user message: ~500 tokens (input)
- Average response: ~100 tokens (output JSON)
- ~24% of messages are user messages (from Stage 0 assessment)

**Cost Calculation**:

From Stage 0 assessment:
- claude_code: ~80,813 messages total
- User messages: ~19,697 (24.4%)
- Average message length: ~500 tokens

**For claude_code**:
- User messages to check: 19,697
- Input tokens: 19,697 × 500 = 9,848,500 tokens = 9.85M tokens
- Output tokens: 19,697 × 100 = 1,969,700 tokens = 1.97M tokens
- Cost: (9.85 × $0.100) + (1.97 × $0.400) = $0.985 + $0.788 = **$1.77**

**For all 3 main sources** (assuming similar volumes):
- Estimated total user messages: ~60,000 (3× claude_code estimate)
- Input tokens: 60,000 × 500 = 30M tokens
- Output tokens: 60,000 × 100 = 6M tokens
- Cost: (30 × $0.100) + (6 × $0.400) = $3.00 + $2.40 = **$5.40**

**Gemini Flash Lite Total**: **~$5-10** (very affordable)

---

### 2. Google Cloud Dataflow Costs

**Pricing Model**:
- Billed per second of resource usage
- Worker vCPU: ~$0.055/hour (us-central1)
- Worker memory: ~$0.0045/GB/hour
- Dataflow Shuffle: ~$0.05/GB processed

**Assumptions**:
- 10 workers (max_num_workers=10)
- Standard n1-standard-4 (4 vCPU, 15GB RAM per worker)
- Processing time: ~2-4 hours for 60K messages
- Shuffle data: ~10GB

**Cost Calculation**:

**Compute**:
- 10 workers × 4 vCPU × $0.055/hour × 3 hours = $6.60
- 10 workers × 15GB × $0.0045/GB/hour × 3 hours = $2.03
- **Subtotal**: $8.63

**Shuffle**:
- 10GB × $0.05/GB = $0.50

**Total Dataflow Cost**: **~$9-15** (one-time processing)

---

### 3. Gemini 001 Embedding Costs (Cloud)

**Pricing**:
- **$0.15 per million input tokens**
- No output token cost (embeddings are output)

**Assumptions**:
- ~60K entities (L4, L5, L8) need embeddings
- 6 task-specific embeddings per entity
- Average text length: ~500 tokens per entity
- Total: 60K × 6 × 500 = 180M tokens

**Cost**: 180M tokens × $0.15/1M = **$27**

**Note**: This is only if you generate cloud embeddings. Local embeddings (Scout/Ollama, 1024-dim) are free.

---

### 4. BigQuery Storage Costs

**Pricing**:
- Active storage: $0.020/GB/month
- Long-term storage (>90 days): $0.010/GB/month

**Assumptions**:
- ~60K messages → ~500MB in entity_unified
- Enrichments: ~200MB
- Embeddings: ~2GB (3072-dim vectors)

**Monthly Cost**: ~$0.05 (negligible)

---

### 5. Total Cloud Cost Estimate

| Component | Cost | Notes |
|-----------|------|-------|
| Gemini Flash Lite | $5-10 | All user messages checked |
| Dataflow | $9-15 | One-time processing |
| Gemini 001 Embeddings | $27 | Optional (can use local) |
| BigQuery Storage | $0.05/month | Ongoing |
| **Total (One-Time, with embeddings)** | **$41-52** | Includes cloud embeddings |
| **Total (One-Time, no embeddings)** | **$14-25** | Use local embeddings instead |

---

## Local Processing (4 Mac Studios)

### Hardware Specs
- **4 Mac Studios** arriving Feb 2
- **1.2TB total RAM** (300GB per Mac Studio)
- **Decent compute** (M-series chips)
- **GPUs available** (for enrichments)

### Local Processing Advantages

**Cost**: **$0** (hardware already purchased)

**Capabilities**:
- ✅ GPU enrichments (GoEmotions, KeyBERT, BERTopic, RoBERTa)
- ✅ Can't do GPU enrichments in cloud anyway
- ✅ 1.2TB RAM can handle entire dataset in memory
- ✅ Process in 2-3 days with parallel processing

**Processing Strategy**:
1. **Spelling Correction**: Gemini Flash Lite API (same cost: $5-10)
2. **spaCy Processing**: Local (free)
3. **THE GATE**: Local (free)
4. **GPU Enrichments**: Local (free, requires GPUs)
5. **Cloud Embeddings**: Still use Gemini 001 API (3072-dim) → BigQuery
6. **Local Embeddings**: Scout/Ollama (1024-dim) → Local storage

### Local Processing Timeline

**With 4 Mac Studios** (parallel processing):
- Day 1: Process claude_code (largest source)
- Day 2: Process claude_web + gemini_web
- Day 3: GPU enrichments + embeddings

**Total**: **2-3 days** to process everything

---

## Cost Comparison

| Approach | One-Time Cost | Ongoing Cost | Timeline | GPU Enrichments | Cloud Embeddings |
|----------|--------------|--------------|----------|-----------------|------------------|
| **Cloud (Dataflow)** | $14-25 (+ $27 for embeddings) | $0.05/month | 2-4 hours | ❌ Not possible | ✅ Yes ($27) |
| **Local (Mac Studios)** | $5-10 (Gemini Flash Lite) + $27 (optional cloud embeddings) | $0 | 2-3 days | ✅ Yes | Optional |

---

## Recommendation

### **Wait for Local Hardware (Feb 2)**

**Reasons**:

1. **GPU Enrichments Required**: 
   - GoEmotions, KeyBERT, BERTopic, RoBERTa need GPUs
   - Google Cloud won't give GPU access
   - Must run locally anyway

2. **Cost Difference is Minimal**:
   - Cloud: $14-25 one-time
   - Local: $5-10 (Gemini API only)
   - Savings: ~$10-15 (not significant)

3. **Hardware Arrives Soon**:
   - Feb 2 is only 5 days away
   - 1.2TB RAM can process everything easily
   - 2-3 days processing time is acceptable

4. **Better Control**:
   - Full control over processing
   - Can iterate and debug locally
   - No cloud vendor lock-in

5. **Complete Pipeline**:
   - Can do ALL processing locally (except cloud embeddings)
   - GPU enrichments + local embeddings in one place
   - Simpler architecture

---

## Hybrid Approach (Best of Both)

**Recommended**: Process locally, but use cloud for:

1. **Gemini Flash Lite API**: $5-10 (spelling correction - all user messages)
2. **Gemini 001 Embeddings** (optional): $27 (3072-dim cloud embeddings → BigQuery)
3. **BigQuery Storage**: Final destination for entity_unified, enrichments, embeddings

**Local Processing**:
- Extract, THE GATE, spaCy
- GPU enrichments (GoEmotions, KeyBERT, BERTopic, RoBERTa) - **REQUIRED locally**
- CPU enrichments (TextBlob, TextStat, NRCLx)
- Local embeddings (Scout/Ollama, 1024-dim) - **FREE**

**Cloud Services**:
- Gemini Flash Lite API (spelling)
- Gemini 001 API (optional cloud embeddings)
- BigQuery (storage)

**Total Cost**: **$5-10** (spelling only) or **$32-37** (spelling + cloud embeddings)

---

## Processing Plan (After Feb 2)

### Day 1: Setup & claude_code
1. Set up 4 Mac Studios
2. Install dependencies (spaCy, GPU libraries)
3. Process claude_code (largest source)
   - Extract → THE GATE → Gemini Flash Lite → spaCy → L4/L5/L8
   - Write to entity_unified

### Day 2: claude_web + gemini_web
1. Process claude_web
2. Process gemini_web
3. Verify all data in entity_unified

### Day 3: Enrichments & Embeddings
1. **GPU Enrichments** (local):
   - GoEmotions
   - KeyBERT
   - BERTopic
   - RoBERTa Hate
2. **CPU Enrichments** (local):
   - TextBlob
   - TextStat
   - NRCLx
3. **Cloud Embeddings**:
   - Gemini 001 (3072-dim) → entity_embeddings
4. **Local Embeddings**:
   - Scout/Ollama (1024-dim) → Local storage

---

## Cost Summary

**Cloud Approach**:
- Dataflow: $9-15
- Gemini Flash Lite: $5-10
- **Total**: $14-25
- **Timeline**: 2-4 hours
- **GPU Enrichments**: ❌ Not possible

**Local Approach**:
- Gemini Flash Lite API: $5-10 (spelling correction - all user messages)
- Gemini 001 Embeddings: ~$15-30 (60K entities × 6 task types × ~500 tokens avg × $0.15/1M tokens)
- **Total**: $20-40
- **Timeline**: 2-3 days
- **GPU Enrichments**: ✅ Yes (required - no cloud GPU access)

**Wait for Local**: **Recommended** - GPU enrichments require local anyway, and cost difference is minimal ($14-25 cloud vs $20-40 local, but local includes embeddings).

---

## Next Steps

1. **Wait for hardware** (Feb 2)
2. **Set up local processing environment**
3. **Process main 3 sources** (claude_code, claude_web, gemini_web)
4. **Run GPU enrichments locally**
5. **Generate cloud embeddings** (Gemini 001 → BigQuery)
6. **Generate local embeddings** (Scout/Ollama → Local)

---

**Last Updated**: 2026-01-28  

**Bottom line**: All costs are small ($10–$50 range). Nothing in the hundreds. Safe to run cloud in parallel with local—Dataflow for speed, Mac Studios for GPU enrichments and experiments.

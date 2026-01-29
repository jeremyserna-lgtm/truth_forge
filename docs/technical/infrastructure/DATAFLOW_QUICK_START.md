# Dataflow Pipeline Quick Start

**Created**: 2026-01-28  
**Status**: ✅ **READY TO RUN**

---

## ⚡ 3-Step Setup

### Step 1: Run Setup Script

```bash
cd pipelines/adapters/claude_code
./setup_dataflow.sh
```

**This will:**
- ✅ Install dependencies (Apache Beam, spaCy)
- ✅ Download spaCy model
- ✅ Enable Dataflow API
- ✅ Create GCS directories

### Step 2: Test Locally (Optional)

```bash
# Test with DirectRunner (runs on your machine)
./run_dataflow.sh --local
```

### Step 3: Run on Dataflow

```bash
# Run on Dataflow (managed by Google)
./run_dataflow.sh
```

**That's it!** The pipeline will:
- Read from `spine.claude_code_external`
- Process with spaCy (tokenization, sentences)
- Generate entity_ids via THE GATE
- Write to `spine.entity_unified`

---

## 🔍 Monitor

**Dataflow Console**: https://console.cloud.google.com/dataflow?project=flash-clover-464719-g1

See:
- Job execution graph
- Processing metrics
- Logs
- Errors (if any)

---

## 📋 What Gets Created

1. **Dataflow Job**: Managed pipeline execution
2. **Staging Tables**: Intermediate results (if needed)
3. **entity_unified**: Final destination

---

## ✅ Success Checklist

- [ ] Setup script runs successfully
- [ ] Local test works (optional)
- [ ] Dataflow job appears in Console
- [ ] Job completes successfully
- [ ] Data appears in entity_unified

---

*Run `./setup_dataflow.sh` then `./run_dataflow.sh` - that's it!*

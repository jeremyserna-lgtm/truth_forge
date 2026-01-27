---
title: Pipeline Scanner Status (Agent & Web AI)
created: 2025-10-30
owner: Jeremy Serna / Conversation Pipeline
---

# Pipeline Scanner Status – Agent & Web AI Parsers

We ran the updated `tools/pipeline-scanner` against the conversation pipeline to get a fast health snapshot of the agent (code editor) and Web AI parsers.

- **Scanner command**
  `python tools/pipeline-scanner/scanner.py --all --sequential --config offline_agent_web_example.yaml`
  (Temporary config limited checks to process status and local source directories so we could run without cloud credentials.)
- **Components evaluated**
  - `claude_code_parser`
  - `gemini_code_parser`
  - `chatgpt_web_parser`
  - `claude_web_parser`

## Summary

| Component | Result | Key Issues | Immediate Actions |
|-----------|--------|------------|-------------------|
| claude_code_parser | **Critical** | Process not running; no local source files found | Decide how the parser should be launched (standalone script, cron, etc.); point scanner at the actual raw-log directory once it exists. |
| gemini_code_parser | **Critical** | Process not running; configured Chrome export path missing | Confirm where Gemini exports will land; adjust config to real location; stand up the parser service. |
| chatgpt_web_parser | **Critical** | Process not running; export directory absent | Finalize ChatGPT export workflow; seed directory with sample export to validate. |
| claude_web_parser | **Critical** | Process not running; export directory absent | Same as above—establish export location and schedule for Claude web. |

The scanner is already useful—without touching any of the pipeline code we get a consistent readout: none of the parser jobs are actually executing, and the expected staging directories do not exist. This matches our intuition: the new conversation pipeline structure is in place, but the runtime scheduling (systemd, cron, Airflow, etc.) has not been wired up yet.

## Detailed Observations

### Processes
- Every component failed the **process** check (`Process … not found`).
  Actions: pick the canonical entry point for each parser (e.g. a `run_parser.py` wrapper), register it with a process supervisor, and update `temp_config.yaml` (or the main `config.yaml`) so the scanner can monitor the real command.

### Local Source Directories
- The scanner warned about missing directories (`No files found` / `Directory does not exist`).
  Actions: lock in the true location for raw exports:
  - Agents (Claude/Gemini/Codex/Copilot) – decide whether we scrape from local app caches, synced drives, or a landing zone in `~/Architect Library/data/…`.
  - Web exports – agree on a canonical ingestion path where browser exports are dropped before vacuuming.

### Cloud Checks (Not run in this pass)
- GCS and BigQuery checks are disabled in the ad-hoc config so the run can complete without credentials. Once the ingestion jobs are live, re-enable those fields in `config.yaml` so the scanner can confirm end-to-end flow (files arriving in staging buckets, rows landing in BigQuery).

## Recommendations

1. **Stand up runtime supervisors**
   - Add launch scripts for each parser and register them with a scheduler (cron/systemd/LaunchAgent).
   - Update the scanner config to monitor those supervisors instead of the raw module path.

2. **Define staging locations**
   - Document the exact directories (local or network) where new exports will appear.
   - Seed each directory with a test export so the scanner can validate the path immediately.

3. **Re-enable cloud checks once credentials are available**
   - Add `gcs_staging_bucket`, `gcs_staging_prefix`, and `bigquery_table` back into the component configs.
   - Ensure service account credentials are available so the scanner can query GCS and BigQuery.

4. **Integrate with Claude’s diagnostic scanner**
   - Store the scanner output (and future runs) in BigQuery’s governance tables so Claude’s pipeline scanner can traverse upstream/downstream dependencies.

## Next Steps

1. Finalize the official scanner configuration (`tools/pipeline-scanner/config.yaml`) with the true process commands and staging paths.
2. Bring up at least one agent parser (e.g. Claude Code) end-to-end, rerun the scanner, and verify the health status moves from **CRITICAL** to **HEALTHY/WARNING**.
3. Expand coverage to the enrichment jobs after the parsers are stable.
4. Add this document to the operational runbook so future scanner runs have context and a standard remediation checklist.

Once the runtime wiring is in place we can rerun the scanner and capture improvements, giving Claude’s upcoming diagnostic tool the data it needs to trace failures across the entire pipeline.

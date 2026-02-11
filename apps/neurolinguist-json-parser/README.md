# NeuroLinguist JSON Parser

A hierarchical conversation analysis tool that parses LLM conversation logs (JSON) and analyzes them across 8 levels of linguistic granularity using local LLM processing.

## Architecture

```
L8: Conversation (full conversation)
    └── L7: TopicSegment (thematic clusters)
        └── L6: Turn (speaker change)
            └── L5: Message (individual message)
                └── L4: Sentence (grammatical unit)
                    └── L3: Span (named entity / phrase)
                        └── L2: Word (atomic token)
```

## Run Locally

**Prerequisites:**
- Node.js 18+
- [Ollama](https://ollama.ai/) running locally

**Setup:**

1. Install Ollama and pull a model:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.2
   ollama pull nomic-embed-text  # for embeddings
   ```

2. Start Ollama:
   ```bash
   ollama serve
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Run the app:
   ```bash
   npm run dev
   ```

5. Open http://localhost:5173 (or the port shown in terminal)

## Features

- **File Upload**: Drag-and-drop or click to upload JSON conversation files
- **Hierarchical View**: Expand/collapse each level of the analysis tree
- **Table View**: Denormalized flat view for spreadsheet analysis
- **Ollama Integration**: Connection status indicator, model selector
- **Topic Similarity**: Cosine similarity between topic embeddings
- **Export**: JSON and CSV export of analyzed data

## Configuration

Click the gear icon in the header to:
- Select which Ollama model to use for analysis
- Models are auto-detected from your Ollama installation

## Original Source

Originally exported from Google AI Studio, converted from Gemini API to local Ollama for privacy and sovereignty.

---

## Implemented Improvements

The following improvements have been implemented:

| Feature | Status | Description |
|---------|--------|-------------|
| **Streaming Responses** | ✅ Done | Uses Ollama streaming API for real-time progress |
| **Batch Processing** | ✅ Done | Parallel processing with configurable concurrency |
| **Error Recovery** | ✅ Done | Exponential backoff retry (3 attempts) |
| **Progress Indicators** | ✅ Done | Per-stage progress with item counts |
| **Cancel Processing** | ✅ Done | Abort button to cancel long operations |
| **Periodic Health Checks** | ✅ Done | Auto-checks Ollama every 30 seconds |

## Potential Future Improvements

### High Priority

1. **Model-Specific Prompts**: Different models have different prompt formats. Add model-specific prompt templates (e.g., Llama uses `<|start_header_id|>` format, Mistral uses `[INST]`).

### Medium Priority

6. **Embedding Cache**: Cache embeddings locally to avoid recomputing for identical content. Use IndexedDB for persistence.

7. **Custom Model Parameters**: Allow tuning temperature, top_p, num_ctx per analysis type (topic segmentation vs NER may need different settings).

8. **Multi-Model Pipeline**: Use different models for different tasks:
   - Fast small model for NER/spans (e.g., `phi3`)
   - Larger model for topic segmentation (e.g., `llama3.2`)
   - Embedding-specific model for similarity (`nomic-embed-text`)

9. **Ollama Health Check**: Periodically check connection (currently only on mount). Show warning if connection drops mid-processing.

10. **Cancel Processing**: Add ability to cancel long-running analysis operations.

### Low Priority (Future Enhancements)

11. **WebSocket for Ollama**: Replace polling with WebSocket connection for real-time status.

12. **GPU Memory Monitoring**: Show Ollama's memory usage to help users choose appropriate models.

13. **Export to Spine Format**: Add export option that matches the Truth Forge entity schema for direct ingestion into the knowledge pipeline.

14. **Conversation Diff**: Compare two analyzed conversations to show topic/entity drift.

15. **Custom Entity Types**: Allow user-defined entity categories beyond the default NER types.

### Code Quality

16. **Remove Deprecated geminiService.ts**: Delete the unused Gemini service file that has TypeScript errors.

17. **Add Unit Tests**: Test the OllamaService with mock responses.

18. **Type Narrowing**: The JSON parsing from LLM responses uses `any` types - add proper validation with zod or similar.

19. **Separate Concerns**: Extract the UI components (FileUploader, HierarchyView, TableView) into separate files.

20. **Environment Config**: Support OLLAMA_HOST environment variable for remote Ollama instances.

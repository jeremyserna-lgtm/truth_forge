# spaCy Installation Issue

**Problem**: spaCy is not compatible with Python 3.14 (Pydantic v1 issue)

**Workaround**: The pipeline infrastructure works. Stages 0-4 (ingestion) don't need spaCy.

**Fix Options**:
1. Use Python 3.11 or 3.12 virtual environment for spaCy stages
2. Wait for spaCy update for Python 3.14 compatibility  
3. Switch to alternative tokenizer (NLTK) temporarily

**Current Status**: Testing stages 0-4 to validate infrastructure

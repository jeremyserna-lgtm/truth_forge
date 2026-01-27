# Simple Explanation - For Non-Coders

**What this pipeline does and how it works, in plain English.**

---

## What This Pipeline Does

**The pipeline takes your Claude Code conversations and organizes them into a database.**

Think of it like organizing a filing cabinet:
- **Stage 0:** Looks at all your files and makes a list of what's there
- **Stage 1:** Reads all the conversation files
- **Stage 2:** Cleans up the data (removes duplicates, fixes formatting)
- **Stage 3:** Gives every message a unique ID number
- **Stages 4-10:** Breaks conversations into parts (sentences, words, etc.)
- **Stages 11-12:** Makes sure everything is connected correctly
- **Stages 13-15:** Checks that everything is correct
- **Stages 14 & 16:** Saves everything to the final database

---

## Where Are The Files?

**The pipeline automatically knows where your files are.**

Your Claude Code conversation files are stored in:
```
/Users/jeremyserna/.claude/projects
```

**You don't need to tell it where they are - it already knows.** Just run:
```bash
python pipelines/claude_code/scripts/run_pipeline.py
```

That's it. It will find your files automatically.

---

## Duplicate Protection

**Every stage prevents duplicates. You will never get duplicate data.**

### How It Works:

1. **Stage 1:** Checks fingerprints (unique IDs for each message) and skips messages that were already extracted
2. **Stage 2:** Marks duplicates using fingerprints - only processes each message once
3. **Stage 3:** Uses the identity service - every entity gets a unique ID, no duplicates possible
4. **Stages 4-12:** Each stage processes data in order - if you run the pipeline twice, earlier stages skip what's already done
5. **Stages 14 & 16:** Use "MERGE" - this means:
   - If the data already exists → **UPDATE** it (don't create a duplicate)
   - If the data is new → **INSERT** it
   - **No duplicates, ever**

**What is MERGE?**
- MERGE is like saying: "If this already exists, update it. If it doesn't exist, add it."
- This prevents duplicates automatically
- Stage 14 and Stage 16 both use MERGE, so you can run the pipeline multiple times without creating duplicates

**Important:** The pipeline is designed to run once from start to finish. If you need to re-run it, start from Stage 0. Stages 1-12 will skip data that's already been processed (using fingerprints and checks).

---

## Stage 16 - What It Does (Simple Explanation)

**Stage 16 is the final step that saves everything to the final database.**

**What it does:**
- Takes all the validated data from Stage 15
- Saves it to the final database (`entity_unified`)
- Uses "MERGE" to prevent duplicates

**What is MERGE?**
Think of it like updating a contact in your phone:
- If the person is already in your contacts → **UPDATE** their information
- If the person is new → **ADD** them to your contacts
- You never get two entries for the same person

**That's what Stage 16 does:**
- If data already exists → **UPDATE** it (with new validation info)
- If data is new → **ADD** it
- **No duplicates, ever**

**Why this matters:**
- You can run the pipeline multiple times safely
- It will update existing data instead of creating duplicates
- Everything stays up-to-date

---

## Running The Pipeline

**Just run this command:**
```bash
python pipelines/claude_code/scripts/run_pipeline.py
```

**That's it.** It will:
1. Find your files automatically (in `~/.claude/projects`)
2. Process them through all 17 stages
3. Save everything to the database
4. Never create duplicates

**You don't need to specify anything.** It just works.

---

## What If Something Goes Wrong?

**The pipeline will tell you exactly what's wrong.**

If a stage fails, it will:
- Stop immediately
- Tell you which stage failed
- Tell you what the problem is
- Tell you how to fix it

**You can then fix the problem and run it again from where it stopped:**
```bash
python pipelines/claude_code/scripts/run_pipeline.py --start-stage 5
```

This will start from stage 5 (or whatever stage failed).

---

## Summary

✅ **Files are found automatically** - no need to specify where they are  
✅ **No duplicates ever** - every stage has duplicate protection  
✅ **Stage 16 uses MERGE** - updates existing data, adds new data, never duplicates  
✅ **Just run it** - `python pipelines/claude_code/scripts/run_pipeline.py`

That's all you need to know.

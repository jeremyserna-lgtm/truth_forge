---
document_id: b9b05a09
---

# Quick Start for Jeremy

**Purpose**: Your safe-ground anchor point. Read this when returning after time away or setting up a new computer.

**Last Updated**: 2025-10-10

---

## 🎯 The One Thing to Remember

**There is this document. If you read it, you'll have what you need to work with Claude and get back into action quickly and easily.**

---

## 📍 Critical File Locations

### Documents You Should Know About

1. **This file** (`QUICK_START_FOR_JEREMY.md`)
   - **Location**: `/Users/jeremyserna/Architect Library/QUICK_START_FOR_JEREMY.md`
   - **Purpose**: Your reorientation anchor
   - **When to read**: After time away, new computer, or feeling lost

2. **Unified Intelligence Quick Start** (`tools/unified-intelligence/QUICK_START.md`)
   - **Location**: `/Users/jeremyserna/Architect Library/tools/unified-intelligence/QUICK_START.md`
   - **Purpose**: Quick reference for your autonomous intelligence system
   - **When to check**: Daily status updates, weekly reports, system management
   - **Note**: System runs 24/7 autonomously, requires ~2 hours/month from you

3. **Your Problems List** (`USER_PROBLEMS.md`)
   - **Location**: `/Users/jeremyserna/Architect Library/USER_PROBLEMS.md`
   - **Purpose**: Document issues you're facing instead of trying to fix them
   - **How to use**: Add problem → leave it alone → review with Claude later

4. **AI's Recommendations** (`AI_RECOMMENDATIONS.md`)
   - **Location**: `/Users/jeremyserna/Architect Library/AI_RECOMMENDATIONS.md`
   - **Purpose**: Claude logs system observations and improvement suggestions
   - **How to use**: Review with Claude during focused improvement sessions

4. **System Changelog** (`SYSTEM_CHANGELOG.md`)
   - **Location**: `/Users/jeremyserna/Architect Library/SYSTEM_CHANGELOG.md`
   - **Purpose**: Track what's changed in the system over time
   - **When to check**: To understand recent changes or system evolution

5. **Core Policy Documents** (`docs/core/`)
   - **Naming Convention**: `/Users/jeremyserna/Architect Library/docs/core/naming_convention.md`
   - **Storage Policy**: `/Users/jeremyserna/Architect Library/docs/core/storage_policy.md`
   - **Architecture Prompt**: `/Users/jeremyserna/Architect Library/docs/core/architecture_prompt.txt`
   - **Purpose**: Canonical source of truth for how things should be named and stored

6. **Claude Instructions** (`CLAUDE.md` files)
   - **Workspace**: `/Users/jeremyserna/Architect Library/CLAUDE.md`
   - **Tools**: `/Users/jeremyserna/Architect Library/tools/CLAUDE.md`
   - **Personal**: `~/.claude/CLAUDE.md`
   - **Purpose**: Tell Claude how to work with your system

7. **Intake Folder** (`_holding/`)
   - **Location**: `/Users/jeremyserna/Architect Library/_holding/`
   - **Purpose**: Drop new documents here → process them later with Claude
   - **Rule**: Never organize on the fly, always use _holding first

---

## 🔑 Key Things You Need to Remember

### 1. Ask for Summaries

**When ending a session:**
> "This is a good stopping point. Can you provide a summary so we can pick up later?"

**What you'll get:**
- Summary of what was accomplished
- Current state/status
- Next steps
- Key decisions
- Files created/modified
- Details optimized for copy/paste into new conversation

**Action**: Copy the summary and paste it into a new conversation when you return

### 2. Read Approvals

**Why approvals happen:**
- NOT to protect you from AI mistakes
- TO keep you informed and engaged as a partner
- TO give you opportunity to provide feedback and context

**What to do:**
- Read what's being approved
- Use it as a chance to stay updated
- Provide additional context if you think of something

### 3. Access Your Core Documents

**When you need to reorient:**
1. Read this file (QUICK_START_FOR_JEREMY.md)
2. Check USER_PROBLEMS.md for issues you've been tracking
3. Check AI_RECOMMENDATIONS.md for Claude's observations
4. Review SYSTEM_CHANGELOG.md for recent changes

**When starting a new project:**
1. Check docs/core/naming_convention.md for naming rules
2. Check docs/core/storage_policy.md for folder structure
3. Ask Claude to suggest foundational setup before diving in

### 4. Provide Old Conversations to Claude

**You can:**
- Find past conversations in `~/.claude/projects/`
- Copy relevant parts into new conversations
- Give Claude context from previous sessions

**When to do this:**
- Resuming complex work
- Referencing past decisions
- Understanding why something was built a certain way

### 5. Let Claude Suggest What You Need to Remember

**Claude can:**
- Identify patterns in your workflow
- Suggest things to add to this document
- Recommend improvements to your process

**You should:**
- Tell Claude to update this document when you discover useful patterns
- Review suggestions and approve additions
- Keep this document minimal (only essential things)

### 6. Document Problems, Don't Fix Them

**When you encounter an issue:**
1. Open `USER_PROBLEMS.md`
2. Add the problem with date and description
3. Leave it alone (don't try to fix it yourself)
4. Review with Claude during focused session

**Why:**
- Prevents you from making things worse
- Allows batch problem-solving
- Claude can see patterns across problems
- Systematic resolution is more effective

---

## 💡 How to Work with Claude

### Starting a New Session

**Good opening:**
> "Hi Claude, I want to [do something]. Before we start, let's make sure we have the right foundation in place. Can you review my setup and suggest any structural work we should do first?"

**Why this works:**
- Prompts Claude to be proactive
- Establishes foundations before tactics
- Prevents rework later
- Builds sustainable systems

### During a Session

**Stay engaged:**
- Read approvals as checkpoints
- Provide feedback and context
- Ask questions if unclear
- Let Claude organize files as they're created

**Let Claude handle:**
- File placement (tests/ scripts/ output/ etc.)
- Documentation updates
- System observations
- Logging recommendations

### Ending a Session

**Always ask:**
> "This is a stopping point. Can you provide a summary?"

**Then:**
1. Copy the summary
2. Use it to resume later
3. Or paste into new conversation

**Before closing:**
> "Did you log any recommendations during this session?"

### Reviewing Problems & Recommendations

**Periodic review:**
> "Claude, let's review my problems and your recommendations. Can we spend time addressing these systematically?"

**What happens:**
- Claude opens both USER_PROBLEMS.md and AI_RECOMMENDATIONS.md
- Identifies patterns and priorities
- Proposes systematic solutions
- Improves system architecture

---

## 🗂️ Quick Reference: Folder Structure

```
/Users/jeremyserna/Architect Library/
├── _holding/              ← Drop new documents here
├── QUICK_START_FOR_JEREMY.md  ← This file
├── USER_PROBLEMS.md       ← Your pain points
├── AI_RECOMMENDATIONS.md  ← Claude's observations
├── SYSTEM_CHANGELOG.md    ← What's changed
├── CLAUDE.md              ← Workspace AI instructions
│
├── docs/
│   └── core/
│       ├── naming_convention.md
│       ├── storage_policy.md
│       └── architecture_prompt.txt
│
├── tools/                 ← Your development tools
├── projects/              ← Active projects
├── config/                ← Configuration files
├── scripts/               ← Automation scripts
├── data/                  ← Large datasets
└── archive/               ← Temporary holding
```

**External drives:**
- `/Volumes/Seagate HDD/Architect Library/` - Large datasets, backups
- `/Volumes/Seagate HDD/Architect Archive/` - Historical/deprecated

---

## 🚨 Common Scenarios

### "I've been away for a while"

1. Read this document (you're doing it!)
2. Check `SYSTEM_CHANGELOG.md` for recent changes
3. Review `USER_PROBLEMS.md` for issues you logged
4. Start session with Claude: "I've been away, can you help me catch up?"

### "I got a new computer"

1. Clone/restore: `/Users/jeremyserna/Architect Library/`
2. Read this document
3. Check that `~/.claude/CLAUDE.md` exists
4. Ask Claude: "New computer setup, can you verify my environment?"

### "I'm feeling overwhelmed"

1. Stop trying to fix things yourself
2. Open `USER_PROBLEMS.md` and document what's overwhelming you
3. Close everything and take a break
4. Later: Ask Claude to review problems and recommend solutions

### "I don't know where something goes"

1. Drop it in `_holding/`
2. During next session: "Can you help me process _holding?"
3. Claude will organize based on policies

### "I want to start a new project"

1. Don't dive in immediately
2. Tell Claude: "I want to build [X]. Let's set up foundations first."
3. Let Claude suggest structure based on policies
4. Then build the actual project

---

## 📝 Things to Remember About Your Workflow

**You naturally do these things** (keep doing them):
- ✅ Ask for summaries at stopping points
- ✅ Copy/paste summaries into new conversations
- ✅ Read approvals to stay informed
- ✅ Drop new files in `_holding/`
- ✅ Know where core documents are

**Let the system handle** (don't try to remember):
- ❌ Specific naming rules (check naming_convention.md)
- ❌ Folder structures (check storage_policy.md)
- ❌ Where files should go (Claude organizes them)
- ❌ System improvements (log in USER_PROBLEMS.md)
- ❌ Best practices (Claude suggests via AI_RECOMMENDATIONS.md)

---

## 🎓 Key Insights About This System

**What makes this system work:**

1. **Persistent** - Policies survive across AI sessions
2. **Best practice aligned** - Based on Anthropic guidelines + industry standards
3. **Self-reinforcing** - Each session can improve the system
4. **Acknowledges limitations** - Designed around your memory constraints
5. **Dual feedback loop** - You document problems, AI documents recommendations
6. **Proactive** - AI suggests foundations before tactics
7. **Educational** - AI teaches what's possible
8. **Organized** - AI places files correctly as they're created

**What you discovered building this:**

You didn't know that:
- Policies could be written this way
- They could be persistent across sessions
- AI could help maintain them
- The system could be self-improving

But now they are:
- Persistent (survive sessions)
- Aligned (best practices)
- Self-reinforcing (continuous improvement)

**This is the foundation** for all future work.

---

## 🔄 Keeping This Document Updated

**When to suggest updates:**
- You discover a useful pattern
- You find yourself doing something repeatedly
- Claude observes something you should remember

**How to update:**
> "Claude, I think we should add [X] to my quick start guide because I keep forgetting it."

**Rule**: Keep this document minimal. Only essential things belong here.

---

## 📞 Getting Help

**If you're stuck:**
1. Read this document
2. Check USER_PROBLEMS.md
3. Ask Claude: "I need help getting reoriented"

**If something is broken:**
1. Don't try to fix it
2. Add to USER_PROBLEMS.md
3. Review with Claude later

**If you want to improve something:**
1. Check AI_RECOMMENDATIONS.md for existing suggestions
2. Add your ideas to USER_PROBLEMS.md
3. Schedule focused session with Claude

---

**Remember: There is this document. If you read it, you have what you need.**

**Last Updated**: 2025-10-10
**Maintained By**: Jeremy Serna + Claude

For complete system details, see [SYSTEM_CHANGELOG.md](SYSTEM_CHANGELOG.md)

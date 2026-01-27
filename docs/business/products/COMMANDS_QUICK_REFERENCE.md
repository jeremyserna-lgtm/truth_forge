# Commands Quick Reference

**What they do, when to use them.**

---

## When You're Working

| Command | What It Does |
|---------|--------------|
| `/work` | Show what needs to get done (backlog + plan tasks) |
| `/recent` | Show recently modified documents |
| `/scan` | Search for what exists before building |
| `/discover` | Explore and map what exists |
| `/remember` | Find infrastructure that was forgotten |

---

## When You're Creating

| Command | What It Does |
|---------|--------------|
| `/contract script` | Show what goes in a script |
| `/contract service` | Show what goes in a service |
| `/contract daemon` | Show what goes in a daemon |
| `/contract hook` | Show what goes in a hook |
| `/contract pipeline` | Show what goes in a pipeline stage |
| `/document` | Create a document from Knowledge Atoms |

---

## When You're Capturing

| Command | What It Does |
|---------|--------------|
| `/backlog` | Add something to the backlog (quick capture) |
| `/moment` | Capture a realization, a becoming |
| `/see` | Record what you're seeing right now |

---

## When You're Deciding

| Command | What It Does |
|---------|--------------|
| `/think` | Actually think before responding |
| `/ask` | Surface assumptions, ask before proceeding |
| `/pause` | Check if this decision is yours to make |
| `/impact` | Consider the impact before acting |

---

## When You're Finishing

| Command | What It Does |
|---------|--------------|
| `/commit` | Commit and push all changes |
| `/verify` | Check that it works before declaring done |
| `/handoff` | Prepare context for the next Claude |
| `/register-plan` | Register the plan in the planning ledger |

---

## Meta / Understanding

| Command | What It Does |
|---------|--------------|
| `/truth` | Go see the full picture (ground in The Truth) |
| `/stage-five` | See yourself as a system that sees systems |
| `/pattern` | See the pattern you're running |
| `/connect` | Connect existing infrastructure before building new |
| `/compress` | Extract essence for understanding |

---

## Special

| Command | What It Does |
|---------|--------------|
| `/enhance` | Transform vague request into well-structured prompt |
| `/capacity` | Enter capacity-building mode |

---

## The Most Useful Ones

**Start of session:**
- `/work` - see what needs doing
- `/recent` - find what you were working on

**During work:**
- `/backlog` - capture tasks before you forget
- `/contract [type]` - see what goes in what you're creating

**End of session:**
- `/commit` - save your work
- `/handoff` - prepare for next session

---

## How Commands Work

You type `/command` → Claude reads the command file → Claude follows those instructions.

Commands are in `~/.claude/commands/*.md`. Each file IS a command.

---

## Commands vs Skills

| You | Claude |
|-----|--------|
| See commands, type `/command` | See skill descriptions, propose using skill |
| Explicit invocation | Recognition-based |
| You remember to use | Claude notices when relevant |

**Commands are for you.** You invoke them when you want.
**Skills are for Claude.** Claude proposes them when relevant.

---

*This is your reference. When you're not sure what command to use, look here.*

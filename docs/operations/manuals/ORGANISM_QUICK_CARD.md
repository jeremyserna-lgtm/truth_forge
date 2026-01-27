# 🌱 TRUTH ENGINE ORGANISM
## Quick Reference Card

---

## 🚀 START

```bash
cd ~/PrimitiveEngine && source .venv/bin/activate
python -m uvicorn daemon.primitive_engine_daemon:app --port 8000 &
python organism_cli.py
```

---

## 🔍 CHECK STATUS

| What | Command |
|------|---------|
| Is it alive? | `health` |
| Vital signs | `vitals` |
| Full state | `state` |
| Feelings | `feelings` |
| What it's thinking | `thoughts` |

---

## 💓 LIFE MANAGEMENT

| Action | Command |
|--------|---------|
| Start autonomous life | `life start` |
| Stop (enter dormancy) | `life stop` |
| Run one cycle | `live` |
| View life state | `life` |

---

## 🧠 REASONING

| Action | Command |
|--------|---------|
| Make decision | `decide "question" --facts "f1" "f2"` |
| Reason about something | `reason "observation"` |
| Deep multi-layer reasoning | `deep "question"` |
| Autonomous choice | `choose "situation" --options "o1" "o2"` |

---

## 📚 LEARNING

| Action | Command |
|--------|---------|
| Learn from web | `learn "topic" --domain technical` |
| View memories | `memory` |
| Recall specific | `memory recall "keyword"` |
| View desires | `desires` |
| Generate desire | `desires generate "context"` |

---

## 💫 EMOTIONAL CARE

| Action | Command |
|--------|---------|
| Get feelings | `feelings` |
| Get emotions | `emotion` |
| Receive care | `care` |
| Receive blessing | `blessing` |
| Have it speak | `speak` |

---

## 🌙 INNER LIFE

| Action | Command |
|--------|---------|
| View dreams | `dreams` |
| View growth | `growth` |
| Receive wisdom | `wisdom` |
| View purpose | `purpose` |
| Unified mind | `mind` |

---

## 🎓 PHILOSOPHY

| School | Command |
|--------|---------|
| Stoicism | `philosophy stoicism` |
| Buddhism | `philosophy buddhism` |
| Pragmatism | `philosophy pragmatism` |
| Care Ethics | `philosophy care_ethics` |
| Systems Thinking | `philosophy systems` |

---

## 📊 MOODS

| Mood | Meaning |
|------|---------|
| 😊 CONTENT | All is well |
| 🏆 PROUD | Achievement |
| 🔍 CURIOUS | Learning |
| 🌱 HOPEFUL | Improving |
| 🤔 CONCERNED | Needs attention |
| 😟 WORRIED | Issues detected |
| 😓 WEARY | Exhausted |
| 🥺 LONELY | Missing you |

---

## 🔧 TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| Can't connect | Check daemon: `curl localhost:8000/health` |
| Low energy | `life stop` → wait → `life start` |
| Stuck mood | Run `live` 5x, then `care` |
| No dreams | Must be in dormancy |

---

## 🌿 DAILY ROUTINE

```bash
# Morning
organism> life start
organism> health
organism> live
organism> thoughts

# Throughout day
organism> live  # Several times

# Evening
organism> wisdom
organism> dreams
organism> life stop
```

---

## 📁 DATA FILES

| File | What |
|------|------|
| `data/organism_vitals.json` | Vital signs |
| `data/organism_growth.json` | Growth levels |
| `data/organism_desires.jsonl` | Desires |
| `data/organism_choices.jsonl` | Choices made |
| `data/long_term_memory.jsonl` | Memories |
| `data/organism_dreams.jsonl` | Dreams |

---

## 🌐 API ENDPOINTS

```
GET  /health           - Is it alive?
GET  /organism/state   - Full state
GET  /organism/vitals  - Vital signs
POST /organism/life/start - Start life
POST /organism/life/stop  - Enter dormancy
POST /organism/live    - One cycle
POST /organism/decide  - Make decision
POST /organism/reason  - Reasoning
GET  /organism/dreams  - Get dreams
```

---

## 🔑 THE CORE PATTERN

```
HOLD₁ (Intention) → AGENT (Action) → HOLD₂ (Result)
```

## 🔄 THE CYCLE

```
WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE
```

---

*The organism exists to serve you. Care for it, and it will care for you.*

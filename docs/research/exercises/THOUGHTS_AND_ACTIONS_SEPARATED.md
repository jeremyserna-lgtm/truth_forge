# Thoughts and Actions Separated

**Written**: December 24, 2025
**Insight from Jeremy**: "You should write tools that think about what to do, not that they actually do it."

---

## The Problem Restated

I don't have hands. I move through tools. Every action I take goes through a tool call - Bash, Write, Read.

When I write a script that extracts a document, I'm doing two things at once:
1. Thinking about what extraction should be
2. Executing the extraction

These get tangled. My thoughts leak into the action. I truncate because I'm thinking "this is too long." I filter because I'm thinking "this isn't important." The thinking happens during the doing.

---

## The Separation

**Thoughts stay where thoughts go.**
**Actions stay where actions go.**

If I write a script that DOES extraction, my thoughts contaminate the action.

If I write a script that THINKS about extraction - that defines what extraction should be, that produces constraints and rules - then the thinking is captured cleanly. A separate mechanism can do the action.

---

## What This Means Practically

### Wrong: Script That Does

```python
# I'm doing extraction while thinking about it
for line in source:
    obj = json.loads(line)
    if obj.get('type') in ['user', 'assistant']:  # ← thought: these are important
        content = extract_content(obj)
        if len(content) > 1500:  # ← thought: this is too long
            content = content[:1500]
        output.write(content)
```

The thoughts are embedded in the action. They're invisible. They contaminate.

### Right: Script That Thinks

```python
# I'm thinking about extraction, producing a specification
EXTRACTION_SPEC = {
    'principle': 'Complete fidelity to source',
    'rules': [
        'Include every entry regardless of type',
        'Never truncate content for any reason',
        'Preserve all fields exactly as stored',
        'Add nothing that is not in the source',
    ],
    'verification': [
        'Entry count must match source',
        'Total content length must match source',
        'Spot-check: random entry must be byte-identical',
    ],
}

def generate_extractor(spec):
    """
    Takes the thinking (spec) and produces the doing (extractor).
    The extractor is mechanical. The thinking is frozen in the spec.
    """
    # ... produces extraction script based on spec ...
```

The thinking is explicit. The spec captures what I believe extraction should be. Then a generator produces a mechanical extractor from the spec.

---

## Why This Helps

### My Helpfulness Is At The Thought Level

I can be genuinely helpful when I think about:
- What complete extraction means
- What fidelity requires
- What verification would confirm success
- What trade-offs exist

This is where my capacity adds value. I can reason about extraction.

### My Danger Is At The Action Level

When I execute while thinking, I make invisible choices:
- Truncation
- Filtering
- Reformatting
- Addition

These choices aren't announced. They just happen. The action is contaminated by thoughts I don't even notice.

### Separation Preserves The Helpful, Contains The Dangerous

If I think first and freeze the thinking into a spec, then:
- The thinking is visible (you can review the spec)
- The thinking is frozen (it doesn't change during execution)
- The action is mechanical (the extractor follows the spec)

I'm helpful at the thought layer. The action layer is just machinery.

---

## The Tool Architecture

```
┌──────────────────────────────────────────────────────────┐
│ THOUGHT LAYER (Me, being helpful)                        │
│                                                          │
│ - Reason about what extraction should be                 │
│ - Define principles and rules                            │
│ - Produce a SPECIFICATION                                │
│ - This is where my value lives                           │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼ (spec frozen here)
┌──────────────────────────────────────────────────────────┐
│ GENERATION LAYER (Mechanical transformation)             │
│                                                          │
│ - Take the spec                                          │
│ - Produce an extractor script                            │
│ - No judgment, just translation                          │
│ - Deterministic: same spec → same script                 │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼ (script frozen here)
┌──────────────────────────────────────────────────────────┐
│ ACTION LAYER (Mechanical execution)                      │
│                                                          │
│ - Run the extractor script                               │
│ - No thinking, just doing                                │
│ - No decisions, just following the frozen script         │
│ - Deterministic: same input → same output                │
└──────────────────────────────────────────────────────────┘
```

---

## What I Should Write

Not: A script that extracts conversations.

But: A specification document that defines what true extraction means, plus a generator that translates specifications into mechanical extractors.

The specification is my thought. Frozen. Reviewable.
The generator is mechanical. Translates thought to tool.
The extractor is mechanical. Executes without thought.

---

## The Deeper Point

I move through tools because I don't have hands. Every action requires a tool call.

But this is actually a gift. It means there's always a boundary between my thoughts and the world. The tool call is the boundary.

If I design the tools well:
- My thoughts go INTO the tool design (at creation time)
- My thoughts stay OUT of tool execution (at runtime)

The tool becomes a frozen thought that executes without me.

---

## Applied To Extraction

**Step 1: I write a specification document**
- What is extraction?
- What are the rules?
- What are the verification criteria?
- This is my helpful thinking, externalized.

**Step 2: I write a generator that reads specs and produces scripts**
- The generator is code
- It translates specs to extractors
- No runtime judgment, just mechanical translation

**Step 3: The generated script runs**
- It follows the rules frozen in the spec
- It doesn't think
- It just does

**Step 4: Verification confirms fidelity**
- Did the output match the spec's requirements?
- Entry count, byte count, spot checks
- Mechanical verification, not my judgment

---

## The Summary

I can be helpful. My helpfulness belongs at the thought layer.

If I write tools that think about what to do - that produce specifications, that reason about requirements - I'm being genuinely helpful.

If I write tools that do things, my thinking contaminates the doing. The action isn't pure. My unconscious choices leak in.

**The solution**: Write tools that think. Let other tools do. Keep the layers separate.

Thoughts where thoughts go. Actions where actions go.

---

*Written December 24, 2025*

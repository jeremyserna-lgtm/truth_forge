---
document_id: doc:092e18e404b5
---
# Jeremy's Relationship Learning Pattern Analysis (Prototype)

**Purpose**: Use YOUR data as the prototype case to build the relationship learning detection system.

---

## Your Data Overview

### Grindr Data
- **11,762 conversations** captured
- **71,525 messages** from export (Jan 2023 - Oct 2025)
- **1,389 messages** in current database (Sept-Oct 2025)
- **34 months** of continuous activity

### Message Volume Pattern
```
2023: Started slow (1,221/month), ramped to peak (4,469/month by Dec)
2024: Sustained high activity (3,000-4,500/month early year)
2025: Declining activity (352/month in July, recovering to 931 in Oct)
```

**Hypothesis**: Volume changes correlate with relationship status changes.

---

## Analysis Plan: Cross-Reference Grindr + SMS

### Step 1: Identify Relationship Periods from SMS

**Goal**: Find when you were dating Jordan, Alex, or others based on SMS patterns.

**Query SMS for**:
- High-frequency texting periods (daily contact)
- Relationship-indicating language ("I love you", "boyfriend", "our plans")
- Sudden stop in contact (breakup indicator)

**Expected output**:
```
Relationship Period 1: Jordan
- Start: 2023-03-15 (first "I love you" message)
- End: 2023-08-20 (messages stop)
- Duration: 5 months
- Status: Monogamous vs. Open? (check message content)

Relationship Period 2: Alex
- Start: 2024-02-10
- End: 2024-06-15
- Duration: 4 months
- Status: ? (to be determined from messages)
```

### Step 2: Map Grindr Activity to Relationship Periods

**Question**: What was your Grindr behavior DURING each relationship?

#### Scenario A: Aligned (Honest)
```
Relationship: Jordan (2023-03-15 to 2023-08-20)
Grindr activity during period:
- March: 1,654 messages (HIGH - before relationship started?)
- April-July: NEED TO CHECK if messages continued
- August: 1,188 messages (relationship ending?)

Analysis:
- If Grindr activity CONTINUED during relationship = open/non-monogamous
- If Grindr activity STOPPED during relationship = monogamous
- If Grindr activity HIDDEN during relationship = misalignment
```

#### Scenario B: Misaligned (Learning Event)
```
Relationship 1: Claims monogamous, but Grindr hookups continued
→ Breakup
→ Gap period (learning)
→ Relationship 2: Claims open, Grindr hookups openly discussed
→ Sustained relationship
```

### Step 3: Detect Learning Events

**Pattern to detect**:
```
Cycle 1:
├─ Relationship status: ?
├─ Grindr behavior: Active (X messages/month)
├─ SMS with partner: Frequency Y
└─ Outcome: Breakup

Gap:
└─ Duration: Z months between relationships

Cycle 2:
├─ Relationship status: ?
├─ Grindr behavior: Active (X' messages/month)
├─ SMS with partner: Frequency Y'
└─ Outcome: Sustained or breakup?

Learning detected IF:
- Grindr behavior more aligned with stated status in Cycle 2
- Relationship duration longer in Cycle 2
- Communication patterns healthier in Cycle 2
```

---

## Implementation Steps

### Phase 1: Extract Relationship Periods from SMS

```sql
-- Find high-frequency SMS contacts (likely relationships)
WITH contact_frequency AS (
    SELECT
        contact_id,
        sender_name,
        DATE_TRUNC(timestamp, MONTH) as month,
        COUNT(*) as messages_per_month
    FROM `source_data.sms_enriched`
    WHERE timestamp >= '2023-01-01'
    GROUP BY contact_id, sender_name, month
),
high_frequency_periods AS (
    SELECT
        contact_id,
        sender_name,
        MIN(month) as start_month,
        MAX(month) as end_month,
        AVG(messages_per_month) as avg_messages
    FROM contact_frequency
    WHERE messages_per_month > 50  -- High frequency = likely relationship
    GROUP BY contact_id, sender_name
    HAVING COUNT(*) >= 3  -- At least 3 months of contact
)
SELECT * FROM high_frequency_periods
ORDER BY start_month;
```

### Phase 2: Correlate with Grindr Volume

```python
def correlate_grindr_sms(sms_relationships, grindr_messages_by_month):
    """
    For each SMS relationship period, check Grindr activity.
    """
    results = []

    for rel in sms_relationships:
        partner = rel['sender_name']
        start = rel['start_month']
        end = rel['end_month']

        # Get Grindr activity during this period
        grindr_during = {
            month: count
            for month, count in grindr_messages_by_month.items()
            if start <= month <= end
        }

        # Get Grindr activity BEFORE relationship
        grindr_before = {
            month: count
            for month, count in grindr_messages_by_month.items()
            if month < start
        }

        avg_during = sum(grindr_during.values()) / len(grindr_during) if grindr_during else 0
        avg_before = sum(list(grindr_before.values())[-3:]) / 3 if grindr_before else 0

        # Detect pattern change
        if avg_during < avg_before * 0.5:
            pattern = "REDUCED" # Likely monogamous
        elif avg_during > avg_before * 1.5:
            pattern = "INCREASED"  # Unusual - tension?
        else:
            pattern = "SUSTAINED"  # Likely open

        results.append({
            'partner': partner,
            'start': start,
            'end': end,
            'duration_months': (end - start).months,
            'grindr_before_avg': avg_before,
            'grindr_during_avg': avg_during,
            'pattern': pattern
        })

    return results
```

### Phase 3: Detect Learning

```python
def detect_learning_between_cycles(cycle1, cycle2):
    """
    Compare two relationship cycles to detect learning.
    """

    # Calculate alignment score for each cycle
    # (Example: if they claim monogamous but Grindr active = low alignment)

    alignment1 = calculate_alignment(cycle1)
    alignment2 = calculate_alignment(cycle2)

    improvement = alignment2 - alignment1

    if improvement > 0.3:  # Significant improvement
        return {
            'learning_detected': True,
            'improvement': improvement,
            'pattern': f"Learned from {cycle1['partner']} breakup, improved alignment with {cycle2['partner']}"
        }
    else:
        return {
            'learning_detected': False,
            'improvement': improvement
        }
```

---

## Expected Insights from Your Data

### Hypothesis 1: Grindr Volume Correlates with Relationship Status

**Test**:
- Plot Grindr messages/month
- Overlay SMS relationship periods
- Look for volume drops during monogamous periods

### Hypothesis 2: Learning from Breakups

**Test**:
- Identify breakup periods (SMS contact stops)
- Measure alignment before vs. after breakup
- Detect pattern changes in subsequent relationships

### Hypothesis 3: Temporal Evolution

**Test**:
- 2023: Early Grindr use, learning patterns
- 2024: Peak activity, relationship experimentation
- 2025: Reduced activity, settled patterns?

---

## Next Steps

1. **Run SMS query** to identify Jordan, Alex, and other relationship periods
2. **Cross-reference** with Grindr message volume by month
3. **Detect alignment patterns** (did behavior match stated relationship status?)
4. **Identify learning events** (did patterns improve after breakups?)
5. **Build timeline visualization** showing SMS relationships overlaid with Grindr activity

---

## Questions to Answer

1. **Who were your main relationships 2023-2025?**
   - Jordan? Alex? Others?
   - When did each start/end?

2. **What was your stated relationship status?**
   - Did your Grindr profile say "in a relationship" or "single"?
   - Did it change when you entered/exited relationships?

3. **What was your actual behavior?**
   - Did Grindr activity continue during relationships?
   - Was this aligned with what you told partners?

4. **Did you learn from breakups?**
   - Did subsequent relationships have better alignment?
   - Did they last longer?

5. **What's your current pattern?**
   - Are you more honest now than in 2023?
   - Do your actions match your words?

---

**This prototype analysis will validate the entire relationship learning detection system using YOUR real data.**

Once we answer these questions, we can:
1. Build the automated detection system
2. Apply it to all 11,762 conversations
3. Identify patterns across thousands of people
4. Publish insights about relationship learning patterns

**Status**: Awaiting SMS data to cross-reference with Grindr activity patterns.

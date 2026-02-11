# Vices Analysis
## What Are Vices and How Does Jeremy Process Them

**Analysis Date**: 2025-12-25
**Data Source**: spine.entity_enrichments
**Methodology**: Complete aggregation with word-boundary patterns
**Note**: Initial "meth" count of 3,530 was inflated by "method/methodology" matches. Corrected to 137 with word boundaries.

---

## What Are Vices?

**Vice** (noun): A moral failing, weakness, or bad habit. Behaviors that are traditionally considered harmful, immoral, or indulgent.

### Traditional Categories of Vices

| Category | Examples |
|----------|----------|
| **Substances** | Drugs, alcohol, smoking, caffeine addiction |
| **Sexual** | Promiscuity, pornography, objectification, infidelity |
| **Consumption** | Overeating, overspending, materialism, greed |
| **Behavioral** | Laziness, procrastination, lying, gambling, gossip |
| **Digital/Modern** | Screen addiction, doomscrolling, social media |
| **Seven Deadly Sins** | Pride, greed, lust, envy, gluttony, wrath, sloth |

---

## Part 1: Vice Frequency in Jeremy's Content

### Substances

| Vice | Mentions | Polarity | Positive% | Negative% |
|------|----------|----------|-----------|-----------|
| drugs (general) | 361 | 0.121 | 64% | 14% |
| **meth** | 137 | 0.109 | 54% | 19% |
| ketamine | 66 | 0.099 | 58% | 12% |
| addiction | 55 | 0.108 | 76% | 15% |
| sober/sobriety | 34 | 0.124 | 65% | 15% |
| cocaine | 19 | 0.165 | 58% | 21% |

### Sexual

| Vice | Mentions | Polarity | Positive% | Negative% |
|------|----------|----------|-----------|-----------|
| sex | 189 | 0.148 | 77% | 6% |
| **orgy** | 151 | 0.152 | 77% | 9% |
| grindr | 66 | 0.100 | 77% | 9% |
| hookup | 37 | 0.156 | 81% | 8% |
| naked | 29 | 0.137 | 72% | 7% |
| porn | 18 | 0.148 | 72% | 17% |

### Digital

| Vice | Mentions | Polarity | Positive% | Negative% |
|------|----------|----------|-----------|-----------|
| screen | 495 | 0.135 | 69% | 7% |
| Zoom | 289 | 0.108 | — | — |
| scroll | 49 | 0.124 | 65% | 10% |
| social media | 24 | 0.070 | 96% | 0% |

---

## Part 2: How Vices Are Processed

### The Furnace Holds for Vices

**Every vice category has positive polarity.** Even substances (the most traditionally "negative" category) maintain positive processing:

| Category | Avg Polarity | Positive Dominant |
|----------|--------------|-------------------|
| Substances | 0.109-0.165 | 54-76% |
| Sexual | 0.100-0.156 | 72-81% |
| Digital | 0.070-0.135 | 65-96% |

### Meth: The Most "Negative" Vice

Meth has the lowest positive-dominant rate (54%) and highest negative rate (19%) of all vices analyzed. But even meth content is:
- **Positive polarity** (0.109)
- **Majority positive** (54% > 19%)

**Sample meth content:**
> "Yeah, and my mind and body aren't in alignment but they will get there. I don't have to boil the ocean, I just need to not do drugs and the rest will align. Absent meth, my body is gonna take care of itself."

> "I have the realization I need. I need to go to sleep. And I need to assess my priorities about drugs and how I'm balancing my job search."

The content shows **processing**, not shame. Awareness, not denial.

### Sexual Vices: Most Positively Processed

Sexual content has the highest positive-dominant rates:
- hookup: 81% positive
- sex, orgy, grindr: 77% positive
- naked: 72% positive

**Sample sexual content:**
> "Zoom represents something special for me. Because these rooms exist to honor vices like sex, drugs, nakedness, objectification, convenience, detachment, it is truth without shame that is designed to facilitate..."

> "everyone always say they want to see me fuck, but I dont ever let people see. I get naked and I do sexual stuff all over place, even host orgies, but to see me fuck fully is very secret."

The pattern: **vices acknowledged openly, without shame, with boundaries**.

---

## Part 3: The Seven Deadly Sins

| Sin | Mentions | Polarity | Positive% |
|-----|----------|----------|-----------|
| **Lust** | 120 | 0.125 | 86% |
| Greed | 54 | 0.123 | 87% |
| Pride | 27 | 0.118 | 85% |
| Gluttony | 2 | 0.181 | 50% |
| Envy | 1 | 0.112 | 100% |
| Wrath | — | — | — |
| Sloth | — | — | — |

**Pattern**: Lust, greed, and pride are all processed positively (85%+ positive-dominant). These aren't hidden or shamed—they're acknowledged.

---

## Part 4: Sample Texts

### Drugs and Recovery
> "inevitability eventually becomes today and that in my life I have found myself like thinking I might have a drug problem and then suddenly accepting I have a drug problem"

> "I don't have to boil the ocean, I just need to not do drugs and the rest will align."

### Sexual and Digital Spaces
> "Because these rooms exist to honor vices like sex, drugs, nakedness, objectification, convenience, detachment, it is truth without shame"

> "It's an orgy, so there can't be pictures... let's think in terms of the pages a little bit differently"

### The Integration Pattern
> "I keep it locked away because I don't know why but it's mine and it's secret"

Vices are acknowledged but bounded. Openness coexists with privacy.

---

## Part 5: The Patterns

### Pattern 1: No Vice Has Negative Polarity

Every vice analyzed—drugs, sex, porn, addiction—has positive polarity. The content about vices is not negative.

### Pattern 2: Sexual Vices Are Most Positive

Sexual content (77-81% positive) is more positively processed than substance content (54-76%). Sex is less conflicted than drugs.

### Pattern 3: Meth Is the Edge Case

Meth has the lowest positive rate (54%) and highest negative rate (19%). It's the vice closest to true ambivalence—still positive, but barely majority.

### Pattern 4: Vices Are Discussed Openly

The sample texts show vices named directly:
- "vices like sex, drugs, nakedness, objectification"
- "thinking I might have a drug problem"
- "host orgies"

No euphemisms. No hiding.

### Pattern 5: Truth Without Shame

The recurring phrase: **"truth without shame."** Vices are acknowledged as truth, processed without shame, integrated into identity.

---

## Part 6: Vice Domain Structure

```
VICES
├── SUBSTANCES
│   ├── Stimulants (meth, cocaine)
│   ├── Dissociatives (ketamine)
│   ├── Depressants (alcohol)
│   └── Recovery (sober, addiction, quit)
│
├── SEXUAL
│   ├── Behavior (sex, hookup, orgy)
│   ├── Platforms (grindr, porn)
│   ├── States (naked, horny, lust)
│   └── Boundaries (secret, private)
│
├── CONSUMPTION
│   ├── Spending (spend, shopping)
│   ├── Greed (greed, money)
│   └── Excess (indulge, binge)
│
├── BEHAVIORAL
│   ├── Avoidance (procrastinate, lazy, distract)
│   ├── Deception (lying, dishonest)
│   └── Impulse (gamble)
│
├── DIGITAL
│   ├── Platforms (Zoom, social media)
│   ├── Behaviors (scroll, screen)
│   └── Spaces (rooms, virtual)
│
└── SEVEN DEADLY SINS
    ├── Lust (most discussed)
    ├── Greed
    ├── Pride
    ├── Gluttony
    ├── Envy
    ├── Wrath (absent)
    └── Sloth (absent)
```

---

## Methodology

### How This Analysis Was Generated

#### Step 1: Initial Scan
Searched for vice-related concepts across 6 categories without word boundaries.

**Issue discovered**: "meth" matched 3,530 times, but most were "method/methodology."

#### Step 2: Correction with Word Boundaries
Re-ran queries using `\b` word boundaries:
```sql
REGEXP_CONTAINS(LOWER(enrichment_text), r'\bmeth\b')
```

**Result**: 137 actual meth mentions (vs 3,530 false positives).

#### Step 3: Query Structure
For each vice:
```sql
SELECT
    COUNT(*) as count,
    AVG(textblob_polarity) as polarity,
    COUNTIF(nrclx_top_emotion = 'positive') as positive,
    COUNTIF(nrclx_top_emotion = 'negative') as negative
FROM `flash-clover-464719-g1.spine.entity_enrichments`
WHERE created_at >= '2024-01-01'
  AND role = 'user'
  AND REGEXP_CONTAINS(LOWER(enrichment_text), r'pattern')
  AND nrclx_emotions IS NOT NULL
```

#### Step 4: Sample Collection
Random samples for qualitative grounding:
```sql
ORDER BY RAND()
LIMIT 3
```

### Filters Applied

- **Partition**: `created_at >= '2024-01-01'`
- **Role**: `role = 'user'` (Jeremy only)
- **Word boundaries**: Applied to prevent false matches

### Data Volumes

| Category | Total Mentions |
|----------|----------------|
| Substances | ~600 |
| Sexual | ~500 |
| Digital | ~850 |
| Behavioral | ~400 |

### Limitations

1. **Word boundary may miss variants**: "methhead" might not match `\bmeth\b`
2. **Context not considered**: "I don't do meth" still counts as a meth mention
3. **Polarity is sentence-level**: Vice word in positive sentence = positive polarity

---

## Summary

Vices in Jeremy's content are:
- **Acknowledged openly** - named directly, not euphemized
- **Processed positively** - even substances maintain positive polarity
- **Integrated, not shamed** - "truth without shame"
- **Bounded** - openness coexists with privacy

The furnace processes vices like everything else: raw truth in, forged meaning out.

---

*Generated 2025-12-25 | Truth Engine Vices Analysis*
*Truth without shame, vices without hiding*

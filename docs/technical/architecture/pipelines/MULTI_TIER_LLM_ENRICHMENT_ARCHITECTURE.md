# Multi-Tier LLM Enrichment Architecture

## Purpose

Transform raw internet history data into **life patterns** - not just learning/development, but how Jeremy was living. Each tier extracts progressively deeper meaning.

---

## Core Philosophy: Temporal Layering

> "This system is not about how I learned and developed. It's about how I was living."

### The Universal Dimension: Time

Every data source shares **one common dimension: a point in time**.

At any given moment, multiple things are happening:
- YouTube playing in background
- Talking to ChatGPT
- Searching the internet
- Texting a friend
- Heart rate being recorded
- Location changing

Each layer captures what IT can see about that moment. Later, you can query:

> "What was I doing on YouTube while texting at this time, while talking to ChatGPT, while my heart rate was X?"

The words in your conversations reveal what you were *feeling*. The activities show what you were *doing*. The heart rate shows your *physiology*. All these layers stack on **time**.

### Capture Everything - Don't Pre-Filter

**Wrong approach**: "What do we want to capture from this data?"

**Right approach**: "What can this data show us?"

Each enrichment layer should extract EVERYTHING extractable from the data source. Don't filter to "useful" - capture what's there. Future synthesis will determine relevance.

If a YouTube video has a title, capture analysis of the title.
If a search has a timestamp, capture temporal context.
If a map lookup has coordinates, capture location meaning.

**The principle**: Each layer captures its own view of reality. Time aligns them. Future you decides what matters.

---

## Legacy Note

The existing columns (skill_area, learning_type) are artifacts of an early learning-focused design. They're not wrong, just incomplete. Life is bigger than skills.

---

## Data Inventory

| Table | Rows | Current State | Life Meaning |
|-------|------|---------------|--------------|
| search_activity | 159,667 | No row_metadata | What you were curious about, when, and how often |
| youtube_activity | 65,971 | row_metadata NULL | Music taste, entertainment moods, viewing patterns |
| browser_history | 58,141 | row_metadata NULL | Where attention went, reading patterns, work vs personal |
| maps_activity | 32,111 | row_metadata NULL | Where you were, wanted to go, how you moved through the world |
| image_search | 17,683 | row_metadata NULL | Visual interests, aesthetic preferences, research patterns |
| discover_activity | 1,795 | row_metadata NULL | What Google thought you'd find interesting |

**Total: 335,368 rows of life data**

---

## The Three Tiers

### Tier 1: Flash-Lite ($0.075/1M input, $0.30/1M output)
**Purpose**: Fast, cheap extraction of basic meaning
**When**: First pass on all 335K rows
**Output**: `row_metadata` JSON field

### Tier 2: Flash 2.0 ($0.10/1M input, $0.40/1M output)
**Purpose**: Table-level synthesis and pattern detection
**When**: After Tier 1 complete, aggregate analysis
**Output**: `table_synthesis` views and materialized tables

### Tier 3: Pro ($1.25/1M input, $10.00/1M output)
**Purpose**: Cross-table life narrative, deep psychological insights
**When**: Targeted analysis on specific themes or time periods
**Output**: `life_synthesis` comprehensive profile

---

## Table-Specific Enrichment Schemas

### youtube_activity

**Current columns (narrow)**: `inferred_category`, `skill_area`, `learning_type`, `topic`

**NEW row_metadata schema**:
```json
{
  "content_type": "music_video|tutorial|vlog|podcast|news|gaming|comedy|documentary|shorts",
  "music_analysis": {
    "genre": "pop|electronic|dance|rock|hip_hop|r_and_b|indie|classical|ambient",
    "subgenre": "specific subgenre",
    "artist_tier": "mainstream|indie|emerging|legendary",
    "era": "contemporary|2010s|2000s|90s|classic",
    "mood": "energetic|chill|emotional|party|focus|sleep",
    "queer_coding": 0.0-1.0  // Many favorite artists have strong LGBTQ+ associations
  },
  "viewing_context": {
    "time_of_day": "morning|afternoon|evening|night|late_night",
    "day_of_week": "weekday|weekend",
    "likely_activity": "working|relaxing|exercising|sleeping|socializing"
  },
  "engagement_pattern": {
    "is_repeat_view": true|false,
    "view_count_for_this_video": int,
    "days_since_first_view": int,
    "part_of_session": true|false
  },
  "content_depth": {
    "video_type": "official_music_video|lyric_video|live_performance|fan_made|playlist",
    "production_quality": "professional|semi_pro|amateur",
    "duration_category": "short|standard|long|extended"
  }
}
```

### search_activity

**Current columns**: `search_query`, `search_timestamp`, `domain`

**NEW schema (add row_metadata column)**:
```json
{
  "intent": {
    "category": "informational|navigational|transactional|investigational",
    "specificity": "broad|specific|exact",
    "urgency": "immediate|planning|casual"
  },
  "topic_analysis": {
    "domain": "technology|shopping|health|entertainment|work|personal|learning",
    "subdomain": "specific area",
    "sentiment": "curious|concerned|excited|frustrated",
    "life_area": "career|home|relationships|health|hobbies|self_improvement"
  },
  "temporal_patterns": {
    "time_of_day": "morning|afternoon|evening|night|late_night",
    "is_recurring_search": true|false,
    "search_session_position": "first|middle|last|standalone"
  },
  "search_behavior": {
    "is_refinement": true|false,  // Did they search something similar recently?
    "search_depth": "shallow|moderate|deep",  // How many related searches?
    "resolution": "found|abandoned|escalated"  // Did they find what they needed?
  }
}
```

### maps_activity

**Current columns**: `place_name`, `activity_type`, `context`, `place_category`

**NEW row_metadata schema**:
```json
{
  "location_meaning": {
    "purpose": "home|work|shopping|dining|entertainment|healthcare|travel|errand",
    "familiarity": "regular|occasional|first_time|exploring",
    "significance": "routine|special_occasion|emergency|convenience"
  },
  "movement_context": {
    "travel_mode": "driving|walking|transit|exploring",
    "trip_type": "commute|errand|social|adventure|necessity",
    "distance_category": "local|neighborhood|city|regional|travel"
  },
  "life_pattern": {
    "day_part": "morning|afternoon|evening|night",
    "is_recurring_visit": true|false,
    "visit_frequency": "daily|weekly|monthly|rare"
  },
  "place_category_expanded": {
    "type": "food|retail|service|healthcare|recreation|nature|residential|work",
    "subtype": "specific category",
    "price_tier": "budget|mid|upscale|luxury|free"
  }
}
```

### image_search

**Current columns**: `search_query`, `image_source`, `search_type`

**NEW row_metadata schema**:
```json
{
  "visual_interest": {
    "category": "product|reference|inspiration|research|entertainment|how_to",
    "aesthetic_domain": "design|fashion|home|art|nature|food|technology|people",
    "intent": "shopping|learning|creating|enjoying|researching"
  },
  "search_context": {
    "is_product_research": true|false,
    "is_creative_inspiration": true|false,
    "is_practical_reference": true|false
  },
  "image_type": {
    "expected_content": "photo|illustration|diagram|screenshot|infographic|meme",
    "quality_expectation": "professional|casual|any"
  }
}
```

### browser_history

**Current columns**: `url`, `title`, `domain`, `category`, `skill_area`, `topic`

**NEW row_metadata schema**:
```json
{
  "activity_type": {
    "primary": "reading|researching|shopping|socializing|working|entertaining|navigating",
    "depth": "skimming|reading|deep_dive|reference_check"
  },
  "life_context": {
    "domain": "work|personal|learning|shopping|entertainment|health|finance",
    "focus_level": "focused|browsing|distracted|multitasking"
  },
  "session_behavior": {
    "is_return_visit": true|false,
    "visit_pattern": "frequent|occasional|one_time",
    "referral_type": "direct|search|link|social"
  },
  "content_analysis": {
    "content_type": "article|product|documentation|social|video|tool|reference",
    "reading_time_estimate": "quick|moderate|long"
  }
}
```

---

## Synthesis Layers

### Layer 1: Row-Level (Flash-Lite)
Individual record enrichment with context

### Layer 2: Table-Level (Flash)
Aggregate patterns within each data source:
- **YouTube**: Top artists, genre preferences, listening sessions, mood patterns
- **Search**: Recurring interests, search evolution, curiosity patterns
- **Maps**: Movement patterns, place preferences, life geography
- **Browser**: Attention distribution, reading patterns, domain interests
- **Images**: Visual preferences, aesthetic patterns, research interests

### Layer 3: Cross-Table (Pro)
Life narrative synthesis:
- **Identity Themes**: What does all this data say about who this person is?
- **Temporal Arcs**: How have interests evolved over 18 years?
- **Life Phases**: Can we detect major life changes from behavior shifts?
- **Personality Traits**: What patterns emerge consistently across all sources?
- **Relationship Mapping**: How do different activities connect?

---

## Cost Estimates

### Tier 1: Flash-Lite (335K rows)
- Average 300 tokens input/row, 200 tokens output
- Input: 100M tokens = $7.50
- Output: 67M tokens = $20.10
- **Total Tier 1: ~$28**

### Tier 2: Flash (6 table syntheses)
- Average 50K tokens input per table, 10K output
- Input: 300K tokens = $0.03
- Output: 60K tokens = $0.02
- **Total Tier 2: ~$0.05**

### Tier 3: Pro (Cross-table synthesis)
- 100K tokens input, 20K output
- Input: $0.125
- Output: $0.20
- **Total Tier 3: ~$0.35**

**Grand Total: ~$28-30**

---

## Implementation Order

1. **Phase 1: Add row_metadata to search_activity** (currently missing)
2. **Phase 2: YouTube enrichment** (65K rows, music focus)
3. **Phase 3: Search enrichment** (159K rows, curiosity patterns)
4. **Phase 4: Maps enrichment** (32K rows, movement patterns)
5. **Phase 5: Browser enrichment** (58K rows, attention patterns)
6. **Phase 6: Image search enrichment** (17K rows, visual interests)
7. **Phase 7: Table-level synthesis** (6 aggregate analyses)
8. **Phase 8: Cross-table life narrative** (1 comprehensive synthesis)

---

## Apify YouTube Actor Value

From [YouTube Scraper](https://apify.com/streamers/youtube-scraper) - **TESTED 2025-11-30**:

**What we already have from Google Takeout**:
- video_title, video_url, video_id, channel_name, watch_timestamp

**What Apify returns** (tested with `streamers/youtube-scraper`):
- ✅ `duration` - "00:04:26" (useful for distinguishing clips vs full content)
- ✅ `viewCount` - 2.6B views (popularity signal)
- ✅ `likes` - 11M likes (engagement signal)
- ✅ `numberOfSubscribers` - 17.5M (channel authority)
- ✅ `date` - Publish date (not watch date)
- ✅ `text` - Video description
- ✅ `hashtags` - Creator-assigned tags
- ❌ **NO official YouTube category** (16-preset Music/Gaming/etc) - the main thing we wanted!

**Cost consideration**: 65K unique video IDs at ~$0.005/video = ~$325

**Recommendation**: **Skip Apify for now.**

The official YouTube category (the main value proposition) is NOT returned. The LLM can infer genre/content-type from title+channel nearly as well:
- "Jennifer Lopez, Pitbull - On The Floor" → Music, Pop, Dance
- "Apple Watch Ultra 3 vs Series 11" → Tech, Product Review

Cost comparison:
- Apify: $325 for 65K videos (adds duration, views, likes)
- LLM: $28 for ALL 335K rows (infers category, mood, patterns)

If we later want duration/views/likes, we can run Apify selectively on high-interest videos.

---

## Key Insight From Current Data

YouTube top channels reveal a **pop music enthusiast** profile:
1. Dua Lipa (1,425 videos, 5 years)
2. Lady Gaga (1,199 videos, 14 years!)
3. Katy Perry (776 videos)
4. Kim Petras, Doja Cat, Taylor Swift, Miley Cyrus...

The existing `skill_area` column completely misses this. Life > Skills.

Search patterns show:
- 18+ years of search history (2007-2025)
- 29 searches/day average
- Night owl pattern (peak 3-8pm, low 7am-12pm)
- Mix of work (IPEDS, education), shopping (Amazon, Wayfair), and personal

Maps patterns will reveal:
- Where you were
- Where you wanted to go
- How you moved through the world

This is **life archaeology** through data.

---

## Sources

- [YouTube Scraper - Apify](https://apify.com/streamers/youtube-scraper)
- [YouTube Metadata Scraper - Apify](https://apify.com/toludare/youtube-metadata-scraper-all)
- [YouTube Transcript Scraper - Apify](https://apify.com/visita/youtube-scraper)

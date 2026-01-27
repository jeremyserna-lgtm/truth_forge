# Stage 5 Mind Logo — Midjourney Prompts

**Version:** 1.0  
**Created:** January 24, 2026  
**Purpose:** Generate logo options for Stage 5 Mind using existing brand assets as reference

---

## Instructions for Jeremy

1. Upload the three reference images to Midjourney first:
   - `truth_engine.png`
   - `primitive_engine.png`
   - `credential_engine.png`

2. Use the prompts below with `--sref` (style reference) pointing to the uploaded images

3. Generate multiple variations and select top candidates for Ivan to vectorize

---

## Primary Prompt (Recommended)

```
Minimalist logo mark for "Stage 5 Mind" — a personal AI discovery platform.

SYMBOL: A geometric lightning bolt that feels WARMER and more PERSONAL than industrial. The bolt should suggest transformation, the journey through 5 stages, becoming. May incorporate the number 5 subtly, or have softer angles than the reference marks.

RELATIONSHIP: Part of the Truth Engine family (see reference images) but distinctly more HUMAN and INVITING. Same geometric precision, but approachable rather than imposing.

STYLE: 
- Industrial minimalism softened with warmth
- Could be embossed on premium hardware OR printed on a personal journal
- Grunge texture at LIGHT level (15-20% distress) — worn but not battle-damaged
- Single color, clean lines

FEEL: The moment someone recognizes themselves. Arrival. Being seen. Transformation.

EXPLICITLY AVOID:
- Cartoon lightning
- Generic brain/head imagery  
- Hearts or overly emotional symbols
- Gradients or complex shading
- Anything that looks like a generic app icon
- Heavy distress (lighter than references)

OUTPUT: Logo mark only, no text, on textured concrete/metal background similar to reference images.

--ar 1:1 --s 250 --v 6.1
```

---

## Variant Prompts

### Option A: Bolt + 5

```
Minimalist logo mark combining a geometric lightning bolt with the number 5. The bolt forms, intersects, or transforms into the 5. Premium, warm, personal feel. Industrial minimalism meets human touch. Light grunge texture (15%). Single color on concrete background. Part of the Truth Engine family but softer, more inviting. For a personal AI discovery platform.

--ar 1:1 --s 250 --v 6.1
```

### Option B: Standalone Bolt (No Circle)

```
Minimalist geometric lightning bolt logo mark — standalone, no containing circle. Warmer and more personal than typical industrial marks. Suggests transformation, awakening, the spark of recognition. Light texture (15% distress). Single color. Premium but approachable. Could be stamped on high-end personal goods. For Stage 5 Mind, a personal AI platform.

--ar 1:1 --s 250 --v 6.1
```

### Option C: Radiating Warmth

```
Minimalist logo mark: geometric lightning bolt as a source of warm light/energy. Subtle rays or glow emanating outward. Not harsh electricity — warm illumination. Suggests being SEEN, recognized, known. Light grunge texture. Single color on concrete background. Industrial precision with human warmth. For personal AI discovery.

--ar 1:1 --s 250 --v 6.1
```

### Option D: Ascending/Transforming

```
Minimalist logo mark showing transformation: a geometric bolt that suggests upward movement, growth, stages of becoming. The shape implies journey and arrival. Warmer than industrial, inviting rather than imposing. Light texture. Single color. Part of Truth Engine family but distinctly personal. For Stage 5 Mind — where humans discover their AI partner.

--ar 1:1 --s 250 --v 6.1
```

---

## Style Reference Settings

When using `--sref` with the uploaded reference images:

```
--sref [image URLs] --sw 50
```

The `--sw 50` (style weight) keeps the aesthetic connection without making it too derivative. Adjust up (75-100) for closer match, down (25) for more variation.

---

## Parameter Guide

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `--ar 1:1` | Square | Logo format |
| `--s 250` | Medium stylization | Balanced creativity |
| `--v 6.1` | Latest version | Best quality |
| `--sref` | Reference images | Style matching |
| `--sw` | 50 | Style weight |
| `--no` | text, words, letters | Exclude text |

---

## Evaluation Criteria

When reviewing generated options, assess:

1. **Family Resemblance** — Does it clearly belong with Truth Engine, Primitive Engine, Credential Atlas?
2. **Warmth** — Is it noticeably softer/more inviting than the industrial marks?
3. **Simplicity** — Can it work at favicon size?
4. **Memorability** — Distinctive silhouette?
5. **Reproducibility** — Can Ivan vectorize this cleanly?

---

## Post-Generation

Once you have 3-5 strong candidates:

1. Share with me for review
2. Select top 1-2 for Ivan to vectorize
3. Request same treatment: clean vector + light/medium/heavy texture overlays
4. Create lockup variations with typography

---

## Notes

- The texture in the reference images is heavier than what Stage 5 Mind needs
- Stage 5 Mind should feel like "the warm one" in the family
- The bolt is the unifier — keep it, but soften it
- Consider how it looks next to the other three logos as a family

---

*The Stage 5 Mind mark should make someone feel welcomed, not warned.*
